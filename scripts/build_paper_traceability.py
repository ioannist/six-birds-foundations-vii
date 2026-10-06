#!/usr/bin/env python3
"""Build the PP-05 paper traceability map from the frozen registries.

One row per catalog entry: cluster and section from PP-01 D2, then the candidate's
disposition, its Lean declarations, its finite assays, its countermodels, its no-go
fronts and cross-family corollaries.

This is a *locator*, not a content cache. Drafting reads FROM the sources it names,
never from this table's own fields, and the table is regenerated rather than edited
whenever the registries move.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
OUT_CSV = ROOT / "paper_prep" / "PP-05_traceability.csv"
OUT_JSON = ROOT / "paper_prep" / "PP-05_traceability.json"

# PP-01 D2: chapter -> (cluster, paper section). Ch01/11/12 are front/back matter.
CHAPTER_PLACEMENT = {
    "Ch01": ("—", "S2 Apparatus + S4 Inheritance and bridge discipline"),
    "Ch02": ("A", "S5 Cluster A — Access and admission"),
    "Ch03": ("A", "S5 Cluster A — Access and admission"),
    "Ch04": ("B", "S6 Cluster B — Contact and join"),
    "Ch05": ("B", "S6 Cluster B — Contact and join"),
    "Ch06": ("B", "S6 Cluster B — Contact and join"),
    "Ch07": ("C", "S7 Cluster C — Enablement and descent"),
    "Ch08": ("C", "S7 Cluster C — Enablement and descent"),
    "Ch09": ("D", "S8 Cluster D — Dynamics and residue"),
    "Ch10": ("D", "S8 Cluster D — Dynamics and residue"),
    "Ch11": ("—", "S10 Two-Theory World and finite laboratories"),
    "Ch12": ("—", "S12 Deferred candidates and future work"),
}

# PP-04 §3: the binding environment per disposition.
ENVIRONMENT = {
    "CONDITIONAL_THEOREM": "theorem",
    "FORMAL_SCHEMA": "definition|remark",
    "REFUTED_CANDIDATE": "remark(+theorem for surviving form)",
    "CLOSED_DEFERRAL": "remark",
    "CONSTRUCTIVE_COUNTERMODEL": "theorem(existence)",
    "LEAN_DECIDABLE_FINITE": "theorem(decidable, cite N)",
}


def jsonl(name: str) -> list[dict]:
    return [json.loads(l) for l in (REG / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def index_by_candidate(rows: list[dict], key: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for r in rows:
        for cid in r.get("candidate_ids") or []:
            out.setdefault(cid, []).append(str(r.get(key, "")))
    return out


def main() -> int:
    candidates = {r["candidate_id"]: r for r in jsonl("final_candidate_closure")}
    nogos = index_by_candidate(jsonl("final_no_go_closure"), "asset_id")

    chapters = [json.loads(l) for l in (ROOT / "vii" / "chapter" / "chapter_nodes.jsonl").read_text().splitlines() if l.strip()]
    placement = {}
    for ch in chapters:
        cids = ch["candidate_ids"]
        cids = json.loads(cids.replace("'", '"')) if isinstance(cids, str) else cids
        for cid in cids:
            placement[cid] = (ch["chapter_id"], ch["title"])

    def j(v):
        return ";".join(str(x) for x in (v or []))

    rows = []
    for cid, c in sorted(candidates.items()):
        chap, title = placement.get(cid, ("\u2014", "UNPLACED"))
        cluster, section = CHAPTER_PLACEMENT.get(chap, ("\u2014", "UNPLACED"))
        disp = str(c.get("terminal_disposition") or "")
        decls = c.get("lean_declarations") or []
        rows.append({
            "candidate_id": cid,
            "name": c.get("name", ""),
            "cluster": cluster,
            "paper_section": section,
            "chapter": chap,
            "chapter_title": title,
            "disposition": disp,
            "required_environment": ENVIRONMENT.get(disp, "UNMAPPED"),
            "proof_grade": c.get("proof_grade", ""),
            "kernel_status": c.get("kernel_status", ""),
            "controlling_asset_id": c.get("controlling_asset_id", ""),
            "lean_declaration_count": len(decls),
            "lean_declarations": j(decls),
            "formalization_targets": j(c.get("formalization_targets")),
            "finite_assays": j(c.get("finite_assay_ids")),
            "countermodels": j(c.get("countermodels")),
            "positive_models": j(c.get("positive_models")),
            "null_models": j(c.get("null_models")),
            "no_go_fronts": j(sorted(nogos.get(cid, []))),
            "corollaries": j(c.get("corollary_ids")),
            "exact_hypotheses_count": len(c.get("exact_hypotheses") or []),
            "nonclaim_count": len(c.get("nonclaims") or []),
            "escape_route_count": len(c.get("escape_routes") or []),
            "registry_row": f"science/registry/final_candidate_closure.jsonl#{cid}",
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    OUT_JSON.write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    unplaced = [r["candidate_id"] for r in rows if r["chapter"] == "—"]
    unmapped = [r["candidate_id"] for r in rows if r["required_environment"] == "UNMAPPED"]
    noleans = [r["candidate_id"] for r in rows if r["lean_declaration_count"] == 0]
    print(json.dumps({
        "rows": len(rows),
        "clusters": {c: sum(1 for r in rows if r["cluster"] == c) for c in "ABCD"},
        "front_back_matter": sum(1 for r in rows if r["cluster"] == "—"),
        "unplaced_candidates": unplaced,
        "unmapped_dispositions": unmapped,
        "candidates_without_lean_declarations": noleans,
        "total_lean_declarations_cited": sum(r["lean_declaration_count"] for r in rows),
        "candidates_with_no_nonclaim": [r["candidate_id"] for r in rows if r["nonclaim_count"] == 0],
    }, indent=1))
    return 1 if (unplaced or unmapped) else 0


if __name__ == "__main__":
    raise SystemExit(main())
