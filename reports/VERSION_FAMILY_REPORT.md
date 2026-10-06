# Version-family and duplicate report

## Decision

Step 1 found **no byte-identical paper roots** and one material near-duplicate/version family: `VF-SAU-01 = {P040, P058}`. Both files are retained. Their claims must not be counted as two independent results until Step 2 completes a claim-level comparison.

## VF-SAU-01 — mathematical-applicability / SAU family

- **P040 catalog title:** The Usefulness of Non-Descending Objects.
  - Internal `\title`: **Why Mathematics Even Works**.
  - Root SHA-256: `ed6ca456595366976b575dae6376fabeda8f6a715172575cb0d092197208c143`.
  - Source: `papers/Tsiokos_2026_The_Usefulness_of_Non_Descending_Objects_A_Six_Birds_Theory_of_Mathematical_Applicability.tex`.
- **P058 catalog title:** Why Mathematics Even Works.
  - Internal `\title`: **The Usefulness of Non-Descending Objects: A Six Birds Theory of Mathematical Applicability**.
  - Root SHA-256: `826e7c826dedd5a5185793527b48a05218b6ddd705a4217772450bf7a42fc122`.
  - Source: `papers/Tsiokos_2026_Why_Mathematics_Even_Works.tex`.

The normalized source-text five-word-shingle Jaccard is **0.6878**. Both expose the same 73-section architecture and the same Strict Audited Utility theorem family, while differing substantively in editorial organization and theorem presentation. The archive filenames and internal titles are crossed: the file catalogued as P040 internally calls itself *Why Mathematics Even Works*, while the file catalogued as P058 internally calls itself *The Usefulness of Non-Descending Objects*. This is a provenance defect, not grounds for silently renaming either frozen source.

**Ruling:** preserve the supplied filenames, stable IDs, and hashes; mark both `VF-SAU-01`; use one family-level evidence source in Step-1 synthesis. Step 1 records the 73-slot structural delta in `reports/P040_P058_SECTION_DELTA.*` and exact raw-TeX line alignment in `reports/P040_P058_LINE_DELTA.*` plus `reports/P040_P058_RAW_TEX_DIFF.patch`; a canonical member and theorem/claim-level delta remain deferred to Step 2.

## Exact duplicates

None among the 58 root TeX files.

## Nearest textual neighbors

The long-shingle similarity scan is a triage instrument, not a semantic identity test. The top pairs are:

| Pair | Jaccard | Step-1 classification |
|---|---:|---|
| P040 / P058 | 0.6878 | unresolved version family |
| P004 / P009 | 0.0401 | thematically related; not versions |
| P024 / P025 | 0.0337 | thematically related; not versions |
| P004 / P017 | 0.0219 | thematically related; not versions |
| P004 / P039 | 0.0217 | thematically related; not versions |
| P016 / P039 | 0.0216 | thematically related; not versions |
| P025 / P039 | 0.0205 | thematically related; not versions |
| P021 / P039 | 0.0203 | thematically related; not versions |
| P003 / P037 | 0.0183 | thematically related; not versions |
| P016 / P022 | 0.0179 | thematically related; not versions |
| P009 / P017 | 0.0178 | thematically related; not versions |
| P011 / P039 | 0.0176 | thematically related; not versions |

Examples below the version threshold include source/application pairs and papers sharing a problem family. Their overlap does not license claim duplication, claim transfer, or replacement of one source by another.

## Step-2 obligation

Build the theorem/claim-level delta for P040/P058 on top of the completed 73-slot structural alignment and exact raw-source line ledger, identify the later/controlling statement for each theorem, and record whether differences are editorial, hypothesis-level, proof-level, or status-level. The line ledger is navigation and provenance control, not a semantic equivalence judgment. Until then, all citations remain member-specific.
