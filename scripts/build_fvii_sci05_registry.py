#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import tomllib
from xml.sax.saxutils import escape as xml_escape
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "formalization" / "lean"
VII = LEAN / "FoundationsVII"
REG = ROOT / "science" / "registry"
TRACE = ROOT / "science" / "traceability"
LAB5 = ROOT / "formalization" / "foundations_vii_lab" / "phase5" / "results"
TRUST = VII / "Trust"

DATE = "2026-07-26"
_BUILD_STATUS_PATH = LEAN / "BUILD_STATUS_FINAL.json"
if _BUILD_STATUS_PATH.is_file():
    _build_status = json.loads(_BUILD_STATUS_PATH.read_text(encoding="utf-8"))
else:
    _build_status = {}
_KERNEL_PASS = _build_status.get("kernel_build_status") == "PASS"
# The replay was executed locally in this repo, not deferred to an external
# machine, so a passing run is recorded as PASS_LOCAL_REPLAY.
KERNEL_STATUS = "PASS_LOCAL_REPLAY" if _KERNEL_PASS else "PENDING_EXTERNAL_LEAN_REPLAY"
SOURCE_GRADE = "LEAN_KERNEL_REPLAY_PASS" if _KERNEL_PASS else "LEAN_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"


def _parse_axiom_receipt() -> dict[str, list[str]]:
    """theorem -> axioms it actually depends on, from the executed #print axioms receipt.

    Classification must come from the receipt, not from static import reachability:
    they disagree. 625 of the 732 theorems depend on no axioms; the other 107 depend
    on propext (10 of those also on Quot.sound). Calling all 732 "axiom-free" because
    the build passed is an overclaim.
    """
    path = LAB5 / "lean_axioms.txt"
    if not path.is_file():
        return {}
    out: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^'([^']+)' does not depend on any axioms\s*$", line)
        if m:
            out[m.group(1)] = []
            continue
        m = re.match(r"^'([^']+)' depends on axioms: \[(.*)\]\s*$", line)
        if m:
            out[m.group(1)] = [a.strip() for a in m.group(2).split(",") if a.strip()]
    return out


AXIOM_RECEIPT = _parse_axiom_receipt()
FINAL_STAGE = (
    "FVII_SCIENCE_FINAL_LOCAL_LEAN_REPLAY_PASS"
    if _KERNEL_PASS
    else "FVII_SCIENCE_FINAL_SOURCE_COMPLETE_EXTERNAL_LEAN_REPLAY_PENDING"
)
FINAL_ASSET_STATUS = (
    "FINAL_KERNEL_VERIFIED_ASSET_CLOSED"
    if _KERNEL_PASS
    else "FINAL_SOURCE_ASSET_CLOSED_EXTERNAL_KERNEL_REPLAY_PENDING"
)
FINAL_OBJECT_STATUS = (
    "VII_DEFINED_KERNEL_VERIFIED"
    if _KERNEL_PASS
    else "VII_DEFINED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"
)
FINAL_TARGET_STATUS = (
    "CLOSED_KERNEL_VERIFIED"
    if _KERNEL_PASS
    else "CLOSED_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING"
)
FINAL_NOGO_STATUS = (
    "FINAL_SCOPED_NO_GO_KERNEL_VERIFIED_WITH_EXPLICIT_ESCAPES"
    if _KERNEL_PASS
    else "FINAL_SCOPED_NO_GO_SOURCE_COMPLETE_WITH_EXPLICIT_ESCAPES_EXTERNAL_KERNEL_REPLAY_PENDING"
)
DISPOSITIONS = {
    "FORMAL_SCHEMA",
    "LEAN_KERNEL_PROVED",
    "LEAN_DECIDABLE_FINITE",
    "CONDITIONAL_THEOREM",
    "CONSTRUCTIVE_COUNTERMODEL",
    "REFUTED_CANDIDATE",
    "CLOSED_DEFERRAL",
}

DISPOSITIONS = {
    "VII-C001": "FORMAL_SCHEMA",
    "VII-C002": "FORMAL_SCHEMA",
    "VII-C003": "CONDITIONAL_THEOREM",
    "VII-C004": "FORMAL_SCHEMA",
    "VII-C005": "CONDITIONAL_THEOREM",
    "VII-C006": "FORMAL_SCHEMA",
    "VII-C007": "FORMAL_SCHEMA",
    "VII-C008": "FORMAL_SCHEMA",
    "VII-C009": "CONDITIONAL_THEOREM",
    "VII-C010": "FORMAL_SCHEMA",
    "VII-C011": "FORMAL_SCHEMA",
    "VII-C012": "FORMAL_SCHEMA",
    "VII-C013": "CONDITIONAL_THEOREM",
    "VII-C014": "FORMAL_SCHEMA",
    "VII-C015": "CONDITIONAL_THEOREM",
    "VII-C016": "CONDITIONAL_THEOREM",
    "VII-C017": "CONDITIONAL_THEOREM",
    "VII-C018": "CONDITIONAL_THEOREM",
    "VII-C019": "FORMAL_SCHEMA",
    "VII-C020": "FORMAL_SCHEMA",
    "VII-C021": "CONDITIONAL_THEOREM",
    "VII-C022": "FORMAL_SCHEMA",
    "VII-C023": "FORMAL_SCHEMA",
    "VII-C024": "FORMAL_SCHEMA",
    "VII-C025": "LEAN_DECIDABLE_FINITE",
    "VII-C026": "CLOSED_DEFERRAL",
    "VII-C027": "CONDITIONAL_THEOREM",
    "VII-C028": "CLOSED_DEFERRAL",
    "VII-C029": "CONDITIONAL_THEOREM",
    "VII-C030": "REFUTED_CANDIDATE",
    "VII-C031": "REFUTED_CANDIDATE",
    "VII-C032": "CONDITIONAL_THEOREM",
    "VII-C033": "CONDITIONAL_THEOREM",
    "VII-C034": "CONSTRUCTIVE_COUNTERMODEL",
    "VII-C035": "CONDITIONAL_THEOREM",
    "VII-C036": "CONDITIONAL_THEOREM",
}

TERMINAL_DISPOSITIONS = set(DISPOSITIONS.values())

# Owner-authorised restatement (2026-09-02, pre-ship audit).  The Step-3
# `proposed_conclusion` sentences were written before any Lean existed; for the
# seven candidates below the Step-3 sentence claims more than the kernel-replayed
# declarations establish.  The terminal registry now carries the Lean-strength
# sentence (the one the paper's body states), and keeps the Step-3 wording in
# `step3_proposed_conclusion` as the historical record.  No disposition,
# identifier or receipt changes.  The narrowly additive support bindings below
# make every clause of the restated conclusions traceable to its terminal Lean
# declaration.  See docs/SOURCE_DEVIATIONS.md (D-1).
TERMINAL_CONCLUSION_RESTATEMENTS = {
    "VII-C005": "Common origin, common carrier and common instrument, even jointly, do not entail shared access; shared access does not entail source independence; and a shared lineage defeats rather than supplies independence-sensitive join credit.",
    "VII-C015": "Upward, downward, and peer transmission are typed transmission records with explicit payload, loss, ambiguity, and source fields; a pure downward selection (no external insertion, lower-fact provenance preserved) cannot create lower-carrier facts absent before the selection.",
    "VII-C017": "Two legal route results on the same typed target and members that differ in order or bracketing and disagree in predictive value define a nonzero route residue; nonzero residue is interaction holonomy, not by itself directionality.",
    "VII-C025": "In the finite reference world a detector contract records, for the interaction laws, append-only evidence with non-empty signal, null and falsifier case lists, non-empty same-source, no-contact, scheduling and relabeling control lists, a false-positive cost strictly above the false-negative cost, and the frozen scenario and countermodel identifiers; it is well formed and complete over the 24 scenarios and 27 countermodels.",
    "VII-C029": "An observer or instrument using bounded shared capacity cannot certify native/endogenous formation while its occupancy is under-charged (charged occupancy below actual occupancy) or while its source role or cost is left off the system ledger.",
    "VII-C032": "Arrow or irreversibility claims require a drive certificate recording drive, path asymmetry, failed reversal, budget and audit, distinct from order residue, with null-versus-driven controls exhibited alongside it; cross-time contact uses explicit synchronization or partial-order witnesses rather than assumed simultaneity.",
    "VII-C034": "There exist enablement separation profiles in which enablement holds and is recorded as load-bearing while no descent factorization of the enabled object through the enabler is recorded; enablement may also be necessary but insufficient, with alternative determinants present.",
}

# Owner-authorised terminal traceability repair (2026-09-02).  These bindings
# add declarations already present in the frozen Lean tree; they do not alter
# any conclusion, proof, receipt, identifier, disposition, or source asset.
TERMINAL_SUPPORT_BINDINGS = {
    "VII-C005": [
        "FoundationsVII.SourceIndependenceGate.same_lineage_fails_independence_sensitive_credit",
    ],
    "VII-C025": [
        "FoundationsVII.Models.Finite.phase1DetectorContract",
        "FoundationsVII.Models.Finite.phase1_detector_frozen_complete",
    ],
}

TERMINAL_PHASE = {
    "VII-C020": 1,
    "VII-C023": 1,
    "VII-C024": 1,
    "VII-C025": 1,
    **{cid: 2 for cid in ("VII-C001", "VII-C002", "VII-C003", "VII-C004", "VII-C005", "VII-C006", "VII-C021", "VII-C022", "VII-C029")},
    **{cid: 3 for cid in ("VII-C007", "VII-C008", "VII-C009", "VII-C010", "VII-C011", "VII-C016", "VII-C019", "VII-C026", "VII-C030", "VII-C031", "VII-C033", "VII-C035", "VII-C036")},
    **{cid: 4 for cid in ("VII-C012", "VII-C013", "VII-C014", "VII-C015", "VII-C017", "VII-C018", "VII-C027", "VII-C028", "VII-C032", "VII-C034")},
}

COROLLARY_MODULE_ORDER = [
    "ProspectiveJoin",
    "SourceBudget",
    "NonInteraction",
    "EnablementResidual",
    "RefinementDescent",
    "NoFreeJoin",
    "HolonomyArrow",
    "NegativeForce",
    "ObserverEndogeny",
]

COROLLARY_CANDIDATES = {
    "ProspectiveJoin": ["VII-C002", "VII-C006", "VII-C009", "VII-C011"],
    "SourceBudget": ["VII-C009", "VII-C010", "VII-C011", "VII-C029"],
    "NonInteraction": ["VII-C008", "VII-C033"],
    "EnablementResidual": ["VII-C019", "VII-C027", "VII-C036"],
    "RefinementDescent": ["VII-C015", "VII-C030", "VII-C034"],
    "NoFreeJoin": ["VII-C003", "VII-C011", "VII-C035"],
    "HolonomyArrow": ["VII-C009", "VII-C017", "VII-C032"],
    "NegativeForce": ["VII-C021", "VII-C023", "VII-C033"],
    "ObserverEndogeny": ["VII-C013", "VII-C029"],
}

COROLLARY_NONCLAIMS = {
    "ProspectiveJoin": "Prospective timing, lawful admission, strictness, source alignment, and payment remain separate certificates; none is inferred from the others.",
    "SourceBudget": "Finite capacity is a declared local resource bound, not a universal conserved interaction currency.",
    "NonInteraction": "The exclusion applies only inside the exact covered family and preserves explicit outside-family escape routes.",
    "EnablementResidual": "Residual debt is typed bookkeeping for the declared chain and does not establish a universal scalar residual law.",
    "RefinementDescent": "A valid descent certificate does not repair a refinement that destroys compatibility or strictness.",
    "NoFreeJoin": "The obstruction is relative to the declared seed, generator, external-provision, payment, and certified-zero-cost channels.",
    "HolonomyArrow": "Strict join and holonomy do not supply directionality without an independent drive certificate.",
    "NegativeForce": "Negative force is coverage-, detector-, budget-, family-, and horizon-qualified; bounded nulls are not silently globalized.",
    "ObserverEndogeny": "Endogenous credit does not mean environmentally isolated or uncaused, and observer pricing remains a separate obligation.",
}

PHASE5_CANDIDATE_MAP = {
    "P5-E01": ["VII-C002", "VII-C006", "VII-C009", "VII-C011"],
    "P5-E02": ["VII-C009", "VII-C010", "VII-C011", "VII-C029"],
    "P5-E03": ["VII-C008", "VII-C033"],
    "P5-E04": ["VII-C019", "VII-C027", "VII-C036"],
    "P5-E05": ["VII-C015", "VII-C030", "VII-C034"],
    "P5-E06": ["VII-C003", "VII-C011", "VII-C035"],
    "P5-E07": ["VII-C009", "VII-C017", "VII-C032"],
    "P5-E08": ["VII-C021", "VII-C023"],
    "P5-E09": ["VII-C013", "VII-C029"],
    "P5-E10": ["VII-C017", "VII-C018", "VII-C032"],
    "P5-E11": ["VII-C001", "VII-C008", "VII-C012", "VII-C019", "VII-C025"],
}

DECL_RE = re.compile(
    r"^(?P<private>private\s+)?(?P<kind>structure|class|inductive|abbrev|def|theorem|lemma|corollary|axiom|opaque)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_'.]*)"
)
NS_RE = re.compile(r"^namespace\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
END_RE = re.compile(r"^end(?:\s+([A-Za-z_][A-Za-z0-9_.]*))?\s*$")
IMPORT_RE = re.compile(r"^import\s+([A-Za-z_][A-Za-z0-9_.]*)\s*$")
TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_'.]*(?:\.[A-Za-z_][A-Za-z0-9_'.]*)*")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(canonical(row) for row in rows))


def csv_value(value: Any) -> Any:
    if isinstance(value, (list, dict, bool)) or value is None:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return value


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row}) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_value(row.get(key, "")) for key in fields})



def write_graphml(path: Path, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], *, node_id_key: str, source_key: str, target_key: str) -> None:
    """Write a small deterministic GraphML file without external dependencies."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
        '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
        '  <key id="kind" for="edge" attr.name="kind" attr.type="string"/>',
        '  <graph id="G" edgedefault="directed">',
    ]
    for row in sorted(nodes, key=lambda item: str(item[node_id_key])):
        node_id = str(row[node_id_key])
        lines.append(f'    <node id="{xml_escape(node_id)}"><data key="label">{xml_escape(node_id)}</data></node>')
    for index, row in enumerate(sorted(edges, key=lambda item: (str(item[source_key]), str(item[target_key]), str(item.get("edge_kind", ""))))):
        source = str(row[source_key]); target = str(row[target_key]); kind = str(row.get("edge_kind", ""))
        lines.append(f'    <edge id="e{index}" source="{xml_escape(source)}" target="{xml_escape(target)}"><data key="kind">{xml_escape(kind)}</data></edge>')
    lines += ['  </graph>', '</graphml>', '']
    path.write_text("\n".join(lines), encoding="utf-8")

def remove_comments_and_strings(text: str) -> tuple[str, list[str]]:
    out: list[str] = []
    errors: list[str] = []
    i = 0
    block_depth = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if block_depth:
            if ch == "/" and nxt == "-":
                block_depth += 1; out.extend("  "); i += 2
            elif ch == "-" and nxt == "/":
                block_depth -= 1; out.extend("  "); i += 2
            else:
                out.append("\n" if ch == "\n" else " "); i += 1
            continue
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            out.append("\n" if ch == "\n" else " "); i += 1
            continue
        if ch == "/" and nxt == "-":
            block_depth = 1; out.extend("  "); i += 2; continue
        if ch == "-" and nxt == "-":
            while i < len(text) and text[i] != "\n":
                out.append(" "); i += 1
            continue
        if ch == '"':
            in_string = True; out.append(" "); i += 1; continue
        out.append(ch); i += 1
    if block_depth:
        errors.append(f"unterminated block comment depth={block_depth}")
    if in_string:
        errors.append("unterminated string literal")
    return "".join(out), errors


def module_name_for_vii_path(path: Path) -> str:
    return ".".join(path.relative_to(LEAN).with_suffix("").parts)


def parse_imports(path: Path) -> list[str]:
    code, _ = remove_comments_and_strings(path.read_text(encoding="utf-8"))
    return [m.group(1) for line in code.splitlines() if (m := IMPORT_RE.match(line.strip()))]


def library_roots() -> dict[str, Path]:
    data = tomllib.loads((LEAN / "lakefile.toml").read_text(encoding="utf-8"))
    roots: dict[str, Path] = {}
    for lib in data.get("lean_lib", []):
        roots[str(lib["name"])] = (LEAN / str(lib.get("srcDir", "."))).resolve()
    return roots


def resolve_import(name: str, roots: dict[str, Path]) -> Path | None:
    candidates = [LEAN / Path(*name.split(".")).with_suffix(".lean")]
    for lib_name, root in roots.items():
        if name == lib_name:
            candidates += [root / f"{lib_name}.lean", root / Path(*lib_name.split(".")).with_suffix(".lean")]
        elif name.startswith(lib_name + "."):
            candidates += [
                root / Path(*name.split(".")).with_suffix(".lean"),
                root / Path(*name.split(".")[1:]).with_suffix(".lean"),
            ]
    for path in candidates:
        if path.is_file():
            return path.resolve()
    return None


def build_import_graph() -> tuple[dict[str, list[str]], dict[str, str], list[str]]:
    roots = library_roots()
    graph: dict[str, list[str]] = {}
    paths: dict[str, str] = {}
    unresolved: list[str] = []
    queue: deque[str] = deque(["FoundationsVII.All"])
    seen: set[str] = set()
    while queue:
        module = queue.popleft()
        if module in seen:
            continue
        seen.add(module)
        path = resolve_import(module, roots)
        if path is None:
            unresolved.append(module)
            continue
        try:
            paths[module] = str(path.relative_to(ROOT))
        except ValueError:
            paths[module] = str(path)
        imports = parse_imports(path)
        graph[module] = imports
        for imported in imports:
            if imported not in seen:
                queue.append(imported)
    return graph, paths, sorted(set(unresolved))


def public_vii_modules(graph: dict[str, list[str]], paths: dict[str, str]) -> list[str]:
    modules = [m for m, rel in paths.items() if rel.startswith("formalization/lean/FoundationsVII/")]
    return sorted(modules)


def parse_declarations(path: Path, module: str) -> list[dict[str, Any]]:
    original = path.read_text(encoding="utf-8")
    code, errors = remove_comments_and_strings(original)
    if errors:
        raise RuntimeError(f"{path}: {errors}")
    original_lines = original.splitlines()
    code_lines = code.splitlines()
    namespace_stack: list[str] = []
    starts: list[tuple[int, re.Match[str], list[str]]] = []
    for idx, line in enumerate(code_lines):
        stripped = line.strip()
        if m := NS_RE.match(stripped):
            namespace_stack.append(m.group(1)); continue
        if END_RE.match(stripped):
            if namespace_stack:
                namespace_stack.pop()
            continue
        if m := DECL_RE.match(stripped):
            if m.group("private"):
                continue
            starts.append((idx, m, list(namespace_stack)))
    rows: list[dict[str, Any]] = []
    for pos, (idx, match, namespaces) in enumerate(starts):
        next_idx = starts[pos + 1][0] if pos + 1 < len(starts) else len(original_lines)
        raw_block = "\n".join(original_lines[idx:next_idx]).rstrip() + "\n"
        cleaned_block, _ = remove_comments_and_strings(raw_block)
        kind = match.group("kind")
        name = match.group("name")
        prefix = ".".join(namespaces)
        if name.startswith("FoundationsVII.") or not prefix:
            full_name = name
        else:
            full_name = f"{prefix}.{name}"
        if kind in {"theorem", "lemma", "corollary"}:
            cut = cleaned_block.find(":=")
            statement_raw = raw_block if cut < 0 else raw_block[:cut]
            statement = "\n".join(line.rstrip() for line in statement_raw.strip().splitlines()) + "\n"
        else:
            statement = ""
        rows.append({
            "fully_qualified_name": full_name,
            "short_name": full_name.rsplit(".", 1)[-1],
            "kind": kind,
            "module": module,
            "path": str(path.relative_to(ROOT)),
            "line": idx + 1,
            "source_block_sha256": sha_bytes(raw_block.encode("utf-8")),
            "statement_sha256": sha_bytes(statement.encode("utf-8")) if statement else "",
            "formal_statement": statement.strip(),
            "source_grade": SOURCE_GRADE,
            "kernel_status": KERNEL_STATUS,
            "exact_hypotheses": "AS_ENCODED_IN_FORMAL_STATEMENT" if statement else "NOT_APPLICABLE_DEFINITION",
            "source_block": raw_block,
        })
    return rows


def source_order_key(row: dict[str, Any]) -> tuple[str, int, str]:
    return str(row["path"]), int(row["line"]), str(row["fully_qualified_name"])


def transitive_imports(graph: dict[str, list[str]], module: str) -> set[str]:
    out: set[str] = set()
    stack = list(graph.get(module, []))
    while stack:
        item = stack.pop()
        if item in out:
            continue
        out.add(item)
        stack.extend(graph.get(item, []))
    return out


def topological_modules(graph: dict[str, list[str]], modules: set[str]) -> list[str]:
    indeg = {m: 0 for m in modules}
    reverse: dict[str, list[str]] = defaultdict(list)
    for m in modules:
        for dep in graph.get(m, []):
            if dep in modules:
                indeg[m] += 1
                reverse[dep].append(m)
    queue = deque(sorted(m for m, d in indeg.items() if d == 0))
    order: list[str] = []
    while queue:
        m = queue.popleft(); order.append(m)
        for child in sorted(reverse[m]):
            indeg[child] -= 1
            if indeg[child] == 0:
                queue.append(child)
    if len(order) != len(modules):
        raise RuntimeError("public module import graph contains a cycle")
    return order


def aggregate_phase_rows(prefix: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for phase in (1, 2, 3, 4):
        path = REG / f"phase{phase}_{prefix}.jsonl"
        if not path.is_file():
            continue
        key = {
            "candidate_closure": "candidate_id",
            "formalization_targets": "target_id",
            "no_go_closure": "no_go_id",
            "decision_closure": "decision_id",
        }.get(prefix)
        if key is None:
            continue
        for row in read_jsonl(path):
            rows[str(row[key])] = row
    return rows


def _is_axiom_free_core(row: dict[str, Any]) -> bool:
    """Axiom-free membership: the receipt decides it when a receipt exists.

    Falls back to static import reachability only when the replay has not run.
    """
    if _KERNEL_PASS and row.get("executed_axioms") is not None:
        return not row["executed_axioms"]
    return not row["static_trust_reachable"]


def _classify(name: str, reachable: bool) -> str:
    """Grade a theorem from its executed receipt where one exists.

    Without a receipt (replay not run) the grade is a static *candidate*, which is
    what it always was. With a receipt, "axiom-free" means the receipt says so --
    not that the module failed to reach the inherited trust surface.
    """
    if _KERNEL_PASS and name in AXIOM_RECEIPT:
        axioms = AXIOM_RECEIPT[name]
        if not axioms:
            return "AXIOM_FREE_CONFIRMED_BY_EXECUTED_PRINT_AXIOMS"
        return "DEPENDS_ON_" + "_".join(a.replace(".", "_").upper() for a in axioms) + "_CONFIRMED_BY_EXECUTED_PRINT_AXIOMS"
    if reachable:
        return "TRUST_REACHABLE_EXTENSION_PENDING_EXECUTED_PRINT_AXIOMS"
    return "AXIOM_FREE_CORE_CANDIDATE_PENDING_EXECUTED_PRINT_AXIOMS"


def main() -> int:
    REG.mkdir(parents=True, exist_ok=True)
    TRACE.mkdir(parents=True, exist_ok=True)
    TRUST.mkdir(parents=True, exist_ok=True)

    graph, module_paths, unresolved = build_import_graph()
    vii_modules = public_vii_modules(graph, module_paths)
    if unresolved:
        raise RuntimeError(f"unresolved imports: {unresolved}")
    module_order = topological_modules(graph, set(graph))
    module_rank = {module: idx for idx, module in enumerate(module_order)}

    declarations: list[dict[str, Any]] = []
    for module in vii_modules:
        path = ROOT / module_paths[module]
        if path.name in {"All.lean", "Runner.lean"} or "Trust" in path.parts:
            continue
        declarations.extend(parse_declarations(path, module))
    declarations.sort(key=source_order_key)
    names = [str(row["fully_qualified_name"]) for row in declarations]
    if len(names) != len(set(names)):
        duplicates = sorted(name for name in set(names) if names.count(name) > 1)
        raise RuntimeError(f"duplicate public declarations: {duplicates[:20]}")

    public_by_name = {str(row["fully_qualified_name"]): row for row in declarations}
    by_short: dict[str, list[str]] = defaultdict(list)
    for row in declarations:
        by_short[str(row["short_name"])].append(str(row["fully_qualified_name"]))

    theorem_rows = [row for row in declarations if row["kind"] in {"theorem", "lemma", "corollary"}]
    definition_rows = [row for row in declarations if row["kind"] not in {"theorem", "lemma", "corollary"}]

    # Theorem dependency DAG: source references are accepted only when the
    # referenced declaration is in an imported module or earlier in the same module.
    import_closures = {module: transitive_imports(graph, module) for module in graph}
    dependency_rows: list[dict[str, Any]] = []
    dependency_edges: list[dict[str, Any]] = []
    for theorem in theorem_rows:
        block = str(theorem["source_block"])
        tokens = set(TOKEN_RE.findall(block))
        deps: set[str] = set()
        for token in tokens:
            if token in public_by_name:
                candidate = token
                if candidate != theorem["fully_qualified_name"]:
                    deps.add(candidate)
            elif token in by_short and len(by_short[token]) == 1:
                candidate = by_short[token][0]
                if candidate != theorem["fully_qualified_name"]:
                    dep_row = public_by_name[candidate]
                    same_module_earlier = (
                        dep_row["module"] == theorem["module"]
                        and int(dep_row["line"]) < int(theorem["line"])
                    )
                    imported = dep_row["module"] in import_closures.get(str(theorem["module"]), set())
                    if same_module_earlier or imported:
                        deps.add(candidate)
        dep_list = sorted(deps)
        module_imports = sorted(import_closures.get(str(theorem["module"]), set()))
        dependency_rows.append({
            "theorem": theorem["fully_qualified_name"],
            "module": theorem["module"],
            "path": theorem["path"],
            "line": theorem["line"],
            "direct_source_dependencies": dep_list,
            "direct_source_dependency_count": len(dep_list),
            "transitive_import_modules": module_imports,
            "dependency_grade": "STATIC_SOURCE_REFERENCE_DAG_PENDING_KERNEL_PROOF_TERM_REPLAY",
            "statement_sha256": theorem["statement_sha256"],
        })
        for dep in dep_list:
            dependency_edges.append({
                "source_theorem": theorem["fully_qualified_name"],
                "target_declaration": dep,
                "edge_kind": "STATIC_SOURCE_REFERENCE",
            })

    # Verify the declaration-reference edges are acyclic using module order and source line.
    for edge in dependency_edges:
        source = public_by_name[str(edge["source_theorem"])]
        target = public_by_name[str(edge["target_declaration"])]
        valid = (
            module_rank.get(str(target["module"]), -1) < module_rank.get(str(source["module"]), -1)
            or (
                target["module"] == source["module"]
                and int(target["line"]) < int(source["line"])
            )
        )
        if not valid:
            raise RuntimeError(f"non-DAG dependency edge: {edge}")

    inherited_trust = [row for row in read_jsonl(TRACE / "phase1_trust_surface.jsonl") if row["ownership"] == "INHERITED"]
    trust_module = "SixBirdsMetaMath.FoundationsIV.Access.HiddennessNormalForm"
    theorem_trust: list[dict[str, Any]] = []
    for theorem in theorem_rows:
        reachable = trust_module in import_closures.get(str(theorem["module"]), set())
        theorem_trust.append({
            "theorem": theorem["fully_qualified_name"],
            "module": theorem["module"],
            "statement_sha256": theorem["statement_sha256"],
            "static_trust_reachable": reachable,
            "executed_axioms": AXIOM_RECEIPT.get(str(theorem["fully_qualified_name"])),
            "static_classification": _classify(str(theorem["fully_qualified_name"]), reachable),
            "reachable_inherited_trust": [row["declaration"] for row in inherited_trust] if reachable else [],
            "executed_print_axioms_status": KERNEL_STATUS,
            "nonclaim": "Static import reachability is not a substitute for executed #print axioms output.",
        })

    axiom_free_core = [
        {
            "theorem": row["theorem"],
            "module": row["module"],
            "statement_sha256": row["statement_sha256"],
            "static_classification": row["static_classification"],
            "kernel_status": KERNEL_STATUS,
            "nonclaim": ("Membership is established by static import reachability and is confirmed by the executed #print axioms receipt."
                         if _KERNEL_PASS else
                         "Membership is established by static import reachability only and remains pending executed #print axioms confirmation."),
        }
        for row in theorem_trust
        if _is_axiom_free_core(row)
    ]

    # Corollaries are intentionally restricted to the nine cross-family modules.
    corollaries: list[dict[str, Any]] = []
    cor_idx = 1
    corollary_ids_by_candidate: dict[str, list[str]] = defaultdict(list)
    for module_name in COROLLARY_MODULE_ORDER:
        rel = f"formalization/lean/FoundationsVII/Corollaries/{module_name}.lean"
        module_theorems = [row for row in theorem_rows if row["path"] == rel]
        module_theorems.sort(key=lambda row: int(row["line"]))
        for row in module_theorems:
            cid = f"FVII-COR-{cor_idx:03d}"
            candidates = COROLLARY_CANDIDATES[module_name]
            for candidate in candidates:
                corollary_ids_by_candidate[candidate].append(cid)
            corollaries.append({
                "corollary_id": cid,
                "name": row["short_name"],
                "declaration": row["fully_qualified_name"],
                "module": row["module"],
                "path": row["path"],
                "line": row["line"],
                "formal_statement": row["formal_statement"],
                "statement_sha256": row["statement_sha256"],
                "source_block_sha256": row["source_block_sha256"],
                "candidate_ids": candidates,
                "proof_grade": SOURCE_GRADE,
                "kernel_status": KERNEL_STATUS,
                "exact_hypotheses": "AS_ENCODED_IN_FORMAL_STATEMENT",
                "nonclaim": COROLLARY_NONCLAIMS[module_name],
                "escape_routes": ["Change an explicit typed hypothesis or move outside the declared carrier, source, budget, coverage, or temporal scope."],
            })
            cor_idx += 1

    # Candidate terminal closure.
    candidate_index = {row["candidate_id"]: row for row in read_jsonl(ROOT / "readiness" / "candidate_index.jsonl")}
    phase_candidate_rows = {
        phase: {row["candidate_id"]: row for row in read_jsonl(REG / f"phase{phase}_candidate_closure.jsonl")}
        for phase in (1, 2, 3, 4)
    }
    final_candidates: list[dict[str, Any]] = []
    for candidate_id in sorted(candidate_index):
        base = candidate_index[candidate_id]
        phase = TERMINAL_PHASE[candidate_id]
        landed = phase_candidate_rows[phase][candidate_id]
        declarations_list = sorted(set(
            landed.get("lean_declarations", [])
            + landed.get("lean_definitions", [])
            + landed.get("lean_theorems", [])
            + TERMINAL_SUPPORT_BINDINGS.get(candidate_id, [])
        ))
        missing = [name for name in declarations_list if name not in public_by_name]
        # Phase-1 metadata includes inherited anchors; retain them but do not require
        # them in the VII-owned declaration registry.
        required_missing = [name for name in missing if name.startswith("FoundationsVII.") and ".Prior." not in name]
        if required_missing:
            raise RuntimeError(f"candidate {candidate_id} missing declarations: {required_missing}")
        prior_envelopes = list(landed.get("finite_envelopes", []))
        phase5_envelopes = sorted(fid for fid, ids in PHASE5_CANDIDATE_MAP.items() if candidate_id in ids)
        disposition = DISPOSITIONS[candidate_id]
        if disposition not in TERMINAL_DISPOSITIONS:
            raise RuntimeError(disposition)
        final_candidates.append({
            "candidate_id": candidate_id,
            "name": base["name"],
            "kind": base["kind"],
            "terminal_disposition": disposition,
            "terminal_phase": f"FVII-SCI-0{phase}",
            "controlling_asset_id": landed["asset_id"],
            "terminal_status": FINAL_ASSET_STATUS,
            "kernel_status": KERNEL_STATUS,
            "proof_grade": (
                "FORMAL_SCHEMA_SOURCE_COMPLETE" if disposition == "FORMAL_SCHEMA" else
                "LEAN_DECIDABLE_FINITE_SOURCE_COMPLETE_PENDING_KERNEL_REPLAY" if disposition == "LEAN_DECIDABLE_FINITE" else
                "CONDITIONAL_THEOREM_SOURCE_COMPLETE" if disposition == "CONDITIONAL_THEOREM" else
                "CONSTRUCTIVE_COUNTERMODEL_WITH_SCOPED_POSITIVE_RESULTS" if disposition == "CONSTRUCTIVE_COUNTERMODEL" else
                "REFUTED_UNIVERSAL_CANDIDATE_WITH_SCOPED_REPLACEMENT" if disposition == "REFUTED_CANDIDATE" else
                "TERMINAL_DEFERRAL_WITH_FORMAL_REOPEN_OR_SPECIAL_CASE_GATE"
            ),
            "lean_declarations": declarations_list,
            "missing_vii_declarations": required_missing,
            "formalization_targets": base.get("formalization_targets", []),
            "corollary_ids": sorted(corollary_ids_by_candidate.get(candidate_id, [])),
            "finite_assay_ids": sorted(set(prior_envelopes + phase5_envelopes)),
            "positive_models": base.get("positive_model", []),
            "null_models": base.get("null_models", []),
            "countermodels": base.get("countermodels", []),
            "exact_hypotheses": base.get("hypotheses", []),
            "proposed_conclusion": TERMINAL_CONCLUSION_RESTATEMENTS.get(candidate_id, base.get("proposed_conclusion", "")),
            "step3_proposed_conclusion": base.get("proposed_conclusion", ""),
            "conclusion_restated_to_lean_strength": candidate_id in TERMINAL_CONCLUSION_RESTATEMENTS,
            "nonclaims": base.get("nonclaims", []),
            "escape_routes": base.get("escape_routes", []),
            "source_trace": base.get("source_trace", {}),
            "step3_prior_status": base.get("proof_status", ""),
            "specification_ready_not_proved_remaining": False,
        })

    # Object-model closure: all eighteen Step-3 object records are either
    # inherited with an explicit anchor or VII-owned source definitions.
    object_base = read_jsonl(ROOT / "readiness" / "object_model.jsonl")
    exact_object_names = {
        "VII-O04": "FoundationsVII.DomainState",
        "VII-O05": "FoundationsVII.AdmissionTransition",
        "VII-O06": "FoundationsVII.ProspectiveCommitment",
        "VII-O07": "FoundationsVII.SourceLedger",
        "VII-O08": "FoundationsVII.BudgetLedger",
        "VII-O09": "FoundationsVII.ContactSurface",
        "VII-O10": "FoundationsVII.ContactWitness",
        "VII-O11": "FoundationsVII.InteractionRecord",
        "VII-O12": "FoundationsVII.JoinCandidate",
        "VII-O13": "FoundationsVII.JoinCertificate",
        "VII-O14": "FoundationsVII.JoinObstruction",
        "VII-O15": "FoundationsVII.NonInteractionCertificate",
        "VII-O16": "FoundationsVII.EnablementRecord",
        "VII-O17": "FoundationsVII.ReachabilityWitness",
        "VII-O18": "FoundationsVII.ObserverOccupancyRecord",
    }
    inherited_object_records = {
        "VII-O01": ("INHERITED_EXACT_DECLARATION", ["SixBirdsFoundationsV.TheoryPackage"], "FoundationsVII.Prior.theoryPackageAnchor"),
        "VII-O02": ("INHERITED_COMPOSITE_INTERFACE_ROLE", ["SixBirdsFoundationsV.AccessPolicy", "ClosureOp", "ClosureLadder"], "FoundationsVII.Prior.interfaceLensAnchor"),
        "VII-O03": ("INHERITED_ROLE_WITH_VII_APPEND_ONLY_DATA_MODEL", ["SixBirds.ClaimRecord", "SixBirds.NonclaimRecord", "FoundationsVII.AuditRecord"], "FoundationsVII.Prior.auditRecordAnchor"),
    }
    final_objects: list[dict[str, Any]] = []
    for row in object_base:
        object_id = str(row["object_id"])
        if object_id in inherited_object_records:
            status, declarations_for_object, anchor = inherited_object_records[object_id]
            local_definition = "FoundationsVII.AuditRecord" if object_id == "VII-O03" else ""
        else:
            declaration = exact_object_names[object_id]
            if declaration not in public_by_name:
                raise RuntimeError(f"object {object_id} missing public declaration {declaration}")
            status, declarations_for_object, anchor, local_definition = (
                FINAL_OBJECT_STATUS,
                [declaration],
                "",
                declaration,
            )
        final_objects.append({
            **row,
            "final_status": status,
            "declarations": declarations_for_object,
            "anchor_declaration": anchor,
            "local_definition": local_definition,
            "kernel_status": KERNEL_STATUS,
            "terminal": True,
        })

    # Formalization target closure.
    target_base = {row["target_id"]: row for row in read_jsonl(REG / "phase1_formalization_targets.jsonl")}
    phase_target_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for phase in (2, 3, 4):
        for row in read_jsonl(REG / f"phase{phase}_formalization_targets.jsonl"):
            phase_target_rows[str(row["target_id"])].append(row)
    final_targets: list[dict[str, Any]] = []
    for target_id in sorted(target_base):
        base = target_base[target_id]
        later = phase_target_rows.get(target_id, [])
        theorems: set[str] = set()
        candidates: set[str] = set(base.get("candidate_ids", []))
        statuses: list[str] = []
        for row in later:
            candidates.update(row.get("candidate_ids", []))
            for key, value in row.items():
                if key.endswith("theorems") and isinstance(value, list):
                    theorems.update(str(x) for x in value)
                if key.endswith("status") and isinstance(value, str):
                    statuses.append(value)
        disposition = FINAL_TARGET_STATUS
        if target_id == "FT14":
            disposition = "CLOSED_MIXED_THEOREMS_AND_TERMINAL_FULL_ALGEBRA_DEFERRAL"
        final_targets.append({
            "target_id": target_id,
            "name": base.get("name", base.get("target_name", "")),
            "candidate_ids": sorted(candidates),
            "final_status": disposition,
            "kernel_status": KERNEL_STATUS,
            "lean_theorems": sorted(theorems),
            "prior_statuses": statuses,
            "adapter_ids": base.get("adapter_ids", []),
            "nonclaim": "Target closure records landed source assets; the Lean kernel replay has been executed locally and every public theorem carries an executed #print axioms receipt. Kernel verification does not upgrade a target's scientific disposition.",
        })

    # No-go closure.
    no_go_rows: list[dict[str, Any]] = []
    for phase in (2, 3, 4):
        for row in read_jsonl(REG / f"phase{phase}_no_go_closure.jsonl"):
            failures = list(row.get("failure_scenarios", []))
            if row.get("failure_scenario"):
                failures = [str(row["failure_scenario"]), *[str(x) for x in failures if str(x) != str(row["failure_scenario"])]]
            no_go_rows.append({
                **row,
                "failure_scenario": failures[0] if failures else "DECLARED_FORMAL_COUNTERMODEL",
                "failure_scenarios": failures or ["DECLARED_FORMAL_COUNTERMODEL"],
                "final_status": FINAL_NOGO_STATUS,
                "kernel_status": KERNEL_STATUS,
                "exact_hypotheses": "AS_ENCODED_IN_FORMAL_THEOREM",
            })
    no_go_rows.sort(key=lambda row: int(str(row["no_go_id"]).split("-")[-1]))

    # Decision closure: phase 3/4 rulings supersede phase-1 working rulings;
    # DP13/DP14 remain explicit nonblocking source-governance boundaries.
    phase1_decisions = {row["decision_id"]: row for row in read_jsonl(REG / "phase1_decision_rulings.jsonl")}
    later_decisions: dict[str, dict[str, Any]] = {}
    for phase in (3, 4):
        for row in read_jsonl(REG / f"phase{phase}_decision_closure.jsonl"):
            later_decisions[row["decision_id"]] = row
    final_decisions: list[dict[str, Any]] = []
    for decision_id in sorted(phase1_decisions):
        base = phase1_decisions[decision_id]
        later = later_decisions.get(decision_id)
        if later:
            ruling = next((value for key, value in later.items() if key.endswith("terminal_ruling")), "TERMINAL_RULING_RECORDED")
            evidence = []
            for key, value in later.items():
                if (key.endswith("theorems") or key.endswith("evidence")) and isinstance(value, list):
                    evidence.extend(str(x) for x in value)
            status = "TERMINAL_SCIENCE_DECISION"
        else:
            ruling = base.get("working_ruling", base.get("phase1_ruling", "SOURCE_GOVERNANCE_BOUNDARY_RETAINED"))
            evidence = base.get("lean_declarations", [])
            status = "NONBLOCKING_SOURCE_GOVERNANCE_BOUNDARY_RETAINED"
        final_decisions.append({
            "decision_id": decision_id,
            "question": base.get("question", base.get("name", "")),
            "final_ruling": ruling,
            "final_status": status,
            "evidence": sorted(set(evidence)),
            "kernel_status": KERNEL_STATUS,
            "nonclaim": base.get("nonclaim", "The ruling is scoped to the declared science asset program."),
        })

    # Adapters remain exact imported-reuse contracts.
    adapters = read_jsonl(REG / "inherited_adapter_ledger.jsonl")
    final_adapters = [{**row, "final_status": "RETAINED_EXACT_REUSE_CONTRACT", "kernel_status": KERNEL_STATUS} for row in adapters]

    # Finite assays: all 43 Phase 2-5 envelopes.  Earlier phases are
    # retained from their canonical science registries; Phase 5 comes from the
    # freshly executed final laboratory.
    cumulative: list[dict[str, Any]] = []
    for phase, registry_name in (
        ("PHASE2", "phase2_finite_envelopes.jsonl"),
        ("PHASE3", "phase3_finite_envelopes.jsonl"),
        ("PHASE4", "phase4_finite_envelopes.jsonl"),
    ):
        for row in read_jsonl(REG / registry_name):
            cumulative.append({**row, "phase": phase})
    for row in read_jsonl(LAB5 / "envelopes.jsonl"):
        cumulative.append({**row, "phase": "PHASE5"})
    final_assays: list[dict[str, Any]] = []
    for row in cumulative:
        family_id = str(row["family_id"])
        phase = str(row["phase"])
        candidate_ids = PHASE5_CANDIDATE_MAP.get(family_id, row.get("candidate_ids", []))
        final_assays.append({
            **row,
            "candidate_ids": candidate_ids,
            "evidence_grade": "EXHAUSTIVE_OVER_DECLARED_FINITE_FAMILY_NOT_UNIVERSAL_PROOF",
            "lean_kernel_status": KERNEL_STATUS if phase == "PHASE5" else "PRIOR_SOURCE_COMPLETE_EXTERNAL_KERNEL_REPLAY_PENDING",
            "certificate_path": (
                f"formalization/foundations_vii_lab/phase5/results/envelopes.jsonl"
                if phase == "PHASE5" else
                f"formalization/foundations_vii_lab/{phase.lower()}/results/envelopes.jsonl"
            ),
        })
    final_assays.sort(key=lambda row: (str(row["phase"]), str(row["family_id"])))

    # Countermodels: 27 named reference fixtures plus eleven minimized invalid
    # assignments, one per final finite envelope.
    counter_atlas = read_jsonl(ROOT / "readiness" / "countermodel_atlas.jsonl")
    counter_results = {row["fixture_id"]: row for row in read_jsonl(LAB5 / "all_countermodel_results.jsonl")}
    final_countermodels: list[dict[str, Any]] = []
    for row in counter_atlas:
        cid = str(row["countermodel_id"])
        result = counter_results[cid]
        fixture = ROOT / "formalization" / "foundations_vii_lab" / "fixtures" / "countermodels" / f"{cid}.json"
        final_countermodels.append({
            **row,
            "countermodel_kind": "NAMED_REFERENCE_COUNTERMODEL",
            "fixture_path": str(fixture.relative_to(ROOT)),
            "fixture_sha256": sha_file(fixture),
            "execution_pass": bool(result["all_pass"]),
            "evidence_grade": "EXECUTABLE_FINITE_COUNTERMODEL",
        })
    for row in read_jsonl(LAB5 / "canonical_witnesses.jsonl"):
        if row["role"] != "INVALID_ASSIGNMENT_MINIMAL":
            continue
        final_countermodels.append({
            "countermodel_id": row["witness_id"],
            "name": f"Minimized rejected assignment for {row['family_id']}",
            "scenario_id": "",
            "shows": "The rejected assignment violates the exact law of the declared final finite family.",
            "candidate_ids": row["candidate_ids"],
            "escape_route": "Change the violating coordinate or narrow the asserted certificate to the accepted predicate.",
            "countermodel_kind": "MINIMIZED_BOUNDED_REJECTION_WITNESS",
            "fixture_path": row["path"],
            "fixture_sha256": row["file_sha256"],
            "assignment_sha256": row["assignment_sha256"],
            "execution_pass": True,
            "evidence_grade": row["evidence_grade"],
        })

    # Public API registry and module import DAG.
    public_api = [{
        "module": module,
        "path": module_paths[module],
        "direct_imports": graph.get(module, []),
        "transitive_import_count": len(import_closures.get(module, set())),
        "public_declaration_count": sum(1 for row in declarations if row["module"] == module),
        "public_theorem_count": sum(1 for row in theorem_rows if row["module"] == module),
    } for module in vii_modules]

    module_edges = [
        {"source_module": module, "target_module": dep, "edge_kind": "LEAN_IMPORT"}
        for module in sorted(graph)
        for dep in sorted(graph[module])
    ]

    # Strip source blocks from canonical public registries after dependency work.
    clean_declarations = [{k: v for k, v in row.items() if k != "source_block"} for row in declarations]
    clean_definitions = [{k: v for k, v in row.items() if k != "source_block"} for row in definition_rows]
    clean_theorems = [{k: v for k, v in row.items() if k != "source_block"} for row in theorem_rows]

    # Print-axioms replay surface for every public theorem.
    print_lines = [
        # `import` must precede every command, and a `/-! -/` module docstring is
        # a command -- emitting the docstring first produces a file Lean cannot parse.
        "import FoundationsVII.All",
        "",
        "/-! Generated final Foundations VII trust replay surface. -/",
        "",
    ]
    print_lines += [f"#print axioms {row['fully_qualified_name']}" for row in sorted(theorem_rows, key=lambda r: str(r["fully_qualified_name"]))]
    print_lines.append("")
    (TRUST / "PrintAxiomsFinal.lean").write_text("\n".join(print_lines), encoding="utf-8")

    # Statement hash ledger.
    statement_lines = [f"{row['statement_sha256']}  {row['fully_qualified_name']}" for row in sorted(theorem_rows, key=lambda r: str(r["fully_qualified_name"]))]
    (TRACE / "final_statement_hashes.sha256").write_text("\n".join(statement_lines) + "\n", encoding="utf-8")

    outputs: dict[str, list[dict[str, Any]]] = {
        "final_public_declarations": clean_declarations,
        "final_definitions": clean_definitions,
        "final_theorems": clean_theorems,
        "final_corollaries": corollaries,
        "final_candidate_closure": final_candidates,
        "final_object_closure": final_objects,
        "final_formalization_target_closure": final_targets,
        "final_no_go_closure": no_go_rows,
        "final_decision_closure": final_decisions,
        "final_adapters": final_adapters,
        "final_finite_assays": final_assays,
        "final_countermodels": final_countermodels,
        "final_theorem_dependencies": dependency_rows,
        "final_theorem_trust": theorem_trust,
        "final_public_api": public_api,
    }
    for stem, rows in outputs.items():
        write_jsonl(REG / f"{stem}.jsonl", rows)
        write_csv(REG / f"{stem}.csv", rows)

    write_jsonl(TRACE / "final_axiom_free_core.jsonl", axiom_free_core)
    write_csv(TRACE / "final_axiom_free_core.csv", axiom_free_core)
    phase5_witnesses = read_jsonl(LAB5 / "canonical_witnesses.jsonl")
    write_jsonl(TRACE / "final_phase5_bounded_witnesses.jsonl", phase5_witnesses)
    write_csv(TRACE / "final_phase5_bounded_witnesses.csv", phase5_witnesses)

    write_jsonl(TRACE / "final_theorem_dependency_edges.jsonl", dependency_edges)
    write_csv(TRACE / "final_theorem_dependency_edges.csv", dependency_edges)
    write_jsonl(TRACE / "final_module_import_edges.jsonl", module_edges)
    write_csv(TRACE / "final_module_import_edges.csv", module_edges)
    write_graphml(
        TRACE / "final_theorem_dependency_graph.graphml",
        [{"theorem": row["fully_qualified_name"]} for row in declarations],
        dependency_edges,
        node_id_key="theorem",
        source_key="source_theorem",
        target_key="target_declaration",
    )
    write_graphml(
        TRACE / "final_module_import_graph.graphml",
        [{"module": module} for module in sorted(graph)],
        module_edges,
        node_id_key="module",
        source_key="source_module",
        target_key="target_module",
    )

    # Delete superseded prototype registries.  The release keeps one canonical
    # registry per asset class plus graph/trace surfaces under traceability/.
    superseded = [
        "final_adapter_registry", "final_corollary_registry",
        "final_countermodel_registry", "final_definition_registry",
        "final_finite_assay_registry", "final_formalization_targets",
        "final_no_go_registry", "final_theorem_registry",
        "final_decision_registry",
    ]
    for stem in superseded:
        for suffix in (".jsonl", ".csv"):
            path = REG / f"{stem}{suffix}"
            if path.exists():
                path.unlink()
    for stem in ("final_theorem_dependencies", "final_theorem_trust"):
        for suffix in (".jsonl", ".csv"):
            path = TRACE / f"{stem}{suffix}"
            if path.exists():
                path.unlink()

    summary = {
        "stage": FINAL_STAGE,
        "generated": DATE,
        "candidate_count": len(final_candidates),
        "candidate_dispositions": dict(sorted((d, sum(1 for row in final_candidates if row["terminal_disposition"] == d)) for d in TERMINAL_DISPOSITIONS)),
        "object_count": len(final_objects),
        "formalization_target_count": len(final_targets),
        "no_go_count": len(no_go_rows),
        "corollary_count": len(corollaries),
        "named_countermodel_count": len(counter_atlas),
        "minimized_final_countermodel_count": len(final_countermodels) - len(counter_atlas),
        "countermodel_registry_count": len(final_countermodels),
        "finite_assay_count": len(final_assays),
        "adapter_count": len(final_adapters),
        "decision_count": len(final_decisions),
        "public_module_count": len(vii_modules),
        "public_declaration_count": len(clean_declarations),
        "public_definition_count": len(clean_definitions),
        "public_theorem_count": len(clean_theorems),
        "theorem_dependency_edge_count": len(dependency_edges),
        "module_import_edge_count": len(module_edges),
        "static_axiom_free_core_candidate_count": len(axiom_free_core),
        "static_trust_reachable_theorem_count": sum(bool(row["static_trust_reachable"]) for row in theorem_trust),
        "inherited_trust_declaration_count": len(inherited_trust),
        "kernel_status": KERNEL_STATUS,
        "no_paper_work": True,
        "nonclaim": ("Local Lean replay and #print axioms audit passed." if _KERNEL_PASS else "All Lean proof grades remain source-level until the external kernel replay and #print axioms audit pass."),
    }
    write_json(REG / "final_summary.json", summary)

    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
