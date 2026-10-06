# Step-2 validation

- **Status:** `PASS`.
- **Checks:** 42 total; 42 passed; 0 failed.
- **Date:** 2026-07-26.

| Check | Status | Detail |
|---|---|---|
| required Step-2 products exist | `PASS` | 31 required products present |
| paper catalog is complete and unique | `PASS` | papers=58 unique=58 |
| canonical claim count and ID uniqueness | `PASS` | claims=2821 unique_ids=2821 |
| all 58 papers occur in the canonical claim corpus | `PASS` | represented=58 missing=[] |
| every claim satisfies the claim-record schema | `PASS` | no schema errors |
| claim IDs are sequential and stable within each paper | `PASS` | all sequential |
| per-paper JSONL files exactly match the canonical corpus | `PASS` | all 58 match |
| all 58 Markdown dossiers index every canonical claim | `PASS` | all dossiers complete |
| all 58 canonical dossier JSON files match claim IDs, status, and bridge completion | `PASS` | all dossier JSON files canonical |
| claim provenance resolves to immutable source and expanded TeX | `PASS` | all source paths/ranges/hashes resolve |
| all claim-level nonclaim and scope pointers resolve | `PASS` | all cross-claim boundaries resolve |
| all explicit formal TeX environments are represented exactly once | `PASS` | expected_envs=1356 claim_envs=1356 unmatched=0 extra=0 |
| claim extraction lanes are complete and non-overlapping | `PASS` | lanes={'SOURCE_EXTRACTED_COMPOSITE': 58, 'SOURCE_EXTRACTED_FORMAL_SURFACE': 1356, 'SOURCE_EXTRACTED_NAMED_SECTION_SURFACE': 532, 'SOURCE_EXTRACTED_EXPLICIT_PROSE_SURFACE': 875} |
| all 58 papers have exactly one source-located composite abstract thesis | `PASS` | theses=58 missing=[] duplicates=[] |
| all explicit abstract nonclaims, scope boundaries, and open obligations are component records | `PASS` | expected_components=48 actual_components=48 missing_surfaces=[] missing=[] extra=[] |
| boilerplate and checklist text is excluded from claims | `PASS` | no boilerplate markers |
| P039 is the sole source-package blocker and remains abstract-only | `PASS` | blocked_claims=2 P039_claims=2 |
| coverage has advanced to 57 BRIDGED papers with P039 blocked | `PASS` | states={'BRIDGED': 57, 'BLOCKED': 1} P039=BLOCKED |
| claim-level formalization status preserves statement and kernel boundaries | `PASS` | all formalization records conservative |
| Step 2 introduces no Foundations VII Lean declarations or Lean-source changes | `PASS` | formalization/lean unchanged from Step 1 |
| all 52 F, 16 E, 13 G and 8 no-go rows resolve to canonical claims | `PASS` | registry=52/16/13/8 resolved_laws=81 resolved_ng=8 |
| bridge atlas count and IDs are canonical | `PASS` | bridges=374 unique_ids=374 |
| every bridge satisfies the bridge schema | `PASS` | no schema errors |
| bridge claim references, classes, and audit paths close | `PASS` | all bridge references valid |
| all 240 in-corpus paper invocations have a bridge row | `PASS` | dependency_edges=240 citation_bridges=240 signature_delta=0 |
| named-law source audit is complete and rejects known local-label collisions | `PASS` | candidates=2022 accepted_occurrences=217 accepted_pairs=45 audit_errors=[] false_bridges=[] |
| every accepted named prior-law occurrence has exactly one grouped bridge | `PASS` | accepted_occurrences=217 grouped_bridges=45 pair_delta=0 coverage_delta=0 |
| all prior F/E/G/no-go rows have a future-reuse contract | `PASS` | contracts=89 expected_ids=89 missing=[] |
| all eight no-go results retain exact statements, carrier, hypotheses, scope, non-scope, and escape | `PASS` | rows=8 errors=[] |
| no-go results are conservatively aligned to the inherited Lean scaffold | `PASS` | rows=8 errors=[] |
| invalid-transfer report covers recurrent SBT role collapses | `PASS` | rows=20 missing_fragments=[] |
| interaction/access/enablement taxonomy is complete | `PASS` | 14 matrices verified |
| all 14 domain applications have concrete carrier/interface/audit maps or a source block | `PASS` | applications=14 errors=[] P039=BLOCKED_SOURCE |
| example/carrier registry is populated and source-grounded | `PASS` | rows=24 kinds={'APPLICATION_PRESSURE_CARRIER': 14, 'SOURCE_NAMED_EXAMPLE_OR_MODEL': 10} errors=[] |
| all 130 wishlist atoms link to source claims, boundaries, and bridge obligations | `PASS` | atoms=130 errors=[] |
| P040/P058 claim-level delta is complete and non-independent | `PASS` | delta_rows=223 bad_refs=0 conflict_status=NON_INDEPENDENT_UNRESOLVED_VERSION_FAMILY |
| all unresolved conflicts are typed and source-grounded | `PASS` | conflicts=6 errors=[] |
| claim/dependency graph is closed and excludes unaudited lexical law edges | `PASS` | nodes=3040 edges=35276 bad_endpoints=0 lexical_law_edges=0 |
| generated summaries match canonical artifacts | `PASS` | claim_summary=2821 bridge_summary=374 carriers=24 graph=3040/35276 |
| Step-2 requirement audit closes every planned delivery obligation | `PASS` | rows=16 ids=16 errors=[] |
| obsolete competing-ID/prototype outputs are absent | `PASS` | no stale prototype outputs |
| Step 3 has not started | `PASS` | no Step-3 artifacts |
