from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

from sixbirds_foundations_v.sweeps.e3_self_maintaining_reclosure_sweep import (
    C_APP_BASE,
    C_APP_BOUNDARY,
    EPSILON_APP,
    EPSILON_OBJ,
    MaintenanceClosureStatus,
    apparatus_distance,
    build_fixture,
    classify_maintenance_status,
    curves_separate,
    delta_maint,
    maintenance_reinstatement_for,
    run_self_maintaining_reclosure_sweep,
)
from sixbirds_foundations_v.worlds.repair_world import (
    LawfulnessStatus,
    MaintenanceAction,
    is_lawful_action,
    step,
)


F = Fraction


def test_e3_sweep_confirms_all_registered_predictions() -> None:
    results = run_self_maintaining_reclosure_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 17


def test_e3_fixture_challenge_schedule_and_maintenance_actions_are_computed() -> None:
    results = run_self_maintaining_reclosure_sweep()
    fixture = build_fixture()

    assert [fixture.config.challenge_process.challenge_at(t, t) for t in range(6)] == [
        C_APP_BASE,
        C_APP_BASE,
        C_APP_BOUNDARY,
        C_APP_BOUNDARY,
        C_APP_BOUNDARY,
        C_APP_BOUNDARY,
    ]
    assert results.challenge_schedule == {
        0: "apparatus_baseline",
        1: "apparatus_baseline",
        2: "apparatus_boundary_drift",
        3: "apparatus_boundary_drift",
        4: "apparatus_boundary_drift",
        5: "apparatus_boundary_drift",
    }
    assert results.maintenance_actions == {"rr_keep": True, "rr_repair": True}
    assert results.repair_action_lawful is True


def test_e3_full_reinstatement_equality_and_distances_match_registration() -> None:
    fixture = build_fixture()
    app_0 = fixture.apparatus["app_0"]
    app_1 = fixture.apparatus["app_1"]
    app_2_pre = fixture.apparatus["app_2_pre"]
    app_2_post = fixture.apparatus["app_2_post"]
    app_decay_0 = fixture.apparatus["app_decay_0"]
    app_decay_1 = fixture.apparatus["app_decay_1"]

    assert fixture.operators["m_keep"].apply(0) == app_1
    assert fixture.operators["m_repair"].apply(2) == app_2_post
    assert maintenance_reinstatement_for(
        fixture,
        0,
        app_0,
        app_1,
        fixture.operators["m_keep"],
        fixture.reinstatements["rr_keep"],
    )
    assert maintenance_reinstatement_for(
        fixture,
        2,
        app_2_pre,
        app_2_post,
        fixture.operators["m_repair"],
        fixture.reinstatements["rr_repair"],
    )
    assert apparatus_distance(app_1, app_0) == F(1, 8)
    assert apparatus_distance(app_2_post, app_2_pre) == F(1, 8)
    assert apparatus_distance(app_decay_1, app_decay_0) == F(3, 8)
    assert apparatus_distance(app_0, app_0) == F(0)


def test_e3_theorem_facing_rows_include_all_maintained_evidence_conjuncts() -> None:
    results = run_self_maintaining_reclosure_sweep()

    for row_name in ("maintained_free", "maintained_challenged"):
        row = results.theorem_rows[row_name]
        assert row["object_fixed"] is True
        assert row["object_coherent"] is True
        assert row["closure_occurrence_pre"] is True
        assert row["closure_occurrence_post"] is True
        assert row["operator_occurrence"] is True
        assert row["maintenance_reinstatement_for"] is True
        assert row["apparatus_maintained_step"] is True
        assert row["delta_maint_empty"] is True
        assert row["no_subsidized_witness"] is True
        assert row["regress_conditional"] is True
        assert row["two_level_fixed_point"] is True
        assert row["maintained_closure_holds"] is True


def test_e3_status_partition_rows_are_derived_as_exactly_one_branch() -> None:
    results = run_self_maintaining_reclosure_sweep()
    fixture = build_fixture()
    expected = {
        "maintained_free": MaintenanceClosureStatus.maintained_closure,
        "maintained_challenged": MaintenanceClosureStatus.maintained_closure,
        "crystal_stable": MaintenanceClosureStatus.crystal_grade,
        "subsidized_fallback": MaintenanceClosureStatus.subsidized_closure,
        "decaying_no_repair": MaintenanceClosureStatus.decaying_closure,
    }

    assert {row.name: row.status for row in results.status_rows} == {
        name: status.value for name, status in expected.items()
    }
    for name, scenario in fixture.scenarios.items():
        status, truths = classify_maintenance_status(fixture, scenario)
        assert status is expected[name]
        assert sum(truths.values()) == 1


def test_e3_e2_regress_bridge_reuses_registered_e2_tower() -> None:
    results = run_self_maintaining_reclosure_sweep()
    bridge = results.e2_bridge

    assert bridge.audited_by_tower is True
    assert bridge.capacity_realizable is True
    assert bridge.capacity_admissible is True
    assert bridge.footprint == 8
    assert bridge.cap == 8
    assert bridge.bound_holds is True
    assert bridge.e2_status == "saturated"
    assert bridge.same_level_claim_accepted is False
    assert bridge.regress_stopped is True


def test_e3_ablation_curves_and_first_separation_are_computed() -> None:
    results = run_self_maintaining_reclosure_sweep()

    assert results.ablation_pass.maintained_apparatus_curve == (
        F(0),
        F(1, 8),
        F(1, 8),
        F(1, 8),
        F(1, 8),
        F(1, 8),
    )
    assert all(value <= EPSILON_APP for value in results.ablation_pass.maintained_apparatus_curve)
    assert results.ablation_pass.apparatus_curve == (
        F(0),
        F(1, 8),
        F(3, 8),
        F(1, 2),
        F(5, 8),
        F(3, 4),
    )
    assert results.ablation_pass.object_curve == (
        F(0),
        F(1, 16),
        F(1, 16),
        F(1, 8),
        F(3, 16),
        F(5, 16),
    )
    assert curves_separate(
        results.ablation_pass.apparatus_curve,
        results.ablation_pass.object_curve,
        EPSILON_APP,
        EPSILON_OBJ,
    ) == (True, 2)
    assert results.ablation_pass.separates is True
    assert results.ablation_pass.first_separation_time == 2

    assert results.ablation_fail.apparatus_curve == (
        F(0),
        F(1, 8),
        F(1, 8),
        F(1, 8),
        F(1, 8),
        F(1, 8),
    )
    assert results.ablation_fail.object_curve == (
        F(0),
        F(1, 16),
        F(1, 16),
        F(1, 8),
        F(1, 8),
        F(1, 8),
    )
    assert all(value <= EPSILON_APP for value in results.ablation_fail.apparatus_curve)
    assert results.ablation_fail.separates is False
    assert results.ablation_fail.first_separation_time is None


def test_e3_delta_controls_distinguish_mrf_defects_from_history_omission() -> None:
    results = run_self_maintaining_reclosure_sweep()
    controls = {row.name: row for row in results.delta_controls}

    assert controls["absent_record"].maintenance_reinstatement_for is False
    assert controls["absent_record"].delta_branch == "absent_record"
    assert controls["fallback_source"].maintenance_reinstatement_for is False
    assert controls["fallback_source"].delta_branch == "bad_source_tag"
    assert controls["off_kernel"].maintenance_reinstatement_for is False
    assert controls["off_kernel"].delta_branch == "off_kernel"
    assert controls["out_of_scope"].maintenance_reinstatement_for is False
    assert controls["out_of_scope"].delta_branch == "out_of_scope"
    assert controls["non_carried"].maintenance_reinstatement_for is False
    assert controls["non_carried"].delta_branch == "generatedByS_false"

    audit_omission = controls["audit_omission"]
    assert audit_omission.maintenance_reinstatement_for is True
    assert audit_omission.delta_nonempty is True
    assert audit_omission.delta_branch == "history_omission"
    assert audit_omission.subsidized_witness is True
    assert audit_omission.maintained_closure is False
    assert audit_omission.subsidized_closure is True

    assert all(row.delta_nonempty for row in controls.values())
    assert all(row.subsidized_witness for row in controls.values())
    assert all(not row.maintained_closure for row in controls.values())
    assert all(row.subsidized_closure for row in controls.values())


def test_e3_unlinked_output_control_rejects_field_mismatch() -> None:
    results = run_self_maintaining_reclosure_sweep()
    unlinked = results.unlinked_control

    assert unlinked["carried_operator_shaped_record_exists"] is True
    assert unlinked["carried_next_apparatus_record_exists"] is True
    assert unlinked["full_output_equality"] is False
    assert unlinked["maintenance_action_lawful"] is False
    assert unlinked["maintenance_reinstatement_for"] is False
    assert unlinked["apparatus_maintained_step"] is False


def test_e3_maintenance_action_derives_apply_result_instead_of_trusting_caller() -> None:
    fixture = build_fixture()
    app_1 = fixture.apparatus["app_1"]
    app_wrong = fixture.apparatus["app_wrong"]
    operator = replace(fixture.operators["m_keep"], outputs={0: app_wrong})
    record = fixture.reinstatements["rr_keep"]
    state = fixture.states["app_0"]
    action = MaintenanceAction(
        operator=operator,
        source_state=record.source_state,
        target_state=record.target_state,
        current_audit_state=state.A,
        claimed_next_apparatus=app_1,
        source_tag=record.source_tag,
        generated_by_s=record.generated_by_s,
        in_scope=record.in_scope,
        reinstatement_ledger_entry=record.reinstatement_ledger_entry,
    )

    assert operator.apply(record.source_state) == app_wrong
    assert action.claimed_next_apparatus == app_1
    assert is_lawful_action(fixture.config, state, action).status is LawfulnessStatus.unlawful


def test_e3_maintenance_action_cannot_forge_next_audit_state() -> None:
    fixture = build_fixture()
    app_1 = fixture.apparatus["app_1"]
    operator = fixture.operators["m_keep"]
    record = fixture.reinstatements["rr_keep"]
    state = fixture.states["app_0"]

    action = MaintenanceAction(
        operator=operator,
        source_state=record.source_state,
        target_state=record.target_state,
        current_audit_state=state.A,
        claimed_next_apparatus=app_1,
        source_tag=record.source_tag,
        generated_by_s=record.generated_by_s,
        in_scope=record.in_scope,
        reinstatement_ledger_entry=record.reinstatement_ledger_entry,
    )
    assert is_lawful_action(fixture.config, state, action).status is LawfulnessStatus.lawful
    stepped = step(fixture.config, state, action)
    assert stepped.y == record.target_state
    assert stepped.A == state.A

    try:
        MaintenanceAction(
            operator=operator,
            source_state=record.source_state,
            target_state=record.target_state,
            current_audit_state=state.A,
            next_audit_state=object(),
            claimed_next_apparatus=app_1,
            source_tag=record.source_tag,
            generated_by_s=record.generated_by_s,
            in_scope=record.in_scope,
            reinstatement_ledger_entry=record.reinstatement_ledger_entry,
        )
    except TypeError:
        forged_field_rejected = True
    else:
        forged_field_rejected = False
    assert forged_field_rejected is True


def test_e3_scope_and_hardcoding_guards_pass() -> None:
    results = run_self_maintaining_reclosure_sweep()

    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True
