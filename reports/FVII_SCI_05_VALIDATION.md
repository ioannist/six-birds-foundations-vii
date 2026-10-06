# FVII-SCI-05 validation

**Status:** `PASS`

**Checks:** 32/32

**Kernel:** `PASS`

| Check | Result | Detail |
| --- | --- | --- |
| final_release_surface_present | PASS | files=22 |
| science_plan_manifest_final | PASS | FINAL_SCIENCE_RELEASE_LOCAL_LEAN_REPLAY_PASS |
| static_lean_source_audit | PASS | 23/23 |
| all_candidates_terminal | PASS | count=36 dispositions={'FORMAL_SCHEMA': 15, 'CONDITIONAL_THEOREM': 15, 'LEAN_DECIDABLE_FINITE': 1, 'CLOSED_DEFERRAL': 2, 'REFUTED_CANDIDATE': 2, 'CONSTRUCTIVE_COUNTERMODEL': 1} |
| all_eighteen_objects_closed | PASS | objects=18 |
| all_twenty_targets_closed_or_superseded | PASS | targets=20 |
| public_declaration_census | PASS | declarations=1477 |
| public_theorem_census | PASS | theorems=732 |
| twenty_one_cross_family_corollaries | PASS | corollaries=21 |
| eleven_terminal_no_gos | PASS | no_gos=11 |
| fifteen_decisions_terminal_or_nonblocking | PASS | decisions=15 |
| thirty_inherited_adapter_contracts | PASS | adapters=30 |
| forty_three_cumulative_finite_assays | PASS | phase_counts={'PHASE2': 9, 'PHASE3': 11, 'PHASE4': 12, 'PHASE5': 11} |
| phase5_global_finite_census | PASS | {"accepted_cases": 21081, "bounded_witness_count": 33, "canonical_cases": 84864, "cross_family_control_count": 12, "raw_cases": 86912, "rejected_cases": 63783} |
| complete_reference_fixture_replay | PASS | 24/24 scenarios and 27/27 named countermodels |
| countermodel_registry_complete | PASS | kinds={'NAMED_REFERENCE_COUNTERMODEL': 27, 'MINIMIZED_BOUNDED_REJECTION_WITNESS': 11} hash_errors=[] |
| all_python_tests | PASS | returncode=0 tests=70 |
| statement_hash_ledger_exact | PASS | hashes=732 |
| theorem_dependency_registry_closed | PASS | theorems=732 edges=943 |
| theorem_trust_registry_closed | PASS | rows=732 trust_reachable=0 |
| public_api_registry | PASS | modules=111 |
| graphml_dependency_surfaces_parse | PASS | counts=[(1477, 943), (165, 344)] errors=[] |
| final_release_manifest_exact | PASS | status=FVII_SCIENCE_FINAL_LOCAL_LEAN_REPLAY_PASS |
| release_entry_points_resolve | PASS | entry_paths=5 |
| final_summary_exact | PASS | {"adapter_count": 30, "candidate_count": 36, "candidate_dispositions": {"CLOSED_DEFERRAL": 2, "CONDITIONAL_THEOREM": 15, "CONSTRUCTIVE_COUNTERMODEL": 1, "FORMAL_SCHEMA": 15, "LEAN_DECIDABLE_FINITE": 1, "REFUTED_CANDIDATE": 2}, "corollary_count": 21, "countermodel_registry_count": 38, "decision_count": 15, "finite_assay_count": 43, "formalization_target_count": 20, "generated": "2026-07-26", "inherited_trust_declaration_count": 6, "kernel_status": "PASS_LOCAL_REPLAY", "minimized_final_countermodel_count": 11, "module_import_edge_count": 344, "named_countermodel_count": 27, "no_go_count": 11, "no_paper_work": true, "nonclaim": "Local Lean replay and #print axioms audit passed.", "object_count": 18, "public_declaration_count": 1477, "public_definition_count": 745, "public_module_count": 111, "public_theorem_count": 732, "stage": "FVII_SCIENCE_FINAL_LOCAL_LEAN_REPLAY_PASS", "static_axiom_free_core_candidate_count": 625, "static_trust_reachable_theorem_count": 0, "theorem_dependency_edge_count": 943} |
| inherited_formal_scaffolds_immutable | PASS | changed=[] |
| no_paper_or_paper_prep_changes | PASS | paper=[] tex_outside_paper_dir=[] |
| paper_prep_is_assets_not_manuscript | PASS | bad_format=[] over_6000w=[] |
| final_public_root_complete | PASS | FoundationsVII.lean -> All -> Release |
| strict_external_lean_replay | PASS | kernel=PASS |
| shell_scripts_parse | PASS | rebuild=0 external=0 |
| python_sources_compile | PASS |  |
