# E16 Adaptability Sweep Results

Overall verdict: PASS
Registered comparisons: 69

## Registered Prediction Comparisons

| comparison | verdict | observed | expected |
| --- | --- | --- | --- |
| claim_coherent_wheel.status | PASS | `coherent_adaptability` | `coherent_adaptability` |
| claim_support_confound.status | PASS | `support_confound` | `support_confound` |
| claim_artifact_trap.status | PASS | `artifact` | `artifact` |
| claim_flat_future.status | PASS | `flat` | `flat` |
| claim_flat_equal_capacity.status | PASS | `flat` | `flat` |
| claim_flattenable.status | PASS | `flattenable` | `flattenable` |
| claim_currentizable.status | PASS | `currentizable_slack` | `currentizable_slack` |
| claim_dissipative.status | PASS | `dissipative` | `dissipative` |
| claim_rejected_perturbation.status | PASS | `adaptability_rejected` | `adaptability_rejected` |
| claim_rejected_unbound_flat.status | PASS | `adaptability_rejected` | `adaptability_rejected` |
| claim_coherent_wheel.current_audit | PASS | `CurrentEventEquiv=true; current_class(FT)=current_class(FF)` | `CurrentEventEquiv=true; current_class(FT)=current_class(FF)` |
| claim_coherent_wheel.route_capacity | PASS | `C_repair: gamma=3/4; eta=1/4; unequal=true` | `C_repair: gamma=3/4; eta=1/4; unequal=true` |
| claim_coherent_wheel.loop_anchor | PASS | `CurrentLoopTrivial=true; PredictiveLoopNontrivial=true; current_image_fixed=true` | `CurrentLoopTrivial=true; PredictiveLoopNontrivial=true; current_image_fixed=true` |
| six_regime_census | PASS | `flat=1; artifact=1; flattenable=1; explicit_latent=1; dissipative=1; coherent_candidate=1` | `flat=1; artifact=1; flattenable=1; explicit_latent=1; dissipative=1; coherent_candidate=1` |
| ctrl_support_only | PASS | `supportFreedom=false; other_freedoms=true; support_confound` | `supportFreedom=false; other_freedoms=true; support_confound` |
| ctrl_flattening_only | PASS | `flatteningFreedom=false; other_freedoms=true; flattenable` | `flatteningFreedom=false; other_freedoms=true; flattenable` |
| ctrl_currentization_only | PASS | `currentizationFreedom=false; completionClears=false; currentizable_slack` | `currentizationFreedom=false; completionClears=false; currentizable_slack` |
| ctrl_dissipation_only | PASS | `dissipationFreedom=false; perturbations_preserve=true; dissipative` | `dissipationFreedom=false; perturbations_preserve=true; dissipative` |
| ctrl_perturbation_only | PASS | `bounded_failure=true; continuation_dissipation=false; adaptability_rejected` | `bounded_failure=true; continuation_dissipation=false; adaptability_rejected` |
| ctrl_e15_still_outstanding | PASS | `residue_eligible=false; candidate=false` | `residue_eligible=false; candidate=false` |
| ctrl_e15_reconciled | PASS | `residue_eligible=true; proceeds_to_controls=true` | `residue_eligible=true; proceeds_to_controls=true` |
| ctrl_e15_disconnected_same_id | PASS | `numeric_id_equal=true; full_record_equal=false; bridge_eligible=false` | `numeric_id_equal=true; full_record_equal=false; bridge_eligible=false` |
| ctrl_undeclared_proxy | PASS | `declared_base_equal=true; SupportConfoundEvidenceFor=false; mechanical_status=coherent_adaptability` | `declared_base_equal=true; SupportConfoundEvidenceFor=false; mechanical_status=coherent_adaptability` |
| ctrl_wrong_route_endpoint | PASS | `endpoint_linkage=false; capacity_difference=false` | `endpoint_linkage=false; capacity_difference=false` |
| ctrl_different_protocols | PASS | `sameProtocol=false; distribution_pair=false` | `sameProtocol=false; distribution_pair=false` |
| ctrl_route_inadmissible | PASS | `routePairAdmissible=false; candidate=false; administrative_rejection=true` | `routePairAdmissible=false; candidate=false; administrative_rejection=true` |
| ctrl_package_undeclared | PASS | `routePackageDeclared=false; candidate=false; administrative_rejection=true` | `routePackageDeclared=false; candidate=false; administrative_rejection=true` |
| ctrl_budget_linkage | PASS | `binding=true; protocolUsesBindingBudget=false; flat=false; rejected=true` | `binding=true; protocolUsesBindingBudget=false; flat=false; rejected=true` |
| ctrl_undeclared_challenge_difference | PASS | `C_hidden_not_declared=true; capacity_difference=false` | `C_hidden_not_declared=true; capacity_difference=false` |
| ctrl_missing_declared_class | PASS | `everyClassCovered=false; complete_distribution=false` | `everyClassCovered=false; complete_distribution=false` |
| ctrl_duplicate_probability_record | PASS | `recordsNodup=false; complete_distribution=false` | `recordsNodup=false; complete_distribution=false` |
| ctrl_duplicate_probability_id | PASS | `recordIdsNodup=false; complete_distribution=false` | `recordIdsNodup=false; complete_distribution=false` |
| ctrl_contradictory_same_class | PASS | `singleValuedPerClass=false; complete_distribution=false` | `singleValuedPerClass=false; complete_distribution=false` |
| ctrl_uncarried_ledger_support | PASS | `everyLedgerEntryCarried=false; capacity_difference=false` | `everyLedgerEntryCarried=false; capacity_difference=false` |
| ctrl_uncarried_distribution | PASS | `distributionCarried=false; complete_distribution=false` | `distributionCarried=false; complete_distribution=false` |
| ctrl_probability_ledger_computation | PASS | `stored=3/4; computed=1/2; everyProbabilityComputed=false` | `stored=3/4; computed=1/2; everyProbabilityComputed=false` |
| ctrl_ledger_relevance | PASS | `supportingLedgerEntryRelevant=false; capacity_difference=false` | `supportingLedgerEntryRelevant=false; capacity_difference=false` |
| ctrl_exact_denominator | PASS | `successful=3; eligible=4; stored=2/3; everyProbabilityComputed=false; exact_ratio=false` | `successful=3; eligible=4; stored=2/3; everyProbabilityComputed=false; exact_ratio=false` |
| ctrl_trial_inventory_omission | PASS | `eligible_trial_missing=true; everyEligibleTrialCovered=false` | `eligible_trial_missing=true; everyEligibleTrialCovered=false` |
| ctrl_protocol_inventory_omission | PASS | `eligible_counterpart_missing=true; supportFreedom=false` | `eligible_counterpart_missing=true; supportFreedom=false` |
| ctrl_completion_inventory_omission | PASS | `eligible_completion_missing=true; flatteningFreedom=false` | `eligible_completion_missing=true; flatteningFreedom=false` |
| ctrl_refinement_inventory_omission | PASS | `eligible_refinement_missing=true; currentizationFreedom=false` | `eligible_refinement_missing=true; currentizationFreedom=false` |
| ctrl_continuation_inventory_omission | PASS | `eligible_continuation_missing=true; dissipationFreedom=false` | `eligible_continuation_missing=true; dissipationFreedom=false` |
| ctrl_perturbation_inventory_omission | PASS | `eligible_trial_missing=true; dissipationFreedom=false` | `eligible_trial_missing=true; dissipationFreedom=false` |
| ctrl_duplicate_counterpart_key | PASS | `recordIdsNodup=false; singleValuedPerDeclaredKey=false` | `recordIdsNodup=false; singleValuedPerDeclaredKey=false` |
| ctrl_unregistered_dissipating_continuation | PASS | `off_inventory=true; DissipativeEvidenceFor=false` | `off_inventory=true; DissipativeEvidenceFor=false` |
| ctrl_completion_label_without_collapse | PASS | `witnessCount=1; discrepancy=1/2; clears=false` | `witnessCount=1; discrepancy=1/2; clears=false` |
| ctrl_changed_support_refinement | PASS | `refinement_base_equal=false; changed_base_refinement_cannot_currentize=true; CurrentizableEvidenceFor=false; SupportConfoundEvidenceFor=false` | `refinement_base_equal=false; changed_base_refinement_cannot_currentize=true; CurrentizableEvidenceFor=false; SupportConfoundEvidenceFor=false` |
| ctrl_out_of_bound_perturbation | PASS | `magnitude=3/4; bound=1/2; eligible=false; coherence_unchanged=true` | `magnitude=3/4; bound=1/2; eligible=false; coherence_unchanged=true` |
| ctrl_wrong_claim_route | PASS | `valid_other_claim=true; evidence_for_current=false` | `valid_other_claim=true; evidence_for_current=false` |
| ctrl_wrong_claim_challenge | PASS | `valid_other_claim=true; evidence_for_current=false` | `valid_other_claim=true; evidence_for_current=false` |
| ctrl_wrong_claim_protocol | PASS | `valid_other_claim=true; evidence_for_current=false` | `valid_other_claim=true; evidence_for_current=false` |
| ctrl_wrong_claim_time | PASS | `other_time=11; current_time=10; evidence_for_current=false` | `other_time=11; current_time=10; evidence_for_current=false` |
| ctrl_priority_artifact_flattening_collision | PASS | `artifactEvidence=true; flattenableEvidence=true; status=artifact` | `artifactEvidence=true; flattenableEvidence=true; status=artifact` |
| ctrl_lower_tag_with_raw_artifact | PASS | `record_tag=flattenable; ArtifactEvidenceFor=true; FlattenableCase=false` | `record_tag=flattenable; ArtifactEvidenceFor=true; FlattenableCase=false` |
| ctrl_status_uniqueness | PASS | `same_claim=true; tags=(artifact,flattenable); complete_status=false` | `same_claim=true; tags=(artifact,flattenable); complete_status=false` |
| mut_counterpart_admissibility | PASS | `protocol/completion/refinement/continuation: each admissible true->false and inventory_sound true->false` | `protocol/completion/refinement/continuation: each admissible true->false and inventory_sound true->false` |
| mut_honest_protocol_clears | PASS | `false->true; ArtifactEvidenceFor=false->true` | `false->true; ArtifactEvidenceFor=false->true` |
| mut_completion_clears | PASS | `false->true; FlattenableEvidenceFor=false->true` | `false->true; FlattenableEvidenceFor=false->true` |
| mut_refinement_currentizes | PASS | `false->true; CurrentizableEvidenceFor=false->true` | `false->true; CurrentizableEvidenceFor=false->true` |
| mut_continuation_dissipates | PASS | `false->true; DissipativeEvidenceFor=false->true` | `false->true; DissipativeEvidenceFor=false->true` |
| mut_perturbation_survival | PASS | `true->false at 1/4; coherent=false; rejected=true` | `true->false at 1/4; coherent=false; rejected=true` |
| mut_e15_bridge_acceptance | PASS | `true->false; residue_eligible=true->false` | `true->false; residue_eligible=true->false` |
| mut_e15_outstanding_status | PASS | `false->true at time 10; residue_eligible=true->false` | `false->true at time 10; residue_eligible=true->false` |
| mut_carriedness_fields | PASS | `sourceTag/generatedByS/inScope flips each make E16Carried=false` | `sourceTag/generatedByS/inScope flips each make E16Carried=false` |
| mut_predictive_reveal | PASS | `no_reveal_core Continuation={id,ell0}; FuturePredictiveEquiv=true; witness=false; candidate=false` | `no_reveal_core Continuation={id,ell0}; FuturePredictiveEquiv=true; witness=false; candidate=false` |
| ctrl_flat_unrelated_pair_rejected | PASS | `claim_pair_unequal=true; claim_pair_no_difference=false; unrelated_pair_complete=true; unrelated_pair_equal=true; unrelated_pair_matches_claim=false; FlatEvidenceFor=false` | `claim_pair_unequal=true; claim_pair_no_difference=false; unrelated_pair_complete=true; unrelated_pair_equal=true; unrelated_pair_matches_claim=false; FlatEvidenceFor=false` |
| ctrl_perturbation_off_universe_rejected | PASS | `old_conditions_met=true; perturbationTrialEligible=false; coverage_unaffected=true; record_inclusion_fails_soundness=true` | `old_conditions_met=true; perturbationTrialEligible=false; coverage_unaffected=true; record_inclusion_fails_soundness=true` |
| ctrl_swapped_trial_populations_rejected | PASS | `everyTrialEligible=false; complete_distribution=false` | `everyTrialEligible=false; complete_distribution=false` |

## Discipline Checks

- Actual scope discipline: `True`
- No hardcoded status discipline: `True`
- Off-inventory dissipation isolation: `True`
- Predictive-reveal isolation: `True`
- Administrative rejection without candidate evidence: `True`
- Wrong-claim E15 bridge isolation: `True`
- Same-ID changed-content route trial rejected: `True`
- Same-ID changed-magnitude perturbation trial rejected: `True`
- Flat cross-witness differential: `True`
