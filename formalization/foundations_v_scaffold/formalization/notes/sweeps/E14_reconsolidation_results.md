# E14 Reconsolidation Sweep Results

Overall verdict: PASS
Registered comparisons: 21

## Registered Prediction Comparisons

| comparison | verdict | observed | expected |
| --- | --- | --- | --- |
| claim_record_repaired.status | PASS | `record_repaired` | `record_repaired` |
| claim_record_coarsened.status | PASS | `record_coarsened` | `record_coarsened` |
| claim_statused_unresolved.status | PASS | `statused_unresolved` | `statused_unresolved` |
| claim_outcome_collision.status | PASS | `outcome_collision` | `outcome_collision` |
| claim_unrealized_direct_reference.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| claim_silent_rewrite.status | PASS | `silent_rewrite` | `silent_rewrite` |
| claim_provenance_defect.status | PASS | `provenance_defect` | `provenance_defect` |
| claim_ordinary_read.status | PASS | `ordinary_read` | `ordinary_read` |
| claim_unstatused_conflict.status | PASS | `unstatused_conflict` | `unstatused_conflict` |
| ctrl_transport_single_valued_same_context | PASS | `complete=true; sound=true; covered=true; single_valued=false; inventory=false` | `complete=true; sound=true; covered=true; single_valued=false; inventory rejected` |
| ctrl_coarsening_audited_pair_mismatch.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| ctrl_unresolved_provenance_root_mismatch.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| ctrl_no_conflict_after_transport | PASS | `context_dependent=True; DeltaSet=[]; trigger_count=0` | `context_dependent=true; DeltaSet={}; trigger/status absent` |
| ctrl_conflict_for_other_claim | PASS | `borrowed_link=False; DeltaSet=[]; trigger_count=0` | `borrowed conflict link=false; own DeltaSet={}; trigger/status absent` |
| ctrl_non_strict_coarsening.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| ctrl_wrong_direction_refinement.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| ctrl_uncarried_post_retrieval_record.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| ctrl_ledger_charge_label_only.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| ctrl_per_retrieval_claim_scoping | PASS | `home=record_repaired; shift=statused_unresolved; home_truths=1; shift_truths=1` | `home=record_repaired; shift=statused_unresolved; both exactly one` |
| ctrl_unrelated_mutation_evidence.status | PASS | `unrealized_disposition` | `unrealized_disposition` |
| strata_budget_memory_fate_direction | PASS | `repair=6/1; coarsened=1/6; unresolved=1/1` | `repair loose/tight=6/1; coarsened loose/tight=1/6; unresolved=1/1` |

## Discipline Checks

- Actual scope discipline: `True`
- No hardcoded status discipline: `True`
