"""Repair-World carrier wiring.

This module assembles the landed D1/D3/D4/D6 Python ports into the finite
carrier described by THEOREMS.md section 7.  It is wiring, not a new lawfulness
theory: probe moves delegate to ``probe_economy``, repair moves delegate to
``e_system``, and D1's repair join is used to update the carried quotient table.
Compilation and offline-toggle actions are declared stubs because their E-law
checkers have not landed yet. E3 maintenance actions have a concrete
lawfulness checker; ``MaintenanceStubAction`` remains available for older
fixtures that deliberately exercise the deferred path.

The carried ledger is treated here as a fixed, pre-provisioned inventory:
Repair-World actions read ledger entries but do not create retirement records,
accumulate spend, or mutate budgets.  Multi-step ledger dynamics are deferred to
the E6/E8/E9 law units that specify the relevant update semantics.

This first carrier also deliberately identifies the external position ``y`` and
D4 trajectory coordinate ``z`` as the same integer.  Repair actions pass
``state.y`` to D4 and set the successor ``y`` to ``z_next``.  If a future E-law
needs repairs asynchronous with external motion, the carrier will need separate
``y`` and ``z`` fields.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Generic, TypeVar

import numpy as np

from sixbirds_foundations_v.carried_records import CarriedRecordEvidence, FineSourceTag
from sixbirds_foundations_v.carrier.kernel import FiniteKernel
from sixbirds_foundations_v.carrier.viability import (
    viability_kernel,
    viability_kernel_history,
)
from sixbirds_foundations_v.e_system import (
    ActiveCarriedInstrument,
    CarriedLedger,
    ESystem,
    lawful_repair_step,
)
from sixbirds_foundations_v.probe_economy import (
    AcquisitionLedgerEvidence,
    ActiveFamily,
    ActiveFamilyClassification,
    AllocationLedgerEvidence,
    ProbeEconomy,
    RetirementLedgerEvidence,
    lawful_acquisition,
    lawful_allocation,
    lawful_retirement,
)
from sixbirds_foundations_v.repair_join import repair_join


Probe = TypeVar("Probe")
XiFamily = TypeVar("XiFamily")
LedgerEntry = TypeVar("LedgerEntry")
InstrumentRecord = TypeVar("InstrumentRecord")
DefectRecord = TypeVar("DefectRecord")
MovePayload = TypeVar("MovePayload")
MoveRecord = TypeVar("MoveRecord")
AuditRecord = TypeVar("AuditRecord")
CarrierItem = TypeVar("CarrierItem", bound=Hashable)
ClassId = TypeVar("ClassId")
RepairClassId = TypeVar("RepairClassId")
StateId = TypeVar("StateId", bound=Hashable)


class LawfulnessStatus(str, Enum):
    lawful = "lawful"
    unlawful = "unlawful"
    deferred = "deferred"


@dataclass(frozen=True)
class ActionLawfulness:
    status: LawfulnessStatus
    reason: str

    @classmethod
    def lawful(cls, reason: str = "lawful") -> "ActionLawfulness":
        return cls(LawfulnessStatus.lawful, reason)

    @classmethod
    def unlawful(cls, reason: str) -> "ActionLawfulness":
        return cls(LawfulnessStatus.unlawful, reason)

    @classmethod
    def deferred(cls, reason: str) -> "ActionLawfulness":
        return cls(LawfulnessStatus.deferred, reason)

    @property
    def is_lawful(self) -> bool:
        return self.status is LawfulnessStatus.lawful

    @property
    def is_deferred(self) -> bool:
        return self.status is LawfulnessStatus.deferred


class UnlawfulActionError(ValueError):
    """Raised when ``step`` is asked to apply a checked-unlawful action."""


class DeferredActionError(ValueError):
    """Raised when ``step`` is asked to apply a declared-but-deferred action."""


class AmbiguousActionError(ValueError):
    """Raised when a lawful stochastic action needs a concrete successor choice."""


@dataclass(frozen=True)
class AuditFlags:
    """Host-specific audit flags for the 1-3 instrument levels."""

    levels: frozenset[int]


@dataclass(frozen=True)
class AuditState(
    Generic[
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ]
):
    instrument: ActiveCarriedInstrument[
        int,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ]
    flags: AuditFlags


@dataclass(frozen=True)
class RepairWorldState(
    Generic[
        CarrierItem,
        ClassId,
        Probe,
        XiFamily,
        LedgerEntry,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        MoveRecord,
        AuditRecord,
    ]
):
    # In this first Repair-World carrier, y is also the D4 trajectory coordinate
    # z used by repair checks.  This is a simplifying identification, not a
    # theorem about external motion and committed trajectories.
    y: int
    q: Mapping[CarrierItem, ClassId]
    L: ActiveFamily[Probe, XiFamily]
    r: CarriedLedger[int, LedgerEntry]
    Lambda: Mapping[str, Fraction]
    A: AuditState[
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        LedgerEntry,
        MoveRecord,
        AuditRecord,
    ]

    def __post_init__(self) -> None:
        object.__setattr__(self, "q", MappingProxyType(dict(self.q)))


@dataclass(frozen=True)
class ChallengeClass:
    name: str


@dataclass(frozen=True)
class ChallengeProcess:
    """Finite challenge process with recurrence and declared drift."""

    recurrence_period: int | None
    default_challenge: ChallengeClass | None = None
    drift_schedule: Mapping[int, ChallengeClass] | None = None
    binding_states: frozenset[int] = frozenset()

    def __post_init__(self) -> None:
        if self.recurrence_period is not None and self.recurrence_period <= 0:
            raise ValueError("recurrence_period must be positive when supplied")

    def challenge_at(self, t: int, y: int) -> ChallengeClass | None:
        if self.recurrence_period is None or t % self.recurrence_period != 0:
            return None
        if self.binding_states and y not in self.binding_states:
            return None
        challenge = self.default_challenge
        if self.drift_schedule:
            for drift_time in sorted(self.drift_schedule):
                if drift_time <= t:
                    challenge = self.drift_schedule[drift_time]
                else:
                    break
        return challenge


@dataclass(frozen=True)
class RepairWorldConfig(
    Generic[
        Probe,
        XiFamily,
        LedgerEntry,
        InstrumentRecord,
        DefectRecord,
        MovePayload,
        MoveRecord,
        AuditRecord,
    ]
):
    kernel: FiniteKernel
    probe_economy: ProbeEconomy[Probe, XiFamily, LedgerEntry]
    e_system: ESystem[
        int,
        InstrumentRecord,
        LedgerEntry,
        DefectRecord,
        MovePayload,
        MoveRecord,
        AuditRecord,
    ]
    challenge_process: ChallengeProcess
    kernel_atol: float = 0.0


@dataclass(frozen=True)
class ExternalAction:
    action_index: int
    next_y: int | None = None


@dataclass(frozen=True)
class AllocationAction(Generic[Probe, XiFamily, LedgerEntry]):
    new_active_family: ActiveFamily[Probe, XiFamily]
    pre_classification: ActiveFamilyClassification
    post_classification: ActiveFamilyClassification
    ledger_evidence: AllocationLedgerEvidence[Probe, LedgerEntry]


@dataclass(frozen=True)
class AcquisitionAction(Generic[Probe, XiFamily, LedgerEntry]):
    probe: Probe
    new_active_family: ActiveFamily[Probe, XiFamily]
    pre_classification: ActiveFamilyClassification
    post_classification: ActiveFamilyClassification
    ledger_evidence: AcquisitionLedgerEvidence[LedgerEntry]
    strict: bool


@dataclass(frozen=True)
class RetirementAction(Generic[Probe, XiFamily, LedgerEntry]):
    probe: Probe
    new_active_family: ActiveFamily[Probe, XiFamily]
    pre_classification: ActiveFamilyClassification
    post_classification: ActiveFamilyClassification
    ledger_evidence: RetirementLedgerEvidence[LedgerEntry]


@dataclass(frozen=True)
class RepairAction(Generic[CarrierItem, RepairClassId, DefectRecord, AuditRecord]):
    repair_package: Mapping[CarrierItem, RepairClassId] | Callable[[CarrierItem], RepairClassId]
    z_next: int
    defect: DefectRecord
    defect_evidence: CarriedRecordEvidence
    audit_record: AuditRecord
    audit_record_evidence: CarriedRecordEvidence


@dataclass(frozen=True)
class MaintenanceAction(Generic[LedgerEntry]):
    """E3 maintenance-reinstatement action over the carried apparatus slot."""

    operator: Any
    source_state: int
    target_state: int
    current_audit_state: AuditState[Any, Any, Any, Any, Any, Any]
    claimed_next_apparatus: Any
    source_tag: FineSourceTag
    generated_by_s: bool
    in_scope: bool
    reinstatement_ledger_entry: LedgerEntry


@dataclass(frozen=True)
class CompilationStubAction:
    deferred_reason: str = "E4 lawfulness not mechanized in Python/Phase 3 pending"


@dataclass(frozen=True)
class MaintenanceStubAction:
    deferred_reason: str = "maintenance action deferred; use MaintenanceAction for E3 lawfulness"


@dataclass(frozen=True)
class OfflineToggleStubAction:
    deferred_reason: str = "E15 deficit-regime/offline law not landed"


RepairWorldAction = (
    ExternalAction
    | AllocationAction[Any, Any, Any]
    | AcquisitionAction[Any, Any, Any]
    | RetirementAction[Any, Any, Any]
    | RepairAction[Any, Any, Any, Any]
    | MaintenanceAction[Any]
    | CompilationStubAction
    | MaintenanceStubAction
    | OfflineToggleStubAction
)


def ring_kernel(n_states: int) -> FiniteKernel:
    """Return a deterministic left/right/stay ring kernel.

    Action indices are ``0 = left``, ``1 = right``, and ``2 = stay``.
    """

    if n_states <= 0:
        raise ValueError("n_states must be positive")
    P = np.zeros((3, n_states, n_states), dtype=float)
    for y in range(n_states):
        P[0, y, (y - 1) % n_states] = 1.0
        P[1, y, (y + 1) % n_states] = 1.0
        P[2, y, y] = 1.0
    kernel = FiniteKernel(P)
    kernel.validate()
    return kernel


def budget_vector(state: RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]) -> Mapping[str, Fraction]:
    """Expose the current display/projection budget vector.

    ``Lambda`` is intentionally not a second carried ledger.  At this stage it
    is a convenience projection supplied alongside the carried ledger ``r``;
    lawfulness checks continue to use ``r`` and D6's ledger-entry predicates.
    Future budget-dual work should either derive this projection from tagged
    carried entries or add an explicit validation certificate.
    """

    return state.Lambda


def _external_support(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
    y: int,
    action: ExternalAction,
) -> set[int]:
    if action.action_index < 0 or action.action_index >= config.kernel.n_actions:
        return set()
    if y < 0 or y >= config.kernel.n_states:
        return set()
    support = {
        y_next
        for y_next, probability in enumerate(config.kernel.P[action.action_index, y])
        if probability > config.kernel_atol
    }
    if action.next_y is not None:
        return {action.next_y} if action.next_y in support else set()
    return support


def _state_uses_config(
    config: RepairWorldConfig[Any, Any, LedgerEntry, Any, Any, Any, Any, Any],
    state: RepairWorldState[Any, Any, Any, Any, LedgerEntry, Any, Any, Any, Any, Any],
) -> bool:
    return state.r is config.e_system.Lambda_S and state.A.instrument is config.e_system.I_S


def _repair_package_function(
    repair_package: Mapping[CarrierItem, RepairClassId] | Callable[[CarrierItem], RepairClassId],
) -> Callable[[CarrierItem], RepairClassId]:
    if callable(repair_package):
        return repair_package
    return lambda item: repair_package[item]


def _repair_package_from_payload(
    payload: Any,
) -> Mapping[Any, Any] | Callable[[Any], Any] | None:
    if callable(payload) or isinstance(payload, Mapping):
        return payload
    return None


def _repair_packages_match(
    supplied: Mapping[Any, Any] | Callable[[Any], Any],
    generated: Mapping[Any, Any] | Callable[[Any], Any],
) -> bool:
    # Identity is required for both callables and mappings.  A custom
    # ``Mapping.__eq__`` can execute arbitrary code just like ``__call__`` can,
    # so equality comparison is not a safe pre-gate operation.
    return supplied is generated


def _materialize_repair_package(
    q: Mapping[CarrierItem, Any],
    repair_package: Mapping[CarrierItem, RepairClassId] | Callable[[CarrierItem], RepairClassId],
) -> dict[CarrierItem, RepairClassId] | None:
    materialized: dict[CarrierItem, RepairClassId] = {}
    try:
        for item in q:
            materialized[item] = repair_package(item) if callable(repair_package) else repair_package[item]
    except Exception:
        return None
    return materialized


def _repair_package_defined_on_q(
    q: Mapping[CarrierItem, Any],
    repair_package: Mapping[CarrierItem, RepairClassId] | Callable[[CarrierItem], RepairClassId],
) -> bool:
    return _materialize_repair_package(q, repair_package) is not None


def _checked_repair_move(
    config: RepairWorldConfig[Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord],
    state: RepairWorldState[CarrierItem, Any, Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord],
    action: RepairAction[CarrierItem, Any, DefectRecord, AuditRecord],
) -> tuple[ActionLawfulness, dict[CarrierItem, Any] | None, dict[CarrierItem, Any] | None]:
    """Validate a RepairAction exactly once and return the materialized package."""

    q_snapshot = dict(state.q)
    generated_move = config.e_system.R_S(action.defect)
    generated_package = _repair_package_from_payload(generated_move.payload)
    if generated_package is None:
        return (
            ActionLawfulness.unlawful("R_S(defect).payload is not a q-refinement package"),
            None,
            None,
        )
    if not _repair_packages_match(action.repair_package, generated_package):
        return (
            ActionLawfulness.unlawful("repair package does not match R_S(defect).payload"),
            None,
            None,
        )
    # Run the D4 gate before invoking any host repair-package callable.  A
    # callable can still mutate shared ledger/instrument objects during a
    # legitimately lawful action's later materialization; this lab records that
    # as an out-of-scope host-mutation limitation rather than deep-copying every
    # shared object into every successor state.
    if config.e_system.is_well_formed() and lawful_repair_step(
        theory=config.e_system.T,
        ledger=config.e_system.Lambda_S,
        defect_record_policy=config.e_system.defect_record_policy,
        move_record_policy=config.e_system.move_record_policy,
        audit_record_policy=config.e_system.audit_record_policy,
        instrument=config.e_system.I_S,
        admissible_move=config.e_system.AdmissibleMove,
        z=state.y,
        z_next=action.z_next,
        defect=action.defect,
        defect_evidence=action.defect_evidence,
        move=generated_move,
        audit_record=action.audit_record,
        audit_record_evidence=action.audit_record_evidence,
    ):
        materialized_package = _materialize_repair_package(q_snapshot, generated_package)
        if materialized_package is None:
            return (
                ActionLawfulness.unlawful(
                    "R_S(defect).payload is not defined on q's carrier"
                ),
                None,
                None,
            )
        return ActionLawfulness.lawful("D4 lawful repair step"), q_snapshot, materialized_package
    return ActionLawfulness.unlawful("D4 repair checker rejected action"), None, None


def _maintenance_outputs_match(claimed: Any, generated: Any) -> bool:
    # Mirroring repair-package discipline: if either side is callable, do not
    # invoke equality, since a hostile ``__eq__``/callable can execute code.
    if callable(claimed) or callable(generated):
        return claimed is generated
    return claimed == generated


def _checked_maintenance_move(
    config: RepairWorldConfig[Any, Any, LedgerEntry, Any, Any, Any, Any, Any],
    state: RepairWorldState[Any, Any, Any, Any, LedgerEntry, Any, Any, Any, Any, Any],
    action: MaintenanceAction[LedgerEntry],
) -> ActionLawfulness:
    """Validate an E3 maintenance action without mutating the state."""

    if not _state_uses_config(config, state):
        return ActionLawfulness.unlawful("state ledger/instrument do not match config E-system")
    if action.current_audit_state != state.A:
        return ActionLawfulness.unlawful("maintenance action does not match current apparatus state")
    if action.source_state != state.y:
        return ActionLawfulness.unlawful("maintenance source state does not match current state")
    if action.source_tag not in {
        FineSourceTag.committed_state,
        FineSourceTag.audited_cell_records,
    }:
        return ActionLawfulness.unlawful("maintenance reinstatement source tag is not carried")
    if action.generated_by_s is not True:
        return ActionLawfulness.unlawful("maintenance reinstatement was not generated by S")
    if action.in_scope is not True:
        return ActionLawfulness.unlawful("maintenance reinstatement is out of scope")
    if action.reinstatement_ledger_entry not in config.e_system.Lambda_S.ledger_entries:
        return ActionLawfulness.unlawful("maintenance ledger entry is not carried")
    if not config.e_system.T.supp_k(action.source_state, action.target_state):
        return ActionLawfulness.unlawful("maintenance transition is not in S.T.suppK")
    generated_output = action.operator.apply(action.source_state)
    if not _maintenance_outputs_match(action.claimed_next_apparatus, generated_output):
        return ActionLawfulness.unlawful(
            "maintenance claimed apparatus does not match operator output"
        )
    return ActionLawfulness.lawful("E3 lawful maintenance step")


def is_lawful_action(
    config: RepairWorldConfig[Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord],
    state: RepairWorldState[Any, Any, Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord],
    action: RepairWorldAction,
    evidence: Any | None = None,
) -> ActionLawfulness:
    """Classify one Repair-World action as lawful, unlawful, or deferred."""

    del evidence
    if isinstance(action, CompilationStubAction):
        return ActionLawfulness.deferred(action.deferred_reason)
    if isinstance(action, MaintenanceStubAction):
        return ActionLawfulness.deferred(action.deferred_reason)
    if isinstance(action, OfflineToggleStubAction):
        return ActionLawfulness.deferred(action.deferred_reason)

    if isinstance(action, ExternalAction):
        if _external_support(config, state.y, action):
            return ActionLawfulness.lawful("kernel support contains external transition")
        return ActionLawfulness.unlawful("external transition not in kernel support")

    if not _state_uses_config(config, state):
        return ActionLawfulness.unlawful("state ledger/instrument do not match config E-system")

    if isinstance(action, AllocationAction):
        if lawful_allocation(
            config.probe_economy,
            state.r,
            state.L,
            action.new_active_family,
            action.pre_classification,
            action.post_classification,
            action.ledger_evidence,
        ):
            return ActionLawfulness.lawful("D6 lawful allocation")
        return ActionLawfulness.unlawful("D6 allocation checker rejected action")

    if isinstance(action, AcquisitionAction):
        if lawful_acquisition(
            config.probe_economy,
            state.r,
            state.L,
            action.probe,
            action.new_active_family,
            action.pre_classification,
            action.post_classification,
            action.ledger_evidence,
            strict=action.strict,
        ):
            return ActionLawfulness.lawful("D6 lawful acquisition")
        return ActionLawfulness.unlawful("D6 acquisition checker rejected action")

    if isinstance(action, RetirementAction):
        if lawful_retirement(
            config.probe_economy,
            state.r,
            state.L,
            action.probe,
            action.new_active_family,
            action.pre_classification,
            action.post_classification,
            action.ledger_evidence,
        ):
            return ActionLawfulness.lawful("D6 lawful retirement")
        return ActionLawfulness.unlawful("D6 retirement checker rejected action")

    if isinstance(action, RepairAction):
        result, _q_snapshot, _materialized_package = _checked_repair_move(config, state, action)
        return result

    if isinstance(action, MaintenanceAction):
        return _checked_maintenance_move(config, state, action)

    return ActionLawfulness.unlawful("unknown action type")


def step(
    config: RepairWorldConfig[Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord],
    state: RepairWorldState[CarrierItem, ClassId, Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord],
    action: RepairWorldAction,
    evidence: Any | None = None,
) -> RepairWorldState[Any, Any, Any, Any, LedgerEntry, Any, DefectRecord, Any, Any, AuditRecord]:
    """Apply a lawful action.

    Unlawful and deferred actions raise instead of silently mutating state.
    Ledger entries are not written here; move-specific ledger records must
    already be present in the carried ledger inventory.
    """

    if isinstance(action, RepairAction):
        result, q_snapshot, materialized_package = _checked_repair_move(config, state, action)
        if result.status is LawfulnessStatus.unlawful:
            raise UnlawfulActionError(result.reason)
        if q_snapshot is None or materialized_package is None:
            raise UnlawfulActionError(result.reason)
        package = _repair_package_function(materialized_package)
        old_q = lambda item: q_snapshot[item]
        joined = repair_join(old_q, package)
        refined_q = {item: joined(item) for item in q_snapshot}
        return replace(state, y=action.z_next, q=refined_q)

    if isinstance(action, MaintenanceAction):
        result = _checked_maintenance_move(config, state, action)
        if result.status is LawfulnessStatus.unlawful:
            raise UnlawfulActionError(result.reason)
        return replace(state, y=action.target_state)

    result = is_lawful_action(config, state, action, evidence)
    if result.status is LawfulnessStatus.deferred:
        raise DeferredActionError(result.reason)
    if result.status is LawfulnessStatus.unlawful:
        raise UnlawfulActionError(result.reason)

    if isinstance(action, ExternalAction):
        support = _external_support(config, state.y, action)
        if action.next_y is not None:
            next_y = action.next_y
        elif len(support) == 1:
            next_y = next(iter(support))
        else:
            raise AmbiguousActionError("external action has non-singleton support; supply next_y")
        return replace(state, y=next_y)

    if isinstance(action, AllocationAction | AcquisitionAction | RetirementAction):
        return replace(state, L=action.new_active_family)

    raise UnlawfulActionError("unknown action type")


def repair_world_viability_kernel_history(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
    state_registry: Mapping[StateId, RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]],
    actions: Sequence[RepairWorldAction],
    safe: Callable[[RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]], bool],
    state_id_of: Callable[[RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]], StateId],
) -> list[set[StateId]]:
    """Run the generic GFP viability iteration over a Repair-World registry."""

    states = list(state_registry.keys())

    def feasible_actions(state_id: StateId) -> list[RepairWorldAction]:
        state = state_registry[state_id]
        return [
            action
            for action in actions
            if is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
        ]

    def post_support(state_id: StateId, action: RepairWorldAction) -> set[StateId]:
        state = state_registry[state_id]
        if isinstance(action, ExternalAction):
            return {
                state_id_of(replace(state, y=y_next))
                for y_next in _external_support(config, state.y, action)
            }
        try:
            return {state_id_of(step(config, state, action))}
        except (DeferredActionError, UnlawfulActionError):
            return set()

    return viability_kernel_history(
        states,
        actions,
        feasible_actions,
        post_support,
        lambda state_id: safe(state_registry[state_id]),
    )


def repair_world_viability_kernel(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
    state_registry: Mapping[StateId, RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]],
    actions: Sequence[RepairWorldAction],
    safe: Callable[[RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]], bool],
    state_id_of: Callable[[RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]], StateId],
) -> set[StateId]:
    states = list(state_registry.keys())

    def feasible_actions(state_id: StateId) -> list[RepairWorldAction]:
        state = state_registry[state_id]
        return [
            action
            for action in actions
            if is_lawful_action(config, state, action).status is LawfulnessStatus.lawful
        ]

    def post_support(state_id: StateId, action: RepairWorldAction) -> set[StateId]:
        state = state_registry[state_id]
        if isinstance(action, ExternalAction):
            return {
                state_id_of(replace(state, y=y_next))
                for y_next in _external_support(config, state.y, action)
            }
        try:
            return {state_id_of(step(config, state, action))}
        except (DeferredActionError, UnlawfulActionError):
            return set()

    return viability_kernel(
        states,
        actions,
        feasible_actions,
        post_support,
        lambda state_id: safe(state_registry[state_id]),
    )


__all__ = [
    "AcquisitionAction",
    "AllocationAction",
    "ActionLawfulness",
    "AuditFlags",
    "AuditState",
    "AmbiguousActionError",
    "ChallengeClass",
    "ChallengeProcess",
    "CompilationStubAction",
    "DeferredActionError",
    "ExternalAction",
    "LawfulnessStatus",
    "MaintenanceAction",
    "MaintenanceStubAction",
    "OfflineToggleStubAction",
    "RepairAction",
    "RepairWorldAction",
    "RepairWorldConfig",
    "RepairWorldState",
    "RetirementAction",
    "UnlawfulActionError",
    "budget_vector",
    "is_lawful_action",
    "repair_world_viability_kernel",
    "repair_world_viability_kernel_history",
    "ring_kernel",
    "step",
]
