from __future__ import annotations

from fractions import Fraction

from sixbirds_foundations_v.sweeps.e11_institutional_rewrite_sweep import (
    SUPPORT_EPSILON,
    ClaimStatus,
    InstitutionalRewriteStatus,
    build_fixture,
    classify_institutional_rewrite_status,
    closure_differs,
    constitutive_evidence_exists_for,
    delta_stack_empty_for,
    kernel_support_differs,
    matched_controls_comparison,
    parameter_conditioning_only,
    reproduces_claimed_effect,
    run_institutional_rewrite_sweep,
    structural_effect_for,
    support_under,
    top_down_channel_accepted_bool,
    top_down_channel_claim_status,
)


F = Fraction


def test_e11_sweep_confirms_all_registered_predictions() -> None:
    results = run_institutional_rewrite_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 20


def test_e11_fixture_uses_registered_intervention_pairs_consistently() -> None:
    fixture = build_fixture()

    macro = fixture.comparisons["comp_macro_label"]
    assert macro.theta_i == "theta_macro_left"
    assert macro.theta_j == "theta_macro_right"
    assert fixture.interventions[macro.theta_i].label == "macro_left"
    assert fixture.interventions[macro.theta_j].label == "macro_right"
    assert fixture.interventions[macro.theta_i].support == fixture.interventions[macro.theta_j].support
    assert fixture.interventions[macro.theta_i].closure_signature == "closure_base"
    assert fixture.interventions[macro.theta_j].closure_signature == "closure_base"


def test_e11_top_down_channel_logic_mirrors_fiii_fixture() -> None:
    fixture = build_fixture()
    accepted = fixture.channels["td_accepted_stack"]
    structural_only = fixture.channels["td_structural_only"]

    assert accepted.host == "Host.fin"
    assert accepted.profile == "baseProfile"
    assert top_down_channel_accepted_bool(accepted) is True
    assert top_down_channel_claim_status(accepted) is ClaimStatus.accepted

    assert structural_only.structural_path_present is True
    assert structural_only.intervention_gate is False
    assert structural_only.effect_gate is False
    assert top_down_channel_accepted_bool(structural_only) is False
    assert top_down_channel_claim_status(structural_only) is ClaimStatus.blocked


def test_e11_support_closure_and_parameter_comparators_are_computed() -> None:
    fixture = build_fixture()

    stack = fixture.comparisons["comp_stack_license"]
    assert support_under(fixture.interventions[stack.theta_i], "b", "d") is False
    assert support_under(fixture.interventions[stack.theta_j], "b", "d") is True
    assert kernel_support_differs(fixture, stack.theta_i, stack.theta_j) is True
    assert closure_differs(fixture, stack.theta_i, stack.theta_j) is True
    assert parameter_conditioning_only(fixture, stack.theta_i, stack.theta_j) is False

    conditioning = fixture.comparisons["comp_conditioning_fee"]
    assert kernel_support_differs(fixture, conditioning.theta_i, conditioning.theta_j) is False
    assert closure_differs(fixture, conditioning.theta_i, conditioning.theta_j) is False
    assert parameter_conditioning_only(fixture, conditioning.theta_i, conditioning.theta_j) is True

    closure_only = fixture.comparisons["comp_stack_closure"]
    assert kernel_support_differs(fixture, closure_only.theta_i, closure_only.theta_j) is False
    assert closure_differs(fixture, closure_only.theta_i, closure_only.theta_j) is True


def test_e11_near_zero_tolerance_is_not_promoted_to_support_rewrite() -> None:
    fixture = build_fixture()
    near = fixture.comparisons["comp_near_zero"]
    low = fixture.interventions[near.theta_i]
    high = fixture.interventions[near.theta_j]

    assert SUPPORT_EPSILON == F(1, 100)
    assert low.transition_weights[("b", "d")] == F(0, 1)
    assert high.transition_weights[("b", "d")] == F(1, 1000)
    assert support_under(low, "b", "d") is False
    assert support_under(high, "b", "d") is False
    assert kernel_support_differs(fixture, near.theta_i, near.theta_j) is False
    assert parameter_conditioning_only(fixture, near.theta_i, near.theta_j) is True

    status, truths, _record = classify_institutional_rewrite_status(fixture, near)
    assert status is InstitutionalRewriteStatus.conditioning
    assert truths == {
        "inert": False,
        "conditioning": True,
        "stack_active": False,
        "constitutive": False,
    }


def test_e11_structural_effect_for_enforces_same_comparison_and_channel() -> None:
    fixture = build_fixture()
    stack = fixture.comparisons["comp_stack_license"]
    effect = fixture.structural_effects["effect_stack_exit"]
    unlinked = fixture.structural_effects["effect_unlinked"]

    assert structural_effect_for(fixture, stack, "td_accepted_stack", effect) is True
    assert effect.comparison_record == stack.comparison_record
    assert effect.channel_record == "td_accepted_stack"

    assert unlinked.comparison_record != stack.comparison_record
    assert unlinked.channel_record == "td_accepted_stack"
    assert structural_effect_for(fixture, stack, "td_accepted_stack", unlinked) is False


def test_e11_delta_stack_opposite_results_are_computed_from_outcomes() -> None:
    fixture = build_fixture()
    stack = fixture.comparisons["comp_stack_license"]
    stack_effect = fixture.structural_effects["effect_stack_exit"]
    claimed = fixture.comparisons["comp_delta_claimed"]
    claimed_effect = fixture.structural_effects["effect_delta_claimed"]
    placebo = fixture.comparisons["comp_delta_placebo"]
    placebo_effect = fixture.parameter_effects["param_effect_delta_placebo"]

    assert stack.theta_i == claimed.theta_i
    assert stack.theta_j == claimed.theta_j
    assert stack_effect.observed_outcome != claimed_effect.observed_outcome
    assert parameter_conditioning_only(fixture, placebo.theta_i, placebo.theta_j) is True
    assert reproduces_claimed_effect(placebo_effect, claimed_effect) is True

    assert delta_stack_empty_for(fixture, stack, stack_effect) is True
    assert delta_stack_empty_for(fixture, claimed, claimed_effect) is False


def test_e11_constitutive_evidence_exists_only_for_compiled_rule() -> None:
    fixture = build_fixture()

    assert (
        constitutive_evidence_exists_for(fixture, fixture.comparisons["comp_stack_license"])
        is False
    )
    assert (
        constitutive_evidence_exists_for(fixture, fixture.comparisons["comp_stack_closure"])
        is False
    )
    assert (
        constitutive_evidence_exists_for(fixture, fixture.comparisons["comp_constitutive_rule"])
        is True
    )


def test_e11_status_partition_rows_are_computed_as_exactly_one_branch() -> None:
    results = run_institutional_rewrite_sweep()
    expected = {
        "stack_support_rewrite": InstitutionalRewriteStatus.stack_active.value,
        "stack_closure_rewrite": InstitutionalRewriteStatus.stack_active.value,
        "constitutive_compiled": InstitutionalRewriteStatus.constitutive.value,
        "conditioning_fee": InstitutionalRewriteStatus.conditioning.value,
        "washout_static": InstitutionalRewriteStatus.inert.value,
    }

    assert {row.name: row.status for row in results.status_rows} == expected
    for row in results.status_rows:
        assert sum((row.inert, row.conditioning, row.stack_active, row.constitutive)) == 1


def test_e11_null_controls_and_boundary_checks_match_registration() -> None:
    results = run_institutional_rewrite_sweep()

    assert results.matched_controls_failure == {
        "has_uncontrolled_witness": True,
        "matched_controls": False,
        "structural_effect_for_any": False,
        "status_theorem_applies": False,
    }
    assert results.unlinked_control["accepted_channel"] is True
    assert results.unlinked_control["support_inequality"] is True
    assert results.unlinked_control["effect_comparison_matches"] is False
    assert results.unlinked_control["structural_effect_for"] is False

    washout = results.boundary_controls["comp_washout_static"]
    conditioning = results.boundary_controls["comp_conditioning_fee"]
    assert washout["parameter_conditioning_only"] is False
    assert washout["status"] == "inert"
    assert conditioning["parameter_conditioning_only"] is True
    assert conditioning["status"] == "conditioning"


def test_e11_macro_inert_and_constitutive_overclaim_controls() -> None:
    results = run_institutional_rewrite_sweep()

    assert results.macro_inert_control["accepted"] is False
    assert results.macro_inert_control["support_equal"] is True
    assert results.macro_inert_control["closure_differs"] is False
    assert results.macro_inert_control["parameter_values_equal"] is True
    assert results.macro_inert_control["parameter_conditioning_only"] is False
    assert results.macro_inert_control["structural_effect_for_any"] is False
    assert results.macro_inert_control["status"] == "inert"

    assert results.constitutive_overclaim_control["structural_effect_for"] is True
    assert results.constitutive_overclaim_control["e4_holds"] is False
    assert results.constitutive_overclaim_control["constitutive_exists"] is False
    assert results.constitutive_overclaim_control["constitutive_holds"] is False
    assert results.constitutive_overclaim_control["stack_active_holds"] is True
    assert results.constitutive_overclaim_control["status_is_stack_active"] is True


def test_e11_blocked_channel_with_genuine_support_difference_is_not_stack_active() -> None:
    results = run_institutional_rewrite_sweep()
    fixture = build_fixture()
    control = results.blocked_channel_control
    comparison = fixture.comparisons["comp_stack_blocked_channel"]
    effect = fixture.structural_effects["effect_blocked_channel"]

    assert comparison.theta_i == "theta_open"
    assert comparison.theta_j == "theta_license"
    assert comparison.channel_record == "td_structural_only"
    assert kernel_support_differs(fixture, comparison.theta_i, comparison.theta_j) is True
    assert support_under(fixture.interventions[comparison.theta_i], "b", "d") is False
    assert support_under(fixture.interventions[comparison.theta_j], "b", "d") is True
    assert top_down_channel_accepted_bool(fixture.channels[comparison.channel_record]) is False
    assert top_down_channel_claim_status(fixture.channels[comparison.channel_record]) is ClaimStatus.blocked
    assert effect.comparison_record == comparison.comparison_record
    assert effect.channel_record == comparison.channel_record
    assert structural_effect_for(fixture, comparison, comparison.channel_record, effect) is False
    assert control["support_difference"] is True
    assert control["support_witness_genuine"] is True
    assert control["top_down_accepted"] is False
    assert control["structural_effect_for"] is False
    assert control["stack_active_holds"] is False
    assert control["status"] == "inert"


def test_e11_lucas_descent_residuals_are_derived_from_support_sets() -> None:
    results = run_institutional_rewrite_sweep()
    fixture = build_fixture()

    rows = {row.regime: row for row in results.lucas_rows}
    for row in results.lucas_rows:
        comparison = fixture.comparisons[row.comparison]
        predicted = int(support_under(fixture.interventions[comparison.theta_i], "b", "d"))
        actual = int(support_under(fixture.interventions[comparison.theta_j], "b", "d"))
        assert row.predicted_support_bd == predicted
        assert row.actual_support_bd == actual
        assert row.residual == abs(actual - predicted)

    assert rows["washout/static"].residual == 0
    assert rows["conditioning-only"].residual == 0
    assert rows["stack-active license"].residual == 1
    assert rows["stack-active license"].descent_failure is True


def test_e11_scope_and_anti_hardcoding_guards_are_computed() -> None:
    results = run_institutional_rewrite_sweep()
    fixture = build_fixture()

    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True
    for row in results.status_rows:
        assert row.carried_status_record in fixture.carried_status_records
        assert row.status != InstitutionalRewriteStatus.unclassified.value

    assert matched_controls_comparison(fixture, fixture.comparisons["comp_unmatched"]) is False
