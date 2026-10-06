from __future__ import annotations

import inspect

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordOccurrence,
    CarriedRecordPolicy,
    CheckRuleRecord,
    DeclaredTrajectory,
    FineSourceTag,
)
from sixbirds_foundations_v.e_system import (
    ActiveCarriedInstrument,
    CarriedLedger,
    ESystem,
    RepairMove,
    RepairSort,
    TheoryPackage,
    lawful_repair_step,
)


def _trajectory() -> DeclaredTrajectory[int]:
    def tau(n: int) -> int:
        return n

    def legitimate_start(candidate_tau, n_start: int) -> bool:
        return n_start == 0 and candidate_tau(n_start) == 0

    def supp_k(z: int, z_next: int) -> bool:
        return z_next == z + 1

    return DeclaredTrajectory(
        legitimate_start=legitimate_start,
        supp_k=supp_k,
        tau=tau,
        step_in_scope=lambda _n: True,
        n_start=0,
    )


def _policy(trajectory: DeclaredTrajectory[int], prefix: str) -> CarriedRecordPolicy[int, str]:
    def rho_of(z: int) -> str:
        return f"{prefix}-{z}"

    def coordinate_declared(readout) -> bool:
        return readout is rho_of

    return CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=coordinate_declared,
        rho_of=rho_of,
        name=prefix,
    )


def _evidence(
    n0: int,
    *,
    tag: FineSourceTag = FineSourceTag.committed_state,
    generated_by_s: bool = True,
    in_scope: bool = True,
) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=tag,
        generated_by_s=generated_by_s,
        in_scope=in_scope,
    )


def _system(
    *,
    detects=None,
    gate_allows=None,
    re_audits=None,
    admissible_move=None,
    move_budget_line: str = "ledger-1",
) -> tuple[
    ESystem[int, str, str, str, str, str, str],
    CarriedRecordEvidence,
    CarriedRecordEvidence,
]:
    trajectory = _trajectory()
    theory = TheoryPackage(
        trajectory=trajectory,
        f="f",
        sigma_f="sigma",
        residual_family="residuals",
        audit_access="audit-access",
        formed_package=True,
    )
    ledger_policy = _policy(trajectory, "ledger")
    defect_policy = _policy(trajectory, "defect")
    move_policy = _policy(trajectory, "move")
    audit_policy = _policy(trajectory, "audit")
    instrument_policy = _policy(trajectory, "instrument")

    ledger_evidence = {"ledger-1": _evidence(1)}
    ledger = CarriedLedger(
        ledger_policy=ledger_policy,
        ledger_entries=["ledger-1"],
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: ledger_evidence.get(entry),
    )
    move = RepairMove(
        sort=RepairSort.P4,
        payload="repair-payload",
        move_record="move-0",
        move_record_evidence=_evidence(0),
        budget_line=move_budget_line,
    )
    instrument_occurrence = CarriedRecordOccurrence(
        record="instrument-0",
        evidence=_evidence(0, tag=FineSourceTag.audited_cell_records),
    )
    instrument = ActiveCarriedInstrument(
        instrument="instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=[instrument_occurrence],
        threshold_records=[instrument_occurrence],
        check_rule_records=[CheckRuleRecord(record=instrument_occurrence, audit="passes")],
        detects=detects or (lambda z, defect: z == 0 and defect == "defect-0"),
        gate_allows=gate_allows or (lambda z, defect, repair: repair == move),
        re_audits=re_audits or (lambda z, repair, z_next, audit: audit == "audit-1"),
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda _defect: move,
        AdmissibleMove=admissible_move
        or (lambda carried_ledger, z, defect, repair: repair.sort == RepairSort.P4),
    )
    return system, _evidence(0), _evidence(1)


def test_genuinely_lawful_repair_step_passes() -> None:
    system, defect_evidence, audit_evidence = _system()

    assert system.is_well_formed()
    assert system.repair_step(
        0,
        1,
        "defect-0",
        defect_evidence,
        "audit-1",
        audit_evidence,
    )


def test_repair_step_rejects_missing_detection_only() -> None:
    system, defect_evidence, audit_evidence = _system(
        detects=lambda _z, _defect: False,
    )

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", audit_evidence)


def test_repair_step_rejects_missing_gate_only() -> None:
    system, defect_evidence, audit_evidence = _system(
        gate_allows=lambda _z, _defect, _move: False,
    )

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", audit_evidence)


def test_repair_step_rejects_off_kernel_transition_only() -> None:
    system, defect_evidence, audit_evidence = _system()

    assert system.is_well_formed()
    assert not system.repair_step(0, 2, "defect-0", defect_evidence, "audit-1", audit_evidence)


def test_repair_step_rejects_missing_reaudit_only() -> None:
    system, defect_evidence, audit_evidence = _system(
        re_audits=lambda _z, _move, _z_next, _audit: False,
    )

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", audit_evidence)


def test_repair_step_rejects_uncarried_defect_record_only() -> None:
    system, _defect_evidence, audit_evidence = _system()
    fallback_defect = _evidence(0, tag=FineSourceTag.fallback)

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", fallback_defect, "audit-1", audit_evidence)


def test_repair_step_rejects_uncarried_audit_record_only() -> None:
    system, defect_evidence, _audit_evidence = _system()
    fallback_audit = _evidence(1, tag=FineSourceTag.fallback)

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", fallback_audit)


def test_repair_step_rejects_budget_line_not_in_ledger_only() -> None:
    system, defect_evidence, audit_evidence = _system(move_budget_line="missing-ledger-line")

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", audit_evidence)


def test_repair_step_rejects_inadmissible_move_only() -> None:
    system, defect_evidence, audit_evidence = _system(
        admissible_move=lambda _ledger, _z, _defect, _move: False,
    )

    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", audit_evidence)


def test_active_instrument_gate_callables_are_bundled_and_load_bearing() -> None:
    system, defect_evidence, audit_evidence = _system(
        detects=lambda _z, _defect: False,
        gate_allows=lambda _z, _defect, _move: True,
        re_audits=lambda _z, _move, _z_next, _audit: True,
    )

    assert "detects" not in inspect.signature(lawful_repair_step).parameters
    assert "gate_allows" not in inspect.signature(lawful_repair_step).parameters
    assert "re_audits" not in inspect.signature(lawful_repair_step).parameters
    assert system.is_well_formed()
    assert not system.repair_step(0, 1, "defect-0", defect_evidence, "audit-1", audit_evidence)
