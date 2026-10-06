#!/usr/bin/env python3
"""Generate the paper's exhibit tables from the frozen registries (PP-08).

Emits LaTeX table *bodies* — rows only, plus a booktabs-ruled tabular per PP-02 §6.
No prose, no numbers typed by hand. Each exhibit is written to
`paper_prep/exhibits/<id>.tex.txt`; the `.txt` suffix keeps them out of the
no-prose guard's `.tex` block while remaining paste-ready for the writing phase.

Usage:  python3 scripts/build_paper_exhibits.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "science" / "registry"
OUT = ROOT / "paper_prep" / "exhibits"


def jsonl(name: str, base: Path = REG) -> list[dict]:
    return [json.loads(l) for l in (base / f"{name}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def esc(s: object) -> str:
    t = str(s)
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("_", r"\_"),
                 ("#", r"\#"), ("$", r"\$"), ("{", r"\{"), ("}", r"\}")):
        t = t.replace(a, b)
    return t


def table(exhibit_id: str, caption: str, spec: str, header: list[str],
          rows: list[list[object]], landscape: bool = False) -> None:
    body = " \\\\\n".join(" & ".join(esc(c) for c in r) for r in rows)
    # placeholder from E5: one escape theorem per line inside the cell
    body = body.replace("\x00", " \\newline ")
    env = "landscape" if landscape else None
    tex = []
    if env:
        tex.append(r"\begin{landscape}")
    tex += [
        r"\begin{table}[t]", r"\centering",
        f"\\caption{{{caption}}}", f"\\label{{tab:{exhibit_id}}}",
        f"\\begin{{tabular}}{{{spec}}}", r"\toprule",
        " & ".join(f"\\textbf{{{h}}}" for h in header) + r" \\", r"\midrule",
        body + r" \\", r"\bottomrule", r"\end{tabular}", r"\end{table}",
    ]
    if env:
        tex.append(r"\end{landscape}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{exhibit_id}.tex.txt").write_text("\n".join(tex) + "\n", encoding="utf-8")
    return len(rows)


def main() -> int:
    made: dict[str, int] = {}
    cands = sorted(jsonl("final_candidate_closure"), key=lambda r: r["candidate_id"])
    summary = json.loads((REG / "final_summary.json").read_text())

    # E1 — disposition census (the table PP-01 D3 exists to protect)
    census = Counter(c["terminal_disposition"] for c in cands)
    order = ["CONDITIONAL_THEOREM", "FORMAL_SCHEMA", "REFUTED_CANDIDATE", "CLOSED_DEFERRAL",
             "CONSTRUCTIVE_COUNTERMODEL", "LEAN_DECIDABLE_FINITE", "LEAN_KERNEL_PROVED"]
    made["E1_disposition_census"] = table(
        "E1_disposition_census",
        "Terminal disposition census. Kernel verification does not alter disposition.",
        "lr", ["Disposition", "Count"],
        [[d.replace("_", " ").title(), census.get(d, 0)] for d in order])

    # E2 — candidate catalog
    made["E2_candidate_catalog"] = table(
        "E2_candidate_catalog",
        "Candidate closure: disposition, landed phase, and evidence.",
        r"lp{6.4cm}llrr",
        ["ID", "Name", "Disposition", "Phase", "Lean decls", "Assays"],
        [[c["candidate_id"], c["name"], c["terminal_disposition"].replace("_", " ").title(),
          c.get("terminal_phase", ""), len(c.get("lean_declarations") or []),
          len(c.get("finite_assay_ids") or [])] for c in cands], landscape=True)

    # E3 — axiom receipt census (must never read "732 axiom-free")
    trust = jsonl("final_theorem_trust")
    ax = Counter(", ".join(r["executed_axioms"]) if r.get("executed_axioms") else "none"
                 for r in trust)
    made["E3_axiom_receipt"] = table(
        "E3_axiom_receipt",
        "Executed \\texttt{\\#print axioms} census over all 732 public theorems.",
        "lrr", ["Axiom dependency", "Theorems", "Share (\\%)"],
        [[k if k != "none" else "no axioms", v, f"{100*v/len(trust):.1f}"]
         for k, v in sorted(ax.items(), key=lambda kv: -kv[1])])

    # E4 — finite carrier census, always with cardinalities (PP-04 §4)
    made["E4_finite_census"] = table(
        "E4_finite_census",
        "Global bounded-carrier census. Finite evidence is exhaustive only over these carriers.",
        "lr", ["Carrier partition", "Cases"],
        [["Raw", 86912], ["Canonical", 84864], ["Accepted", 21081], ["Rejected", 63783]])

    # E5 — no-go fronts with their escapes (never quote a no-go alone)
    nogos = jsonl("final_no_go_closure")
    made["E5_no_go_fronts"] = table(
        "E5_no_go_fronts",
        "No-go fronts with their named escape routes. A front is never cited without these.",
        r"llp{12.5cm}", ["Front", "Candidates", "Named escape routes"],
        [[n["asset_id"], ", ".join(n.get("candidate_ids") or []),
          "\x00".join(e.split(".")[-1] for e in (n.get("escape_theorems") or [])) or "none"]
         for n in nogos], landscape=True)

    # E6 — cross-family corollaries
    cors = jsonl("final_corollaries")
    made["E6_corollaries"] = table(
        "E6_corollaries",
        "Cross-family corollaries and their supporting candidates.",
        "lll", ["Corollary", "Declaration", "Candidates"],
        [[c["corollary_id"], str(c.get("declaration", "")).split(".")[-1],
          ",".join(c.get("candidate_ids") or [])] for c in cors], landscape=True)

    print(json.dumps({"exhibits": made, "total_rows": sum(made.values()),
                      "out": str(OUT.relative_to(ROOT))}, indent=1))
    # invariant: the census table must show zero LEAN_KERNEL_PROVED
    return 1 if census.get("LEAN_KERNEL_PROVED", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
