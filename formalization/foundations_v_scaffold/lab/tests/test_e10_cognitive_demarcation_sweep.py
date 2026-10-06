from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import pytest

from sixbirds_foundations_v.carried_records import FineSourceTag
from sixbirds_foundations_v.sweeps.e10_cognitive_demarcation_sweep import (
    CognitiveClaimRef,
    CognitiveStatus,
    GoalStatus,
    IntentionStatus,
    _actual_scope_discipline,
    _no_hardcoded_status_discipline,
    _status_rows,
    build_fixture,
    classify_cognitive_status,
    classify_goal_status,
    classify_intention_status,
    cognitive_case,
    cognitive_status_record_matches_claim,
    decodable_correlate_case,
    every_route_evaluated,
    gate_without_repair_case,
    goal_case,
    goal_evidence,
    goal_status_record_matches_claim,
    intention_case,
    intention_evidence,
    intention_status_record_matches_claim,
    package_repair_descent,
    repair_without_gate_case,
    route_substitution_persistence_certified,
    run_e10_cognitive_demarcation_sweep,
    schedule_trap_case,
    structural_path_only_case,
    top_down_kernel_gate_certified,
)


def test_e10_sweep_confirms_all_registered_predictions() -> None:
    results = run_e10_cognitive_demarcation_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 26
    assert len(results.rows) == 24
    assert len(results.controls) == 2
    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True


@pytest.mark.parametrize(
    ("claim", "expected"),
    (
        ("claim_pkg_nav_cognitive", CognitiveStatus.cognitive),
        ("claim_pkg_passive_non_cognitive", CognitiveStatus.non_cognitive),
        ("claim_pkg_schedule_trap", CognitiveStatus.schedule_trap),
        ("claim_pkg_external_scaffold", CognitiveStatus.scaffolding),
        ("claim_pkg_structural_path", CognitiveStatus.structural_path_only),
        ("claim_pkg_decodable", CognitiveStatus.decodable_correlate),
        ("claim_pkg_repair_no_gate", CognitiveStatus.repair_without_gate),
        ("claim_pkg_gate_no_repair", CognitiveStatus.gate_without_repair),
        ("ctrl_decodable_priority_blocks_cognitive", CognitiveStatus.decodable_correlate),
        ("ctrl_schedule_priority_blocks_cognitive", CognitiveStatus.schedule_trap),
    ),
)
def test_e10_registered_cognitive_status_rows(claim: str, expected: CognitiveStatus) -> None:
    fixture = build_fixture()
    status, truths, record = classify_cognitive_status(fixture, claim)

    assert status is expected
    assert record is not None
    assert sum(truths.values()) == 1


@pytest.mark.parametrize(
    ("claim", "expected"),
    (
        ("claim_intention_clean", IntentionStatus.intention),
        ("claim_intention_neutral", IntentionStatus.not_intention),
        ("claim_intention_posthoc", IntentionStatus.post_hoc_intention),
        ("claim_intention_approximate", IntentionStatus.approximate_support_defect),
        ("claim_intention_target_incoherent", IntentionStatus.target_incoherent_restriction),
        ("ctrl_post_hoc_priority_blocks_intention", IntentionStatus.post_hoc_intention),
        ("ctrl_uncarried_intention_rejected", IntentionStatus.not_intention),
    ),
)
def test_e10_registered_intention_status_rows(claim: str, expected: IntentionStatus) -> None:
    fixture = build_fixture()
    status, truths, record = classify_intention_status(fixture, claim)

    assert status is expected
    assert record is not None
    assert sum(truths.values()) == 1


@pytest.mark.parametrize(
    ("claim", "expected"),
    (
        ("claim_goal_clean", GoalStatus.goal),
        ("claim_goal_neutral", GoalStatus.not_goal),
        ("claim_goal_reward_proxy_only", GoalStatus.reward_proxy_only),
        ("claim_goal_route_unstable", GoalStatus.route_unstable),
        ("ctrl_reward_proxy_priority_blocks_goal", GoalStatus.reward_proxy_only),
        ("ctrl_every_route_evaluated_universal", GoalStatus.not_goal),
        ("ctrl_uncarried_goal_rejected", GoalStatus.not_goal),
    ),
)
def test_e10_registered_goal_status_rows(claim: str, expected: GoalStatus) -> None:
    fixture = build_fixture()
    status, truths, record = classify_goal_status(fixture, claim)

    assert status is expected
    assert record is not None
    assert sum(truths.values()) == 1


@pytest.mark.parametrize(
    "control_name",
    (
        "ctrl_support_for_intervention_linkage",
        "ctrl_main_claim_scoping",
    ),
)
def test_e10_registered_controls(control_name: str) -> None:
    results = run_e10_cognitive_demarcation_sweep()

    assert results.controls[control_name].passed_control is True


def test_e10_wrong_class_descent_constraint_is_enforced() -> None:
    fixture = build_fixture()

    assert package_repair_descent(fixture, "desc_other_real", "pkg_other_repair", "C_other") is True
    assert package_repair_descent(fixture, "desc_other_real", "pkg_other_repair", "C_nav") is False

    mutated_package = replace(fixture.packages["pkg_other_repair"], declared_class="C_nav")
    mutated = replace(
        fixture,
        packages={**fixture.packages, "pkg_other_repair": mutated_package},
    )

    assert package_repair_descent(mutated, "desc_other_real", "pkg_other_repair", "C_other") is False
    assert classify_cognitive_status(fixture, "ctrl_wrong_class_claim")[0] is CognitiveStatus.non_cognitive


def test_e10_support_for_intervention_linkage_is_load_bearing() -> None:
    fixture = build_fixture()
    bad_gate = replace(fixture.gates["gate_nav_cognitive"], support1="supp_wrong_for_intervention")
    mutated = replace(
        fixture,
        gates={**fixture.gates, "gate_nav_cognitive": bad_gate},
    )

    assert top_down_kernel_gate_certified(fixture, "gate_nav_cognitive", "pkg_nav_cognitive", "C_nav") is True
    assert fixture.ctx.support_for_intervention(fixture, "supp_wrong_for_intervention", "int_nav_value0") is False
    assert top_down_kernel_gate_certified(mutated, "gate_nav_cognitive", "pkg_nav_cognitive", "C_nav") is False
    assert cognitive_case(
        mutated,
        mutated.cognitive_claims["claim_pkg_nav_cognitive"],
        mutated.cognitive_status_records["status_pkg_nav_cognitive"],
    ) is False


def test_e10_kernel_support_difference_reads_support_set_content() -> None:
    fixture = build_fixture()
    equal_content_support = replace(
        fixture.supports["supp_nav_val1"],
        support_set=fixture.supports["supp_nav_val0"].support_set,
    )
    mutated = replace(
        fixture,
        supports={**fixture.supports, "supp_nav_val1": equal_content_support},
    )

    assert fixture.ctx.kernel_support_differs(fixture, "supp_nav_val0", "supp_nav_val1") is True
    assert mutated.supports["supp_nav_val0"].support_id != mutated.supports["supp_nav_val1"].support_id
    assert mutated.ctx.kernel_support_differs(mutated, "supp_nav_val0", "supp_nav_val1") is False
    assert top_down_kernel_gate_certified(mutated, "gate_nav_cognitive", "pkg_nav_cognitive", "C_nav") is False
    assert cognitive_case(
        mutated,
        mutated.cognitive_claims["claim_pkg_nav_cognitive"],
        mutated.cognitive_status_records["status_pkg_nav_cognitive"],
    ) is False


def test_e10_structural_path_supports_must_match_claim_challenge_class() -> None:
    fixture = build_fixture()
    wrong_class_before = replace(fixture.supports["supp_struct_before"], challenge_class="C_other")
    wrong_class_after = replace(fixture.supports["supp_struct_after"], challenge_class="C_other")
    mutated = replace(
        fixture,
        supports={
            **fixture.supports,
            "supp_struct_before": wrong_class_before,
            "supp_struct_after": wrong_class_after,
        },
    )
    claim = mutated.cognitive_claims["claim_pkg_structural_path"]
    record = mutated.cognitive_status_records["status_pkg_structural_path"]

    assert mutated.ctx.kernel_support_differs(mutated, "supp_struct_before", "supp_struct_after") is True
    assert structural_path_only_case(mutated, claim, record) is False


def test_e10_schedule_trap_supports_must_match_claim_challenge_class() -> None:
    fixture = build_fixture()
    wrong_class_before = replace(fixture.supports["supp_sched_before"], challenge_class="C_other")
    wrong_class_after = replace(fixture.supports["supp_sched_after"], challenge_class="C_other")
    mutated = replace(
        fixture,
        supports={
            **fixture.supports,
            "supp_sched_before": wrong_class_before,
            "supp_sched_after": wrong_class_after,
        },
    )
    claim = mutated.cognitive_claims["claim_pkg_schedule_trap"]
    record = mutated.cognitive_status_records["status_pkg_schedule_trap"]

    assert mutated.schedules[record.schedule_record].challenge_class == claim.challenge_class
    assert schedule_trap_case(mutated, claim, record) is False
    assert classify_cognitive_status(mutated, "claim_pkg_schedule_trap")[0] is CognitiveStatus.unclassified


def test_e10_status_record_matching_is_claim_scoped_across_all_apparatuses() -> None:
    fixture = build_fixture()

    cognitive_record = fixture.cognitive_status_records["status_pkg_nav_cognitive"]
    exact_cognitive = fixture.cognitive_claims["claim_pkg_nav_cognitive"]
    wrong_cognitive = CognitiveClaimRef("wrong_class", "pkg_nav_cognitive", "C_other")
    assert cognitive_status_record_matches_claim(exact_cognitive, cognitive_record) is True
    assert cognitive_status_record_matches_claim(wrong_cognitive, cognitive_record) is False

    intention_record = fixture.intention_status_records["status_intention_clean"]
    exact_intention = fixture.intention_claims["claim_intention_clean"]
    wrong_intention = replace(exact_intention, target_class="T_other")
    assert intention_status_record_matches_claim(exact_intention, intention_record) is True
    assert intention_status_record_matches_claim(wrong_intention, intention_record) is False

    goal_record = fixture.goal_status_records["status_goal_clean"]
    exact_goal = fixture.goal_claims["claim_goal_clean"]
    wrong_goal = replace(exact_goal, theta="theta_not_goal")
    assert goal_status_record_matches_claim(exact_goal, goal_record) is True
    assert goal_status_record_matches_claim(wrong_goal, goal_record) is False


def test_e10_mandatory_falsifier_priorities_win_over_superficial_positive_evidence() -> None:
    fixture = build_fixture()

    decodable_claim = fixture.cognitive_claims["ctrl_decodable_priority_blocks_cognitive"]
    decodable_record = fixture.cognitive_status_records["status_priority_decodable"]
    assert decodable_correlate_case(fixture, decodable_claim, decodable_record) is True
    assert package_repair_descent(fixture, "desc_priority_decodable", "pkg_priority_decodable", "C_memory") is True
    assert classify_cognitive_status(fixture, "ctrl_decodable_priority_blocks_cognitive")[0] is CognitiveStatus.decodable_correlate

    schedule_claim = fixture.cognitive_claims["ctrl_schedule_priority_blocks_cognitive"]
    schedule_record = fixture.cognitive_status_records["status_priority_schedule"]
    assert schedule_trap_case(fixture, schedule_claim, schedule_record) is True
    assert package_repair_descent(fixture, "desc_priority_schedule", "pkg_priority_schedule", "C_nav") is True
    assert classify_cognitive_status(fixture, "ctrl_schedule_priority_blocks_cognitive")[0] is CognitiveStatus.schedule_trap

    assert classify_intention_status(fixture, "ctrl_post_hoc_priority_blocks_intention")[0] is IntentionStatus.post_hoc_intention
    assert classify_goal_status(fixture, "ctrl_reward_proxy_priority_blocks_goal")[0] is GoalStatus.reward_proxy_only


def test_e10_every_route_evaluated_is_universal_not_existential() -> None:
    fixture = build_fixture()
    routes = fixture.route_sets["target_missing_eval_plan"]
    evaluations = fixture.route_evaluation_sets["target_missing_eval_plan"]

    assert len(routes) == 2
    assert len(evaluations) == 1
    assert every_route_evaluated(fixture, "target_missing_eval_plan", routes, evaluations) is False
    assert route_substitution_persistence_certified(
        fixture,
        "theta_missing_eval",
        "T_plan",
        "target_missing_eval_plan",
    ) is False
    assert classify_goal_status(fixture, "ctrl_every_route_evaluated_universal")[0] is GoalStatus.not_goal


def test_e10_uncarried_intention_and_goal_theta_packages_are_rejected() -> None:
    fixture = build_fixture()

    assert intention_evidence(
        fixture,
        "theta_uncarried_intention",
        "T_plan",
        "restrict_uncarried_intention",
    ) is False
    assert classify_intention_status(fixture, "ctrl_uncarried_intention_rejected")[0] is IntentionStatus.not_intention

    assert goal_evidence(
        fixture,
        "theta_uncarried_goal",
        "T_plan",
        "target_uncarried_goal_plan",
    ) is False
    assert classify_goal_status(fixture, "ctrl_uncarried_goal_rejected")[0] is GoalStatus.not_goal


def test_e10_uncarried_records_are_rejected_even_with_committed_source_tag() -> None:
    fixture = build_fixture()
    uncarried_theta = replace(
        fixture.packages["theta_uncarried_intention"],
        carried=False,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )
    mutated = replace(
        fixture,
        packages={**fixture.packages, "theta_uncarried_intention": uncarried_theta},
    )

    assert intention_evidence(
        mutated,
        "theta_uncarried_intention",
        "T_plan",
        "restrict_uncarried_intention",
    ) is False


def test_e10_discipline_checks_are_computed_from_rows_and_controls() -> None:
    fixture = build_fixture()
    rows = _status_rows(fixture)
    results = run_e10_cognitive_demarcation_sweep()
    broken_rows = {
        **rows,
        "claim_pkg_nav_cognitive": replace(rows["claim_pkg_nav_cognitive"], observed="unclassified"),
    }
    broken_results = replace(results, rows=broken_rows)

    assert _actual_scope_discipline(fixture, rows) is True
    assert _no_hardcoded_status_discipline(results) is True
    assert _no_hardcoded_status_discipline(broken_results) is False


def test_e10_fraction_data_uses_exact_rationals() -> None:
    fixture = build_fixture()

    assert isinstance(fixture.reward_proxies["reward_proxy_only_plan"].proxy_value, Fraction)
    assert fixture.reward_proxies["reward_proxy_only_plan"].proxy_value == Fraction(7, 10)
    assert fixture.reward_proxies["reward_priority_plan"].proxy_value == Fraction(9, 10)
