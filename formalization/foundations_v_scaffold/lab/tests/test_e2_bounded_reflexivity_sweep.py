from __future__ import annotations

from fractions import Fraction

from sixbirds_foundations_v.sweeps.e2_bounded_reflexivity_sweep import (
    CAPACITY,
    C_AB,
    C_BASE,
    C_CD,
    ClaimStatus,
    F,
    Q0,
    R_AB,
    R_CD,
    SameLevelSelfAuditClaim,
    audit_cost,
    capacity_admissible,
    capacity_saturated,
    challenge_process,
    classify_status,
    delta_count,
    joined_quotient,
    levels_for_depth,
    run_bounded_reflexivity_sweep,
    same_level_self_audit_classify,
    total_loss,
    tower_footprint,
)


def test_e2_sweep_confirms_all_registered_predictions() -> None:
    results = run_bounded_reflexivity_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 13


def test_e2_challenge_trigger_and_delta_fixture_match_registration() -> None:
    results = run_bounded_reflexivity_sweep()
    process = challenge_process()
    q1 = joined_quotient(Q0, R_AB)
    q2 = joined_quotient(q1, R_CD)

    assert [process.challenge_at(t, 0) for t in range(5)] == [
        C_BASE,
        C_BASE,
        C_AB,
        C_CD,
        C_CD,
    ]
    assert results.challenge_schedule == {
        0: "baseline",
        1: "baseline",
        2: "split_ab",
        3: "split_cd",
        4: "split_cd",
    }
    assert delta_count(Q0, C_AB) == 1
    assert delta_count(q1, C_AB) == 0
    assert delta_count(q1, C_CD) == 1
    assert delta_count(q2, C_CD) == 0
    assert results.delta_counts == {
        "Q0_C_ab": 1,
        "Q1_C_ab": 0,
        "Q1_C_cd": 1,
        "Q2_C_cd": 0,
    }
    assert results.trigger_checks == {2: True, 3: True}


def test_e2_self_audit_classifier_and_circular_status_are_computed() -> None:
    results = run_bounded_reflexivity_sweep()
    claim = SameLevelSelfAuditClaim(
        in_claim_types=True,
        self_dependent=True,
        has_level_shift_bridge=False,
    )

    assert same_level_self_audit_classify(claim) is ClaimStatus.undefinedCircular
    assert results.self_audit_status is ClaimStatus.undefinedCircular
    assert results.self_audit_accepted is False

    circular = results.controls["same_level_circularity"].observed
    assert circular["classifier_accepted"] is False
    assert circular["classifier_status"] == "undefinedCircular"
    assert circular["status"] == "circular_blocked"
    assert circular["active_scoped"] is False
    assert circular["rotating"] is False
    assert circular["saturated"] is False
    assert circular["circular_blocked"] is True


def test_e2_capacity_footprint_and_saturation_are_derived_from_record_sets() -> None:
    results = run_bounded_reflexivity_sweep()

    assert CAPACITY == 8
    assert [tower_footprint(levels_for_depth(depth)) for depth in range(5)] == [
        0,
        2,
        5,
        8,
        10,
    ]
    assert [capacity_admissible(levels_for_depth(depth)) for depth in range(5)] == [
        True,
        True,
        True,
        True,
        False,
    ]
    assert tuple(
        (row.depth, row.current_footprint, row.next_footprint, row.saturated)
        for row in results.saturation_rows
    ) == ((1, 2, 5, False), (2, 5, 8, False), (3, 8, 10, True))
    assert capacity_saturated(levels_for_depth(1)) is False
    assert capacity_saturated(levels_for_depth(2)) is False
    assert capacity_saturated(levels_for_depth(3)) is True


def test_e2_rotation_sequence_and_fresh_level_bridge_match_registration() -> None:
    results = run_bounded_reflexivity_sweep()

    observed = tuple(
        (
            row.name,
            row.trigger_present,
            row.starting_depth,
            row.saturated,
            row.status,
            row.next_depth,
            row.extension.self_soundness_accepted if row.extension else None,
            None
            if row.next_level is None
            else (
                row.next_level.level_index,
                row.next_level.level_tag,
                row.next_level.lower_stack_target,
            ),
        )
        for row in results.rotation_rows
    )
    assert observed == (
        ("no-trigger control", False, 1, False, "active_scoped", 1, None, None),
        ("triggered step 1", True, 1, False, "rotating", 2, False, (1, 20, (0,))),
        ("triggered step 2", True, 2, False, "rotating", 3, False, (2, 30, (0, 1))),
        ("saturated trigger", True, 3, True, "saturated", 3, None, None),
    )


def test_e2_per_level_status_partition_rows_are_exactly_one() -> None:
    results = run_bounded_reflexivity_sweep()

    observed = tuple(
        (
            row.config,
            row.depth,
            row.target_level,
            row.trigger_present,
            row.circular_claim,
            row.footprint,
            row.saturated,
            row.status,
            row.active_scoped,
            row.rotating,
            row.saturated_holds,
            row.circular_blocked,
        )
        for row in results.status_rows
    )
    assert observed == (
        ("active_base", 1, 0, False, False, 2, False, "active_scoped", True, False, False, False),
        ("rotate_1_to_2", 1, 0, True, False, 2, False, "rotating", False, True, False, False),
        ("rotate_2_to_3", 2, 1, True, False, 5, False, "rotating", False, True, False, False),
        ("saturated_3", 3, 2, True, False, 8, True, "saturated", False, False, True, False),
        ("circular_0", 1, 0, False, True, 2, False, "circular_blocked", False, False, False, True),
    )
    assert all(
        sum(
            (
                row.active_scoped,
                row.rotating,
                row.saturated_holds,
                row.circular_blocked,
            )
        )
        == 1
        for row in results.status_rows
    )

    status, truths = classify_status(
        levels=levels_for_depth(3),
        target_level=2,
        trigger_present=True,
        claim=None,
    )
    assert status.value == "saturated"
    assert truths == {
        "active_scoped": False,
        "rotating": False,
        "saturated": True,
        "circular_blocked": False,
    }


def test_e2_diminishing_returns_optimum_is_computed_by_argmin() -> None:
    results = run_bounded_reflexivity_sweep()

    assert [audit_cost(depth) for depth in range(4)] == [
        Fraction(0),
        Fraction(1, 12),
        Fraction(5, 24),
        Fraction(1, 3),
    ]
    assert [total_loss(depth) for depth in range(4)] == [
        Fraction(18, 24),
        Fraction(14, 24),
        Fraction(13, 24),
        Fraction(14, 24),
    ]
    assert tuple((row.depth, row.total_loss) for row in results.loss_rows) == (
        (0, F(18, 24)),
        (1, F(14, 24)),
        (2, F(13, 24)),
        (3, F(14, 24)),
    )
    assert results.optimum_depth == 2


def test_e2_controls_match_registered_nulls() -> None:
    results = run_bounded_reflexivity_sweep()

    capacity = results.controls["capacity_null"].observed
    assert capacity["tower_footprint"] == 10
    assert capacity["capacity_admissible"] is False
    assert capacity["capacity_saturated_depth_3"] is True
    assert capacity["capacity_bound_certified_depths"] is True
    assert capacity["over_capacity_attempted_admissible"] is False

    unlinked = results.controls["unlinked_bridge"].observed
    assert unlinked["fiii_extension_exists"] is True
    assert unlinked["carried_rotating_extension_realized"] is False
    assert unlinked["bad_next_level_index"] == 2
    assert unlinked["expected_next_index"] == 1

    incomplete = results.controls["incomplete_inventory"].observed
    assert incomplete["carried_level_1_exists"] is True
    assert incomplete["tower_slot_1_present"] is False
    assert incomplete["complete_carried_instrument_tower"] is False
    assert incomplete["complete_status_claim_accepted"] is False

    assert results.actual_tower_discipline is True
