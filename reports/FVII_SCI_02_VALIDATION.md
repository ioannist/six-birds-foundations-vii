# FVII-SCI-02 validation

**Status:** `PASS`  
**Checks:** 31/31  
**Lean kernel status:** `NOT_RUN_LOCAL_ENVIRONMENT`

| Check | Status | Detail |
|---|---:|---|
| `phase1_base_tag` | PASS | 4b6469169067adac48af304cb8918922d51b9f6f |
| `science_plan_phase2_state` | PASS | PHASE_02_EXECUTED_PHASES_03_TO_05_PENDING |
| `phase2_public_declaration_registry` | PASS | rows=237 |
| `phase2_theorem_registry` | PASS | rows=130 |
| `theorem_registry_subset` | PASS | all theorem names are public declarations |
| `stable_phase2_asset_ids` | PASS | rows=237 |
| `source_statement_hashes` | PASS | all declarations hashed |
| `nine_terminal_candidates` | PASS | ids=['VII-C001', 'VII-C002', 'VII-C003', 'VII-C004', 'VII-C005', 'VII-C006', 'VII-C021', 'VII-C022', 'VII-C029'] |
| `candidate_terminal_grades` | PASS | all terminal with theorem surface |
| `candidate_dossiers` | PASS | nine dossiers |
| `five_no_go_fronts` | PASS | ids=['NGVII-01', 'NGVII-03', 'NGVII-04', 'NGVII-05', 'NGVII-11'] |
| `no_go_escapes_and_controls` | PASS | all no-gos have theorem, escape, positive control |
| `no_go_dossiers` | PASS | five dossiers |
| `formalization_target_set` | PASS | ids=['FT01', 'FT02', 'FT03', 'FT04', 'FT05', 'FT16', 'FT17', 'FT18'] |
| `ft18_admission_half_only` | PASS | ADMISSION_HALF_COMPLETE_JOIN_HALF_RESERVED_FOR_FVII_SCI_03 |
| `nine_finite_envelopes` | PASS | ids=['P2-E01', 'P2-E02', 'P2-E03', 'P2-E04', 'P2-E05', 'P2-E06', 'P2-E07', 'P2-E08', 'P2-E09'] |
| `bounded_envelope_cardinalities` | PASS | raw=1332 canonical=1076 accepted=470 rejected=606 |
| `fifteen_canonical_witnesses` | PASS | ids=15 |
| `primary_fixture_python_replay` | PASS | 10 scenarios and 9 countermodels pass |
| `phase2_summary_closure` | PASS | COMPLETE_SOURCE_LEVEL_EXTERNAL_LEAN_REPLAY_PENDING |
| `asset_trace_closure` | PASS | rows=404 |
| `statement_hash_ledger` | PASS | rows=130 |
| `python_protocol_and_model_tests` | PASS | tests=34 returncode=0 |
| `static_lean_source_audit` | PASS | STATIC_SOURCE_AUDIT_NOT_KERNEL_ELABORATION |
| `python_source_compilation` | PASS | seven source files |
| `shell_syntax` | PASS | files=2 |
| `deterministic_phase2_regeneration` | PASS | sha256=923c3b8fc083adfbd5fadbb3a1ff2cdb9d6a2ac453691c5b9abbba15e18e46fb |
| `phase1_and_inherited_immutability` | PASS | changed=[] |
| `no_paper_work` | PASS | changed=[] |
| `phases_3_4_5_not_executed` | PASS | no later science directories |
| `lean_boundary_truthfully_recorded` | PASS | NOT_RUN_LOCAL_ENVIRONMENT |
