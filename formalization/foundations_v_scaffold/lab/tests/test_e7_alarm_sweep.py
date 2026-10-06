from __future__ import annotations

from fractions import Fraction

from sixbirds_foundations_v.sweeps.e7_alarm_sweep import (
    F,
    SAFE_KERNEL,
    run_alarm_sweep,
)
from sixbirds_foundations_v.xi import mat


def test_e7_alarm_sweep_confirms_all_registered_predictions() -> None:
    results = run_alarm_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []


def test_e7_xi_witness_fixture_is_exact() -> None:
    results = run_alarm_sweep()

    for hazard_level in (0, 1, 2, 3):
        witness = results.xi_witnesses[hazard_level]
        expected = Fraction(hazard_level * hazard_level)
        assert witness.residual_matrix == mat([[expected]])
        assert witness.delta_xi == mat([[expected]])
        assert witness.excess == expected
        assert witness.blind_spot_witness is (hazard_level > 0)


def test_e7_existential_kernel_and_detection_latency_match_registration() -> None:
    results = run_alarm_sweep()

    assert results.existential_kernel_preempt == set(SAFE_KERNEL)
    assert results.existential_kernel_in_policy == set(SAFE_KERNEL)

    assert (
        results.latency_by_budget[0].currentized,
        results.latency_by_budget[0].currentization_time,
        results.latency_by_budget[0].latency,
        results.latency_by_budget[0].final_state,
    ) == (False, None, None, 5)
    assert (
        results.latency_by_budget[1].currentized,
        results.latency_by_budget[1].currentization_time,
        results.latency_by_budget[1].latency,
        results.latency_by_budget[1].final_state,
    ) == (True, 3, 2, 4)
    assert (
        results.latency_by_budget[2].currentized,
        results.latency_by_budget[2].currentization_time,
        results.latency_by_budget[2].latency,
        results.latency_by_budget[2].final_state,
    ) == (True, 2, 1, 4)
    assert (
        results.latency_by_budget[3].currentized,
        results.latency_by_budget[3].currentization_time,
        results.latency_by_budget[3].latency,
        results.latency_by_budget[3].final_state,
    ) == (True, 1, 0, 4)


def test_e7_policy_realized_preemption_beats_in_policy_competition() -> None:
    results = run_alarm_sweep()

    outcomes = {outcome.config: outcome for outcome in results.matched_outcomes}
    assert set(outcomes) == {"N0", "H1", "H2", "H3"}

    assert sum(outcome.preemption_survived for outcome in outcomes.values()) == 4
    assert sum(not outcome.preemption_survived for outcome in outcomes.values()) == 0
    assert sum(outcome.in_policy_survived for outcome in outcomes.values()) == 1
    assert sum(not outcome.in_policy_survived for outcome in outcomes.values()) == 3

    for config_name in ("H1", "H2", "H3"):
        outcome = outcomes[config_name]
        assert outcome.preemption_survived
        assert not outcome.in_policy_survived
        assert "A" in outcome.preemption_actions
        assert "A" not in outcome.in_policy_actions
        assert outcome.in_policy_path[-1] == 5
        assert outcome.preemption_path[-1] == 4


def test_e7_threshold_census_and_protocol_artifact_control_match_registration() -> None:
    results = run_alarm_sweep()

    lawful_rows = tuple(
        (
            row.theta,
            row.true_currentizations,
            row.lawful_artifact_discounts,
            row.false_alarms,
            row.missed_genuine_alarms,
        )
        for row in results.lawful_census.values()
    )
    assert lawful_rows == (
        (0, 3, 2, 0, 0),
        (1, 2, 1, 0, 1),
        (2, 1, 0, 0, 2),
        (3, 0, 0, 0, 3),
    )

    no_audit_rows = tuple(
        (row.theta, row.false_alarms, row.missed_genuine_alarms)
        for row in results.no_audit_census.values()
    )
    assert no_audit_rows == (
        (0, 2, 0),
        (1, 1, 1),
        (2, 0, 2),
        (3, 0, 3),
    )

    assert results.protocol_artifacts[0].disposition == "lawful_discount(protocol_artifact)"
    assert results.protocol_artifacts[1].disposition == "lawful_discount(protocol_artifact)"
    assert results.protocol_artifacts[2].disposition == "none"
    assert results.protocol_artifacts[3].disposition == "none"
    assert all(not row.viability_coupled for row in results.protocol_artifacts.values())
    assert all(not row.currentization_holds for row in results.protocol_artifacts.values())
    assert all(row.false_alarm_count == 0 for row in results.protocol_artifacts.values())


def test_e7_preemption_signature_is_recorded_for_currentizations() -> None:
    results = run_alarm_sweep()

    rewrites = [
        row.rewrite
        for row in results.latency_by_budget.values()
        if row.rewrite is not None
    ]
    for outcome in results.matched_outcomes:
        rewrites.extend(outcome.preemption_rewrites)

    assert rewrites
    for rewrite in rewrites:
        assert rewrite.pre != rewrite.post
        assert rewrite.pre.preempted_witness is None
        assert rewrite.post.preempted_witness == (F(1),)
        assert rewrite.post.witness_exposure_admissible((F(1),))
        assert rewrite.preemption_signature_holds

