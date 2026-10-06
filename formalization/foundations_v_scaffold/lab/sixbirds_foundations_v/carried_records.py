"""D3 carried-record checks for the Repair-World lab.

The API follows the final Lean shape used by ``ESystem.lean``:
system trajectory data is shared, record-family readouts live in a fixed
``CarriedRecordPolicy``, and a record occurrence supplies only its own read
time and source classification.  Callers should not manufacture a fresh
trajectory or readout per record value.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar


Z = TypeVar("Z")
R = TypeVar("R")


class FineSourceTag(str, Enum):
    committed_state = "committed_state"
    audited_cell_records = "audited_cell_records"
    independent_pair_witness = "independent_pair_witness"
    simulation_trace = "simulation_trace"
    ablation_record = "ablation_record"
    fallback = "fallback"
    unknown = "unknown"
    contradictory = "contradictory"


def carried_source(
    tag: FineSourceTag,
    generated_by_s: bool,
    in_scope: bool,
) -> bool:
    """Return D3's ``CarriedSource`` predicate."""

    return (
        tag in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and generated_by_s is True
        and in_scope is True
    )


@dataclass(frozen=True)
class DeclaredTrajectory(Generic[Z]):
    """Shared system-level trajectory data.

    This is the Python counterpart of the fixed ``LegitimateStart``, ``suppK``,
    ``tau``, ``StepInScope``, and ``nStart`` fields carried by D4's
    ``TheoryPackage``.  One such value belongs to the carrier/system; it is not
    evidence that an individual record gets to re-choose.
    """

    legitimate_start: Callable[[Callable[[int], Z], int], bool]
    supp_k: Callable[[Z, Z], bool]
    tau: Callable[[int], Z]
    step_in_scope: Callable[[int], bool]
    n_start: int

    def __post_init__(self) -> None:
        if self.n_start < 0:
            raise ValueError("n_start must be nonnegative")


@dataclass(frozen=True)
class CarriedRecordPolicy(Generic[Z, R]):
    """Fixed carriedness policy for one record family."""

    trajectory: DeclaredTrajectory[Z]
    coordinate_declared: Callable[[Callable[[Z], R]], bool]
    rho_of: Callable[[Z], R]
    name: str | None = None


@dataclass(frozen=True)
class CarriedRecordEvidence:
    """Concrete occurrence data for one carried-record witness."""

    n0: int
    source_tag: FineSourceTag
    generated_by_s: bool
    in_scope: bool

    def __post_init__(self) -> None:
        if self.n0 < 0:
            raise ValueError("n0 must be nonnegative")


@dataclass(frozen=True)
class CarriedRecordOccurrence(Generic[R]):
    """A record value bundled with its own declared source occurrence."""

    record: R
    evidence: CarriedRecordEvidence


@dataclass(frozen=True)
class CheckRuleRecord(Generic[R]):
    """Instrument check-rule record anchored by an audit/check tag."""

    record: CarriedRecordOccurrence[R]
    audit: Any


def own_kernel_trace_to(trajectory: DeclaredTrajectory[Z], n0: int) -> bool:
    """Check D3's final contiguous ``OwnKernelTraceTo`` condition.

    Every index in ``[n_start, n0)`` must be in scope and must be a transition
    supported by the shared kernel relation.  This is a conjunction at every
    step, not an implication gated by ``step_in_scope``.
    """

    if n0 < trajectory.n_start:
        return False
    if not trajectory.legitimate_start(trajectory.tau, trajectory.n_start):
        return False
    for n in range(trajectory.n_start, n0):
        if not trajectory.step_in_scope(n):
            return False
        if not trajectory.supp_k(trajectory.tau(n), trajectory.tau(n + 1)):
            return False
    return True


def carried_record_at(
    policy: CarriedRecordPolicy[Z, R],
    rho: R,
    n0: int,
    source_tag: FineSourceTag,
    generated_by_s: bool,
    in_scope: bool,
) -> bool:
    """Check D4's concrete ``CarriedRecordAt`` wrapper.

    The trajectory and family readout come from ``policy``.  The caller supplies
    only the record occurrence's own read time and source classification.
    """

    trajectory = policy.trajectory
    return (
        policy.coordinate_declared(policy.rho_of)
        and own_kernel_trace_to(trajectory, n0)
        and rho == policy.rho_of(trajectory.tau(n0))
        and carried_source(source_tag, generated_by_s, in_scope)
    )


def carried_record_occurrence(
    policy: CarriedRecordPolicy[Z, R],
    occurrence: CarriedRecordOccurrence[R],
) -> bool:
    evidence = occurrence.evidence
    return carried_record_at(
        policy,
        occurrence.record,
        evidence.n0,
        evidence.source_tag,
        evidence.generated_by_s,
        evidence.in_scope,
    )


def has_carried_record_evidence(
    policy: CarriedRecordPolicy[Z, R],
    rho: R,
    evidence: CarriedRecordEvidence,
) -> bool:
    """Verify a supplied D4-style evidence object.

    This is deliberately not an existential search for evidence.
    """

    return carried_record_at(
        policy,
        rho,
        evidence.n0,
        evidence.source_tag,
        evidence.generated_by_s,
        evidence.in_scope,
    )


def carried_instrument(
    policy: CarriedRecordPolicy[Z, R],
    *,
    records_are_complete_inventory: bool,
    visibility_records: Sequence[CarriedRecordOccurrence[R]],
    threshold_records: Sequence[CarriedRecordOccurrence[R]],
    check_rule_records: Sequence[CheckRuleRecord[R]],
) -> bool:
    """Check D3's carried-instrument shape over explicit record occurrences."""

    return (
        records_are_complete_inventory is True
        and all(carried_record_occurrence(policy, record) for record in visibility_records)
        and all(carried_record_occurrence(policy, record) for record in threshold_records)
        and all(
            carried_record_occurrence(policy, check_rule.record)
            for check_rule in check_rule_records
        )
    )


__all__ = [
    "CarriedRecordEvidence",
    "CarriedRecordOccurrence",
    "CarriedRecordPolicy",
    "CheckRuleRecord",
    "DeclaredTrajectory",
    "FineSourceTag",
    "carried_instrument",
    "carried_record_at",
    "carried_record_occurrence",
    "carried_source",
    "has_carried_record_evidence",
    "own_kernel_trace_to",
]
