# E13 Repair Transport Sweep Results

Overall verdict: PASS
Registered comparisons: 19

## Registered Prediction Comparisons

| comparison | verdict | observed | expected |
| --- | --- | --- | --- |
| claim_comm_clean.status | PASS | `communicated` | `communicated` |
| claim_teach_absent_capacity.status | PASS | `taught` | `taught` |
| claim_force_null.status | PASS | `coercion_null` | `coercion_null` |
| claim_symbol_stable.status | PASS | `symbolic` | `symbolic` |
| claim_scaffolded_no_capacity.status | PASS | `scaffolded_or_primed` | `scaffolded_or_primed` |
| claim_primed_no_capacity.status | PASS | `scaffolded_or_primed` | `scaffolded_or_primed` |
| claim_influence_different_class.status | PASS | `influence_only` | `influence_only` |
| reject_unpaid_bridge.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_uncarried_target_repair.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_role_preservation_failure.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_symbol_context_instability.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_symbol_role_drift.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_saturation_relabel.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_parameter_channel_only.status | PASS | `transport_rejected` | `transport_rejected` |
| reject_flow_crossing_no_bridge.status | PASS | `transport_rejected` | `transport_rejected` |
| ctrl_shared_comparator_bundle_nontrivial | PASS | `force=True; role_accept=True; role_reject=True; bridge_accept=True; bridge_reject=True` | `shared ctx_main computes both accepting and rejecting comparator results` |
| ctrl_transport_claim_kind_scoping | PASS | `comm=True; teaching=False; symbol=False` | `communication record matches only communication claim, not teaching/symbol claims` |
| ctrl_claim_independence | PASS | `claim_comm_clean=communicated; claim_symbol_stable=symbolic` | `distinct claims keep independent statuses` |
| ctrl_falsifier_claim_linkage | PASS | `claimLinked=False` | `mismatched-token/bridge falsifier linkage is false` |

## Discipline Checks

- Actual scope discipline: `True`
- No hardcoded status discipline: `True`
