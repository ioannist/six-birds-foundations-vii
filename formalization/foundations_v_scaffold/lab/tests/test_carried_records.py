from __future__ import annotations

import inspect

import pytest

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordOccurrence,
    CarriedRecordPolicy,
    CheckRuleRecord,
    DeclaredTrajectory,
    FineSourceTag,
    carried_instrument,
    carried_record_at,
    carried_record_occurrence,
    carried_source,
    has_carried_record_evidence,
    own_kernel_trace_to,
)


def _trajectory(*, out_of_scope_step: int | None = None) -> DeclaredTrajectory[int]:
    def tau(n: int) -> int:
        return n

    def legitimate_start(candidate_tau, n_start: int) -> bool:
        return n_start == 0 and candidate_tau(n_start) == 0

    def supp_k(z: int, z_next: int) -> bool:
        return z_next == z + 1

    def step_in_scope(n: int) -> bool:
        return n != out_of_scope_step

    return DeclaredTrajectory(
        legitimate_start=legitimate_start,
        supp_k=supp_k,
        tau=tau,
        step_in_scope=step_in_scope,
        n_start=0,
    )


def _policy(
    trajectory: DeclaredTrajectory[int] | None = None,
) -> CarriedRecordPolicy[int, str]:
    def rho_of(z: int) -> str:
        return f"record-{z}"

    def coordinate_declared(readout) -> bool:
        return readout is rho_of

    return CarriedRecordPolicy(
        trajectory=trajectory or _trajectory(),
        coordinate_declared=coordinate_declared,
        rho_of=rho_of,
        name="test-record-family",
    )


def test_carried_source_accepts_only_system_generated_in_scope_core_tags() -> None:
    assert carried_source(FineSourceTag.committed_state, True, True)
    assert carried_source(FineSourceTag.audited_cell_records, True, True)
    assert not carried_source(FineSourceTag.independent_pair_witness, True, True)
    assert not carried_source(FineSourceTag.simulation_trace, True, True)
    assert not carried_source(FineSourceTag.ablation_record, True, True)
    assert not carried_source(FineSourceTag.fallback, True, True)
    assert not carried_source(FineSourceTag.unknown, True, True)
    assert not carried_source(FineSourceTag.contradictory, True, True)
    assert not carried_source(FineSourceTag.committed_state, False, True)
    assert not carried_source(FineSourceTag.committed_state, True, False)


def test_genuinely_carried_record_passes_carried_record_at() -> None:
    policy = _policy()
    evidence = CarriedRecordEvidence(
        n0=2,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )
    occurrence = CarriedRecordOccurrence(record="record-2", evidence=evidence)

    assert own_kernel_trace_to(policy.trajectory, 2)
    assert carried_record_at(
        policy,
        occurrence.record,
        evidence.n0,
        evidence.source_tag,
        evidence.generated_by_s,
        evidence.in_scope,
    )
    assert carried_record_occurrence(policy, occurrence)
    assert has_carried_record_evidence(policy, occurrence.record, evidence)


def test_degenerate_per_record_trajectory_cannot_be_passed_to_api() -> None:
    policy = _policy()
    assert "tau" not in inspect.signature(carried_record_at).parameters
    assert "supp_k" not in inspect.signature(carried_record_at).parameters
    assert not carried_record_at(
        policy,
        "forged-record",
        1,
        FineSourceTag.committed_state,
        True,
        True,
    )

    with pytest.raises(TypeError):
        carried_record_at(
            policy,
            "forged-record",
            1,
            FineSourceTag.committed_state,
            True,
            True,
            tau=lambda _n: "forged-record",
        )


def test_fallback_occurrence_cannot_borrow_same_value_carriedness() -> None:
    policy = _policy()
    rho = "record-2"

    assert carried_record_at(
        policy,
        rho,
        2,
        FineSourceTag.committed_state,
        True,
        True,
    )
    assert not carried_record_at(
        policy,
        rho,
        2,
        FineSourceTag.fallback,
        True,
        True,
    )


def test_out_of_scope_step_in_contiguous_range_blocks_carriedness() -> None:
    policy = _policy(_trajectory(out_of_scope_step=1))

    assert not own_kernel_trace_to(policy.trajectory, 2)
    assert not carried_record_at(
        policy,
        "record-2",
        2,
        FineSourceTag.committed_state,
        True,
        True,
    )


def test_carried_instrument_requires_complete_inventory_and_all_records() -> None:
    policy = _policy()
    evidence = CarriedRecordEvidence(
        n0=1,
        source_tag=FineSourceTag.audited_cell_records,
        generated_by_s=True,
        in_scope=True,
    )
    occurrence = CarriedRecordOccurrence(record="record-1", evidence=evidence)
    check_rule = CheckRuleRecord(record=occurrence, audit="passes")

    assert carried_instrument(
        policy,
        records_are_complete_inventory=True,
        visibility_records=[occurrence],
        threshold_records=[occurrence],
        check_rule_records=[check_rule],
    )
    assert not carried_instrument(
        policy,
        records_are_complete_inventory=False,
        visibility_records=[occurrence],
        threshold_records=[occurrence],
        check_rule_records=[check_rule],
    )

    fallback = CarriedRecordOccurrence(
        record="record-1",
        evidence=CarriedRecordEvidence(
            n0=1,
            source_tag=FineSourceTag.fallback,
            generated_by_s=True,
            in_scope=True,
        ),
    )
    assert not carried_instrument(
        policy,
        records_are_complete_inventory=True,
        visibility_records=[occurrence],
        threshold_records=[occurrence],
        check_rule_records=[CheckRuleRecord(record=fallback, audit="passes")],
    )
