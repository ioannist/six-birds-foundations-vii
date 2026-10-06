from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import pytest

from sixbirds_foundations_v.sweeps.e8_control_price_sweep import (
    BudgetAuditStatus,
    ControlPriceStatus,
    SlackResidualExplanationRecord,
    build_fixture,
    budget_inflates,
    budget_inflation_audit,
    capture_detected_case,
    capture_claim_rejected_case,
    classify_budget_audit_status,
    classify_control_price_status,
    component_shadow_price_lawful,
    control_claim_contains_component,
    field_complete_for_declared_constraints,
    omega_lineage_blind_spot,
    proxy_failure,
    run_e8_control_price_sweep,
    slack_collapse_violation,
    summary_lawful,
    summary_predictive_legitimacy,
    summary_slack_collapse,
)
from sixbirds_foundations_v.sweeps.e2_bounded_reflexivity_sweep import (
    capacity_bound_holds,
    capacity_saturated,
    tower_footprint,
)


def test_e8_sweep_confirms_all_registered_predictions() -> None:
    results = run_e8_control_price_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 21
    assert len(results.main_rows) == 8
    assert len(results.budget_rows) == 5
    assert len(results.controls) == 8
    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True


@pytest.mark.parametrize(
    ("claim", "expected"),
    (
        ("claim_component_cpu_lawful", ControlPriceStatus.component_lawful),
        ("claim_field_ops_lawful", ControlPriceStatus.field_lawful),
        ("claim_summary_ops_lawful", ControlPriceStatus.summary_lawful),
        ("claim_summary_slack_obstructed", ControlPriceStatus.slack_obstructed),
        ("claim_component_io_slack", ControlPriceStatus.slack_obstructed),
        ("claim_component_proxy", ControlPriceStatus.proxy_obstructed),
        ("claim_summary_redescription", ControlPriceStatus.summary_redescription),
        ("claim_field_incomplete", ControlPriceStatus.incomplete_or_unpriced),
    ),
)
def test_e8_main_control_price_registered_statuses(
    claim: str,
    expected: ControlPriceStatus,
) -> None:
    fixture = build_fixture()
    status, truths, record = classify_control_price_status(fixture, claim)

    assert status is expected
    assert record is not None
    assert sum(truths.values()) == 1


@pytest.mark.parametrize(
    ("claim", "expected"),
    (
        ("claim_shared_discharge", BudgetAuditStatus.residual_discharge_verified),
        ("claim_shared_capture", BudgetAuditStatus.capture_detected),
        ("claim_no_capture_rejected", BudgetAuditStatus.capture_claim_rejected),
        ("claim_capacity_blocked", BudgetAuditStatus.meta_audit_capacity_blocked),
        ("claim_missing_meta_audit", BudgetAuditStatus.meta_audit_missing),
    ),
)
def test_e8_budget_audit_registered_statuses(
    claim: str,
    expected: BudgetAuditStatus,
) -> None:
    fixture = build_fixture()
    status, truths, record = classify_budget_audit_status(fixture, claim)

    assert status is expected
    assert record is not None
    assert sum(truths.values()) == 1


def test_e8_component_binding_shadow_price_is_computed_from_fixture_data() -> None:
    fixture = build_fixture()
    component = fixture.components["cmp_cpu_bind"]

    assert component.spend == component.budget
    assert component.marginal_discharge / component.marginal_cost == Fraction(3, 2)
    assert component.kkt.lambda_value == Fraction(3, 2)
    assert component.component_record.lambda_value == component.kkt.lambda_value
    assert component_shadow_price_lawful(fixture, "cmp_cpu_bind") is True


def test_e8_summary_slack_obstructed_uses_summary_disjunct_not_component_disjunct() -> None:
    fixture = build_fixture()
    claim = fixture.control_claims["claim_summary_slack_obstructed"]
    status, truths, _record = classify_control_price_status(fixture, "claim_summary_slack_obstructed")

    assert status is ControlPriceStatus.slack_obstructed
    assert truths["slack_obstructed"] is True
    assert summary_predictive_legitimacy(fixture, "summary_slack_obstructed") is True
    assert summary_slack_collapse(fixture, "summary_slack_obstructed") is False
    assert all(
        slack_collapse_violation(fixture, component_name) is False
        for component_name in fixture.fields["field_summary_slack"].components
    )
    assert claim.kind.value == "summary"


def test_e8_linked_slack_residual_explanation_blocks_violation() -> None:
    fixture = build_fixture()
    component = fixture.components["cmp_io_slack_violation"]
    explanation = SlackResidualExplanationRecord(
        name="explain_io_slack",
        signal_ref=component.signal_record.name,
        component_ref=component.component_record.name,
    )
    mutated = replace(
        fixture,
        slack_residual_explanations={
            **fixture.slack_residual_explanations,
            explanation.name: explanation,
        },
    )

    assert slack_collapse_violation(fixture, "cmp_io_slack_violation") is True
    assert slack_collapse_violation(mutated, "cmp_io_slack_violation") is False


def test_e8_field_slack_obstruction_is_claim_kind_aware() -> None:
    fixture = build_fixture()
    member_claim = fixture.control_claims["ctrl_field_member_slack_obstruction"]
    unrelated_claim = fixture.control_claims["ctrl_unrelated_component_not_obstructing_field"]

    assert control_claim_contains_component(fixture, member_claim, "cmp_io_slack_violation") is True
    assert classify_control_price_status(fixture, "ctrl_field_member_slack_obstruction")[0] is ControlPriceStatus.slack_obstructed

    assert control_claim_contains_component(fixture, unrelated_claim, "cmp_unrelated_slack_violation") is False
    assert classify_control_price_status(fixture, "ctrl_unrelated_component_not_obstructing_field")[0] is ControlPriceStatus.field_lawful


def test_e8_proxy_failure_uses_three_shared_comparator_failures() -> None:
    fixture = build_fixture()
    component = fixture.components["cmp_proxy_bind"]

    assert fixture.proxy_prediction_records["cmp_proxy_bind"].hit is False
    assert fixture.proxy_stability_records["cmp_proxy_bind"].lambda_drift == Fraction(1, 5)
    assert fixture.ledger_comparator.aligned(
        component.signal_record,
        component.constraint_record,
        component.spend,
        component.budget,
        component.component_record.lambda_value,
    ) is False
    assert proxy_failure(fixture, "cmp_proxy_bind") is True
    assert classify_control_price_status(fixture, "claim_component_proxy")[0] is ControlPriceStatus.proxy_obstructed


def test_e8_proxy_failure_does_not_fabricate_worst_case_witnesses() -> None:
    fixture = build_fixture()
    component = fixture.components["cmp_unrelated_slack_violation"]
    prediction = fixture.proxy_prediction_records["cmp_unrelated_slack_violation"]
    stability = fixture.proxy_stability_records["cmp_unrelated_slack_violation"]

    assert fixture.ledger_comparator.aligned(
        component.signal_record,
        component.constraint_record,
        component.spend,
        component.budget,
        component.component_record.lambda_value,
    ) is False
    assert fixture.prediction_comparator.predicts(component.signal_record, prediction) is True
    assert fixture.stability_comparator.stable(component.signal_record, stability) is True
    assert proxy_failure(fixture, "cmp_unrelated_slack_violation") is False


def test_e8_summary_legitimacy_comparators_are_not_trivial() -> None:
    fixture = build_fixture()

    assert summary_predictive_legitimacy(fixture, "summary_ops_lawful") is True
    assert summary_lawful(fixture, "summary_ops_lawful") is True
    assert summary_predictive_legitimacy(fixture, "summary_redescription") is False
    assert classify_control_price_status(fixture, "claim_summary_redescription")[0] is ControlPriceStatus.summary_redescription


def test_e8_field_completion_is_checked_against_declared_constraints() -> None:
    fixture = build_fixture()

    assert field_complete_for_declared_constraints(fixture, "field_ops_lawful") is True
    assert field_complete_for_declared_constraints(fixture, "field_incomplete") is False
    assert classify_control_price_status(fixture, "claim_field_incomplete")[0] is ControlPriceStatus.incomplete_or_unpriced


def test_e8_budget_audit_claim_ref_uses_full_triple_scope() -> None:
    fixture = build_fixture()

    assert fixture.budget_claims["claim_shared_discharge"].budget_move_record == "bm_shared"
    assert fixture.budget_claims["claim_shared_capture"].budget_move_record == "bm_shared"
    assert fixture.budget_claims["claim_shared_discharge"].lineage_record != fixture.budget_claims["claim_shared_capture"].lineage_record
    assert classify_budget_audit_status(fixture, "claim_shared_discharge")[0] is BudgetAuditStatus.residual_discharge_verified
    assert classify_budget_audit_status(fixture, "claim_shared_capture")[0] is BudgetAuditStatus.capture_detected


def test_e8_no_capture_rejection_reads_carried_blind_spot_record() -> None:
    fixture = build_fixture()
    audit = fixture.no_capture_audits["no_capture"]
    blind = fixture.blind_spot_audits[audit.blind_spot_record]

    assert audit.lineage_record == "lineage_no_capture"
    assert blind.lineage_ref == audit.lineage_record
    assert blind.hazard == 0
    assert omega_lineage_blind_spot(blind.hazard) is False
    assert classify_budget_audit_status(fixture, "claim_no_capture_rejected")[0] is BudgetAuditStatus.capture_claim_rejected


def test_e8_capture_rejection_requires_claimed_capture_record_linkage() -> None:
    fixture = build_fixture()
    claim = fixture.budget_claims["claim_no_capture_rejected"]
    record = fixture.budget_status_records["status_no_capture_rejected"]
    retargeted = replace(
        fixture.meta_audit_records["meta_no_capture"],
        budget_move_ref="bm_shared",
    )
    mutated = replace(
        fixture,
        meta_audit_records={
            **fixture.meta_audit_records,
            "meta_no_capture": retargeted,
        },
    )

    assert capture_claim_rejected_case(fixture, claim, record) is True
    assert capture_claim_rejected_case(mutated, claim, record) is False


def test_e8_wrong_lineage_capture_claim_is_rejected() -> None:
    fixture = build_fixture()
    claim = fixture.budget_claims["ctrl_wrong_lineage_capture_claim"]
    record = fixture.budget_status_records["status_wrong_lineage_capture"]

    assert omega_lineage_blind_spot(1) is True
    assert fixture.budget_moves["bm_wrong_lineage"].old_budget < fixture.budget_moves["bm_wrong_lineage"].new_budget
    assert budget_inflation_audit(fixture, "inflation_wrong_lineage", claim) is False
    assert capture_detected_case(fixture, claim, record) is False


def test_e8_budget_inflation_ignores_disconnected_metadata_flag() -> None:
    fixture = build_fixture()
    claim = fixture.budget_claims["ctrl_disconnected_budget_inflation_flag"]
    record = fixture.budget_status_records["status_disconnected_budget_flag"]
    move = fixture.budget_moves["bm_equal_budget_metadata_inflated"]

    assert move.reported_inflated is True
    assert move.old_budget == move.new_budget == Fraction(12)
    assert budget_inflates(move) is False
    assert budget_inflation_audit(fixture, "inflation_flag_blind", claim) is False
    assert capture_detected_case(fixture, claim, record) is False


def test_e8_inflation_without_blindspot_is_residual_discharge_not_capture() -> None:
    fixture = build_fixture()

    assert budget_inflates(fixture.budget_moves["bm_inflation_no_blind"]) is True
    assert omega_lineage_blind_spot(0) is False
    assert classify_budget_audit_status(fixture, "claim_inflation_no_blind")[0] is BudgetAuditStatus.residual_discharge_verified


def test_e8_e2_capacity_bound_is_computed_from_tower_records() -> None:
    fixture = build_fixture()
    bound = fixture.e2_bounds["capacity_bound"]

    assert tower_footprint(bound.levels) == 8
    assert capacity_bound_holds(bound.levels, bound.cap) is True
    assert capacity_saturated(bound.levels, bound.cap) is True
    assert classify_budget_audit_status(fixture, "claim_capacity_blocked")[0] is BudgetAuditStatus.meta_audit_capacity_blocked
