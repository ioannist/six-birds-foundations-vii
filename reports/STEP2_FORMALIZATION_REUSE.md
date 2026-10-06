# Step-2 formalization reuse and proof posture

## Inherited active scaffold

- Unique active Lean modules: **123**.
- Unique declarations: **2587**.
- Theorem declarations: **793**.
- Resolved local import edges: **297**; unresolved imports: **0**.
- Lexical `sorry` / `admit` tokens: **0 / 0**.
- Inherited trust surface: **1 axiom and 5 opaque declarations**.
- Foundations VII declarations: **0**.

## Claim-level mapping census

`MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION`=1, `MATCHED_IMPORTED_LAW_DECLARATION`=80, `NO_MATCH`=1269, `PAPER_DISCLOSED_ASSET_NOT_IMPORTED`=1415, `PLAUSIBLE_IMPORTED_MATCH_REQUIRES_STATEMENT_REVIEW`=52, `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT`=4

`MATCHED_IMPORTED_LAW_DECLARATION` means the law disclosure/traceability ledgers assign a locally imported declaration to the source row. `MATCHED_IMPORTED_ABSTRACT_CORE_DECLARATION` means an imported theorem captures a reusable abstract core but is not certified identical to the paper theorem. `PRIOR_SCAFFOLD_CORE_CORRESPONDENCE_REQUIRES_STATEMENT_AUDIT` marks a plausible typed core whose carrier, hypotheses, or conclusion still require an explicit adapter. `PLAUSIBLE_IMPORTED_MATCH_REQUIRES_STATEMENT_REVIEW` is lexical navigation only. `PAPER_DISCLOSED_ASSET_NOT_IMPORTED` means the paper reports a formal/computational asset but the corresponding source is absent from the supplied active scaffold or no claim-specific local declaration was assigned. `NO_MATCH` means no local claim-level match was assigned. None of these statuses silently implies a fresh local kernel replay.

## Law-series reuse

- Source registry coverage: **52 F**, **16 E**, **13 G**, and **8 no-go** rows.
- Reuse contracts: **89**, one per prior law/no-go row.
- Source audit reviewed **2022 F/E/G-shaped tokens**; **217 substantive occurrences** form **45 grouped target-paper/law bridges**. Rejected local figures, exhibits, workflow items, range endpoints, and mathematical symbols remain visible in the audit ledger.
- No-go/prior-scaffold correspondence: **8 rows**, with exact matches, abstract-core correspondences, missing local assets, and no-match cases kept distinct.
- The F/E/G and no-go paper statements remain controlling even where multiple component claims or Lean declarations are associated with one numbered result.

## Machine-status boundary

The supplied repositories request Lean 4.28.0. That toolchain was unavailable in the execution environment. The build therefore verifies source presence, declaration indexing, trust accounting, byte identity, and static import closure, while preserving prior paper-side theorem/test claims as inherited evidence rather than restating them as a new kernel run.
