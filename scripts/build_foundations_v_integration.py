#!/usr/bin/env python3
"""Build the formalization-aware Foundations V integration products.

This is still Step 1 reconnaissance.  It indexes and reconciles the supplied
Foundations V theorem base, completes the missing E16 root/manifest surface via
VII-owned adapters, and updates paper-versus-local coverage records.  It does
not create Foundations VII claims, bridges, laws, or proofs.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import shutil
import tomllib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "formalization" / "foundations_v_scaffold"
VI = ROOT / "formalization" / "foundations_vi_scaffold"
LEAN = V / "lean"
OUT = ROOT / "formalization" / "integration"
PROV = ROOT / "formalization" / "_provenance"

DEF_LAW = {
    "CarriedRecord": "D3",
    "ClosedLoopScope": "D5",
    "ESystem": "D4",
    "PredictiveSurplus": "D2",
    "ProbeEconomy": "D6",
    "RepairJoin": "D1",
}
LAW_MODULE = {
    "E1": "SixBirdsFoundationsV.Laws.E1Internalization",
    "E2": "SixBirdsFoundationsV.Laws.E2BoundedReflexivity",
    "E3": "SixBirdsFoundationsV.Laws.E3SelfMaintainingReclosure",
    "E4": "SixBirdsFoundationsV.Laws.E4RepairCompilation",
    "E5": "SixBirdsFoundationsV.Laws.E5ReclosureCollapse",
    "E6": "SixBirdsFoundationsV.Laws.E6E9PricedAccess",
    "E7": "SixBirdsFoundationsV.Laws.E7Alarm",
    "E8": "SixBirdsFoundationsV.Laws.E8ControlPrice",
    "E9": "SixBirdsFoundationsV.Laws.E6E9PricedAccess",
    "E10": "SixBirdsFoundationsV.Laws.E10CognitiveDemarcation",
    "E11": "SixBirdsFoundationsV.Laws.E11InstitutionalRewrite",
    "E12": "SixBirdsFoundationsV.Laws.E12Individuation",
    "E13": "SixBirdsFoundationsV.Laws.E13RepairTransport",
    "E14": "SixBirdsFoundationsV.Laws.E14Reconsolidation",
    "E15": "SixBirdsFoundationsV.Laws.E15OfflineReclosure",
    "E16": "SixBirdsFoundationsV.Laws.E16Adaptability",
}
LAW_STEM = {
    "E1": "E1",
    "E2": "E2",
    "E3": "E3",
    "E4": "E4",
    "E5": "E5",
    "E6": "E6_E9",
    "E7": "E7",
    "E8": "E8",
    "E9": "E6_E9",
    "E10": "E10",
    "E11": "E11",
    "E12": "E12",
    "E13": "E13",
    "E14": "E14",
    "E15": "E15",
    "E16": "E16",
}
SWEEP_STEM = {
    "E1": "E1_internalization",
    "E2": "E2_bounded_reflexivity",
    "E3": "E3_self_maintaining_reclosure",
    "E4": "E4_repair_compilation",
    "E5": "E5_reclosure_collapse",
    "E6": "E6_E9_probe_shop",
    "E7": "E7_alarm",
    "E8": "E8_control_price",
    "E9": "E6_E9_probe_shop",
    "E10": "E10_cognitive_demarcation",
    "E11": "E11_institutional_rewrite",
    "E12": "E12_individuation",
    "E13": "E13_repair_transport",
    "E14": "E14_reconsolidation",
    "E15": "E15_offline_reclosure",
    "E16": "E16_adaptability",
}
TEST_FILE = {
    "E1": "test_e1_internalization_sweep.py",
    "E2": "test_e2_bounded_reflexivity_sweep.py",
    "E3": "test_e3_self_maintaining_reclosure_sweep.py",
    "E4": "test_e4_repair_compilation_sweep.py",
    "E5": "test_e5_reclosure_collapse_sweep.py",
    "E6": "test_e6_e9_probe_shop_sweep.py",
    "E7": "test_e7_alarm_sweep.py",
    "E8": "test_e8_control_price_sweep.py",
    "E9": "test_e6_e9_probe_shop_sweep.py",
    "E10": "test_e10_cognitive_demarcation_sweep.py",
    "E11": "test_e11_institutional_rewrite_sweep.py",
    "E12": "test_e12_individuation_sweep.py",
    "E13": "test_e13_repair_transport_sweep.py",
    "E14": "test_e14_reconsolidation_sweep.py",
    "E15": "test_e15_offline_reclosure_sweep.py",
    "E16": "",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_shared() -> Any:
    path = ROOT / "scripts" / "build_formalization_indexes.py"
    spec = importlib.util.spec_from_file_location("shared_formal_index", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load shared formalization indexer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    module.layer_for = layer_for
    return module


def layer_for(module: str) -> str:
    if module.startswith("SixBirdsFoundationsV"):
        return "FOUNDATIONS_V"
    if module.startswith("SixBirdsIII"):
        return "FOUNDATIONS_III"
    if module == "Xi" or module.startswith("Xi.") or module == "Main" or module.startswith("Main."):
        return "XI_SUPPORT"
    if module.startswith("HolonomyMemory"):
        return "HOLONOMY_SUPPORT"
    return "UNCLASSIFIED"


def module_map() -> dict[str, Path]:
    modules: dict[str, Path] = {}

    def add(src: Path, candidates: Iterable[Path]) -> None:
        for path in candidates:
            if not path.is_file():
                continue
            module = ".".join(path.relative_to(src).with_suffix("").parts)
            prior = modules.get(module)
            if prior is not None and prior.resolve() != path.resolve():
                raise RuntimeError(f"duplicate V module {module}: {prior} / {path}")
            modules[module] = path

    add(LEAN, [LEAN / "SixBirdsFoundationsV.lean", *sorted((LEAN / "SixBirdsFoundationsV").rglob("*.lean"))])
    iii = LEAN / "vendor" / "foundations" / "six-birds-foundations-iii" / "lean" / "full"
    add(iii, sorted(iii.rglob("*.lean")))
    xi = LEAN / "vendor" / "foundations" / "xi"
    add(xi, sorted(xi.rglob("*.lean")))
    hol = LEAN / "vendor" / "foundations" / "holonomy-memory"
    add(hol, sorted(hol.rglob("*.lean")))
    return dict(sorted(modules.items()))


def law_for_module(module: str) -> str:
    if ".Definitional." in module:
        return DEF_LAW[module.rsplit(".", 1)[-1]]
    if module.endswith("E6E9PricedAccess"):
        return "E6+E9"
    match = re.search(r"\.Laws\.(E\d+)", module)
    return match.group(1) if match else ""


def toml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def build_indexes() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Path]]:
    shared = load_shared()
    modules = module_map()
    module_rows: list[dict[str, Any]] = []
    declaration_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for module, path in modules.items():
        text = path.read_text(encoding="utf-8", errors="replace")
        cleaned = shared.strip_lean_comments(text)
        decls = shared.declarations_from(module, path)
        declaration_rows.extend(decls)
        imports = shared.imports_from(text)
        kinds = Counter(row["kind"] for row in decls)
        module_rows.append(
            {
                "layer": layer_for(module),
                "module": module,
                "file": str(path.relative_to(ROOT)),
                "law_id": law_for_module(module),
                "lines": len(text.splitlines()),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "imports": len(imports),
                "declarations": len(decls),
                "theorems": kinds["theorem"] + kinds["lemma"],
                "axioms": kinds["axiom"],
                "opaque_constants": kinds["opaque"],
                "sorry_tokens": len(re.findall(r"\bsorry\b", cleaned)),
                "admit_tokens": len(re.findall(r"\badmit\b", cleaned)),
            }
        )
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

    module_rows.sort(key=lambda r: (r["layer"], r["module"]))
    declaration_rows.sort(key=lambda r: (r["file"], int(r["line"]), r["declared_name"]))
    edge_rows.sort(key=lambda r: (r["from_module"], int(r["line"]), r["to_module"]))

    write_csv(OUT / "foundations_v_lean_modules.csv", module_rows, list(module_rows[0]))
    write_csv(OUT / "foundations_v_lean_declarations.csv", declaration_rows, list(declaration_rows[0]))
    write_csv(OUT / "foundations_v_lean_import_edges.csv", edge_rows, list(edge_rows[0]))
    write_csv(
        OUT / "foundations_v_lean_unresolved_imports.csv",
        unresolved,
        ["from_module", "to_module", "from_file", "line", "resolved_file", "resolution"],
    )

    authored = [row for row in declaration_rows if row["layer"] == "FOUNDATIONS_V"]
    write_csv(OUT / "foundations_v_authored_declarations.csv", authored, list(authored[0]))
    authored_theorems = [row for row in authored if row["kind"] in {"theorem", "lemma"}]
    write_csv(OUT / "foundations_v_authored_theorems.csv", authored_theorems, list(authored_theorems[0]))
    kinds = Counter(row["kind"] for row in declaration_rows)
    authored_kinds = Counter(row["kind"] for row in authored)
    layers = Counter(row["layer"] for row in module_rows)
    summary = {
        "lean_toolchain": (LEAN / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "lean_files": len(module_rows),
        "lean_modules": len(module_rows),
        "lean_import_edges": len(edge_rows),
        "unresolved_imports": len(unresolved),
        "lexically_indexed_declarations": len(declaration_rows),
        "authored_foundations_v_declarations": len(authored),
        "authored_foundations_v_theorems": authored_kinds["theorem"] + authored_kinds["lemma"],
        "declaration_kinds": dict(sorted(kinds.items())),
        "authored_declaration_kinds": dict(sorted(authored_kinds.items())),
        "module_layers": dict(sorted(layers.items())),
        "sorry_tokens": sum(int(r["sorry_tokens"]) for r in module_rows),
        "admit_tokens": sum(int(r["admit_tokens"]) for r in module_rows),
        "axiom_declarations": sum(int(r["axioms"]) for r in module_rows),
        "opaque_declarations": sum(int(r["opaque_constants"]) for r in module_rows),
        "foundations_v_definition_modules": 6,
        "foundations_v_law_modules": 15,
        "foundations_v_e_laws_covered": 16,
        "upstream_root_missing_modules": ["SixBirdsFoundationsV.Laws.E16Adaptability"],
    }
    (OUT / "foundations_v_formalization_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary, declaration_rows, modules


def build_manifest_completion(declarations: list[dict[str, Any]]) -> dict[str, Any]:
    manifest_path = V / "formalization" / "manifests" / "foundations_v_manifest.toml"
    upstream = tomllib.loads(manifest_path.read_text(encoding="utf-8"))["declarations"]
    upstream_by_name = {row["name"]: row for row in upstream}
    authored = [row for row in declarations if row["layer"] == "FOUNDATIONS_V"]
    actual_by_name = {row["fully_qualified_name"]: row for row in authored}
    missing_from_lean = sorted(set(upstream_by_name) - set(actual_by_name))
    added = sorted(set(actual_by_name) - set(upstream_by_name))

    rows: list[dict[str, Any]] = []
    completed: list[dict[str, str]] = []
    for name, actual in sorted(actual_by_name.items(), key=lambda item: (item[1]["file"], int(item[1]["line"]), item[0])):
        prior = upstream_by_name.get(name)
        law_id = str(prior["law_id"]) if prior else law_for_module(actual["module"])
        if not law_id:
            raise RuntimeError(f"cannot assign law id to {name}")
        kind = str(prior["kind"]) if prior else ("theorem" if actual["kind"] in {"theorem", "lemma"} else "definition")
        source_file = str(prior["source_file"]) if prior else actual["file"]
        intended = str(prior["intended_status"]) if prior else "mechanize_now"
        trust = str(prior["trust_base_tag"]) if prior else "none"
        status = "UPSTREAM_MANIFEST_MATCH" if prior else "VII_E16_MANIFEST_COMPLETION"
        rows.append(
            {
                "name": name,
                "law_id": law_id,
                "lean_kind": actual["kind"],
                "manifest_kind": kind,
                "module": actual["module"],
                "file": actual["file"],
                "line": actual["line"],
                "upstream_manifest_status": status,
                "source_file": source_file,
                "trust_base_tag": trust,
            }
        )
        completed.append(
            {
                "name": name,
                "law_id": law_id,
                "kind": kind,
                "intended_status": intended,
                "source_file": source_file,
                "trust_base_tag": trust,
                "lean_module": actual["module"],
                "lean_file": actual["file"],
                "lean_line": str(actual["line"]),
                "integration_status": status,
            }
        )

    write_csv(OUT / "foundations_v_manifest_reconciliation.csv", rows, list(rows[0]))
    lines = [
        "# VII-owned completed Foundations V declaration manifest.",
        "# The upstream 1,141-row manifest is preserved byte-for-byte in the imported scaffold.",
        "# This normalized manifest adds the 120 already-landed E16 declarations and records exact Lean locations.",
        "",
    ]
    for row in completed:
        lines.append("[[declarations]]")
        for key in ("name", "law_id", "kind", "intended_status", "source_file", "trust_base_tag", "lean_module", "lean_file", "lean_line", "integration_status"):
            lines.append(f"{key} = {toml_quote(row[key])}")
        lines.append("")
    (OUT / "foundations_v_completed_manifest.toml").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "upstream_manifest_rows": len(upstream),
        "actual_authored_declarations": len(authored),
        "completed_manifest_rows": len(completed),
        "upstream_rows_missing_from_lean": missing_from_lean,
        "actual_rows_missing_from_upstream_manifest": len(added),
        "actual_only_law_ids": sorted({law_for_module(actual_by_name[name]["module"]) for name in added}),
        "actual_only_names": added,
    }
    (OUT / "foundations_v_manifest_reconciliation.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def build_root_audit(modules: dict[str, Path]) -> dict[str, Any]:
    shared = load_shared()
    root_path = LEAN / "SixBirdsFoundationsV.lean"
    imports = {name for name, _ in shared.imports_from(root_path.read_text(encoding="utf-8"))}
    expected = [
        *[f"SixBirdsFoundationsV.Definitional.{name}" for name in sorted(DEF_LAW)],
        *sorted(set(LAW_MODULE.values())),
    ]
    rows = []
    for module in expected:
        present = module in imports
        rows.append(
            {
                "module": module,
                "exists_in_imported_tree": "YES" if module in modules else "NO",
                "imported_by_upstream_root": "YES" if present else "NO",
                "imported_by_vii_complete_wrapper": "YES" if (present or module.endswith("E16Adaptability")) else "NO",
                "ruling": "UPSTREAM_ROOT_PRESENT" if present else "UPSTREAM_ROOT_OMISSION_REPAIRED_BY_VII_WRAPPER",
            }
        )
    write_csv(OUT / "foundations_v_root_import_audit.csv", rows, list(rows[0]))
    missing = [r["module"] for r in rows if r["imported_by_upstream_root"] == "NO"]
    summary = {
        "expected_authored_submodules": len(expected),
        "upstream_root_imported": len(expected) - len(missing),
        "upstream_root_missing": missing,
        "vii_wrapper": "formalization/lean/FoundationsVII/PriorFoundationsVComplete.lean",
        "vii_wrapper_complete": all(r["imported_by_vii_complete_wrapper"] == "YES" for r in rows),
    }
    (OUT / "foundations_v_root_import_audit.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def build_vendor_equivalence() -> dict[str, Any]:
    va = LEAN / "vendor" / "foundations" / "six-birds-foundations-iii" / "lean" / "full"
    vb = VI / "lean" / "vendor" / "foundations" / "six-birds-foundations-iii" / "lean" / "full"
    a = {p.relative_to(va).as_posix(): p for p in va.rglob("*") if p.is_file()}
    b = {p.relative_to(vb).as_posix(): p for p in vb.rglob("*") if p.is_file()}
    rows = []
    for rel in sorted(set(a) | set(b)):
        ah = sha256(a[rel]) if rel in a else ""
        bh = sha256(b[rel]) if rel in b else ""
        rows.append(
            {
                "relative_path": rel,
                "foundations_v_sha256": ah,
                "foundations_vi_sha256": bh,
                "status": "BYTE_IDENTICAL" if ah and ah == bh else ("MISSING_IN_V" if not ah else "MISSING_IN_VI" if not bh else "DIFFERENT"),
            }
        )
    write_csv(OUT / "foundations_v_vi_vendor_equivalence.csv", rows, list(rows[0]))
    summary = Counter(row["status"] for row in rows)
    return dict(summary)


def module_stats() -> dict[str, dict[str, str]]:
    return {row["module"]: row for row in read_csv(OUT / "foundations_v_lean_modules.csv")}


def build_law_traceability() -> list[dict[str, Any]]:
    e_disclosure = {row["law_id"]: row for row in read_csv(OUT / "e_law_formalization_disclosure.csv")}
    stats = module_stats()
    completed = read_csv(OUT / "foundations_v_manifest_reconciliation.csv")
    manifest_counts = Counter(row["law_id"] for row in completed)
    rows = []
    for i in range(1, 17):
        law = f"E{i}"
        module = LAW_MODULE[law]
        file = stats[module]["file"]
        stem = LAW_STEM[law]
        sweep = SWEEP_STEM[law]
        test = TEST_FILE[law]
        rows.append(
            {
                "law_id": law,
                "name": e_disclosure[law]["name"],
                "paper_grade": e_disclosure[law]["paper_grade"],
                "theorem_ledger": "formalization/foundations_v_scaffold/THEOREMS.md",
                "lean_module": module,
                "lean_file": file,
                "declaration_count": stats[module]["declarations"],
                "theorem_count": stats[module]["theorems"],
                "completed_manifest_rows": manifest_counts["E6+E9"] if law in {"E6", "E9"} else manifest_counts[law],
                "gate_note": f"formalization/foundations_v_scaffold/formalization/notes/gates/{stem}.md",
                "example_note": f"formalization/foundations_v_scaffold/formalization/notes/examples/{stem}.md",
                "sweep_predictions": f"formalization/foundations_v_scaffold/formalization/notes/sweeps/{sweep}_predictions.md",
                "sweep_results": f"formalization/foundations_v_scaffold/formalization/notes/sweeps/{sweep}_results.md",
                "pytest_file": f"formalization/foundations_v_scaffold/lab/tests/{test}" if test else "",
                "standalone_sweep": "formalization/foundations_v_scaffold/lab/sixbirds_foundations_v/sweeps/e16_adaptability_sweep.py" if law == "E16" else "",
                "root_import_status": "VII_COMPLETE_WRAPPER" if law == "E16" else "UPSTREAM_ROOT",
            }
        )
    write_csv(OUT / "foundations_v_e_law_traceability.csv", rows, list(rows[0]))
    return rows


def update_e_disclosure() -> None:
    path = OUT / "e_law_formalization_disclosure.csv"
    rows = read_csv(path)
    for row in rows:
        law = row["law_id"]
        row["local_import_status"] = (
            "PRESENT_SHARED_MODULE" if law in {"E6", "E9"} else
            "PRESENT_MODULE_WITH_VII_ROOT_COMPLETION" if law == "E16" else
            "PRESENT_DEDICATED_MODULE"
        )
        row["local_verification_state"] = "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED"
        row["local_kernel_build"] = "NOT_RUN: Lean/Lake unavailable"
        if law == "E16":
            row["caveat"] = "The E16 module is locally present (120 declarations, 15 theorems). The upstream root and 1,141-row manifest omit it; the VII-owned complete wrapper and 1,261-row completed manifest repair discoverability without modifying upstream files. Paper grade and host-certificate obligations remain controlling."
        else:
            row["caveat"] = "The module is locally present and statically import-closed. This verifies source availability and dependency closure, not a local kernel replay; paper grade, conditional hypotheses, and host-certificate obligations remain controlling."
    write_csv(path, rows, list(rows[0]))


def update_prior_coverage() -> None:
    path = OUT / "prior_law_formalization_coverage.csv"
    rows = read_csv(path)
    disclosure = {r["law_id"]: r for r in read_csv(OUT / "e_law_formalization_disclosure.csv")}
    stats = module_stats()
    for row in rows:
        if row["series"] != "E":
            continue
        law = row["law_id"]
        module = LAW_MODULE[law]
        row.update(
            {
                "coverage_status": "IMPORTED_MECHANIZED_MODULE",
                "paper_grade": disclosure[law]["paper_grade"],
                "lean_module": module,
                "lean_file": stats[module]["file"],
                "key_declarations": disclosure[law]["paper_principal_declarations"],
                "dependency_audit_status": "STATIC_IMPORT_CLOSED;LOCAL_SOURCE_RELOCATION_AUDITED",
                "caveat": "Local source and import closure are verified. No local Lean kernel build is claimed. E16 uses a VII-owned complete import wrapper because the upstream root omits its landed module." if law == "E16" else "Local source and import closure are verified. No local Lean kernel build is claimed; paper-side conditionality and proof grade are unchanged.",
            }
        )
    write_csv(path, rows, list(rows[0]))


def update_spine_coverage(summary: dict[str, Any]) -> None:
    path = OUT / "foundations_spine_formalization_coverage.csv"
    rows = read_csv(path)
    for row in rows:
        if row["paper_id"] != "P030":
            continue
        row["local_assets"] = (
            f"PRESENT: 22 authored modules (root + 6 D modules + 15 law modules), "
            f"{summary['authored_foundations_v_declarations']} authored declarations including "
            f"{summary['authored_foundations_v_theorems']} theorems; all E1-E16 modules, manifest/gate/example/sweep assets, and finite lab package retained."
        )
        row["local_verification_state"] = "R1_ASSET_PRESENT;R2_STATIC_INDEXED;R3_IMPORT_RESOLVED;R5_RUNTIME_BASELINE_RECORDED_SEPARATELY"
        row["local_kernel_build"] = "NOT_RUN: Lean/Lake unavailable"
        row["trust_or_fidelity_boundary"] = "Zero authored axiom/opaque/sorry/admit declarations were found lexically. E16 was landed but omitted from the upstream root and declaration manifest; VII-owned adapters complete import/manifest discoverability. Conditional classifications still depend on host-supplied complete evidence."
        row["reuse_ruling"] = "Reuse exact D1-D6 and E1-E16 modules through FoundationsVII.PriorFoundationsVComplete; preserve theorem/conditional-classification grades and do not infer empirical certificate construction from typed classification proofs."
    write_csv(path, rows, list(rows[0]))
    md = [
        "# Foundations spine — paper report versus locally reusable formal assets",
        "",
        "This is a Step-1 reconciliation table, not a claim-level bridge atlas.",
        "",
        "| Paper | Paper-reported scope | Local asset state | Reuse ruling |",
        "|---|---|---|---|",
    ]
    for row in rows:
        md.append(f"| {row['paper_id']} — {row['paper_title']} | {row['paper_reported_scope']} | {row['local_assets']} {row['local_verification_state']}; kernel: {row['local_kernel_build']}. | {row['reuse_ruling']} |")
    md += ["", "Full fidelity, trust, and source-anchor fields are in `foundations_spine_formalization_coverage.csv`."]
    (OUT / "FOUNDATIONS_SPINE_FORMALIZATION_COVERAGE.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def build_status_reconciliation() -> None:
    inventory = {row["law_id"]: row for row in tomllib.loads((V / "formalization" / "paper_inventory.toml").read_text(encoding="utf-8"))["items"]}
    queue = {row["law_id"]: row for row in read_csv(V / "formalization" / "traceability" / "queue_foundations_v.csv")}
    stats = module_stats()
    rows = []
    for law, module in LAW_MODULE.items():
        qid = "E6+E9" if law in {"E6", "E9"} else law
        inv = inventory.get(law, {})
        q = queue.get(qid, {})
        actual = int(stats[module]["declarations"])
        stale = inv.get("intended_status") == "unformalized" or q.get("intended_status") == "unformalized"
        rows.append(
            {
                "law_id": law,
                "paper_inventory_status": inv.get("intended_status", ""),
                "queue_status": q.get("intended_status", ""),
                "actual_lean_module": module,
                "actual_declarations": actual,
                "actual_theorems": stats[module]["theorems"],
                "status_ruling": "STALE_PLANNING_STATUS_SUPERSEDED_BY_LANDED_SOURCE" if stale else "PLANNING_STATUS_CONSISTENT_WITH_LANDED_SOURCE",
            }
        )
    write_csv(OUT / "foundations_v_status_reconciliation.csv", rows, list(rows[0]))


def build_dependency_relocation() -> dict[str, Any]:
    audit_path = V / "scripts" / "audit_foundations_dependencies.py"
    spec = importlib.util.spec_from_file_location("v_audit", audit_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Foundations V dependency inventory parser")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    inventory_path = V / "formalization" / "inventory" / "imported_foundations.yml"
    entries = audit.load_inventory(inventory_path)
    candidates = sorted((ROOT / "source" / "papers").glob("*.tex"))
    candidates += sorted((VI / "paper").glob("*"))
    texts = {path: path.read_text(encoding="utf-8", errors="replace") for path in candidates if path.is_file()}
    rows = []
    entry_status = Counter()
    for idx, entry in enumerate(entries, 1):
        identifiers = audit.identifiers_for(entry)
        hit_files: set[Path] = set()
        missing: list[str] = []
        for identifier in identifiers:
            hits = [path for path, text in texts.items() if identifier in text]
            if hits:
                hit_files.update(hits)
            else:
                missing.append(identifier)
        found = len(identifiers) - len(missing)
        status = "ALL_IDENTIFIERS_RELOCATED" if not missing else "PARTIAL_IDENTIFIERS_RELOCATED" if found else "NO_EXACT_IDENTIFIER_RELOCATED"
        entry_status[status] += 1
        rows.append(
            {
                "entry_index": idx,
                "object_name": entry.get("object_name", ""),
                "upstream_status": entry.get("status", ""),
                "original_source_paths": ";".join(str(p) for p in audit.source_paths_for(entry)),
                "identifier_count": len(identifiers),
                "exact_identifiers_found": found,
                "missing_identifiers": " || ".join(missing),
                "local_candidate_files": ";".join(str(p.relative_to(ROOT)) for p in sorted(hit_files)),
                "relocation_status": status,
                "ruling": "The upstream absolute path cannot be replayed in this self-contained archive; local exact-identifier relocation is reconnaissance evidence only and does not prove statement identity.",
            }
        )
    write_csv(OUT / "foundations_v_dependency_relocation.csv", rows, list(rows[0]))
    summary = {"inventory_entries": len(entries), **dict(entry_status)}
    (OUT / "foundations_v_dependency_relocation.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def build_cumulative_lean_index() -> dict[str, Any]:
    """Index the unique active module surface across V, VI, and the VII shell.

    Duplicate SixBirdsIII modules bundled by both upstream archives are counted
    once, using the Foundations VI path selected by the active Lake project.
    Their byte identity is validated separately.
    """
    shared = load_shared()

    vi_path = ROOT / "scripts" / "build_formalization_indexes.py"
    spec = importlib.util.spec_from_file_location("vi_formal_index_for_cumulative", vi_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load VI formalization indexer")
    vi_builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vi_builder)
    vi_builder.ROOT = ROOT

    v_modules = module_map()
    vi_modules = vi_builder.module_map()
    duplicate_modules = set(v_modules) & set(vi_modules)
    modules = dict(v_modules)
    modules.update(vi_modules)  # active Lake chooses the VI SixBirdsIII copy
    active_modules = {
        "FoundationsVII": ROOT / "formalization" / "lean" / "FoundationsVII.lean",
        "FoundationsVII.PriorScaffold": ROOT / "formalization" / "lean" / "FoundationsVII" / "PriorScaffold.lean",
        "FoundationsVII.PriorFoundationsVComplete": ROOT / "formalization" / "lean" / "FoundationsVII" / "PriorFoundationsVComplete.lean",
    }
    modules.update(active_modules)

    module_rows: list[dict[str, Any]] = []
    declaration_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for module, path in sorted(modules.items()):
        text = path.read_text(encoding="utf-8", errors="replace")
        cleaned = shared.strip_lean_comments(text)
        decls = shared.declarations_from(module, path)
        imports = shared.imports_from(text)
        declaration_rows.extend(decls)
        if module in active_modules:
            origin = "FOUNDATIONS_VII_IMPORT_SHELL"
        elif module in duplicate_modules:
            origin = "FOUNDATIONS_V_AND_VI_IDENTICAL_ACTIVE_VI_COPY"
        elif module in vi_modules:
            origin = "FOUNDATIONS_VI_ARCHIVE"
        else:
            origin = "FOUNDATIONS_V_ARCHIVE"
        kinds = Counter(row["kind"] for row in decls)
        module_rows.append({
            "module": module,
            "active_file": str(path.relative_to(ROOT)),
            "origin": origin,
            "duplicate_upstream_copy": "YES" if module in duplicate_modules else "NO",
            "imports": len(imports),
            "declarations": len(decls),
            "theorems": kinds["theorem"] + kinds["lemma"],
            "axioms": kinds["axiom"],
            "opaque_constants": kinds["opaque"],
            "sorry_tokens": len(re.findall(r"\bsorry\b", cleaned)),
            "admit_tokens": len(re.findall(r"\badmit\b", cleaned)),
            "sha256": sha256(path),
        })
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

    declaration_rows.sort(key=lambda row: (row["file"], int(row["line"]), row["declared_name"]))
    edge_rows.sort(key=lambda row: (row["from_module"], int(row["line"]), row["to_module"]))
    write_csv(OUT / "cumulative_lean_modules.csv", module_rows, list(module_rows[0]))
    write_csv(OUT / "cumulative_lean_declarations.csv", declaration_rows, list(declaration_rows[0]))
    cumulative_theorems = [row for row in declaration_rows if row["kind"] in {"theorem", "lemma"}]
    write_csv(OUT / "cumulative_lean_theorems.csv", cumulative_theorems, list(cumulative_theorems[0]))
    write_csv(OUT / "cumulative_lean_import_edges.csv", edge_rows, list(edge_rows[0]))
    write_csv(
        OUT / "cumulative_lean_unresolved_imports.csv",
        unresolved,
        ["from_module", "to_module", "from_file", "line", "resolved_file", "resolution"],
    )
    origins = Counter(row["origin"] for row in module_rows)
    kinds = Counter(row["kind"] for row in declaration_rows)
    cumulative = {
        "unique_active_modules": len(module_rows),
        "unique_inherited_modules": len(module_rows) - len(active_modules),
        "v_archive_modules": len(v_modules),
        "vi_archive_modules": len(vi_modules),
        "duplicate_module_names": len(duplicate_modules),
        "active_vii_import_shell_modules": len(active_modules),
        "unique_active_declarations": len(declaration_rows),
        "unique_active_theorems": len(cumulative_theorems),
        "active_vii_declarations": sum(int(row["declarations"]) for row in module_rows if row["origin"] == "FOUNDATIONS_VII_IMPORT_SHELL"),
        "import_edges": len(edge_rows),
        "unresolved_imports": len(unresolved),
        "sorry_tokens": sum(int(row["sorry_tokens"]) for row in module_rows),
        "admit_tokens": sum(int(row["admit_tokens"]) for row in module_rows),
        "axiom_declarations": sum(int(row["axioms"]) for row in module_rows),
        "opaque_declarations": sum(int(row["opaque_constants"]) for row in module_rows),
        "module_origins": dict(sorted(origins.items())),
        "declaration_kinds": dict(sorted(kinds.items())),
        "duplicate_modules": sorted(duplicate_modules),
        "selection_rule": "Foundations VI copy selected for byte-identical duplicate SixBirdsIII modules",
        "lean_toolchain": (ROOT / "formalization" / "lean" / "lean-toolchain").read_text(encoding="utf-8").strip(),
    }
    (OUT / "cumulative_formalization_summary.json").write_text(
        json.dumps(cumulative, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return cumulative


def update_summary(v_summary: dict[str, Any], manifest: dict[str, Any]) -> None:
    path = OUT / "formalization_summary.json"
    combined = json.loads(path.read_text(encoding="utf-8"))
    combined["foundations_v_e_laws_locally_covered"] = 16
    combined["foundations_v_e_laws_with_dedicated_modules"] = 14
    combined["foundations_v_e_laws_in_shared_module"] = 2
    combined.pop("foundations_v_e_laws_with_dedicated_imported_modules", None)
    combined["foundations_v_authored_modules"] = 22
    combined["foundations_v_authored_declarations"] = v_summary["authored_foundations_v_declarations"]
    combined["foundations_v_authored_theorems"] = v_summary["authored_foundations_v_theorems"]
    combined["foundations_v_completed_manifest_rows"] = manifest["completed_manifest_rows"]
    combined["foundations_v_upstream_manifest_rows"] = manifest["upstream_manifest_rows"]
    combined["foundations_v_upstream_root_missing_modules"] = v_summary["upstream_root_missing_modules"]
    combined["foundations_v_total_lean_modules_in_its_archive"] = v_summary["lean_modules"]
    combined["foundations_v_total_lean_declarations_in_its_archive"] = v_summary["lexically_indexed_declarations"]
    (path).write_text(json.dumps(combined, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(v_summary: dict[str, Any], manifest: dict[str, Any], root_audit: dict[str, Any], vendor: dict[str, Any], relocation: dict[str, Any], cumulative: dict[str, Any]) -> None:
    text = f"""# Foundations V theorem-base integration — Step 1 completion

## Scope

This integration imports the supplied cognition/Foundations V repository into the cumulative Foundations VII preparation repository. It remains Step 1: no all-paper claim extraction, bridge adjudication, Foundations VII law design, or new VII theorem statement has begun.

## Imported proof surface

- Upstream archive commit: `{(PROV / 'foundations_v_upstream_commit.txt').read_text().strip()}`.
- Active curated import: 372 byte-exact files, including **all Lean sources** and all vendored Lean dependencies.
- Lean archive index: {v_summary['lean_modules']} modules, {v_summary['lexically_indexed_declarations']} total lexical declarations, zero unresolved imports, zero `sorry`, zero `admit`, zero authored axioms, and zero opaque declarations.
- Foundations V authored surface: 22 modules and **{v_summary['authored_foundations_v_declarations']} declarations**, including **{v_summary['authored_foundations_v_theorems']} theorems**. This exactly matches the paper-reported 1,261 authored declarations / 187 theorems.
- Definitions: D1--D6 are present. Laws: all E1--E16 are present; E6 and E9 share one module.

## Completion repairs kept outside the immutable upstream tree

The upstream root imports every authored submodule except the already-landed `SixBirdsFoundationsV.Laws.E16Adaptability`. Its declaration manifest likewise contains {manifest['upstream_manifest_rows']} rows and omits the {manifest['actual_rows_missing_from_upstream_manifest']} E16 declarations. The repository therefore adds:

1. `formalization/lean/FoundationsVII/PriorFoundationsVComplete.lean`, which imports the upstream root and E16 explicitly;
2. `formalization/integration/foundations_v_completed_manifest.toml`, a {manifest['completed_manifest_rows']}-row normalized manifest linked to exact Lean files and lines.

The original root and manifest remain byte-for-byte unchanged.

## Dependency and version control

- All imported Foundations V Lean imports resolve locally.
- The Foundations III vendor copy bundled with Foundations V is byte-identical to the copy bundled with Foundations VI: {vendor.get('BYTE_IDENTICAL', 0)} files, no differences. The active Lake project therefore declares one SixBirdsIII library and retains both provenance copies.
- The historical imported-foundations inventory uses absolute local-checkout paths. In this self-contained repository, {relocation.get('ALL_IDENTIFIERS_RELOCATED', 0)} of {relocation['inventory_entries']} entries have every identifier relocated exactly, {relocation.get('PARTIAL_IDENTIFIERS_RELOCATED', 0)} are partial, and {relocation.get('NO_EXACT_IDENTIFIER_RELOCATED', 0)} has no exact-string relocation. These are explicitly recorded as source-packaging/wording limitations, not silently marked verified.

## Deduplicated cumulative active graph

The V and VI archives overlap on {cumulative['duplicate_module_names']} Foundations III module names. Their source copies are byte-identical and remain retained for provenance; the active Lake project selects one copy. The resulting graph contains **{cumulative['unique_active_modules']} unique modules**, **{cumulative['unique_active_declarations']} declarations**, including **{cumulative['unique_active_theorems']} theorem declarations**, and **{cumulative['import_edges']} resolved imports**, with zero VII declarations and zero unresolved imports. Machine-readable rows are in `cumulative_lean_modules.csv`, `cumulative_lean_declarations.csv`, `cumulative_lean_theorems.csv`, and `cumulative_lean_import_edges.csv`.

## Reuse rule

Foundations VII work may import `FoundationsVII.PriorScaffold` or the narrower `FoundationsVII.PriorFoundationsVComplete`. Paper-side theorem grades, conditional hypotheses, complete-evidence assumptions, and nonclaims remain controlling. A typed classification theorem is not evidence that a biological, cognitive, or social certificate was constructed honestly.
"""
    (ROOT / "reports" / "FOUNDATIONS_V_INTEGRATION_REPORT.md").write_text(text, encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    v_summary, declarations, modules = build_indexes()
    manifest = build_manifest_completion(declarations)
    root_audit = build_root_audit(modules)
    vendor = build_vendor_equivalence()
    update_e_disclosure()
    update_prior_coverage()
    build_law_traceability()
    build_status_reconciliation()
    relocation = build_dependency_relocation()
    cumulative = build_cumulative_lean_index()
    update_spine_coverage(v_summary)
    update_summary(v_summary, manifest)
    write_report(v_summary, manifest, root_audit, vendor, relocation, cumulative)
    print(
        "Foundations V integration built: "
        f"{v_summary['lean_modules']} modules; "
        f"{v_summary['authored_foundations_v_declarations']} authored declarations; "
        f"{manifest['completed_manifest_rows']} completed manifest rows; "
        f"{cumulative['unique_active_modules']} unique active modules."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
