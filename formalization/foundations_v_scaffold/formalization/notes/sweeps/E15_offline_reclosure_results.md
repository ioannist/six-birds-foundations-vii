# E15 Offline Reclosure Sweep Results

Overall verdict: PASS
Registered comparisons: 46

## Registered Prediction Comparisons

| comparison | verdict | observed | expected |
| --- | --- | --- | --- |
| claim_alternation_required.status | PASS | `alternation_required; observed_duty=1/4; predicted_duty=1/4` | `alternation_required; observed_duty=1/4; predicted_duty=1/4` |
| claim_online_sufficient.status | PASS | `online_sufficient; alternation=False` | `online_sufficient; alternation=False` |
| claim_offline_optional.status | PASS | `offline_optional` | `offline_optional` |
| claim_deficit_online_counterexample.status | PASS | `deficit_online_counterexample; lower_holds=False` | `deficit_online_counterexample; lower_holds=False` |
| claim_decorative_exchange_active.status | PASS | `decorative_offline; exchange=1` | `decorative_offline; exchange=1` |
| claim_decorative_no_discharge.status | PASS | `decorative_offline; discharged=0` | `decorative_offline; discharged=0` |
| claim_decorative_bad_reallocation.status | PASS | `decorative_offline; exact_allocation=False` | `decorative_offline; exact_allocation=False` |
| claim_duty_cycle_mismatch.status | PASS | `duty_cycle_mismatch; observed_duty=1/3; predicted_duty=1/4; error=1/12>1/24` | `duty_cycle_mismatch; observed_duty=1/3; predicted_duty=1/4; error=1/12>1/24` |
| claim_skipped_offline_cascade.status | PASS | `skipped_offline_cascade` | `skipped_offline_cascade` |
| claim_zero_exchange_without_p2.status | PASS | `offline_reclosure_rejected; census=0; gate=False` | `offline_reclosure_rejected; census=0; gate=False` |
| ctrl_three_source_exact_aggregation | PASS | `total=20; source omissions=[False, False, False]` | `total=20; source omissions=[false,false,false]` |
| ctrl_e14_direct_witness_required | PASS | `lookalike credited=0; E14 item=False` | `lookalike credited=0; E14 item=false` |
| ctrl_f3_certificate_required | PASS | `F3 item=False` | `F3 item=false` |
| ctrl_xi_posthoc_scalarization_rejected | PASS | `Xi item=False; declaration=False; amount link=False` | `Xi item=false; declaration=false; amount link=false` |
| ctrl_xi_amount_without_matrix_rejected | PASS | `Xi record/item=False` | `Xi record/item=false` |
| ctrl_duplicate_physical_ledger_charge | PASS | `ledgerChargesNodup=False` | `ledgerChargesNodup=false` |
| ctrl_free_capacity_smuggling_rejected | PASS | `geometry=False; positive branch=False` | `geometry=false; positive branch=false` |
| ctrl_capacity_gain_equation | PASS | `6=4+2; fitted 11/2=False; fitted 13/2=False` | `6=4+2; fitted 11/2=false; fitted 13/2=false` |
| ctrl_gross_accrual_not_net_change | PASS | `accrual=5; discharge=3; net=2` | `accrual=5; discharge=3; net=2` |
| sweep_deficit_boundary | PASS | `7/2=online_sufficient; 4=online_sufficient; 5=alternation_required` | `7/2=online_sufficient; 4=online_sufficient; 5=alternation_required` |
| ctrl_incomplete_phase_flow_inventory | PASS | `everyPhaseCovered=False; status=offline_reclosure_rejected` | `everyPhaseCovered=false; status=offline_reclosure_rejected` |
| ctrl_recurrence_uses_online_duration | PASS | `online duration checks=[False, True]; alternation=False; status=offline_reclosure_rejected` | `online duration checks=[false,true]; alternation=false; status=offline_reclosure_rejected` |
| ctrl_posthoc_tolerance_rejected | PASS | `prediction=False; mismatch=False` | `prediction=false; mismatch=false` |
| ctrl_claim_scoping | PASS | `shared scope=True; online=online_sufficient; mismatch=duty_cycle_mismatch; cross matches=[False, False]` | `shared scope=true; online=online_sufficient; mismatch=duty_cycle_mismatch; cross matches=[false,false]` |
| ctrl_evidence_priority_not_status_tag | PASS | `counterexample raw=True; alternation case=False; statusUnique with both=False; canonical=deficit_online_counterexample` | `counterexample raw=true; alternation case=false; statusUnique with both=false; canonical=deficit_online_counterexample` |
| ctrl_alarm_without_e7_acceptance | PASS | `cascade evidence=False` | `cascade evidence=false` |
| ctrl_stress_without_e5_acceptance | PASS | `cascade evidence=False` | `cascade evidence=false` |
| ctrl_cascade_chronology_lineage_mutations | PASS | `five cascade mutations=[False, False, False, False, False]` | `five cascade mutations=[false,false,false,false,false]` |
| ctrl_e5_suspension_is_not_e15_offline | PASS | `E5 suspension=True; E15 genuine offline=False` | `E5 suspension=true; E15 genuine offline=false` |
| ctrl_offline_overcapacity_is_decorative.status | PASS | `decorative_offline; offline_optional=False` | `decorative_offline; offline_optional=False` |
| ctrl_exchange_census_omission | PASS | `completeForSchedule=False` | `completeForSchedule=false` |
| ctrl_exchange_census_record_duplicate | PASS | `recordsNodup=False` | `recordsNodup=false` |
| ctrl_exchange_census_id_duplicate | PASS | `recordIdsNodup=False` | `recordIdsNodup=false` |
| ctrl_exchange_eligibility_soundness_matrix | PASS | `eligibility=[False, False, False, False]; soundness=False; phase coverage=False` | `eligibility=[false,false,false,false]; soundness=false; phase coverage=false` |
| ctrl_shared_context_mutation_matrix | PASS | `nine predicates=True; Xi equality=True; mutations=[False, False, False, False, False, False, False, False, False, False]` | `nine predicates=true; Xi equality=true; ten mutations=false` |
| ctrl_carriedness_conjunction_mutations | PASS | `vectors=[(False, False, False), (False, False, False), (False, False, False), (False, False, False), (False, False, False), (False, False, False), (False, False, False)]` | `seven representative vectors=[false,false,false]` |
| ctrl_allocation_postdates_horizon | PASS | `geometry=False` | `geometry=false` |
| ctrl_p2_gate_component_mutations | PASS | `six P2 mutations=[False, False, False, False, False, False]; exchange=0` | `six P2 mutations=false; exchange=0` |
| ctrl_claim_match_key_mutations | PASS | `five claim matches=[False, False, False, False, False]` | `five claim matches=false` |
| ctrl_debt_and_flow_duplicate_safety | PASS | `duplicate-safety vector=[False, False, False, False]` | `duplicate-safety vector=[false,false,false,false]` |
| ctrl_online_discharge_capacity_bound | PASS | `persistent/bounded/sufficient=[False, False, False]; rates=[Fraction(5, 1), Fraction(5, 1), Fraction(5, 1)]; other fields=[True, True, True]` | `persistent/bounded/sufficient=[false,false,false]; rates=[5,5,5]; other fields=[true,true,true]` |
| census_offline_ablation_alarm_stress | PASS | `alarm/stress/chronology=4/4/4; collapse comparison absent` | `alarm/stress/chronology=4/4/4; collapse comparison absent` |
| ctrl_eight_way_partition_and_top_exclusion | PASS | `ten claims exactly one=True; counterexample lower holds=False` | `ten claims exactly one; counterexample lower holds=false` |
| ctrl_e14_wrong_canonical_status_rejected | PASS | `E14 debt item false; credited E14 amount 0` | `E14 debt item false; credited E14 amount 0` |
| ctrl_offline_flow_off_inventory_rejected | PASS | `genuine offline false; decorative offline false` | `genuine offline false; decorative offline false` |
| ctrl_discharge_out_of_phase_rejected | PASS | `everyDischargeLinked = false; CompleteClosureDebtFlow = false` | `everyDischargeLinked = false; CompleteClosureDebtFlow = false` |

## Discipline Checks

- Actual scope discipline: `True`
- No hardcoded status discipline: `True`
