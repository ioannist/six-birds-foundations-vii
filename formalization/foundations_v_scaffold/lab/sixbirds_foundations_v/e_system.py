"""D4 endogenous closure-system checks for the Repair-World lab.

This is a structural Python port of the landed ``ESystem.lean`` surface.  The
module uses verification-shaped checkers: formedness, carriedness, instrument
gates, and admissibility remain host-supplied certificates/predicates, and this
module checks that a proposed repair step supplies every required certificate.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordOccurrence,
    CarriedRecordPolicy,
    CheckRuleRecord,
    DeclaredTrajectory,
    carried_instrument,
    has_carried_record_evidence,
)


Z = TypeVar("Z")
LedgerEntry = TypeVar("LedgerEntry")
InstrumentRecord = TypeVar("InstrumentRecord")
DefectRecord = TypeVar("DefectRecord")
MovePayload = TypeVar("MovePayload")
MoveRecord = TypeVar("MoveRecord")
AuditRecord = TypeVar("AuditRecord")


class RepairSort(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"
    P5 = "P5"


@dataclass(frozen=True)
class TheoryPackage(Generic[Z]):
    """Parametric D4 theory package.

    ``DeclaredTrajectory`` owns the shared ``suppK``, ``tau``,
    ``StepInScope``, ``LegitimateStart``, and ``nStart`` data.  The remaining
    fields are opaque host data, matching the Lean port's Mathlib-free,
    parametric treatment.
    """

    trajectory: DeclaredTrajectory[Z]
    f: Any
    sigma_f: Any
    residual_family: Any
    audit_access: Any
    formed_package: bool

    @property
    def supp_k(self) -> Callable[[Z, Z], bool]:
        return self.trajectory.supp_k

    def is_formed(self) -> bool:
        return self.formed_package is True


@dataclass(frozen=True)
class CarriedLedger(Generic[Z, LedgerEntry]):
    ledger_policy: CarriedRecordPolicy[Z, LedgerEntry]
    ledger_entries: Sequence[LedgerEntry]
    complete_ledger_inventory: bool
    ledger_evidence: Callable[[LedgerEntry], CarriedRecordEvidence | None]

    def entry_carried(self, entry: LedgerEntry) -> bool:
        evidence = self.ledger_evidence(entry)
        if evidence is None:
            return False
        return has_carried_record_evidence(self.ledger_policy, entry, evidence)

    def is_carried(self) -> bool:
        return self.complete_ledger_inventory is True and all(
            self.entry_carried(entry) for entry in self.ledger_entries
        )


@dataclass(frozen=True)
class RepairMove(Generic[MovePayload, LedgerEntry, MoveRecord]):
    sort: RepairSort
    payload: MovePayload
    move_record: MoveRecord
    move_record_evidence: CarriedRecordEvidence
    budget_line: LedgerEntry

    def record_carried(self, policy: CarriedRecordPolicy[Any, MoveRecord]) -> bool:
        return has_carried_record_evidence(
            policy,
            self.move_record,
            self.move_record_evidence,
        )


@dataclass(frozen=True)
class ActiveCarriedInstrument(
    Generic[
        Z,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ]
):
    """D4 active instrument: carried records plus its own gates."""

    instrument: Any
    instrument_record_policy: CarriedRecordPolicy[Z, InstrumentRecord]
    records_are_complete_inventory: bool
    visibility_records: Sequence[CarriedRecordOccurrence[InstrumentRecord]]
    threshold_records: Sequence[CarriedRecordOccurrence[InstrumentRecord]]
    check_rule_records: Sequence[CheckRuleRecord[InstrumentRecord]]
    detects: Callable[[Z, DefectRecord], bool]
    gate_allows: Callable[
        [Z, DefectRecord, RepairMove[MovePayload, LedgerEntry, MoveRecord]],
        bool,
    ]
    re_audits: Callable[
        [Z, RepairMove[MovePayload, LedgerEntry, MoveRecord], Z, AuditRecord],
        bool,
    ]

    def is_carried(self) -> bool:
        return carried_instrument(
            self.instrument_record_policy,
            records_are_complete_inventory=self.records_are_complete_inventory,
            visibility_records=self.visibility_records,
            threshold_records=self.threshold_records,
            check_rule_records=self.check_rule_records,
        )


def _policy_uses_theory(
    theory: TheoryPackage[Z],
    policy: CarriedRecordPolicy[Z, Any],
) -> bool:
    return policy.trajectory is theory.trajectory


def lawful_repair_step(
    *,
    theory: TheoryPackage[Z],
    ledger: CarriedLedger[Z, LedgerEntry],
    defect_record_policy: CarriedRecordPolicy[Z, DefectRecord],
    move_record_policy: CarriedRecordPolicy[Z, MoveRecord],
    audit_record_policy: CarriedRecordPolicy[Z, AuditRecord],
    instrument: ActiveCarriedInstrument[
        Z,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ],
    admissible_move: Callable[
        [
            CarriedLedger[Z, LedgerEntry],
            Z,
            DefectRecord,
            RepairMove[MovePayload, LedgerEntry, MoveRecord],
        ],
        bool,
    ],
    z: Z,
    z_next: Z,
    defect: DefectRecord,
    defect_evidence: CarriedRecordEvidence,
    move: RepairMove[MovePayload, LedgerEntry, MoveRecord],
    audit_record: AuditRecord,
    audit_record_evidence: CarriedRecordEvidence,
) -> bool:
    """Check D4's ``LawfulRepairStep`` conjunction."""

    return (
        theory.is_formed()
        and _policy_uses_theory(theory, ledger.ledger_policy)
        and _policy_uses_theory(theory, defect_record_policy)
        and _policy_uses_theory(theory, move_record_policy)
        and _policy_uses_theory(theory, audit_record_policy)
        and _policy_uses_theory(theory, instrument.instrument_record_policy)
        and ledger.is_carried()
        and instrument.is_carried()
        and has_carried_record_evidence(
            defect_record_policy,
            defect,
            defect_evidence,
        )
        and move.record_carried(move_record_policy)
        and instrument.detects(z, defect)
        and instrument.gate_allows(z, defect, move)
        and admissible_move(ledger, z, defect, move)
        and move.budget_line in ledger.ledger_entries
        and theory.supp_k(z, z_next)
        and instrument.re_audits(z, move, z_next, audit_record)
        and has_carried_record_evidence(
            audit_record_policy,
            audit_record,
            audit_record_evidence,
        )
    )


def repair_generator_step(
    *,
    theory: TheoryPackage[Z],
    ledger: CarriedLedger[Z, LedgerEntry],
    defect_record_policy: CarriedRecordPolicy[Z, DefectRecord],
    move_record_policy: CarriedRecordPolicy[Z, MoveRecord],
    audit_record_policy: CarriedRecordPolicy[Z, AuditRecord],
    instrument: ActiveCarriedInstrument[
        Z,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ],
    admissible_move: Callable[
        [
            CarriedLedger[Z, LedgerEntry],
            Z,
            DefectRecord,
            RepairMove[MovePayload, LedgerEntry, MoveRecord],
        ],
        bool,
    ],
    repair_generator: Callable[
        [DefectRecord],
        RepairMove[MovePayload, LedgerEntry, MoveRecord],
    ],
    z: Z,
    z_next: Z,
    defect: DefectRecord,
    defect_evidence: CarriedRecordEvidence,
    audit_record: AuditRecord,
    audit_record_evidence: CarriedRecordEvidence,
) -> bool:
    return lawful_repair_step(
        theory=theory,
        ledger=ledger,
        defect_record_policy=defect_record_policy,
        move_record_policy=move_record_policy,
        audit_record_policy=audit_record_policy,
        instrument=instrument,
        admissible_move=admissible_move,
        z=z,
        z_next=z_next,
        defect=defect,
        defect_evidence=defect_evidence,
        move=repair_generator(defect),
        audit_record=audit_record,
        audit_record_evidence=audit_record_evidence,
    )


@dataclass(frozen=True)
class ESystem(
    Generic[
        Z,
        InstrumentRecord,
        LedgerEntry,
        DefectRecord,
        MovePayload,
        MoveRecord,
        AuditRecord,
    ]
):
    T: TheoryPackage[Z]
    defect_record_policy: CarriedRecordPolicy[Z, DefectRecord]
    move_record_policy: CarriedRecordPolicy[Z, MoveRecord]
    audit_record_policy: CarriedRecordPolicy[Z, AuditRecord]
    I_S: ActiveCarriedInstrument[
        Z,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ]
    Lambda_S: CarriedLedger[Z, LedgerEntry]
    R_S: Callable[[DefectRecord], RepairMove[MovePayload, LedgerEntry, MoveRecord]]
    AdmissibleMove: Callable[
        [
            CarriedLedger[Z, LedgerEntry],
            Z,
            DefectRecord,
            RepairMove[MovePayload, LedgerEntry, MoveRecord],
        ],
        bool,
    ]

    def is_well_formed(self) -> bool:
        return (
            self.T.is_formed()
            and _policy_uses_theory(self.T, self.defect_record_policy)
            and _policy_uses_theory(self.T, self.move_record_policy)
            and _policy_uses_theory(self.T, self.audit_record_policy)
            and _policy_uses_theory(self.T, self.I_S.instrument_record_policy)
            and _policy_uses_theory(self.T, self.Lambda_S.ledger_policy)
            and self.I_S.is_carried()
            and self.Lambda_S.is_carried()
        )

    def repair_step(
        self,
        z: Z,
        z_next: Z,
        defect: DefectRecord,
        defect_evidence: CarriedRecordEvidence,
        audit_record: AuditRecord,
        audit_record_evidence: CarriedRecordEvidence,
    ) -> bool:
        return self.is_well_formed() and repair_generator_step(
            theory=self.T,
            ledger=self.Lambda_S,
            defect_record_policy=self.defect_record_policy,
            move_record_policy=self.move_record_policy,
            audit_record_policy=self.audit_record_policy,
            instrument=self.I_S,
            admissible_move=self.AdmissibleMove,
            repair_generator=self.R_S,
            z=z,
            z_next=z_next,
            defect=defect,
            defect_evidence=defect_evidence,
            audit_record=audit_record,
            audit_record_evidence=audit_record_evidence,
        )


__all__ = [
    "ActiveCarriedInstrument",
    "CarriedLedger",
    "ESystem",
    "RepairMove",
    "RepairSort",
    "TheoryPackage",
    "lawful_repair_step",
    "repair_generator_step",
]
