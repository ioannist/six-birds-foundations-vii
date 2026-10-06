from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

from sixbirds_foundations_v.carried_records import FineSourceTag
from sixbirds_foundations_v.probe_economy import acquisition_strict
from sixbirds_foundations_v.sweeps.e5_reclosure_collapse_sweep import (
    CHALLENGE,
    H0,
    H1,
    N_STATES,
    OTHER_CHALLENGE,
    ReclosureCollapseStatus,
    apparatus_intact,
    binding_operational_challenge_active,
    build_fixture,
    candidate_acquisition,
    classify_reclosure_collapse_status,
    collapse_budget_feasible,
    collapse_falsifier,
    collapse_rescue_admissible_in_budget,
    collapse_rescue_descends,
    complete_collapse_rescue_inventory,
    constructible_self_candidates,
    descent_certificate_structurally_linked,
    external_subsidy_witness,
    irreversibility_coherence,
    irreversible_collapse_input,
    no_active_external_subsidy_after_withdrawal,
    operations_gated_off,
    rescue_candidate_constructible,
    rescue_move_credited_for_descent,
    run_e5_reclosure_collapse_sweep,
    scenario_statused_residuals,
    statused_residual_accrual,
    subsidizer_budget_feasible,
    subsidizer_move_descends,
    suspension_witness,
)


def test_e5_sweep_confirms_all_registered_predictions() -> None:
    results = run_e5_reclosure_collapse_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 20
    assert len(results.scenario_rows) == 11
    assert len(results.controls) == 9


def test_e5_ring_fixture_and_schedules_match_preregistration() -> None:
    fixture = build_fixture()

    assert fixture.kernel.n_states == N_STATES
    assert N_STATES == 18
    assert fixture.kernel.P[1, 17, 0] == 1.0
    assert all(enabled is False for time, _operation, enabled in fixture.operation_gates if time == 3)
    assert operations_gated_off(fixture, H0) is True
    assert binding_operational_challenge_active(fixture, CHALLENGE, H0) is False
    assert binding_operational_challenge_active(fixture, CHALLENGE, H1) is False


def test_e5_status_rows_are_priority_classified() -> None:
    rows = {row.scenario: row for row in run_e5_reclosure_collapse_sweep().scenario_rows}
    expected = {
        "scn_viable_self_repair": "viable",
        "scn_stressed_self_repair": "stressed",
        "scn_viable_boundary_update": "viable",
        "scn_viable_acquisition": "viable",
        "scn_viable_apparatus_reclosure": "viable",
        "scn_subsidized_external_rescue": "subsidized",
        "scn_suspended_gated_operations": "suspended",
        "scn_collapsed_recoverable": "collapsed_recoverable",
        "scn_collapsed_irreversible": "collapsed_irreversible",
        "scn_revived_new_lineage": "revived",
        "scn_post_withdrawal_reclassified": "viable",
    }

    for scenario, status in expected.items():
        row = rows[scenario]
        assert row.status == status
        assert row.complete_inventory is True
        assert sum(
            (
                row.revived,
                row.subsidized,
                row.suspended,
                row.viable,
                row.stressed,
                row.collapsed_irreversible,
                row.collapsed_recoverable,
            )
        ) == 1


def test_e5_all_four_rescue_families_have_positive_coverage() -> None:
    fixture = build_fixture()
    positive = {
        "repair": "mv_repair_viable",
        "boundary": "mv_boundary_viable",
        "apparatus_reclosure": "mv_reclosure_viable",
        "acquisition": "mv_acquisition_viable",
    }

    for move_name in positive.values():
        candidate = fixture.candidates[move_name]
        assert rescue_candidate_constructible(fixture, candidate) is True
        assert collapse_rescue_admissible_in_budget(fixture, candidate) is True
        assert collapse_rescue_descends(candidate) is True


def test_e5_boundary_update_positive_and_off_kernel_control_are_distinct() -> None:
    fixture = build_fixture()
    positive = fixture.candidates["mv_boundary_viable"]
    off_kernel = fixture.candidates["mv_recover_off_kernel_boundary"]

    assert positive.payload.pre_source == 16
    assert positive.payload.post_target == 17
    assert rescue_candidate_constructible(fixture, positive) is True
    assert collapse_rescue_descends(positive) is True

    assert off_kernel.payload.pre_source == 8
    assert off_kernel.payload.post_target == 10
    assert rescue_candidate_constructible(fixture, off_kernel) is False
    assert "mv_recover_off_kernel_boundary" not in fixture.scenarios[
        "scn_collapsed_recoverable"
    ].declared_candidates


def test_e5_acquisition_positive_uses_probe_economy_machinery() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["mv_acquisition_viable"]
    payload = candidate.payload

    assert payload.probe == "probe_stabilizer"
    assert fixture.probe_economy.catalog.contains(payload.probe) is True
    assert acquisition_strict(
        fixture.probe_economy.same_family_saturated,
        payload.active_family,
        payload.probe,
    ) is True
    assert candidate_acquisition(fixture, payload) is True
    assert collapse_rescue_admissible_in_budget(fixture, candidate) is True


def test_e5_viable_apparatus_reclosure_exercises_non_revival_path() -> None:
    fixture = build_fixture()
    scenario = fixture.scenarios["scn_viable_apparatus_reclosure"]
    candidate = fixture.candidates["mv_reclosure_viable"]

    status, truths, record = classify_reclosure_collapse_status(fixture, scenario.name)

    assert scenario.revival is None
    assert candidate.payload.record.source_state == 5
    assert candidate.payload.record.target_state == 6
    assert rescue_candidate_constructible(fixture, candidate) is True
    assert collapse_rescue_admissible_in_budget(fixture, candidate) is True
    assert collapse_rescue_descends(candidate) is True
    assert truths["revived"] is False
    assert truths["viable"] is True
    assert status is ReclosureCollapseStatus.viable
    assert record is not None
    assert record.rescue_move_record == candidate.move_record


def test_e5_constructive_falsifier_defeats_collapsed_core() -> None:
    fixture = build_fixture()
    scenario = fixture.scenarios["scn_viable_self_repair"]

    assert complete_collapse_rescue_inventory(fixture, scenario) is True
    assert collapse_falsifier(fixture, scenario) is True
    row = {row.scenario: row for row in run_e5_reclosure_collapse_sweep().scenario_rows}[
        "scn_viable_self_repair"
    ]
    assert row.collapsed_core is False


def test_e5_stressed_depends_on_same_scope_residual() -> None:
    fixture = build_fixture()
    stressed = fixture.scenarios["scn_stressed_self_repair"]
    viable = fixture.scenarios["scn_viable_self_repair"]

    assert tuple(residual.name for residual in scenario_statused_residuals(fixture, stressed)) == (
        "residual_stressed",
    )
    assert scenario_statused_residuals(fixture, viable) == ()
    assert classify_reclosure_collapse_status(fixture, stressed.name)[0] is ReclosureCollapseStatus.stressed


def test_e5_suspension_inputs_are_computed_from_fixture_data() -> None:
    fixture = build_fixture()
    scenario = fixture.scenarios["scn_suspended_gated_operations"]
    witness = fixture.suspensions["suspension_ops_gate"]

    assert operations_gated_off(fixture, H0) is True
    assert apparatus_intact(fixture, witness) is True
    assert binding_operational_challenge_active(fixture, CHALLENGE, H0) is False
    assert suspension_witness(fixture, scenario, witness) is True
    assert classify_reclosure_collapse_status(fixture, scenario.name)[0] is ReclosureCollapseStatus.suspended


def test_e5_subsidized_is_external_only_and_not_self_carried() -> None:
    fixture = build_fixture()
    scenario = fixture.scenarios["scn_subsidized_external_rescue"]
    subsidy = fixture.subsidies["subsidy_ext_1"]

    assert external_subsidy_witness(fixture, scenario, subsidy) is True
    assert subsidizer_budget_feasible(subsidy) is True
    assert subsidizer_move_descends(subsidy) is True
    assert all(
        fixture.candidates[name].move_record != subsidy.supplied_move.move_record
        for name in constructible_self_candidates(fixture, scenario)
    )
    assert collapse_falsifier(fixture, scenario) is False
    assert classify_reclosure_collapse_status(fixture, scenario.name)[0] is ReclosureCollapseStatus.subsidized


def test_e5_over_budget_descent_does_not_falsify_collapse() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["mv_ctrl_over_budget"]

    assert collapse_rescue_descends(candidate) is True
    assert candidate.payload.budget.spend == Fraction(3, 2)
    assert collapse_rescue_admissible_in_budget(fixture, candidate) is False


def test_e5_budget_witness_must_belong_to_candidate_move() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["mv_repair_viable"]
    other = fixture.candidates["mv_repair_stressed"]

    mismatched_budget = replace(candidate.payload.budget, move_record=other.move_record)

    assert mismatched_budget.spend <= mismatched_budget.budget
    assert collapse_budget_feasible(fixture, candidate.payload.budget, candidate.move_record) is True
    assert collapse_budget_feasible(fixture, mismatched_budget, candidate.move_record) is False


def test_e5_unlinked_descent_certificate_is_rejected_before_candidate_exists() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["mv_ctrl_unlinked_candidate"]
    cert = candidate.payload.descent

    assert cert.descent_for_move.name == "mv_ctrl_unlinked_named"
    assert descent_certificate_structurally_linked(cert) is False
    assert rescue_move_credited_for_descent(candidate.move_record, cert.descent_readout_record) is False
    assert rescue_candidate_constructible(fixture, candidate) is False


def test_e5_fallback_uncarried_candidate_is_rejected() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["mv_ctrl_fallback"]
    payload = candidate.payload

    assert payload.source_tag is FineSourceTag.fallback
    assert payload.generated_by_s is False
    assert payload.in_scope is False
    assert collapse_rescue_descends(candidate) is True
    assert rescue_candidate_constructible(fixture, candidate) is False


def test_e5_irreversibility_coherence_rejects_inconsistent_pair() -> None:
    fixture = build_fixture()
    good_reach = fixture.reachability["reach_irrev"]
    good_kernel = fixture.kernels["kernel_irrev"]
    bad_reach = fixture.reachability["reach_inconsistent"]
    bad_kernel = fixture.kernels["kernel_nonempty_bad"]

    assert irreversibility_coherence(good_reach, good_kernel, CHALLENGE, H0) is True
    assert irreversible_collapse_input(good_reach, good_kernel, CHALLENGE, H0) is True
    assert irreversibility_coherence(bad_reach, bad_kernel, CHALLENGE, H0) is False
    assert irreversible_collapse_input(bad_reach, bad_kernel, CHALLENGE, H0) is False


def test_e5_irreversibility_coherence_rejects_wrong_scope_pair() -> None:
    fixture = build_fixture()
    wrong_scope_reach = replace(
        fixture.reachability["reach_irrev"],
        name="reach_wrong_scope",
        challenge_class=OTHER_CHALLENGE,
        horizon=H1,
    )
    wrong_scope_kernel = replace(
        fixture.kernels["kernel_irrev"],
        name="kernel_wrong_scope",
        challenge_class=OTHER_CHALLENGE,
        horizon=H1,
    )

    assert irreversibility_coherence(wrong_scope_reach, wrong_scope_kernel, OTHER_CHALLENGE, H1) is True
    assert irreversibility_coherence(wrong_scope_reach, wrong_scope_kernel, CHALLENGE, H0) is False
    assert irreversible_collapse_input(wrong_scope_reach, wrong_scope_kernel, CHALLENGE, H0) is False


def test_e5_wrong_scope_residual_does_not_reclassify_viable() -> None:
    fixture = build_fixture()

    global_same_scope = statused_residual_accrual(fixture, CHALLENGE, H0)
    assert "residual_wrong_scope" not in {residual.name for residual in global_same_scope}
    status = classify_reclosure_collapse_status(fixture, "scn_viable_self_repair")[0]
    assert status is ReclosureCollapseStatus.viable


def test_e5_incomplete_inventory_attempt_is_not_creditable() -> None:
    fixture = build_fixture()
    scenario = fixture.scenarios["ctrl_incomplete_inventory_attempt"]

    assert constructible_self_candidates(fixture, scenario) == ("mv_repair_viable",)
    assert scenario.declared_candidates == ()
    assert complete_collapse_rescue_inventory(fixture, scenario) is False
    assert collapse_falsifier(fixture, scenario) is False


def test_e5_active_collapsed_system_activity_is_not_rescue() -> None:
    fixture = build_fixture()
    scenario = fixture.scenarios["scn_collapsed_recoverable"]
    activity = scenario.ordinary_activity[0]

    assert activity.name == "ordinary_tick"
    assert activity.source == 0
    assert activity.target == 1
    assert activity.rescue_move is False
    assert collapse_falsifier(fixture, scenario) is False
    assert classify_reclosure_collapse_status(fixture, scenario.name)[0] is ReclosureCollapseStatus.collapsed_recoverable


def test_e5_subsidy_withdrawal_reclassifies_to_non_subsidized_status() -> None:
    fixture = build_fixture()

    assert classify_reclosure_collapse_status(fixture, "scn_subsidized_external_rescue")[0] is ReclosureCollapseStatus.subsidized
    assert no_active_external_subsidy_after_withdrawal(fixture) is True
    assert fixture.active_subsidies[(CHALLENGE, H1)] == ()
    assert classify_reclosure_collapse_status(fixture, "scn_post_withdrawal_reclassified")[0] is ReclosureCollapseStatus.viable


def test_e5_scope_and_anti_hardcoding_guards_are_computed() -> None:
    results = run_e5_reclosure_collapse_sweep()
    fixture = build_fixture()

    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True
    for row in results.scenario_rows:
        assert row.carried_status_record in fixture.carried_status_records
        assert row.status != ReclosureCollapseStatus.unclassified.value
