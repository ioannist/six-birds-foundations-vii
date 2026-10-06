from __future__ import annotations

import pytest

from sixbirds_foundations_v.e_system import RepairSort
from sixbirds_foundations_v.probe_economy import same_family_saturated
from sixbirds_foundations_v.sweeps.e4_repair_compilation_sweep import (
    N_STATES,
    THRESHOLD,
    ConstructionRejected,
    CompilationStatus,
    GateStatus,
    PromotionBridgeData,
    PromotionStatus,
    StrictGateStatus,
    _pass_gates,
    _rejected_gates,
    accepted_promotion_family,
    build_fixture,
    build_window_no_obstruction_reduction,
    build_window_payload_drift,
    build_window_too_short,
    build_wrong_sort_candidate,
    carried_obstruction_status_for,
    classify_compilation_status,
    compilation_lawful,
    compiled_descent,
    compiled_operator_record_attributed_to,
    decompilation_event_exists,
    e4_brittleness_instance,
    higher_package_goes_silent,
    idempotence_stable_across_window,
    obstruction_reducing_across_window,
    out_of_class_obstruction_witness,
    promote,
    promotion_accepted_core_bool,
    required_core_gates_pass_bool,
    run_e4_repair_compilation_sweep,
    top_down_channel_accepted_bool,
)


def test_e4_sweep_confirms_all_registered_predictions() -> None:
    results = run_e4_repair_compilation_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 16


def test_e4_ring_fixture_and_window_match_preregistration() -> None:
    fixture = build_fixture()

    assert fixture.config.kernel.n_states == N_STATES
    assert N_STATES == 20
    assert fixture.config.e_system.T.supp_k(19, 0) is True
    assert fixture.window.episode_times == (0, 1, 2)
    assert len(fixture.window.episode_times) >= 2
    assert obstruction_reducing_across_window(fixture, fixture.window) is True
    assert idempotence_stable_across_window(fixture.window, THRESHOLD) is True


def test_e4_candidate_status_rows_are_computed() -> None:
    rows = {row.candidate_opt: row for row in run_e4_repair_compilation_sweep().candidate_rows}
    expected = {
        "none": ("exposed", None, None, None, None, None),
        "cand_compiled": ("compiled", True, True, True, False, False),
        "cand_compiled_support_gate": ("compiled", True, True, True, False, False),
        "cand_mis_compiled": ("mis_compiled", True, True, True, False, True),
        "cand_decompiled": ("decompiled", True, True, True, True, False),
        "cand_compiling_blocked_channel": ("compiling", False, True, True, False, False),
        "cand_compiling_promotion_rejected": ("compiling", False, True, True, False, False),
        "cand_compiling_memory_only": ("compiling", False, True, True, False, False),
        "cand_compiling_same_family": ("compiling", False, True, True, False, False),
        "cand_compiling_unverified_descent": ("compiling", True, False, True, False, False),
        "cand_statused_obstruction": ("compiled", True, True, True, False, False),
    }

    for candidate, values in expected.items():
        row = rows[candidate]
        assert (
            row.status,
            row.lawful,
            row.descent,
            row.silent,
            row.decompilation_event,
            row.out_of_class_witness,
        ) == values
        assert sum((row.exposed, row.decompiled, row.compiled, row.mis_compiled, row.compiling)) == 1


def test_e4_promotion_mirror_matches_fiii_logic() -> None:
    accepted = PromotionBridgeData("accepted", True, _pass_gates())
    rejected = PromotionBridgeData("rejected", True, _rejected_gates())
    non_strict = PromotionBridgeData(
        "non_strict",
        True,
        _pass_gates(StrictGateStatus.non_strict_pass),
    )
    plain = PromotionBridgeData(
        "plain",
        True,
        _pass_gates(StrictGateStatus.not_required),
    )

    assert required_core_gates_pass_bool(accepted.gates) is True
    assert promotion_accepted_core_bool(accepted) is True
    assert promote(accepted) is PromotionStatus.strict
    assert accepted_promotion_family(promote(accepted)) is True

    assert required_core_gates_pass_bool(rejected.gates) is False
    assert promote(rejected) is PromotionStatus.candidate
    assert accepted_promotion_family(promote(rejected)) is False

    assert promote(non_strict) is PromotionStatus.non_strict
    assert accepted_promotion_family(promote(non_strict)) is True
    assert promote(plain) is PromotionStatus.accepted


def test_e4_blocked_channel_and_promotion_controls_isolate_condition_i() -> None:
    fixture = build_fixture()
    blocked = fixture.candidates["cand_compiling_blocked_channel"]
    rejected = fixture.candidates["cand_compiling_promotion_rejected"]

    assert top_down_channel_accepted_bool(fixture.channel_records[blocked.channel_record]) is False
    assert fixture.channel_records[blocked.channel_record].effect_gate is False
    assert compilation_lawful(fixture, blocked) is False
    assert compiled_descent(blocked) is True
    assert higher_package_goes_silent(fixture, fixture.window, blocked) is True

    promotion = fixture.promotion_data[rejected.promotion_data]
    assert promotion.admissible is True
    assert promotion.gates.ctrl is GateStatus.fail
    assert required_core_gates_pass_bool(promotion.gates) is False
    assert accepted_promotion_family(promote(promotion)) is False
    assert top_down_channel_accepted_bool(fixture.channel_records[rejected.channel_record]) is True
    assert compilation_lawful(fixture, rejected) is False


def test_e4_support_gate_p2_candidate_compiles() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["cand_compiled_support_gate"]

    assert candidate.move_sort is RepairSort.P2
    assert compilation_lawful(fixture, candidate) is True
    assert compiled_descent(candidate) is True
    assert higher_package_goes_silent(fixture, fixture.window, candidate) is True
    status, truths, _record = classify_compilation_status(fixture, candidate.name)
    assert status is CompilationStatus.compiled
    assert truths["compiled"] is True


def test_e4_memory_only_and_same_family_controls_isolate_conditions_ii_iii() -> None:
    fixture = build_fixture()
    memory_only = fixture.candidates["cand_compiling_memory_only"]
    same_family = fixture.candidates["cand_compiling_same_family"]

    assert memory_only.memory_only.survives_control is False
    assert top_down_channel_accepted_bool(fixture.channel_records[memory_only.channel_record]) is True
    assert accepted_promotion_family(promote(fixture.promotion_data[memory_only.promotion_data])) is True
    assert compilation_lawful(fixture, memory_only) is False

    assert same_family.memory_only.survives_control is True
    assert same_family_saturated(
        same_family.saturated_predicate,
        same_family.active_family,
        same_family.probe,
    ) is True
    assert same_family.probe == "probe_e4"
    assert compilation_lawful(fixture, same_family) is False

    ordinary = fixture.candidates["cand_compiled"]
    assert ordinary.saturated_predicate is same_family.saturated_predicate
    assert same_family_saturated(
        ordinary.saturated_predicate,
        ordinary.active_family,
        ordinary.probe,
    ) is False
    assert ordinary.probe not in ordinary.active_family.support


def test_e4_valid_windows_can_fail_scope_hypotheses_independently() -> None:
    fixture = build_fixture()

    no_reduction = build_window_no_obstruction_reduction()
    assert no_reduction.name == "window_no_obstruction_reduction"
    assert len(no_reduction.episode_times) >= 2
    assert all(
        invocation.audit_entry in fixture.audit_records
        for invocation in no_reduction.invocations.values()
    )
    assert obstruction_reducing_across_window(fixture, no_reduction) is False
    assert idempotence_stable_across_window(no_reduction, THRESHOLD) is True

    payload_drift = build_window_payload_drift()
    assert payload_drift.name == "window_payload_drift"
    assert len(payload_drift.episode_times) >= 2
    assert all(
        invocation.audit_entry in fixture.audit_records
        for invocation in payload_drift.invocations.values()
    )
    assert obstruction_reducing_across_window(fixture, payload_drift) is True
    assert idempotence_stable_across_window(payload_drift, THRESHOLD) is False


def test_e4_unverified_descent_is_not_derived_from_lawfulness() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["cand_compiling_unverified_descent"]

    assert compilation_lawful(fixture, candidate) is True
    assert compiled_descent(candidate) is False
    assert higher_package_goes_silent(fixture, fixture.window, candidate) is True
    status, truths, _record = classify_compilation_status(fixture, candidate.name)
    assert status is CompilationStatus.compiling
    assert truths["compiled"] is False
    assert truths["compiling"] is True


def test_e4_decompiled_priority_overrides_compiled_core() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["cand_decompiled"]

    assert compilation_lawful(fixture, candidate) is True
    assert compiled_descent(candidate) is True
    assert higher_package_goes_silent(fixture, fixture.window, candidate) is True
    assert decompilation_event_exists(fixture, candidate) is True
    status, truths, _record = classify_compilation_status(fixture, candidate.name)
    assert status is CompilationStatus.decompiled
    assert truths["decompiled"] is True
    assert truths["compiled"] is False


def test_e4_statused_obstruction_blocks_only_unstatused_witness() -> None:
    fixture = build_fixture()
    mis = fixture.candidates["cand_mis_compiled"]
    statused = fixture.candidates["cand_statused_obstruction"]

    assert mis.out_of_class_split_pair == statused.out_of_class_split_pair
    assert out_of_class_obstruction_witness(fixture, mis) is True
    assert carried_obstruction_status_for(fixture, statused, statused.out_of_class_split_pair) is True
    assert out_of_class_obstruction_witness(fixture, statused) is False
    assert classify_compilation_status(fixture, mis.name)[0] is CompilationStatus.mis_compiled
    assert classify_compilation_status(fixture, statused.name)[0] is CompilationStatus.compiled


def test_e4_brittleness_instance_uses_miscompiled_split_pair() -> None:
    fixture = build_fixture()
    candidate = fixture.candidates["cand_mis_compiled"]

    assert candidate.out_of_class_split_pair == ("x", "y")
    assert e4_brittleness_instance(fixture) is True


def test_e4_structural_controls_reject_at_construction_or_attribution() -> None:
    fixture = build_fixture()

    with pytest.raises(ConstructionRejected):
        build_window_too_short()
    with pytest.raises(ConstructionRejected):
        build_wrong_sort_candidate()
    assert fixture.candidates["cand_compiled"].move_sort is RepairSort.P1

    unattributed = fixture.candidates["cand_unattributed"]
    assert compiled_operator_record_attributed_to(fixture, fixture.window, unattributed) is False
    status, truths, _record = classify_compilation_status(fixture, unattributed.name)
    assert status is CompilationStatus.unclassified
    assert any(truths.values()) is False


def test_e4_scope_and_anti_hardcoding_guards_are_computed() -> None:
    results = run_e4_repair_compilation_sweep()
    fixture = build_fixture()

    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True
    for row in results.candidate_rows:
        assert row.carried_status_record in fixture.carried_status_records
        assert row.status != CompilationStatus.unclassified.value
