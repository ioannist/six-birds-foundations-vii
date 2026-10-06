# E10 Cognitive Demarcation Sweep Results

Overall verdict: PASS
Registered comparisons: 26

## Registered Prediction Comparisons

| comparison | verdict | observed | expected |
| --- | --- | --- | --- |
| claim_pkg_nav_cognitive.status | PASS | `cognitive` | `cognitive` |
| claim_pkg_passive_non_cognitive.status | PASS | `non_cognitive` | `non_cognitive` |
| claim_pkg_schedule_trap.status | PASS | `schedule_trap` | `schedule_trap` |
| claim_pkg_external_scaffold.status | PASS | `scaffolding` | `scaffolding` |
| claim_pkg_structural_path.status | PASS | `structural_path_only` | `structural_path_only` |
| claim_pkg_decodable.status | PASS | `decodable_correlate` | `decodable_correlate` |
| claim_pkg_repair_no_gate.status | PASS | `repair_without_gate` | `repair_without_gate` |
| claim_pkg_gate_no_repair.status | PASS | `gate_without_repair` | `gate_without_repair` |
| claim_intention_clean.status | PASS | `intention` | `intention` |
| claim_intention_neutral.status | PASS | `not_intention` | `not_intention` |
| claim_intention_posthoc.status | PASS | `post_hoc_intention` | `post_hoc_intention` |
| claim_intention_approximate.status | PASS | `approximate_support_defect` | `approximate_support_defect` |
| claim_intention_target_incoherent.status | PASS | `target_incoherent_restriction` | `target_incoherent_restriction` |
| claim_goal_clean.status | PASS | `goal` | `goal` |
| claim_goal_neutral.status | PASS | `not_goal` | `not_goal` |
| claim_goal_reward_proxy_only.status | PASS | `reward_proxy_only` | `reward_proxy_only` |
| claim_goal_route_unstable.status | PASS | `route_unstable` | `route_unstable` |
| ctrl_support_for_intervention_linkage | PASS | `good=True; wrong=False; bad_gate=False` | `good support link true; wrong support link false; bad gate false` |
| ctrl_main_claim_scoping | PASS | `exact=True; wrong_same_package=False; desc_other_valid=True; desc_other_wrong=False; wrong_status=non_cognitive` | `exact package/class scoping holds; wrong-class real C_other repair queried under C_nav yields non_cognitive` |
| ctrl_decodable_priority_blocks_cognitive.status | PASS | `decodable_correlate` | `decodable_correlate` |
| ctrl_schedule_priority_blocks_cognitive.status | PASS | `schedule_trap` | `schedule_trap` |
| ctrl_post_hoc_priority_blocks_intention.status | PASS | `post_hoc_intention` | `post_hoc_intention` |
| ctrl_reward_proxy_priority_blocks_goal.status | PASS | `reward_proxy_only` | `reward_proxy_only` |
| ctrl_every_route_evaluated_universal.status | PASS | `not_goal` | `not_goal` |
| ctrl_uncarried_intention_rejected.status | PASS | `not_intention` | `not_intention` |
| ctrl_uncarried_goal_rejected.status | PASS | `not_goal` | `not_goal` |

## Discipline Checks

- Actual scope discipline: `True`
- No hardcoded status discipline: `True`
