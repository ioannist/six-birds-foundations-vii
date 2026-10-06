# FVII-SCI-01 validation

**Status:** `PASS`
**Mode:** `USER_AUTHORIZED_EXTERNAL_LEAN_REPLAY`
**Acceptance checks:** 38/38 pass
**Informational boundaries:** 1

| Check | Status | Detail |
|---|---|---|
| `object_registry` | PASS | rows=18 |
| `fifteen_vii_owned_types` | PASS | O04-O18 |
| `audit_anchor_and_local_representation` | PASS | inherited audit role anchored separately from the VII append-only representation |
| `formalization_target_registry` | PASS | rows=20 |
| `adapter_ledger` | PASS | rows=30 |
| `adapter_target_coverage` | PASS | FT01-FT20 |
| `candidate_registry` | PASS | rows=36 |
| `terminal_candidate_partition` | PASS | C020/C023/C024/C025 |
| `later_candidate_nonexecution` | PASS | support_rows=32 |
| `terminal_declaration_trace` | PASS | no missing terminal source declarations |
| `terminal_protocol_strength` | PASS | missing=[] |
| `decision_registry` | PASS | rows=15 |
| `decision_non_silent_resolution` | PASS | all decisions retain a terminal phase |
| `public_declaration_registry` | PASS | rows=447 |
| `stable_science_asset_ids` | PASS | unique=447 rows=447 |
| `vii_owned_trust_surface` | PASS | no new VII axiom/opaque |
| `inherited_trust_explicit` | PASS | one inherited axiom plus five opaque constants |
| `fixture_census` | PASS | scenarios=24 countermodels=27 |
| `fixture_ids` | PASS | complete frozen IDs |
| `lossless_step3_migration` | PASS | flags, expectations, assertions, traces |
| `typed_fixture_sections` | PASS | 15 VII-owned records plus append-only audit |
| `canonical_fixture_bytes` | PASS | sorted compact UTF-8 plus trailing newline |
| `closed_fixture_schemas` | PASS | root, flags, structural records, and countermodels reject undeclared fields |
| `fixture_manifest_hashes` | PASS | rows=51 |
| `countermodel_scenario_hashes` | PASS | 27/27 |
| `python_unit_tests` | PASS | 25 tests |
| `python_reference_world` | PASS | 24/24 scenarios; 27/27 countermodels |
| `twenty_four_reached_statuses` | PASS | distinct=24 |
| `deterministic_generators` | PASS | fingerprint=718e1dc48ea050b0 |
| `lean_static_validation` | PASS | imports, lexical structure, declarations, scope |
| `python_syntax` | PASS | files=55 errors=[] |
| `shell_syntax` | PASS | scripts/rebuild_fvii_sci01.sh, scripts/run_fvii_sci01_external_lean.sh |
| `imported_scaffolds_immutable` | PASS | Foundations V/VI byte surfaces unchanged from plan tag |
| `no_paper_writing` | PASS | no tracked or untracked TeX changed or added |
| `no_later_phase_modules` | PASS | Phase 2-4 science not executed |
| `external_replay_instructions` | PASS | directions and executable script |
| `transient_artifacts_absent` | PASS | found=[] |
| `lean_environment_override` | PASS | PENDING_EXTERNAL_LEAN_BUILD_AND_DIFFERENTIAL_REPLAY |

## Informational boundary

- Lean kernel build, #print axioms replay, and 51-case Lean/Python differential remain pending external execution; this is nonblocking under the owner's explicit authorization.
