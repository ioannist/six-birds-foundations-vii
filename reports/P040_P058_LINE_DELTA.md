# P040/P058 exact raw-TeX line delta

## Scope

This is the line-by-line version-control artifact required by Step 1 for unresolved near-duplicates. It aligns the immutable raw TeX sources exactly and emits a standard unified diff. It does **not** decide whether corresponding theorems are mathematically equivalent, which paper is canonical, or whether either paper supplies independent evidence.

## Source identity

- P040: `source/papers/Tsiokos_2026_The_Usefulness_of_Non_Descending_Objects_A_Six_Birds_Theory_of_Mathematical_Applicability.tex`; SHA-256 `ed6ca456595366976b575dae6376fabeda8f6a715172575cb0d092197208c143`; 5775 lines.
- P058: `source/papers/Tsiokos_2026_Why_Mathematics_Even_Works.tex`; SHA-256 `826e7c826dedd5a5185793527b48a05218b6ddd705a4217772450bf7a42fc122`; 5758 lines.

## Alignment census

- Exact raw-line SequenceMatcher ratio: **0.829099106911**.
- Alignment blocks: **505**.
- Equal / replace / delete / insert blocks: **253 / 221 / 18 / 13**.
- Equal raw lines: P040 **4781**, P058 **4781**.
- Non-equal raw lines: P040 **994**, P058 **977**.
- Unified diff length: **3240** lines.

## Products

- `reports/P040_P058_LINE_DELTA.csv` — all alignment blocks, including equal blocks, with exact one-based source ranges and bounded excerpts.
- `reports/P040_P058_RAW_TEX_DIFF.patch` — exact standard unified diff over the immutable raw TeX files.
- `generated/p040_p058_line_delta.json` — machine-readable source hashes and census.
- `reports/P040_P058_SECTION_DELTA.csv` — complementary 73-slot structural heading alignment.

## Step-2 boundary

The family remains `UNRESOLVED_VERSION_FAMILY`, with no canonical member. Step 2 must compare definitions, theorem statements, hypotheses, proof/evidence grades, nonclaims, and formalization references before any canonicalization or evidence deduplication beyond the existing family-level control.
