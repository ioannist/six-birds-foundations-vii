#!/usr/bin/env python3
"""Build machine-readable indexes over the imported Foundations VI scaffold.

This is a lexical/provenance index, not a replacement for Lean elaboration.
It exists to make prior declarations, imports, law coverage, labs, and trust
assumptions addressable before Foundations VII work begins.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "formalization" / "foundations_vi_scaffold"
LEAN = SCAFFOLD / "lean"
OUT = ROOT / "formalization" / "integration"

DECL_KINDS = (
    "abbrev",
    "axiom",
    "class",
    "def",
    "inductive",
    "instance",
    "lemma",
    "opaque",
    "structure",
    "theorem",
)

G_GRADES = {
    "G1": "theorem (Part a) / schema (Part b)",
    "G2": "theorem",
    "G3": "theorem",
    "G4": "schema",
    "G5": "calibration-anchored schema",
    "G6": "schema",
    "G7": "calibration-anchored schema",
    "G8": "theorem",
    "G9": "calibration-anchored schema",
    "G10": "theorem",
    "G11": "theorem",
    "G12": "theorem",
    "G13": "schema",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def strip_lean_comments(text: str) -> str:
    """Remove Lean line and nested block comments while preserving newlines."""

    out: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if block_depth:
            if ch == "/" and nxt == "-":
                block_depth += 1
                out.extend("  ")
                i += 2
                continue
            if ch == "-" and nxt == "/":
                block_depth -= 1
                out.extend("  ")
                i += 2
                continue
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue
        if not in_string and ch == "/" and nxt == "-":
            block_depth = 1
            out.extend("  ")
            i += 2
            continue
        if not in_string and ch == "-" and nxt == "-":
            while i < len(text) and text[i] != "\n":
                out.append(" ")
                i += 1
            continue
        out.append(ch)
        if ch == '"' and not escaped:
            in_string = not in_string
        escaped = ch == "\\" and not escaped
        if ch != "\\":
            escaped = False
        i += 1
    return "".join(out)


def library_roots() -> list[tuple[str, Path]]:
    config = tomllib.loads((LEAN / "lakefile.toml").read_text(encoding="utf-8"))
    roots: list[tuple[str, Path]] = []
    for lib in config.get("lean_lib", []):
        name = str(lib["name"])
        src = LEAN / str(lib.get("srcDir", "."))
        roots.append((name, src.resolve()))
    return roots


def module_map() -> dict[str, Path]:
    modules: dict[str, Path] = {}
    for lib_name, src in library_roots():
        if src == LEAN.resolve():
            candidates = [LEAN / f"{lib_name}.lean"]
            candidates.extend(sorted((LEAN / lib_name).rglob("*.lean")))
        else:
            candidates = sorted(src.rglob("*.lean"))
        for path in candidates:
            if not path.exists():
                continue
            rel = path.resolve().relative_to(src)
            module = ".".join(rel.with_suffix("").parts)
            prior = modules.get(module)
            if prior is not None and prior.resolve() != path.resolve():
                raise RuntimeError(f"duplicate module {module}: {prior} and {path}")
            modules[module] = path
    return dict(sorted(modules.items()))


def layer_for(module: str) -> str:
    if module.startswith("SixBirdsFoundationsVI"):
        return "FOUNDATIONS_VI"
    if module.startswith("SixBirdsIII"):
        return "FOUNDATIONS_III"
    if module == "SixBirds" or module.startswith("SixBirds."):
        return "FOUNDATIONS_II"
    if module.startswith("ClosureLadder"):
        return "FOUNDATIONS_I_CLOSURE"
    if module == "SixBirdsMetaMath.FoundationsICompat":
        return "FOUNDATIONS_I_COMPAT"
    if module.startswith("SixBirdsMetaMath.FoundationsIV"):
        return "FOUNDATIONS_IV"
    if module.startswith("SixBirdsMetaMath"):
        return "SHARED_META_MATH"
    return "UNCLASSIFIED"


def imports_from(text: str) -> list[tuple[str, int]]:
    cleaned = strip_lean_comments(text)
    rows: list[tuple[str, int]] = []
    for lineno, line in enumerate(cleaned.splitlines(), 1):
        match = re.match(r"^\s*import\s+(.+?)\s*$", line)
        if not match:
            continue
        for token in match.group(1).split():
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_'.]*", token):
                rows.append((token, lineno))
    return rows


def declarations_from(module: str, path: Path) -> list[dict[str, Any]]:
    cleaned = strip_lean_comments(path.read_text(encoding="utf-8", errors="replace"))
    scope: list[tuple[str, str]] = []
    rows: list[dict[str, Any]] = []
    kind_alt = "|".join(DECL_KINDS)
    decl_re = re.compile(
        rf"^\s*(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|unsafe)\s+)*"
        rf"({kind_alt})\s+([A-Za-z_][A-Za-z0-9_'.]*)\b"
    )
    for lineno, line in enumerate(cleaned.splitlines(), 1):
        ns = re.match(r"^\s*namespace\s+([A-Za-z_][A-Za-z0-9_'.]*)\s*$", line)
        if ns:
            scope.append(("namespace", ns.group(1)))
            continue
        sec = re.match(r"^\s*section(?:\s+([A-Za-z_][A-Za-z0-9_']*))?\s*$", line)
        if sec:
            scope.append(("section", sec.group(1) or ""))
            continue
        if re.match(r"^\s*end(?:\s+[A-Za-z_][A-Za-z0-9_'.]*)?\s*$", line):
            if scope:
                scope.pop()
            continue
        match = decl_re.match(line)
        if not match:
            continue
        kind, declared = match.groups()
        namespaces = [name for typ, name in scope if typ == "namespace" and name]
        prefix = ".".join(namespaces)
        if "." in declared or not prefix:
            fq = declared if not prefix or declared.startswith(prefix + ".") else f"{prefix}.{declared}"
        else:
            fq = f"{prefix}.{declared}"
        rows.append(
            {
                "layer": layer_for(module),
                "module": module,
                "file": str(path.relative_to(ROOT)),
                "line": lineno,
                "kind": kind,
                "declared_name": declared,
                "namespace": prefix,
                "fully_qualified_name": fq,
            }
        )
    return rows


def load_imported_foundations() -> list[dict[str, Any]]:
    audit_path = SCAFFOLD / "scripts" / "audit_foundations_dependencies.py"
    spec = importlib.util.spec_from_file_location("foundations_vi_dependency_audit", audit_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load imported dependency audit")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.load_inventory(SCAFFOLD / "formalization" / "inventory" / "imported_foundations.yml")


def top_level_f_id(path: Path) -> str:
    head = path.read_text(encoding="utf-8", errors="replace")[:1200]
    match = re.search(r"\b(F\d+[a-z]?)\b", head)
    return match.group(1) if match else ""


def semicolon(paths: Iterable[Path]) -> str:
    return ";".join(str(path.relative_to(ROOT)) for path in sorted(paths))


def build() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    modules = module_map()
    all_declarations: list[dict[str, Any]] = []
    module_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for module, path in modules.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        cleaned = strip_lean_comments(text)
        declarations = declarations_from(module, path)
        all_declarations.extend(declarations)
        imports = imports_from(text)
        for imported, lineno in imports:
            row = {
                "from_module": module,
                "to_module": imported,
                "from_file": str(path.relative_to(ROOT)),
                "line": lineno,
                "resolved_file": str(modules[imported].relative_to(ROOT)) if imported in modules else "",
                "resolution": "LOCAL" if imported in modules else "UNRESOLVED_OR_EXTERNAL",
            }
            edge_rows.append(row)
            if imported not in modules:
                unresolved.append(row)
        kind_counts = Counter(row["kind"] for row in declarations)
        module_rows.append(
            {
                "layer": layer_for(module),
                "module": module,
                "file": str(path.relative_to(ROOT)),
                "lines": len(text.splitlines()),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "imports": len(imports),
                "declarations": len(declarations),
                "theorems": kind_counts["theorem"] + kind_counts["lemma"],
                "axioms": kind_counts["axiom"],
                "opaque_constants": kind_counts["opaque"],
                "sorry_tokens": len(re.findall(r"\bsorry\b", cleaned)),
                "admit_tokens": len(re.findall(r"\badmit\b", cleaned)),
            }
        )

    module_rows.sort(key=lambda row: (row["layer"], row["module"]))
    all_declarations.sort(key=lambda row: (row["file"], int(row["line"]), row["declared_name"]))
    edge_rows.sort(key=lambda row: (row["from_module"], int(row["line"]), row["to_module"]))

    write_csv(
        OUT / "lean_modules.csv",
        module_rows,
        [
            "layer", "module", "file", "lines", "bytes", "sha256", "imports",
            "declarations", "theorems", "axioms", "opaque_constants", "sorry_tokens", "admit_tokens",
        ],
    )
    write_csv(
        OUT / "lean_declarations.csv",
        all_declarations,
        ["layer", "module", "file", "line", "kind", "declared_name", "namespace", "fully_qualified_name"],
    )
    write_csv(
        OUT / "lean_import_edges.csv",
        edge_rows,
        ["from_module", "to_module", "from_file", "line", "resolved_file", "resolution"],
    )
    write_csv(
        OUT / "lean_unresolved_imports.csv",
        unresolved,
        ["from_module", "to_module", "from_file", "line", "resolved_file", "resolution"],
    )

    graph = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    ET.SubElement(graph, "key", {"id": "layer", "for": "node", "attr.name": "layer", "attr.type": "string"})
    ET.SubElement(graph, "key", {"id": "file", "for": "node", "attr.name": "file", "attr.type": "string"})
    g = ET.SubElement(graph, "graph", edgedefault="directed", id="lean-imports")
    for module in modules:
        node = ET.SubElement(g, "node", id=module)
        ET.SubElement(node, "data", key="layer").text = layer_for(module)
        ET.SubElement(node, "data", key="file").text = str(modules[module].relative_to(ROOT))
    for idx, edge in enumerate(edge_rows, 1):
        if edge["to_module"] in modules:
            ET.SubElement(g, "edge", id=f"e{idx}", source=edge["from_module"], target=edge["to_module"])
    ET.indent(graph)
    ET.ElementTree(graph).write(OUT / "lean_import_graph.graphml", encoding="utf-8", xml_declaration=True)

    decls_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_declarations:
        decls_by_module[row["module"]].append(row)

    audited_rows = {str(row.get("object", "")): row for row in load_imported_foundations()}
    coverage_rows: list[dict[str, Any]] = []
    for module, path in modules.items():
        if layer_for(module) != "FOUNDATIONS_IV":
            continue
        law_id = top_level_f_id(path)
        if not law_id:
            continue
        audited = audited_rows.get(law_id, {})
        theorem_names = [
            row["declared_name"] for row in decls_by_module[module] if row["kind"] in {"theorem", "lemma"}
        ]
        coverage_rows.append(
            {
                "series": "F",
                "law_id": law_id,
                "name": path.stem,
                "coverage_status": "IMPORTED_MECHANIZED_MODULE",
                "paper_grade": "",
                "lean_module": module,
                "lean_file": str(path.relative_to(ROOT)),
                "key_declarations": ";".join(str(x) for x in audited.get("identifiers", theorem_names[:8])),
                "dependency_audit_status": str(audited.get("status", "not_in_FVI_dependency_inventory")),
                "caveat": str(audited.get("audit_note", "Module is present but was not one of the ten F-laws cited by Foundations VI.")),
            }
        )

    g_manifest = tomllib.loads(
        (SCAFFOLD / "formalization" / "manifests" / "foundations_vi_manifest.toml").read_text(encoding="utf-8")
    )
    g_rows: list[dict[str, Any]] = []
    for law in g_manifest.get("laws", []):
        law_id = str(law["law_id"])
        lean_file = SCAFFOLD / str(law["lean_file"])
        rel_to_lean = lean_file.relative_to(LEAN).with_suffix("")
        module = ".".join(rel_to_lean.parts)
        theorem_names = [
            row["declared_name"] for row in decls_by_module.get(module, []) if row["kind"] in {"theorem", "lemma"}
        ]
        row = {
            "series": "G",
            "law_id": law_id,
            "name": str(law["name"]),
            "coverage_status": str(law["intended_status"]).upper(),
            "paper_grade": G_GRADES[law_id],
            "lean_module": module,
            "lean_file": str(lean_file.relative_to(ROOT)),
            "key_declarations": ";".join(theorem_names),
            "dependency_audit_status": "law gate and manifest present",
            "caveat": "Status is inherited from the supplied Foundations VI manifest; later VII work must preserve each law's theorem/schema grade.",
        }
        coverage_rows.append(row)
        g_rows.append(row)

    with (ROOT / "registry" / "E_laws.csv").open(newline="", encoding="utf-8") as handle:
        for source_row in csv.DictReader(handle):
            coverage_rows.append(
                {
                    "series": "E",
                    "law_id": source_row.get("law_id", ""),
                    "name": source_row.get("name", ""),
                    "coverage_status": "NO_DEDICATED_IMPORTED_MODULE_LOCATED",
                    "paper_grade": source_row.get("status", ""),
                    "lean_module": "",
                    "lean_file": "",
                    "key_declarations": "",
                    "dependency_audit_status": "not represented as an E-series library in this archive",
                    "caveat": "This is an import-scope finding, not a claim that no Foundations V mechanization exists elsewhere.",
                }
            )

    series_order = {"F": 0, "E": 1, "G": 2}
    coverage_rows.sort(key=lambda row: (series_order[row["series"]], int(re.sub(r"\D", "", row["law_id"]) or 0), row["law_id"]))
    write_csv(
        OUT / "prior_law_formalization_coverage.csv",
        coverage_rows,
        [
            "series", "law_id", "name", "coverage_status", "paper_grade", "lean_module", "lean_file",
            "key_declarations", "dependency_audit_status", "caveat",
        ],
    )

    trace_rows: list[dict[str, Any]] = []
    for row in sorted(g_rows, key=lambda x: int(x["law_id"][1:])):
        law_id = row["law_id"]
        n = int(law_id[1:])
        packages = list((SCAFFOLD / "lab" / "foundations_vi_lab").glob(f"g{n:02d}_*"))
        tests = list((SCAFFOLD / "lab" / "tests").glob(f"test_g{n:02d}*.py"))
        results = list((SCAFFOLD / "lab" / "results").glob(f"{law_id}-*"))
        gate = SCAFFOLD / "formalization" / "notes" / "gates" / f"{law_id}.md"
        example = SCAFFOLD / "formalization" / "notes" / "examples" / f"{law_id}.md"
        trace_rows.append(
            {
                "law_id": law_id,
                "name": row["name"],
                "paper_grade": row["paper_grade"],
                "manifest_status": row["coverage_status"],
                "theorem_ledger": str((SCAFFOLD / "THEOREMS.md").relative_to(ROOT)),
                "lean_module": row["lean_module"],
                "lean_file": row["lean_file"],
                "theorem_count": sum(1 for d in decls_by_module[row["lean_module"]] if d["kind"] in {"theorem", "lemma"}),
                "gate_note": str(gate.relative_to(ROOT)) if gate.exists() else "",
                "example_note": str(example.relative_to(ROOT)) if example.exists() else "",
                "lab_packages": semicolon(packages),
                "test_files": semicolon(tests),
                "recorded_results": semicolon(results),
                "paper_source": str((SCAFFOLD / "paper" / "main.tex").relative_to(ROOT)),
            }
        )
    write_csv(
        OUT / "g_law_traceability.csv",
        trace_rows,
        [
            "law_id", "name", "paper_grade", "manifest_status", "theorem_ledger", "lean_module", "lean_file",
            "theorem_count", "gate_note", "example_note", "lab_packages", "test_files", "recorded_results", "paper_source",
        ],
    )

    layer_counts = Counter(row["layer"] for row in module_rows)
    kind_counts = Counter(row["kind"] for row in all_declarations)
    summary = {
        "lean_toolchain": (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "lean_modules": len(module_rows),
        "lean_files": len(list(LEAN.rglob("*.lean"))),
        "lean_import_edges": len(edge_rows),
        "unresolved_imports": len(unresolved),
        "lexically_indexed_declarations": len(all_declarations),
        "declaration_kinds": dict(sorted(kind_counts.items())),
        "module_layers": dict(sorted(layer_counts.items())),
        "sorry_tokens": sum(int(row["sorry_tokens"]) for row in module_rows),
        "admit_tokens": sum(int(row["admit_tokens"]) for row in module_rows),
        "axiom_declarations": sum(int(row["axioms"]) for row in module_rows),
        "opaque_declarations": sum(int(row["opaque_constants"]) for row in module_rows),
        "foundations_iv_law_modules": len([row for row in coverage_rows if row["series"] == "F"]),
        "foundations_vi_g_laws": len(g_rows),
        "foundations_v_e_laws_locally_covered": 0,
        "foundations_v_e_laws_with_dedicated_modules": 0,
        "foundations_v_e_laws_in_shared_module": 0,
        "python_source_files": len(list((SCAFFOLD / "lab").rglob("*.py"))),
        "python_test_files": len(list((SCAFFOLD / "lab" / "tests").glob("test_*.py"))),
    }
    (OUT / "formalization_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    summary = build()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
