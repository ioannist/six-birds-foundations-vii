# FVII-SCI-03 validation

- **Status:** `PASS`
- **Checks:** 36/36
- **Lean kernel status:** `NOT_RUN_LOCAL_ENVIRONMENT`

| Check | Status | Detail |
|---|---:|---|
| `phase2_base_tag` | PASS | 14fcd7f291f573fd7f8a3f6dcb9957ecf270b00b |
| `science_plan_phase3_state` | PASS | PHASE_03_EXECUTED_PHASES_04_TO_05_PENDING |
| `phase3_public_declaration_registry` | PASS | rows=363 |
| `phase3_theorem_registry` | PASS | rows=183 |
| `theorem_registry_subset` | PASS | all theorem names are public declarations |
| `stable_phase3_asset_ids` | PASS | rows=363 |
| `source_statement_hashes` | PASS | every declaration has statement and source-block hashes |
| `no_source_level_trust_shortcuts` | PASS | kinds=[] |
| `thirteen_terminal_candidates` | PASS | ids=['VII-C007', 'VII-C008', 'VII-C009', 'VII-C010', 'VII-C011', 'VII-C016', 'VII-C019', 'VII-C026', 'VII-C030', 'VII-C031', 'VII-C033', 'VII-C035', 'VII-C036'] |
| `candidate_terminal_grades_and_boundaries` | PASS | all terminal with theorem surface and nonclaim |
| `candidate_finite_or_structural_controls` | PASS | every candidate has a formal or bounded control |
| `candidate_source_trace_counts` | PASS | every candidate retains Step-3 source support or boundary provenance |
| `candidate_dossiers` | PASS | thirteen terminal dossiers |
| `five_no_go_fronts` | PASS | ids=['NGVII-02', 'NGVII-06', 'NGVII-07', 'NGVII-08', 'NGVII-09'] |
| `no_go_dossiers` | PASS | five scoped dossiers |
| `formalization_target_closure` | PASS | ids=['FT05', 'FT06', 'FT07', 'FT08', 'FT09', 'FT10', 'FT16', 'FT18', 'FT19', 'FT20'] |
| `eight_terminal_scope_decisions` | PASS | ids=['DP01', 'DP02', 'DP03', 'DP04', 'DP05', 'DP06', 'DP10', 'DP15'] |
| `decision_dossier` | PASS | terminal rulings collected |
| `eleven_finite_envelopes` | PASS | raw=141112 canonical=73528 accepted=34532 rejected=38996 |
| `finite_envelope_nonclaims` | PASS | bounded evidence grades and nonclaims retained |
| `twenty_seven_canonical_witnesses` | PASS | ids=27 |
| `primary_fixture_python_replay` | PASS | 12 scenarios and 14 countermodels pass |
| `phase3_summary_closure` | PASS | COMPLETE_SOURCE_LEVEL_EXTERNAL_LEAN_REPLAY_PENDING |
| `seven_status_partition_counts` | PASS | {'NO_EVIDENCED_CONTACT': 4, 'EVIDENCED_CONTACT': 4, 'COMMON_REFINEMENT': 8, 'LAWFUL_COMPOSITE': 64, 'STRICT_JOIN': 2, 'OBSTRUCTED': 80, 'CERTIFIED_NONINTERACTION': 8} |
| `asset_trace_closure` | PASS | rows=525 |
| `statement_hash_ledger` | PASS | rows=183 |
| `five_finite_no_go_controls` | PASS | rows=5 |
| `python_protocol_and_model_tests` | PASS | tests=48 returncode=0 |
| `static_lean_source_audit` | PASS | STATIC_SOURCE_AUDIT_NOT_KERNEL_ELABORATION |
| `python_source_compilation` | PASS | files=7 |
| `shell_syntax` | PASS | files=2 |
| `deterministic_phase3_regeneration` | PASS | sha256=bdeb828ab9a04e559b351c7048ee96c5965fedce7df8cd8648a320c68aa9f190 |
| `phase2_and_inherited_immutability` | PASS | changed=[] |
| `no_paper_work` | PASS | changed=[] |
| `phases_4_and_5_not_executed` | PASS | no later science directories |
| `lean_boundary_truthfully_recorded` | PASS | NOT_RUN_LOCAL_ENVIRONMENT |
