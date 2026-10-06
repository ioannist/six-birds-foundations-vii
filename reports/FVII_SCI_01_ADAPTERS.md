# FVII-SCI-01 inherited adapter audit

All twenty formalization targets have narrow adapter modules. Every adapter imports and `#check`s its exact inherited declaration and records source/target types, preserved hypotheses, added hypotheses, lost hypotheses, trust dependencies, and nonclaims. The metadata is not a transport theorem.

| Target | Name | Adapter rows | Module | Phase-1 status | Later science |
|---|---|---|---|---|---|
| FT01 | Finite access-status data model | 2 | FoundationsVII.Prior.FT01 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT02 | Admission reachability graph and occurrence separation | 2 | FoundationsVII.Prior.FT02 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT03 | Bootstrap obstruction | 1 | FoundationsVII.Prior.FT03 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT04 | Prospective commitment timestamp/budget record | 1 | FoundationsVII.Prior.FT04 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT05 | Source and bridge ledger | 2 | FoundationsVII.Prior.FT05 | PROTOCOL_ASSET_COMPLETE_SOURCE_LEVEL | False |
| FT06 | Typed contact witness | 1 | FoundationsVII.Prior.FT06 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT07 | Join certificate normal form | 2 | FoundationsVII.Prior.FT07 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT08 | Anti-product/nonfactorization witness | 1 | FoundationsVII.Prior.FT08 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT09 | Join obstruction and budget record | 2 | FoundationsVII.Prior.FT09 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT10 | Coverage-qualified non-interaction certificate | 1 | FoundationsVII.Prior.FT10 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT11 | Enablement record | 1 | FoundationsVII.Prior.FT11 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT12 | Endogenous generator criterion | 1 | FoundationsVII.Prior.FT12 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT13 | Transmission/descent fidelity | 1 | FoundationsVII.Prior.FT13 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT14 | Confluence and critical-pair finite models | 2 | FoundationsVII.Prior.FT14 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT15 | Interaction holonomy/arrow separation | 2 | FoundationsVII.Prior.FT15 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT16 | Budget and observer occupancy | 2 | FoundationsVII.Prior.FT16 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT17 | Negative quantifier and claim-grade rules | 2 | FoundationsVII.Prior.FT17 | PROTOCOL_ASSET_COMPLETE_SOURCE_LEVEL | False |
| FT18 | No-free-access/no-free-join lemmas | 1 | FoundationsVII.Prior.FT18 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT19 | Parent retention and refinement transport | 1 | FoundationsVII.Prior.FT19 | TYPED_SUPPORT_AND_EXACT_ADAPTER_COMPLETE | True |
| FT20 | Residual/needle and finite-world semantics | 2 | FoundationsVII.Prior.FT20 | PROTOCOL_ASSET_COMPLETE_SOURCE_LEVEL | False |

## Exact reuse records

| Adapter | Target | Source declaration | Source | VII metadata declaration | Status |
|---|---|---|---|---|---|
| FVII-ADP-01-01 | FT01 | SixBirds.ClaimRecord | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-ii/lean/full/SixBirds/Admissibility.lean:5 | FoundationsVII.Prior.adapter_ft01_claimrecord_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-01-02 | FT01 | SixBirdsFoundationsV.AccessPolicy | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E6E9PricedAccess.lean:239 | FoundationsVII.Prior.adapter_ft01_accesspolicy_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-02-01 | FT02 | SixBirdsFoundationsV.RepairGeneratorReachabilityRecord | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E5ReclosureCollapse.lean:100 | FoundationsVII.Prior.adapter_ft02_repairgeneratorreachabilityrecord_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-02-02 | FT02 | SixBirdsFoundationsV.RepairGeneratorReachabilityCertified | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E5ReclosureCollapse.lean:966 | FoundationsVII.Prior.adapter_ft02_repairgeneratorreachabilitycertified_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-03-01 | FT03 | SixBirdsFoundationsV.NoReachableRepairGenerator | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E1Internalization.lean:365 | FoundationsVII.Prior.adapter_ft03_noreachablerepairgenerator_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-04-01 | FT04 | SixBirdsFoundationsV.SharedBudgetAllocationRecord | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E15OfflineReclosure.lean:93 | FoundationsVII.Prior.adapter_ft04_sharedbudgetallocationrecord_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-05-01 | FT05 | SixBirdsFoundationsV.CarriedSource | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Definitional/CarriedRecord.lean:26 | FoundationsVII.Prior.adapter_ft05_carriedsource_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-05-02 | FT05 | SixBirdsFoundationsV.TransportTokenRecord | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E13RepairTransport.lean:59 | FoundationsVII.Prior.adapter_ft05_transporttokenrecord_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-06-01 | FT06 | SixBirdsIII.InstrumentClaimRecord | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/InstrumentClaims.lean:5 | FoundationsVII.Prior.adapter_ft06_instrumentclaimrecord_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-07-01 | FT07 | SixBirdsFoundationsV.repairJoin | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Definitional/RepairJoin.lean:19 | FoundationsVII.Prior.adapter_ft07_repairjoin_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-07-02 | FT07 | SixBirdsFoundationsV.join_well_defined | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Definitional/RepairJoin.lean:42 | FoundationsVII.Prior.adapter_ft07_join_well_defined_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-08-01 | FT08 | SixBirdsFoundationsV.StrictSelfExtension | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E1Internalization.lean:198 | FoundationsVII.Prior.adapter_ft08_strictselfextension_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-09-01 | FT09 | SixBirdsFoundationsV.BudgetFeasible | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E6E9PricedAccess.lean:67 | FoundationsVII.Prior.adapter_ft09_budgetfeasible_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-09-02 | FT09 | SixBirdsFoundationsV.ObstructionStatusRecord | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E4RepairCompilation.lean:282 | FoundationsVII.Prior.adapter_ft09_obstructionstatusrecord_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-10-01 | FT10 | SixBirdsFoundationsV.E11_NCTDObstruction | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E11InstitutionalRewrite.lean:966 | FoundationsVII.Prior.adapter_ft10_e11_nctdobstruction_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-11-01 | FT11 | SixBirdsFoundationsV.RepairGeneratorReachabilityRecord | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E5ReclosureCollapse.lean:100 | FoundationsVII.Prior.adapter_ft11_repairgeneratorreachabilityrecord_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-12-01 | FT12 | SixBirdsFoundationsV.NoReachableRepairGeneratorExcludesEndogenousFamily | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E1Internalization.lean:643 | FoundationsVII.Prior.adapter_ft12_noreachablerepairgeneratorexcludesendogenousfamily_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-13-01 | FT13 | SixBirdsIII.descent_square_recovery | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-iii/lean/full/SixBirdsIII/HighStructure.lean:17 | FoundationsVII.Prior.adapter_ft13_descent_square_recovery_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-14-01 | FT14 | SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_confluent_runs_share_final | formalization/foundations_vi_scaffold/lean/SixBirdsFoundationsVI/Laws/G8OdometerAbelianization.lean:737 | FoundationsVII.Prior.adapter_ft14_caseb_confluent_runs_share_final_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-14-02 | FT14 | SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseD_nonconfluent_witness | formalization/foundations_vi_scaffold/lean/SixBirdsFoundationsVI/Laws/G8OdometerAbelianization.lean:884 | FoundationsVII.Prior.adapter_ft14_cased_nonconfluent_witness_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-15-01 | FT15 | HolonomyMemory.LoopAsymmetry | formalization/foundations_v_scaffold/lean/vendor/foundations/holonomy-memory/HolonomyMemory/Asymmetry.lean:13 | FoundationsVII.Prior.adapter_ft15_loopasymmetry_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-15-02 | FT15 | HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent | formalization/foundations_v_scaffold/lean/vendor/foundations/holonomy-memory/HolonomyMemory/Asymmetry.lean:28 | FoundationsVII.Prior.adapter_ft15_loopasymmetry_exhibits_movedpredictive_fixedcurrent_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-16-01 | FT16 | SixBirdsFoundationsV.BindingExposureBudget | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E6E9PricedAccess.lean:81 | FoundationsVII.Prior.adapter_ft16_bindingexposurebudget_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-16-02 | FT16 | SixBirdsFoundationsV.PositiveAccessMoveCosts | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E6E9PricedAccess.lean:228 | FoundationsVII.Prior.adapter_ft16_positiveaccessmovecosts_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-17-01 | FT17 | SixBirds.AdmissibleClaim | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-ii/lean/full/SixBirds/Admissibility.lean:26 | FoundationsVII.Prior.adapter_ft17_admissibleclaim_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-17-02 | FT17 | SixBirds.NonclaimRecord | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-foundations-ii/lean/full/SixBirds/Admissibility.lean:41 | FoundationsVII.Prior.adapter_ft17_nonclaimrecord_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-18-01 | FT18 | SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction.financed_refinement_retains_access | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-meta-math/lean/SixBirdsMetaMath/FoundationsIV/Access/NoFreeDistinction.lean:134 | FoundationsVII.Prior.adapter_ft18_financed_refinement_retains_access_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-19-01 | FT19 | SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence.persistence_extension_retains_old | formalization/foundations_vi_scaffold/lean/vendor/foundations/six-birds-meta-math/lean/SixBirdsMetaMath/FoundationsIV/StatusRecordsCoherence/ObjectPersistence.lean:258 | FoundationsVII.Prior.adapter_ft19_persistence_extension_retains_old_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-20-01 | FT20 | SixBirdsFoundationsV.ResidualStatusRecord | formalization/foundations_v_scaffold/lean/SixBirdsFoundationsV/Laws/E5ReclosureCollapse.lean:84 | FoundationsVII.Prior.adapter_ft20_residualstatusrecord_01 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
| FVII-ADP-20-02 | FT20 | SixBirdsMetaMath.Xi.Obstruction.blindSpotWitness | formalization/foundations_v_scaffold/lean/vendor/foundations/xi/Xi/Obstruction.lean:27 | FoundationsVII.Prior.adapter_ft20_blindspotwitness_02 | PHASE1_ADAPTER_REGISTERED_NOT_SEMANTIC_EQUIVALENCE |
