from __future__ import annotations

from dataclasses import replace
from fractions import Fraction

import pytest

import sixbirds_foundations_v.sweeps.e15_offline_reclosure_sweep as e15


F = Fraction

REGISTERED_STATUS_EXPECTATIONS = (
    ("claim_alternation_required", e15.OfflineReclosureStatus.alternation_required),
    ("claim_online_sufficient", e15.OfflineReclosureStatus.online_sufficient),
    ("claim_offline_optional", e15.OfflineReclosureStatus.offline_optional),
    (
        "claim_deficit_online_counterexample",
        e15.OfflineReclosureStatus.deficit_online_counterexample,
    ),
    ("claim_decorative_exchange_active", e15.OfflineReclosureStatus.decorative_offline),
    ("claim_decorative_no_discharge", e15.OfflineReclosureStatus.decorative_offline),
    ("claim_decorative_bad_reallocation", e15.OfflineReclosureStatus.decorative_offline),
    ("claim_duty_cycle_mismatch", e15.OfflineReclosureStatus.duty_cycle_mismatch),
    ("claim_skipped_offline_cascade", e15.OfflineReclosureStatus.skipped_offline_cascade),
    (
        "claim_zero_exchange_without_p2",
        e15.OfflineReclosureStatus.offline_reclosure_rejected,
    ),
    (
        "ctrl_offline_overcapacity_is_decorative",
        e15.OfflineReclosureStatus.decorative_offline,
    ),
)

REGISTERED_CONTROL_NAMES = tuple(
    name
    for name in e15.REGISTERED_COMPARISON_ORDER
    if not name.endswith(".status")
)

REGISTERED_EXPECTED = (
    "alternation_required; observed_duty=1/4; predicted_duty=1/4",
    "online_sufficient; alternation=False",
    "offline_optional",
    "deficit_online_counterexample; lower_holds=False",
    "decorative_offline; exchange=1",
    "decorative_offline; discharged=0",
    "decorative_offline; exact_allocation=False",
    "duty_cycle_mismatch; observed_duty=1/3; predicted_duty=1/4; error=1/12>1/24",
    "skipped_offline_cascade",
    "offline_reclosure_rejected; census=0; gate=False",
    "total=20; source omissions=[false,false,false]",
    "lookalike credited=0; E14 item=false",
    "F3 item=false",
    "Xi item=false; declaration=false; amount link=false",
    "Xi record/item=false",
    "ledgerChargesNodup=false",
    "geometry=false; positive branch=false",
    "6=4+2; fitted 11/2=false; fitted 13/2=false",
    "accrual=5; discharge=3; net=2",
    "7/2=online_sufficient; 4=online_sufficient; 5=alternation_required",
    "everyPhaseCovered=false; status=offline_reclosure_rejected",
    "online duration checks=[false,true]; alternation=false; status=offline_reclosure_rejected",
    "prediction=false; mismatch=false",
    "shared scope=true; online=online_sufficient; mismatch=duty_cycle_mismatch; cross matches=[false,false]",
    "counterexample raw=true; alternation case=false; statusUnique with both=false; canonical=deficit_online_counterexample",
    "cascade evidence=false",
    "cascade evidence=false",
    "five cascade mutations=[false,false,false,false,false]",
    "E5 suspension=true; E15 genuine offline=false",
    "decorative_offline; offline_optional=False",
    "completeForSchedule=false",
    "recordsNodup=false",
    "recordIdsNodup=false",
    "eligibility=[false,false,false,false]; soundness=false; phase coverage=false",
    "nine predicates=true; Xi equality=true; ten mutations=false",
    "seven representative vectors=[false,false,false]",
    "geometry=false",
    "six P2 mutations=false; exchange=0",
    "five claim matches=false",
    "duplicate-safety vector=[false,false,false,false]",
    "persistent/bounded/sufficient=[false,false,false]; rates=[5,5,5]; other fields=[true,true,true]",
    "alarm/stress/chronology=4/4/4; collapse comparison absent",
    "ten claims exactly one; counterexample lower holds=false",
    "E14 debt item false; credited E14 amount 0",
    "genuine offline false; decorative offline false",
    "everyDischargeLinked = false; CompleteClosureDebtFlow = false",
)


@pytest.fixture(scope="module")
def fixture() -> e15.Fixture:
    return e15.build_fixture()


@pytest.fixture(scope="module")
def results() -> e15.SweepResults:
    return e15.run_e15_offline_reclosure_sweep()


def test_e15_sweep_confirms_all_registered_predictions(
    results: e15.SweepResults,
) -> None:
    assert len(results.comparisons) == 46
    assert tuple(row.name for row in results.comparisons) == e15.REGISTERED_COMPARISON_ORDER
    assert tuple(row.expected for row in results.comparisons) == REGISTERED_EXPECTED
    assert [row.name for row in results.comparisons if not row.passed] == []
    assert results.actual_scope_discipline is True
    assert results.no_hardcoded_status_discipline is True


@pytest.mark.parametrize(("claim_name", "expected"), REGISTERED_STATUS_EXPECTATIONS)
def test_e15_registered_status_comparisons(
    fixture: e15.Fixture,
    claim_name: str,
    expected: e15.OfflineReclosureStatus,
) -> None:
    observed, truths, record = e15.classify_offline_reclosure_status(fixture, claim_name)

    assert observed is expected
    assert record is not None
    assert record.status is expected
    assert sum(truths.values()) == 1
    assert truths[expected] is True
    assert e15.complete_offline_reclosure_status(fixture, claim_name) is True


@pytest.mark.parametrize("control_name", REGISTERED_CONTROL_NAMES)
def test_e15_registered_nonstatus_comparisons(
    results: e15.SweepResults, control_name: str
) -> None:
    control = results.controls[control_name]
    comparison = next(row for row in results.comparisons if row.name == control_name)

    assert control.passed_control is True
    assert comparison.passed is True


@pytest.mark.parametrize(
    ("duration", "rate", "amounts"),
    (
        (F(3), F(6), (F(6), F(6), F(6))),
        (F(2), F(6), (F(4), F(4), F(4))),
        (F(6), F(5), (F(12), F(12), F(6))),
        (F(3), F(3), (F(3), F(3), F(3))),
        (F(3), F(7, 2), (F(7, 2), F(7, 2), F(7, 2))),
        (F(3), F(4), (F(4), F(4), F(4))),
        (F(1), F(5), (F(2), F(2), F(1))),
        (F(4), F(6), (F(10), F(8), F(6))),
        (F(2), F(3), (F(2), F(2), F(2))),
    ),
)
def test_e15_accrual_profiles_are_exact(
    duration: Fraction, rate: Fraction, amounts: tuple[Fraction, Fraction, Fraction]
) -> None:
    observed = e15._accrual_amounts(duration, rate)

    assert observed == amounts
    assert sum(observed, F(0)) == duration * rate


def test_e15_recurrence_uses_phase_ordinal_and_online_duration(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["ctrl_recurrence_uses_online_duration"]
    second_online = data.flows[2]

    assert second_online.phase_record.phase_id == 1220013
    assert {entry.key[1] for entry in second_online.accrued_entries} == {
        34000302,
        34000311,
        34000321,
    }
    assert [snapshot.total_debt for snapshot in e15._all_snapshots(data)] == [
        26,
        34,
        28,
        32,
        26,
    ]
    assert e15.alternating_offline_substrate(fixture, data) is False
    assert e15.phase_duration(data.schedule.phases[0]) == 4
    assert data.recurrence_bound.maximum_online_run == 3


def test_e15_every_discharge_is_a_whole_before_snapshot_entry(
    fixture: e15.Fixture,
) -> None:
    for data in fixture.claims.values():
        for flow in data.flows:
            assert e15.complete_closure_debt_flow(fixture, flow) is True
            for discharge in flow.discharge_records:
                assert discharge.debt_entry in flow.before_snapshot.entries
                assert discharge.amount == discharge.debt_entry.amount
                assert discharge.debt_entry not in flow.after_snapshot.entries


def test_e15_debt_uses_actual_e14_and_literal_xi_interfaces(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_alternation_required"]
    snapshot = data.flows[0].before_snapshot
    e14_entry = e15._entry_by_kind(
        snapshot.entries, e15.ClosureDebtComponentKind.e14_reconsolidation
    )
    xi_entry = e15._entry_by_kind(
        snapshot.entries, e15.ClosureDebtComponentKind.xi_adequacy_residual
    )

    assert isinstance(e14_entry.source, e15.E14ResidualDebtSource)
    assert e15.actual_e14_statused_unresolved(fixture, e14_entry.source) is True
    assert isinstance(xi_entry.source, e15.XiAdequacyResidualDebtRecord)
    assert xi_entry.source.residual_matrix == e15.adequacyResidual(
        xi_entry.source.C,
        xi_entry.source.L,
        xi_entry.source.D,
        xi_entry.source.KLLdagger,
    )
    assert e15.closure_debt(snapshot.entries) == 20


def test_e15_e14_debt_rejects_unregistered_formation_and_transport(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_alternation_required"]
    snapshot = data.flows[0].before_snapshot
    entry = e15._entry_by_kind(
        snapshot.entries, e15.ClosureDebtComponentKind.e14_reconsolidation
    )
    assert isinstance(entry.source, e15.E14ResidualDebtSource)

    unregistered_formation = replace(
        entry.source.candidate.formation_record,
        formation_id=entry.source.candidate.formation_record.formation_id + 9000000,
    )
    bad_source = replace(
        entry.source,
        candidate=replace(
            entry.source.candidate, formation_record=unregistered_formation
        ),
    )
    bad_entry = replace(entry, source=bad_source)
    no_transport_registry = replace(fixture, e14_transport_registry={})

    assert e15.e14_residual_debt_item(
        fixture, data.scope, snapshot.observed_at, bad_entry
    ) is False
    assert e15.e14_residual_debt_item(
        no_transport_registry, data.scope, snapshot.observed_at, entry
    ) is False


def test_e15_e14_debt_rejects_genuine_wrong_canonical_status(
    fixture: e15.Fixture,
) -> None:
    checks = e15._v42_wrong_canonical_status_checks(fixture)
    source = checks["source"]
    native = checks["native_fixture"]

    assert isinstance(source, e15.E14ResidualDebtSource)
    assert source.candidate.trigger.conflict_record.conflict_id == 640001
    assert source.candidate.residual_record.residual_id == 640002
    assert source.registration_record.registration_id == 640003
    assert source.candidate.ledger_entry.ledger_entry_id == 640004
    assert source.status_record.status_record_id == 640051
    assert {
        candidate.repair_package.repair_id
        for candidate in native.repair_candidates.values()
    } == {640060}
    assert {
        candidate.mutation_record.mutation_id
        for candidate in native.repair_candidates.values()
    } == {640061}
    assert {
        candidate.mutation_record.mutation_id
        for candidate in native.coarsening_candidates.values()
    } == {640064}
    assert checks["concrete_valid"] is True
    assert checks["repair_valid"] is True
    assert checks["coarsening_valid"] is True
    assert checks["occurrence_valid"] is True
    assert checks["collision_case"] is True
    assert checks["observed_status"] is e15.e14.ReconsolidationStatus.outcome_collision
    assert checks["exactly_one"] is True
    assert checks["original_item"] is True
    assert checks["collision_item"] is False
    assert checks["credited"] == 0


def test_e15_off_inventory_offline_flows_are_rejected_only_by_membership(
    fixture: e15.Fixture,
) -> None:
    checks = e15._v42_off_inventory_flow_checks(fixture)
    data = checks["data"]
    positive = checks["positive_clone"]
    decorative = checks["decorative_clone"]

    assert positive.flow_id == 1450072
    assert decorative.flow_id == 1450073
    assert positive not in data.flows
    assert decorative not in data.flows
    assert checks["positive_complete"] is True
    assert checks["decorative_complete"] is True
    assert checks["positive_member_accepts"] is True
    assert checks["decorative_member_accepts"] is True
    assert checks["positive_off_inventory"] is False
    assert checks["decorative_off_inventory"] is False


def test_e15_out_of_phase_discharge_fails_only_timestamp_linkage(
    fixture: e15.Fixture,
) -> None:
    checks = e15._v42_out_of_phase_discharge_checks(fixture)
    canonical = checks["canonical"]
    mutated = checks["mutated_discharge"]
    fields = checks["checks"]

    assert canonical.flow_id == 1460071
    assert canonical.discharge_records[0].discharge_id == 58000171
    assert canonical.discharge_records[0].discharged_at == 1
    assert mutated.discharged_at == 2
    assert mutated.phase_record.start_time == 0
    assert mutated.phase_record.end_time == 1
    assert fields["everyDischargeLinked"] is False
    assert checks["other_fields"] is True
    assert checks["complete"] is False


def test_e15_budget_geometry_is_projected_from_one_allocation(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_alternation_required"]

    assert e15.derived_offline_budget_geometry(
        fixture, data.scope, data.budget_data, data.allocation
    )
    assert e15.kappa_on(data.allocation) == 4
    assert e15.freed_allocation(data.allocation) == 2
    assert e15.kappa_off(data.allocation) == 6
    assert e15.kappa_off(data.allocation) == (
        e15.kappa_on(data.allocation) + e15.freed_allocation(data.allocation)
    )


def test_e15_zero_exchange_does_not_substitute_for_p2_gate(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_zero_exchange_without_p2"]
    phase = data.schedule.phases[0]

    assert e15.complete_external_exchange_inventory(fixture, data) is True
    assert e15.exchange_in_phase(data.exchange_records, phase) == 0
    assert data.gates == ()
    assert e15.genuine_offline_phase_evidence(fixture, data, phase) is False


def test_e15_complete_exchange_census_rejects_omission_and_duplicates(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_alternation_required"]
    omitted = data.exchange_records[1:]
    repeated = data.exchange_records + (data.exchange_records[0],)
    reused_id = data.exchange_records + (
        replace(data.exchange_records[0], exchanged_amount=2),
    )

    assert e15.external_exchange_inventory_checks(fixture, data, omitted)[
        "completeForSchedule"
    ] is False
    assert e15.external_exchange_inventory_checks(fixture, data, repeated)[
        "recordsNodup"
    ] is False
    assert e15.external_exchange_inventory_checks(fixture, data, reused_id)[
        "recordIdsNodup"
    ] is False


def test_e15_top_priority_raw_evidence_excludes_lower_status_tag(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_deficit_online_counterexample"]
    adversarial = replace(
        data.status_record, status=e15.OfflineReclosureStatus.alternation_required
    )
    raw = e15.raw_evidence_truths(fixture, data)
    truths = e15.case_truths_for_record(fixture, data, adversarial)

    assert raw[e15.OfflineReclosureStatus.deficit_online_counterexample] is True
    assert truths[e15.OfflineReclosureStatus.alternation_required] is False
    assert all(truths[status] is False for status in e15.STATUS_PRIORITY)


def test_e15_full_claim_key_keeps_status_records_independent(
) -> None:
    online_fixture, online, mismatch_fixture, mismatch = (
        e15.build_claim_scoping_pair()
    )

    assert online.scope is mismatch.scope
    assert e15.classify_claim_data(online_fixture, online)[0] is (
        e15.OfflineReclosureStatus.online_sufficient
    )
    assert e15.classify_claim_data(mismatch_fixture, mismatch)[0] is (
        e15.OfflineReclosureStatus.duty_cycle_mismatch
    )
    assert e15.offline_reclosure_status_record_matches_claim(
        online.claim_ref, online.status_record
    )
    assert e15.offline_reclosure_status_record_matches_claim(
        mismatch.claim_ref, mismatch.status_record
    )
    assert not e15.offline_reclosure_status_record_matches_claim(
        online.claim_ref, mismatch.status_record
    )
    assert not e15.offline_reclosure_status_record_matches_claim(
        mismatch.claim_ref, online.status_record
    )


def test_e15_online_capacity_bound_is_load_bearing(
    fixture: e15.Fixture,
) -> None:
    persistent = fixture.claims["capacity_persistent"]
    bounded = fixture.claims["capacity_bounded"]
    sufficient = fixture.claims["capacity_sufficient"]

    assert [e15.closure_debt_discharge_rate(data.flows[0]) for data in (
        persistent,
        bounded,
        sufficient,
    )] == [5, 5, 5]
    assert e15.persistent_deficit_evidence(fixture, persistent) is False
    assert e15.deficit_online_bounded_counterexample(fixture, bounded) is False
    assert e15.online_sufficient_evidence(fixture, sufficient) is False
    assert all(
        e15.persistent_deficit_noncapacity_checks(fixture, persistent).values()
    )
    assert all(
        e15.bounded_counterexample_noncapacity_checks(fixture, bounded).values()
    )
    assert all(
        e15.online_sufficient_noncapacity_checks(fixture, sufficient).values()
    )


def test_e15_negative_tolerance_is_rejected_at_construction(
    fixture: e15.Fixture,
) -> None:
    tolerance = fixture.claims["claim_duty_cycle_mismatch"].tolerance

    with pytest.raises(ValueError, match="nonnegative"):
        replace(tolerance, tolerance=F(-1))


@pytest.mark.parametrize("maximum", (F(0), F(-1)))
def test_e15_nonpositive_recurrence_bound_is_rejected_at_construction(
    fixture: e15.Fixture, maximum: Fraction
) -> None:
    recurrence = fixture.claims["claim_deficit_online_counterexample"].recurrence_bound

    with pytest.raises(ValueError, match="positive"):
        replace(recurrence, maximum_online_run=maximum)


def test_e15_missing_first_online_flow_fails_closed(
    fixture: e15.Fixture,
) -> None:
    data = fixture.claims["claim_duty_cycle_mismatch"]
    first_online = next(
        phase for phase in data.schedule.phases if phase.mode is e15.OperatingMode.online
    )
    incomplete = replace(
        data,
        flows=tuple(flow for flow in data.flows if flow.phase_record != first_online),
    )

    assert e15.duty_cycle_prediction_evidence(fixture, incomplete) is False
    assert e15.duty_cycle_mismatch_evidence(fixture, incomplete) is False


def test_e15_offline_ablation_census_is_carried_and_chronological(
    fixture: e15.Fixture,
) -> None:
    traces = [fixture.claims[f"ablation_trace_{index}"] for index in range(1, 5)]

    assert all(e15.skipped_offline_cascade_evidence(fixture, data) for data in traces)
    assert all(data.alarm_observation.observed_at < data.stress_observation.observed_at for data in traces)
    assert all(data.alarm_observation.phase_record in data.schedule.phases for data in traces)
    assert all(data.stress_observation.phase_record in data.schedule.phases for data in traces)
