from __future__ import annotations

from dataclasses import replace

from sixbirds_foundations_v.sweeps.e12_individuation_sweep import (
    N_STATES,
    REGISTERED_CANDIDATES,
    FineSourceTag,
    IndividuationStatusRecord,
    IndividuationStatus,
    Subcarrier,
    attributed_to_i,
    build_fixture,
    budget_closed_on,
    candidate_member,
    coarsest_quotient_certified,
    has_viability_sufficient_boundary,
    individuates,
    individuation_status_occurrence_for,
    maximal_individuating,
    record_closed_on,
    repair_closed_on,
    run_e12_individuation_sweep,
    self_maintained_boundary,
    sufficiency_closure_certified,
    viability_sufficient_boundary,
)


def test_e12_sweep_confirms_all_registered_predictions() -> None:
    results = run_e12_individuation_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []
    assert len(results.comparisons) == 19


def test_e12_ring_fixture_and_candidate_inventory_match_preregistration() -> None:
    fixture = build_fixture()

    assert fixture.config.kernel.n_states == N_STATES
    assert N_STATES == 30
    assert fixture.config.e_system.T.supp_k(29, 0) is True
    assert fixture.config.e_system.T.supp_k(29, 29) is False
    assert tuple(REGISTERED_CANDIDATES) == tuple(row.candidate for row in run_e12_individuation_sweep().candidate_rows)
    assert fixture.candidates["cand_integrated"].states == frozenset({0, 1, 2})
    assert fixture.candidates["cand_coalition"].states == frozenset({9, 10})
    assert fixture.candidates["cand_unlinked_control"].states == frozenset({19})
    assert fixture.candidates["cand_bound_control"].states == frozenset({24, 25})
    assert fixture.candidates["cand_max_sub"].states == frozenset({26, 27})
    assert fixture.candidates["cand_max_sup"].states == frozenset({26, 27, 28})
    assert all(16 not in candidate.states for candidate in fixture.candidates.values())


def test_e12_candidate_closure_and_status_rows_are_computed() -> None:
    rows = {row.candidate: row for row in run_e12_individuation_sweep().candidate_rows}
    expected = {
        "cand_integrated": (True, True, True, True, True, "integrated"),
        "cand_subsidiary": (True, False, True, True, True, "subsidiary"),
        "cand_platform_dependent": (True, True, True, True, False, "platform_dependent"),
        "cand_shadow": (True, True, False, True, True, "shadow"),
        "cand_fed_a": (False, False, False, False, False, "federated"),
        "cand_fed_b": (False, False, False, False, False, "federated"),
        "cand_coalition": (True, True, True, True, True, "integrated"),
        "cand_overlap_x": (True, True, True, True, True, "federated"),
        "cand_overlap_y": (True, True, True, True, True, "federated"),
        "cand_non_individuated": (False, False, False, False, False, "non_individuated"),
        "cand_vacuous_attempt": (False, False, False, False, False, "non_individuated"),
        "cand_coarsest_control": (True, True, True, True, True, "integrated"),
        "cand_bound_control": (True, True, True, False, True, "non_individuated"),
        "cand_max_sub": (True, True, True, True, True, "non_individuated"),
        "cand_max_sup": (True, True, True, True, True, "integrated"),
    }

    for candidate, values in expected.items():
        row = rows[candidate]
        assert (
            row.repair_closed,
            row.budget_closed,
            row.record_closed,
            row.viability_sufficient_boundary,
            row.self_maintained_boundary,
            row.status,
        ) == values
        assert sum(
            (
                row.integrated,
                row.federated,
                row.subsidiary,
                row.platform_dependent,
                row.shadow,
                row.non_individuated,
            )
        ) == 1


def test_e12_federated_disjuncts_are_distinguished() -> None:
    fixture = build_fixture()
    rows = {row.candidate: row for row in run_e12_individuation_sweep().candidate_rows}

    assert individuates(fixture, "cand_fed_a") is False
    assert individuates(fixture, "cand_fed_b") is False
    assert maximal_individuating(fixture, "cand_coalition") is True
    assert rows["cand_fed_a"].federated_disjunct == "coalition"
    assert rows["cand_fed_b"].federated_disjunct == "coalition"

    assert maximal_individuating(fixture, "cand_overlap_x") is True
    assert maximal_individuating(fixture, "cand_overlap_y") is True
    assert rows["cand_overlap_x"].federated_disjunct == "overlap"
    assert rows["cand_overlap_y"].federated_disjunct == "overlap"


def test_e12_non_vacuity_control_fails_all_empty_closures() -> None:
    fixture = build_fixture()
    results = run_e12_individuation_sweep()

    control = results.non_vacuity_control
    assert control == {
        "has_repair_witness": False,
        "has_budget_witness": False,
        "has_record_witness": False,
        "repair_closed": False,
        "budget_closed": False,
        "record_closed": False,
    }
    assert repair_closed_on(fixture, "cand_vacuous_attempt") is False
    assert budget_closed_on(fixture, "cand_vacuous_attempt") is False
    assert record_closed_on(fixture, "cand_vacuous_attempt") is False


def test_e12_arbitrary_fragment_is_not_a_declared_candidate() -> None:
    fixture = build_fixture()
    control = run_e12_individuation_sweep().arbitrary_fragment_control

    assert control["fragment"] == "{0}"
    assert control["is_declared_candidate"] is False
    assert control["registered_status"] is False
    assert control["candidate_loop_skips"] is True
    assert frozenset({0}) not in {
        fixture.candidates[name].states for name in fixture.candidate_order
    }


def test_e12_status_occurrence_rejects_carried_undeclared_fragment() -> None:
    fixture = build_fixture()
    fragment_name = "undeclared_fragment_0"
    status_record = IndividuationStatusRecord(
        name="status:undeclared_fragment_0",
        candidate_name=fragment_name,
        status=IndividuationStatus.non_individuated,
        supporting_ledger_entries=("ledger:status:undeclared_fragment_0",),
        supporting_audit_records=("audit:status:undeclared_fragment_0",),
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )
    fixture_with_forged_status = replace(
        fixture,
        candidates={
            **fixture.candidates,
            fragment_name: Subcarrier(fragment_name, frozenset({0})),
        },
        status_records={**fixture.status_records, fragment_name: status_record},
        carried_status_records=fixture.carried_status_records | frozenset({status_record.name}),
        ledger_entries=fixture.ledger_entries | frozenset(status_record.supporting_ledger_entries),
        audit_records=fixture.audit_records | frozenset(status_record.supporting_audit_records),
    )

    assert fragment_name in fixture_with_forged_status.candidates
    assert fragment_name not in fixture_with_forged_status.candidate_order
    assert status_record.name in fixture_with_forged_status.carried_status_records
    assert all(
        entry in fixture_with_forged_status.ledger_entries
        for entry in status_record.supporting_ledger_entries
    )
    assert all(
        audit in fixture_with_forged_status.audit_records
        for audit in status_record.supporting_audit_records
    )
    assert status_record.candidate_name == fragment_name
    assert status_record.source_tag is FineSourceTag.committed_state
    assert status_record.generated_by_s is True
    assert status_record.in_scope is True
    assert candidate_member(fixture_with_forged_status, fragment_name) is False
    assert (
        individuation_status_occurrence_for(fixture_with_forged_status, fragment_name)
        is False
    )


def test_e12_coarsest_quotient_direction_uses_q_factors_through_pi() -> None:
    fixture = build_fixture()
    controls = {row.name: row for row in run_e12_individuation_sweep().quotient_controls}
    boundaries = {
        boundary.variant: boundary
        for boundary in fixture.activities["cand_coarsest_control"].boundaries
    }
    two = boundaries["two_class"]
    three = boundaries["three_class"]

    assert sufficiency_closure_certified(fixture, two) is True
    assert sufficiency_closure_certified(fixture, three) is True
    assert coarsest_quotient_certified(fixture, "cand_coarsest_control", two) is True
    assert coarsest_quotient_certified(fixture, "cand_coarsest_control", three) is False
    assert viability_sufficient_boundary(fixture, "cand_coarsest_control", two) is True
    assert viability_sufficient_boundary(fixture, "cand_coarsest_control", three) is False
    assert has_viability_sufficient_boundary(fixture, "cand_coarsest_control") is True
    assert controls["two_class"].coarsest is True
    assert controls["three_class"].coarsest is False


def test_e12_unlinked_tau_n0_control_ignores_decoy_rhoof_witness() -> None:
    fixture = build_fixture()
    controls = {row.name: row for row in run_e12_individuation_sweep().unlinked_controls}
    witnesses = {
        witness.name: witness
        for witness in fixture.activities["cand_unlinked_control"].budget_witnesses
    }

    inside = controls["cand_unlinked_control:inside_tau"]
    outside = controls["cand_unlinked_control:outside_tau"]
    assert inside.tau_state == 19
    assert inside.decoy_state == 20
    assert inside.same_rho_of is True
    assert inside.attributed_to_i is True
    assert attributed_to_i(
        fixture,
        "cand_unlinked_control",
        witnesses["cand_unlinked_control:inside_tau"],
    ) is True

    assert outside.tau_state == 20
    assert outside.decoy_state == 19
    assert outside.same_rho_of is True
    assert outside.attributed_to_i is False
    assert attributed_to_i(
        fixture,
        "cand_unlinked_control",
        witnesses["cand_unlinked_control:outside_tau"],
    ) is False


def test_e12_platform_dependency_fails_only_self_maintenance_attribution() -> None:
    fixture = build_fixture()
    maintenance = fixture.activities["cand_platform_dependent"].maintenance
    assert maintenance is not None
    assert maintenance.record.source_state == 23
    assert 23 not in fixture.candidates["cand_platform_dependent"].states
    assert repair_closed_on(fixture, "cand_platform_dependent") is True
    assert budget_closed_on(fixture, "cand_platform_dependent") is True
    assert record_closed_on(fixture, "cand_platform_dependent") is True
    assert has_viability_sufficient_boundary(fixture, "cand_platform_dependent") is True
    assert self_maintained_boundary(fixture, "cand_platform_dependent") is False


def test_e12_bound_control_isolated_delta_bound_failure() -> None:
    fixture = build_fixture()
    rows = {row.candidate: row for row in run_e12_individuation_sweep().candidate_rows}
    activity = fixture.activities["cand_bound_control"]
    assert len(activity.boundaries) == 1
    quotient = activity.boundaries[0]

    assert repair_closed_on(fixture, "cand_bound_control") is True
    assert budget_closed_on(fixture, "cand_bound_control") is True
    assert record_closed_on(fixture, "cand_bound_control") is True
    assert self_maintained_boundary(fixture, "cand_bound_control") is True
    assert quotient.classify(24, fixture.candidates["cand_bound_control"]) == quotient.classify(
        25, fixture.candidates["cand_bound_control"]
    )
    assert sufficiency_closure_certified(fixture, quotient) is False
    assert has_viability_sufficient_boundary(fixture, "cand_bound_control") is False
    assert rows["cand_bound_control"].status == "non_individuated"
    assert rows["cand_bound_control"].non_individuated is True


def test_e12_maximality_control_isolated_delta_max_failure() -> None:
    fixture = build_fixture()
    rows = {row.candidate: row for row in run_e12_individuation_sweep().candidate_rows}

    assert fixture.candidates["cand_max_sub"].states < fixture.candidates["cand_max_sup"].states
    assert repair_closed_on(fixture, "cand_max_sub") is True
    assert budget_closed_on(fixture, "cand_max_sub") is True
    assert record_closed_on(fixture, "cand_max_sub") is True
    assert has_viability_sufficient_boundary(fixture, "cand_max_sub") is True
    assert self_maintained_boundary(fixture, "cand_max_sub") is True
    assert individuates(fixture, "cand_max_sub") is True
    assert individuates(fixture, "cand_max_sup") is True
    assert maximal_individuating(fixture, "cand_max_sub") is False
    assert maximal_individuating(fixture, "cand_max_sup") is True
    assert rows["cand_max_sub"].status == "non_individuated"
    assert rows["cand_max_sub"].non_individuated is True
    assert rows["cand_max_sup"].status == "integrated"
    assert rows["cand_max_sup"].integrated is True


def test_e12_scope_and_anti_hardcoding_guards_are_computed() -> None:
    results = run_e12_individuation_sweep()
    fixture = build_fixture()

    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True
    for row in results.candidate_rows:
        assert row.candidate in REGISTERED_CANDIDATES
        assert row.carried_status_record in fixture.carried_status_records
        assert row.status != IndividuationStatus.unclassified.value
