#!/usr/bin/env python3
"""Build the exact inherited-adapter modules and machine-readable ledger."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "formalization" / "step3" / "prior_reuse_matrix.csv"
TARGETS = ROOT / "formalization" / "step3" / "formalization_targets.csv"
OUT = ROOT / "formalization" / "lean" / "FoundationsVII" / "Prior"
REG = ROOT / "science" / "registry"

TARGET_TYPES = {
    "FT01": "FoundationsVII.DomainState / graded access status",
    "FT02": "FoundationsVII.AdmissionTransition / FoundationsVII.ReachabilityWitness",
    "FT03": "bootstrap obstruction over FoundationsVII.AdmissionTransition",
    "FT04": "FoundationsVII.ProspectiveCommitment / FoundationsVII.BudgetLedger",
    "FT05": "FoundationsVII.SourceLedger / FoundationsVII.BridgeContract / FoundationsVII.BridgeLedger",
    "FT06": "FoundationsVII.ContactWitness",
    "FT07": "FoundationsVII.JoinCertificate",
    "FT08": "strictness component of FoundationsVII.JoinCertificate",
    "FT09": "FoundationsVII.JoinObstruction / FoundationsVII.BudgetLedger",
    "FT10": "FoundationsVII.NonInteractionCertificate",
    "FT11": "FoundationsVII.EnablementRecord",
    "FT12": "endogenous-source criterion over FoundationsVII.EnablementRecord",
    "FT13": "transmission/descent fidelity over FoundationsVII.EnablementRecord",
    "FT14": "finite confluence records over FoundationsVII.InteractionRecord",
    "FT15": "holonomy/arrow-separated FoundationsVII.InteractionRecord",
    "FT16": "FoundationsVII.BudgetLedger / FoundationsVII.ObserverOccupancyRecord",
    "FT17": "FoundationsVII.AuditRecord / GradedClaim / NegativeEvidenceRecord",
    "FT18": "no-free access/join protocol records",
    "FT19": "retention component of FoundationsVII.JoinCertificate",
    "FT20": "FoundationsVII.JoinObstruction / finite reference-world semantics",
}
PRESERVED = {
    "FT01": ["typed claim/access coordinates", "declared audit scope"],
    "FT02": ["explicit reachability record", "exclusive reachability status"],
    "FT03": ["declared carrier and horizon", "absence of reachable repair generator"],
    "FT04": ["declared timestamps and budget allocation", "source-located allocation record"],
    "FT05": ["fine source tag", "source/target carrier identity", "declared transport token"],
    "FT06": ["typed instrument claim and subject/interface ownership"],
    "FT07": ["declared repair-join inputs", "well-definedness premises"],
    "FT08": ["strict self-extension/nonfactorization witness"],
    "FT09": ["budget feasibility premises", "typed obstruction status"],
    "FT10": ["the original institutional rewrite hypotheses and covered carrier"],
    "FT11": ["declared reachability record and scope"],
    "FT12": ["absence of reachable generator under the inherited criterion"],
    "FT13": ["descent-square maps and recovery premise"],
    "FT14": ["declared finite run system and confluence/nonconfluence hypotheses"],
    "FT15": ["loop, quotient, and current/predictive interfaces"],
    "FT16": ["binding budget/positive-cost premises"],
    "FT17": ["claim bookkeeping, grade, and explicit nonclaims"],
    "FT18": ["old access retention and financed refinement map"],
    "FT19": ["old identity and persistence-extension map"],
    "FT20": ["residual status / adequacy-defect witness and exact carrier"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lean_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def lean_list(values: list[str]) -> str:
    return "[" + ", ".join(lean_string(v) for v in values) + "]"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def declaration_found(row: dict[str, str]) -> bool:
    text = (ROOT / row["file"]).read_text(encoding="utf-8")
    pattern = re.compile(
        r"(?m)^\s*(?:structure|def|abbrev|inductive|theorem|lemma|opaque|axiom)\s+"
        + re.escape(row["declared_name"])
        + r"\b"
    )
    return bool(pattern.search(text))


def write_csv_jsonl(base: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    base.parent.mkdir(parents=True, exist_ok=True)
    with base.with_suffix(".csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False, sort_keys=True) if isinstance(v, (list, dict)) else v for k, v in row.items()})
    with base.with_suffix(".jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    REG.mkdir(parents=True, exist_ok=True)
    matrix = read_csv(MATRIX)
    target_rows = {row["target_id"]: row for row in read_csv(TARGETS)}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in matrix:
        grouped[row["target_id"]].append(row)

    ledger: list[dict[str, Any]] = []
    all_imports = ["FoundationsVII.Prior.Metadata", "FoundationsVII.Prior.Contract", "FoundationsVII.Prior.FoundationalObjects"]
    for target_id in sorted(grouped, key=lambda x: int(x[2:])):
        rows = grouped[target_id]
        modules = list(dict.fromkeys(row["module"] for row in rows))
        lines = [
            "/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/",
            "",
            "import FoundationsVII.Prior.Metadata",
        ]
        lines += [f"import {module}" for module in modules]
        lines += ["", "namespace FoundationsVII.Prior", ""]
        for i, row in enumerate(rows, start=1):
            decl_name = f"adapter_{target_id.lower()}_{slug(row['declared_name'])}_{i:02d}"
            adapter_id = f"FVII-ADP-{int(target_id[2:]):02d}-{i:02d}"
            added = [
                f"VII-owned source, audit, and disposition fields for {target_rows[target_id]['name']}",
                "explicit accepted bridge before semantic reuse",
            ]
            lost = ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
            trust = ["exact imported declaration; theorem-level axioms are separately audited"]
            lines += [
                f"#check {row['fully_qualified_name']}",
                f"def {decl_name} : AdapterMetadata :=",
                f"  {{ adapterId := {lean_string(adapter_id)}",
                f"    formalizationTarget := {lean_string(target_id)}",
                f"    sourceModule := {lean_string(row['module'])}",
                f"    sourceDeclaration := {lean_string(row['fully_qualified_name'])}",
                f"    sourceType := {lean_string(row['kind'] + ' ' + row['fully_qualified_name'])}",
                f"    targetType := {lean_string(TARGET_TYPES[target_id])}",
                f"    preservedHypotheses := {lean_list(PRESERVED[target_id])}",
                f"    addedHypotheses := {lean_list(added)}",
                f"    lostHypotheses := {lean_list(lost)}",
                f"    trustDependencies := {lean_list(trust)} }}",
                "",
            ]
            source_path = ROOT / row["file"]
            ledger.append({
                "adapter_id": adapter_id,
                "target_id": target_id,
                "target_name": target_rows[target_id]["name"],
                "source_module": row["module"],
                "source_declaration": row["fully_qualified_name"],
                "source_file": row["file"],
                "source_line": int(row["line"]),
                "source_kind": row["kind"],
                "source_sha256": sha256(source_path),
                "source_declaration_found": declaration_found(row),
                "target_type": TARGET_TYPES[target_id],
                "preserved_hypotheses": PRESERVED[target_id],
                "added_hypotheses": added,
                "lost_hypotheses": lost,
                "trust_dependencies": trust,
                "candidate_ids": json.loads(row["candidate_ids"]),
                "lean_adapter_module": f"FoundationsVII.Prior.{target_id}",
                "lean_metadata_declaration": f"FoundationsVII.Prior.{decl_name}",
                "kernel_status": "SOURCE_AUTHORED_EXTERNAL_KERNEL_REPLAY_PENDING",
                "status": "PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE",
            })
        lines += ["end FoundationsVII.Prior", ""]
        (OUT / f"{target_id}.lean").write_text("\n".join(lines), encoding="utf-8")
        all_imports.append(f"FoundationsVII.Prior.{target_id}")

    all_lines = [
        "/-! Exact inherited-adapter root. Every FT module imports/checks only its listed source declarations. -/",
        "",
    ] + [f"import {module}" for module in all_imports] + [""]
    (OUT / "All.lean").write_text("\n".join(all_lines), encoding="utf-8")

    fields = list(ledger[0])
    write_csv_jsonl(REG / "inherited_adapter_ledger", ledger, fields)
    summary = {
        "targets": len(grouped),
        "adapter_rows": len(ledger),
        "all_source_declarations_found": all(r["source_declaration_found"] for r in ledger),
        "status": "PASS" if len(grouped) == 20 and len(ledger) == 30 and all(r["source_declaration_found"] for r in ledger) else "FAIL",
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
