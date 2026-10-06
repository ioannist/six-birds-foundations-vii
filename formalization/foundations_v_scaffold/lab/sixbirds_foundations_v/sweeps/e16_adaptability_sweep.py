"""E16 adaptability sweep against the committed Round A predictions.

The sweep builds finite route-transport cores, exact repair-ledger trial
inventories, the E15 route-residue bridge, and the four Holonomy controls from
records.  Classification uses claim-scoped raw evidence in the Lean priority
order.  The vendored Lean/Python Holonomy implementations are deliberately not
calculation dependencies.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum
from fractions import Fraction
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Callable, Iterable

from sixbirds_foundations_v.carried_records import FineSourceTag, carried_source
from sixbirds_foundations_v.probe_economy import ActiveFamily, ProbeMove, ProbeMoveKind
import sixbirds_foundations_v.sweeps.e14_reconsolidation_sweep as e14
import sixbirds_foundations_v.sweeps.e15_offline_reclosure_sweep as e15
from sixbirds_foundations_v.worlds.repair_world import RepairAction, is_lawful_action


F = Fraction
HISTORIES = ("FF", "FT", "TF", "TT")
C_REPAIR = "C_repair"
C_SHIFT = "C_shift"
CLASSES = (C_REPAIR, C_SHIFT)
AUXILIARY_CLASSES = ("C_aux_repair", "C_aux_shift")

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT / "formalization" / "notes" / "sweeps" / "E16_adaptability_results.md"
)

REGISTERED_COMPARISON_ORDER = (
    "claim_coherent_wheel.status",
    "claim_support_confound.status",
    "claim_artifact_trap.status",
    "claim_flat_future.status",
    "claim_flat_equal_capacity.status",
    "claim_flattenable.status",
    "claim_currentizable.status",
    "claim_dissipative.status",
    "claim_rejected_perturbation.status",
    "claim_rejected_unbound_flat.status",
    "claim_coherent_wheel.current_audit",
    "claim_coherent_wheel.route_capacity",
    "claim_coherent_wheel.loop_anchor",
    "six_regime_census",
    "ctrl_support_only",
    "ctrl_flattening_only",
    "ctrl_currentization_only",
    "ctrl_dissipation_only",
    "ctrl_perturbation_only",
    "ctrl_e15_still_outstanding",
    "ctrl_e15_reconciled",
    "ctrl_e15_disconnected_same_id",
    "ctrl_undeclared_proxy",
    "ctrl_wrong_route_endpoint",
    "ctrl_different_protocols",
    "ctrl_route_inadmissible",
    "ctrl_package_undeclared",
    "ctrl_budget_linkage",
    "ctrl_undeclared_challenge_difference",
    "ctrl_missing_declared_class",
    "ctrl_duplicate_probability_record",
    "ctrl_duplicate_probability_id",
    "ctrl_contradictory_same_class",
    "ctrl_uncarried_ledger_support",
    "ctrl_uncarried_distribution",
    "ctrl_probability_ledger_computation",
    "ctrl_ledger_relevance",
    "ctrl_exact_denominator",
    "ctrl_trial_inventory_omission",
    "ctrl_protocol_inventory_omission",
    "ctrl_completion_inventory_omission",
    "ctrl_refinement_inventory_omission",
    "ctrl_continuation_inventory_omission",
    "ctrl_perturbation_inventory_omission",
    "ctrl_duplicate_counterpart_key",
    "ctrl_unregistered_dissipating_continuation",
    "ctrl_completion_label_without_collapse",
    "ctrl_changed_support_refinement",
    "ctrl_out_of_bound_perturbation",
    "ctrl_wrong_claim_route",
    "ctrl_wrong_claim_challenge",
    "ctrl_wrong_claim_protocol",
    "ctrl_wrong_claim_time",
    "ctrl_priority_artifact_flattening_collision",
    "ctrl_lower_tag_with_raw_artifact",
    "ctrl_status_uniqueness",
    "mut_counterpart_admissibility",
    "mut_honest_protocol_clears",
    "mut_completion_clears",
    "mut_refinement_currentizes",
    "mut_continuation_dissipates",
    "mut_perturbation_survival",
    "mut_e15_bridge_acceptance",
    "mut_e15_outstanding_status",
    "mut_carriedness_fields",
    "mut_predictive_reveal",
    "ctrl_flat_unrelated_pair_rejected",
    "ctrl_perturbation_off_universe_rejected",
    "ctrl_swapped_trial_populations_rejected",
)


class AdaptabilityStatus(str, Enum):
    support_confound = "support_confound"
    artifact = "artifact"
    flat = "flat"
    flattenable = "flattenable"
    currentizable_slack = "currentizable_slack"
    dissipative = "dissipative"
    coherent_adaptability = "coherent_adaptability"
    adaptability_rejected = "adaptability_rejected"
    unclassified = "unclassified"


STATUS_PRIORITY = (
    AdaptabilityStatus.support_confound,
    AdaptabilityStatus.artifact,
    AdaptabilityStatus.flat,
    AdaptabilityStatus.flattenable,
    AdaptabilityStatus.currentizable_slack,
    AdaptabilityStatus.dissipative,
    AdaptabilityStatus.coherent_adaptability,
    AdaptabilityStatus.adaptability_rejected,
)


@dataclass(frozen=True)
class CarriedFact:
    n0: int = 0
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True
    present: bool = True


CARRIED = CarriedFact()


def _freeze_for_hash(value: object) -> object:
    if isinstance(value, Mapping):
        return frozenset(
            (_freeze_for_hash(key), _freeze_for_hash(item))
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_for_hash(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze_for_hash(item) for item in value)
    if is_dataclass(value) and not isinstance(value, type):
        return (
            type(value),
            tuple(
                (field.name, _freeze_for_hash(getattr(value, field.name)))
                for field in fields(value)
            ),
        )
    hash(value)
    return value


def e16_carried(record: object) -> bool:
    fact = getattr(record, "carried", None)
    return (
        isinstance(fact, (CarriedFact, e15.CarriedFact))
        and fact.present
        and fact.n0 >= 0
        and carried_source(fact.source_tag, fact.generated_by_s, fact.in_scope)
    )


WheelMap = tuple[int, ...]


@dataclass(frozen=True)
class NativeRouteTransportCore:
    name: str
    histories: tuple[str, ...]
    observations: tuple[bool, ...]
    continuations: tuple[WheelMap, ...]
    identity: WheelMap

    def push(self, history: str, continuation: WheelMap) -> str:
        return self.histories[continuation[self.histories.index(history)]]

    def compose(self, first: WheelMap, second: WheelMap) -> WheelMap:
        return tuple(second[first[index]] for index in range(len(self.histories)))


def _all_maps(size: int) -> tuple[WheelMap, ...]:
    return tuple(tuple(values) for values in product(range(size), repeat=size))


def wheel_core() -> NativeRouteTransportCore:
    return NativeRouteTransportCore(
        "wheel",
        HISTORIES,
        (False, False, True, True),
        _all_maps(4),
        (0, 1, 2, 3),
    )


def flat_native_core() -> NativeRouteTransportCore:
    return NativeRouteTransportCore("flat_native", ("F", "T"), (False, True), ((0, 1),), (0, 1))


def no_reveal_core() -> NativeRouteTransportCore:
    return NativeRouteTransportCore(
        "no_reveal_core", HISTORIES, (False, False, True, True), ((0, 1, 2, 3), (1, 0, 3, 2)), (0, 1, 2, 3)
    )


@lru_cache(maxsize=None)
def core_laws(core: NativeRouteTransportCore) -> bool:
    history_indices = range(len(core.histories))
    continuation_set = set(core.continuations)
    return (
        core.identity in continuation_set
        and all(core.push(history, core.identity) == history for history in core.histories)
        and all(
            core.compose(first, second) in continuation_set
            and core.push(core.push(core.histories[index], first), second)
            == core.push(core.histories[index], core.compose(first, second))
            for first in core.continuations
            for second in core.continuations
            for index in history_indices
        )
    )


def observe(core: NativeRouteTransportCore, history: str) -> bool:
    return core.observations[core.histories.index(history)]


@lru_cache(maxsize=None)
def current_event_equiv(core: NativeRouteTransportCore, left: str, right: str) -> bool:
    return observe(core, left) == observe(core, right)


@lru_cache(maxsize=None)
def future_predictive_equiv(core: NativeRouteTransportCore, left: str, right: str) -> bool:
    return all(
        observe(core, core.push(left, continuation))
        == observe(core, core.push(right, continuation))
        for continuation in core.continuations
    )


@lru_cache(maxsize=None)
def quotient_classes(
    core: NativeRouteTransportCore, relation: Callable[[NativeRouteTransportCore, str, str], bool]
) -> tuple[tuple[str, ...], ...]:
    remaining = list(core.histories)
    classes: list[tuple[str, ...]] = []
    while remaining:
        representative = remaining[0]
        block = tuple(item for item in remaining if relation(core, representative, item))
        classes.append(block)
        remaining = [item for item in remaining if item not in block]
    return tuple(classes)


def quotient_class(core: NativeRouteTransportCore, history: str, *, predictive: bool) -> int:
    relation = future_predictive_equiv if predictive else current_event_equiv
    return next(index for index, block in enumerate(quotient_classes(core, relation)) if history in block)


@lru_cache(maxsize=None)
def flat_at(core: NativeRouteTransportCore) -> bool:
    return all(
        current_event_equiv(core, left, right) == future_predictive_equiv(core, left, right)
        for left in core.histories
        for right in core.histories
    )


ELL0 = (1, 0, 3, 2)
REVEAL = (0, 3, 0, 3)
ERASE_LATENT = (0, 0, 2, 2)


@dataclass(frozen=True)
class ComparisonBaseRecord:
    base_id: int
    support: tuple[str, ...]
    declared_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RoutePackageRecord:
    package_id: int
    comparison_base: ComparisonBaseRecord
    core: NativeRouteTransportCore
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RoutePairRecord:
    route_pair_id: int
    package: RoutePackageRecord
    source: str
    gamma: WheelMap
    eta: WheelMap
    gamma_endpoint: str
    eta_endpoint: str
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ChallengeFamilyRecord:
    family_id: int
    classes: tuple[str, ...]
    declared_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ProtocolRecord:
    protocol_id: int
    family: ChallengeFamilyRecord
    measured_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class LedgerEntry:
    ledger_entry_id: int
    trial_id: int
    amount: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RepairTrialRecord:
    trial_id: int
    route_endpoint: str
    challenge_class: str
    discharge_entry: LedgerEntry
    ledger_before: tuple[int, ...]
    ledger_after: tuple[int, ...]
    repair_action: RepairAction
    observed_at: Fraction
    carried: CarriedFact = CARRIED

    def __hash__(self) -> int:
        return hash(
            _freeze_for_hash((
                self.trial_id,
                self.route_endpoint,
                self.challenge_class,
                self.discharge_entry,
                self.ledger_before,
                self.ledger_after,
                self.repair_action,
                self.observed_at,
                self.carried,
            ))
        )


@dataclass(frozen=True)
class ProbabilityRecord:
    probability_record_id: int
    challenge_class: str
    probability: Fraction
    supporting_entries: tuple[LedgerEntry, ...]
    measured_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RepairDistribution:
    distribution_id: int
    route_endpoint: str
    protocol: ProtocolRecord
    records: tuple[ProbabilityRecord, ...]
    trials: tuple[RepairTrialRecord, ...]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class DeclaredCapacityDifference:
    package: RoutePackageRecord
    route_pair: RoutePairRecord
    left: RepairDistribution
    right: RepairDistribution
    challenge_class: str
    left_record: ProbabilityRecord
    right_record: ProbabilityRecord


@dataclass(frozen=True)
class ContinuedCapacityDifference:
    left_after: str
    right_after: str
    left: RepairDistribution
    right: RepairDistribution
    challenge_class: str
    left_record: ProbabilityRecord
    right_record: ProbabilityRecord


@dataclass(frozen=True)
class BudgetLedgerEntry:
    ledger_entry_id: int
    amount: Fraction
    label: str
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class BudgetWitness:
    spend: Fraction
    budget: Fraction
    move: ProbeMove[str, str]
    budget_entry: BudgetLedgerEntry
    spend_entry: BudgetLedgerEntry


@dataclass(frozen=True)
class RouteResiduePayload:
    package: RoutePackageRecord
    route_pair: RoutePairRecord
    challenge_class: str
    gamma_probability: Fraction
    eta_probability: Fraction


@dataclass(frozen=True)
class BridgeRecord:
    bridge_id: int
    residue: e15.RouteResidueDebtRecord
    package: RoutePackageRecord
    route_pair: RoutePairRecord
    capacity_difference: DeclaredCapacityDifference
    reconciled_at: Fraction
    observed_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ProtocolCounterpartRecord:
    counterpart_id: int
    candidate_id: int
    observed_at: Fraction
    comparison_base: ComparisonBaseRecord
    honest_package: RoutePackageRecord
    honest_pair: RoutePairRecord
    honest_difference: DeclaredCapacityDifference | None
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class CompletionCounterpartRecord:
    counterpart_id: int
    candidate_id: int
    observed_at: Fraction
    comparison_base: ComparisonBaseRecord
    completed_package: RoutePackageRecord
    completed_pair: RoutePairRecord
    witness_count: int
    discrepancy: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RefinementCounterpartRecord:
    counterpart_id: int
    candidate_id: int
    observed_at: Fraction
    comparison_base: ComparisonBaseRecord
    refined_package: RoutePackageRecord
    refined_pair: RoutePairRecord
    witness_count: int
    discrepancy: Fraction
    max_fiber: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ContinuationControlRecord:
    counterpart_id: int
    candidate_id: int
    observed_at: Fraction
    comparison_base: ComparisonBaseRecord
    package: RoutePackageRecord
    route_pair: RoutePairRecord
    continuation: WheelMap
    left_after: str
    right_after: str
    later_difference: ContinuedCapacityDifference | None
    carried: CarriedFact = CARRIED


Counterpart = (
    ProtocolCounterpartRecord
    | CompletionCounterpartRecord
    | RefinementCounterpartRecord
    | ContinuationControlRecord
)
COUNTERPART_TYPES = (
    ProtocolCounterpartRecord,
    CompletionCounterpartRecord,
    RefinementCounterpartRecord,
    ContinuationControlRecord,
)


@dataclass(frozen=True)
class PerturbationBoundRecord:
    bound_id: int
    candidate_id: int
    maximum_magnitude: Fraction
    declared_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class PerturbationTrialRecord:
    trial_id: int
    candidate_id: int
    observed_at: Fraction
    comparison_base: ComparisonBaseRecord
    package: RoutePackageRecord
    perturbed_pair: RoutePairRecord
    magnitude: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class Inventory:
    records: tuple[object, ...]
    eligible_records: tuple[object, ...]


@dataclass(frozen=True)
class ClaimRef:
    candidate_id: int
    package: RoutePackageRecord
    route_pair: RoutePairRecord
    protocol: ProtocolRecord
    economy: object
    budget: BudgetWitness
    challenge_class: str
    observed_at: Fraction


@dataclass(frozen=True)
class AdaptabilityClassifierContext:
    carrier: object
    declared_package_ids: frozenset[int]
    admissible_route_pairs: frozenset[tuple[int, int]]
    protocol_budget_links: frozenset[tuple[int, int, int]]
    admissible_counterpart_ids: frozenset[int]
    accepted_bridge_ids: frozenset[int]
    relevant_ledger_entry_ids: frozenset[int]
    eligible_route_endpoint_trials: frozenset[RepairTrialRecord]
    eligible_perturbation_trials: frozenset[PerturbationTrialRecord]

    def route_package_declared(self, package: RoutePackageRecord) -> bool:
        return package.package_id in self.declared_package_ids

    def route_pair_admissible(self, pair: RoutePairRecord) -> bool:
        return (pair.package.package_id, pair.route_pair_id) in self.admissible_route_pairs

    def protocol_uses_binding_budget(self, protocol: ProtocolRecord, budget: BudgetWitness) -> bool:
        return (
            protocol.protocol_id,
            budget.budget_entry.ledger_entry_id,
            budget.spend_entry.ledger_entry_id,
        ) in self.protocol_budget_links

    def counterpart_admissible(self, record: Counterpart) -> bool:
        return record.counterpart_id in self.admissible_counterpart_ids

    def counterpart_clears(self, record: Counterpart) -> bool:
        return counterpart_clears(self, record)

    def perturbation_preserves(self, record: PerturbationTrialRecord) -> bool:
        return route_predictive_witness(record.perturbed_pair)

    def perturbation_trial_eligible(self, record: PerturbationTrialRecord) -> bool:
        return record in self.eligible_perturbation_trials

    def trial_eligible_for_route_endpoint(
        self, trial: RepairTrialRecord, endpoint: str
    ) -> bool:
        return (
            trial.route_endpoint == endpoint
            and trial in self.eligible_route_endpoint_trials
        )

    def bridge_accepted(self, record: BridgeRecord) -> bool:
        return record.bridge_id in self.accepted_bridge_ids

    def ledger_entry_relevant(self, entry: LedgerEntry) -> bool:
        return entry.ledger_entry_id in self.relevant_ledger_entry_ids

    def ledger_entry_carried(self, entry: LedgerEntry) -> bool:
        return _lambda_entry_carried(entry)


@dataclass(frozen=True)
class StatusRecord:
    status_record_id: int
    claim_ref: ClaimRef
    status: AdaptabilityStatus
    recorded_at: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ClaimData:
    name: str
    fixture_index: int
    claim_ref: ClaimRef
    left_distribution: RepairDistribution | None
    right_distribution: RepairDistribution | None
    capacity_difference: DeclaredCapacityDifference | None
    bridge: BridgeRecord | None
    e15_context: e15.OfflineReclosureClassifierContext
    ctx: AdaptabilityClassifierContext
    protocol_inventory: Inventory
    completion_inventory: Inventory
    refinement_inventory: Inventory
    continuation_inventory: Inventory
    perturbation_bound: PerturbationBoundRecord
    perturbation_inventory: Inventory
    administrative_reason: str | None = None
    status_record: StatusRecord | None = None
    declared_distribution_pairs: tuple[
        tuple[RepairDistribution, RepairDistribution], ...
    ] = ()
    off_universe_perturbation: PerturbationTrialRecord | None = None


@dataclass(frozen=True)
class Fixture:
    wheel: NativeRouteTransportCore
    flat_native: NativeRouteTransportCore
    no_reveal: NativeRouteTransportCore
    claims: dict[str, ClaimData]
    controls: dict[str, ClaimData]


@dataclass(frozen=True)
class StatusRow:
    name: str
    observed: AdaptabilityStatus
    truths: dict[AdaptabilityStatus, bool]
    status_record: StatusRecord


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    rows: dict[str, StatusRow]
    comparisons: tuple[Comparison, ...]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    off_inventory_isolation_discipline: bool
    predictive_reveal_isolation_discipline: bool
    administrative_without_candidate_discipline: bool
    wrong_claim_bridge_isolation_discipline: bool
    route_trial_clone_rejected_discipline: bool
    perturbation_clone_rejected_discipline: bool
    flat_cross_witness_differential_discipline: bool


def id_base(index: int) -> int:
    return 16000000 + 100000 * index


def _nodup(values: Iterable[object]) -> bool:
    sequence = tuple(values)
    return all(
        left != right
        for left_index, left in enumerate(sequence)
        for right_index, right in enumerate(sequence)
        if left_index < right_index
    )


def challenge_family_valid(family: ChallengeFamilyRecord) -> bool:
    return bool(family.classes) and _nodup(family.classes)


def probability_record_valid(record: ProbabilityRecord) -> bool:
    return (
        0 <= record.probability <= 1
        and _nodup(record.supporting_entries)
    )


def _record_id(record: object) -> int:
    for name in (
        "counterpart_id", "trial_id", "probability_record_id", "ledger_entry_id",
        "distribution_id", "bridge_id", "status_record_id",
    ):
        if hasattr(record, name):
            return int(getattr(record, name))
    raise TypeError(f"record has no registered identifier: {record!r}")


def counterpart_kind(record: Counterpart) -> str:
    if isinstance(record, ProtocolCounterpartRecord):
        return "protocol"
    if isinstance(record, CompletionCounterpartRecord):
        return "completion"
    if isinstance(record, RefinementCounterpartRecord):
        return "refinement"
    if isinstance(record, ContinuationControlRecord):
        return "continuation"
    raise TypeError(f"not an E16 counterpart: {record!r}")


def counterpart_declared_key(record: Counterpart) -> tuple[int, Fraction, object]:
    if isinstance(record, ContinuationControlRecord):
        return (record.candidate_id, record.observed_at, record.counterpart_id)
    return (record.candidate_id, record.observed_at, record.comparison_base)


def inventory_checks(inventory: Inventory, eligible: Callable[[object], bool]) -> dict[str, bool]:
    records = inventory.records
    universe = inventory.eligible_records
    return {
        "recordsNodup": _nodup(records),
        "recordIdsNodup": _nodup(_record_id(record) for record in records),
        "everyEligibleCovered": all(record in records for record in universe if eligible(record)),
        "everyRecordEligible": all(record in universe and eligible(record) for record in records),
        "everyRecordCarried": all(e16_carried(record) for record in records),
        "singleValuedPerDeclaredKey": all(
            first == second
            for first in records
            for second in records
            if (
                isinstance(first, COUNTERPART_TYPES)
                and isinstance(second, COUNTERPART_TYPES)
                and counterpart_declared_key(first) == counterpart_declared_key(second)
            )
            or (
                not isinstance(first, COUNTERPART_TYPES)
                and not isinstance(second, COUNTERPART_TYPES)
                and _record_id(first) == _record_id(second)
            )
        ),
    }


def complete_inventory(inventory: Inventory, eligible: Callable[[object], bool]) -> bool:
    return all(inventory_checks(inventory, eligible).values())


def route_pair_linked(pair: RoutePairRecord) -> bool:
    core = pair.package.core
    return (
        pair.source in core.histories
        and pair.gamma in core.continuations
        and pair.eta in core.continuations
        and pair.gamma_endpoint == core.push(pair.source, pair.gamma)
        and pair.eta_endpoint == core.push(pair.source, pair.eta)
    )


def same_current_route_endpoints(pair: RoutePairRecord) -> bool:
    return route_pair_linked(pair) and current_event_equiv(
        pair.package.core, pair.gamma_endpoint, pair.eta_endpoint
    )


def route_predictive_witness(pair: RoutePairRecord) -> bool:
    return same_current_route_endpoints(pair) and not future_predictive_equiv(
        pair.package.core, pair.gamma_endpoint, pair.eta_endpoint
    )


def trial_records_discharge(trial: RepairTrialRecord) -> bool:
    entry_id = trial.discharge_entry.ledger_entry_id
    return (
        e16_carried(trial)
        and e16_carried(trial.discharge_entry)
        and trial.repair_action == _repair_substrate()[1]
        and _d4_action_lawful()
        and entry_id not in trial.ledger_before
        and entry_id in trial.ledger_after
    )


def trial_eligible_for_route_endpoint(
    ctx: AdaptabilityClassifierContext,
    trial: RepairTrialRecord,
    endpoint: str,
) -> bool:
    return ctx.trial_eligible_for_route_endpoint(trial, endpoint)


def trial_inventory_checks(
    distribution: RepairDistribution, ctx: AdaptabilityClassifierContext
) -> dict[str, bool]:
    trials = distribution.trials
    eligible_records = tuple(
        trial
        for trial in ctx.eligible_route_endpoint_trials
        if trial.route_endpoint == distribution.route_endpoint
    )
    return {
        "trialsNodup": _nodup(trials),
        "trialIdsNodup": _nodup(trial.trial_id for trial in trials),
        "everyEligibleTrialCovered": all(
            trial in trials for trial in eligible_records
        ),
        "everyTrialEligible": all(
            trial_eligible_for_route_endpoint(
                ctx, trial, distribution.route_endpoint
            )
            for trial in trials
        ),
        "everyTrialCarried": all(e16_carried(trial) for trial in trials),
        "singleValuedPerTrialId": all(
            first == second
            for first in trials
            for second in trials
            if first.trial_id == second.trial_id
        ),
    }


def successful_trials(
    distribution: RepairDistribution,
    challenge_class: str,
    ctx: AdaptabilityClassifierContext,
) -> tuple[RepairTrialRecord, ...]:
    return tuple(
        trial
        for trial in distribution.trials
        if trial.challenge_class == challenge_class
        and trial_eligible_for_route_endpoint(
            ctx, trial, distribution.route_endpoint
        )
        and trial_records_discharge(trial)
    )


def eligible_trials(
    distribution: RepairDistribution,
    challenge_class: str,
    ctx: AdaptabilityClassifierContext,
) -> tuple[RepairTrialRecord, ...]:
    return tuple(
        trial
        for trial in distribution.trials
        if trial.challenge_class == challenge_class
        and trial_eligible_for_route_endpoint(
            ctx, trial, distribution.route_endpoint
        )
    )


def probability_computed(
    distribution: RepairDistribution,
    record: ProbabilityRecord,
    ctx: AdaptabilityClassifierContext,
) -> bool:
    eligible = eligible_trials(distribution, record.challenge_class, ctx)
    successful = successful_trials(distribution, record.challenge_class, ctx)
    expected_entries = tuple(trial.discharge_entry for trial in successful)
    return (
        bool(eligible)
        and record.measured_at == distribution.protocol.measured_at
        and record.probability == F(len(successful), len(eligible))
        and record.supporting_entries == expected_entries
        and all(
            e16_carried(entry)
            and ctx.ledger_entry_carried(entry)
            and ctx.ledger_entry_relevant(entry)
            for entry in record.supporting_entries
        )
    )


def distribution_checks(
    distribution: RepairDistribution, ctx: AdaptabilityClassifierContext
) -> dict[str, bool]:
    records = distribution.records
    trial_checks = trial_inventory_checks(distribution, ctx)
    return {
        "distributionCarried": e16_carried(distribution),
        "challengeFamilyValid": challenge_family_valid(
            distribution.protocol.family
        ),
        "recordsNodup": _nodup(records),
        "recordIdsNodup": _nodup(record.probability_record_id for record in records),
        "everyClassCovered": all(any(record.challenge_class == C for record in records) for C in distribution.protocol.family.classes),
        "everyRecordDeclared": all(record.challenge_class in distribution.protocol.family.classes for record in records),
        "singleValuedPerClass": all(
            first == second
            for first in records
            for second in records
            if first.challenge_class == second.challenge_class
        ),
        "everyProbabilityCarried": all(e16_carried(record) for record in records),
        "everyProbabilityRecordValid": all(
            probability_record_valid(record) for record in records
        ),
        "everyProbabilityComputed": all(probability_computed(distribution, record, ctx) for record in records),
        "everyLedgerEntryCarried": all(
            e16_carried(entry) and ctx.ledger_entry_carried(entry)
            for record in records
            for entry in record.supporting_entries
        ),
        "everyLedgerEntryRelevant": all(ctx.ledger_entry_relevant(entry) for record in records for entry in record.supporting_entries),
        **trial_checks,
    }


def complete_distribution(
    distribution: RepairDistribution, ctx: AdaptabilityClassifierContext
) -> bool:
    return all(distribution_checks(distribution, ctx).values())


def declared_capacity_difference_valid(
    ctx: AdaptabilityClassifierContext, difference: DeclaredCapacityDifference
) -> bool:
    left = difference.left_record
    right = difference.right_record
    return (
        difference.route_pair.package == difference.package
        and route_pair_linked(difference.route_pair)
        and difference.left.route_endpoint == difference.route_pair.gamma_endpoint
        and difference.right.route_endpoint == difference.route_pair.eta_endpoint
        and difference.left.protocol == difference.right.protocol
        and complete_distribution(difference.left, ctx)
        and complete_distribution(difference.right, ctx)
        and difference.challenge_class in difference.left.protocol.family.classes
        and left in difference.left.records
        and right in difference.right.records
        and left.challenge_class == difference.challenge_class
        and right.challenge_class == difference.challenge_class
        and left.probability != right.probability
        and e16_carried(left)
        and e16_carried(right)
        and probability_computed(difference.left, left, ctx)
        and probability_computed(difference.right, right, ctx)
    )


def continued_capacity_difference_valid(
    ctx: AdaptabilityClassifierContext, difference: ContinuedCapacityDifference
) -> bool:
    left = difference.left_record
    right = difference.right_record
    return (
        difference.left.route_endpoint == difference.left_after
        and difference.right.route_endpoint == difference.right_after
        and difference.left.protocol == difference.right.protocol
        and complete_distribution(difference.left, ctx)
        and complete_distribution(difference.right, ctx)
        and difference.challenge_class in difference.left.protocol.family.classes
        and left in difference.left.records
        and right in difference.right.records
        and left.challenge_class == difference.challenge_class
        and right.challenge_class == difference.challenge_class
        and left.probability != right.probability
        and probability_computed(difference.left, left, ctx)
        and probability_computed(difference.right, right, ctx)
    )


def counterpart_package_linked(record: Counterpart) -> bool:
    if isinstance(record, ProtocolCounterpartRecord):
        return (
            record.comparison_base == record.honest_package.comparison_base
            and record.honest_pair.package == record.honest_package
            and route_pair_linked(record.honest_pair)
        )
    if isinstance(record, CompletionCounterpartRecord):
        return (
            record.comparison_base == record.completed_package.comparison_base
            and record.completed_pair.package == record.completed_package
            and route_pair_linked(record.completed_pair)
        )
    if isinstance(record, RefinementCounterpartRecord):
        return (
            record.comparison_base == record.refined_package.comparison_base
            and record.refined_pair.package == record.refined_package
            and route_pair_linked(record.refined_pair)
        )
    return (
        record.comparison_base == record.package.comparison_base
        and record.route_pair.package == record.package
        and route_pair_linked(record.route_pair)
        and record.continuation in record.package.core.continuations
        and record.left_after
        == record.package.core.push(record.route_pair.gamma_endpoint, record.continuation)
        and record.right_after
        == record.package.core.push(record.route_pair.eta_endpoint, record.continuation)
    )


def counterpart_clears(ctx: AdaptabilityClassifierContext, record: Counterpart) -> bool:
    if not counterpart_package_linked(record):
        return False
    if isinstance(record, ProtocolCounterpartRecord):
        return record.honest_difference is None
    if isinstance(record, CompletionCounterpartRecord):
        return record.witness_count == 0 and record.discrepancy == 0
    if isinstance(record, RefinementCounterpartRecord):
        return (
            record.witness_count == 0
            and record.discrepancy == 0
            and record.max_fiber == 1
        )
    return record.later_difference is None


def counterpart_positive_difference_valid(
    ctx: AdaptabilityClassifierContext, record: Counterpart
) -> bool:
    if not counterpart_package_linked(record):
        return False
    if isinstance(record, ProtocolCounterpartRecord):
        return (
            record.honest_difference is not None
            and declared_capacity_difference_valid(ctx, record.honest_difference)
            and record.honest_difference.left.protocol.measured_at == record.observed_at
        )
    if isinstance(record, ContinuationControlRecord):
        return (
            record.later_difference is not None
            and continued_capacity_difference_valid(ctx, record.later_difference)
            and record.later_difference.left.protocol.measured_at == record.observed_at
            and record.later_difference.right.protocol.measured_at == record.observed_at
        )
    return True


def probability_for(distribution: RepairDistribution, challenge_class: str) -> ProbabilityRecord | None:
    matches = tuple(record for record in distribution.records if record.challenge_class == challenge_class)
    return matches[0] if len(matches) == 1 else None


def distributions_match_claim_for(
    claim: ClaimRef,
    left: RepairDistribution,
    right: RepairDistribution,
) -> bool:
    return (
        left.route_endpoint == claim.route_pair.gamma_endpoint
        and right.route_endpoint == claim.route_pair.eta_endpoint
        and left.protocol == claim.protocol
        and right.protocol == claim.protocol
        and claim.challenge_class in claim.protocol.family.classes
    )


def distributions_match_claim(data: ClaimData) -> bool:
    if data.left_distribution is None or data.right_distribution is None:
        return False
    return distributions_match_claim_for(
        data.claim_ref, data.left_distribution, data.right_distribution
    )


def repair_capacity_distribution_pair_complete(
    ctx: AdaptabilityClassifierContext,
    pair: RoutePairRecord,
    left: RepairDistribution,
    right: RepairDistribution,
) -> bool:
    return (
        complete_distribution(left, ctx)
        and complete_distribution(right, ctx)
        and left.protocol == right.protocol
        and left.route_endpoint == pair.gamma_endpoint
        and right.route_endpoint == pair.eta_endpoint
    )


def no_declared_capacity_difference_for(
    ctx: AdaptabilityClassifierContext,
    pair: RoutePairRecord,
    left: RepairDistribution,
    right: RepairDistribution,
) -> bool:
    if not repair_capacity_distribution_pair_complete(ctx, pair, left, right):
        return False
    return all(
        (left_record := probability_for(left, challenge_class)) is not None
        and (right_record := probability_for(right, challenge_class)) is not None
        and left_record.probability == right_record.probability
        for challenge_class in left.protocol.family.classes
    )


def declared_capacity_difference(data: ClaimData) -> bool:
    if (
        data.capacity_difference is None
        or data.left_distribution is None
        or data.right_distribution is None
    ):
        return False
    return (
        distributions_match_claim(data)
        and data.capacity_difference.package == data.claim_ref.package
        and data.capacity_difference.route_pair == data.claim_ref.route_pair
        and data.capacity_difference.left == data.left_distribution
        and data.capacity_difference.right == data.right_distribution
        and data.capacity_difference.challenge_class == data.claim_ref.challenge_class
        and declared_capacity_difference_valid(data.ctx, data.capacity_difference)
    )


def no_declared_capacity_difference(data: ClaimData) -> bool:
    if data.left_distribution is None or data.right_distribution is None:
        return False
    return no_declared_capacity_difference_for(
        data.ctx,
        data.claim_ref.route_pair,
        data.left_distribution,
        data.right_distribution,
    )


def declared_flat_pair_evaluations(
    data: ClaimData,
) -> tuple[tuple[RepairDistribution, RepairDistribution, bool, bool], ...]:
    return tuple(
        (
            left,
            right,
            distributions_match_claim_for(data.claim_ref, left, right),
            no_declared_capacity_difference_for(
                data.ctx, data.claim_ref.route_pair, left, right
            ),
        )
        for left, right in data.declared_distribution_pairs
    )


def flat_second_arm_evidence(data: ClaimData) -> bool:
    return any(
        matches_claim and no_difference
        for _, _, matches_claim, no_difference
        in declared_flat_pair_evaluations(data)
    )


def exposure_budget_witness_valid(data: ClaimData) -> bool:
    budget = data.claim_ref.budget
    economy = data.claim_ref.economy
    return (
        e16_carried(budget.budget_entry)
        and e16_carried(budget.spend_entry)
        and _lambda_entry_carried(budget.budget_entry)
        and _lambda_entry_carried(budget.spend_entry)
        and budget.budget_entry.amount == budget.budget
        and budget.spend_entry.amount == budget.spend
        and economy.exposure_budget_entry(budget.budget_entry, budget.budget)
        and economy.exposure_spend_entry(budget.spend_entry, budget.spend)
        and economy.budget_admissible(budget.move)
    )


def binding_budget(data: ClaimData) -> bool:
    budget = data.claim_ref.budget
    return (
        exposure_budget_witness_valid(data)
        and budget.spend <= budget.budget
        and budget.spend == budget.budget
    )


def bridge_eligible(data: ClaimData) -> bool:
    if data.bridge is None or data.capacity_difference is None:
        return False
    claim = data.claim_ref
    bridge = data.bridge
    payload = bridge.residue.route_residue
    return (
        isinstance(payload, RouteResiduePayload)
        and e16_carried(bridge.residue)
        and e16_carried(bridge)
        and data.ctx.bridge_accepted(bridge)
        and bridge.package == claim.package == payload.package
        and bridge.route_pair == claim.route_pair == payload.route_pair
        and bridge.capacity_difference == data.capacity_difference
        and bridge.capacity_difference.challenge_class
        == claim.challenge_class
        == payload.challenge_class
        and bridge.capacity_difference.left_record.probability
        == payload.gamma_probability
        and bridge.capacity_difference.right_record.probability
        == payload.eta_probability
        and declared_capacity_difference_valid(data.ctx, bridge.capacity_difference)
        and bridge.residue.reconciliation_claim_id == claim.candidate_id
        and bridge.reconciled_at <= claim.observed_at
        and bridge.observed_at == claim.observed_at
        and not data.e15_context.f3_route_residue_awaiting_reconciliation(
            bridge.residue, claim.observed_at
        )
    )


def candidate_matches_claim(data: ClaimData) -> bool:
    if data.left_distribution is None or data.right_distribution is None:
        return False
    claim = data.claim_ref
    return (
        data.bridge is not None
        and claim.candidate_id == id_base(data.fixture_index) + 4
        and claim.package == claim.route_pair.package
        and claim.protocol == data.left_distribution.protocol == data.right_distribution.protocol
        and claim.observed_at == claim.protocol.measured_at == data.bridge.observed_at
    )


def candidate_evidence_checks(data: ClaimData) -> dict[str, bool]:
    claim = data.claim_ref
    return {
        "candidateMatchesClaim": candidate_matches_claim(data),
        "packageCarried": e16_carried(claim.package),
        "baseCarried": e16_carried(claim.package.comparison_base),
        "pairCarried": e16_carried(claim.route_pair),
        "protocolCarried": e16_carried(claim.protocol),
        "familyCarried": e16_carried(claim.protocol.family),
        "familyRecordValid": challenge_family_valid(claim.protocol.family),
        "familyPredatesClaim": claim.protocol.family.declared_at <= claim.observed_at,
        "coreLaws": core_laws(claim.package.core),
        "packageDeclared": data.ctx.route_package_declared(claim.package),
        "pairAdmissible": data.ctx.route_pair_admissible(claim.route_pair),
        "sameCurrent": same_current_route_endpoints(claim.route_pair),
        "predictiveWitness": route_predictive_witness(claim.route_pair),
        "bindingBudget": binding_budget(data),
        "protocolUsesBudget": data.ctx.protocol_uses_binding_budget(
            claim.protocol, claim.budget
        ),
        "capacityDifference": declared_capacity_difference(data),
        "bridgeEligibility": bridge_eligible(data),
    }


def candidate_evidence(data: ClaimData) -> bool:
    return all(candidate_evidence_checks(data).values())


def eligible_counterpart(data: ClaimData, kind: str, record: object) -> bool:
    return (
        isinstance(record, COUNTERPART_TYPES)
        and counterpart_kind(record) == kind
        and record.candidate_id == data.claim_ref.candidate_id
        and record.observed_at == data.claim_ref.observed_at
        and data.ctx.counterpart_admissible(record)
        and counterpart_package_linked(record)
        and (
            not isinstance(record, (ProtocolCounterpartRecord, ContinuationControlRecord))
            or data.ctx.counterpart_clears(record)
            or counterpart_positive_difference_valid(data.ctx, record)
        )
    )


def counterpart_complete(data: ClaimData, kind: str, inventory: Inventory) -> bool:
    return complete_inventory(inventory, lambda record: eligible_counterpart(data, kind, record))


def support_confound_evidence_for(data: ClaimData) -> bool:
    inventory = data.protocol_inventory
    return counterpart_complete(data, "protocol", inventory) and any(
        isinstance(record, ProtocolCounterpartRecord)
        and record.honest_package.comparison_base
        != data.claim_ref.package.comparison_base
        for record in inventory.records
    )


def artifact_evidence_for(data: ClaimData) -> bool:
    inventory = data.protocol_inventory
    return candidate_evidence(data) and counterpart_complete(data, "protocol", inventory) and any(
        isinstance(record, ProtocolCounterpartRecord)
        and record.comparison_base == data.claim_ref.package.comparison_base
        and data.ctx.counterpart_clears(record)
        for record in inventory.records
    )


def gated_flat_control_evidence(data: ClaimData) -> bool:
    claim = data.claim_ref
    return (
        claim.package == claim.route_pair.package
        and e16_carried(claim.package)
        and e16_carried(claim.package.comparison_base)
        and e16_carried(claim.route_pair)
        and e16_carried(claim.protocol)
        and e16_carried(claim.protocol.family)
        and challenge_family_valid(claim.protocol.family)
        and claim.protocol.family.declared_at <= claim.observed_at
        and data.ctx.route_package_declared(claim.package)
        and data.ctx.route_pair_admissible(claim.route_pair)
        and same_current_route_endpoints(claim.route_pair)
        and binding_budget(data)
        and data.ctx.protocol_uses_binding_budget(claim.protocol, claim.budget)
        and (
            future_predictive_equiv(claim.package.core, claim.route_pair.gamma_endpoint, claim.route_pair.eta_endpoint)
            or flat_second_arm_evidence(data)
        )
    )


def flat_evidence_for(data: ClaimData) -> bool:
    return gated_flat_control_evidence(data)


def flattenable_evidence_for(data: ClaimData) -> bool:
    inventory = data.completion_inventory
    return candidate_evidence(data) and counterpart_complete(data, "completion", inventory) and any(
        isinstance(record, CompletionCounterpartRecord)
        and record.comparison_base == data.claim_ref.package.comparison_base
        and data.ctx.counterpart_clears(record)
        and record.witness_count == 0
        and record.discrepancy == 0
        for record in inventory.records
    )


def currentizable_evidence_for(data: ClaimData) -> bool:
    inventory = data.refinement_inventory
    return candidate_evidence(data) and counterpart_complete(data, "refinement", inventory) and any(
        isinstance(record, RefinementCounterpartRecord)
        and record.comparison_base == data.claim_ref.package.comparison_base
        and data.ctx.counterpart_clears(record)
        and record.witness_count == 0
        and record.discrepancy == 0
        and record.max_fiber == 1
        for record in inventory.records
    )


def continuation_dissipates(data: ClaimData, record: ContinuationControlRecord) -> bool:
    return (
        counterpart_package_linked(record)
        and data.ctx.counterpart_clears(record)
        and record.later_difference is None
    )


def dissipative_evidence_for(data: ClaimData) -> bool:
    inventory = data.continuation_inventory
    return candidate_evidence(data) and counterpart_complete(data, "continuation", inventory) and any(
        isinstance(record, ContinuationControlRecord) and continuation_dissipates(data, record)
        for record in inventory.records
    )


def perturbation_old_conditions(data: ClaimData, record: object) -> bool:
    return (
        isinstance(record, PerturbationTrialRecord)
        and record.candidate_id == data.claim_ref.candidate_id
        and record.observed_at == data.claim_ref.observed_at
        and record.comparison_base == data.claim_ref.package.comparison_base
        and record.package == data.claim_ref.package
        and record.perturbed_pair.package == record.package
        and route_pair_linked(record.perturbed_pair)
        and record.magnitude >= 0
        and record.magnitude <= data.perturbation_bound.maximum_magnitude
    )


def perturbation_eligible(data: ClaimData, record: object) -> bool:
    return (
        isinstance(record, PerturbationTrialRecord)
        and data.ctx.perturbation_trial_eligible(record)
        and perturbation_old_conditions(data, record)
    )


def complete_perturbation_inventory_checks(data: ClaimData) -> dict[str, bool]:
    bound = data.perturbation_bound
    inventory = data.perturbation_inventory
    records = inventory.records
    universe = inventory.eligible_records
    return {
        "boundCarried": e16_carried(bound),
        "boundCandidateLinked": bound.candidate_id == data.claim_ref.candidate_id,
        "boundPredatesClaim": bound.declared_at <= data.claim_ref.observed_at,
        "boundNonnegative": bound.maximum_magnitude >= 0,
        "recordsNodup": _nodup(records),
        "recordIdsNodup": _nodup(_record_id(record) for record in records),
        "eligibleUniverseMatchesContext": (
            frozenset(universe) == data.ctx.eligible_perturbation_trials
        ),
        "everyEligibleCovered": all(
            record in records
            for record in data.ctx.eligible_perturbation_trials
            if perturbation_eligible(data, record)
        ),
        "everyRecordEligible": all(
            record in data.ctx.eligible_perturbation_trials
            and perturbation_eligible(data, record)
            for record in records
        ),
        "everyRecordCarried": all(e16_carried(record) for record in records),
        "singleValuedPerDeclaredKey": all(
            first == second
            for first in records
            for second in records
            if isinstance(first, PerturbationTrialRecord)
            and isinstance(second, PerturbationTrialRecord)
            and first.candidate_id == second.candidate_id
            and first.observed_at == second.observed_at
            and first.trial_id == second.trial_id
        ),
    }


def complete_perturbation_inventory(data: ClaimData) -> bool:
    return all(complete_perturbation_inventory_checks(data).values())


def support_freedom(data: ClaimData) -> bool:
    inventory = data.protocol_inventory
    return counterpart_complete(data, "protocol", inventory) and all(
        isinstance(record, ProtocolCounterpartRecord)
        and record.comparison_base == data.claim_ref.package.comparison_base
        and not data.ctx.counterpart_clears(record)
        for record in inventory.records
    )


def flattening_freedom(data: ClaimData) -> bool:
    inventory = data.completion_inventory
    return counterpart_complete(data, "completion", inventory) and all(
        isinstance(record, CompletionCounterpartRecord)
        and record.comparison_base == data.claim_ref.package.comparison_base
        and not data.ctx.counterpart_clears(record)
        for record in inventory.records
    )


def currentization_freedom(data: ClaimData) -> bool:
    inventory = data.refinement_inventory
    return counterpart_complete(data, "refinement", inventory) and all(
        isinstance(record, RefinementCounterpartRecord)
        and record.comparison_base == data.claim_ref.package.comparison_base
        and not data.ctx.counterpart_clears(record)
        for record in inventory.records
    )


def dissipation_freedom(data: ClaimData) -> bool:
    continuation_complete = counterpart_complete(data, "continuation", data.continuation_inventory)
    return (
        continuation_complete
        and complete_perturbation_inventory(data)
        and all(
            isinstance(record, ContinuationControlRecord) and not continuation_dissipates(data, record)
            for record in data.continuation_inventory.records
        )
        and all(
            isinstance(record, PerturbationTrialRecord) and data.ctx.perturbation_preserves(record)
            for record in data.perturbation_inventory.records
        )
    )


def coherent_adaptability_evidence_for(data: ClaimData) -> bool:
    return (
        candidate_evidence(data)
        and support_freedom(data)
        and flattening_freedom(data)
        and currentization_freedom(data)
        and dissipation_freedom(data)
    )


def bounded_perturbation_failure(data: ClaimData) -> bool:
    return (
        candidate_evidence(data)
        and complete_perturbation_inventory(data)
        and any(
            isinstance(record, PerturbationTrialRecord)
            and perturbation_eligible(data, record)
            and not data.ctx.perturbation_preserves(record)
            for record in data.perturbation_inventory.records
        )
    )


def administrative_rejection(data: ClaimData) -> bool:
    claim = data.claim_ref
    reason = data.administrative_reason
    return (
        claim.route_pair.package == claim.package
        and route_pair_linked(claim.route_pair)
        and e16_carried(claim.package)
        and e16_carried(claim.package.comparison_base)
        and e16_carried(claim.route_pair)
        and e16_carried(claim.protocol)
        and e16_carried(claim.protocol.family)
        and challenge_family_valid(claim.protocol.family)
        and claim.protocol.measured_at == claim.observed_at
        and exposure_budget_witness_valid(data)
        and (
            (reason == "package_undeclared" and not data.ctx.route_package_declared(claim.package))
            or (reason == "pair_inadmissible" and not data.ctx.route_pair_admissible(claim.route_pair))
            or (reason == "budget_not_binding" and not binding_budget(data))
            or (reason == "protocol_budget_unlinked" and not data.ctx.protocol_uses_binding_budget(claim.protocol, claim.budget))
        )
    )


def adaptability_rejected_evidence_for(data: ClaimData) -> bool:
    return bounded_perturbation_failure(data) or administrative_rejection(data)


EVIDENCE_FUNCTIONS: dict[AdaptabilityStatus, Callable[[ClaimData], bool]] = {
    AdaptabilityStatus.support_confound: support_confound_evidence_for,
    AdaptabilityStatus.artifact: artifact_evidence_for,
    AdaptabilityStatus.flat: flat_evidence_for,
    AdaptabilityStatus.flattenable: flattenable_evidence_for,
    AdaptabilityStatus.currentizable_slack: currentizable_evidence_for,
    AdaptabilityStatus.dissipative: dissipative_evidence_for,
    AdaptabilityStatus.coherent_adaptability: coherent_adaptability_evidence_for,
    AdaptabilityStatus.adaptability_rejected: adaptability_rejected_evidence_for,
}


def raw_evidence_truths(data: ClaimData) -> dict[AdaptabilityStatus, bool]:
    return {status: function(data) for status, function in EVIDENCE_FUNCTIONS.items()}


def classify_claim_data(data: ClaimData) -> AdaptabilityStatus:
    truths = raw_evidence_truths(data)
    return next((status for status in STATUS_PRIORITY if truths[status]), AdaptabilityStatus.unclassified)


def status_occurrence_for(claim: ClaimRef, record: StatusRecord) -> bool:
    return record.claim_ref == claim and e16_carried(record)


def case_holds(data: ClaimData, record: StatusRecord, status: AdaptabilityStatus) -> bool:
    truths = raw_evidence_truths(data)
    index = STATUS_PRIORITY.index(status)
    return (
        status_occurrence_for(data.claim_ref, record)
        and record.status is status
        and truths[status]
        and all(not truths[higher] for higher in STATUS_PRIORITY[:index])
    )


def complete_adaptability_status(data: ClaimData, record: StatusRecord) -> bool:
    return sum(case_holds(data, record, status) for status in STATUS_PRIORITY) == 1


def _probability_id(base: int, side: int, class_index: int) -> int:
    return base + 100 + 10 * side + class_index


def _trial_id(base: int, side: int, class_index: int, k: int) -> int:
    return base + 1000 + 100 * side + 10 * class_index + k


def _trial_ledger_id(base: int, side: int, class_index: int, k: int) -> int:
    return base + 2000 + 100 * side + 10 * class_index + k


def _make_distribution(
    base: int,
    side: int,
    endpoint: str,
    protocol: ProtocolRecord,
    successes: dict[str, frozenset[int]],
    challenge_classes: tuple[str, ...] = CLASSES,
) -> RepairDistribution:
    trials: list[RepairTrialRecord] = []
    records: list[ProbabilityRecord] = []
    _substrate, repair_action = _repair_substrate()
    for class_index, challenge_class in enumerate(challenge_classes):
        class_trials: list[RepairTrialRecord] = []
        for k in range(4):
            identifier = _trial_id(base, side, class_index, k)
            ledger = LedgerEntry(_trial_ledger_id(base, side, class_index, k), identifier, F(1))
            success = k in successes[challenge_class]
            trial = RepairTrialRecord(
                identifier,
                endpoint,
                challenge_class,
                ledger,
                (),
                (ledger.ledger_entry_id,) if success else (),
                repair_action,
                F(10),
            )
            trials.append(trial)
            class_trials.append(trial)
        successful = tuple(trial.discharge_entry for trial in class_trials if trial_records_discharge(trial))
        records.append(
            ProbabilityRecord(
                _probability_id(base, side, class_index),
                challenge_class,
                F(len(successful), 4),
                successful,
                F(10),
            )
        )
    return RepairDistribution(
        base + 30 + side,
        endpoint,
        protocol,
        tuple(records),
        tuple(trials),
    )


@lru_cache(maxsize=1)
def _repair_substrate() -> tuple[e14.Fixture, RepairAction]:
    """Return one Repair-World E-system and one D4-lawful repair action."""

    fixture = e14.build_fixture()
    action = fixture.repair_candidates["repair_evidence_repair"].action
    if not is_lawful_action(fixture.carrier.config, fixture.carrier.state, action).is_lawful:
        raise RuntimeError("E16 Repair-World substrate lacks its registered D4 repair")
    return fixture, action


@lru_cache(maxsize=1)
def _e16_carrier() -> object:
    substrate, action = _repair_substrate()
    fixture_indices = (*range(1, 11), *range(1015, 1070))
    ledger_entries: list[object] = []
    for index in fixture_indices:
        base = id_base(index)
        ledger_entries.extend(
            LedgerEntry(
                _trial_ledger_id(base, side, class_index, k),
                _trial_id(base, side, class_index, k),
                F(1),
            )
            for side in (range(4) if index == 1067 else range(2))
            for class_index in range(2)
            for k in range(4)
        )
        ledger_entries.extend(
            (
                BudgetLedgerEntry(base + 20, F(6), "exposure-budget"),
                BudgetLedgerEntry(
                    base + 21,
                    F(5) if index == 10 else F(6),
                    "exposure-spend",
                ),
            )
        )
    quotient = substrate.repair_candidates[
        "repair_evidence_repair"
    ].trigger.conflict_record.transport_record.current_quotient
    return e14._build_repair_world_carrier((action,), tuple(ledger_entries), quotient)


@lru_cache(maxsize=None)
def _lambda_entry_carried(entry: object) -> bool:
    ledger = _e16_carrier().config.e_system.Lambda_S
    return entry in _lambda_entry_set() and ledger.ledger_evidence(entry) is not None


@lru_cache(maxsize=1)
def _lambda_entry_set() -> frozenset[object]:
    return frozenset(_e16_carrier().config.e_system.Lambda_S.ledger_entries)


@lru_cache(maxsize=1)
def _d4_action_lawful() -> bool:
    carrier = _e16_carrier()
    action = _repair_substrate()[1]
    return is_lawful_action(carrier.config, carrier.state, action).is_lawful


def _capacity_difference(
    package: RoutePackageRecord,
    pair: RoutePairRecord,
    left: RepairDistribution,
    right: RepairDistribution,
    challenge_class: str = C_REPAIR,
) -> DeclaredCapacityDifference:
    left_record = probability_for(left, challenge_class)
    right_record = probability_for(right, challenge_class)
    if left_record is None or right_record is None:
        raise RuntimeError("capacity-difference fixture lacks its declared class")
    return DeclaredCapacityDifference(
        package, pair, left, right, challenge_class, left_record, right_record
    )


def _distribution_at(distribution: RepairDistribution, endpoint: str) -> RepairDistribution:
    return replace(
        distribution,
        route_endpoint=endpoint,
        trials=tuple(replace(trial, route_endpoint=endpoint) for trial in distribution.trials),
    )


def _continued_difference(
    left_after: str,
    right_after: str,
    left_source: RepairDistribution,
    right_source: RepairDistribution,
) -> ContinuedCapacityDifference:
    left = _distribution_at(left_source, left_after)
    right = _distribution_at(right_source, right_after)
    left_record = probability_for(left, C_REPAIR)
    right_record = probability_for(right, C_REPAIR)
    if left_record is None or right_record is None:
        raise RuntimeError("continued difference lacks its declared class")
    return ContinuedCapacityDifference(
        left_after, right_after, left, right, C_REPAIR, left_record, right_record
    )


def _build_claim(
    name: str,
    index: int,
    core: NativeRouteTransportCore,
    *,
    source: str = "FF",
    gamma: WheelMap | None = None,
    eta: WheelMap | None = None,
    equal_capacity: bool = False,
    support_confound: bool = False,
    artifact: bool = False,
    flattenable: bool = False,
    currentizable: bool = False,
    dissipative: bool = False,
    perturbation_failure: bool = False,
    unbound: bool = False,
) -> ClaimData:
    base = id_base(index)
    gamma_map = gamma if gamma is not None else (ELL0 if len(core.histories) == 4 else core.identity)
    eta_map = eta if eta is not None else core.identity
    comparison_base = ComparisonBaseRecord(base + 1, ("visible",), F(0))
    package = RoutePackageRecord(base + 2, comparison_base, core)
    pair = RoutePairRecord(
        base + 3,
        package,
        source,
        gamma_map,
        eta_map,
        core.push(source, gamma_map),
        core.push(source, eta_map),
    )
    family = ChallengeFamilyRecord(base + 10, CLASSES, F(0))
    protocol = ProtocolRecord(base + 11, family, F(10))
    gamma_success = {C_REPAIR: frozenset((0, 1, 2)), C_SHIFT: frozenset((0, 1))}
    eta_success = {C_REPAIR: frozenset((0,)) if not equal_capacity else frozenset((0, 1, 2)), C_SHIFT: frozenset((0, 1))}
    left = _make_distribution(base, 0, pair.gamma_endpoint, protocol, gamma_success)
    right = _make_distribution(base, 1, pair.eta_endpoint, protocol, eta_success)
    capacity_difference = (
        None if equal_capacity else _capacity_difference(package, pair, left, right)
    )
    active = ActiveFamily(("adaptability_probe",), {"adaptability_probe": F(1)}, as_xi_family="adaptability")
    move = ProbeMove(ProbeMoveKind.allocation, active, active)
    spend = F(5) if unbound else F(6)
    budget_amount = F(6)
    budget = BudgetWitness(
        spend,
        budget_amount,
        move,
        BudgetLedgerEntry(base + 20, budget_amount, "exposure-budget"),
        BudgetLedgerEntry(base + 21, spend, "exposure-spend"),
    )
    substrate, _repair_action = _repair_substrate()
    claim = ClaimRef(
        base + 4,
        package,
        pair,
        protocol,
        substrate.carrier.config.probe_economy,
        budget,
        C_REPAIR,
        F(10),
    )
    payload = RouteResiduePayload(package, pair, C_REPAIR, F(3, 4), F(1, 4))
    residue = e15.RouteResidueDebtRecord(base + 13, payload, claim.candidate_id, F(4), F(1, 2))
    e15_context = e15.OfflineReclosureClassifierContext(
        frozenset(), frozenset(), frozenset(), frozenset(), frozenset(), (), frozenset(), frozenset()
    )
    bridge = (
        None
        if capacity_difference is None
        else BridgeRecord(
            base + 12, residue, package, pair, capacity_difference, F(9), F(10)
        )
    )
    protocol_base = ComparisonBaseRecord(base + 3005, ("changed",), F(0)) if support_confound else comparison_base
    honest_package = (
        RoutePackageRecord(base + 3006, protocol_base, core)
        if support_confound
        else package
    )
    honest_pair = replace(pair, package=honest_package)
    honest_left = _distribution_at(left, honest_pair.gamma_endpoint)
    honest_right = _distribution_at(right, honest_pair.eta_endpoint)
    honest_difference = (
        None
        if artifact or equal_capacity
        else _capacity_difference(
            honest_package, honest_pair, honest_left, honest_right
        )
    )
    protocol_record = ProtocolCounterpartRecord(
        base + 3000,
        claim.candidate_id,
        F(10),
        protocol_base,
        honest_package,
        honest_pair,
        honest_difference,
    )
    completion_record = CompletionCounterpartRecord(
        base + 4000,
        claim.candidate_id,
        F(10),
        comparison_base,
        package,
        pair,
        0 if flattenable else 1,
        F(0) if flattenable else F(1, 2),
    )
    refinement_record = RefinementCounterpartRecord(
        base + 5000,
        claim.candidate_id,
        F(10),
        comparison_base,
        package,
        pair,
        0 if currentizable else 1,
        F(0) if currentizable else F(1, 2),
        1 if currentizable else 2,
    )
    reveal_left = core.push(pair.gamma_endpoint, REVEAL) if REVEAL in core.continuations else pair.gamma_endpoint
    reveal_right = core.push(pair.eta_endpoint, REVEAL) if REVEAL in core.continuations else pair.eta_endpoint
    reveal_continuation = REVEAL if REVEAL in core.continuations else core.identity
    reveal_difference = (
        _continued_difference(reveal_left, reveal_right, left, right)
        if probability_for(left, C_REPAIR).probability
        != probability_for(right, C_REPAIR).probability
        else None
    )
    continuation_records = [
        ContinuationControlRecord(
            base + 6000,
            claim.candidate_id,
            F(10),
            comparison_base,
            package,
            pair,
            reveal_continuation,
            reveal_left,
            reveal_right,
            reveal_difference,
        )
    ]
    if dissipative:
        continuation_records.append(
            ContinuationControlRecord(
                base + 6001,
                claim.candidate_id,
                F(10),
                comparison_base,
                package,
                pair,
                ERASE_LATENT,
                core.push(pair.gamma_endpoint, ERASE_LATENT),
                core.push(pair.eta_endpoint, ERASE_LATENT),
                None,
            )
        )
    bound = PerturbationBoundRecord(base + 7000, claim.candidate_id, F(1, 2), F(5))
    perturbations = tuple(
        PerturbationTrialRecord(
            base + 7100 + k,
            claim.candidate_id,
            F(10),
            comparison_base,
            package,
            replace(
                pair,
                eta=pair.gamma,
                eta_endpoint=pair.gamma_endpoint,
            )
            if perturbation_failure and magnitude == F(1, 4)
            else pair,
            magnitude,
        )
        for k, magnitude in enumerate((F(0), F(1, 4), F(1, 2)))
    )
    route_distributions = [left, right, honest_left, honest_right]
    if reveal_difference is not None:
        route_distributions.extend(
            (reveal_difference.left, reveal_difference.right)
        )
    all_counterparts = (protocol_record, completion_record, refinement_record, *continuation_records)
    ctx = AdaptabilityClassifierContext(
        _e16_carrier(),
        frozenset((package.package_id,)),
        frozenset(((package.package_id, pair.route_pair_id),)),
        frozenset(((protocol.protocol_id, budget.budget_entry.ledger_entry_id, budget.spend_entry.ledger_entry_id),)),
        frozenset(record.counterpart_id for record in all_counterparts),
        frozenset((bridge.bridge_id,)) if bridge is not None else frozenset(),
        frozenset(
            trial.discharge_entry.ledger_entry_id
            for distribution in (left, right)
            for trial in distribution.trials
        ),
        frozenset(
            trial
            for distribution in route_distributions
            for trial in distribution.trials
        ),
        frozenset(perturbations),
    )
    data = ClaimData(
        name,
        index,
        claim,
        left,
        right,
        capacity_difference,
        bridge,
        e15_context,
        ctx,
        Inventory((protocol_record,), (protocol_record,)),
        Inventory((completion_record,), (completion_record,)),
        Inventory((refinement_record,), (refinement_record,)),
        Inventory(tuple(continuation_records), tuple(continuation_records)),
        bound,
        Inventory(perturbations, perturbations),
        administrative_reason="budget_not_binding" if unbound else None,
        declared_distribution_pairs=((left, right),),
    )
    return data


def _flat_unrelated_pair_control(
    core: NativeRouteTransportCore,
) -> ClaimData:
    data = _build_claim(
        "ctrl_flat_unrelated_pair_rejected", 1067, core
    )
    base = id_base(1067)
    family = ChallengeFamilyRecord(base + 15, AUXILIARY_CLASSES, F(0))
    protocol = ProtocolRecord(base + 16, family, F(10))
    equal_successes = {
        AUXILIARY_CLASSES[0]: frozenset((0, 1)),
        AUXILIARY_CLASSES[1]: frozenset((0, 1)),
    }
    auxiliary_left = _make_distribution(
        base,
        2,
        data.claim_ref.route_pair.gamma_endpoint,
        protocol,
        equal_successes,
        AUXILIARY_CLASSES,
    )
    auxiliary_right = _make_distribution(
        base,
        3,
        data.claim_ref.route_pair.eta_endpoint,
        protocol,
        equal_successes,
        AUXILIARY_CLASSES,
    )
    if data.left_distribution is None or data.right_distribution is None:
        raise RuntimeError("flat unrelated-pair control requires claim distributions")
    left = replace(
        data.left_distribution,
        trials=data.left_distribution.trials + auxiliary_left.trials,
    )
    right = replace(
        data.right_distribution,
        trials=data.right_distribution.trials + auxiliary_right.trials,
    )
    auxiliary_left = replace(
        auxiliary_left,
        trials=left.trials,
    )
    auxiliary_right = replace(
        auxiliary_right,
        trials=right.trials,
    )
    ctx = replace(
        data.ctx,
        relevant_ledger_entry_ids=data.ctx.relevant_ledger_entry_ids.union(
            trial.discharge_entry.ledger_entry_id
            for distribution in (auxiliary_left, auxiliary_right)
            for trial in distribution.trials
        ),
        eligible_route_endpoint_trials=data.ctx.eligible_route_endpoint_trials.union(
            trial
            for distribution in (auxiliary_left, auxiliary_right)
            for trial in distribution.trials
        ),
    )
    difference = _capacity_difference(
        data.claim_ref.package,
        data.claim_ref.route_pair,
        left,
        right,
    )
    bridge = (
        None
        if data.bridge is None
        else replace(data.bridge, capacity_difference=difference)
    )
    return replace(
        data,
        ctx=ctx,
        left_distribution=left,
        right_distribution=right,
        capacity_difference=difference,
        bridge=bridge,
        declared_distribution_pairs=(
            (left, right),
            (auxiliary_left, auxiliary_right),
        ),
    )


def _perturbation_off_universe_control(
    core: NativeRouteTransportCore,
) -> ClaimData:
    data = _build_claim(
        "ctrl_perturbation_off_universe_rejected", 1068, core
    )
    off_universe = PerturbationTrialRecord(
        id_base(1068) + 7190,
        data.claim_ref.candidate_id,
        data.claim_ref.observed_at,
        data.claim_ref.package.comparison_base,
        data.claim_ref.package,
        data.claim_ref.route_pair,
        F(1, 4),
    )
    return replace(data, off_universe_perturbation=off_universe)


def _swapped_trial_populations_control(
    core: NativeRouteTransportCore,
) -> ClaimData:
    data = _build_claim(
        "ctrl_swapped_trial_populations_rejected", 1069, core
    )
    if data.left_distribution is None or data.right_distribution is None:
        raise RuntimeError("swapped trial control requires both distributions")
    left_trials = data.left_distribution.trials
    right_trials = data.right_distribution.trials
    left = replace(data.left_distribution, trials=right_trials)
    right = replace(data.right_distribution, trials=left_trials)
    return replace(
        data,
        left_distribution=left,
        right_distribution=right,
        declared_distribution_pairs=((left, right),),
    )


def _with_status(data: ClaimData) -> ClaimData:
    status = classify_claim_data(data)
    record = StatusRecord(id_base(data.fixture_index) + 14, data.claim_ref, status, F(10))
    return replace(data, status_record=record)


def build_fixture() -> Fixture:
    wheel = wheel_core()
    flat = flat_native_core()
    no_reveal = no_reveal_core()
    claims = {
        "claim_coherent_wheel": _build_claim("claim_coherent_wheel", 1, wheel),
        "claim_support_confound": _build_claim("claim_support_confound", 2, wheel, support_confound=True),
        "claim_artifact_trap": _build_claim("claim_artifact_trap", 3, wheel, artifact=True),
        "claim_flat_future": _build_claim("claim_flat_future", 4, flat, source="F"),
        "claim_flat_equal_capacity": _build_claim("claim_flat_equal_capacity", 5, wheel, equal_capacity=True),
        "claim_flattenable": _build_claim("claim_flattenable", 6, wheel, flattenable=True),
        "claim_currentizable": _build_claim("claim_currentizable", 7, wheel, currentizable=True),
        "claim_dissipative": _build_claim("claim_dissipative", 8, wheel, dissipative=True),
        "claim_rejected_perturbation": _build_claim("claim_rejected_perturbation", 9, wheel, perturbation_failure=True),
        "claim_rejected_unbound_flat": _build_claim("claim_rejected_unbound_flat", 10, flat, source="F", unbound=True),
    }
    controls: dict[str, ClaimData] = {}
    for row, name in enumerate(REGISTERED_COMPARISON_ORDER, 1):
        if row < 15:
            continue
        controls[name] = _build_claim(name, 1000 + row, wheel)
    controls["ctrl_support_only"] = _build_claim(
        "ctrl_support_only", 1015, wheel, support_confound=True
    )
    controls["ctrl_flattening_only"] = _build_claim(
        "ctrl_flattening_only", 1016, wheel, flattenable=True
    )
    controls["ctrl_currentization_only"] = _build_claim(
        "ctrl_currentization_only", 1017, wheel, currentizable=True
    )
    controls["ctrl_dissipation_only"] = _build_claim(
        "ctrl_dissipation_only", 1018, wheel, dissipative=True
    )
    controls["ctrl_perturbation_only"] = _build_claim(
        "ctrl_perturbation_only", 1019, wheel, perturbation_failure=True
    )
    controls["ctrl_flat_unrelated_pair_rejected"] = (
        _flat_unrelated_pair_control(wheel)
    )
    controls["ctrl_perturbation_off_universe_rejected"] = (
        _perturbation_off_universe_control(wheel)
    )
    controls["ctrl_swapped_trial_populations_rejected"] = (
        _swapped_trial_populations_control(wheel)
    )
    return Fixture(
        wheel,
        flat,
        no_reveal,
        {name: _with_status(data) for name, data in claims.items()},
        controls,
    )


def _status_rows(fixture: Fixture) -> dict[str, StatusRow]:
    rows: dict[str, StatusRow] = {}
    for name, data in fixture.claims.items():
        if data.status_record is None:
            raise RuntimeError(f"missing status record for {name}")
        observed = classify_claim_data(data)
        truths = {status: case_holds(data, data.status_record, status) for status in STATUS_PRIORITY}
        rows[name] = StatusRow(name, observed, truths, data.status_record)
    return rows


def _replace_claim(data: ClaimData, *, fixture_index: int, name: str, **changes: object) -> ClaimData:
    return replace(data, name=name, fixture_index=fixture_index, status_record=None, **changes)


def _mutate_record_carried(record: object, **changes: object) -> object:
    return replace(record, carried=replace(getattr(record, "carried"), **changes))


def _off_inventory_continuation(data: ClaimData) -> ContinuationControlRecord:
    core = data.claim_ref.package.core
    pair = data.claim_ref.route_pair
    return ContinuationControlRecord(
        id_base(data.fixture_index) + 6001,
        data.claim_ref.candidate_id,
        data.claim_ref.observed_at,
        data.claim_ref.package.comparison_base,
        data.claim_ref.package,
        pair,
        ERASE_LATENT,
        core.push(pair.gamma_endpoint, ERASE_LATENT),
        core.push(pair.eta_endpoint, ERASE_LATENT),
        None,
    )


def _pair_on_core(
    pair: RoutePairRecord,
    package: RoutePackageRecord,
    core: NativeRouteTransportCore,
) -> RoutePairRecord:
    return replace(
        pair,
        package=package,
        gamma=ELL0,
        eta=core.identity,
        gamma_endpoint=core.push(pair.source, ELL0),
        eta_endpoint=core.push(pair.source, core.identity),
    )


def _relink_no_reveal_claim(
    data: ClaimData, core: NativeRouteTransportCore
) -> ClaimData:
    if data.bridge is None or data.capacity_difference is None:
        raise RuntimeError("no-reveal control requires a complete candidate bridge")
    package = replace(data.claim_ref.package, core=core)
    pair = _pair_on_core(data.claim_ref.route_pair, package, core)
    left = _distribution_at(data.left_distribution, pair.gamma_endpoint)
    right = _distribution_at(data.right_distribution, pair.eta_endpoint)
    difference = _capacity_difference(package, pair, left, right)
    claim = replace(data.claim_ref, package=package, route_pair=pair)

    payload = RouteResiduePayload(
        package,
        pair,
        difference.challenge_class,
        difference.left_record.probability,
        difference.right_record.probability,
    )
    residue = replace(data.bridge.residue, route_residue=payload)
    bridge = replace(
        data.bridge,
        residue=residue,
        package=package,
        route_pair=pair,
        capacity_difference=difference,
    )

    protocol_records: list[ProtocolCounterpartRecord] = []
    for record in data.protocol_inventory.records:
        if not isinstance(record, ProtocolCounterpartRecord):
            raise RuntimeError("protocol inventory contains the wrong record family")
        honest_package = replace(record.honest_package, core=core)
        honest_pair = _pair_on_core(record.honest_pair, honest_package, core)
        honest_difference = (
            None
            if record.honest_difference is None
            else _capacity_difference(
                honest_package,
                honest_pair,
                _distribution_at(record.honest_difference.left, honest_pair.gamma_endpoint),
                _distribution_at(record.honest_difference.right, honest_pair.eta_endpoint),
            )
        )
        protocol_records.append(
            replace(
                record,
                honest_package=honest_package,
                honest_pair=honest_pair,
                honest_difference=honest_difference,
            )
        )

    completion_records = tuple(
        replace(record, completed_package=package, completed_pair=pair)
        for record in data.completion_inventory.records
        if isinstance(record, CompletionCounterpartRecord)
    )
    refinement_records = tuple(
        replace(record, refined_package=package, refined_pair=pair)
        for record in data.refinement_inventory.records
        if isinstance(record, RefinementCounterpartRecord)
    )
    continuation_records: list[ContinuationControlRecord] = []
    for record in data.continuation_inventory.records:
        if not isinstance(record, ContinuationControlRecord):
            raise RuntimeError("continuation inventory contains the wrong record family")
        continuation = core.identity
        left_after = core.push(pair.gamma_endpoint, continuation)
        right_after = core.push(pair.eta_endpoint, continuation)
        continuation_records.append(
            replace(
                record,
                package=package,
                route_pair=pair,
                continuation=continuation,
                left_after=left_after,
                right_after=right_after,
                later_difference=_continued_difference(
                    left_after, right_after, left, right
                ),
            )
        )
    perturbation_records = tuple(
        replace(
            record,
            comparison_base=package.comparison_base,
            package=package,
            perturbed_pair=pair,
        )
        for record in data.perturbation_inventory.records
        if isinstance(record, PerturbationTrialRecord)
    )
    return replace(
        data,
        claim_ref=claim,
        left_distribution=left,
        right_distribution=right,
        capacity_difference=difference,
        bridge=bridge,
        protocol_inventory=Inventory(tuple(protocol_records), tuple(protocol_records)),
        completion_inventory=Inventory(completion_records, completion_records),
        refinement_inventory=Inventory(refinement_records, refinement_records),
        continuation_inventory=Inventory(
            tuple(continuation_records), tuple(continuation_records)
        ),
        perturbation_inventory=Inventory(perturbation_records, perturbation_records),
        declared_distribution_pairs=((left, right),),
    )


def _observations(fixture: Fixture, rows: dict[str, StatusRow]) -> dict[str, str]:
    base = fixture.claims["claim_coherent_wheel"]
    observed: dict[str, str] = {f"{name}.status": row.observed.value for name, row in rows.items()}
    pair = base.claim_ref.route_pair
    core = pair.package.core
    observed["claim_coherent_wheel.current_audit"] = (
        f"CurrentEventEquiv={str(current_event_equiv(core, pair.gamma_endpoint, pair.eta_endpoint)).lower()}; "
        + (
            "current_class(FT)=current_class(FF)"
            if quotient_class(core, pair.gamma_endpoint, predictive=False)
            == quotient_class(core, pair.eta_endpoint, predictive=False)
            else "current_class(FT)!=current_class(FF)"
        )
    )
    left = probability_for(base.left_distribution, C_REPAIR)
    right = probability_for(base.right_distribution, C_REPAIR)
    if left is None or right is None:
        raise RuntimeError("canonical E16 capacity records are incomplete")
    observed["claim_coherent_wheel.route_capacity"] = (
        f"C_repair: gamma={left.probability}; eta={right.probability}; unequal={str(left.probability != right.probability).lower()}"
    )
    current_trivial = all(current_event_equiv(core, core.push(history, ELL0), history) for history in core.histories)
    predictive_nontrivial = any(not future_predictive_equiv(core, core.push(history, ELL0), history) for history in core.histories)
    observed["claim_coherent_wheel.loop_anchor"] = (
        f"CurrentLoopTrivial={str(current_trivial).lower()}; PredictiveLoopNontrivial={str(predictive_nontrivial).lower()}; "
        f"current_image_fixed={str(current_trivial).lower()}"
    )
    regime_statuses = (
        rows["claim_flat_future"].observed,
        rows["claim_artifact_trap"].observed,
        rows["claim_flattenable"].observed,
        rows["claim_currentizable"].observed,
        rows["claim_dissipative"].observed,
        rows["claim_coherent_wheel"].observed,
    )
    regime_order = (
        ("flat", AdaptabilityStatus.flat),
        ("artifact", AdaptabilityStatus.artifact),
        ("flattenable", AdaptabilityStatus.flattenable),
        ("explicit_latent", AdaptabilityStatus.currentizable_slack),
        ("dissipative", AdaptabilityStatus.dissipative),
        ("coherent_candidate", AdaptabilityStatus.coherent_adaptability),
    )
    observed["six_regime_census"] = "; ".join(
        f"{label}={sum(status is target for status in regime_statuses)}"
        for label, target in regime_order
    )

    support = fixture.controls["ctrl_support_only"]
    observed["ctrl_support_only"] = f"supportFreedom={str(support_freedom(support)).lower()}; other_freedoms={str(flattening_freedom(support) and currentization_freedom(support) and dissipation_freedom(support)).lower()}; {classify_claim_data(support).value}"
    flatten = fixture.controls["ctrl_flattening_only"]
    observed["ctrl_flattening_only"] = f"flatteningFreedom={str(flattening_freedom(flatten)).lower()}; other_freedoms={str(support_freedom(flatten) and currentization_freedom(flatten) and dissipation_freedom(flatten)).lower()}; {classify_claim_data(flatten).value}"
    current = fixture.controls["ctrl_currentization_only"]
    completion_clears = flattenable_evidence_for(current)
    observed["ctrl_currentization_only"] = f"currentizationFreedom={str(currentization_freedom(current)).lower()}; completionClears={str(completion_clears).lower()}; {classify_claim_data(current).value}"
    dissipative = fixture.controls["ctrl_dissipation_only"]
    observed["ctrl_dissipation_only"] = f"dissipationFreedom={str(dissipation_freedom(dissipative)).lower()}; perturbations_preserve={str(all(dissipative.ctx.perturbation_preserves(record) for record in dissipative.perturbation_inventory.records if isinstance(record, PerturbationTrialRecord))).lower()}; {classify_claim_data(dissipative).value}"
    perturbation = fixture.controls["ctrl_perturbation_only"]
    observed["ctrl_perturbation_only"] = f"bounded_failure={str(bounded_perturbation_failure(perturbation)).lower()}; continuation_dissipation={str(dissipative_evidence_for(perturbation)).lower()}; {classify_claim_data(perturbation).value}"

    base = fixture.controls["ctrl_e15_still_outstanding"]
    outstanding_context = replace(base.e15_context, f3_awaiting_registry=frozenset(((base.bridge.residue.residue_id, F(10)),)))
    outstanding = replace(base, e15_context=outstanding_context)
    observed["ctrl_e15_still_outstanding"] = f"residue_eligible={str(bridge_eligible(outstanding)).lower()}; candidate={str(candidate_evidence(outstanding)).lower()}"
    base = fixture.controls["ctrl_e15_reconciled"]
    observed["ctrl_e15_reconciled"] = f"residue_eligible={str(bridge_eligible(base)).lower()}; proceeds_to_controls={str(coherent_adaptability_evidence_for(base)).lower()}"
    base = fixture.controls["ctrl_e15_disconnected_same_id"]
    payload = base.bridge.residue.route_residue
    if not isinstance(payload, RouteResiduePayload):
        raise RuntimeError("canonical E16 bridge lacks its full route-residue payload")
    changed_payload = replace(payload, challenge_class=C_SHIFT, gamma_probability=F(1, 2), eta_probability=F(1, 2))
    changed_residue = replace(base.bridge.residue, route_residue=changed_payload, residual_amount=F(1, 4))
    disconnected = replace(base, bridge=replace(base.bridge, residue=changed_residue))
    observed["ctrl_e15_disconnected_same_id"] = f"numeric_id_equal={str(changed_residue.residue_id == base.bridge.residue.residue_id).lower()}; full_record_equal={str(changed_residue == base.bridge.residue).lower()}; bridge_eligible={str(bridge_eligible(disconnected)).lower()}"
    base = fixture.controls["ctrl_undeclared_proxy"]
    declared_base_equal = all(
        isinstance(record, ProtocolCounterpartRecord)
        and record.comparison_base == base.claim_ref.package.comparison_base
        for record in base.protocol_inventory.records
    )
    observed["ctrl_undeclared_proxy"] = f"declared_base_equal={str(declared_base_equal).lower()}; SupportConfoundEvidenceFor={str(support_confound_evidence_for(base)).lower()}; mechanical_status={classify_claim_data(base).value}"

    base = fixture.controls["ctrl_wrong_route_endpoint"]
    wrong_pair = replace(base.claim_ref.route_pair, gamma_endpoint="TT")
    wrong_claim = replace(base.claim_ref, route_pair=wrong_pair)
    wrong_route = replace(base, claim_ref=wrong_claim)
    observed["ctrl_wrong_route_endpoint"] = f"endpoint_linkage={str(route_pair_linked(wrong_pair)).lower()}; capacity_difference={str(declared_capacity_difference(wrong_route)).lower()}"
    base = fixture.controls["ctrl_different_protocols"]
    other_protocol = replace(base.right_distribution.protocol, protocol_id=base.right_distribution.protocol.protocol_id + 1)
    different_protocols = replace(base, right_distribution=replace(base.right_distribution, protocol=other_protocol))
    observed["ctrl_different_protocols"] = f"sameProtocol={str(base.left_distribution.protocol == different_protocols.right_distribution.protocol).lower()}; distribution_pair={str(distributions_match_claim(different_protocols)).lower()}"
    base = fixture.controls["ctrl_route_inadmissible"]
    route_ctx = replace(base.ctx, admissible_route_pairs=frozenset())
    route_bad = replace(base, ctx=route_ctx, administrative_reason="pair_inadmissible")
    observed["ctrl_route_inadmissible"] = f"routePairAdmissible={str(route_ctx.route_pair_admissible(base.claim_ref.route_pair)).lower()}; candidate={str(candidate_evidence(route_bad)).lower()}; administrative_rejection={str(administrative_rejection(route_bad)).lower()}"
    base = fixture.controls["ctrl_package_undeclared"]
    package_ctx = replace(base.ctx, declared_package_ids=frozenset())
    package_bad = replace(base, ctx=package_ctx, administrative_reason="package_undeclared")
    observed["ctrl_package_undeclared"] = f"routePackageDeclared={str(package_ctx.route_package_declared(base.claim_ref.package)).lower()}; candidate={str(candidate_evidence(package_bad)).lower()}; administrative_rejection={str(administrative_rejection(package_bad)).lower()}"
    base = fixture.controls["ctrl_budget_linkage"]
    budget_ctx = replace(base.ctx, protocol_budget_links=frozenset())
    budget_bad = replace(base, ctx=budget_ctx, administrative_reason="protocol_budget_unlinked")
    observed["ctrl_budget_linkage"] = f"binding={str(binding_budget(budget_bad)).lower()}; protocolUsesBindingBudget={str(budget_ctx.protocol_uses_binding_budget(base.claim_ref.protocol, base.claim_ref.budget)).lower()}; flat={str(flat_evidence_for(budget_bad)).lower()}; rejected={str(adaptability_rejected_evidence_for(budget_bad)).lower()}"

    base = fixture.controls["ctrl_undeclared_challenge_difference"]
    hidden_record = ProbabilityRecord(id_base(1029) + 100, "C_hidden", F(1), (), F(10))
    hidden_left = replace(base.left_distribution, records=base.left_distribution.records + (hidden_record,))
    hidden = replace(base, left_distribution=hidden_left)
    observed["ctrl_undeclared_challenge_difference"] = f"C_hidden_not_declared={str('C_hidden' not in base.claim_ref.protocol.family.classes).lower()}; capacity_difference={str(declared_capacity_difference(hidden)).lower()}"
    base = fixture.controls["ctrl_missing_declared_class"]
    missing = replace(base.left_distribution, records=(base.left_distribution.records[0],))
    observed["ctrl_missing_declared_class"] = f"everyClassCovered={str(distribution_checks(missing, base.ctx)['everyClassCovered']).lower()}; complete_distribution={str(complete_distribution(missing, base.ctx)).lower()}"
    base = fixture.controls["ctrl_duplicate_probability_record"]
    duplicate_record = replace(base.left_distribution, records=base.left_distribution.records + (base.left_distribution.records[0],))
    observed["ctrl_duplicate_probability_record"] = f"recordsNodup={str(distribution_checks(duplicate_record, base.ctx)['recordsNodup']).lower()}; complete_distribution={str(complete_distribution(duplicate_record, base.ctx)).lower()}"
    base = fixture.controls["ctrl_duplicate_probability_id"]
    same_id = replace(base.left_distribution.records[0], probability=F(1, 2))
    duplicate_id = replace(base.left_distribution, records=base.left_distribution.records + (same_id,))
    observed["ctrl_duplicate_probability_id"] = f"recordIdsNodup={str(distribution_checks(duplicate_id, base.ctx)['recordIdsNodup']).lower()}; complete_distribution={str(complete_distribution(duplicate_id, base.ctx)).lower()}"
    base = fixture.controls["ctrl_contradictory_same_class"]
    same_id = replace(base.left_distribution.records[0], probability=F(1, 2))
    contradictory = replace(same_id, probability_record_id=same_id.probability_record_id + 50000)
    contradictory_distribution = replace(base.left_distribution, records=base.left_distribution.records + (contradictory,))
    observed["ctrl_contradictory_same_class"] = f"singleValuedPerClass={str(distribution_checks(contradictory_distribution, base.ctx)['singleValuedPerClass']).lower()}; complete_distribution={str(complete_distribution(contradictory_distribution, base.ctx)).lower()}"
    base = fixture.controls["ctrl_uncarried_ledger_support"]
    first_probability = base.left_distribution.records[0]
    uncarried_entry = _mutate_record_carried(first_probability.supporting_entries[0], source_tag=FineSourceTag.fallback)
    uncarried_probability = replace(first_probability, supporting_entries=(uncarried_entry,) + first_probability.supporting_entries[1:])
    uncarried_ledger = replace(base.left_distribution, records=(uncarried_probability,) + base.left_distribution.records[1:])
    observed["ctrl_uncarried_ledger_support"] = f"everyLedgerEntryCarried={str(distribution_checks(uncarried_ledger, base.ctx)['everyLedgerEntryCarried']).lower()}; capacity_difference={str(declared_capacity_difference(replace(base, left_distribution=uncarried_ledger))).lower()}"
    base = fixture.controls["ctrl_uncarried_distribution"]
    uncarried_distribution = _mutate_record_carried(base.left_distribution, source_tag=FineSourceTag.fallback)
    observed["ctrl_uncarried_distribution"] = f"distributionCarried={str(distribution_checks(uncarried_distribution, base.ctx)['distributionCarried']).lower()}; complete_distribution={str(complete_distribution(uncarried_distribution, base.ctx)).lower()}"
    base = fixture.controls["ctrl_probability_ledger_computation"]
    first_probability = base.left_distribution.records[0]
    repair_trials = tuple(
        replace(trial, ledger_after=())
        if trial.challenge_class == C_REPAIR
        and trial.trial_id == _trial_id(id_base(base.fixture_index), 0, 0, 2)
        else trial
        for trial in base.left_distribution.trials
    )
    ledger_wrong = replace(
        first_probability,
        probability=F(3, 4),
        supporting_entries=first_probability.supporting_entries[:2],
    )
    ledger_wrong_dist = replace(
        base.left_distribution,
        records=(ledger_wrong,) + base.left_distribution.records[1:],
        trials=repair_trials,
    )
    trial_replacements = dict(zip(base.left_distribution.trials, repair_trials))
    ledger_ctx = replace(
        base.ctx,
        eligible_route_endpoint_trials=frozenset(
            trial_replacements.get(trial, trial)
            for trial in base.ctx.eligible_route_endpoint_trials
        ),
    )
    computed_ratio = F(
        len(successful_trials(ledger_wrong_dist, C_REPAIR, ledger_ctx)),
        len(eligible_trials(ledger_wrong_dist, C_REPAIR, ledger_ctx)),
    )
    observed["ctrl_probability_ledger_computation"] = f"stored=3/4; computed={computed_ratio}; everyProbabilityComputed={str(distribution_checks(ledger_wrong_dist, ledger_ctx)['everyProbabilityComputed']).lower()}"
    base = fixture.controls["ctrl_ledger_relevance"]
    first_probability = base.left_distribution.records[0]
    irrelevant_entry = first_probability.supporting_entries[0]
    irrelevant_probability = replace(first_probability, supporting_entries=(irrelevant_entry,) + first_probability.supporting_entries[1:])
    irrelevant_dist = replace(base.left_distribution, records=(irrelevant_probability,) + base.left_distribution.records[1:])
    relevance_ctx = replace(
        base.ctx,
        relevant_ledger_entry_ids=base.ctx.relevant_ledger_entry_ids.difference(
            (irrelevant_entry.ledger_entry_id,)
        ),
    )
    relevance_data = replace(base, left_distribution=irrelevant_dist, ctx=relevance_ctx)
    observed["ctrl_ledger_relevance"] = f"supportingLedgerEntryRelevant={str(relevance_ctx.ledger_entry_relevant(irrelevant_entry)).lower()}; capacity_difference={str(declared_capacity_difference(relevance_data)).lower()}"
    base = fixture.controls["ctrl_exact_denominator"]
    first_probability = base.left_distribution.records[0]
    denominator_record = replace(first_probability, probability=F(2, 3))
    denominator_dist = replace(base.left_distribution, records=(denominator_record,) + base.left_distribution.records[1:])
    eligible_count = len(eligible_trials(denominator_dist, C_REPAIR, base.ctx))
    successful_count = len(successful_trials(denominator_dist, C_REPAIR, base.ctx))
    exact_ratio = denominator_record.probability == F(successful_count, eligible_count)
    observed["ctrl_exact_denominator"] = f"successful={successful_count}; eligible={eligible_count}; stored=2/3; everyProbabilityComputed={str(distribution_checks(denominator_dist, base.ctx)['everyProbabilityComputed']).lower()}; exact_ratio={str(exact_ratio).lower()}"
    base = fixture.controls["ctrl_trial_inventory_omission"]
    omitted_trial = replace(base.left_distribution, trials=base.left_distribution.trials[:-1])
    omitted_checks = trial_inventory_checks(omitted_trial, base.ctx)
    observed["ctrl_trial_inventory_omission"] = f"eligible_trial_missing={str(not omitted_checks['everyEligibleTrialCovered']).lower()}; everyEligibleTrialCovered={str(omitted_checks['everyEligibleTrialCovered']).lower()}"

    inventory_specs = (
        ("ctrl_protocol_inventory_omission", "supportFreedom", "protocol", support_freedom),
        ("ctrl_completion_inventory_omission", "flatteningFreedom", "completion", flattening_freedom),
        ("ctrl_refinement_inventory_omission", "currentizationFreedom", "refinement", currentization_freedom),
        ("ctrl_continuation_inventory_omission", "dissipationFreedom", "continuation", dissipation_freedom),
    )
    for name, label, kind, freedom in inventory_specs:
        data = fixture.controls[name]
        inventory = getattr(data, f"{kind}_inventory")
        mutated_inventory = Inventory((), inventory.eligible_records)
        field = f"{kind}_inventory"
        mutated = replace(data, **{field: mutated_inventory})
        checks = inventory_checks(mutated_inventory, lambda record, k=kind: eligible_counterpart(mutated, k, record))
        observed[name] = f"eligible_{'counterpart' if kind == 'protocol' else kind}_missing={str(not checks['everyEligibleCovered']).lower()}; {label}={str(freedom(mutated)).lower()}"
    base = fixture.controls["ctrl_perturbation_inventory_omission"]
    perturbation_omitted = replace(base, perturbation_inventory=Inventory(base.perturbation_inventory.records[:-1], base.perturbation_inventory.eligible_records))
    perturb_checks = inventory_checks(perturbation_omitted.perturbation_inventory, lambda record: perturbation_eligible(perturbation_omitted, record))
    observed["ctrl_perturbation_inventory_omission"] = f"eligible_trial_missing={str(not perturb_checks['everyEligibleCovered']).lower()}; dissipationFreedom={str(dissipation_freedom(perturbation_omitted)).lower()}"
    base = fixture.controls["ctrl_duplicate_counterpart_key"]
    duplicate_counterpart = replace(base.completion_inventory.records[0], witness_count=0)
    dup_inventory = Inventory(base.completion_inventory.records + (duplicate_counterpart,), base.completion_inventory.eligible_records + (duplicate_counterpart,))
    dup_checks = inventory_checks(dup_inventory, lambda record: eligible_counterpart(base, "completion", record))
    observed["ctrl_duplicate_counterpart_key"] = f"recordIdsNodup={str(dup_checks['recordIdsNodup']).lower()}; singleValuedPerDeclaredKey={str(dup_checks['singleValuedPerDeclaredKey']).lower()}"
    base = fixture.controls["ctrl_unregistered_dissipating_continuation"]
    off_inventory = _off_inventory_continuation(base)
    off_ctx = replace(
        base.ctx,
        admissible_counterpart_ids=base.ctx.admissible_counterpart_ids.union((off_inventory.counterpart_id,)),
    )
    base = replace(base, ctx=off_ctx)
    observed["ctrl_unregistered_dissipating_continuation"] = f"off_inventory={str(off_inventory not in base.continuation_inventory.records).lower()}; DissipativeEvidenceFor={str(dissipative_evidence_for(base)).lower()}"
    base = fixture.controls["ctrl_completion_label_without_collapse"]
    completion_label = base.completion_inventory.records[0]
    observed["ctrl_completion_label_without_collapse"] = f"witnessCount={completion_label.witness_count}; discrepancy={completion_label.discrepancy}; clears={str(base.ctx.counterpart_clears(completion_label)).lower()}"
    base = fixture.controls["ctrl_changed_support_refinement"]
    changed_base = ComparisonBaseRecord(id_base(1048) + 5009, ("changed",), F(0))
    changed_package = replace(
        base.claim_ref.package,
        package_id=id_base(1048) + 5010,
        comparison_base=changed_base,
    )
    changed_pair = replace(
        base.claim_ref.route_pair,
        package=changed_package,
    )
    changed_refinement = replace(
        base.refinement_inventory.records[0],
        comparison_base=changed_base,
        refined_package=changed_package,
        refined_pair=changed_pair,
        witness_count=0,
        discrepancy=F(0),
        max_fiber=1,
    )
    changed_ctx = replace(
        base.ctx,
        admissible_counterpart_ids=frozenset((changed_refinement.counterpart_id,)),
    )
    changed_refinement_data = replace(base, ctx=changed_ctx, refinement_inventory=Inventory((changed_refinement,), (changed_refinement,)))
    observed["ctrl_changed_support_refinement"] = f"refinement_base_equal={str(changed_refinement.comparison_base == base.claim_ref.package.comparison_base).lower()}; changed_base_refinement_cannot_currentize={str(not currentizable_evidence_for(changed_refinement_data)).lower()}; CurrentizableEvidenceFor={str(currentizable_evidence_for(changed_refinement_data)).lower()}; SupportConfoundEvidenceFor={str(support_confound_evidence_for(changed_refinement_data)).lower()}"
    base = fixture.controls["ctrl_out_of_bound_perturbation"]
    out_of_bound = PerturbationTrialRecord(
        id_base(1049) + 7103,
        base.claim_ref.candidate_id,
        F(10),
        base.claim_ref.package.comparison_base,
        base.claim_ref.package,
        base.claim_ref.route_pair,
        F(3, 4),
    )
    out_data = replace(base, perturbation_inventory=Inventory(base.perturbation_inventory.records, base.perturbation_inventory.eligible_records))
    observed["ctrl_out_of_bound_perturbation"] = f"magnitude=3/4; bound=1/2; eligible={str(perturbation_eligible(out_data, out_of_bound)).lower()}; coherence_unchanged={str(coherent_adaptability_evidence_for(out_data)).lower()}"

    for name in (
        "ctrl_wrong_claim_route", "ctrl_wrong_claim_challenge",
        "ctrl_wrong_claim_protocol", "ctrl_wrong_claim_time",
    ):
        data = fixture.controls[name]
        if name.endswith("route"):
            claim = replace(data.claim_ref, route_pair=replace(data.claim_ref.route_pair, route_pair_id=data.claim_ref.route_pair.route_pair_id + 1))
        elif name.endswith("challenge"):
            claim = replace(data.claim_ref, challenge_class=C_SHIFT)
        elif name.endswith("protocol"):
            claim = replace(data.claim_ref, protocol=replace(data.claim_ref.protocol, protocol_id=data.claim_ref.protocol.protocol_id + 1))
        else:
            claim = replace(data.claim_ref, observed_at=F(11))
        valid_other_claim = coherent_adaptability_evidence_for(data)
        other = replace(data, claim_ref=claim)
        evidence = coherent_adaptability_evidence_for(other)
        prefix = (
            f"other_time={claim.observed_at}; current_time={data.claim_ref.observed_at}; "
            if name.endswith("time")
            else f"valid_other_claim={str(valid_other_claim).lower()}; "
        )
        observed[name] = prefix + f"evidence_for_current={str(evidence).lower()}"

    artifact = _build_claim(
        "ctrl_priority_artifact_flattening_collision", 1054, fixture.wheel,
        artifact=True,
    )
    artifact_completion = replace(artifact.completion_inventory.records[0], witness_count=0, discrepancy=F(0))
    collision = replace(artifact, completion_inventory=Inventory((artifact_completion,), (artifact_completion,)))
    observed["ctrl_priority_artifact_flattening_collision"] = f"artifactEvidence={str(artifact_evidence_for(collision)).lower()}; flattenableEvidence={str(flattenable_evidence_for(collision)).lower()}; status={classify_claim_data(collision).value}"
    lower_base = _build_claim("ctrl_lower_tag_with_raw_artifact", 1055, fixture.wheel, artifact=True)
    lower_completion = replace(lower_base.completion_inventory.records[0], witness_count=0, discrepancy=F(0))
    lower_collision = replace(lower_base, completion_inventory=Inventory((lower_completion,), (lower_completion,)))
    lower_record = StatusRecord(id_base(1055) + 14, lower_collision.claim_ref, AdaptabilityStatus.flattenable, F(10))
    observed["ctrl_lower_tag_with_raw_artifact"] = f"record_tag={lower_record.status.value}; ArtifactEvidenceFor={str(artifact_evidence_for(lower_collision)).lower()}; FlattenableCase={str(case_holds(lower_collision, lower_record, AdaptabilityStatus.flattenable)).lower()}"
    unique_data = _build_claim("ctrl_status_uniqueness", 1056, fixture.wheel, artifact=True)
    artifact_record = StatusRecord(id_base(1056) + 14, unique_data.claim_ref, AdaptabilityStatus.artifact, F(10))
    flatten_record = StatusRecord(id_base(1056) + 15, unique_data.claim_ref, AdaptabilityStatus.flattenable, F(10))
    complete_status = complete_adaptability_status(unique_data, artifact_record) and complete_adaptability_status(unique_data, flatten_record)
    observed["ctrl_status_uniqueness"] = f"same_claim={str(artifact_record.claim_ref == flatten_record.claim_ref).lower()}; tags=(artifact,flattenable); complete_status={str(complete_status).lower()}"

    base = fixture.controls["mut_counterpart_admissibility"]
    admissibility_results: list[str] = []
    for kind, field in (("protocol", "protocol_inventory"), ("completion", "completion_inventory"), ("refinement", "refinement_inventory"), ("continuation", "continuation_inventory")):
        inventory = getattr(base, field)
        bad_record = inventory.records[0]
        bad_inventory = inventory
        bad_ctx = replace(
            base.ctx,
            admissible_counterpart_ids=base.ctx.admissible_counterpart_ids.difference((bad_record.counterpart_id,)),
        )
        mutated = replace(base, ctx=bad_ctx, **{field: bad_inventory})
        before = inventory_checks(inventory, lambda record, k=kind: eligible_counterpart(base, k, record))["everyRecordEligible"]
        after = inventory_checks(bad_inventory, lambda record, k=kind: eligible_counterpart(mutated, k, record))["everyRecordEligible"]
        admissibility_results.append(f"{kind} admissible {str(before).lower()}->{str(after).lower()} and inventory_sound {str(before).lower()}->{str(after).lower()}")
    all_admissibility_flipped = all("true->false" in result for result in admissibility_results)
    observed["mut_counterpart_admissibility"] = (
        "protocol/completion/refinement/continuation: each admissible true->false and inventory_sound true->false"
        if all_admissibility_flipped else "counterpart admissibility mutation failed"
    )
    base = fixture.controls["mut_honest_protocol_clears"]
    protocol_clear = replace(base.protocol_inventory.records[0], honest_difference=None)
    protocol_mut = replace(base, protocol_inventory=Inventory((protocol_clear,), (protocol_clear,)))
    observed["mut_honest_protocol_clears"] = f"false->true; ArtifactEvidenceFor={str(artifact_evidence_for(base)).lower()}->{str(artifact_evidence_for(protocol_mut)).lower()}"
    base = fixture.controls["mut_completion_clears"]
    completion_clear = replace(base.completion_inventory.records[0], witness_count=0, discrepancy=F(0))
    completion_mut = replace(base, completion_inventory=Inventory((completion_clear,), (completion_clear,)))
    observed["mut_completion_clears"] = f"false->true; FlattenableEvidenceFor={str(flattenable_evidence_for(base)).lower()}->{str(flattenable_evidence_for(completion_mut)).lower()}"
    base = fixture.controls["mut_refinement_currentizes"]
    refinement_clear = replace(base.refinement_inventory.records[0], witness_count=0, discrepancy=F(0), max_fiber=1)
    refinement_mut = replace(base, refinement_inventory=Inventory((refinement_clear,), (refinement_clear,)))
    observed["mut_refinement_currentizes"] = f"false->true; CurrentizableEvidenceFor={str(currentizable_evidence_for(base)).lower()}->{str(currentizable_evidence_for(refinement_mut)).lower()}"
    base = fixture.controls["mut_continuation_dissipates"]
    continuation_clear = replace(
        base.continuation_inventory.records[0],
        continuation=ERASE_LATENT,
        left_after=base.claim_ref.package.core.push(
            base.claim_ref.route_pair.gamma_endpoint, ERASE_LATENT
        ),
        right_after=base.claim_ref.package.core.push(
            base.claim_ref.route_pair.eta_endpoint, ERASE_LATENT
        ),
        later_difference=None,
    )
    continuation_mut = replace(base, continuation_inventory=Inventory((continuation_clear,), (continuation_clear,)))
    observed["mut_continuation_dissipates"] = f"false->true; DissipativeEvidenceFor={str(dissipative_evidence_for(base)).lower()}->{str(dissipative_evidence_for(continuation_mut)).lower()}"
    base = fixture.controls["mut_perturbation_survival"]
    perturbed_record = replace(
        base.perturbation_inventory.records[1],
        perturbed_pair=replace(
            base.perturbation_inventory.records[1].perturbed_pair,
            eta=base.perturbation_inventory.records[1].perturbed_pair.gamma,
            eta_endpoint=base.perturbation_inventory.records[1].perturbed_pair.gamma_endpoint,
        ),
    )
    perturbation_mut = replace(
        base,
        ctx=replace(
            base.ctx,
            eligible_perturbation_trials=frozenset(
                perturbed_record if record == base.perturbation_inventory.records[1]
                else record
                for record in base.ctx.eligible_perturbation_trials
            ),
        ),
        perturbation_inventory=Inventory(
            (base.perturbation_inventory.records[0], perturbed_record, base.perturbation_inventory.records[2]),
            (base.perturbation_inventory.eligible_records[0], perturbed_record, base.perturbation_inventory.eligible_records[2]),
        ),
    )
    observed["mut_perturbation_survival"] = f"true->false at 1/4; coherent={str(coherent_adaptability_evidence_for(perturbation_mut)).lower()}; rejected={str(adaptability_rejected_evidence_for(perturbation_mut)).lower()}"
    base = fixture.controls["mut_e15_bridge_acceptance"]
    bridge_bad = replace(base, ctx=replace(base.ctx, accepted_bridge_ids=frozenset()))
    observed["mut_e15_bridge_acceptance"] = f"true->false; residue_eligible={str(bridge_eligible(base)).lower()}->{str(bridge_eligible(bridge_bad)).lower()}"
    base = fixture.controls["mut_e15_outstanding_status"]
    outstanding_context = replace(base.e15_context, f3_awaiting_registry=frozenset(((base.bridge.residue.residue_id, F(10)),)))
    outstanding = replace(base, e15_context=outstanding_context)
    observed["mut_e15_outstanding_status"] = f"false->true at time 10; residue_eligible={str(bridge_eligible(base)).lower()}->{str(bridge_eligible(outstanding)).lower()}"

    base = fixture.controls["mut_carriedness_fields"]
    representatives = (
        base.claim_ref.package,
        base.claim_ref.package.comparison_base,
        base.claim_ref.route_pair,
        base.claim_ref.protocol,
        base.claim_ref.protocol.family,
        base.left_distribution,
        base.left_distribution.records[0],
        base.left_distribution.trials[0],
        base.protocol_inventory.records[0],
        base.completion_inventory.records[0],
        base.refinement_inventory.records[0],
        base.continuation_inventory.records[0],
        base.bridge,
        StatusRecord(id_base(1065) + 14, base.claim_ref, classify_claim_data(base), F(10)),
    )
    carried_flips = all(
        not e16_carried(_mutate_record_carried(record, **mutation))
        for record in representatives
        for mutation in (
            {"source_tag": FineSourceTag.fallback},
            {"generated_by_s": False},
            {"in_scope": False},
        )
    )
    observed["mut_carriedness_fields"] = f"sourceTag/generatedByS/inScope flips each make E16Carried={str(not carried_flips).lower()}"
    base = fixture.controls["mut_predictive_reveal"]
    no_reveal_data = _relink_no_reveal_claim(base, fixture.no_reveal)
    no_reveal_pair = no_reveal_data.claim_ref.route_pair
    observed["mut_predictive_reveal"] = f"no_reveal_core Continuation={{id,ell0}}; FuturePredictiveEquiv={str(future_predictive_equiv(fixture.no_reveal, no_reveal_pair.gamma_endpoint, no_reveal_pair.eta_endpoint)).lower()}; witness={str(route_predictive_witness(no_reveal_pair)).lower()}; candidate={str(candidate_evidence(no_reveal_data)).lower()}"

    data = fixture.controls["ctrl_flat_unrelated_pair_rejected"]
    if (
        data.left_distribution is None
        or data.right_distribution is None
        or len(data.declared_distribution_pairs) != 2
    ):
        raise RuntimeError("flat unrelated-pair control is incomplete")
    evaluations = declared_flat_pair_evaluations(data)
    claim_left, claim_right, _, claim_pair_no_difference = evaluations[0]
    unrelated_left, unrelated_right, unrelated_pair_matches_claim, unrelated_pair_equal = (
        evaluations[1]
    )
    if (
        claim_left != data.left_distribution
        or claim_right != data.right_distribution
    ):
        raise RuntimeError("flat control's first declared pair is not its claim pair")
    claim_pair_unequal = declared_capacity_difference(data)
    unrelated_pair_complete = repair_capacity_distribution_pair_complete(
        data.ctx,
        data.claim_ref.route_pair,
        unrelated_left,
        unrelated_right,
    )
    observed["ctrl_flat_unrelated_pair_rejected"] = (
        f"claim_pair_unequal={str(claim_pair_unequal).lower()}; "
        f"claim_pair_no_difference={str(claim_pair_no_difference).lower()}; "
        f"unrelated_pair_complete={str(unrelated_pair_complete).lower()}; "
        f"unrelated_pair_equal={str(unrelated_pair_equal).lower()}; "
        f"unrelated_pair_matches_claim={str(unrelated_pair_matches_claim).lower()}; "
        f"FlatEvidenceFor={str(flat_evidence_for(data)).lower()}"
    )

    data = fixture.controls["ctrl_perturbation_off_universe_rejected"]
    off_universe = data.off_universe_perturbation
    if off_universe is None:
        raise RuntimeError("off-universe perturbation control lacks its trial")
    baseline_checks = complete_perturbation_inventory_checks(data)
    force_included = replace(
        data,
        perturbation_inventory=replace(
            data.perturbation_inventory,
            records=data.perturbation_inventory.records + (off_universe,),
        ),
    )
    included_checks = complete_perturbation_inventory_checks(force_included)
    observed["ctrl_perturbation_off_universe_rejected"] = (
        f"old_conditions_met={str(perturbation_old_conditions(data, off_universe)).lower()}; "
        f"perturbationTrialEligible={str(data.ctx.perturbation_trial_eligible(off_universe)).lower()}; "
        f"coverage_unaffected={str(baseline_checks['everyEligibleCovered']).lower()}; "
        f"record_inclusion_fails_soundness={str(not included_checks['everyRecordEligible']).lower()}"
    )

    data = fixture.controls["ctrl_swapped_trial_populations_rejected"]
    if data.left_distribution is None or data.right_distribution is None:
        raise RuntimeError("swapped trial control lacks its distributions")
    left_checks = trial_inventory_checks(data.left_distribution, data.ctx)
    right_checks = trial_inventory_checks(data.right_distribution, data.ctx)
    every_trial_eligible = (
        left_checks["everyTrialEligible"] and right_checks["everyTrialEligible"]
    )
    complete_distributions = (
        complete_distribution(data.left_distribution, data.ctx)
        and complete_distribution(data.right_distribution, data.ctx)
    )
    observed["ctrl_swapped_trial_populations_rejected"] = (
        f"everyTrialEligible={str(every_trial_eligible).lower()}; "
        f"complete_distribution={str(complete_distributions).lower()}"
    )
    return observed


EXPECTED_VALUES = (
    "coherent_adaptability", "support_confound", "artifact", "flat", "flat", "flattenable", "currentizable_slack", "dissipative", "adaptability_rejected", "adaptability_rejected",
    "CurrentEventEquiv=true; current_class(FT)=current_class(FF)",
    "C_repair: gamma=3/4; eta=1/4; unequal=true",
    "CurrentLoopTrivial=true; PredictiveLoopNontrivial=true; current_image_fixed=true",
    "flat=1; artifact=1; flattenable=1; explicit_latent=1; dissipative=1; coherent_candidate=1",
    "supportFreedom=false; other_freedoms=true; support_confound",
    "flatteningFreedom=false; other_freedoms=true; flattenable",
    "currentizationFreedom=false; completionClears=false; currentizable_slack",
    "dissipationFreedom=false; perturbations_preserve=true; dissipative",
    "bounded_failure=true; continuation_dissipation=false; adaptability_rejected",
    "residue_eligible=false; candidate=false", "residue_eligible=true; proceeds_to_controls=true",
    "numeric_id_equal=true; full_record_equal=false; bridge_eligible=false",
    "declared_base_equal=true; SupportConfoundEvidenceFor=false; mechanical_status=coherent_adaptability",
    "endpoint_linkage=false; capacity_difference=false", "sameProtocol=false; distribution_pair=false",
    "routePairAdmissible=false; candidate=false; administrative_rejection=true",
    "routePackageDeclared=false; candidate=false; administrative_rejection=true",
    "binding=true; protocolUsesBindingBudget=false; flat=false; rejected=true",
    "C_hidden_not_declared=true; capacity_difference=false", "everyClassCovered=false; complete_distribution=false",
    "recordsNodup=false; complete_distribution=false", "recordIdsNodup=false; complete_distribution=false",
    "singleValuedPerClass=false; complete_distribution=false", "everyLedgerEntryCarried=false; capacity_difference=false",
    "distributionCarried=false; complete_distribution=false", "stored=3/4; computed=1/2; everyProbabilityComputed=false",
    "supportingLedgerEntryRelevant=false; capacity_difference=false",
    "successful=3; eligible=4; stored=2/3; everyProbabilityComputed=false; exact_ratio=false",
    "eligible_trial_missing=true; everyEligibleTrialCovered=false", "eligible_counterpart_missing=true; supportFreedom=false",
    "eligible_completion_missing=true; flatteningFreedom=false", "eligible_refinement_missing=true; currentizationFreedom=false",
    "eligible_continuation_missing=true; dissipationFreedom=false", "eligible_trial_missing=true; dissipationFreedom=false",
    "recordIdsNodup=false; singleValuedPerDeclaredKey=false", "off_inventory=true; DissipativeEvidenceFor=false",
    "witnessCount=1; discrepancy=1/2; clears=false",
    "refinement_base_equal=false; changed_base_refinement_cannot_currentize=true; CurrentizableEvidenceFor=false; SupportConfoundEvidenceFor=false",
    "magnitude=3/4; bound=1/2; eligible=false; coherence_unchanged=true",
    "valid_other_claim=true; evidence_for_current=false", "valid_other_claim=true; evidence_for_current=false",
    "valid_other_claim=true; evidence_for_current=false", "other_time=11; current_time=10; evidence_for_current=false",
    "artifactEvidence=true; flattenableEvidence=true; status=artifact",
    "record_tag=flattenable; ArtifactEvidenceFor=true; FlattenableCase=false",
    "same_claim=true; tags=(artifact,flattenable); complete_status=false",
    "protocol/completion/refinement/continuation: each admissible true->false and inventory_sound true->false",
    "false->true; ArtifactEvidenceFor=false->true", "false->true; FlattenableEvidenceFor=false->true",
    "false->true; CurrentizableEvidenceFor=false->true", "false->true; DissipativeEvidenceFor=false->true",
    "true->false at 1/4; coherent=false; rejected=true", "true->false; residue_eligible=true->false",
    "false->true at time 10; residue_eligible=true->false",
    "sourceTag/generatedByS/inScope flips each make E16Carried=false",
    "no_reveal_core Continuation={id,ell0}; FuturePredictiveEquiv=true; witness=false; candidate=false",
    "claim_pair_unequal=true; claim_pair_no_difference=false; unrelated_pair_complete=true; unrelated_pair_equal=true; unrelated_pair_matches_claim=false; FlatEvidenceFor=false",
    "old_conditions_met=true; perturbationTrialEligible=false; coverage_unaffected=true; record_inclusion_fails_soundness=true",
    "everyTrialEligible=false; complete_distribution=false",
)


def _comparisons(fixture: Fixture, rows: dict[str, StatusRow]) -> tuple[Comparison, ...]:
    observed = _observations(fixture, rows)
    if len(REGISTERED_COMPARISON_ORDER) != 69 or len(EXPECTED_VALUES) != 69:
        raise RuntimeError("E16 registered comparison table must contain exactly 69 rows")
    return tuple(
        Comparison(name, observed[name] == expected, observed[name], expected)
        for name, expected in zip(REGISTERED_COMPARISON_ORDER, EXPECTED_VALUES, strict=True)
    )


def _actual_scope_discipline(fixture: Fixture, rows: dict[str, StatusRow]) -> bool:
    return (
        len(fixture.wheel.continuations) == 4 ** 4
        and core_laws(fixture.wheel)
        and core_laws(fixture.flat_native)
        and core_laws(fixture.no_reveal)
        and flat_at(fixture.flat_native)
        and not flat_at(fixture.wheel)
        and quotient_class(fixture.wheel, "FT", predictive=True)
        != quotient_class(fixture.wheel, "FF", predictive=True)
        and all(
        status_occurrence_for(fixture.claims[name].claim_ref, row.status_record)
        and complete_adaptability_status(fixture.claims[name], row.status_record)
        for name, row in rows.items()
        )
    )


def _no_hardcoded_status_discipline(rows: dict[str, StatusRow], comparisons: tuple[Comparison, ...]) -> bool:
    return all(
        row.observed is not AdaptabilityStatus.unclassified
        and sum(row.truths.values()) == 1
        and row.truths[row.observed]
        and row.status_record.status is row.observed
        for row in rows.values()
    ) and all(comparison.passed for comparison in comparisons)


def _off_inventory_isolation_discipline(fixture: Fixture) -> bool:
    data = fixture.controls["ctrl_unregistered_dissipating_continuation"]
    off_record = _off_inventory_continuation(data)
    off_clears = continuation_dissipates(data, off_record)
    omitted = (
        off_record not in data.continuation_inventory.records
        and off_record not in data.continuation_inventory.eligible_records
    )
    baseline_complete = counterpart_complete(
        data, "continuation", data.continuation_inventory
    )
    baseline_rejects = not dissipative_evidence_for(data)
    admitted_ctx = replace(
        data.ctx,
        admissible_counterpart_ids=data.ctx.admissible_counterpart_ids.union(
            (off_record.counterpart_id,)
        ),
    )
    admitted = replace(
        data,
        ctx=admitted_ctx,
        continuation_inventory=Inventory((off_record,), (off_record,)),
    )
    return (
        off_clears
        and omitted
        and baseline_complete
        and baseline_rejects
        and counterpart_complete(admitted, "continuation", admitted.continuation_inventory)
        and dissipative_evidence_for(admitted)
    )


def _predictive_reveal_isolation_discipline(fixture: Fixture) -> bool:
    data = _relink_no_reveal_claim(
        fixture.controls["mut_predictive_reveal"], fixture.no_reveal
    )
    checks = candidate_evidence_checks(data)
    return (
        checks["predictiveWitness"] is False
        and all(value for name, value in checks.items() if name != "predictiveWitness")
        and candidate_evidence(data) is False
    )


def _administrative_without_candidate_discipline(fixture: Fixture) -> bool:
    baseline = fixture.controls["ctrl_package_undeclared"]
    data = replace(
        baseline,
        ctx=replace(baseline.ctx, declared_package_ids=frozenset()),
        left_distribution=None,
        right_distribution=None,
        capacity_difference=None,
        bridge=None,
        administrative_reason="package_undeclared",
    )
    return (
        not candidate_matches_claim(data)
        and not data.ctx.route_package_declared(data.claim_ref.package)
        and administrative_rejection(data)
    )


def _wrong_claim_bridge_isolation_discipline(fixture: Fixture) -> bool:
    baseline = fixture.claims["claim_coherent_wheel"]
    if baseline.bridge is None:
        return False
    wrong_residue = replace(
        baseline.bridge.residue,
        reconciliation_claim_id=baseline.claim_ref.candidate_id + 1,
    )
    wrong_claim = replace(
        baseline,
        bridge=replace(baseline.bridge, residue=wrong_residue),
    )
    return bridge_eligible(baseline) and not bridge_eligible(wrong_claim)


def _route_trial_clone_rejected_discipline(fixture: Fixture) -> bool:
    baseline = fixture.claims["claim_coherent_wheel"]
    if baseline.left_distribution is None:
        return False
    original = baseline.left_distribution.trials[0]
    clone = replace(
        original,
        ledger_after=original.ledger_after
        + (original.discharge_entry.ledger_entry_id + 1_000_000,),
    )
    mutated = replace(
        baseline.left_distribution,
        trials=(clone,) + baseline.left_distribution.trials[1:],
    )
    checks = trial_inventory_checks(mutated, baseline.ctx)
    return (
        clone.trial_id == original.trial_id
        and clone not in baseline.ctx.eligible_route_endpoint_trials
        and not checks["everyEligibleTrialCovered"]
        and not checks["everyTrialEligible"]
    )


def _perturbation_clone_rejected_discipline(fixture: Fixture) -> bool:
    baseline = fixture.claims["claim_coherent_wheel"]
    original = baseline.perturbation_inventory.records[0]
    if not isinstance(original, PerturbationTrialRecord):
        return False
    clone = replace(original, magnitude=original.magnitude + F(1, 8))
    mutated = replace(
        baseline,
        perturbation_inventory=Inventory(
            (clone,) + baseline.perturbation_inventory.records[1:],
            baseline.perturbation_inventory.eligible_records,
        ),
    )
    checks = complete_perturbation_inventory_checks(mutated)
    return (
        clone.trial_id == original.trial_id
        and clone not in baseline.ctx.eligible_perturbation_trials
        and checks["eligibleUniverseMatchesContext"]
        and not checks["everyEligibleCovered"]
        and not checks["everyRecordEligible"]
    )


def _flat_cross_witness_differential_discipline(fixture: Fixture) -> bool:
    data = fixture.controls["ctrl_flat_unrelated_pair_rejected"]
    evaluations = declared_flat_pair_evaluations(data)
    pair_local = any(
        matches_claim and no_difference
        for _, _, matches_claim, no_difference in evaluations
    )
    cross_mixed = (
        any(matches_claim for _, _, matches_claim, _ in evaluations)
        and any(no_difference for _, _, _, no_difference in evaluations)
    )
    return (
        len(evaluations) == 2
        and cross_mixed
        and not pair_local
        and not flat_second_arm_evidence(data)
        and not flat_evidence_for(data)
    )


def run_e16_adaptability_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = _status_rows(fixture)
    comparisons = _comparisons(fixture, rows)
    return SweepResults(
        rows,
        comparisons,
        _actual_scope_discipline(fixture, rows),
        _no_hardcoded_status_discipline(rows, comparisons),
        _off_inventory_isolation_discipline(fixture),
        _predictive_reveal_isolation_discipline(fixture),
        _administrative_without_candidate_discipline(fixture),
        _wrong_claim_bridge_isolation_discipline(fixture),
        _route_trial_clone_rejected_discipline(fixture),
        _perturbation_clone_rejected_discipline(fixture),
        _flat_cross_witness_differential_discipline(fixture),
    )


def format_results_markdown(results: SweepResults) -> str:
    failures = tuple(comparison for comparison in results.comparisons if not comparison.passed)
    lines = [
        "# E16 Adaptability Sweep Results", "",
        f"Overall verdict: {'PASS' if not failures else 'FAIL'}",
        f"Registered comparisons: {len(results.comparisons)}", "",
        "## Registered Prediction Comparisons", "",
        "| comparison | verdict | observed | expected |",
        "| --- | --- | --- | --- |",
    ]
    for comparison in results.comparisons:
        lines.append(
            f"| {comparison.name} | {'PASS' if comparison.passed else 'FAIL'} | "
            f"`{comparison.observed}` | `{comparison.expected}` |"
        )
    lines.extend((
        "", "## Discipline Checks", "",
        f"- Actual scope discipline: `{results.actual_scope_discipline}`",
        f"- No hardcoded status discipline: `{results.no_hardcoded_status_discipline}`",
        f"- Off-inventory dissipation isolation: `{results.off_inventory_isolation_discipline}`",
        f"- Predictive-reveal isolation: `{results.predictive_reveal_isolation_discipline}`",
        f"- Administrative rejection without candidate evidence: `{results.administrative_without_candidate_discipline}`",
        f"- Wrong-claim E15 bridge isolation: `{results.wrong_claim_bridge_isolation_discipline}`",
        f"- Same-ID changed-content route trial rejected: `{results.route_trial_clone_rejected_discipline}`",
        f"- Same-ID changed-magnitude perturbation trial rejected: `{results.perturbation_clone_rejected_discipline}`",
        f"- Flat cross-witness differential: `{results.flat_cross_witness_differential_discipline}`", "",
    ))
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_e16_adaptability_sweep()
    path.write_text(format_results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    passed = sum(comparison.passed for comparison in results.comparisons)
    total = len(results.comparisons)
    print(f"E16 adaptability sweep: {passed}/{total} comparisons PASS")
    for comparison in results.comparisons:
        verdict = "PASS" if comparison.passed else "FAIL"
        print(f"{verdict}: {comparison.name}: observed={comparison.observed} expected={comparison.expected}")


if __name__ == "__main__":
    main()
