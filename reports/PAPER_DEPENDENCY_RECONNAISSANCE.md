# Step-1 corpus-paper dependency reconnaissance

## Scope and authority

This report closes the original Step-1 requirement that every survey card name its dependency papers. It parses citation commands in the frozen supplied TeX roots and resolves only an explicit, reviewable table of in-corpus citation-key aliases. It is a **navigation graph**, not a theorem dependency graph.

A citation edge does **not** establish that a result is imported, that hypotheses match, that a bridge is valid, that two papers are independent evidence, or that a cited paper is the unique source of a construction. Those judgments remain Step-2 claim/bridge work.

## Census

- Papers covered: **58**.
- Resolved directed in-corpus citation edges: **240**.
- Papers with at least one resolved in-corpus citation: **53**.
- Papers with an unresolved internal-looking key: **2**.
- Papers naming a corpus-like work outside the 58-paper catalog: **5**.
- P039 remains source-package blocked; absence of resolved citations there is not evidence of independence.

## Most-cited supplied corpus papers at survey depth

| Paper | Incoming source-paper count |
|---|---:|
| P031 — Foundations I: Foundations of Emergence Calculus | 37 |
| P027 — Foundations II: Admissibility Meta-Theory and Exact Six | 17 |
| P026 — Foundations III: Finite Audited Interaction Calculus | 13 |
| P012 — Holonomy with Memory | 11 |
| P015 — Locally Boolean, Globally Obstructed | 9 |
| P047 — Emergent Geometric and Thermodynamic Regimes | 8 |
| P009 — Emergence IS the Needle Killer | 7 |
| P016 — Marking, Erasure, and Recombination on Fixed Support | 7 |
| P021 — Promotion Criteria and Surviving Packages | 7 |
| P022 — Recombination Witnesses on Fixed Support | 7 |
| P046 — A Mathematics Is a Theory | 7 |
| P004 — Adequacy Residuals and Blind-Spot Currency | 6 |
| P006 — Audited Operational Realisability (AOR) | 6 |
| P014 — Internal Structure of a Surviving Promoted Package | 5 |
| P028 — Foundations IV: Layer-Agnostic Structural Laws | 5 |
| P038 — Strict Theory Extension on a Lawful Continuous Cantor Shell | 5 |
| P007 — Carrier Exactification after Promotion | 4 |
| P032 — No-Go Theorems for Audited Emergence | 4 |
| P033 — Protocol Trap: Holonomy without Entropy Production | 4 |
| P054 — Currency, Constraint Duality, and Shadow Prices | 4 |

## Papers with unresolved or out-of-corpus internal references

| Source | Unresolved internal keys | Out-of-corpus keys |
|---|---|---|
| P030 | — | Tsiokos2026Life [Life-theory paper; not in the 58-paper catalog] |
| P053 | SBTRecognition [recognition-source key; no unique 58-paper target recoverable from supplied roots] | — |
| P056 | — | life [A Life Is a Theory; not in the 58-paper catalog]; tobe [What It Is Like to Be a Layer proposal; not in the 58-paper catalog]; tte [Tests to Events / Born-route repository; not in the 58-paper catalog] |
| P055 | — | six_birds_life [Life-theory paper/repository; not in the 58-paper catalog] |
| P002 | Tsiokos2026Stone [ambiguous cross-domain Six Birds paper key; external bibliography absent] | — |
| P001 | — | Tsiokos2026WakeStone [To Wake a Stone / A Life Is a Theory; not in the 58-paper catalog] |
| P047 | — | Tsiokos2026Life [Life-theory paper; not in the 58-paper catalog] |

## Machine-readable products

- `corpus/paper_dependency_edges.csv` — resolved source-to-target citation edges with keys and source lines.
- `corpus/paper_dependency_summary.csv` — exactly one status row per paper.
- `corpus/paper_citation_key_audit.csv` — classification of every distinct citation key used by every root.
- `generated/paper_dependency_reconnaissance.json` — complete per-paper reconstruction data and census.

## Step-2 boundary

Step 2 must replace citation-level navigation with claim-level records: exact source statement, hypotheses, object typing, proof/evidence grade, local Lean declaration where any, target use, and an explicit bridge verdict. This Step-1 graph is useful for reading order and omission detection only.
