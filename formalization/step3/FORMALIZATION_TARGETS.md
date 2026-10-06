# Foundations VII formalization targets

Step 3 specifies proof targets and exact inherited declaration reuse only. It adds no Lean declaration and claims no fresh Lean 4.28.0 kernel replay.

| ID | Target | Mode | Priority | Candidates | Prior declarations |
| --- | --- | --- | --- | --- | --- |
| FT01 | Finite access-status data model | Lean candidate | P0 | VII-C001, VII-C002, VII-C022 | SixBirds.ClaimRecord, SixBirdsFoundationsV.AccessPolicy |
| FT02 | Admission reachability graph and occurrence separation | Lean candidate | P0 | VII-C001, VII-C002, VII-C021 | SixBirdsFoundationsV.RepairGeneratorReachabilityRecord, SixBirdsFoundationsV.RepairGeneratorReachabilityCertified |
| FT03 | Bootstrap obstruction | direct proof + Lean candidate | P0 | VII-C003, VII-C035 | SixBirdsFoundationsV.NoReachableRepairGenerator |
| FT04 | Prospective commitment timestamp/budget record | schema then Lean candidate | P1 | VII-C004, VII-C006 | SixBirdsFoundationsV.SharedBudgetAllocationRecord |
| FT05 | Source and bridge ledger | Lean candidate | P0 | VII-C004, VII-C005, VII-C010, VII-C016, VII-C020 | SixBirdsFoundationsV.CarriedSource, SixBirdsFoundationsV.TransportTokenRecord |
| FT06 | Typed contact witness | finite data model | P0 | VII-C007, VII-C016 | SixBirdsIII.InstrumentClaimRecord |
| FT07 | Join certificate normal form | Lean candidate | P0 | VII-C007, VII-C009, VII-C026, VII-C030 | SixBirdsFoundationsV.repairJoin, SixBirdsFoundationsV.join_well_defined |
| FT08 | Anti-product/nonfactorization witness | direct proof + finite check | P0 | VII-C009, VII-C035, VII-C036 | SixBirdsFoundationsV.StrictSelfExtension |
| FT09 | Join obstruction and budget record | Lean candidate | P0 | VII-C008, VII-C011, VII-C019, VII-C031 | SixBirdsFoundationsV.BudgetFeasible, SixBirdsFoundationsV.ObstructionStatusRecord |
| FT10 | Coverage-qualified non-interaction certificate | finite exhaustive check | P1 | VII-C008, VII-C033 | SixBirdsFoundationsV.E11_NCTDObstruction |
| FT11 | Enablement record | Lean candidate | P0 | VII-C012, VII-C014, VII-C027, VII-C034 | SixBirdsFoundationsV.RepairGeneratorReachabilityRecord |
| FT12 | Endogenous generator criterion | direct proof + Lean candidate | P0 | VII-C013 | SixBirdsFoundationsV.NoReachableRepairGeneratorExcludesEndogenousFamily |
| FT13 | Transmission/descent fidelity | schema only until maps fixed | P1 | VII-C015, VII-C034 | SixBirdsIII.descent_square_recovery |
| FT14 | Confluence and critical-pair finite models | finite exhaustive check | P1 | VII-C017, VII-C018, VII-C028 | SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_confluent_runs_share_final, SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseD_nonconfluent_witness |
| FT15 | Interaction holonomy/arrow separation | Lean candidate + finite check | P0 | VII-C017, VII-C027, VII-C032 | HolonomyMemory.LoopAsymmetry, HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent |
| FT16 | Budget and observer occupancy | finite data model | P0 | VII-C006, VII-C011, VII-C013, VII-C029 | SixBirdsFoundationsV.BindingExposureBudget, SixBirdsFoundationsV.PositiveAccessMoveCosts |
| FT17 | Negative quantifier and claim-grade rules | direct proof | P0 | VII-C002, VII-C005, VII-C020, VII-C021, VII-C022, VII-C023, VII-C024, VII-C033 | SixBirds.AdmissibleClaim, SixBirds.NonclaimRecord |
| FT18 | No-free-access/no-free-join lemmas | direct proof + Lean candidate | P0 | VII-C003, VII-C035 | SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction.financed_refinement_retains_access |
| FT19 | Parent retention and refinement transport | Lean candidate | P1 | VII-C015, VII-C030 | SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence.persistence_extension_retains_old |
| FT20 | Residual/needle and finite-world semantics | finite exhaustive check | P1 | VII-C019, VII-C025, VII-C031, VII-C036 | SixBirdsFoundationsV.ResidualStatusRecord, SixBirdsMetaMath.Xi.Obstruction.blindSpotWitness |
