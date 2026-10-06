#!/usr/bin/env python3
"""Build the PP-06 claim-grade and nonclaim ledger.

For every catalog entry this binds, in one row: what may be asserted, at what
grade, in which LaTeX environment, under which exact hypotheses, with which
nonclaims and which escape routes.

The point is to make grade inflation mechanically detectable rather than a matter
of a drafter's care. It emits a per-claim ledger plus a `forbidden_phrases` list
that a later prose lint can run against a draft.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
OUT_CSV = ROOT / "paper_prep" / "PP-06_claim_ledger.csv"
OUT_JSON = ROOT / "paper_prep" / "PP-06_claim_ledger.json"

# PP-04 §3. Per disposition: environment, the required sentence frame, and the
# verbs that may NOT be applied to a result of that grade.
GRADE_RULES = {
    "CONDITIONAL_THEOREM": {
        "environment": "theorem",
        "frame": "Under H1-Hk, <conclusion>.",
        "may_use": ["proved", "theorem", "holds under"],
        "must_not_use": ["in general", "always", "for all theories", "unconditionally"],
        "must_state": "every hypothesis, inside the theorem statement",
    },
    "FORMAL_SCHEMA": {
        "environment": "definition|remark",
        "frame": "<Object> is typed as <schema>; the schema records <what>.",
        "may_use": ["defines", "types", "records", "schema"],
        "must_not_use": ["proved", "theorem", "establishes", "demonstrates"],
        "must_state": "that it is a schema, not a theorem",
    },
    "REFUTED_CANDIDATE": {
        "environment": "remark(+theorem for surviving form)",
        "frame": "The unconditional form is refuted; what survives is <conditional form>.",
        "may_use": ["refuted", "fails unconditionally"],
        "must_not_use": ["open", "unproven", "not yet shown"],
        "must_state": "what survives conditionally",
    },
    "CLOSED_DEFERRAL": {
        "environment": "remark",
        "frame": "Closed as a deferral; the landed fragment is <fragment>.",
        "may_use": ["deferred", "closed as a deferral", "landed fragment"],
        "must_not_use": ["proved", "delivered", "in progress", "future work will"],
        "must_state": "which fragment landed and which part is deferred",
    },
    "CONSTRUCTIVE_COUNTERMODEL": {
        "environment": "theorem(existence)",
        "frame": "There exists a witness refuting <named claim>.",
        "may_use": ["exhibits", "witness", "refutes"],
        "must_not_use": ["refutes the idea that", "casts doubt on", "suggests"],
        "must_state": "the exact claim the witness kills",
    },
    "LEAN_DECIDABLE_FINITE": {
        "environment": "theorem(decidable, cite N)",
        "frame": "Decidable over the declared carrier (N = <cardinality>).",
        "may_use": ["decidable over", "exhaustive over the declared carrier"],
        "must_not_use": ["exhaustive", "complete", "for all", "in general"],
        "must_state": "the carrier cardinality",
    },
    "LEAN_KERNEL_PROVED": {
        "environment": "FORBIDDEN - no row carries this disposition (PP-01 D3)",
        "frame": "",
        "may_use": [],
        "must_not_use": ["*"],
        "must_state": "",
    },
}

# Verification axis never upgrades the disposition axis (PP-04 §3).
FORBIDDEN_PHRASES = [
    "kernel-verified theorem",
    "kernel-proved",
    "machine-proved theorem",
    "formally proved theorem",
    "proved by Lean",
    "verified theorem",
]


def jsonl(name: str) -> list[dict]:
    return [json.loads(l) for l in (REG / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    candidates = jsonl("final_candidate_closure")
    rows = []
    for c in sorted(candidates, key=lambda r: r["candidate_id"]):
        disp = str(c.get("terminal_disposition") or "")
        rule = GRADE_RULES.get(disp)
        if rule is None:
            print(f"UNKNOWN DISPOSITION {disp} on {c['candidate_id']}")
            return 1
        rows.append({
            "candidate_id": c["candidate_id"],
            "name": c.get("name", ""),
            "disposition": disp,
            "environment": rule["environment"],
            "sentence_frame": rule["frame"],
            "must_state": rule["must_state"],
            "may_use": ";".join(rule["may_use"]),
            "must_not_use": ";".join(rule["must_not_use"]),
            "proposed_conclusion": c.get("proposed_conclusion", ""),
            "exact_hypotheses": " | ".join(c.get("exact_hypotheses") or []),
            "nonclaims": " | ".join(c.get("nonclaims") or []),
            "escape_routes": " | ".join(c.get("escape_routes") or []),
            "kernel_status": c.get("kernel_status", ""),
        })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    OUT_JSON.write_text(json.dumps(
        {"forbidden_phrases": FORBIDDEN_PHRASES, "grade_rules": GRADE_RULES, "claims": rows},
        indent=1, sort_keys=True) + "\n", encoding="utf-8")

    from collections import Counter
    census = Counter(r["disposition"] for r in rows)
    missing_hyp = [r["candidate_id"] for r in rows
                   if r["disposition"] == "CONDITIONAL_THEOREM" and not r["exact_hypotheses"]]
    missing_non = [r["candidate_id"] for r in rows if not r["nonclaims"]]
    kernel_proved = census.get("LEAN_KERNEL_PROVED", 0)
    print(json.dumps({
        "claims": len(rows),
        "census": dict(sorted(census.items())),
        "LEAN_KERNEL_PROVED_must_be_zero": kernel_proved,
        "conditional_theorems_without_stated_hypotheses": missing_hyp,
        "claims_without_a_nonclaim": missing_non,
        "forbidden_phrase_count": len(FORBIDDEN_PHRASES),
    }, indent=1))
    return 1 if (kernel_proved or missing_hyp or missing_non) else 0


if __name__ == "__main__":
    raise SystemExit(main())
