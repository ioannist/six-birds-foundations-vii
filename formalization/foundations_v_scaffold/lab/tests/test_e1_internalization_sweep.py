from __future__ import annotations

from fractions import Fraction

from sixbirds_foundations_v.carried_records import FineSourceTag
from sixbirds_foundations_v.sweeps.e1_internalization_sweep import (
    C_BASE,
    C_SPLIT,
    F,
    Q0,
    R_SAME,
    R_SPLIT,
    RepairAuditEntry,
    binding_by_horizon,
    challenge_process,
    classify_status,
    delta_endo_empty,
    delta_count,
    joined_quotient,
    residual_level,
    run_internalization_sweep,
    strict_challenge_descent,
    viability_descends,
)


def test_e1_internalization_sweep_confirms_all_registered_predictions() -> None:
    results = run_internalization_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []


def test_e1_challenge_switch_and_delta_counts_match_registration() -> None:
    results = run_internalization_sweep()
    process = challenge_process()

    assert [process.challenge_at(t, 0) for t in range(5)] == [
        C_BASE,
        C_BASE,
        C_SPLIT,
        C_SPLIT,
        C_SPLIT,
    ]
    assert results.challenge_schedule == {
        0: "baseline",
        1: "baseline",
        2: "split_ab",
        3: "split_ab",
        4: "split_ab",
    }

    q1 = joined_quotient(Q0, R_SPLIT)
    assert results.q1 == q1
    assert results.enabled_step_q == q1
    assert delta_count(Q0, C_SPLIT) == 1
    assert delta_count(q1, C_SPLIT) == 0
    assert delta_count(Q0, C_BASE) == 0
    assert results.delta_q0_split == 1
    assert results.delta_q1_split == 0
    assert results.delta_q0_base == 0


def test_e1_enabled_and_ablated_generator_reachability_match_registration() -> None:
    results = run_internalization_sweep()

    assert results.enabled_repair_lawful is True
    assert results.ablated_repair_lawful is False
    assert results.generator_reachability_discipline is True
    assert results.no_reachable_repair_generator_ablated is True
    assert results.endogenous_family_valid_enabled is True
    assert results.endogenous_family_valid_ablated is False
    assert results.enabled_challenged_times == frozenset({2})
    assert results.ablated_challenged_times == frozenset({2, 3, 4})


def test_e1_status_table_matches_registered_five_way_partition() -> None:
    results = run_internalization_sweep()

    observed = tuple(
        (
            row.horizon,
            row.active_challenge,
            row.binding,
            row.enabled_status,
            row.enabled_residual,
            row.enabled_cumulative_spend,
            row.ablated_status,
            row.ablated_residual,
        )
        for row in results.status_rows
    )
    assert observed == (
        (0, "baseline", False, "slack", Fraction(0), Fraction(0), "slack", Fraction(0)),
        (1, "baseline", False, "slack", Fraction(0), Fraction(0), "slack", Fraction(0)),
        (
            2,
            "split_ab",
            True,
            "endogenously_repairing",
            Fraction(0),
            Fraction(2),
            "stressed",
            Fraction(1),
        ),
        (
            3,
            "split_ab",
            True,
            "endogenously_repairing",
            Fraction(0),
            Fraction(2),
            "stressed",
            Fraction(2),
        ),
        (
            4,
            "split_ab",
            True,
            "endogenously_repairing",
            Fraction(0),
            Fraction(2),
            "collapsing",
            Fraction(3),
        ),
    )
    assert {
        row.horizon for row in results.status_rows if row.ablated_status in {"stressed", "collapsing"}
    } == {2, 3, 4}
    assert {row.horizon for row in results.status_rows if row.binding} == {2, 3, 4}


def test_e1_status_classifier_derives_from_primitives() -> None:
    q_history = {time: Q0 for time in range(5)}
    assert binding_by_horizon(q_history, 1) is False
    assert binding_by_horizon(q_history, 2) is True

    no_entries: dict[int, tuple[RepairAuditEntry, ...]] = {}
    assert residual_level(q_history, no_entries, 4) == F(3)
    assert viability_descends(F(2)) is True
    assert viability_descends(F(3)) is False
    assert (
        classify_status(
            binding=binding_by_horizon(q_history, 4),
            delta_empty=True,
            has_reachable_generator=False,
            family_valid=False,
            measured_discharge=False,
            residual=F(3),
            descends=viability_descends(F(3)),
        )
        == "collapsing"
    )
    assert (
        classify_status(
            binding=True,
            delta_empty=False,
            has_reachable_generator=False,
            family_valid=False,
            measured_discharge=True,
            residual=F(3),
            descends=viability_descends(F(3)),
        )
        == "collapsing"
    )
    assert (
        classify_status(
            binding=True,
            delta_empty=True,
            has_reachable_generator=False,
            family_valid=False,
            measured_discharge=False,
            residual=F(0),
            descends=viability_descends(F(0)),
        )
        == "unclassified"
    )
    assert (
        classify_status(
            binding=True,
            delta_empty=False,
            has_reachable_generator=False,
            family_valid=False,
            measured_discharge=False,
            residual=F(1),
            descends=viability_descends(F(1)),
        )
        == "unclassified"
    )

    fallback_entry = RepairAuditEntry(
        name="fallback-rho",
        source_tag=FineSourceTag.fallback,
        generated_by_s=False,
        in_scope=True,
        carried=False,
        kernel_realized=True,
        in_repair_audit_entries=True,
        discharges=True,
        refinement="R_split",
        cost=F(2),
    )
    assert delta_endo_empty((fallback_entry,)) is False
    assert (
        classify_status(
            binding=True,
            delta_empty=delta_endo_empty((fallback_entry,)),
            has_reachable_generator=False,
            family_valid=False,
            measured_discharge=True,
            residual=F(1),
            descends=viability_descends(F(1)),
        )
        == "externally_subsidized"
    )

    assert (
        classify_status(
            binding=True,
            delta_empty=True,
            has_reachable_generator=True,
            family_valid=True,
            measured_discharge=True,
            residual=F(0),
            descends=viability_descends(F(0)),
        )
        == "endogenously_repairing"
    )


def test_e1_delta_discharge_budget_and_source_census_match_registration() -> None:
    results = run_internalization_sweep()

    assert tuple(
        (row.time, row.variant, row.pre_delta, row.post_delta, row.discharge)
        for row in results.delta_rows
    ) == (
        (2, "enabled", 1, 0, 1),
        (2, "ablated", 1, 1, 0),
        (3, "ablated", 1, 1, 0),
        (4, "ablated", 1, 1, 0),
    )
    assert results.enabled_total_discharge == 1
    assert results.ablated_total_discharge == 0

    assert tuple(
        (row.time, row.repair, row.cost, row.cumulative_spend, row.budget_feasible)
        for row in results.budget_rows
    ) == (
        (0, "none", Fraction(0), Fraction(0), True),
        (1, "none", Fraction(0), Fraction(0), True),
        (2, "rho_2", Fraction(2), Fraction(2), True),
        (3, "none", Fraction(0), Fraction(2), True),
        (4, "none", Fraction(0), Fraction(2), True),
    )
    assert results.total_spend_enabled == Fraction(2)
    assert results.remaining_budget_enabled == Fraction(1)
    assert results.family_budget_feasible is True

    enabled = results.enabled_census
    assert enabled.installed_refinements == 1
    assert enabled.committed_state == 1
    assert enabled.generated_by_s_true == 1
    assert enabled.in_scope_true == 1
    assert enabled.carried == 1
    assert enabled.kernel_realized == 1
    assert enabled.in_repair_audit_entries == 1
    assert enabled.delta_endo_entries == 0
    assert enabled.fallback == 0
    assert enabled.unknown == 0
    assert enabled.contradictory == 0
    assert enabled.independent_pair_witness == 0
    assert enabled.simulation_trace == 0
    assert enabled.ablation_record == 0
    assert enabled.generated_by_s_false == 0
    assert enabled.in_scope_false == 0
    assert enabled.not_carried == 0
    assert enabled.off_kernel == 0
    assert enabled.audit_omitted == 0

    ablated = results.ablated_census
    assert ablated.installed_refinements == 0
    assert ablated.committed_state == 0
    assert ablated.delta_endo_entries == 0


def test_e1_controls_match_registered_non_endogenous_classifications() -> None:
    results = run_internalization_sweep()

    external = results.controls["external_subsidy"]
    assert (
        external.pre_delta,
        external.post_delta,
        external.discharge,
        external.delta_endo_count,
        external.endogenously_repairing_holds,
        external.status,
        external.strict_self_extension,
        external.no_schedule_trap,
        external.in_repair_audit_entries,
    ) == (1, 0, 1, 1, False, "externally_subsidized", True, True, True)

    same_family = results.controls["same_family"]
    assert joined_quotient(Q0, R_SAME) == results.q_same
    assert strict_challenge_descent(Q0, results.q_same) is False
    assert (
        same_family.pre_delta,
        same_family.post_delta,
        same_family.discharge,
        same_family.strict_challenge_descent,
        same_family.strict_self_extension,
        same_family.no_schedule_trap,
        same_family.in_repair_audit_entries,
        same_family.endogenously_repairing_holds,
        same_family.status,
    ) == (1, 1, 0, False, False, True, True, False, "stressed")

    schedule = results.controls["schedule_trap"]
    assert (
        schedule.pre_delta,
        schedule.post_delta,
        schedule.discharge,
        schedule.strict_self_extension,
        schedule.no_schedule_trap,
        schedule.in_repair_audit_entries,
        schedule.delta_endo_count,
        schedule.endogenously_repairing_holds,
        schedule.status,
    ) == (1, 0, 1, True, False, False, 1, False, "externally_subsidized")

    omission = results.controls["audit_omission"]
    assert (
        omission.discharge,
        omission.strict_self_extension,
        omission.no_schedule_trap,
        omission.in_repair_audit_entries,
        omission.delta_endo_count,
        omission.endogenously_repairing_holds,
        omission.status,
    ) == (1, True, True, False, 1, False, "externally_subsidized")


def test_e1_delta_endo_bad_source_tags_are_the_registered_python_tags() -> None:
    bad_tags = {
        FineSourceTag.fallback,
        FineSourceTag.unknown,
        FineSourceTag.contradictory,
        FineSourceTag.independent_pair_witness,
        FineSourceTag.simulation_trace,
        FineSourceTag.ablation_record,
    }
    good_tags = {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}

    assert bad_tags.isdisjoint(good_tags)
