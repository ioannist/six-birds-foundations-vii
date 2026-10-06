"""E15 offline-reclosure sweep against the committed Round A predictions.

The fixture is a finite, single-carrier Repair-World instance.  Closure debt,
flow rates, budget geometry, exchange censuses, P2 gates, duty fractions, and
the eight-way status partition are recomputed from records.  Status selection
uses claim-scoped raw evidence in the Lean priority order; status tags never
serve as evidence that a higher-priority branch is absent.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Callable, Iterable

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordOccurrence,
    CarriedRecordPolicy,
    CheckRuleRecord,
    DeclaredTrajectory,
    FineSourceTag,
    carried_source,
)
from sixbirds_foundations_v.e_system import (
    ActiveCarriedInstrument,
    CarriedLedger,
    ESystem,
    RepairMove,
    RepairSort,
    TheoryPackage,
)
from sixbirds_foundations_v.probe_economy import (
    ActiveFamily,
    ProbeCatalog,
    ProbeEconomy,
    ProbeMove,
    ProbeMoveKind,
)
import sixbirds_foundations_v.sweeps.e14_reconsolidation_sweep as e14
import sixbirds_foundations_v.sweeps.e5_reclosure_collapse_sweep as e5
from sixbirds_foundations_v.worlds.repair_world import (
    AuditFlags,
    AuditState,
    ChallengeProcess,
    RepairAction,
    RepairWorldConfig,
    RepairWorldState,
    is_lawful_action,
    ring_kernel,
)
from sixbirds_foundations_v.xi.adequacy_residual import adequacyResidual
from sixbirds_foundations_v.xi.matrix import Mat


F = Fraction
CHALLENGE_CLASS = "C_reclosure"
ITEMS = ("a", "b", "c", "d")
E14_CTX = e14.ReconsolidationClassifierContext()

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E15_offline_reclosure_results.md"
)

REGISTERED_COMPARISON_ORDER = (
    "claim_alternation_required.status",
    "claim_online_sufficient.status",
    "claim_offline_optional.status",
    "claim_deficit_online_counterexample.status",
    "claim_decorative_exchange_active.status",
    "claim_decorative_no_discharge.status",
    "claim_decorative_bad_reallocation.status",
    "claim_duty_cycle_mismatch.status",
    "claim_skipped_offline_cascade.status",
    "claim_zero_exchange_without_p2.status",
    "ctrl_three_source_exact_aggregation",
    "ctrl_e14_direct_witness_required",
    "ctrl_f3_certificate_required",
    "ctrl_xi_posthoc_scalarization_rejected",
    "ctrl_xi_amount_without_matrix_rejected",
    "ctrl_duplicate_physical_ledger_charge",
    "ctrl_free_capacity_smuggling_rejected",
    "ctrl_capacity_gain_equation",
    "ctrl_gross_accrual_not_net_change",
    "sweep_deficit_boundary",
    "ctrl_incomplete_phase_flow_inventory",
    "ctrl_recurrence_uses_online_duration",
    "ctrl_posthoc_tolerance_rejected",
    "ctrl_claim_scoping",
    "ctrl_evidence_priority_not_status_tag",
    "ctrl_alarm_without_e7_acceptance",
    "ctrl_stress_without_e5_acceptance",
    "ctrl_cascade_chronology_lineage_mutations",
    "ctrl_e5_suspension_is_not_e15_offline",
    "ctrl_offline_overcapacity_is_decorative.status",
    "ctrl_exchange_census_omission",
    "ctrl_exchange_census_record_duplicate",
    "ctrl_exchange_census_id_duplicate",
    "ctrl_exchange_eligibility_soundness_matrix",
    "ctrl_shared_context_mutation_matrix",
    "ctrl_carriedness_conjunction_mutations",
    "ctrl_allocation_postdates_horizon",
    "ctrl_p2_gate_component_mutations",
    "ctrl_claim_match_key_mutations",
    "ctrl_debt_and_flow_duplicate_safety",
    "ctrl_online_discharge_capacity_bound",
    "census_offline_ablation_alarm_stress",
    "ctrl_eight_way_partition_and_top_exclusion",
    "ctrl_e14_wrong_canonical_status_rejected",
    "ctrl_offline_flow_off_inventory_rejected",
    "ctrl_discharge_out_of_phase_rejected",
)


class OperatingMode(str, Enum):
    online = "online"
    offline = "offline"


class ClosureDebtComponentKind(str, Enum):
    e14_reconsolidation = "e14_reconsolidation"
    f3_route_residue = "f3_route_residue"
    xi_adequacy_residual = "xi_adequacy_residual"


class OfflineReclosureStatus(str, Enum):
    deficit_online_counterexample = "deficit_online_counterexample"
    decorative_offline = "decorative_offline"
    duty_cycle_mismatch = "duty_cycle_mismatch"
    skipped_offline_cascade = "skipped_offline_cascade"
    alternation_required = "alternation_required"
    online_sufficient = "online_sufficient"
    offline_optional = "offline_optional"
    offline_reclosure_rejected = "offline_reclosure_rejected"
    unclassified = "unclassified"


STATUS_PRIORITY = (
    OfflineReclosureStatus.deficit_online_counterexample,
    OfflineReclosureStatus.decorative_offline,
    OfflineReclosureStatus.duty_cycle_mismatch,
    OfflineReclosureStatus.skipped_offline_cascade,
    OfflineReclosureStatus.alternation_required,
    OfflineReclosureStatus.online_sufficient,
    OfflineReclosureStatus.offline_optional,
    OfflineReclosureStatus.offline_reclosure_rejected,
)


@dataclass(frozen=True)
class CarriedFact:
    n0: int = 0
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True
    present: bool = True


CARRIED = CarriedFact()


@dataclass(frozen=True)
class ClosureDebtHorizonRecord:
    horizon_id: int
    start_time: Fraction
    end_time: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ClosureDebtScopeRecord:
    debt_claim_id: int
    challenge_class: str
    horizon: ClosureDebtHorizonRecord
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RouteResidueDebtRecord:
    residue_id: int
    route_residue: str
    reconciliation_claim_id: int
    recorded_at: Fraction
    residual_amount: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class XiResidualValuationPolicyRecord:
    valuation_policy_id: int
    declared_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class XiAdequacyResidualDebtRecord:
    residual_id: int
    C: Mat | None
    L: Mat | None
    D: Mat | None
    KLLdagger: Mat | None
    residual_matrix: Mat | None
    valuation_policy: XiResidualValuationPolicyRecord
    reconciliation_claim_id: int
    recorded_at: Fraction
    residual_amount: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class E14ResidualRegistrationRecord:
    registration_id: int
    residual_record: e14.ReconsolidationResidualRecord
    registered_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class E14ResidualDebtSource:
    candidate: e14.StatusedUnresolvedCandidate
    registration_record: E14ResidualRegistrationRecord
    source_formation: e14.MemoryRecordFormationRecord
    claim_ref: e14.ReconsolidationClaimRef
    disposition_inventory: e14.CompleteReconsolidationDispositionInventory
    status_record: e14.ReconsolidationStatusRecord


@dataclass(frozen=True)
class LedgerEntry:
    ledger_entry_id: int
    source_id: int
    amount: Fraction
    label: str
    carried: CarriedFact = CARRIED

    @property
    def residual_id(self) -> int:
        """E14's native ledger interface names the same source key residual_id."""
        return self.source_id


@dataclass(frozen=True)
class SharedBudgetAllocationRecord:
    allocation_id: int
    scope: ClosureDebtScopeRecord
    declared_at: Fraction
    online_external_allocation: Fraction
    online_internal_discharge_allocation: Fraction
    offline_external_allocation: Fraction
    offline_internal_discharge_allocation: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ExposureBudgetWitness:
    spend: Fraction
    budget: Fraction
    budget_entry: LedgerEntry
    spend_entry: LedgerEntry
    move: ProbeMove[str, str]


@dataclass(frozen=True)
class OperatingPhaseRecord:
    phase_id: int
    scope: ClosureDebtScopeRecord
    allocation_record: SharedBudgetAllocationRecord
    mode: OperatingMode
    start_time: Fraction
    end_time: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class DeclaredOperatingSchedule:
    schedule_id: int
    scope: ClosureDebtScopeRecord
    phases: tuple[OperatingPhaseRecord, ...]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ExternalExchangeRecord:
    exchange_record_id: int
    phase_record: OperatingPhaseRecord
    exchanged_amount: Fraction
    recorded_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ExchangeGateRecord:
    gate_record_id: int
    phase_record: OperatingPhaseRecord
    action: RepairAction[str, str, str, str]
    sort: RepairSort
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class DutyCycleToleranceRecord:
    tolerance_id: int
    scope: ClosureDebtScopeRecord
    declared_at: Fraction
    tolerance: Fraction
    carried: CarriedFact = CARRIED

    def __post_init__(self) -> None:
        if self.tolerance < 0:
            raise ValueError("tolerance must be nonnegative")


@dataclass(frozen=True)
class OfflineRecurrenceBoundRecord:
    recurrence_bound_id: int
    scope: ClosureDebtScopeRecord
    declared_at: Fraction
    maximum_online_run: Fraction
    carried: CarriedFact = CARRIED

    def __post_init__(self) -> None:
        if self.maximum_online_run <= 0:
            raise ValueError("maximum_online_run must be positive")


@dataclass(frozen=True)
class DebtBoundRecord:
    bound_id: int
    scope: ClosureDebtScopeRecord
    declared_at: Fraction
    upper_bound: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class E7AlarmCascadeObservation:
    observation_id: int
    scope: ClosureDebtScopeRecord
    phase_record: OperatingPhaseRecord
    observed_at: Fraction
    disposition_kind: str
    discount_reason: str | None
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class E5StressCascadeObservation:
    observation_id: int
    scope: ClosureDebtScopeRecord
    phase_record: OperatingPhaseRecord
    observed_at: Fraction
    status: str
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ClosureDebtEntryRecord:
    kind: ClosureDebtComponentKind
    source: E14ResidualDebtSource | RouteResidueDebtRecord | XiAdequacyResidualDebtRecord
    ledger_entry: LedgerEntry

    def __post_init__(self) -> None:
        expected = {
            ClosureDebtComponentKind.e14_reconsolidation: E14ResidualDebtSource,
            ClosureDebtComponentKind.f3_route_residue: RouteResidueDebtRecord,
            ClosureDebtComponentKind.xi_adequacy_residual: XiAdequacyResidualDebtRecord,
        }[self.kind]
        if not isinstance(self.source, expected):
            raise TypeError(f"{self.kind.value} entry has the wrong source record type")

    @property
    def amount(self) -> Fraction:
        if self.kind is ClosureDebtComponentKind.e14_reconsolidation:
            if not isinstance(self.source, E14ResidualDebtSource):
                raise TypeError("E14 debt entry lacks an E14 source")
            return self.source.candidate.residual_record.residual_amount
        return self.source.residual_amount

    @property
    def key(self) -> tuple[ClosureDebtComponentKind, int]:
        if self.kind is ClosureDebtComponentKind.e14_reconsolidation:
            if not isinstance(self.source, E14ResidualDebtSource):
                raise TypeError("E14 debt entry lacks an E14 source")
            source_id = self.source.candidate.residual_record.residual_id
        else:
            source_id = self.source.residue_id if isinstance(
                self.source, RouteResidueDebtRecord
            ) else self.source.residual_id
        return (self.kind, source_id)


@dataclass(frozen=True)
class ClosureDebtSnapshotRecord:
    snapshot_id: int
    scope: ClosureDebtScopeRecord
    observed_at: Fraction
    entries: tuple[ClosureDebtEntryRecord, ...]
    total_debt: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class DebtDischargeRecord:
    discharge_id: int
    phase_record: OperatingPhaseRecord
    debt_entry: ClosureDebtEntryRecord
    amount: Fraction
    discharged_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ClosureDebtFlowRecord:
    flow_id: int
    phase_record: OperatingPhaseRecord
    before_snapshot: ClosureDebtSnapshotRecord
    after_snapshot: ClosureDebtSnapshotRecord
    accrued_entries: tuple[ClosureDebtEntryRecord, ...]
    discharge_records: tuple[DebtDischargeRecord, ...]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class OfflineReclosureClaimRef:
    scope: ClosureDebtScopeRecord
    allocation_record: SharedBudgetAllocationRecord
    schedule: DeclaredOperatingSchedule
    tolerance_record: DutyCycleToleranceRecord
    recurrence_bound: OfflineRecurrenceBoundRecord


@dataclass(frozen=True)
class OfflineReclosureStatusRecord:
    status_record_id: int
    status: OfflineReclosureStatus
    scope: ClosureDebtScopeRecord
    allocation_record: SharedBudgetAllocationRecord
    schedule: DeclaredOperatingSchedule
    tolerance_record: DutyCycleToleranceRecord
    recurrence_bound: OfflineRecurrenceBoundRecord
    phase_record: OperatingPhaseRecord | None = None
    alarm_observation: E7AlarmCascadeObservation | None = None
    stress_observation: E5StressCascadeObservation | None = None
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ClaimData:
    name: str
    fixture_index: int
    scope: ClosureDebtScopeRecord
    allocation: SharedBudgetAllocationRecord
    budget_data: ExposureBudgetWitness
    schedule: DeclaredOperatingSchedule
    tolerance: DutyCycleToleranceRecord
    recurrence_bound: OfflineRecurrenceBoundRecord
    flows: tuple[ClosureDebtFlowRecord, ...]
    exchange_records: tuple[ExternalExchangeRecord, ...]
    gates: tuple[ExchangeGateRecord, ...]
    debt_bound: DebtBoundRecord | None
    alarm_observation: E7AlarmCascadeObservation | None
    stress_observation: E5StressCascadeObservation | None
    status_record: OfflineReclosureStatusRecord | None

    @property
    def claim_ref(self) -> OfflineReclosureClaimRef:
        return OfflineReclosureClaimRef(
            self.scope,
            self.allocation,
            self.schedule,
            self.tolerance,
            self.recurrence_bound,
        )


@dataclass(frozen=True)
class RepairWorldCarrier:
    config: RepairWorldConfig
    state: RepairWorldState
    lambda_entries: tuple[LedgerEntry, ...]


@dataclass(frozen=True)
class OfflineReclosureClassifierContext:
    e14_outstanding_registry: frozenset[tuple[int, Fraction]]
    f3_awaiting_registry: frozenset[tuple[int, Fraction]]
    accepted_xi_policy_ids: frozenset[int]
    xi_awaiting_registry: frozenset[tuple[int, Fraction]]
    accepted_external_gate_ids: frozenset[int]
    external_channel_by_gate: tuple[tuple[int, str], ...]
    accepted_e7_alarm_ids: frozenset[int]
    accepted_e5_stress_ids: frozenset[int]

    def e14_residual_outstanding(
        self, registration: E14ResidualRegistrationRecord, as_of: Fraction
    ) -> bool:
        return (registration.registration_id, as_of) in self.e14_outstanding_registry

    def f3_route_residue_awaiting_reconciliation(
        self, residue: RouteResidueDebtRecord, as_of: Fraction
    ) -> bool:
        return (residue.residue_id, as_of) in self.f3_awaiting_registry

    def xi_valuation_policy_accepted(
        self, policy: XiResidualValuationPolicyRecord
    ) -> bool:
        return policy.valuation_policy_id in self.accepted_xi_policy_ids

    def xi_residual_amount(
        self, policy: XiResidualValuationPolicyRecord, matrix: Mat
    ) -> Fraction:
        if policy.valuation_policy_id not in self.accepted_xi_policy_ids:
            return F(0)
        return sum((sum(row, F(0)) for row in matrix), F(0))

    def xi_residual_awaiting_discharge(
        self, residual: XiAdequacyResidualDebtRecord, as_of: Fraction
    ) -> bool:
        return (residual.residual_id, as_of) in self.xi_awaiting_registry

    def ledger_entry_charges_route_residue(
        self,
        entry: LedgerEntry,
        residue: RouteResidueDebtRecord,
        amount: Fraction,
    ) -> bool:
        return (
            entry.label == "f3-route-residue"
            and entry.source_id == residue.residue_id
            and entry.amount == amount
            and amount > 0
        )

    def ledger_entry_charges_xi_residual(
        self,
        entry: LedgerEntry,
        residual: XiAdequacyResidualDebtRecord,
        amount: Fraction,
    ) -> bool:
        return (
            entry.label == "xi-adequacy-residual"
            and entry.source_id == residual.residual_id
            and entry.amount == amount
            and amount > 0
        )

    def gate_closes_external_exchange(self, gate: ExchangeGateRecord) -> bool:
        return (
            gate.gate_record_id in self.accepted_external_gate_ids
            and dict(self.external_channel_by_gate).get(gate.gate_record_id)
            == "external_exchange"
        )

    def e7_alarm_observation_accepted(
        self, observation: E7AlarmCascadeObservation
    ) -> bool:
        return (
            observation.observation_id in self.accepted_e7_alarm_ids
            and observation.disposition_kind == "statused"
            and observation.discount_reason == "closure_debt"
        )

    def e5_stress_observation_accepted(
        self, observation: E5StressCascadeObservation
    ) -> bool:
        return (
            observation.observation_id in self.accepted_e5_stress_ids
            and observation.status == "stressed"
        )


@dataclass(frozen=True)
class Fixture:
    carrier: RepairWorldCarrier
    ctx: OfflineReclosureClassifierContext
    claims: dict[str, ClaimData]
    eligible_debt_entries: dict[tuple[int, Fraction], tuple[ClosureDebtEntryRecord, ...]]
    eligible_exchanges: dict[int, tuple[ExternalExchangeRecord, ...]]
    e14_formation_registry: dict[int, e14.CarriedMemoryRecord]
    e14_transport_registry: dict[int, e14.RetrievalTransportRecord]


@dataclass(frozen=True)
class StatusRow:
    name: str
    observed: OfflineReclosureStatus
    truths: dict[OfflineReclosureStatus, bool]
    status_record: OfflineReclosureStatusRecord | None


@dataclass(frozen=True)
class ControlRow:
    name: str
    expected: str
    observed: str
    passed_control: bool


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    rows: dict[str, StatusRow]
    controls: dict[str, ControlRow]
    comparisons: tuple[Comparison, ...]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool


def _record_carried(record: object) -> bool:
    fact = getattr(record, "carried", None)
    return (
        isinstance(fact, (CarriedFact, e14.CarriedFact))
        and fact.present
        and carried_source(fact.source_tag, fact.generated_by_s, fact.in_scope)
    )


def closure_debt(entries: Iterable[ClosureDebtEntryRecord]) -> Fraction:
    return sum((entry.amount for entry in entries), F(0))


def accrued_debt(flow: ClosureDebtFlowRecord) -> Fraction:
    return closure_debt(flow.accrued_entries)


def discharged_debt(flow: ClosureDebtFlowRecord) -> Fraction:
    return sum((record.amount for record in flow.discharge_records), F(0))


def phase_duration(phase: OperatingPhaseRecord) -> Fraction:
    return phase.end_time - phase.start_time


def closure_debt_accrual_rate(flow: ClosureDebtFlowRecord) -> Fraction:
    return accrued_debt(flow) / phase_duration(flow.phase_record)


def closure_debt_discharge_rate(flow: ClosureDebtFlowRecord) -> Fraction:
    return discharged_debt(flow) / phase_duration(flow.phase_record)


def total_duration(schedule: DeclaredOperatingSchedule) -> Fraction:
    return sum((phase_duration(phase) for phase in schedule.phases), F(0))


def offline_duration(schedule: DeclaredOperatingSchedule) -> Fraction:
    return sum(
        (
            phase_duration(phase)
            for phase in schedule.phases
            if phase.mode is OperatingMode.offline
        ),
        F(0),
    )


def observed_offline_duty(schedule: DeclaredOperatingSchedule) -> Fraction:
    return offline_duration(schedule) / total_duration(schedule)


def kappa_on(allocation: SharedBudgetAllocationRecord) -> Fraction:
    return allocation.online_internal_discharge_allocation


def freed_allocation(allocation: SharedBudgetAllocationRecord) -> Fraction:
    return allocation.online_external_allocation


def kappa_off(allocation: SharedBudgetAllocationRecord) -> Fraction:
    return allocation.offline_internal_discharge_allocation


def predicted_offline_duty(
    accrual_rate: Fraction, allocation: SharedBudgetAllocationRecord
) -> Fraction:
    deficit = accrual_rate - kappa_on(allocation)
    return deficit / (deficit + kappa_off(allocation))


def declared_operating_schedule(schedule: DeclaredOperatingSchedule) -> bool:
    phases = schedule.phases
    return (
        _record_carried(schedule)
        and bool(phases)
        and len(set(phases)) == len(phases)
        and all(_record_carried(phase) for phase in phases)
        and all(phase.scope == schedule.scope for phase in phases)
        and all(phase.start_time < phase.end_time for phase in phases)
        and phases[0].start_time == schedule.scope.horizon.start_time
        and phases[-1].end_time == schedule.scope.horizon.end_time
        and all(left.end_time == right.start_time for left, right in zip(phases, phases[1:]))
    )


def _e14_status_fixture(
    fixture: Fixture, source: E14ResidualDebtSource
) -> e14.Fixture:
    candidate = source.candidate
    trigger = candidate.trigger
    family = trigger.family
    transports = trigger.inventory.declared_transports
    dispositions = source.disposition_inventory.declared_dispositions
    return e14.Fixture(
        carrier=fixture.carrier,
        ctx=E14_CTX,
        claims={trigger.source_record.claim_record.name: trigger.source_record.claim_record},
        memory_records={
            trigger.source_record.name: trigger.source_record,
            candidate.current_record_at_status.name: candidate.current_record_at_status,
        },
        formations={
            source.source_formation.name: source.source_formation,
            candidate.formation_record.name: candidate.formation_record,
        },
        quotients={
            transport.current_quotient.name: transport.current_quotient
            for transport in transports
        },
        contexts={context.name: context for context in family.contexts},
        families={family.name: family},
        transports={transport.name: transport for transport in transports},
        retrieval_inventories={trigger.inventory.name: trigger.inventory},
        conflicts={trigger.conflict_record.name: trigger.conflict_record},
        triggers={trigger.name: trigger},
        repair_packages={},
        mutations={},
        distinction_audits={},
        provenances={},
        provenance_audits={},
        residuals={candidate.residual_record.name: candidate.residual_record},
        ledger_entries={str(candidate.ledger_entry.residual_id): candidate.ledger_entry},
        dispositions={disposition.name: disposition for disposition in dispositions},
        disposition_inventories={trigger.name: source.disposition_inventory},
        repair_candidates={},
        coarsening_candidates={},
        unresolved_candidates={candidate.name: candidate},
        outcome_inventories={},
        silent_candidates={},
        provenance_defect_candidates={},
        reconsolidation_claims={source.claim_ref.name: source.claim_ref},
        status_records={source.status_record.name: source.status_record},
        formation_registry=fixture.e14_formation_registry,
        transport_registry=fixture.e14_transport_registry,
        record_quotient_links=frozenset(),
        unsupported_pairs={},
        f9_registry={
            trigger.conflict_record.conflict_id: dispositions[0].disposition_id
        }
        if len(dispositions) == 1
        else {},
        coarsening_install_registry=frozenset(),
        strata=(),
    )


def _actual_e14_trigger(
    fixture: Fixture, debt_source: E14ResidualDebtSource
) -> bool:
    candidate = debt_source.candidate
    trigger = candidate.trigger
    source_record = trigger.source_record
    family = trigger.family
    inventory = trigger.inventory
    conflict = trigger.conflict_record
    transports = inventory.declared_transports
    return (
        _record_carried(source_record)
        and _record_carried(source_record.claim_record)
        and _record_carried(family)
        and _record_carried(debt_source.source_formation)
        and debt_source.source_formation.memory_record == trigger.source_record
        and fixture.e14_formation_registry.get(debt_source.source_formation.formation_id)
        == trigger.source_record
        and len(family.contexts) >= 2
        and len(set(family.contexts)) == len(family.contexts)
        and all(_record_carried(context) for context in family.contexts)
        and inventory.source_record == source_record
        and inventory.family == family
        and all(
            _record_carried(transport)
            and transport.source_record == source_record
            and transport.context_record in family.contexts
            and fixture.e14_transport_registry.get(transport.transport_id)
            == transport
            for transport in transports
        )
        and all(
            any(transport.context_record == context for transport in transports)
            for context in family.contexts
        )
        and all(
            first.context_record != second.context_record
            or first.transported_record == second.transported_record
            for first in transports
            for second in transports
        )
        and any(
            first.context_record != second.context_record
            and first.transported_record != second.transported_record
            for first in transports
            for second in transports
        )
        and _record_carried(conflict)
        and conflict.source_record == source_record
        and conflict.claim_record == source_record.claim_record
        and conflict.transport_record in transports
        and bool(e14.delta_set(conflict.transport_record, conflict.claim_record))
    )


def actual_e14_statused_unresolved(
    fixture: Fixture, source: E14ResidualDebtSource
) -> bool:
    candidate = source.candidate
    trigger = candidate.trigger
    current = candidate.current_record_at_status
    original = trigger.source_record
    residual = candidate.residual_record
    entry = candidate.ledger_entry
    registration = source.registration_record
    claim = source.claim_ref
    status_record = source.status_record
    native_fixture = _e14_status_fixture(fixture, source)
    return (
        _actual_e14_trigger(fixture, source)
        and claim.source_record == original
        and claim.family == trigger.family
        and claim.transport_record == trigger.conflict_record.transport_record
        and claim.context_record == trigger.conflict_record.transport_record.context_record
        and claim.claim_record == original.claim_record
        and status_record.residual_record == residual
        and e14.reconsolidation_status_occurrence_for(claim, status_record)
        and status_record.status is e14.ReconsolidationStatus.statused_unresolved
        and e14.statused_unresolved_case(native_fixture, claim, status_record)
        and _record_carried(current)
        and _record_carried(current.claim_record)
        and _record_carried(candidate.formation_record)
        and candidate.formation_record.memory_record == current
        and fixture.e14_formation_registry.get(candidate.formation_record.formation_id)
        == current
        and current.record_id == original.record_id
        and current.claim_record == original.claim_record
        and current.version == original.version
        and current.provenance_root_id == original.provenance_root_id
        and current.record_value == original.record_value
        and _record_carried(residual)
        and residual.conflict_record == trigger.conflict_record
        and residual.residual_amount > 0
        and entry in fixture.carrier.lambda_entries
        and _record_carried(entry)
        and entry.source_id == residual.residual_id
        and entry.amount == residual.residual_amount
        and entry.label == "reconsolidation-residual"
        and registration.residual_record == residual
    )


def e14_residual_debt_item(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    as_of: Fraction,
    entry: ClosureDebtEntryRecord,
) -> bool:
    if entry.kind is not ClosureDebtComponentKind.e14_reconsolidation:
        return False
    source = entry.source
    if not isinstance(source, E14ResidualDebtSource):
        return False
    candidate = source.candidate
    registration = source.registration_record
    return (
        actual_e14_statused_unresolved(fixture, source)
        and _record_carried(registration)
        and registration.residual_record == candidate.residual_record
        and registration.registered_at <= as_of
        and fixture.ctx.e14_residual_outstanding(registration, as_of)
        and scope.horizon.start_time <= as_of <= scope.horizon.end_time
        and candidate.residual_record.conflict_record == candidate.trigger.conflict_record
        and candidate.residual_record.conflict_record.claim_record.claim_id
        == scope.debt_claim_id
        and entry.ledger_entry == candidate.ledger_entry
    )


def f3_route_residue_debt_item(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    as_of: Fraction,
    entry: ClosureDebtEntryRecord,
) -> bool:
    if entry.kind is not ClosureDebtComponentKind.f3_route_residue:
        return False
    residue = entry.source
    if not isinstance(residue, RouteResidueDebtRecord):
        return False
    return (
        _record_carried(residue)
        and residue.residual_amount > 0
        and residue.reconciliation_claim_id == scope.debt_claim_id
        and residue.recorded_at <= as_of
        and scope.horizon.start_time <= as_of <= scope.horizon.end_time
        and fixture.ctx.f3_route_residue_awaiting_reconciliation(residue, as_of)
        and entry.ledger_entry in fixture.carrier.lambda_entries
        and _record_carried(entry.ledger_entry)
        and fixture.ctx.ledger_entry_charges_route_residue(
            entry.ledger_entry, residue, residue.residual_amount
        )
    )


def xi_adequacy_residual_debt_item(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    as_of: Fraction,
    entry: ClosureDebtEntryRecord,
) -> bool:
    if entry.kind is not ClosureDebtComponentKind.xi_adequacy_residual:
        return False
    residual = entry.source
    if not isinstance(residual, XiAdequacyResidualDebtRecord):
        return False
    matrices_present = all(
        matrix is not None
        for matrix in (residual.C, residual.L, residual.D, residual.KLLdagger, residual.residual_matrix)
    )
    computed = (
        matrices_present
        and residual.residual_matrix
        == adequacyResidual(residual.C, residual.L, residual.D, residual.KLLdagger)
    )
    return (
        _record_carried(residual.valuation_policy)
        and residual.valuation_policy.declared_at <= scope.horizon.start_time
        and fixture.ctx.xi_valuation_policy_accepted(residual.valuation_policy)
        and _record_carried(residual)
        and computed
        and residual.residual_matrix is not None
        and residual.residual_amount
        == fixture.ctx.xi_residual_amount(
            residual.valuation_policy, residual.residual_matrix
        )
        and residual.residual_amount > 0
        and residual.reconciliation_claim_id == scope.debt_claim_id
        and residual.recorded_at <= as_of
        and scope.horizon.start_time <= as_of <= scope.horizon.end_time
        and fixture.ctx.xi_residual_awaiting_discharge(residual, as_of)
        and entry.ledger_entry in fixture.carrier.lambda_entries
        and _record_carried(entry.ledger_entry)
        and fixture.ctx.ledger_entry_charges_xi_residual(
            entry.ledger_entry, residual, residual.residual_amount
        )
    )


def debt_entry_sound(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    as_of: Fraction,
    entry: ClosureDebtEntryRecord,
) -> bool:
    return (
        e14_residual_debt_item(fixture, scope, as_of, entry)
        or f3_route_residue_debt_item(fixture, scope, as_of, entry)
        or xi_adequacy_residual_debt_item(fixture, scope, as_of, entry)
    )


def complete_closure_debt_inventory_checks(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    as_of: Fraction,
    entries: tuple[ClosureDebtEntryRecord, ...],
) -> dict[str, bool]:
    eligible = fixture.eligible_debt_entries.get((scope.debt_claim_id, as_of), ())
    return {
        "keysNodup": len({entry.key for entry in entries}) == len(entries),
        "ledgerChargesNodup": len({entry.ledger_entry for entry in entries})
        == len(entries),
        "sound": all(debt_entry_sound(fixture, scope, as_of, entry) for entry in entries),
        "coverage": all(entry in entries for entry in eligible)
        and all(entry in eligible for entry in entries),
    }


def complete_closure_debt_inventory(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    as_of: Fraction,
    entries: tuple[ClosureDebtEntryRecord, ...],
) -> bool:
    return all(complete_closure_debt_inventory_checks(fixture, scope, as_of, entries).values())


def complete_closure_debt_snapshot(
    fixture: Fixture, snapshot: ClosureDebtSnapshotRecord
) -> bool:
    return (
        _record_carried(snapshot)
        and snapshot.scope.horizon.start_time
        <= snapshot.observed_at
        <= snapshot.scope.horizon.end_time
        and complete_closure_debt_inventory(
            fixture, snapshot.scope, snapshot.observed_at, snapshot.entries
        )
        and snapshot.total_debt == closure_debt(snapshot.entries)
    )


def complete_closure_debt_flow_checks(
    fixture: Fixture, flow: ClosureDebtFlowRecord
) -> dict[str, bool]:
    accrued_keys = tuple(entry.key for entry in flow.accrued_entries)
    discharge_ids = tuple(record.discharge_id for record in flow.discharge_records)
    discharged_entries = tuple(record.debt_entry for record in flow.discharge_records)
    before = flow.before_snapshot.entries
    after = flow.after_snapshot.entries
    return {
        "flowCarried": _record_carried(flow),
        "beforeComplete": complete_closure_debt_snapshot(fixture, flow.before_snapshot),
        "afterComplete": complete_closure_debt_snapshot(fixture, flow.after_snapshot),
        "phaseLinked": flow.before_snapshot.observed_at == flow.phase_record.start_time
        and flow.after_snapshot.observed_at == flow.phase_record.end_time,
        "accruedEntriesNodup": len(set(accrued_keys)) == len(accrued_keys),
        "dischargesNodup": len(set(discharge_ids)) == len(discharge_ids),
        "dischargedEntriesNodup": len(set(discharged_entries)) == len(discharged_entries),
        "everyAccrualNew": all(entry not in before and entry in after for entry in flow.accrued_entries),
        "everyNewEntryCovered": all(
            entry in before or entry in flow.accrued_entries for entry in after
        ),
        "everyDischargeCarried": all(_record_carried(record) for record in flow.discharge_records),
        "everyDischargeLinked": all(
            record.phase_record == flow.phase_record
            and record.phase_record.start_time
            <= record.discharged_at
            <= record.phase_record.end_time
            and record.debt_entry in before
            and record.amount > 0
            and record.amount == record.debt_entry.amount
            and record.debt_entry not in after
            for record in flow.discharge_records
        ),
        "balanceEquation": flow.after_snapshot.total_debt
        == flow.before_snapshot.total_debt + accrued_debt(flow) - discharged_debt(flow),
    }


def complete_closure_debt_flow(fixture: Fixture, flow: ClosureDebtFlowRecord) -> bool:
    return all(complete_closure_debt_flow_checks(fixture, flow).values())


def derived_offline_budget_geometry(
    fixture: Fixture,
    scope: ClosureDebtScopeRecord,
    budget_data: ExposureBudgetWitness | None,
    allocation: SharedBudgetAllocationRecord | None,
) -> bool:
    if budget_data is None or allocation is None:
        return False
    return (
        _record_carried(allocation)
        and allocation.scope == scope
        and allocation.declared_at <= scope.horizon.start_time
        and budget_data.spend <= budget_data.budget
        and budget_data.spend == budget_data.budget
        and budget_data.budget_entry in fixture.carrier.lambda_entries
        and budget_data.spend_entry in fixture.carrier.lambda_entries
        and _record_carried(budget_data.budget_entry)
        and _record_carried(budget_data.spend_entry)
        and fixture.carrier.config.probe_economy.exposure_budget_entry(
            budget_data.budget_entry, budget_data.budget
        )
        and fixture.carrier.config.probe_economy.exposure_spend_entry(
            budget_data.spend_entry, budget_data.spend
        )
        and fixture.carrier.config.probe_economy.budget_admissible(budget_data.move)
        and allocation.online_external_allocation > 0
        and allocation.online_internal_discharge_allocation >= 0
        and allocation.online_external_allocation
        + allocation.online_internal_discharge_allocation
        == budget_data.budget
        and allocation.offline_external_allocation == 0
        and allocation.offline_internal_discharge_allocation
        == allocation.online_internal_discharge_allocation
        + allocation.online_external_allocation
        and allocation.offline_external_allocation
        + allocation.offline_internal_discharge_allocation
        == budget_data.budget
    )


def phase_flow_inventory_checks(
    fixture: Fixture,
    data: ClaimData,
    flows: tuple[ClosureDebtFlowRecord, ...] | None = None,
) -> dict[str, bool]:
    inventory = data.flows if flows is None else flows
    return {
        "everyPhaseCarried": all(_record_carried(phase) for phase in data.schedule.phases),
        "everyPhaseCovered": all(
            sum(flow.phase_record == phase and complete_closure_debt_flow(fixture, flow) for flow in inventory)
            == 1
            for phase in data.schedule.phases
        ),
        "flowSingleValuedPerPhase": all(
            first.phase_record != second.phase_record or first == second
            for first in inventory
            for second in inventory
        ),
        "noForeignFlows": all(flow.phase_record in data.schedule.phases for flow in inventory),
    }


def complete_phase_flow_inventory(
    fixture: Fixture,
    data: ClaimData,
    flows: tuple[ClosureDebtFlowRecord, ...] | None = None,
) -> bool:
    return all(phase_flow_inventory_checks(fixture, data, flows).values())


def eligible_external_exchange(
    data: ClaimData, record: ExternalExchangeRecord
) -> bool:
    return (
        _record_carried(record)
        and record.phase_record in data.schedule.phases
        and record.exchanged_amount >= 0
        and record.phase_record.start_time
        <= record.recorded_at
        <= record.phase_record.end_time
    )


def external_exchange_inventory_checks(
    fixture: Fixture,
    data: ClaimData,
    records: tuple[ExternalExchangeRecord, ...] | None = None,
) -> dict[str, bool]:
    inventory = data.exchange_records if records is None else records
    eligible = fixture.eligible_exchanges.get(data.schedule.schedule_id, ())
    return {
        "recordsNodup": len(set(inventory)) == len(inventory),
        "recordIdsNodup": len({record.exchange_record_id for record in inventory})
        == len(inventory),
        "completeForSchedule": all(record in inventory for record in eligible),
        "soundForSchedule": all(eligible_external_exchange(data, record) for record in inventory),
        "everyPhaseCovered": all(
            any(record.phase_record == phase for record in inventory)
            for phase in data.schedule.phases
        ),
    }


def complete_external_exchange_inventory(
    fixture: Fixture,
    data: ClaimData,
    records: tuple[ExternalExchangeRecord, ...] | None = None,
) -> bool:
    return all(external_exchange_inventory_checks(fixture, data, records).values())


def exchange_in_phase(
    records: tuple[ExternalExchangeRecord, ...], phase: OperatingPhaseRecord
) -> Fraction:
    return sum(
        (record.exchanged_amount for record in records if record.phase_record == phase),
        F(0),
    )


def p2_external_exchange_gate_evidence(
    fixture: Fixture, phase: OperatingPhaseRecord, gate: ExchangeGateRecord
) -> bool:
    generated = fixture.carrier.config.e_system.R_S(gate.action.defect)
    return (
        _record_carried(gate)
        and gate.phase_record == phase
        and generated.payload == gate.action.repair_package
        and generated.sort is RepairSort.P2
        and gate.sort is RepairSort.P2
        and is_lawful_action(
            fixture.carrier.config, fixture.carrier.state, gate.action
        ).is_lawful
        and fixture.ctx.gate_closes_external_exchange(gate)
    )


def _flow_for_phase(data: ClaimData, phase: OperatingPhaseRecord) -> ClosureDebtFlowRecord | None:
    matching = tuple(flow for flow in data.flows if flow.phase_record == phase)
    return matching[0] if len(matching) == 1 else None


def persistent_deficit_noncapacity_checks(
    fixture: Fixture, data: ClaimData
) -> dict[str, bool]:
    online = tuple(phase for phase in data.schedule.phases if phase.mode is OperatingMode.online)
    rates = tuple(
        closure_debt_accrual_rate(flow)
        for phase in online
        if (flow := _flow_for_phase(data, phase)) is not None
    )
    return {
        "geometry": derived_offline_budget_geometry(
            fixture, data.scope, data.budget_data, data.allocation
        ),
        "scheduleCarriedAndDeclared": declared_operating_schedule(data.schedule),
        "flowInventory": complete_phase_flow_inventory(fixture, data),
        "everyPhaseUsesClaimAllocation": all(
            phase.allocation_record == data.allocation
            for phase in data.schedule.phases
        ),
        "onlinePhaseExists": bool(online),
        "everyOnlineRateLinked": len(rates) == len(online)
        and bool(rates)
        and len(set(rates)) == 1,
        "persistentDeficit": bool(rates)
        and kappa_on(data.allocation) < rates[0],
    }


def persistent_deficit_evidence(fixture: Fixture, data: ClaimData) -> bool:
    online = tuple(
        phase for phase in data.schedule.phases if phase.mode is OperatingMode.online
    )
    return all(persistent_deficit_noncapacity_checks(fixture, data).values()) and all(
        (flow := _flow_for_phase(data, phase)) is not None
        and closure_debt_discharge_rate(flow) <= kappa_on(data.allocation)
        for phase in online
    )


def genuine_offline_flow_evidence(
    fixture: Fixture,
    data: ClaimData,
    phase: OperatingPhaseRecord,
    flow: ClosureDebtFlowRecord,
) -> bool:
    gates = tuple(gate for gate in data.gates if gate.phase_record == phase)
    return (
        derived_offline_budget_geometry(fixture, data.scope, data.budget_data, data.allocation)
        and complete_phase_flow_inventory(fixture, data)
        and complete_external_exchange_inventory(fixture, data)
        and phase in data.schedule.phases
        and phase.mode is OperatingMode.offline
        and _record_carried(phase)
        and flow in data.flows
        and flow.phase_record == phase
        and _record_carried(flow)
        and complete_closure_debt_flow(fixture, flow)
        and phase.allocation_record == data.allocation
        and len(gates) == 1
        and p2_external_exchange_gate_evidence(fixture, phase, gates[0])
        and exchange_in_phase(data.exchange_records, phase) == 0
        and discharged_debt(flow) > 0
        and flow.after_snapshot.total_debt < flow.before_snapshot.total_debt
        and closure_debt_discharge_rate(flow) <= kappa_off(data.allocation)
        and phase.allocation_record.offline_internal_discharge_allocation
        == kappa_off(data.allocation)
    )


def genuine_offline_phase_evidence(
    fixture: Fixture, data: ClaimData, phase: OperatingPhaseRecord
) -> bool:
    flow = _flow_for_phase(data, phase)
    return flow is not None and genuine_offline_flow_evidence(
        fixture, data, phase, flow
    )


def alternating_offline_substrate(fixture: Fixture, data: ClaimData) -> bool:
    phases = data.schedule.phases
    offline = tuple(phase for phase in phases if phase.mode is OperatingMode.offline)
    online = tuple(phase for phase in phases if phase.mode is OperatingMode.online)
    return (
        persistent_deficit_evidence(fixture, data)
        and complete_external_exchange_inventory(fixture, data)
        and _record_carried(data.recurrence_bound)
        and data.recurrence_bound.scope == data.scope
        and data.recurrence_bound.declared_at <= data.scope.horizon.start_time
        and len(offline) >= 2
        and phases[0].mode is OperatingMode.online
        and all(left.mode is not right.mode for left, right in zip(phases, phases[1:]))
        and all(exchange_in_phase(data.exchange_records, phase) > 0 for phase in online)
        and all(
            (flow := _flow_for_phase(data, phase)) is not None
            and closure_debt_discharge_rate(flow) == kappa_on(data.allocation)
            for phase in online
        )
        and all(genuine_offline_phase_evidence(fixture, data, phase) for phase in offline)
        and all(
            (flow := _flow_for_phase(data, phase)) is not None
            and closure_debt_discharge_rate(flow) == kappa_off(data.allocation)
            and accrued_debt(flow) == 0
            for phase in offline
        )
        and all(
            phase_duration(phase) <= data.recurrence_bound.maximum_online_run
            and any(
                later.mode is OperatingMode.offline
                and phase.end_time <= later.start_time
                for later in phases
            )
            for phase in online
        )
    )


def duty_cycle_prediction_evidence(fixture: Fixture, data: ClaimData) -> bool:
    online = tuple(phase for phase in data.schedule.phases if phase.mode is OperatingMode.online)
    if not online:
        return False
    flow = _flow_for_phase(data, online[0])
    if flow is None:
        return False
    return (
        alternating_offline_substrate(fixture, data)
        and _record_carried(data.tolerance)
        and data.tolerance.scope == data.scope
        and data.tolerance.declared_at <= data.scope.horizon.start_time
        and abs(
            observed_offline_duty(data.schedule)
            - predicted_offline_duty(closure_debt_accrual_rate(flow), data.allocation)
        )
        <= data.tolerance.tolerance
    )


def online_sufficient_noncapacity_checks(
    fixture: Fixture, data: ClaimData
) -> dict[str, bool]:
    return {
        "geometry": derived_offline_budget_geometry(
            fixture, data.scope, data.budget_data, data.allocation
        ),
        "scheduleCarriedAndDeclared": declared_operating_schedule(data.schedule),
        "flowInventory": complete_phase_flow_inventory(fixture, data),
        "exchangeInventory": complete_external_exchange_inventory(fixture, data),
        "everyPhaseUsesClaimAllocation": all(
            phase.allocation_record == data.allocation
            for phase in data.schedule.phases
        ),
        "everyPhaseOnline": all(
            phase.mode is OperatingMode.online for phase in data.schedule.phases
        ),
        "actualDischargeOffsetsAccrual": all(
            closure_debt_accrual_rate(flow) <= closure_debt_discharge_rate(flow)
            for flow in data.flows
        ),
        "debtNonincreasing": all(
            flow.after_snapshot.total_debt <= flow.before_snapshot.total_debt
            for flow in data.flows
        ),
        "everyPhaseExchanges": all(
            exchange_in_phase(data.exchange_records, phase) > 0
            for phase in data.schedule.phases
        ),
    }


def online_sufficient_evidence(fixture: Fixture, data: ClaimData) -> bool:
    return all(online_sufficient_noncapacity_checks(fixture, data).values()) and all(
        closure_debt_discharge_rate(flow) <= kappa_on(data.allocation)
        for flow in data.flows
    )


def optional_offline_outside_deficit_evidence(fixture: Fixture, data: ClaimData) -> bool:
    online = tuple(phase for phase in data.schedule.phases if phase.mode is OperatingMode.online)
    offline = tuple(phase for phase in data.schedule.phases if phase.mode is OperatingMode.offline)
    rates = tuple(
        closure_debt_accrual_rate(flow)
        for phase in online
        if (flow := _flow_for_phase(data, phase)) is not None
    )
    return (
        derived_offline_budget_geometry(fixture, data.scope, data.budget_data, data.allocation)
        and declared_operating_schedule(data.schedule)
        and complete_phase_flow_inventory(fixture, data)
        and complete_external_exchange_inventory(fixture, data)
        and all(phase.allocation_record == data.allocation for phase in data.schedule.phases)
        and bool(online)
        and len(rates) == len(online)
        and len(set(rates)) == 1
        and all(
            (flow := _flow_for_phase(data, phase)) is not None
            and closure_debt_discharge_rate(flow) <= kappa_on(data.allocation)
            for phase in online
        )
        and rates[0] <= kappa_on(data.allocation)
        and bool(offline)
        and all(genuine_offline_phase_evidence(fixture, data, phase) for phase in offline)
    )


def bounded_counterexample_noncapacity_checks(
    fixture: Fixture, data: ClaimData
) -> dict[str, bool]:
    bound = data.debt_bound
    checks = {
        f"deficit.{name}": value
        for name, value in persistent_deficit_noncapacity_checks(
            fixture, data
        ).items()
    }
    checks.update(
        {
            "exchangeInventory": complete_external_exchange_inventory(
                fixture, data
            ),
            "debtBoundPresent": bound is not None,
            "boundCarried": bound is not None and _record_carried(bound),
            "boundScoped": bound is not None and bound.scope == data.scope,
            "boundDeclaredInAdvance": bound is not None
            and bound.declared_at <= data.scope.horizon.start_time,
            "recurrenceBoundCarried": _record_carried(data.recurrence_bound),
            "recurrenceBoundScoped": data.recurrence_bound.scope == data.scope,
            "recurrenceBoundDeclaredInAdvance": data.recurrence_bound.declared_at
            <= data.scope.horizon.start_time,
            "horizonExceedsRecurrenceBound": data.recurrence_bound.maximum_online_run
            < data.scope.horizon.end_time - data.scope.horizon.start_time,
            "allPhasesOnline": all(
                phase.mode is OperatingMode.online
                for phase in data.schedule.phases
            ),
            "everySnapshotBounded": bound is not None
            and all(
                flow.before_snapshot.total_debt <= bound.upper_bound
                and flow.after_snapshot.total_debt <= bound.upper_bound
                for flow in data.flows
            ),
            "exchangePersists": all(
                exchange_in_phase(data.exchange_records, phase) > 0
                for phase in data.schedule.phases
            ),
        }
    )
    return checks


def deficit_online_bounded_counterexample(fixture: Fixture, data: ClaimData) -> bool:
    return (
        all(bounded_counterexample_noncapacity_checks(fixture, data).values())
        and all(
            closure_debt_discharge_rate(flow) <= kappa_on(data.allocation)
            for flow in data.flows
        )
    )


def decorative_offline_flow_evidence(
    fixture: Fixture,
    data: ClaimData,
    phase: OperatingPhaseRecord,
    flow: ClosureDebtFlowRecord,
) -> bool:
    if not (
        derived_offline_budget_geometry(fixture, data.scope, data.budget_data, data.allocation)
        and complete_phase_flow_inventory(fixture, data)
        and complete_external_exchange_inventory(fixture, data)
    ):
        return False
    return (
        phase in data.schedule.phases
        and phase.mode is OperatingMode.offline
        and _record_carried(phase)
        and flow in data.flows
        and flow.phase_record == phase
        and _record_carried(flow)
        and complete_closure_debt_flow(fixture, flow)
        and (
            exchange_in_phase(data.exchange_records, phase) > 0
            or phase.allocation_record != data.allocation
            or phase.allocation_record.offline_external_allocation != 0
            or phase.allocation_record.offline_internal_discharge_allocation
            != data.allocation.online_internal_discharge_allocation
            + data.allocation.online_external_allocation
            or discharged_debt(flow) <= 0
            or flow.before_snapshot.total_debt <= flow.after_snapshot.total_debt
            or kappa_off(data.allocation) < closure_debt_discharge_rate(flow)
        )
    )


def decorative_offline_evidence(fixture: Fixture, data: ClaimData) -> bool:
    return any(
        (flow := _flow_for_phase(data, phase)) is not None
        and decorative_offline_flow_evidence(fixture, data, phase, flow)
        for phase in data.schedule.phases
    )


def duty_cycle_mismatch_evidence(fixture: Fixture, data: ClaimData) -> bool:
    online = tuple(phase for phase in data.schedule.phases if phase.mode is OperatingMode.online)
    if not online:
        return False
    flow = _flow_for_phase(data, online[0])
    if flow is None:
        return False
    return (
        alternating_offline_substrate(fixture, data)
        and _record_carried(data.tolerance)
        and data.tolerance.scope == data.scope
        and data.tolerance.declared_at <= data.scope.horizon.start_time
        and data.tolerance.tolerance
        < abs(
            observed_offline_duty(data.schedule)
            - predicted_offline_duty(closure_debt_accrual_rate(flow), data.allocation)
        )
    )


def skipped_offline_cascade_evidence(fixture: Fixture, data: ClaimData) -> bool:
    alarm = data.alarm_observation
    stress = data.stress_observation
    return (
        persistent_deficit_evidence(fixture, data)
        and complete_external_exchange_inventory(fixture, data)
        and all(phase.mode is OperatingMode.online for phase in data.schedule.phases)
        and all(flow.before_snapshot.total_debt < flow.after_snapshot.total_debt for flow in data.flows)
        and alarm is not None
        and stress is not None
        and _record_carried(alarm)
        and _record_carried(stress)
        and alarm.scope == data.scope
        and stress.scope == data.scope
        and alarm.phase_record.start_time <= alarm.observed_at <= alarm.phase_record.end_time
        and stress.phase_record.start_time <= stress.observed_at <= stress.phase_record.end_time
        and fixture.ctx.e7_alarm_observation_accepted(alarm)
        and fixture.ctx.e5_stress_observation_accepted(stress)
        and stress.status == "stressed"
        and alarm.observed_at < stress.observed_at
        and alarm.phase_record in data.schedule.phases
        and stress.phase_record in data.schedule.phases
    )


def offline_reclosure_status_record_matches_claim(
    claim: OfflineReclosureClaimRef, record: OfflineReclosureStatusRecord
) -> bool:
    return (
        record.scope == claim.scope
        and record.allocation_record == claim.allocation_record
        and record.schedule == claim.schedule
        and record.tolerance_record == claim.tolerance_record
        and record.recurrence_bound == claim.recurrence_bound
    )


def offline_reclosure_status_occurrence_for(
    claim: OfflineReclosureClaimRef, record: OfflineReclosureStatusRecord
) -> bool:
    return offline_reclosure_status_record_matches_claim(claim, record) and _record_carried(record)


def raw_evidence_truths(fixture: Fixture, data: ClaimData) -> dict[OfflineReclosureStatus, bool]:
    return {
        OfflineReclosureStatus.deficit_online_counterexample: deficit_online_bounded_counterexample(fixture, data),
        OfflineReclosureStatus.decorative_offline: decorative_offline_evidence(fixture, data),
        OfflineReclosureStatus.duty_cycle_mismatch: duty_cycle_mismatch_evidence(fixture, data),
        OfflineReclosureStatus.skipped_offline_cascade: skipped_offline_cascade_evidence(fixture, data),
        OfflineReclosureStatus.alternation_required: duty_cycle_prediction_evidence(fixture, data),
        OfflineReclosureStatus.online_sufficient: online_sufficient_evidence(fixture, data),
        OfflineReclosureStatus.offline_optional: optional_offline_outside_deficit_evidence(fixture, data),
    }


def case_truths_for_record(
    fixture: Fixture, data: ClaimData, record: OfflineReclosureStatusRecord
) -> dict[OfflineReclosureStatus, bool]:
    raw = raw_evidence_truths(fixture, data)
    occurrence = offline_reclosure_status_occurrence_for(data.claim_ref, record)
    truths: dict[OfflineReclosureStatus, bool] = {}
    for index, status in enumerate(STATUS_PRIORITY):
        higher_absent = all(not raw[higher] for higher in STATUS_PRIORITY[:index])
        own_positive = True if status is OfflineReclosureStatus.offline_reclosure_rejected else raw[status]
        linkage = True
        if status is OfflineReclosureStatus.decorative_offline:
            linkage = record.phase_record is not None and record.phase_record in data.schedule.phases
        elif status is OfflineReclosureStatus.skipped_offline_cascade:
            linkage = (
                record.alarm_observation == data.alarm_observation
                and record.stress_observation == data.stress_observation
            )
        truths[status] = (
            occurrence
            and record.status is status
            and higher_absent
            and own_positive
            and linkage
        )
    return truths


def classify_claim_data(
    fixture: Fixture,
    data: ClaimData,
    record: OfflineReclosureStatusRecord | None = None,
) -> tuple[OfflineReclosureStatus, dict[OfflineReclosureStatus, bool], OfflineReclosureStatusRecord | None]:
    candidate = data.status_record if record is None else record
    if candidate is None:
        return (
            OfflineReclosureStatus.unclassified,
            {status: False for status in STATUS_PRIORITY},
            None,
        )
    truths = case_truths_for_record(fixture, data, candidate)
    fired = tuple(status for status in STATUS_PRIORITY if truths[status])
    observed = fired[0] if len(fired) == 1 else OfflineReclosureStatus.unclassified
    return observed, truths, candidate


def classify_offline_reclosure_status(
    fixture: Fixture, claim_name: str
) -> tuple[OfflineReclosureStatus, dict[OfflineReclosureStatus, bool], OfflineReclosureStatusRecord | None]:
    return classify_claim_data(fixture, fixture.claims[claim_name])


def complete_offline_reclosure_status(fixture: Fixture, claim_name: str) -> bool:
    data = fixture.claims[claim_name]
    observed, truths, record = classify_claim_data(fixture, data)
    return (
        observed is not OfflineReclosureStatus.unclassified
        and record is not None
        and sum(truths.values()) == 1
        and offline_reclosure_status_occurrence_for(data.claim_ref, record)
    )


@dataclass(frozen=True)
class PhaseSpec:
    mode: OperatingMode
    duration: Fraction
    accrual_rate: Fraction
    discharge_rate: Fraction
    exchange_amount: Fraction


def _status_ids(tag_index: int) -> dict[str, Callable[[int], int] | int]:
    return {
        "horizon": 1600 + tag_index,
        "allocation": 2000 + tag_index,
        "schedule": 3000 + tag_index,
        "tolerance": 4000 + tag_index,
        "recurrence": 5000 + tag_index,
        "status": 6000 + tag_index,
        "phase": lambda j: 10000 + 100 * tag_index + j,
        "exchange": lambda j: 20000 + 100 * tag_index + j,
        "gate": lambda j: 30000 + 100 * tag_index + j,
        "flow": lambda j: 40000 + 100 * tag_index + j,
        "snapshot": lambda j: 50000 + 100 * tag_index + j,
    }


def _band_ids(base: int) -> dict[str, Callable[[int], int] | int]:
    return {
        "horizon": base + 1,
        "allocation": base + 2,
        "schedule": base + 3,
        "tolerance": base + 4,
        "recurrence": base + 5,
        "status": base + 6,
        "phase": lambda j: base + 10 + j,
        "exchange": lambda j: base + 30 + j,
        "gate": lambda j: base + 50 + j,
        "flow": lambda j: base + 70 + j,
        "snapshot": lambda j: base + 90 + j,
    }


def _control_ids(row: int, variant: int = 0) -> dict[str, Callable[[int], int] | int]:
    return _band_ids(1000000 + 10000 * row + 100 * variant)


def _id_value(ids: dict[str, Callable[[int], int] | int], key: str, ordinal: int | None = None) -> int:
    value = ids[key]
    if callable(value):
        if ordinal is None:
            raise ValueError(f"{key} requires an ordinal")
        return value(ordinal)
    if ordinal is not None:
        raise ValueError(f"{key} does not accept an ordinal")
    return value


def _xi_matrices(amount: Fraction) -> tuple[Mat, Mat, Mat, Mat, Mat]:
    parameters = {
        F(6): (F(3), F(1, 3)),
        F(4): (F(2), F(0)),
        F(3): (F(2), F(1, 4)),
        F(7, 2): (F(2), F(1, 8)),
        F(2): (F(2), F(1, 2)),
        F(1): (F(1), F(0)),
    }
    D_value, inverse_value = parameters[amount]
    C = ((F(1),),)
    L = ((F(1),),)
    D = ((D_value,),)
    inverse = ((inverse_value,),)
    return C, L, D, inverse, adequacyResidual(C, L, D, inverse)


def _make_e14_entry(
    scope: ClosureDebtScopeRecord,
    source_base: int,
    amount: Fraction,
    name: str,
) -> ClosureDebtEntryRecord:
    claim = e14.MemoryClaimRecord(
        f"{name}_claim", scope.debt_claim_id, (0, 1, 2, 3)
    )
    home = e14.RetrievalContextRecord(f"{name}_home", source_base + 40)
    shift = e14.RetrievalContextRecord(f"{name}_shift", source_base + 41)
    family = e14.DeclaredRetrievalContextFamily(
        f"{name}_family", source_base + 42, (home, shift)
    )
    values = (
        frozenset(("episode",)),
        frozenset(("route",)),
        frozenset(("audit",)),
        frozenset(("target",)),
    )
    memory = e14.CarriedMemoryRecord(
        f"{name}_memory", source_base + 43, 1, claim, values, source_base + 44
    )
    source_formation = e14.MemoryRecordFormationRecord(
        f"{name}_source_formation", source_base + 49, memory, 0
    )
    quotient = e14.RecordQuotientRecord(
        f"{name}_quotient", source_base + 45, ("q", "q", "r", "s")
    )
    home_transport = e14.RetrievalTransportRecord(
        f"{name}_home_transport",
        source_base + 46,
        memory,
        home,
        quotient,
        ("t", "t", "u", "v"),
        0,
    )
    shift_transport = e14.RetrievalTransportRecord(
        f"{name}_shift_transport",
        source_base + 47,
        memory,
        shift,
        quotient,
        ("t", "t", "u", "w"),
        0,
    )
    inventory = e14.CompleteRetrievalTransportInventory(
        f"{name}_inventory", memory, family, (home_transport, shift_transport)
    )
    conflict = e14.RetrievalConflictRecord(
        f"{name}_conflict", source_base + 1, memory, shift_transport, claim
    )
    trigger = e14.ReconsolidationTrigger(
        f"{name}_trigger", memory, family, inventory, conflict
    )
    residual = e14.ReconsolidationResidualRecord(
        f"{name}_residual", source_base + 2, conflict, amount
    )
    ledger = LedgerEntry(
        source_base + 4,
        residual.residual_id,
        amount,
        "reconsolidation-residual",
        carried=e14.CARRIED,
    )
    current = replace(memory, name=f"{name}_current")
    formation = e14.MemoryRecordFormationRecord(
        f"{name}_formation", source_base + 48, current, 0
    )
    candidate = e14.StatusedUnresolvedCandidate(
        f"{name}_unresolved", trigger, current, formation, residual, ledger
    )
    disposition = e14.ReconsolidationDispositionRecord(
        f"{name}_disposition",
        source_base + 50,
        conflict,
        e14.ReconsolidationDisposition.statused_unresolved,
        None,
        residual,
    )
    disposition_inventory = e14.CompleteReconsolidationDispositionInventory(
        f"{name}_disposition_inventory", conflict, (disposition,)
    )
    claim_ref = e14.ReconsolidationClaimRef(
        f"{name}_claim_ref",
        memory,
        family,
        shift_transport,
        shift,
        claim,
    )
    status_record = e14.ReconsolidationStatusRecord(
        name=f"{name}_status",
        status_record_id=source_base + 51,
        status=e14.ReconsolidationStatus.statused_unresolved,
        source_record=memory,
        family=family,
        transport_record=shift_transport,
        context_record=shift,
        claim_record=claim,
        conflict_record=conflict,
        residual_record=residual,
        disposition_record=disposition,
    )
    registration = E14ResidualRegistrationRecord(
        source_base + 3, residual, F(0)
    )
    return ClosureDebtEntryRecord(
        ClosureDebtComponentKind.e14_reconsolidation,
        E14ResidualDebtSource(
            candidate,
            registration,
            source_formation,
            claim_ref,
            disposition_inventory,
            status_record,
        ),
        ledger,
    )


def _replace_debt_entry_in_claim(
    data: ClaimData,
    original: ClosureDebtEntryRecord,
    replacement: ClosureDebtEntryRecord,
) -> ClaimData:
    def replace_snapshot(
        snapshot: ClosureDebtSnapshotRecord,
    ) -> ClosureDebtSnapshotRecord:
        entries = tuple(
            replacement if entry == original else entry for entry in snapshot.entries
        )
        return replace(snapshot, entries=entries, total_debt=closure_debt(entries))

    return replace(
        data,
        flows=tuple(
            replace(
                flow,
                before_snapshot=replace_snapshot(flow.before_snapshot),
                after_snapshot=replace_snapshot(flow.after_snapshot),
                accrued_entries=tuple(
                    replacement if entry == original else entry
                    for entry in flow.accrued_entries
                ),
                discharge_records=tuple(
                    replace(
                        discharge,
                        debt_entry=replacement
                        if discharge.debt_entry == original
                        else discharge.debt_entry,
                    )
                    for discharge in flow.discharge_records
                ),
            )
            for flow in data.flows
        ),
    )


def _e14_collision_fixture(
    fixture: Fixture, source: E14ResidualDebtSource
) -> e14.Fixture:
    native = _e14_status_fixture(fixture, source)
    trigger = source.candidate.trigger
    original = trigger.source_record
    transport = trigger.conflict_record.transport_record
    base = source.candidate.residual_record.residual_id - 2

    repair_value = (
        frozenset(("collision_left",)),
        frozenset(("collision_right",)),
        frozenset(),
        frozenset(),
    )
    repaired = e14.CarriedMemoryRecord(
        f"{original.name}_collision_repaired",
        original.record_id,
        original.version + 1,
        original.claim_record,
        tuple(
            value | addition
            for value, addition in zip(original.record_value, repair_value, strict=True)
        ),
        original.provenance_root_id,
    )
    repair_package = e14.RecordRepairPackage(
        f"{original.name}_collision_package", base + 60, transport.context_record, repair_value
    )
    repair_mutation = e14.RecordMutationRecord(
        f"{original.name}_collision_repair_mutation",
        base + 61,
        original,
        repaired,
        transport.transport_id,
        transport.context_record,
        e14.RecordMutationKind.repair,
    )
    repair_formation = e14.MemoryRecordFormationRecord(
        f"{original.name}_collision_repair_formation",
        base + 62,
        repaired,
        transport.retrieved_at,
    )
    repair_provenance = e14.MutationProvenanceRecord(
        f"{original.name}_collision_repair_provenance",
        base + 63,
        repair_mutation,
        original,
        repaired,
        original.provenance_root_id,
    )
    repair_action_evidence = CarriedRecordEvidence(
        base + 60, FineSourceTag.audited_cell_records, True, True
    )
    repair_action = RepairAction(
        repair_package={
            item: repair_value[index] for index, item in enumerate(ITEMS)
        },
        z_next=2,
        defect=f"collision_repair_{base}",
        defect_evidence=repair_action_evidence,
        audit_record=f"collision_repair_audit_{base}",
        audit_record_evidence=repair_action_evidence,
    )
    repair_candidate = e14.RecordRepairCandidate(
        f"{original.name}_collision_repair_evidence",
        trigger,
        repair_package,
        repaired,
        repair_formation,
        repair_mutation,
        repair_provenance,
        0,
        repair_action,
    )

    coarsened = e14.CarriedMemoryRecord(
        f"{original.name}_collision_coarsened",
        original.record_id,
        original.version + 1,
        original.claim_record,
        original.record_value,
        original.provenance_root_id,
    )
    before_quotient = e14.RecordQuotientRecord(
        f"{original.name}_collision_before_quotient",
        base + 66,
        ("a", "b", "c", "d"),
    )
    after_quotient = e14.RecordQuotientRecord(
        f"{original.name}_collision_after_quotient",
        base + 67,
        ("ab", "ab", "c", "d"),
    )
    coarsening_mutation = e14.RecordMutationRecord(
        f"{original.name}_collision_coarsening_mutation",
        base + 64,
        original,
        coarsened,
        transport.transport_id,
        transport.context_record,
        e14.RecordMutationKind.coarsening,
    )
    coarsening_formation = e14.MemoryRecordFormationRecord(
        f"{original.name}_collision_coarsening_formation",
        base + 65,
        coarsened,
        transport.retrieved_at,
    )
    support_audit = e14.DistinctionSupportAuditRecord(
        f"{original.name}_collision_support_audit",
        base + 68,
        before_quotient,
        after_quotient,
        original.claim_record.claim_id,
        "a",
        "b",
    )
    coarsening_provenance = e14.MutationProvenanceRecord(
        f"{original.name}_collision_coarsening_provenance",
        base + 69,
        coarsening_mutation,
        original,
        coarsened,
        original.provenance_root_id,
    )
    coarsening_action_evidence = CarriedRecordEvidence(
        base + 64, FineSourceTag.audited_cell_records, True, True
    )
    coarsening_action = RepairAction(
        repair_package={item: after_quotient.quotient[index] for index, item in enumerate(ITEMS)},
        z_next=3,
        defect=f"collision_coarsening_{base}",
        defect_evidence=coarsening_action_evidence,
        audit_record=f"collision_coarsening_audit_{base}",
        audit_record_evidence=coarsening_action_evidence,
    )
    coarsening_candidate = e14.RecordCoarseningCandidate(
        f"{original.name}_collision_coarsening_evidence",
        trigger,
        coarsened,
        coarsening_formation,
        before_quotient,
        after_quotient,
        support_audit,
        coarsening_mutation,
        coarsening_provenance,
        0,
        coarsening_action,
    )
    collision_carrier = e14._build_repair_world_carrier(
        (repair_action, coarsening_action),
        (source.candidate.ledger_entry,),
        transport.current_quotient,
    )

    return replace(
        native,
        carrier=collision_carrier,
        memory_records={
            **native.memory_records,
            repaired.name: repaired,
            coarsened.name: coarsened,
        },
        formations={
            **native.formations,
            repair_formation.name: repair_formation,
            coarsening_formation.name: coarsening_formation,
        },
        quotients={
            **native.quotients,
            before_quotient.name: before_quotient,
            after_quotient.name: after_quotient,
        },
        repair_packages={repair_package.name: repair_package},
        mutations={
            repair_mutation.name: repair_mutation,
            coarsening_mutation.name: coarsening_mutation,
        },
        distinction_audits={support_audit.name: support_audit},
        provenances={
            repair_provenance.name: repair_provenance,
            coarsening_provenance.name: coarsening_provenance,
        },
        repair_candidates={repair_candidate.name: repair_candidate},
        coarsening_candidates={coarsening_candidate.name: coarsening_candidate},
        formation_registry={
            **native.formation_registry,
            repair_formation.formation_id: repaired,
            coarsening_formation.formation_id: coarsened,
        },
        record_quotient_links=frozenset(
            (
                (original.name, before_quotient.name),
                (coarsened.name, after_quotient.name),
            )
        ),
        unsupported_pairs={
            support_audit.audit_id: frozenset((frozenset(("a", "b")),))
        },
        coarsening_install_registry=frozenset(
            (
                (
                    coarsening_action.defect,
                    original.name,
                    coarsened.name,
                    before_quotient.name,
                    after_quotient.name,
                ),
            )
        ),
    )


def _make_f3_entry(
    scope: ClosureDebtScopeRecord,
    residue_id: int,
    ledger_id: int,
    amount: Fraction,
    name: str,
) -> ClosureDebtEntryRecord:
    residue = RouteResidueDebtRecord(
        residue_id, name, scope.debt_claim_id, F(0), amount
    )
    ledger = LedgerEntry(ledger_id, residue_id, amount, "f3-route-residue")
    return ClosureDebtEntryRecord(
        ClosureDebtComponentKind.f3_route_residue, residue, ledger
    )


def _make_xi_entry(
    scope: ClosureDebtScopeRecord,
    source_base: int,
    amount: Fraction,
    name: str,
) -> ClosureDebtEntryRecord:
    C, L, D, inverse, residual_matrix = _xi_matrices(amount)
    policy = XiResidualValuationPolicyRecord(source_base + 22, F(-1))
    residual = XiAdequacyResidualDebtRecord(
        source_base + 21,
        C,
        L,
        D,
        inverse,
        residual_matrix,
        policy,
        scope.debt_claim_id,
        F(0),
        amount,
    )
    ledger = LedgerEntry(
        source_base + 23,
        residual.residual_id,
        amount,
        "xi-adequacy-residual",
    )
    return ClosureDebtEntryRecord(
        ClosureDebtComponentKind.xi_adequacy_residual, residual, ledger
    )


def _base_entries(
    scope: ClosureDebtScopeRecord,
    fixture_index: int,
    reserves: tuple[Fraction, ...],
) -> tuple[ClosureDebtEntryRecord, ...]:
    base = 100000 + 100 * fixture_index
    entries: list[ClosureDebtEntryRecord] = [
        _make_e14_entry(scope, base, F(8), f"debt_e14_{fixture_index}"),
        _make_f3_entry(
            scope, base + 11, base + 12, F(8), f"debt_f3_{fixture_index}"
        ),
        _make_xi_entry(scope, base, F(4), f"debt_xi_{fixture_index}"),
    ]
    for index, amount in enumerate(reserves):
        entries.append(
            _make_f3_entry(
                scope,
                base + 31 + 2 * index,
                base + 32 + 2 * index,
                amount,
                f"reserve_{fixture_index}_{index}",
            )
        )
    return tuple(entries)


def _accrual_amounts(duration: Fraction, rate: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    profiles = {
        (F(3), F(6)): (F(6), F(6), F(6)),
        (F(2), F(6)): (F(4), F(4), F(4)),
        (F(6), F(5)): (F(12), F(12), F(6)),
        (F(3), F(3)): (F(3), F(3), F(3)),
        (F(3), F(7, 2)): (F(7, 2), F(7, 2), F(7, 2)),
        (F(3), F(4)): (F(4), F(4), F(4)),
        (F(1), F(5)): (F(2), F(2), F(1)),
        (F(4), F(6)): (F(10), F(8), F(6)),
        (F(2), F(3)): (F(2), F(2), F(2)),
    }
    return profiles[(duration, rate)]


def _accrued_entries(
    scope: ClosureDebtScopeRecord,
    fixture_index: int,
    phase_ordinal: int,
    duration: Fraction,
    rate: Fraction,
) -> tuple[ClosureDebtEntryRecord, ...]:
    if rate == 0:
        return ()
    e14_amount, f3_amount, xi_amount = _accrual_amounts(duration, rate)
    base = 2000000 + 10000 * fixture_index + 100 * phase_ordinal
    return (
        _make_e14_entry(
            scope, base, e14_amount, f"accrual_e14_{fixture_index}_{phase_ordinal}"
        ),
        _make_f3_entry(
            scope,
            base + 11,
            base + 12,
            f3_amount,
            f"accrual_f3_{fixture_index}_{phase_ordinal}",
        ),
        _make_xi_entry(
            scope, base, xi_amount, f"accrual_xi_{fixture_index}_{phase_ordinal}"
        ),
    )


def _select_whole_entries(
    entries: tuple[ClosureDebtEntryRecord, ...], amount: Fraction
) -> tuple[ClosureDebtEntryRecord, ...]:
    if amount == 0:
        return ()
    for count in range(1, len(entries) + 1):
        for selected in combinations(entries, count):
            if closure_debt(selected) == amount:
                return selected
    raise ValueError(f"no whole-entry subset discharges {amount} from {tuple(e.amount for e in entries)}")


def _phase_specs(*rows: tuple[str, int | Fraction, int | Fraction, int | Fraction, int | Fraction]) -> tuple[PhaseSpec, ...]:
    return tuple(
        PhaseSpec(
            OperatingMode.online if mode == "O" else OperatingMode.offline,
            F(duration),
            F(accrual),
            F(discharge),
            F(exchange),
        )
        for mode, duration, accrual, discharge, exchange in rows
    )


def _build_claim_data(
    *,
    name: str,
    fixture_index: int,
    ids: dict[str, Callable[[int], int] | int],
    specs: tuple[PhaseSpec, ...],
    maximum_online_run: Fraction,
    tolerance: Fraction,
    reserves: tuple[Fraction, ...] = (),
    status: OfflineReclosureStatus | None = None,
    debt_bound: Fraction | None = None,
    tolerance_declared_at: Fraction = F(-1),
    allocation_declared_at: Fraction = F(-1),
    omit_p2_gates: bool = False,
    bad_phase_allocation: bool = False,
    cascade: bool = False,
    scope_override: ClosureDebtScopeRecord | None = None,
    forced_discharge_keys: dict[int, tuple[tuple[ClosureDebtComponentKind, int], ...]] | None = None,
) -> ClaimData:
    end_time = sum((spec.duration for spec in specs), F(0))
    if scope_override is None:
        horizon = ClosureDebtHorizonRecord(
            _id_value(ids, "horizon"), F(0), end_time
        )
        scope = ClosureDebtScopeRecord(
            1500 + fixture_index, CHALLENGE_CLASS, horizon
        )
    else:
        if (
            scope_override.horizon.start_time != 0
            or scope_override.horizon.end_time != end_time
        ):
            raise ValueError("scope override must match the schedule horizon")
        scope = scope_override
    allocation = SharedBudgetAllocationRecord(
        _id_value(ids, "allocation"),
        scope,
        allocation_declared_at,
        F(2),
        F(4),
        F(0),
        F(6),
    )
    phase_allocation_override = (
        SharedBudgetAllocationRecord(
            2099, scope, F(-1), F(2), F(4), F(1), F(5)
        )
        if bad_phase_allocation
        else None
    )
    debt_base = 100000 + 100 * fixture_index
    budget_entry = LedgerEntry(debt_base + 80, debt_base + 80, F(6), "exposure-budget")
    spend_entry = LedgerEntry(debt_base + 81, debt_base + 81, F(6), "exposure-spend")
    active = ActiveFamily(support=("offline_probe",), weight={"offline_probe": F(1)}, as_xi_family="offline")
    budget_move = ProbeMove(ProbeMoveKind.allocation, active, active)
    budget_data = ExposureBudgetWitness(F(6), F(6), budget_entry, spend_entry, budget_move)

    phases: list[OperatingPhaseRecord] = []
    cursor = F(0)
    for ordinal, spec in enumerate(specs, 1):
        phase_allocation = allocation if phase_allocation_override is None else phase_allocation_override
        phases.append(
            OperatingPhaseRecord(
                _id_value(ids, "phase", ordinal),
                scope,
                phase_allocation,
                spec.mode,
                cursor,
                cursor + spec.duration,
            )
        )
        cursor += spec.duration
    schedule = DeclaredOperatingSchedule(_id_value(ids, "schedule"), scope, tuple(phases))
    tolerance_record = DutyCycleToleranceRecord(
        _id_value(ids, "tolerance"), scope, tolerance_declared_at, tolerance
    )
    recurrence = OfflineRecurrenceBoundRecord(
        _id_value(ids, "recurrence"), scope, F(-1), maximum_online_run
    )

    current = _base_entries(scope, fixture_index, reserves)
    initial_snapshot = ClosureDebtSnapshotRecord(
        _id_value(ids, "snapshot", 0), scope, F(0), current, closure_debt(current)
    )
    flows: list[ClosureDebtFlowRecord] = []
    before = initial_snapshot
    forced = forced_discharge_keys or {}
    for ordinal, (phase, spec) in enumerate(zip(phases, specs, strict=True), 1):
        accrued = _accrued_entries(
            scope, fixture_index, ordinal, spec.duration, spec.accrual_rate
        )
        target_discharge = spec.duration * spec.discharge_rate
        if ordinal in forced:
            by_key = {entry.key: entry for entry in current}
            selected = tuple(by_key[key] for key in forced[ordinal])
            if closure_debt(selected) != target_discharge:
                raise ValueError(f"forced discharge for {name} phase {ordinal} has wrong amount")
        else:
            selected = _select_whole_entries(current, target_discharge)
        selected_set = set(selected)
        after_entries = tuple(entry for entry in current if entry not in selected_set) + accrued
        after = ClosureDebtSnapshotRecord(
            _id_value(ids, "snapshot", ordinal),
            scope,
            phase.end_time,
            after_entries,
            closure_debt(after_entries),
        )
        discharge_base = 2000000 + 10000 * fixture_index + 100 * ordinal
        discharges = tuple(
            DebtDischargeRecord(
                discharge_base + 70 + index,
                phase,
                entry,
                entry.amount,
                phase.end_time,
            )
            for index, entry in enumerate(selected, 1)
        )
        flows.append(
            ClosureDebtFlowRecord(
                _id_value(ids, "flow", ordinal),
                phase,
                before,
                after,
                accrued,
                discharges,
            )
        )
        current = after_entries
        before = after

    exchanges = tuple(
        ExternalExchangeRecord(
            _id_value(ids, "exchange", ordinal),
            phase,
            spec.exchange_amount,
            phase.start_time,
        )
        for ordinal, (phase, spec) in enumerate(zip(phases, specs, strict=True), 1)
    )
    gates: list[ExchangeGateRecord] = []
    if not omit_p2_gates:
        for ordinal, phase in enumerate(phases, 1):
            if phase.mode is not OperatingMode.offline:
                continue
            gate_id = _id_value(ids, "gate", ordinal)
            evidence = CarriedRecordEvidence(
                gate_id,
                FineSourceTag.audited_cell_records,
                True,
                True,
            )
            action = RepairAction(
                repair_package={item: f"gate_{gate_id}" for item in ITEMS},
                z_next=1,
                defect=f"gate_defect_{gate_id}",
                defect_evidence=evidence,
                audit_record=f"gate_audit_{gate_id}",
                audit_record_evidence=evidence,
            )
            gates.append(ExchangeGateRecord(gate_id, phase, action, RepairSort.P2))

    bound = None
    if debt_bound is not None:
        bound = DebtBoundRecord(
            _id_value(ids, "recurrence") + 100, scope, F(-1), debt_bound
        )
    alarm = None
    stress = None
    if cascade:
        alarm = E7AlarmCascadeObservation(
            _id_value(ids, "status") + 1000,
            scope,
            phases[0],
            F(1),
            "statused",
            "closure_debt",
        )
        stress = E5StressCascadeObservation(
            _id_value(ids, "status") + 2000,
            scope,
            phases[-1],
            F(5),
            "stressed",
        )

    status_record = None
    if status is not None:
        linked_phase = phases[0] if status is OfflineReclosureStatus.decorative_offline else None
        status_record = OfflineReclosureStatusRecord(
            _id_value(ids, "status"),
            status,
            scope,
            allocation,
            schedule,
            tolerance_record,
            recurrence,
            linked_phase,
            alarm if status is OfflineReclosureStatus.skipped_offline_cascade else None,
            stress if status is OfflineReclosureStatus.skipped_offline_cascade else None,
        )
    return ClaimData(
        name,
        fixture_index,
        scope,
        allocation,
        budget_data,
        schedule,
        tolerance_record,
        recurrence,
        tuple(flows),
        exchanges,
        tuple(gates),
        bound,
        alarm,
        stress,
        status_record,
    )


def _build_repair_world_carrier(claims: Iterable[ClaimData]) -> RepairWorldCarrier:
    claims_tuple = tuple(claims)
    gates = tuple(gate for data in claims_tuple for gate in data.gates)
    gate_budget = {
        gate.action.defect: data.budget_data.budget_entry
        for data in claims_tuple
        for gate in data.gates
    }
    actions = tuple(gate.action for gate in gates)

    all_entries: list[LedgerEntry] = []
    for data in claims_tuple:
        all_entries.extend((data.budget_data.budget_entry, data.budget_data.spend_entry))
        for flow in data.flows:
            all_entries.extend(entry.ledger_entry for entry in flow.before_snapshot.entries)
            all_entries.extend(entry.ledger_entry for entry in flow.after_snapshot.entries)
    ledger_entries = tuple(dict.fromkeys(all_entries))

    trajectory = DeclaredTrajectory(
        legitimate_start=lambda _tau, n: n == 0,
        supp_k=lambda left, right: right == left + 1,
        tau=lambda n: n,
        step_in_scope=lambda n: n >= 0,
        n_start=0,
    )

    def policy(name: str, records: dict[int, object]) -> CarriedRecordPolicy:
        return CarriedRecordPolicy(
            trajectory=trajectory,
            coordinate_declared=lambda _rho: True,
            rho_of=lambda coordinate: records[coordinate],
            name=name,
        )

    defect_by_time = {action.defect_evidence.n0: action.defect for action in actions}
    audit_by_time = {
        action.audit_record_evidence.n0: action.audit_record for action in actions
    }
    move_record_by_time = {
        action.defect_evidence.n0: f"move_{action.defect}" for action in actions
    }
    defect_policy = policy("e15-defect", defect_by_time)
    audit_policy = policy("e15-audit", audit_by_time)
    move_policy = policy("e15-move", move_record_by_time)

    ledger_times = {entry: index + 1 for index, entry in enumerate(ledger_entries)}
    ledger_policy = policy(
        "e15-ledger", {time: entry for entry, time in ledger_times.items()}
    )
    ledger = CarriedLedger(
        ledger_policy=ledger_policy,
        ledger_entries=ledger_entries,
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: CarriedRecordEvidence(
            n0=ledger_times[entry],
            source_tag=entry.carried.source_tag,
            generated_by_s=entry.carried.generated_by_s,
            in_scope=entry.carried.in_scope,
        )
        if entry in ledger_times and entry.carried.present
        else None,
    )

    instrument_record = "e15-instrument-record"
    instrument_policy = policy("e15-instrument", {0: instrument_record})
    occurrence = CarriedRecordOccurrence(
        instrument_record,
        CarriedRecordEvidence(
            0, FineSourceTag.audited_cell_records, True, True
        ),
    )
    moves_by_defect = {
        action.defect: RepairMove(
            sort=RepairSort.P2,
            payload=action.repair_package,
            move_record=f"move_{action.defect}",
            move_record_evidence=action.defect_evidence,
            budget_line=gate_budget[action.defect],
        )
        for action in actions
    }
    audits = {
        (f"move_{action.defect}", action.z_next): action.audit_record
        for action in actions
    }
    instrument = ActiveCarriedInstrument(
        instrument="e15-p2-gate-instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=(occurrence,),
        threshold_records=(occurrence,),
        check_rule_records=(CheckRuleRecord(occurrence, "passes"),),
        detects=lambda _z, defect: defect in moves_by_defect,
        gate_allows=lambda _z, defect, move: moves_by_defect.get(defect) == move,
        re_audits=lambda _z, move, z_next, audit: audits.get(
            (move.move_record, z_next)
        )
        == audit,
    )
    theory = TheoryPackage(
        trajectory=trajectory,
        f="e15-f",
        sigma_f="e15-sigma",
        residual_family="e15-residual-family",
        audit_access="e15-audit-access",
        formed_package=True,
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda defect: moves_by_defect[defect],
        AdmissibleMove=lambda _ledger, _z, defect, move: moves_by_defect.get(defect)
        == move,
    )
    active = ActiveFamily(
        support=("offline_probe",),
        weight={"offline_probe": F(1)},
        as_xi_family="offline",
    )
    active_policy = policy("e15-active-family", {0: active})
    economy = ProbeEconomy(
        catalog=ProbeCatalog(("offline_probe",), True),
        active_family_policy=active_policy,
        same_family_saturated=lambda _active, _probe: False,
        exposure_cost_entry=lambda _entry, _probe, _cost: True,
        exposure_budget_entry=lambda entry, budget: entry.label == "exposure-budget"
        and entry.amount == budget,
        exposure_spend_entry=lambda entry, spend: entry.label == "exposure-spend"
        and entry.amount == spend,
        retirement_record_entry=lambda _entry, _probe: True,
        budget_admissible=lambda move: move.kind is ProbeMoveKind.allocation,
    )
    config = RepairWorldConfig(
        kernel=ring_kernel(2),
        probe_economy=economy,
        e_system=system,
        challenge_process=ChallengeProcess(recurrence_period=None),
    )
    state = RepairWorldState(
        y=0,
        q={item: item for item in ITEMS},
        L=active,
        r=ledger,
        Lambda={
            "repair": F(6),
            "repair_spend": F(6),
            "exposure": F(2),
            "maintenance": F(0),
            "risk": F(0),
        },
        A=AuditState(instrument=instrument, flags=AuditFlags(frozenset((1, 2, 3)))),
    )
    return RepairWorldCarrier(config, state, ledger_entries)


def _all_snapshots(data: ClaimData) -> tuple[ClosureDebtSnapshotRecord, ...]:
    snapshots: list[ClosureDebtSnapshotRecord] = []
    for flow in data.flows:
        if flow.before_snapshot not in snapshots:
            snapshots.append(flow.before_snapshot)
        if flow.after_snapshot not in snapshots:
            snapshots.append(flow.after_snapshot)
    return tuple(snapshots)


def _make_context(claims: Iterable[ClaimData]) -> OfflineReclosureClassifierContext:
    claims_tuple = tuple(claims)
    e14_registry: set[tuple[int, Fraction]] = set()
    f3_registry: set[tuple[int, Fraction]] = set()
    xi_registry: set[tuple[int, Fraction]] = set()
    xi_policies: set[int] = set()
    for data in claims_tuple:
        for snapshot in _all_snapshots(data):
            for entry in snapshot.entries:
                if entry.kind is ClosureDebtComponentKind.e14_reconsolidation:
                    source = entry.source
                    if not isinstance(source, E14ResidualDebtSource):
                        continue
                    e14_registry.add(
                        (source.registration_record.registration_id, snapshot.observed_at)
                    )
                elif entry.kind is ClosureDebtComponentKind.f3_route_residue:
                    source = entry.source
                    if not isinstance(source, RouteResidueDebtRecord):
                        continue
                    f3_registry.add((source.residue_id, snapshot.observed_at))
                else:
                    source = entry.source
                    if not isinstance(source, XiAdequacyResidualDebtRecord):
                        continue
                    xi_registry.add((source.residual_id, snapshot.observed_at))
                    xi_policies.add(source.valuation_policy.valuation_policy_id)
    gates = tuple(gate for data in claims_tuple for gate in data.gates)
    alarms = tuple(
        data.alarm_observation
        for data in claims_tuple
        if data.alarm_observation is not None
    )
    stresses = tuple(
        data.stress_observation
        for data in claims_tuple
        if data.stress_observation is not None
    )
    return OfflineReclosureClassifierContext(
        frozenset(e14_registry),
        frozenset(f3_registry),
        frozenset(xi_policies),
        frozenset(xi_registry),
        frozenset(gate.gate_record_id for gate in gates),
        tuple((gate.gate_record_id, "external_exchange") for gate in gates),
        frozenset(alarm.observation_id for alarm in alarms),
        frozenset(stress.observation_id for stress in stresses),
    )


def _assemble_fixture(claims: dict[str, ClaimData]) -> Fixture:
    claims_tuple = tuple(claims.values())
    carrier = _build_repair_world_carrier(claims_tuple)
    ctx = _make_context(claims_tuple)
    eligible_debt_entries: dict[
        tuple[int, Fraction], tuple[ClosureDebtEntryRecord, ...]
    ] = {}
    eligible_exchanges: dict[int, tuple[ExternalExchangeRecord, ...]] = {}
    formations: dict[int, e14.CarriedMemoryRecord] = {}
    transports: dict[int, e14.RetrievalTransportRecord] = {}
    for data in claims_tuple:
        for snapshot in _all_snapshots(data):
            eligible_debt_entries[(data.scope.debt_claim_id, snapshot.observed_at)] = snapshot.entries
            for entry in snapshot.entries:
                if not isinstance(entry.source, E14ResidualDebtSource):
                    continue
                source = entry.source
                formations[source.source_formation.formation_id] = (
                    source.source_formation.memory_record
                )
                formations[source.candidate.formation_record.formation_id] = (
                    source.candidate.formation_record.memory_record
                )
                for transport in source.candidate.trigger.inventory.declared_transports:
                    transports[transport.transport_id] = transport
        eligible_exchanges[data.schedule.schedule_id] = data.exchange_records
    return Fixture(
        carrier,
        ctx,
        claims,
        eligible_debt_entries,
        eligible_exchanges,
        formations,
        transports,
    )


def build_fixture() -> Fixture:
    claims: dict[str, ClaimData] = {}

    status_specs = (
        (
            "claim_alternation_required",
            1,
            _phase_specs(("O", 3, 6, 4, 1), ("F", 1, 0, 6, 0), ("O", 3, 6, 4, 1), ("F", 1, 0, 6, 0)),
            F(3),
            F(0),
            (),
            OfflineReclosureStatus.alternation_required,
        ),
        (
            "claim_online_sufficient",
            2,
            _phase_specs(("O", 3, 3, 3, 1), ("O", 3, 3, 3, 1)),
            F(3),
            F(0),
            (F(9),),
            OfflineReclosureStatus.online_sufficient,
        ),
        (
            "claim_offline_optional",
            3,
            _phase_specs(("O", 3, 3, 3, 1), ("F", 1, 0, 6, 0)),
            F(3),
            F(0),
            (F(9),),
            OfflineReclosureStatus.offline_optional,
        ),
        (
            "claim_deficit_online_counterexample",
            4,
            _phase_specs(*(("O", 2, 6, 4, 1),) * 5),
            F(3),
            F(0),
            (),
            OfflineReclosureStatus.deficit_online_counterexample,
        ),
        (
            "claim_decorative_exchange_active",
            5,
            _phase_specs(("F", 1, 0, 6, 1)),
            F(1),
            F(0),
            (F(6),),
            OfflineReclosureStatus.decorative_offline,
        ),
        (
            "claim_decorative_no_discharge",
            6,
            _phase_specs(("F", 1, 0, 0, 0)),
            F(1),
            F(0),
            (),
            OfflineReclosureStatus.decorative_offline,
        ),
        (
            "claim_decorative_bad_reallocation",
            7,
            _phase_specs(("F", 1, 0, 5, 0)),
            F(1),
            F(0),
            (F(5),),
            OfflineReclosureStatus.decorative_offline,
        ),
        (
            "claim_duty_cycle_mismatch",
            8,
            _phase_specs(("O", 2, 6, 4, 1), ("F", 1, 0, 6, 0), ("O", 2, 6, 4, 1), ("F", 1, 0, 6, 0)),
            F(2),
            F(1, 24),
            (F(6), F(6)),
            OfflineReclosureStatus.duty_cycle_mismatch,
        ),
        (
            "claim_skipped_offline_cascade",
            9,
            _phase_specs(*(("O", 2, 6, 4, 1),) * 3),
            F(2),
            F(0),
            (),
            OfflineReclosureStatus.skipped_offline_cascade,
        ),
        (
            "claim_zero_exchange_without_p2",
            10,
            _phase_specs(("F", 1, 0, 6, 0)),
            F(1),
            F(0),
            (F(6),),
            OfflineReclosureStatus.offline_reclosure_rejected,
        ),
    )
    for name, tag, specs, maximum, tolerance, reserves, status in status_specs:
        claims[name] = _build_claim_data(
            name=name,
            fixture_index=tag,
            ids=_status_ids(tag),
            specs=specs,
            maximum_online_run=maximum,
            tolerance=tolerance,
            reserves=reserves,
            status=status,
            debt_bound=F(40) if tag == 4 else None,
            omit_p2_gates=tag == 10,
            bad_phase_allocation=tag == 7,
            cascade=tag == 9,
        )

    boundary_rows = (
        (
            "boundary_rate_7_2",
            20,
            _phase_specs(("O", 3, F(7, 2), F(7, 2), 1), ("O", 3, F(7, 2), F(7, 2), 1)),
            F(3),
            (F(21, 2),),
            OfflineReclosureStatus.online_sufficient,
        ),
        (
            "boundary_rate_4",
            21,
            _phase_specs(("O", 3, 4, 4, 1), ("O", 3, 4, 4, 1)),
            F(3),
            (),
            OfflineReclosureStatus.online_sufficient,
        ),
        (
            "boundary_rate_5",
            22,
            _phase_specs(("O", 6, 5, 4, 1), ("F", 1, 0, 6, 0), ("O", 6, 5, 4, 1), ("F", 1, 0, 6, 0)),
            F(6),
            (F(4),),
            OfflineReclosureStatus.alternation_required,
        ),
    )
    for ordinal, (name, index, specs, maximum, reserves, status) in enumerate(boundary_rows):
        claims[name] = _build_claim_data(
            name=name,
            fixture_index=index,
            ids=_band_ids(70000 + 1000 * ordinal),
            specs=specs,
            maximum_online_run=maximum,
            tolerance=F(0),
            reserves=reserves,
            status=status,
        )

    for ordinal, index in enumerate(range(30, 34)):
        name = f"ablation_trace_{ordinal + 1}"
        claims[name] = _build_claim_data(
            name=name,
            fixture_index=index,
            ids=_band_ids(80000 + 1000 * ordinal),
            specs=_phase_specs(*(("O", 2, 6, 4, 1),) * 3),
            maximum_online_run=F(2),
            tolerance=F(0),
            cascade=True,
        )

    claims["ctrl_gross_accrual_not_net_change"] = _build_claim_data(
        name="ctrl_gross_accrual_not_net_change",
        fixture_index=2900,
        ids=_control_ids(19),
        specs=_phase_specs(("O", 1, 5, 3, 1)),
        maximum_online_run=F(3),
        tolerance=F(0),
        reserves=(F(3),),
    )

    recurrence_keys = {
        1: (
            (ClosureDebtComponentKind.e14_reconsolidation, 420002),
            (ClosureDebtComponentKind.f3_route_residue, 420011),
        ),
        2: ((ClosureDebtComponentKind.xi_adequacy_residual, 34000121),),
        3: ((ClosureDebtComponentKind.f3_route_residue, 34000111),),
        4: ((ClosureDebtComponentKind.f3_route_residue, 420031),),
    }
    claims["ctrl_recurrence_uses_online_duration"] = _build_claim_data(
        name="ctrl_recurrence_uses_online_duration",
        fixture_index=3200,
        ids=_control_ids(22),
        specs=_phase_specs(("O", 4, 6, 4, 1), ("F", 1, 0, 6, 0), ("O", 2, 6, 4, 1), ("F", 1, 0, 6, 0)),
        maximum_online_run=F(3),
        tolerance=F(0),
        reserves=(F(6),),
        status=OfflineReclosureStatus.offline_reclosure_rejected,
        forced_discharge_keys=recurrence_keys,
    )

    claims["ctrl_posthoc_tolerance_rejected"] = _build_claim_data(
        name="ctrl_posthoc_tolerance_rejected",
        fixture_index=3300,
        ids=_control_ids(23),
        specs=_phase_specs(("O", 2, 6, 4, 1), ("F", 1, 0, 6, 0), ("O", 2, 6, 4, 1), ("F", 1, 0, 6, 0)),
        maximum_online_run=F(2),
        tolerance=F(1, 24),
        reserves=(F(6), F(6)),
        tolerance_declared_at=F(1),
    )

    claims["ctrl_allocation_postdates_horizon"] = _build_claim_data(
        name="ctrl_allocation_postdates_horizon",
        fixture_index=4700,
        ids=_control_ids(37),
        specs=_phase_specs(("O", 3, 6, 4, 1), ("F", 1, 0, 6, 0), ("O", 3, 6, 4, 1), ("F", 1, 0, 6, 0)),
        maximum_online_run=F(3),
        tolerance=F(0),
        allocation_declared_at=F(1),
    )

    claims["ctrl_offline_overcapacity_is_decorative"] = _build_claim_data(
        name="ctrl_offline_overcapacity_is_decorative",
        fixture_index=4000,
        ids=_control_ids(30),
        specs=_phase_specs(("O", 3, 3, 3, 1), ("F", 1, 0, 6, 0), ("F", 1, 0, 7, 0)),
        maximum_online_run=F(3),
        tolerance=F(0),
        reserves=(F(9),),
        status=OfflineReclosureStatus.decorative_offline,
    )

    capacity_rows = (
        (
            "capacity_persistent",
            5100,
            _phase_specs(("O", 2, 6, 5, 1)),
            (F(10),),
            None,
        ),
        (
            "capacity_bounded",
            5101,
            _phase_specs(("O", 2, 6, 5, 1), ("O", 2, 6, 5, 1)),
            (F(10), F(10)),
            F(44),
        ),
        (
            "capacity_sufficient",
            5102,
            _phase_specs(("O", 2, 3, 5, 1)),
            (F(10),),
            None,
        ),
    )
    for variant, (name, index, specs, reserves, bound) in enumerate(capacity_rows):
        claims[name] = _build_claim_data(
            name=name,
            fixture_index=index,
            ids=_control_ids(41, variant),
            specs=specs,
            maximum_online_run=F(3),
            tolerance=F(0),
            reserves=reserves,
            debt_bound=bound,
        )

    wrong_canonical = _build_claim_data(
        name="ctrl_e14_wrong_canonical_status_rejected",
        fixture_index=5400,
        ids=_control_ids(44),
        specs=_phase_specs(("O", 1, 0, 0, 1)),
        maximum_online_run=F(1),
        tolerance=F(0),
    )
    claims[wrong_canonical.name] = wrong_canonical

    claims["ctrl_offline_flow_off_inventory_rejected"] = _build_claim_data(
        name="ctrl_offline_flow_off_inventory_rejected",
        fixture_index=5500,
        ids=_control_ids(45),
        specs=_phase_specs(("F", 1, 0, 6, 0)),
        maximum_online_run=F(1),
        tolerance=F(0),
        reserves=(F(6),),
    )
    claims["ctrl_discharge_out_of_phase_rejected"] = _build_claim_data(
        name="ctrl_discharge_out_of_phase_rejected",
        fixture_index=5600,
        ids=_control_ids(46),
        specs=_phase_specs(("F", 1, 0, 6, 0)),
        maximum_online_run=F(1),
        tolerance=F(0),
        reserves=(F(6),),
    )

    return _assemble_fixture(claims)


def build_claim_scoping_pair() -> tuple[Fixture, ClaimData, Fixture, ClaimData]:
    shared_scope = ClosureDebtScopeRecord(
        4900,
        CHALLENGE_CLASS,
        ClosureDebtHorizonRecord(1240001, F(0), F(6)),
    )
    scoped_online = _build_claim_data(
        name="ctrl_claim_scoping_online",
        fixture_index=3400,
        ids=_control_ids(24, 0),
        specs=_phase_specs(("O", 3, 3, 3, 1), ("O", 3, 3, 3, 1)),
        maximum_online_run=F(3),
        tolerance=F(0),
        reserves=(F(9),),
        status=OfflineReclosureStatus.online_sufficient,
        scope_override=shared_scope,
    )
    scoped_mismatch = _build_claim_data(
        name="ctrl_claim_scoping_mismatch",
        fixture_index=3401,
        ids=_control_ids(24, 1),
        specs=_phase_specs(
            ("O", 2, 6, 4, 1),
            ("F", 1, 0, 6, 0),
            ("O", 2, 6, 4, 1),
            ("F", 1, 0, 6, 0),
        ),
        maximum_online_run=F(2),
        tolerance=F(1, 24),
        reserves=(F(6), F(6)),
        status=OfflineReclosureStatus.duty_cycle_mismatch,
        scope_override=shared_scope,
    )
    online_fixture = _assemble_fixture({scoped_online.name: scoped_online})
    mismatch_fixture = _assemble_fixture(
        {scoped_mismatch.name: scoped_mismatch}
    )
    return online_fixture, scoped_online, mismatch_fixture, scoped_mismatch


def _status_rows(fixture: Fixture) -> dict[str, StatusRow]:
    names = (
        "claim_alternation_required",
        "claim_online_sufficient",
        "claim_offline_optional",
        "claim_deficit_online_counterexample",
        "claim_decorative_exchange_active",
        "claim_decorative_no_discharge",
        "claim_decorative_bad_reallocation",
        "claim_duty_cycle_mismatch",
        "claim_skipped_offline_cascade",
        "claim_zero_exchange_without_p2",
        "ctrl_offline_overcapacity_is_decorative",
    )
    rows: dict[str, StatusRow] = {}
    for name in names:
        observed, truths, record = classify_offline_reclosure_status(fixture, name)
        rows[name] = StatusRow(name, observed, truths, record)
    return rows


def _control(
    name: str, expected: str, observed: str, passed: bool
) -> ControlRow:
    return ControlRow(name, expected, observed, passed)


def _entry_by_kind(
    entries: tuple[ClosureDebtEntryRecord, ...], kind: ClosureDebtComponentKind
) -> ClosureDebtEntryRecord:
    return next(entry for entry in entries if entry.kind is kind)


def _remove_context_value(
    ctx: OfflineReclosureClassifierContext, field: str, value: object
) -> OfflineReclosureClassifierContext:
    current = getattr(ctx, field)
    return replace(ctx, **{field: frozenset(item for item in current if item != value)})


def _v42_wrong_canonical_status_checks(fixture: Fixture) -> dict[str, object]:
    data = fixture.claims["ctrl_e14_wrong_canonical_status_rejected"]
    snapshot = data.flows[0].before_snapshot
    entry = _entry_by_kind(
        snapshot.entries, ClosureDebtComponentKind.e14_reconsolidation
    )
    if not isinstance(entry.source, E14ResidualDebtSource):
        raise RuntimeError("v42 canonical-status control lacks its E14 source")
    source = entry.source
    raw_native = _e14_collision_fixture(fixture, source)
    raw_cores = e14._evidence_cores(raw_native, source.claim_ref)
    derived_status = next(
        status for status in e14.STATUS_PRIORITY if raw_cores[status]
    )
    collision_source = replace(
        source,
        status_record=replace(
            source.status_record,
            status=derived_status,
        ),
    )
    collision_entry = replace(entry, source=collision_source)
    collision_data = _replace_debt_entry_in_claim(data, entry, collision_entry)
    native = _e14_collision_fixture(fixture, collision_source)
    observed_status, truths, observed_record = e14.classify_reconsolidation_status(
        native, collision_source.claim_ref.name
    )
    concrete_valid = e14.statused_unresolved_evidence(
        native, collision_source.candidate
    )
    repair_valid = all(
        e14.record_repair_evidence(native, candidate)
        for candidate in native.repair_candidates.values()
    )
    coarsening_valid = all(
        e14.record_coarsening_evidence(native, candidate)
        for candidate in native.coarsening_candidates.values()
    )
    occurrence_valid = e14.reconsolidation_status_occurrence_for(
        collision_source.claim_ref, collision_source.status_record
    )
    collision_case = e14.outcome_collision_case(
        native, collision_source.claim_ref, collision_source.status_record
    )
    original_item = e14_residual_debt_item(
        fixture, data.scope, snapshot.observed_at, entry
    )
    collision_item = e14_residual_debt_item(
        fixture,
        collision_data.scope,
        collision_data.flows[0].before_snapshot.observed_at,
        collision_entry,
    )
    credited = collision_entry.amount if collision_item else F(0)
    return {
        "entry": collision_entry,
        "source": collision_source,
        "native_fixture": native,
        "concrete_valid": concrete_valid,
        "repair_valid": repair_valid,
        "coarsening_valid": coarsening_valid,
        "occurrence_valid": occurrence_valid,
        "collision_case": collision_case,
        "observed_status": observed_status,
        "observed_record": observed_record,
        "exactly_one": sum(truths.values()) == 1,
        "original_item": original_item,
        "collision_item": collision_item,
        "credited": credited,
    }


def _v42_off_inventory_flow_checks(fixture: Fixture) -> dict[str, object]:
    data = fixture.claims["ctrl_offline_flow_off_inventory_rejected"]
    phase = data.schedule.phases[0]
    canonical = data.flows[0]

    positive_clone = replace(canonical, flow_id=_id_value(_control_ids(45), "flow", 2))
    positive_member_data = replace(data, flows=(positive_clone,))
    positive_member_fixture = _assemble_fixture(
        {positive_member_data.name: positive_member_data}
    )

    decorative_after = replace(
        canonical.before_snapshot,
        snapshot_id=_id_value(_control_ids(45), "snapshot", 3),
        observed_at=phase.end_time,
    )
    decorative_member = replace(
        canonical,
        flow_id=_id_value(_control_ids(45), "flow", 1),
        after_snapshot=decorative_after,
        accrued_entries=(),
        discharge_records=(),
    )
    decorative_clone = replace(
        decorative_member, flow_id=_id_value(_control_ids(45), "flow", 3)
    )
    decorative_member_data = replace(data, flows=(decorative_member,))
    decorative_member_fixture = _assemble_fixture(
        {decorative_member_data.name: decorative_member_data}
    )

    return {
        "data": data,
        "phase": phase,
        "positive_clone": positive_clone,
        "decorative_clone": decorative_clone,
        "positive_complete": complete_closure_debt_flow(fixture, positive_clone),
        "decorative_complete": complete_closure_debt_flow(
            decorative_member_fixture, decorative_clone
        ),
        "positive_member_accepts": genuine_offline_flow_evidence(
            positive_member_fixture,
            positive_member_data,
            phase,
            positive_clone,
        ),
        "decorative_member_accepts": decorative_offline_flow_evidence(
            decorative_member_fixture,
            decorative_member_data,
            phase,
            decorative_member,
        ),
        "positive_off_inventory": genuine_offline_flow_evidence(
            fixture, data, phase, positive_clone
        ),
        "decorative_off_inventory": decorative_offline_flow_evidence(
            decorative_member_fixture,
            decorative_member_data,
            phase,
            decorative_clone,
        ),
    }


def _v42_out_of_phase_discharge_checks(fixture: Fixture) -> dict[str, object]:
    data = fixture.claims["ctrl_discharge_out_of_phase_rejected"]
    canonical = data.flows[0]
    if len(canonical.discharge_records) != 1:
        raise RuntimeError("v42 timestamp control requires one discharge")
    mutated_discharge = replace(canonical.discharge_records[0], discharged_at=F(2))
    mutated_flow = replace(canonical, discharge_records=(mutated_discharge,))
    checks = complete_closure_debt_flow_checks(fixture, mutated_flow)
    return {
        "data": data,
        "canonical": canonical,
        "mutated_discharge": mutated_discharge,
        "mutated_flow": mutated_flow,
        "checks": checks,
        "other_fields": all(
            value for name, value in checks.items() if name != "everyDischargeLinked"
        ),
        "complete": complete_closure_debt_flow(fixture, mutated_flow),
    }


def _control_rows(fixture: Fixture, rows: dict[str, StatusRow]) -> dict[str, ControlRow]:
    controls: dict[str, ControlRow] = {}
    base = fixture.claims["claim_alternation_required"]
    base_snapshot = base.flows[0].before_snapshot
    base_entries = base_snapshot.entries

    omitted = tuple(
        complete_closure_debt_inventory(
            fixture,
            base.scope,
            base_snapshot.observed_at,
            tuple(candidate for candidate in base_entries if candidate != entry),
        )
        for entry in base_entries
    )
    total = closure_debt(base_entries)
    controls["ctrl_three_source_exact_aggregation"] = _control(
        "ctrl_three_source_exact_aggregation",
        "total=20; source omissions=[false,false,false]",
        f"total={total}; source omissions={list(omitted)}",
        total == 20 and omitted == (False, False, False),
    )

    e14_entry = _entry_by_kind(base_entries, ClosureDebtComponentKind.e14_reconsolidation)
    if not isinstance(e14_entry.source, E14ResidualDebtSource):
        raise RuntimeError("canonical E14 entry has the wrong source type")
    candidate = e14_entry.source.candidate
    lookalike_current = replace(
        candidate.current_record_at_status,
        provenance_root_id=candidate.current_record_at_status.provenance_root_id + 1,
    )
    lookalike = replace(
        e14_entry,
        source=replace(
            e14_entry.source,
            candidate=replace(candidate, current_record_at_status=lookalike_current),
        ),
    )
    e14_valid = e14_residual_debt_item(
        fixture, base.scope, base_snapshot.observed_at, lookalike
    )
    controls["ctrl_e14_direct_witness_required"] = _control(
        "ctrl_e14_direct_witness_required",
        "lookalike credited=0; E14 item=false",
        f"lookalike credited={lookalike.amount if e14_valid else 0}; E14 item={e14_valid}",
        not e14_valid,
    )

    f3_entry = _entry_by_kind(base_entries, ClosureDebtComponentKind.f3_route_residue)
    if not isinstance(f3_entry.source, RouteResidueDebtRecord):
        raise RuntimeError("canonical F3 entry has the wrong source type")
    unregistered_f3_source = replace(f3_entry.source, residue_id=f3_entry.source.residue_id + 999)
    unregistered_f3 = replace(
        f3_entry,
        source=unregistered_f3_source,
        ledger_entry=replace(f3_entry.ledger_entry, source_id=unregistered_f3_source.residue_id),
    )
    f3_valid = f3_route_residue_debt_item(
        fixture, base.scope, base_snapshot.observed_at, unregistered_f3
    )
    controls["ctrl_f3_certificate_required"] = _control(
        "ctrl_f3_certificate_required",
        "F3 item=false",
        f"F3 item={f3_valid}",
        not f3_valid,
    )

    xi_entry = _entry_by_kind(base_entries, ClosureDebtComponentKind.xi_adequacy_residual)
    if not isinstance(xi_entry.source, XiAdequacyResidualDebtRecord):
        raise RuntimeError("canonical Xi entry has the wrong source type")
    posthoc_policy = replace(xi_entry.source.valuation_policy, declared_at=F(1))
    posthoc_xi = replace(
        xi_entry,
        source=replace(
            xi_entry.source,
            valuation_policy=posthoc_policy,
            residual_amount=F(5),
        ),
    )
    declaration_link = posthoc_policy.declared_at <= base.scope.horizon.start_time
    amount_link = (
        posthoc_xi.source.residual_matrix is not None
        and posthoc_xi.source.residual_amount
        == fixture.ctx.xi_residual_amount(posthoc_policy, posthoc_xi.source.residual_matrix)
    )
    posthoc_valid = xi_adequacy_residual_debt_item(
        fixture, base.scope, base_snapshot.observed_at, posthoc_xi
    )
    controls["ctrl_xi_posthoc_scalarization_rejected"] = _control(
        "ctrl_xi_posthoc_scalarization_rejected",
        "Xi item=false; declaration=false; amount link=false",
        f"Xi item={posthoc_valid}; declaration={declaration_link}; amount link={amount_link}",
        not posthoc_valid and not declaration_link and not amount_link,
    )

    no_matrix_xi = replace(
        xi_entry,
        source=replace(
            xi_entry.source,
            C=None,
            L=None,
            D=None,
            KLLdagger=None,
            residual_matrix=None,
        ),
    )
    no_matrix_valid = xi_adequacy_residual_debt_item(
        fixture, base.scope, base_snapshot.observed_at, no_matrix_xi
    )
    controls["ctrl_xi_amount_without_matrix_rejected"] = _control(
        "ctrl_xi_amount_without_matrix_rejected",
        "Xi record/item=false",
        f"Xi record/item={no_matrix_valid}",
        not no_matrix_valid,
    )

    duplicate_charge_entries = (
        f3_entry,
        replace(xi_entry, ledger_entry=f3_entry.ledger_entry),
    )
    duplicate_checks = complete_closure_debt_inventory_checks(
        fixture, base.scope, base_snapshot.observed_at, duplicate_charge_entries
    )
    controls["ctrl_duplicate_physical_ledger_charge"] = _control(
        "ctrl_duplicate_physical_ledger_charge",
        "ledgerChargesNodup=false",
        f"ledgerChargesNodup={duplicate_checks['ledgerChargesNodup']}",
        not duplicate_checks["ledgerChargesNodup"],
    )

    free_geometry = derived_offline_budget_geometry(
        fixture, base.scope, None, None
    )
    controls["ctrl_free_capacity_smuggling_rejected"] = _control(
        "ctrl_free_capacity_smuggling_rejected",
        "geometry=false; positive branch=false",
        f"geometry={free_geometry}; positive branch={free_geometry}",
        not free_geometry,
    )

    geometry = derived_offline_budget_geometry(
        fixture, base.scope, base.budget_data, base.allocation
    )
    low = replace(base.allocation, offline_internal_discharge_allocation=F(11, 2))
    high = replace(base.allocation, offline_internal_discharge_allocation=F(13, 2))
    low_valid = derived_offline_budget_geometry(fixture, base.scope, base.budget_data, low)
    high_valid = derived_offline_budget_geometry(fixture, base.scope, base.budget_data, high)
    equation = kappa_off(base.allocation) == kappa_on(base.allocation) + freed_allocation(base.allocation)
    controls["ctrl_capacity_gain_equation"] = _control(
        "ctrl_capacity_gain_equation",
        "6=4+2; fitted 11/2=false; fitted 13/2=false",
        f"{kappa_off(base.allocation)}={kappa_on(base.allocation)}+{freed_allocation(base.allocation)}; fitted 11/2={low_valid}; fitted 13/2={high_valid}",
        geometry and equation and not low_valid and not high_valid,
    )

    gross = fixture.claims["ctrl_gross_accrual_not_net_change"].flows[0]
    gross_a = closure_debt_accrual_rate(gross)
    gross_d = closure_debt_discharge_rate(gross)
    gross_net = gross.after_snapshot.total_debt - gross.before_snapshot.total_debt
    controls["ctrl_gross_accrual_not_net_change"] = _control(
        "ctrl_gross_accrual_not_net_change",
        "accrual=5; discharge=3; net=2",
        f"accrual={gross_a}; discharge={gross_d}; net={gross_net}",
        (gross_a, gross_d, gross_net) == (F(5), F(3), F(2)),
    )

    boundary_names = ("boundary_rate_7_2", "boundary_rate_4", "boundary_rate_5")
    boundary_statuses = tuple(
        classify_offline_reclosure_status(fixture, name)[0] for name in boundary_names
    )
    controls["sweep_deficit_boundary"] = _control(
        "sweep_deficit_boundary",
        "7/2=online_sufficient; 4=online_sufficient; 5=alternation_required",
        "; ".join(
            f"{rate}={status.value}"
            for rate, status in zip(("7/2", "4", "5"), boundary_statuses, strict=True)
        ),
        boundary_statuses
        == (
            OfflineReclosureStatus.online_sufficient,
            OfflineReclosureStatus.online_sufficient,
            OfflineReclosureStatus.alternation_required,
        ),
    )

    incomplete = replace(base, flows=base.flows[:-1])
    incomplete_checks = phase_flow_inventory_checks(fixture, incomplete)
    rejected_record = replace(
        base.status_record,
        status=OfflineReclosureStatus.offline_reclosure_rejected,
    )
    incomplete = replace(incomplete, status_record=rejected_record)
    incomplete_status = classify_claim_data(fixture, incomplete)[0]
    controls["ctrl_incomplete_phase_flow_inventory"] = _control(
        "ctrl_incomplete_phase_flow_inventory",
        "everyPhaseCovered=false; status=offline_reclosure_rejected",
        f"everyPhaseCovered={incomplete_checks['everyPhaseCovered']}; status={incomplete_status.value}",
        not incomplete_checks["everyPhaseCovered"]
        and incomplete_status is OfflineReclosureStatus.offline_reclosure_rejected,
    )

    recurrence = fixture.claims["ctrl_recurrence_uses_online_duration"]
    recurrence_raw = raw_evidence_truths(fixture, recurrence)
    recurrence_status = classify_offline_reclosure_status(
        fixture, "ctrl_recurrence_uses_online_duration"
    )[0]
    durations = tuple(
        phase_duration(phase) <= recurrence.recurrence_bound.maximum_online_run
        for phase in recurrence.schedule.phases
        if phase.mode is OperatingMode.online
    )
    controls["ctrl_recurrence_uses_online_duration"] = _control(
        "ctrl_recurrence_uses_online_duration",
        "online duration checks=[false,true]; alternation=false; status=offline_reclosure_rejected",
        f"online duration checks={list(durations)}; alternation={recurrence_raw[OfflineReclosureStatus.alternation_required]}; status={recurrence_status.value}",
        durations == (False, True)
        and not recurrence_raw[OfflineReclosureStatus.alternation_required]
        and recurrence_status is OfflineReclosureStatus.offline_reclosure_rejected,
    )

    posthoc = fixture.claims["ctrl_posthoc_tolerance_rejected"]
    posthoc_prediction = duty_cycle_prediction_evidence(fixture, posthoc)
    posthoc_mismatch = duty_cycle_mismatch_evidence(fixture, posthoc)
    controls["ctrl_posthoc_tolerance_rejected"] = _control(
        "ctrl_posthoc_tolerance_rejected",
        "prediction=false; mismatch=false",
        f"prediction={posthoc_prediction}; mismatch={posthoc_mismatch}",
        not posthoc_prediction and not posthoc_mismatch,
    )

    (
        scoped_online_fixture,
        scoped_online,
        scoped_mismatch_fixture,
        scoped_mismatch,
    ) = build_claim_scoping_pair()
    online_status = classify_claim_data(
        scoped_online_fixture, scoped_online
    )[0]
    mismatch_status = classify_claim_data(
        scoped_mismatch_fixture, scoped_mismatch
    )[0]
    cross_matches = (
        offline_reclosure_status_record_matches_claim(
            scoped_online.claim_ref, scoped_mismatch.status_record
        ),
        offline_reclosure_status_record_matches_claim(
            scoped_mismatch.claim_ref, scoped_online.status_record
        ),
    )
    same_scope = scoped_online.claim_ref.scope == scoped_mismatch.claim_ref.scope
    controls["ctrl_claim_scoping"] = _control(
        "ctrl_claim_scoping",
        "shared scope=true; online=online_sufficient; mismatch=duty_cycle_mismatch; cross matches=[false,false]",
        f"shared scope={same_scope}; online={online_status.value}; mismatch={mismatch_status.value}; cross matches={list(cross_matches)}",
        same_scope
        and online_status is OfflineReclosureStatus.online_sufficient
        and mismatch_status is OfflineReclosureStatus.duty_cycle_mismatch
        and cross_matches == (False, False),
    )

    counter = fixture.claims["claim_deficit_online_counterexample"]
    adversarial_record = replace(
        counter.status_record,
        status=OfflineReclosureStatus.alternation_required,
    )
    adversarial_case = case_truths_for_record(fixture, counter, adversarial_record)[
        OfflineReclosureStatus.alternation_required
    ]
    counter_raw = raw_evidence_truths(fixture, counter)[
        OfflineReclosureStatus.deficit_online_counterexample
    ]
    unique_with_both = counter.status_record.status == adversarial_record.status
    controls["ctrl_evidence_priority_not_status_tag"] = _control(
        "ctrl_evidence_priority_not_status_tag",
        "counterexample raw=true; alternation case=false; statusUnique with both=false; canonical=deficit_online_counterexample",
        f"counterexample raw={counter_raw}; alternation case={adversarial_case}; statusUnique with both={unique_with_both}; canonical={rows[counter.name].observed.value}",
        counter_raw
        and not adversarial_case
        and not unique_with_both
        and rows[counter.name].observed is OfflineReclosureStatus.deficit_online_counterexample,
    )

    cascade = fixture.claims["claim_skipped_offline_cascade"]
    if cascade.alarm_observation is None or cascade.stress_observation is None:
        raise RuntimeError("canonical cascade lacks its observations")
    alarm_ctx = _remove_context_value(
        fixture.ctx,
        "accepted_e7_alarm_ids",
        cascade.alarm_observation.observation_id,
    )
    alarm_fixture = replace(fixture, ctx=alarm_ctx)
    alarm_valid = skipped_offline_cascade_evidence(alarm_fixture, cascade)
    controls["ctrl_alarm_without_e7_acceptance"] = _control(
        "ctrl_alarm_without_e7_acceptance",
        "cascade evidence=false",
        f"cascade evidence={alarm_valid}",
        not alarm_valid,
    )

    stress_ctx = _remove_context_value(
        fixture.ctx,
        "accepted_e5_stress_ids",
        cascade.stress_observation.observation_id,
    )
    stress_fixture = replace(fixture, ctx=stress_ctx)
    stress_valid = skipped_offline_cascade_evidence(stress_fixture, cascade)
    controls["ctrl_stress_without_e5_acceptance"] = _control(
        "ctrl_stress_without_e5_acceptance",
        "cascade evidence=false",
        f"cascade evidence={stress_valid}",
        not stress_valid,
    )

    last_phase = cascade.schedule.phases[-1]
    chronology_alarm = replace(
        cascade.alarm_observation, phase_record=last_phase, observed_at=F(11, 2)
    )
    chronology_stress = replace(
        cascade.stress_observation, phase_record=last_phase, observed_at=F(5)
    )
    chronology_data = replace(
        cascade,
        alarm_observation=chronology_alarm,
        stress_observation=chronology_stress,
    )
    outside_alarm = replace(
        cascade,
        alarm_observation=replace(cascade.alarm_observation, observed_at=F(-1)),
    )
    outside_stress = replace(
        cascade,
        stress_observation=replace(cascade.stress_observation, observed_at=F(7)),
    )
    foreign_scope = fixture.claims["claim_online_sufficient"].scope
    wrong_scope = replace(
        cascade,
        alarm_observation=replace(cascade.alarm_observation, scope=foreign_scope),
    )
    foreign_phase = fixture.claims["claim_online_sufficient"].schedule.phases[0]
    wrong_phase_alarm = replace(
        cascade.alarm_observation,
        phase_record=foreign_phase,
        observed_at=foreign_phase.start_time,
    )
    wrong_phase = replace(cascade, alarm_observation=wrong_phase_alarm)
    cascade_mutations = (
        skipped_offline_cascade_evidence(fixture, chronology_data),
        skipped_offline_cascade_evidence(fixture, outside_alarm),
        skipped_offline_cascade_evidence(fixture, outside_stress),
        skipped_offline_cascade_evidence(fixture, wrong_scope),
        skipped_offline_cascade_evidence(fixture, wrong_phase),
    )
    controls["ctrl_cascade_chronology_lineage_mutations"] = _control(
        "ctrl_cascade_chronology_lineage_mutations",
        "five cascade mutations=[false,false,false,false,false]",
        f"five cascade mutations={list(cascade_mutations)}",
        cascade_mutations == (False, False, False, False, False),
    )

    e5_fixture = e5.build_fixture()
    e5_scenario = e5_fixture.scenarios["scn_suspended_gated_operations"]
    suspension = e5_fixture.suspensions["suspension_ops_gate"]
    suspension_valid = e5.suspension_witness(
        e5_fixture, e5_scenario, suspension
    )
    no_e15_offline = not genuine_offline_phase_evidence(
        fixture,
        fixture.claims["claim_zero_exchange_without_p2"],
        fixture.claims["claim_zero_exchange_without_p2"].schedule.phases[0],
    )
    controls["ctrl_e5_suspension_is_not_e15_offline"] = _control(
        "ctrl_e5_suspension_is_not_e15_offline",
        "E5 suspension=true; E15 genuine offline=false",
        f"E5 suspension={suspension_valid}; E15 genuine offline={not no_e15_offline}",
        suspension_valid and no_e15_offline,
    )

    overcapacity = fixture.claims["ctrl_offline_overcapacity_is_decorative"]
    overcapacity_status = rows[overcapacity.name].observed
    overcapacity_optional = optional_offline_outside_deficit_evidence(
        fixture, overcapacity
    )
    controls["ctrl_offline_overcapacity_is_decorative"] = _control(
        "ctrl_offline_overcapacity_is_decorative",
        "decorative_offline; offline_optional=false",
        f"{overcapacity_status.value}; offline_optional={overcapacity_optional}",
        overcapacity_status is OfflineReclosureStatus.decorative_offline
        and not overcapacity_optional,
    )

    positive_exchange = next(
        record for record in base.exchange_records if record.exchanged_amount > 0
    )
    omitted_records = tuple(
        record for record in base.exchange_records if record != positive_exchange
    )
    omission_checks = external_exchange_inventory_checks(
        fixture, base, omitted_records
    )
    controls["ctrl_exchange_census_omission"] = _control(
        "ctrl_exchange_census_omission",
        "completeForSchedule=false",
        f"completeForSchedule={omission_checks['completeForSchedule']}",
        not omission_checks["completeForSchedule"],
    )

    duplicate_records = base.exchange_records + (base.exchange_records[0],)
    duplicate_record_checks = external_exchange_inventory_checks(
        fixture, base, duplicate_records
    )
    controls["ctrl_exchange_census_record_duplicate"] = _control(
        "ctrl_exchange_census_record_duplicate",
        "recordsNodup=false",
        f"recordsNodup={duplicate_record_checks['recordsNodup']}",
        not duplicate_record_checks["recordsNodup"],
    )

    same_id_record = replace(
        base.exchange_records[0],
        exchanged_amount=base.exchange_records[0].exchanged_amount + 1,
    )
    duplicate_ids = base.exchange_records + (same_id_record,)
    duplicate_id_checks = external_exchange_inventory_checks(fixture, base, duplicate_ids)
    controls["ctrl_exchange_census_id_duplicate"] = _control(
        "ctrl_exchange_census_id_duplicate",
        "recordIdsNodup=false",
        f"recordIdsNodup={duplicate_id_checks['recordIdsNodup']}",
        not duplicate_id_checks["recordIdsNodup"],
    )

    first_exchange = base.exchange_records[0]
    uncarried_exchange = replace(
        first_exchange,
        carried=replace(first_exchange.carried, source_tag=FineSourceTag.fallback),
    )
    foreign_exchange = replace(
        first_exchange,
        exchange_record_id=first_exchange.exchange_record_id + 900000,
        phase_record=foreign_phase,
        recorded_at=foreign_phase.start_time,
    )
    negative_exchange = replace(
        first_exchange,
        exchange_record_id=first_exchange.exchange_record_id + 900001,
        exchanged_amount=F(-1),
    )
    late_exchange = replace(
        first_exchange,
        exchange_record_id=first_exchange.exchange_record_id + 900002,
        recorded_at=first_exchange.phase_record.end_time + 1,
    )
    eligibility = (
        eligible_external_exchange(base, uncarried_exchange),
        eligible_external_exchange(base, foreign_exchange),
        eligible_external_exchange(base, negative_exchange),
        eligible_external_exchange(base, late_exchange),
    )
    one_phase_records = tuple(
        record
        for record in base.exchange_records
        if record.phase_record != base.schedule.phases[-1]
    )
    unsound_inventory = one_phase_records + (
        uncarried_exchange,
        foreign_exchange,
        negative_exchange,
        late_exchange,
    )
    eligibility_checks = external_exchange_inventory_checks(
        fixture, base, unsound_inventory
    )
    controls["ctrl_exchange_eligibility_soundness_matrix"] = _control(
        "ctrl_exchange_eligibility_soundness_matrix",
        "eligibility=[false,false,false,false]; soundness=false; phase coverage=false",
        f"eligibility={list(eligibility)}; soundness={eligibility_checks['soundForSchedule']}; phase coverage={eligibility_checks['everyPhaseCovered']}",
        eligibility == (False, False, False, False)
        and not eligibility_checks["soundForSchedule"]
        and not eligibility_checks["everyPhaseCovered"],
    )

    gate = base.gates[0]
    baseline_alarm = cascade.alarm_observation
    baseline_stress = cascade.stress_observation
    baseline_context_values = (
        fixture.ctx.e14_residual_outstanding(
            e14_entry.source.registration_record, base_snapshot.observed_at
        ),
        fixture.ctx.f3_route_residue_awaiting_reconciliation(
            f3_entry.source, base_snapshot.observed_at
        ),
        fixture.ctx.xi_valuation_policy_accepted(xi_entry.source.valuation_policy),
        fixture.ctx.xi_residual_awaiting_discharge(
            xi_entry.source, base_snapshot.observed_at
        ),
        fixture.ctx.ledger_entry_charges_route_residue(
            f3_entry.ledger_entry, f3_entry.source, f3_entry.amount
        ),
        fixture.ctx.ledger_entry_charges_xi_residual(
            xi_entry.ledger_entry, xi_entry.source, xi_entry.amount
        ),
        fixture.ctx.gate_closes_external_exchange(gate),
        fixture.ctx.e7_alarm_observation_accepted(baseline_alarm),
        fixture.ctx.e5_stress_observation_accepted(baseline_stress),
    )
    if xi_entry.source.residual_matrix is None:
        raise RuntimeError("canonical Xi entry lacks its computed matrix")
    xi_amount_equal = xi_entry.source.residual_amount == fixture.ctx.xi_residual_amount(
        xi_entry.source.valuation_policy, xi_entry.source.residual_matrix
    )
    context_mutations = (
        fixture.ctx.e14_residual_outstanding(
            replace(
                e14_entry.source.registration_record,
                registration_id=e14_entry.source.registration_record.registration_id + 999,
            ),
            base_snapshot.observed_at,
        ),
        fixture.ctx.f3_route_residue_awaiting_reconciliation(
            replace(f3_entry.source, residue_id=f3_entry.source.residue_id + 999),
            base_snapshot.observed_at,
        ),
        fixture.ctx.xi_valuation_policy_accepted(
            replace(
                xi_entry.source.valuation_policy,
                valuation_policy_id=xi_entry.source.valuation_policy.valuation_policy_id + 999,
            )
        ),
        xi_entry.source.residual_amount
        == fixture.ctx.xi_residual_amount(
            xi_entry.source.valuation_policy, ((xi_entry.source.residual_amount + 1,),)
        ),
        fixture.ctx.xi_residual_awaiting_discharge(
            replace(xi_entry.source, residual_id=xi_entry.source.residual_id + 999),
            base_snapshot.observed_at,
        ),
        fixture.ctx.ledger_entry_charges_route_residue(
            replace(f3_entry.ledger_entry, source_id=f3_entry.source.residue_id + 1, amount=f3_entry.amount + 1),
            f3_entry.source,
            f3_entry.amount,
        ),
        fixture.ctx.ledger_entry_charges_xi_residual(
            replace(xi_entry.ledger_entry, source_id=xi_entry.source.residual_id + 1, amount=xi_entry.amount + 1),
            xi_entry.source,
            xi_entry.amount,
        ),
        replace(
            fixture.ctx,
            external_channel_by_gate=tuple(
                (identifier, "other_channel" if identifier == gate.gate_record_id else channel)
                for identifier, channel in fixture.ctx.external_channel_by_gate
            ),
        ).gate_closes_external_exchange(gate),
        alarm_fixture.ctx.e7_alarm_observation_accepted(baseline_alarm),
        stress_fixture.ctx.e5_stress_observation_accepted(baseline_stress),
    )
    controls["ctrl_shared_context_mutation_matrix"] = _control(
        "ctrl_shared_context_mutation_matrix",
        "nine predicates=true; Xi equality=true; ten mutations=false",
        f"nine predicates={all(baseline_context_values)}; Xi equality={xi_amount_equal}; mutations={list(context_mutations)}",
        all(baseline_context_values)
        and xi_amount_equal
        and context_mutations == (False,) * 10,
    )

    representatives = (
        f3_entry.source,
        base.allocation,
        base.schedule.phases[0],
        base.exchange_records[0],
        base.gates[0],
        base.flows[0],
        base.status_record,
    )
    carried_matrix: list[tuple[bool, bool, bool]] = []
    for record in representatives:
        fact = record.carried
        carried_matrix.append(
            (
                _record_carried(replace(record, carried=replace(fact, source_tag=FineSourceTag.fallback))),
                _record_carried(replace(record, carried=replace(fact, generated_by_s=False))),
                _record_carried(replace(record, carried=replace(fact, in_scope=False))),
            )
        )
    controls["ctrl_carriedness_conjunction_mutations"] = _control(
        "ctrl_carriedness_conjunction_mutations",
        "seven representative vectors=[false,false,false]",
        f"vectors={carried_matrix}",
        carried_matrix == [(False, False, False)] * len(representatives),
    )

    postdated = fixture.claims["ctrl_allocation_postdates_horizon"]
    postdated_geometry = derived_offline_budget_geometry(
        fixture, postdated.scope, postdated.budget_data, postdated.allocation
    )
    controls["ctrl_allocation_postdates_horizon"] = _control(
        "ctrl_allocation_postdates_horizon",
        "geometry=false",
        f"geometry={postdated_geometry}",
        not postdated_geometry,
    )

    gate_data = fixture.claims["claim_offline_optional"]
    gate_phase = next(
        phase for phase in gate_data.schedule.phases if phase.mode is OperatingMode.offline
    )
    canonical_gate = next(gate for gate in gate_data.gates if gate.phase_record == gate_phase)
    uncarried_gate = replace(
        canonical_gate,
        carried=replace(canonical_gate.carried, source_tag=FineSourceTag.fallback),
    )
    wrong_phase_gate = replace(canonical_gate, phase_record=gate_data.schedule.phases[0])
    broken_action = replace(
        canonical_gate.action,
        repair_package={item: "unlinked_gate" for item in ITEMS},
    )
    broken_generator_gate = replace(canonical_gate, action=broken_action)
    wrong_sort_gate = replace(canonical_gate, sort=RepairSort.P1)
    unlawful_gate = replace(
        canonical_gate,
        action=replace(canonical_gate.action, z_next=0),
    )
    rejected_gate_ctx = _remove_context_value(
        fixture.ctx,
        "accepted_external_gate_ids",
        canonical_gate.gate_record_id,
    )
    rejected_gate_fixture = replace(fixture, ctx=rejected_gate_ctx)
    gate_mutations = (
        p2_external_exchange_gate_evidence(fixture, gate_phase, uncarried_gate),
        p2_external_exchange_gate_evidence(fixture, gate_phase, wrong_phase_gate),
        p2_external_exchange_gate_evidence(fixture, gate_phase, broken_generator_gate),
        p2_external_exchange_gate_evidence(fixture, gate_phase, wrong_sort_gate),
        p2_external_exchange_gate_evidence(fixture, gate_phase, unlawful_gate),
        p2_external_exchange_gate_evidence(
            rejected_gate_fixture, gate_phase, canonical_gate
        ),
    )
    controls["ctrl_p2_gate_component_mutations"] = _control(
        "ctrl_p2_gate_component_mutations",
        "six P2 mutations=false; exchange=0",
        f"six P2 mutations={list(gate_mutations)}; exchange={exchange_in_phase(gate_data.exchange_records, gate_phase)}",
        gate_mutations == (False,) * 6
        and exchange_in_phase(gate_data.exchange_records, gate_phase) == 0,
    )

    base_record = base.status_record
    if base_record is None:
        raise RuntimeError("canonical status record is missing")
    other = fixture.claims["claim_online_sufficient"]
    claim_match_mutations = (
        replace(base_record, scope=other.scope),
        replace(base_record, allocation_record=other.allocation),
        replace(base_record, schedule=other.schedule),
        replace(base_record, tolerance_record=other.tolerance),
        replace(base_record, recurrence_bound=other.recurrence_bound),
    )
    match_results = tuple(
        offline_reclosure_status_record_matches_claim(base.claim_ref, record)
        for record in claim_match_mutations
    )
    controls["ctrl_claim_match_key_mutations"] = _control(
        "ctrl_claim_match_key_mutations",
        "five claim matches=false",
        f"five claim matches={list(match_results)}",
        match_results == (False,) * 5,
    )

    first_flow = base.flows[0]
    duplicate_debt_checks = complete_closure_debt_inventory_checks(
        fixture,
        base.scope,
        base_snapshot.observed_at,
        (base_entries[0], base_entries[0]),
    )
    duplicate_accrual = replace(
        first_flow,
        accrued_entries=(first_flow.accrued_entries[0], first_flow.accrued_entries[0]),
    )
    accrual_checks = complete_closure_debt_flow_checks(fixture, duplicate_accrual)
    if len(first_flow.discharge_records) < 2:
        raise RuntimeError("canonical flow lacks two discharge records")
    duplicate_id_records = (
        first_flow.discharge_records[0],
        replace(
            first_flow.discharge_records[1],
            discharge_id=first_flow.discharge_records[0].discharge_id,
        ),
    )
    duplicate_ids_flow = replace(first_flow, discharge_records=duplicate_id_records)
    discharge_id_checks = complete_closure_debt_flow_checks(fixture, duplicate_ids_flow)
    duplicate_entry_records = (
        first_flow.discharge_records[0],
        replace(
            first_flow.discharge_records[1],
            debt_entry=first_flow.discharge_records[0].debt_entry,
            amount=first_flow.discharge_records[0].amount,
        ),
    )
    duplicate_entries_flow = replace(first_flow, discharge_records=duplicate_entry_records)
    discharge_entry_checks = complete_closure_debt_flow_checks(
        fixture, duplicate_entries_flow
    )
    duplicate_vector = (
        duplicate_debt_checks["keysNodup"],
        accrual_checks["accruedEntriesNodup"],
        discharge_id_checks["dischargesNodup"],
        discharge_entry_checks["dischargedEntriesNodup"],
    )
    controls["ctrl_debt_and_flow_duplicate_safety"] = _control(
        "ctrl_debt_and_flow_duplicate_safety",
        "duplicate-safety vector=[false,false,false,false]",
        f"duplicate-safety vector={list(duplicate_vector)}",
        duplicate_vector == (False, False, False, False),
    )

    capacity_persistent = fixture.claims["capacity_persistent"]
    capacity_bounded = fixture.claims["capacity_bounded"]
    capacity_sufficient = fixture.claims["capacity_sufficient"]
    capacity_results = (
        persistent_deficit_evidence(fixture, capacity_persistent),
        deficit_online_bounded_counterexample(fixture, capacity_bounded),
        online_sufficient_evidence(fixture, capacity_sufficient),
    )
    capacity_rates = tuple(
        closure_debt_discharge_rate(data.flows[0])
        for data in (capacity_persistent, capacity_bounded, capacity_sufficient)
    )
    capacity_noncapacity_checks = (
        persistent_deficit_noncapacity_checks(fixture, capacity_persistent),
        bounded_counterexample_noncapacity_checks(fixture, capacity_bounded),
        online_sufficient_noncapacity_checks(fixture, capacity_sufficient),
    )
    capacity_other_fields = tuple(
        all(checks.values()) for checks in capacity_noncapacity_checks
    )
    controls["ctrl_online_discharge_capacity_bound"] = _control(
        "ctrl_online_discharge_capacity_bound",
        "persistent/bounded/sufficient=[false,false,false]; rates=[5,5,5]; other fields=[true,true,true]",
        f"persistent/bounded/sufficient={list(capacity_results)}; rates={list(capacity_rates)}; other fields={list(capacity_other_fields)}",
        capacity_results == (False, False, False)
        and capacity_rates == (F(5), F(5), F(5))
        and capacity_other_fields == (True, True, True),
    )

    ablations = tuple(fixture.claims[f"ablation_trace_{index}"] for index in range(1, 5))
    alarm_count = sum(
        data.alarm_observation is not None
        and fixture.ctx.e7_alarm_observation_accepted(data.alarm_observation)
        for data in ablations
    )
    stress_count = sum(
        data.stress_observation is not None
        and fixture.ctx.e5_stress_observation_accepted(data.stress_observation)
        for data in ablations
    )
    chronology_count = sum(skipped_offline_cascade_evidence(fixture, data) for data in ablations)
    controls["census_offline_ablation_alarm_stress"] = _control(
        "census_offline_ablation_alarm_stress",
        "alarm/stress/chronology=4/4/4; collapse comparison absent",
        f"alarm/stress/chronology={alarm_count}/{stress_count}/{chronology_count}; collapse comparison absent",
        (alarm_count, stress_count, chronology_count) == (4, 4, 4),
    )

    primary_names = tuple(name for name, *_rest in (
        ("claim_alternation_required",),
        ("claim_online_sufficient",),
        ("claim_offline_optional",),
        ("claim_deficit_online_counterexample",),
        ("claim_decorative_exchange_active",),
        ("claim_decorative_no_discharge",),
        ("claim_decorative_bad_reallocation",),
        ("claim_duty_cycle_mismatch",),
        ("claim_skipped_offline_cascade",),
        ("claim_zero_exchange_without_p2",),
    ))
    primary_exact = all(
        complete_offline_reclosure_status(fixture, name)
        and sum(rows[name].truths.values()) == 1
        for name in primary_names
    )
    counter_lower = all(
        not rows["claim_deficit_online_counterexample"].truths[status]
        for status in STATUS_PRIORITY[1:]
    )
    controls["ctrl_eight_way_partition_and_top_exclusion"] = _control(
        "ctrl_eight_way_partition_and_top_exclusion",
        "ten claims exactly one; counterexample lower holds=false",
        f"ten claims exactly one={primary_exact}; counterexample lower holds={not counter_lower}",
        primary_exact and counter_lower,
    )

    canonical_checks = _v42_wrong_canonical_status_checks(fixture)
    canonical_item = bool(canonical_checks["collision_item"])
    canonical_credit = canonical_checks["credited"]
    controls["ctrl_e14_wrong_canonical_status_rejected"] = _control(
        "ctrl_e14_wrong_canonical_status_rejected",
        "E14 debt item false; credited E14 amount 0",
        f"E14 debt item {str(canonical_item).lower()}; credited E14 amount {canonical_credit}",
        bool(canonical_checks["concrete_valid"])
        and bool(canonical_checks["repair_valid"])
        and bool(canonical_checks["coarsening_valid"])
        and bool(canonical_checks["occurrence_valid"])
        and bool(canonical_checks["collision_case"])
        and canonical_checks["observed_status"]
        is e14.ReconsolidationStatus.outcome_collision
        and bool(canonical_checks["exactly_one"])
        and bool(canonical_checks["original_item"])
        and not canonical_item
        and canonical_credit == 0,
    )

    inventory_checks = _v42_off_inventory_flow_checks(fixture)
    genuine_off_inventory = bool(inventory_checks["positive_off_inventory"])
    decorative_off_inventory = bool(
        inventory_checks["decorative_off_inventory"]
    )
    controls["ctrl_offline_flow_off_inventory_rejected"] = _control(
        "ctrl_offline_flow_off_inventory_rejected",
        "genuine offline false; decorative offline false",
        f"genuine offline {str(genuine_off_inventory).lower()}; "
        f"decorative offline {str(decorative_off_inventory).lower()}",
        bool(inventory_checks["positive_complete"])
        and bool(inventory_checks["decorative_complete"])
        and bool(inventory_checks["positive_member_accepts"])
        and bool(inventory_checks["decorative_member_accepts"])
        and not genuine_off_inventory
        and not decorative_off_inventory,
    )

    timestamp_checks = _v42_out_of_phase_discharge_checks(fixture)
    discharge_linked = bool(timestamp_checks["checks"]["everyDischargeLinked"])
    flow_complete = bool(timestamp_checks["complete"])
    controls["ctrl_discharge_out_of_phase_rejected"] = _control(
        "ctrl_discharge_out_of_phase_rejected",
        "everyDischargeLinked = false; CompleteClosureDebtFlow = false",
        f"everyDischargeLinked = {str(discharge_linked).lower()}; "
        f"CompleteClosureDebtFlow = {str(flow_complete).lower()}",
        bool(timestamp_checks["other_fields"])
        and not discharge_linked
        and not flow_complete,
    )

    return controls


def _status_display(
    fixture: Fixture, name: str, status: OfflineReclosureStatus
) -> str:
    data = fixture.claims[name]
    if name == "claim_alternation_required":
        online = next(
            phase
            for phase in data.schedule.phases
            if phase.mode is OperatingMode.online
        )
        flow = _flow_for_phase(data, online)
        if flow is None:
            return f"{status.value}; observed_duty=missing; predicted_duty=missing"
        return (
            f"{status.value}; observed_duty={observed_offline_duty(data.schedule)}; "
            f"predicted_duty={predicted_offline_duty(closure_debt_accrual_rate(flow), data.allocation)}"
        )
    if name == "claim_online_sufficient":
        return f"{status.value}; alternation={duty_cycle_prediction_evidence(fixture, data)}"
    if name == "claim_deficit_online_counterexample":
        lower = any(case_truths_for_record(fixture, data, data.status_record)[candidate] for candidate in STATUS_PRIORITY[1:])
        return f"{status.value}; lower_holds={lower}"
    if name == "claim_decorative_exchange_active":
        return f"{status.value}; exchange={exchange_in_phase(data.exchange_records, data.schedule.phases[0])}"
    if name == "claim_decorative_no_discharge":
        return f"{status.value}; discharged={discharged_debt(data.flows[0])}"
    if name == "claim_decorative_bad_reallocation":
        return f"{status.value}; exact_allocation={data.schedule.phases[0].allocation_record == data.allocation}"
    if name == "claim_duty_cycle_mismatch":
        online = next(phase for phase in data.schedule.phases if phase.mode is OperatingMode.online)
        flow = _flow_for_phase(data, online)
        if flow is None:
            return f"{status.value}; error=missing_flow"
        error = abs(
            observed_offline_duty(data.schedule)
            - predicted_offline_duty(closure_debt_accrual_rate(flow), data.allocation)
        )
        return (
            f"{status.value}; observed_duty={observed_offline_duty(data.schedule)}; "
            f"predicted_duty={predicted_offline_duty(closure_debt_accrual_rate(flow), data.allocation)}; "
            f"error={error}>{data.tolerance.tolerance}"
        )
    if name == "claim_zero_exchange_without_p2":
        phase = data.schedule.phases[0]
        gate = any(p2_external_exchange_gate_evidence(fixture, phase, candidate) for candidate in data.gates)
        return f"{status.value}; census={exchange_in_phase(data.exchange_records, phase)}; gate={gate}"
    if name == "ctrl_offline_overcapacity_is_decorative":
        return f"{status.value}; offline_optional={optional_offline_outside_deficit_evidence(fixture, data)}"
    return status.value


def _status_expected_display(fixture: Fixture, name: str) -> str:
    record = fixture.claims[name].status_record
    if record is None:
        return OfflineReclosureStatus.unclassified.value
    return _status_display(fixture, name, record.status)


def _comparisons(
    fixture: Fixture, rows: dict[str, StatusRow], controls: dict[str, ControlRow]
) -> tuple[Comparison, ...]:
    comparisons: list[Comparison] = []
    for name in REGISTERED_COMPARISON_ORDER:
        if name.endswith(".status"):
            row_name = name.removesuffix(".status")
            row = rows[row_name]
            observed = _status_display(fixture, row_name, row.observed)
            expected = _status_expected_display(fixture, row_name)
            comparisons.append(Comparison(name, observed == expected, observed, expected))
        else:
            control = controls[name]
            comparisons.append(
                Comparison(name, control.passed_control, control.observed, control.expected)
            )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture, rows: dict[str, StatusRow]) -> bool:
    return all(
        row.status_record is not None
        and offline_reclosure_status_occurrence_for(
            fixture.claims[name].claim_ref, row.status_record
        )
        and complete_offline_reclosure_status(fixture, name)
        for name, row in rows.items()
    )


def _no_hardcoded_status_discipline(
    rows: dict[str, StatusRow], controls: dict[str, ControlRow]
) -> bool:
    return all(
        row.status_record is not None
        and row.observed is not OfflineReclosureStatus.unclassified
        and sum(row.truths.values()) == 1
        and row.truths[row.observed]
        and row.observed is row.status_record.status
        for row in rows.values()
    ) and all(control.passed_control for control in controls.values())


def run_e15_offline_reclosure_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = _status_rows(fixture)
    controls = _control_rows(fixture, rows)
    comparisons = _comparisons(fixture, rows, controls)
    return SweepResults(
        rows,
        controls,
        comparisons,
        _actual_scope_discipline(fixture, rows),
        _no_hardcoded_status_discipline(rows, controls),
    )


def format_results_markdown(results: SweepResults) -> str:
    failures = tuple(comparison for comparison in results.comparisons if not comparison.passed)
    lines = [
        "# E15 Offline Reclosure Sweep Results",
        "",
        f"Overall verdict: {'PASS' if not failures else 'FAIL'}",
        f"Registered comparisons: {len(results.comparisons)}",
        "",
        "## Registered Prediction Comparisons",
        "",
        "| comparison | verdict | observed | expected |",
        "| --- | --- | --- | --- |",
    ]
    for comparison in results.comparisons:
        lines.append(
            f"| {comparison.name} | {'PASS' if comparison.passed else 'FAIL'} | "
            f"`{comparison.observed}` | `{comparison.expected}` |"
        )
    lines.extend(
        [
            "",
            "## Discipline Checks",
            "",
            f"- Actual scope discipline: `{results.actual_scope_discipline}`",
            f"- No hardcoded status discipline: `{results.no_hardcoded_status_discipline}`",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_e15_offline_reclosure_sweep()
    path.write_text(format_results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    passed = sum(comparison.passed for comparison in results.comparisons)
    total = len(results.comparisons)
    print(f"E15 offline reclosure sweep: {passed}/{total} comparisons PASS")
    for comparison in results.comparisons:
        verdict = "PASS" if comparison.passed else "FAIL"
        print(
            f"{verdict}: {comparison.name}: "
            f"observed={comparison.observed} expected={comparison.expected}"
        )


if __name__ == "__main__":
    main()
