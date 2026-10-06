"""E14 reconsolidation sweep against the committed Round A predictions.

The fixture in ``E14_reconsolidation_predictions.md`` is mirrored here as a
finite, single-carrier Repair-World instance.  Statuses are produced only by
the claim-scoped nine-case priority chain after evaluating carried records,
literal ``Delta``, direct F9 record references, D1 refinement, D4 repair
actions, exact ledger charges, and provenance links.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Callable

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
from sixbirds_foundations_v.probe_economy import ActiveFamily, ProbeCatalog, ProbeEconomy
from sixbirds_foundations_v.repair_join import Refines, repair_join
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


F = Fraction
ITEMS = ("a", "b", "c", "d")

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E14_reconsolidation_results.md"
)

REGISTERED_COMPARISON_ORDER = (
    "claim_record_repaired.status",
    "claim_record_coarsened.status",
    "claim_statused_unresolved.status",
    "claim_outcome_collision.status",
    "claim_unrealized_direct_reference.status",
    "claim_silent_rewrite.status",
    "claim_provenance_defect.status",
    "claim_ordinary_read.status",
    "claim_unstatused_conflict.status",
    "ctrl_transport_single_valued_same_context",
    "ctrl_coarsening_audited_pair_mismatch.status",
    "ctrl_unresolved_provenance_root_mismatch.status",
    "ctrl_no_conflict_after_transport",
    "ctrl_conflict_for_other_claim",
    "ctrl_non_strict_coarsening.status",
    "ctrl_wrong_direction_refinement.status",
    "ctrl_uncarried_post_retrieval_record.status",
    "ctrl_ledger_charge_label_only.status",
    "ctrl_per_retrieval_claim_scoping",
    "ctrl_unrelated_mutation_evidence.status",
    "strata_budget_memory_fate_direction",
)


class RecordMutationKind(str, Enum):
    repair = "repair"
    coarsening = "coarsening"


class ReconsolidationDisposition(str, Enum):
    record_repair = "record_repair"
    record_coarsening = "record_coarsening"
    statused_unresolved = "statused_unresolved"


class ReconsolidationStatus(str, Enum):
    provenance_defect = "provenance_defect"
    silent_rewrite = "silent_rewrite"
    ordinary_read = "ordinary_read"
    outcome_collision = "outcome_collision"
    unrealized_disposition = "unrealized_disposition"
    record_repaired = "record_repaired"
    record_coarsened = "record_coarsened"
    statused_unresolved = "statused_unresolved"
    unstatused_conflict = "unstatused_conflict"
    unclassified = "unclassified"


@dataclass(frozen=True)
class CarriedFact:
    n0: int = 0
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True
    present: bool = True


CARRIED = CarriedFact()


@dataclass(frozen=True)
class MemoryClaimRecord:
    name: str
    claim_id: int
    demand: tuple[int, int, int, int]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RetrievalContextRecord:
    name: str
    context_id: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class DeclaredRetrievalContextFamily:
    name: str
    family_id: int
    contexts: tuple[RetrievalContextRecord, ...]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class CarriedMemoryRecord:
    name: str
    record_id: int
    version: int
    claim_record: MemoryClaimRecord
    record_value: tuple[frozenset[str], ...]
    provenance_root_id: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class MemoryRecordFormationRecord:
    name: str
    formation_id: int
    memory_record: CarriedMemoryRecord
    formed_at: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RecordQuotientRecord:
    name: str
    quotient_id: int
    quotient: tuple[str, str, str, str]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RetrievalTransportRecord:
    name: str
    transport_id: int
    source_record: CarriedMemoryRecord
    context_record: RetrievalContextRecord
    current_quotient: RecordQuotientRecord
    transported_record: tuple[str, str, str, str]
    retrieved_at: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class CompleteRetrievalTransportInventory:
    name: str
    source_record: CarriedMemoryRecord
    family: DeclaredRetrievalContextFamily
    declared_transports: tuple[RetrievalTransportRecord, ...]


@dataclass(frozen=True)
class RetrievalConflictRecord:
    name: str
    conflict_id: int
    source_record: CarriedMemoryRecord
    transport_record: RetrievalTransportRecord
    claim_record: MemoryClaimRecord
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ReconsolidationTrigger:
    name: str
    source_record: CarriedMemoryRecord
    family: DeclaredRetrievalContextFamily
    inventory: CompleteRetrievalTransportInventory
    conflict_record: RetrievalConflictRecord


@dataclass(frozen=True)
class RecordRepairPackage:
    name: str
    repair_id: int
    context_record: RetrievalContextRecord
    repair_value: tuple[frozenset[str], ...]
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class RecordMutationRecord:
    name: str
    mutation_id: int
    before_record: CarriedMemoryRecord
    after_record: CarriedMemoryRecord
    retrieval_transport_id: int
    context_record: RetrievalContextRecord
    mutation_kind: RecordMutationKind
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class DistinctionSupportAuditRecord:
    name: str
    audit_id: int
    before_quotient: RecordQuotientRecord
    after_quotient: RecordQuotientRecord
    claim_id: int
    merged_left: str
    merged_right: str
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class MutationProvenanceRecord:
    name: str
    provenance_id: int
    mutation_record: RecordMutationRecord
    declared_parent: CarriedMemoryRecord
    declared_derived_record: CarriedMemoryRecord
    declared_root_id: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ProvenanceAuditRecord:
    name: str
    audit_id: int
    before_record: CarriedMemoryRecord
    after_record: CarriedMemoryRecord
    retrieval_transport_id: int
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ReconsolidationResidualRecord:
    name: str
    residual_id: int
    conflict_record: RetrievalConflictRecord
    residual_amount: Fraction
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class LedgerEntry:
    name: str
    residual_id: int
    amount: Fraction
    label: str = "reconsolidation-residual"
    charged_metadata: bool = False
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class ReconsolidationDispositionRecord:
    name: str
    disposition_id: int
    conflict_record: RetrievalConflictRecord
    disposition: ReconsolidationDisposition
    supporting_mutation: RecordMutationRecord | None
    supporting_residual: ReconsolidationResidualRecord | None
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class CompleteReconsolidationDispositionInventory:
    name: str
    conflict_record: RetrievalConflictRecord
    declared_dispositions: tuple[ReconsolidationDispositionRecord, ...]


@dataclass(frozen=True)
class RecordRepairCandidate:
    name: str
    trigger: ReconsolidationTrigger
    repair_package: RecordRepairPackage
    after_record: CarriedMemoryRecord
    formation_record: MemoryRecordFormationRecord
    mutation_record: RecordMutationRecord
    provenance_record: MutationProvenanceRecord
    z_before: int
    action: RepairAction[str, frozenset[str], str, str]


@dataclass(frozen=True)
class RecordCoarseningCandidate:
    name: str
    trigger: ReconsolidationTrigger
    after_record: CarriedMemoryRecord
    formation_record: MemoryRecordFormationRecord
    before_quotient: RecordQuotientRecord
    after_quotient: RecordQuotientRecord
    support_audit: DistinctionSupportAuditRecord
    mutation_record: RecordMutationRecord
    provenance_record: MutationProvenanceRecord
    z_before: int
    action: RepairAction[str, str, str, str]


@dataclass(frozen=True)
class StatusedUnresolvedCandidate:
    name: str
    trigger: ReconsolidationTrigger
    current_record_at_status: CarriedMemoryRecord
    formation_record: MemoryRecordFormationRecord
    residual_record: ReconsolidationResidualRecord
    ledger_entry: LedgerEntry


@dataclass(frozen=True)
class CompleteReconsolidationOutcomeInventory:
    name: str
    trigger: ReconsolidationTrigger
    repair_mutation_records: tuple[RecordMutationRecord, ...]
    coarsening_mutation_records: tuple[RecordMutationRecord, ...]
    unresolved_residual_records: tuple[ReconsolidationResidualRecord, ...]


@dataclass(frozen=True)
class SilentRewriteCandidate:
    name: str
    trigger: ReconsolidationTrigger
    after_record: CarriedMemoryRecord
    formation_record: MemoryRecordFormationRecord
    audit_record: ProvenanceAuditRecord
    disposition_inventory: CompleteReconsolidationDispositionInventory
    outcome_inventory: CompleteReconsolidationOutcomeInventory


@dataclass(frozen=True)
class LaunderedProvenanceCandidate:
    name: str
    trigger: ReconsolidationTrigger
    after_record: CarriedMemoryRecord
    formation_record: MemoryRecordFormationRecord
    mutation_record: RecordMutationRecord
    provenance_record: MutationProvenanceRecord
    audit_record: ProvenanceAuditRecord


@dataclass(frozen=True)
class ReconsolidationClaimRef:
    name: str
    source_record: CarriedMemoryRecord
    family: DeclaredRetrievalContextFamily
    transport_record: RetrievalTransportRecord
    context_record: RetrievalContextRecord
    claim_record: MemoryClaimRecord


@dataclass(frozen=True)
class ReconsolidationStatusRecord:
    name: str
    status_record_id: int
    status: ReconsolidationStatus
    source_record: CarriedMemoryRecord
    family: DeclaredRetrievalContextFamily
    transport_record: RetrievalTransportRecord
    context_record: RetrievalContextRecord
    claim_record: MemoryClaimRecord
    conflict_record: RetrievalConflictRecord | None = None
    mutation_record: RecordMutationRecord | None = None
    residual_record: ReconsolidationResidualRecord | None = None
    disposition_record: ReconsolidationDispositionRecord | None = None
    provenance_audit_record: ProvenanceAuditRecord | None = None
    carried: CarriedFact = CARRIED


@dataclass(frozen=True)
class BudgetMetadata:
    exposure_budget: Fraction
    exposure_spend: Fraction
    residual_budget: Fraction
    residual_demand: Fraction


@dataclass(frozen=True)
class StratumEpisode:
    name: str
    claim_name: str
    budget: BudgetMetadata


@dataclass(frozen=True)
class RepairWorldCarrier:
    items: tuple[str, ...]
    config: RepairWorldConfig
    state: RepairWorldState
    lambda_entries: tuple[LedgerEntry, ...]


@dataclass(frozen=True)
class ReconsolidationClassifierContext:
    """One shared comparator bundle, corresponding to Lean's context."""

    def f20_record_formed(
        self, fixture: Fixture, formation: MemoryRecordFormationRecord
    ) -> bool:
        return (
            _record_carried(formation)
            and fixture.formation_registry.get(formation.formation_id) == formation.memory_record
        )

    def retrieval_declared(
        self, fixture: Fixture, transport: RetrievalTransportRecord
    ) -> bool:
        return (
            _record_carried(transport)
            and _f20_record_is_carried(fixture, transport.source_record)
            and fixture.transport_registry.get(transport.transport_id) == transport
            and sum(
                candidate.transport_id == transport.transport_id
                for candidate in fixture.transport_registry.values()
            )
            == 1
        )

    def repair_move_installs_join(
        self,
        action: RepairAction[str, frozenset[str], str, str],
        package: RecordRepairPackage,
        before: CarriedMemoryRecord,
        after: CarriedMemoryRecord,
    ) -> bool:
        payload = tuple(action.repair_package[item] for item in ITEMS)
        return payload == package.repair_value and all(
            after.record_value[index]
            == before.record_value[index] | package.repair_value[index]
            for index in range(len(ITEMS))
        )

    def record_uses_quotient(
        self, fixture: Fixture, record: CarriedMemoryRecord, quotient: RecordQuotientRecord
    ) -> bool:
        return (record.name, quotient.name) in fixture.record_quotient_links

    def coarsening_move_installs_record(
        self,
        fixture: Fixture,
        candidate: RecordCoarseningCandidate,
    ) -> bool:
        key = (
            candidate.action.defect,
            candidate.trigger.source_record.name,
            candidate.after_record.name,
            candidate.before_quotient.name,
            candidate.after_quotient.name,
        )
        return key in fixture.coarsening_install_registry

    def distinction_no_longer_supportable(
        self,
        fixture: Fixture,
        audit: DistinctionSupportAuditRecord,
        claim: MemoryClaimRecord,
    ) -> bool:
        pair = frozenset((audit.merged_left, audit.merged_right))
        return (
            audit.claim_id == claim.claim_id
            and pair in fixture.unsupported_pairs.get(audit.audit_id, frozenset())
        )

    def f9_classifies_native_conflict(
        self,
        fixture: Fixture,
        conflict: RetrievalConflictRecord,
        disposition: ReconsolidationDispositionRecord,
    ) -> bool:
        return (
            disposition.conflict_record == conflict
            and fixture.f9_registry.get(conflict.conflict_id) == disposition.disposition_id
        )

    def ledger_entry_charges_residual(
        self,
        entry: LedgerEntry,
        residual: ReconsolidationResidualRecord,
        amount: Fraction,
    ) -> bool:
        return (
            entry.residual_id == residual.residual_id
            and entry.amount == amount
            and amount > 0
        )

    def provenance_matches_mutation(
        self, provenance: MutationProvenanceRecord
    ) -> bool:
        mutation = provenance.mutation_record
        return (
            provenance.declared_parent == mutation.before_record
            and provenance.declared_derived_record == mutation.after_record
            and provenance.declared_root_id == mutation.before_record.provenance_root_id
            and mutation.after_record.provenance_root_id
            == mutation.before_record.provenance_root_id
        )


@dataclass(frozen=True)
class Fixture:
    carrier: RepairWorldCarrier
    ctx: ReconsolidationClassifierContext
    claims: dict[str, MemoryClaimRecord]
    memory_records: dict[str, CarriedMemoryRecord]
    formations: dict[str, MemoryRecordFormationRecord]
    quotients: dict[str, RecordQuotientRecord]
    contexts: dict[str, RetrievalContextRecord]
    families: dict[str, DeclaredRetrievalContextFamily]
    transports: dict[str, RetrievalTransportRecord]
    retrieval_inventories: dict[str, CompleteRetrievalTransportInventory]
    conflicts: dict[str, RetrievalConflictRecord]
    triggers: dict[str, ReconsolidationTrigger]
    repair_packages: dict[str, RecordRepairPackage]
    mutations: dict[str, RecordMutationRecord]
    distinction_audits: dict[str, DistinctionSupportAuditRecord]
    provenances: dict[str, MutationProvenanceRecord]
    provenance_audits: dict[str, ProvenanceAuditRecord]
    residuals: dict[str, ReconsolidationResidualRecord]
    ledger_entries: dict[str, LedgerEntry]
    dispositions: dict[str, ReconsolidationDispositionRecord]
    disposition_inventories: dict[str, CompleteReconsolidationDispositionInventory]
    repair_candidates: dict[str, RecordRepairCandidate]
    coarsening_candidates: dict[str, RecordCoarseningCandidate]
    unresolved_candidates: dict[str, StatusedUnresolvedCandidate]
    outcome_inventories: dict[str, CompleteReconsolidationOutcomeInventory]
    silent_candidates: dict[str, SilentRewriteCandidate]
    provenance_defect_candidates: dict[str, LaunderedProvenanceCandidate]
    reconsolidation_claims: dict[str, ReconsolidationClaimRef]
    status_records: dict[str, ReconsolidationStatusRecord]
    formation_registry: dict[int, CarriedMemoryRecord]
    transport_registry: dict[int, RetrievalTransportRecord]
    record_quotient_links: frozenset[tuple[str, str]]
    unsupported_pairs: dict[int, frozenset[frozenset[str]]]
    f9_registry: dict[int, int]
    coarsening_install_registry: frozenset[tuple[str, str, str, str, str]]
    strata: tuple[StratumEpisode, ...]


@dataclass(frozen=True)
class StatusRow:
    name: str
    expected: ReconsolidationStatus
    observed: ReconsolidationStatus
    truths: dict[ReconsolidationStatus, bool]
    status_record: ReconsolidationStatusRecord | None

    @property
    def passed(self) -> bool:
        return self.observed is self.expected


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
    return isinstance(fact, CarriedFact) and fact.present and carried_source(
        fact.source_tag, fact.generated_by_s, fact.in_scope
    )


def _f20_record_is_carried(fixture: Fixture, memory: CarriedMemoryRecord) -> bool:
    return any(
        formation.memory_record == memory
        and _record_carried(memory)
        and _record_carried(memory.claim_record)
        and _record_carried(formation)
        and fixture.ctx.f20_record_formed(fixture, formation)
        for formation in fixture.formations.values()
    )


def _at(values: tuple[object, ...], item: str) -> object:
    return values[ITEMS.index(item)]


def _function(values: tuple[object, ...]) -> Callable[[str], object]:
    return lambda item: _at(values, item)


def declared_retrieval_context_family(family: DeclaredRetrievalContextFamily) -> bool:
    return len(family.contexts) >= 2 and len(set(family.contexts)) == len(family.contexts) and _record_carried(family)


def declared_retrieval_transport(
    fixture: Fixture,
    source_record: CarriedMemoryRecord,
    family: DeclaredRetrievalContextFamily,
    transport: RetrievalTransportRecord,
) -> bool:
    return (
        transport.source_record == source_record
        and transport.context_record in family.contexts
        and _f20_record_is_carried(fixture, source_record)
        and _record_carried(transport.context_record)
        and declared_retrieval_context_family(family)
        and fixture.ctx.retrieval_declared(fixture, transport)
    )


def retrieval_inventory_checks(
    fixture: Fixture, inventory: CompleteRetrievalTransportInventory
) -> dict[str, bool]:
    declared = inventory.declared_transports
    eligible = tuple(
        transport
        for transport in fixture.transports.values()
        if declared_retrieval_transport(
            fixture, inventory.source_record, inventory.family, transport
        )
    )
    complete = all(transport in declared for transport in eligible)
    sound = all(
        declared_retrieval_transport(
            fixture, inventory.source_record, inventory.family, transport
        )
        for transport in declared
    )
    covered = all(
        any(transport.context_record == context for transport in declared)
        for context in inventory.family.contexts
    )
    single_valued = all(
        first.context_record != second.context_record
        or first.transported_record == second.transported_record
        for first in declared
        for second in declared
    )
    return {
        "completeForClaim": complete,
        "soundForClaim": sound,
        "everyContextCovered": covered,
        "transportSingleValuedPerContext": single_valued,
    }


def complete_retrieval_transport_inventory(
    fixture: Fixture, inventory: CompleteRetrievalTransportInventory
) -> bool:
    return all(retrieval_inventory_checks(fixture, inventory).values())


def context_dependent_retrieval(
    fixture: Fixture, inventory: CompleteRetrievalTransportInventory
) -> bool:
    return complete_retrieval_transport_inventory(fixture, inventory) and any(
        first.context_record != second.context_record
        and first.transported_record != second.transported_record
        for first in inventory.declared_transports
        for second in inventory.declared_transports
    )


def retrieval_without_transport_evidence(
    fixture: Fixture, inventory: CompleteRetrievalTransportInventory
) -> bool:
    return complete_retrieval_transport_inventory(fixture, inventory) and all(
        first.transported_record == second.transported_record
        for first in inventory.declared_transports
        for second in inventory.declared_transports
    )


def delta_set(
    transport: RetrievalTransportRecord, claim: MemoryClaimRecord
) -> frozenset[frozenset[str]]:
    joined = repair_join(
        _function(transport.current_quotient.quotient),
        _function(transport.transported_record),
    )
    return frozenset(
        frozenset((left, right))
        for left, right in combinations(ITEMS, 2)
        if joined(left) == joined(right)
        and _at(claim.demand, left) != _at(claim.demand, right)
    )


def retrieval_conflict_evidence(
    fixture: Fixture,
    source_record: CarriedMemoryRecord,
    family: DeclaredRetrievalContextFamily,
    conflict: RetrievalConflictRecord,
) -> bool:
    return (
        declared_retrieval_transport(
            fixture, source_record, family, conflict.transport_record
        )
        and conflict.source_record == source_record
        and conflict.claim_record == source_record.claim_record
        and _record_carried(conflict)
        and bool(delta_set(conflict.transport_record, source_record.claim_record))
    )


def reconsolidation_trigger(fixture: Fixture, trigger: ReconsolidationTrigger) -> bool:
    return (
        trigger.inventory.source_record == trigger.source_record
        and trigger.inventory.family == trigger.family
        and complete_retrieval_transport_inventory(fixture, trigger.inventory)
        and context_dependent_retrieval(fixture, trigger.inventory)
        and retrieval_conflict_evidence(
            fixture, trigger.source_record, trigger.family, trigger.conflict_record
        )
        and trigger.conflict_record.transport_record
        in trigger.inventory.declared_transports
    )


def disposition_inventory_checks(
    fixture: Fixture, inventory: CompleteReconsolidationDispositionInventory
) -> dict[str, bool]:
    eligible = tuple(
        disposition
        for disposition in fixture.dispositions.values()
        if disposition.conflict_record == inventory.conflict_record
        and fixture.ctx.f9_classifies_native_conflict(
            fixture, inventory.conflict_record, disposition
        )
        and _record_carried(disposition)
    )
    return {
        "completeForConflict": all(
            disposition in inventory.declared_dispositions for disposition in eligible
        ),
        "soundForConflict": all(
            disposition.conflict_record == inventory.conflict_record
            and fixture.ctx.f9_classifies_native_conflict(
                fixture, inventory.conflict_record, disposition
            )
            and _record_carried(disposition)
            for disposition in inventory.declared_dispositions
        ),
        "statusSingleValued": len(
            {disposition.disposition for disposition in inventory.declared_dispositions}
        )
        <= 1,
    }


def complete_disposition_inventory(
    fixture: Fixture, inventory: CompleteReconsolidationDispositionInventory
) -> bool:
    return all(disposition_inventory_checks(fixture, inventory).values())


def f9_reconsolidation_coverage_certified(
    fixture: Fixture, inventory: CompleteReconsolidationDispositionInventory
) -> ReconsolidationDispositionRecord | None:
    if not complete_disposition_inventory(fixture, inventory):
        return None
    return inventory.declared_dispositions[0] if inventory.declared_dispositions else None


def no_f9_disposition_for(
    fixture: Fixture, inventory: CompleteReconsolidationDispositionInventory
) -> bool:
    return complete_disposition_inventory(fixture, inventory) and not inventory.declared_dispositions


def _repair_action_carried(action: RepairAction[object, object, object, object]) -> bool:
    return carried_source(
        action.defect_evidence.source_tag,
        action.defect_evidence.generated_by_s,
        action.defect_evidence.in_scope,
    ) and carried_source(
        action.audit_record_evidence.source_tag,
        action.audit_record_evidence.generated_by_s,
        action.audit_record_evidence.in_scope,
    )


def record_repair_evidence(fixture: Fixture, candidate: RecordRepairCandidate) -> bool:
    trigger = candidate.trigger
    mutation = candidate.mutation_record
    provenance = candidate.provenance_record
    source = trigger.source_record
    return (
        reconsolidation_trigger(fixture, trigger)
        and _record_carried(candidate.repair_package)
        and _f20_record_is_carried(fixture, candidate.after_record)
        and candidate.formation_record.memory_record == candidate.after_record
        and _record_carried(mutation)
        and _record_carried(provenance)
        and mutation.before_record == source
        and mutation.after_record == candidate.after_record
        and mutation.retrieval_transport_id == trigger.conflict_record.transport_record.transport_id
        and mutation.context_record == trigger.conflict_record.transport_record.context_record
        and mutation.mutation_kind is RecordMutationKind.repair
        and provenance.mutation_record == mutation
        and provenance.declared_parent == source
        and provenance.declared_derived_record == candidate.after_record
        and fixture.ctx.provenance_matches_mutation(provenance)
        and candidate.after_record.record_id == source.record_id
        and candidate.after_record.claim_record == source.claim_record
        and candidate.after_record.version == source.version + 1
        and _repair_action_carried(candidate.action)
        and fixture.carrier.state.y == candidate.z_before
        and is_lawful_action(
            fixture.carrier.config, fixture.carrier.state, candidate.action
        ).is_lawful
        and fixture.ctx.repair_move_installs_join(
            candidate.action, candidate.repair_package, source, candidate.after_record
        )
        and candidate.repair_package.context_record
        == trigger.conflict_record.transport_record.context_record
    )


def record_coarsening_evidence(
    fixture: Fixture, candidate: RecordCoarseningCandidate
) -> bool:
    trigger = candidate.trigger
    mutation = candidate.mutation_record
    provenance = candidate.provenance_record
    audit = candidate.support_audit
    source = trigger.source_record
    before = candidate.before_quotient
    after = candidate.after_quotient
    return (
        reconsolidation_trigger(fixture, trigger)
        and _f20_record_is_carried(fixture, candidate.after_record)
        and candidate.formation_record.memory_record == candidate.after_record
        and _record_carried(before)
        and _record_carried(after)
        and _record_carried(audit)
        and _record_carried(mutation)
        and _record_carried(provenance)
        and fixture.ctx.record_uses_quotient(fixture, source, before)
        and fixture.ctx.record_uses_quotient(fixture, candidate.after_record, after)
        and audit.before_quotient == before
        and audit.after_quotient == after
        and audit.claim_id == source.claim_record.claim_id
        and Refines(_function(before.quotient), _function(after.quotient), ITEMS)
        and _at(after.quotient, audit.merged_left)
        == _at(after.quotient, audit.merged_right)
        and _at(before.quotient, audit.merged_left)
        != _at(before.quotient, audit.merged_right)
        and fixture.ctx.distinction_no_longer_supportable(
            fixture, audit, source.claim_record
        )
        and mutation.before_record == source
        and mutation.after_record == candidate.after_record
        and mutation.retrieval_transport_id == trigger.conflict_record.transport_record.transport_id
        and mutation.context_record == trigger.conflict_record.transport_record.context_record
        and mutation.mutation_kind is RecordMutationKind.coarsening
        and provenance.mutation_record == mutation
        and provenance.declared_parent == source
        and provenance.declared_derived_record == candidate.after_record
        and fixture.ctx.provenance_matches_mutation(provenance)
        and candidate.after_record.record_id == source.record_id
        and candidate.after_record.claim_record == source.claim_record
        and candidate.after_record.version == source.version + 1
        and _repair_action_carried(candidate.action)
        and fixture.carrier.state.y == candidate.z_before
        and is_lawful_action(
            fixture.carrier.config, fixture.carrier.state, candidate.action
        ).is_lawful
        and fixture.ctx.coarsening_move_installs_record(fixture, candidate)
    )


def statused_unresolved_evidence(
    fixture: Fixture, candidate: StatusedUnresolvedCandidate
) -> bool:
    trigger = candidate.trigger
    current = candidate.current_record_at_status
    source = trigger.source_record
    residual = candidate.residual_record
    entry = candidate.ledger_entry
    return (
        reconsolidation_trigger(fixture, trigger)
        and _f20_record_is_carried(fixture, current)
        and candidate.formation_record.memory_record == current
        and current.record_id == source.record_id
        and current.claim_record == source.claim_record
        and current.version == source.version
        and current.provenance_root_id == source.provenance_root_id
        and current.record_value == source.record_value
        and _record_carried(residual)
        and residual.conflict_record == trigger.conflict_record
        and residual.residual_amount > 0
        and entry in fixture.carrier.lambda_entries
        and _record_carried(entry)
        and fixture.ctx.ledger_entry_charges_residual(
            entry, residual, residual.residual_amount
        )
    )


def outcome_inventory_checks(
    fixture: Fixture, inventory: CompleteReconsolidationOutcomeInventory
) -> dict[str, bool]:
    valid_repairs = tuple(
        candidate.mutation_record
        for candidate in fixture.repair_candidates.values()
        if candidate.trigger == inventory.trigger and record_repair_evidence(fixture, candidate)
    )
    valid_coarsenings = tuple(
        candidate.mutation_record
        for candidate in fixture.coarsening_candidates.values()
        if candidate.trigger == inventory.trigger and record_coarsening_evidence(fixture, candidate)
    )
    valid_unresolved = tuple(
        candidate.residual_record
        for candidate in fixture.unresolved_candidates.values()
        if candidate.trigger == inventory.trigger and statused_unresolved_evidence(fixture, candidate)
    )
    return {
        "completeRepairs": all(
            record in inventory.repair_mutation_records for record in valid_repairs
        ),
        "completeCoarsenings": all(
            record in inventory.coarsening_mutation_records for record in valid_coarsenings
        ),
        "completeUnresolved": all(
            record in inventory.unresolved_residual_records for record in valid_unresolved
        ),
        "soundRepairs": all(record in valid_repairs for record in inventory.repair_mutation_records),
        "soundCoarsenings": all(
            record in valid_coarsenings for record in inventory.coarsening_mutation_records
        ),
        "soundUnresolved": all(
            record in valid_unresolved for record in inventory.unresolved_residual_records
        ),
    }


def complete_outcome_inventory(
    fixture: Fixture, inventory: CompleteReconsolidationOutcomeInventory
) -> bool:
    return reconsolidation_trigger(fixture, inventory.trigger) and all(
        outcome_inventory_checks(fixture, inventory).values()
    )


def no_reconsolidation_outcome_for(
    fixture: Fixture, inventory: CompleteReconsolidationOutcomeInventory
) -> bool:
    return complete_outcome_inventory(fixture, inventory) and not (
        inventory.repair_mutation_records
        or inventory.coarsening_mutation_records
        or inventory.unresolved_residual_records
    )


def disposition_realized_by_inventory(
    fixture: Fixture,
    disposition_inventory: CompleteReconsolidationDispositionInventory,
    outcome_inventory: CompleteReconsolidationOutcomeInventory,
) -> bool:
    coverage = f9_reconsolidation_coverage_certified(fixture, disposition_inventory)
    if coverage is None or not complete_outcome_inventory(fixture, outcome_inventory):
        return False
    if coverage.disposition is ReconsolidationDisposition.record_repair:
        return (
            coverage.supporting_residual is None
            and coverage.supporting_mutation in outcome_inventory.repair_mutation_records
        )
    if coverage.disposition is ReconsolidationDisposition.record_coarsening:
        return (
            coverage.supporting_residual is None
            and coverage.supporting_mutation in outcome_inventory.coarsening_mutation_records
        )
    return (
        coverage.supporting_mutation is None
        and coverage.supporting_residual in outcome_inventory.unresolved_residual_records
    )


def reconsolidation_outcome_collision(fixture: Fixture, trigger: ReconsolidationTrigger) -> bool:
    repairs = any(
        candidate.trigger == trigger and record_repair_evidence(fixture, candidate)
        for candidate in fixture.repair_candidates.values()
    )
    coarsenings = any(
        candidate.trigger == trigger and record_coarsening_evidence(fixture, candidate)
        for candidate in fixture.coarsening_candidates.values()
    )
    unresolved = any(
        candidate.trigger == trigger and statused_unresolved_evidence(fixture, candidate)
        for candidate in fixture.unresolved_candidates.values()
    )
    return sum((repairs, coarsenings, unresolved)) >= 2


def complete_mutation_provenance_inventory(
    fixture: Fixture,
    before: CarriedMemoryRecord,
    after: CarriedMemoryRecord,
    transport_id: int,
    declared: tuple[MutationProvenanceRecord, ...],
) -> bool:
    eligible = tuple(
        provenance
        for provenance in fixture.provenances.values()
        if provenance.mutation_record.before_record == before
        and provenance.mutation_record.after_record == after
        and provenance.mutation_record.retrieval_transport_id == transport_id
        and _record_carried(provenance)
    )
    return all(provenance in declared for provenance in eligible)


def silent_rewrite_evidence(fixture: Fixture, candidate: SilentRewriteCandidate) -> bool:
    source = candidate.trigger.source_record
    transport_id = candidate.trigger.conflict_record.transport_record.transport_id
    declared: tuple[MutationProvenanceRecord, ...] = ()
    return (
        reconsolidation_trigger(fixture, candidate.trigger)
        and complete_disposition_inventory(fixture, candidate.disposition_inventory)
        and complete_outcome_inventory(fixture, candidate.outcome_inventory)
        and _f20_record_is_carried(fixture, candidate.after_record)
        and candidate.formation_record.memory_record == candidate.after_record
        and _record_carried(candidate.audit_record)
        and candidate.audit_record.before_record == source
        and candidate.audit_record.after_record == candidate.after_record
        and candidate.audit_record.retrieval_transport_id == transport_id
        and source.record_value != candidate.after_record.record_value
        and candidate.after_record.record_id == source.record_id
        and candidate.after_record.claim_record == source.claim_record
        and no_reconsolidation_outcome_for(fixture, candidate.outcome_inventory)
        and no_f9_disposition_for(fixture, candidate.disposition_inventory)
        and complete_mutation_provenance_inventory(
            fixture, source, candidate.after_record, transport_id, declared
        )
        and not declared
    )


def laundered_provenance_defect(
    fixture: Fixture, candidate: LaunderedProvenanceCandidate
) -> bool:
    source = candidate.trigger.source_record
    transport_id = candidate.trigger.conflict_record.transport_record.transport_id
    mutation = candidate.mutation_record
    return (
        reconsolidation_trigger(fixture, candidate.trigger)
        and _f20_record_is_carried(fixture, candidate.after_record)
        and candidate.formation_record.memory_record == candidate.after_record
        and _record_carried(mutation)
        and _record_carried(candidate.provenance_record)
        and _record_carried(candidate.audit_record)
        and mutation.before_record == source
        and mutation.after_record == candidate.after_record
        and mutation.retrieval_transport_id == transport_id
        and candidate.audit_record.before_record == source
        and candidate.audit_record.after_record == candidate.after_record
        and candidate.audit_record.retrieval_transport_id == transport_id
        and source.record_value != candidate.after_record.record_value
        and candidate.after_record.record_id == source.record_id
        and candidate.after_record.claim_record == source.claim_record
        and candidate.provenance_record.mutation_record == mutation
        and not fixture.ctx.provenance_matches_mutation(candidate.provenance_record)
    )


def reconsolidation_status_record_matches_claim(
    claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord
) -> bool:
    return (
        record.source_record == claim.source_record
        and record.family == claim.family
        and record.transport_record == claim.transport_record
        and record.context_record == claim.context_record
        and record.claim_record == claim.claim_record
        and claim.transport_record.source_record == claim.source_record
        and claim.transport_record.context_record == claim.context_record
        and claim.context_record in claim.family.contexts
        and claim.source_record.claim_record == claim.claim_record
    )


def reconsolidation_status_occurrence_for(
    claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord
) -> bool:
    return reconsolidation_status_record_matches_claim(claim, record) and _record_carried(record)


STATUS_PRIORITY = (
    ReconsolidationStatus.provenance_defect,
    ReconsolidationStatus.silent_rewrite,
    ReconsolidationStatus.ordinary_read,
    ReconsolidationStatus.outcome_collision,
    ReconsolidationStatus.unrealized_disposition,
    ReconsolidationStatus.record_repaired,
    ReconsolidationStatus.record_coarsened,
    ReconsolidationStatus.statused_unresolved,
    ReconsolidationStatus.unstatused_conflict,
)


def _matching_triggers(
    fixture: Fixture, claim: ReconsolidationClaimRef
) -> tuple[ReconsolidationTrigger, ...]:
    return tuple(
        trigger
        for trigger in fixture.triggers.values()
        if trigger.source_record == claim.source_record
        and trigger.family == claim.family
        and trigger.conflict_record.transport_record == claim.transport_record
        and reconsolidation_trigger(fixture, trigger)
    )


def _ordinary_read_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    return any(
        inventory.source_record == claim.source_record
        and inventory.family == claim.family
        and claim.transport_record in inventory.declared_transports
        and retrieval_without_transport_evidence(fixture, inventory)
        for inventory in fixture.retrieval_inventories.values()
    )


def _provenance_defect_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    return any(
        candidate.trigger in _matching_triggers(fixture, claim)
        and laundered_provenance_defect(fixture, candidate)
        for candidate in fixture.provenance_defect_candidates.values()
    )


def _silent_rewrite_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    return any(
        candidate.trigger in _matching_triggers(fixture, claim)
        and silent_rewrite_evidence(fixture, candidate)
        for candidate in fixture.silent_candidates.values()
    )


def _outcome_collision_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    return any(
        reconsolidation_outcome_collision(fixture, trigger)
        for trigger in _matching_triggers(fixture, claim)
    )


def _unrealized_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    for trigger in _matching_triggers(fixture, claim):
        disposition_inventory = fixture.disposition_inventories.get(trigger.name)
        outcome_inventory = fixture.outcome_inventories.get(trigger.name)
        if disposition_inventory is None or outcome_inventory is None:
            continue
        if (
            f9_reconsolidation_coverage_certified(fixture, disposition_inventory)
            is not None
            and complete_outcome_inventory(fixture, outcome_inventory)
            and not disposition_realized_by_inventory(
                fixture, disposition_inventory, outcome_inventory
            )
        ):
            return True
    return False


def _record_repaired_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    for trigger in _matching_triggers(fixture, claim):
        inventory = fixture.disposition_inventories.get(trigger.name)
        if inventory is None:
            continue
        disposition = f9_reconsolidation_coverage_certified(fixture, inventory)
        if disposition is None:
            continue
        for candidate in fixture.repair_candidates.values():
            if (
                candidate.trigger == trigger
                and record_repair_evidence(fixture, candidate)
                and disposition.disposition is ReconsolidationDisposition.record_repair
                and disposition.supporting_mutation == candidate.mutation_record
                and disposition.supporting_residual is None
            ):
                return True
    return False


def _record_coarsened_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    for trigger in _matching_triggers(fixture, claim):
        inventory = fixture.disposition_inventories.get(trigger.name)
        if inventory is None:
            continue
        disposition = f9_reconsolidation_coverage_certified(fixture, inventory)
        if disposition is None:
            continue
        for candidate in fixture.coarsening_candidates.values():
            if (
                candidate.trigger == trigger
                and record_coarsening_evidence(fixture, candidate)
                and disposition.disposition
                is ReconsolidationDisposition.record_coarsening
                and disposition.supporting_mutation == candidate.mutation_record
                and disposition.supporting_residual is None
            ):
                return True
    return False


def _statused_unresolved_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    for trigger in _matching_triggers(fixture, claim):
        inventory = fixture.disposition_inventories.get(trigger.name)
        if inventory is None:
            continue
        disposition = f9_reconsolidation_coverage_certified(fixture, inventory)
        if disposition is None:
            continue
        for candidate in fixture.unresolved_candidates.values():
            if (
                candidate.trigger == trigger
                and statused_unresolved_evidence(fixture, candidate)
                and disposition.disposition
                is ReconsolidationDisposition.statused_unresolved
                and disposition.supporting_mutation is None
                and disposition.supporting_residual == candidate.residual_record
            ):
                return True
    return False


def _unstatused_conflict_core(fixture: Fixture, claim: ReconsolidationClaimRef) -> bool:
    return any(
        (inventory := fixture.disposition_inventories.get(trigger.name)) is not None
        and no_f9_disposition_for(fixture, inventory)
        for trigger in _matching_triggers(fixture, claim)
    )


def _evidence_cores(
    fixture: Fixture, claim: ReconsolidationClaimRef
) -> dict[ReconsolidationStatus, bool]:
    return {
        ReconsolidationStatus.provenance_defect: _provenance_defect_core(fixture, claim),
        ReconsolidationStatus.silent_rewrite: _silent_rewrite_core(fixture, claim),
        ReconsolidationStatus.ordinary_read: _ordinary_read_core(fixture, claim),
        ReconsolidationStatus.outcome_collision: _outcome_collision_core(fixture, claim),
        ReconsolidationStatus.unrealized_disposition: _unrealized_core(fixture, claim),
        ReconsolidationStatus.record_repaired: _record_repaired_core(fixture, claim),
        ReconsolidationStatus.record_coarsened: _record_coarsened_core(fixture, claim),
        ReconsolidationStatus.statused_unresolved: _statused_unresolved_core(fixture, claim),
        ReconsolidationStatus.unstatused_conflict: _unstatused_conflict_core(fixture, claim),
    }


def _record_evidence_linked(
    fixture: Fixture,
    claim: ReconsolidationClaimRef,
    record: ReconsolidationStatusRecord,
    status: ReconsolidationStatus,
) -> bool:
    if status is ReconsolidationStatus.ordinary_read:
        return True
    for trigger in _matching_triggers(fixture, claim):
        if record.conflict_record != trigger.conflict_record:
            continue
        if status is ReconsolidationStatus.provenance_defect:
            return any(
                candidate.trigger == trigger
                and candidate.audit_record == record.provenance_audit_record
                and laundered_provenance_defect(fixture, candidate)
                for candidate in fixture.provenance_defect_candidates.values()
            )
        if status is ReconsolidationStatus.silent_rewrite:
            return any(
                candidate.trigger == trigger
                and candidate.audit_record == record.provenance_audit_record
                and silent_rewrite_evidence(fixture, candidate)
                for candidate in fixture.silent_candidates.values()
            )
        if status is ReconsolidationStatus.outcome_collision:
            return reconsolidation_outcome_collision(fixture, trigger)
        inventory = fixture.disposition_inventories.get(trigger.name)
        if status is ReconsolidationStatus.unstatused_conflict:
            return inventory is not None and no_f9_disposition_for(fixture, inventory)
        if inventory is None:
            continue
        disposition = f9_reconsolidation_coverage_certified(fixture, inventory)
        if disposition is None or record.disposition_record != disposition:
            continue
        if status is ReconsolidationStatus.unrealized_disposition:
            outcome = fixture.outcome_inventories.get(trigger.name)
            return (
                outcome is not None
                and record.disposition_record == disposition
                and not disposition_realized_by_inventory(fixture, inventory, outcome)
            )
        if status is ReconsolidationStatus.record_repaired:
            return any(
                candidate.trigger == trigger
                and candidate.mutation_record == record.mutation_record
                and disposition.supporting_mutation == candidate.mutation_record
                and record_repair_evidence(fixture, candidate)
                for candidate in fixture.repair_candidates.values()
            )
        if status is ReconsolidationStatus.record_coarsened:
            return any(
                candidate.trigger == trigger
                and candidate.mutation_record == record.mutation_record
                and disposition.supporting_mutation == candidate.mutation_record
                and record_coarsening_evidence(fixture, candidate)
                for candidate in fixture.coarsening_candidates.values()
            )
        if status is ReconsolidationStatus.statused_unresolved:
            return any(
                candidate.trigger == trigger
                and candidate.residual_record == record.residual_record
                and disposition.supporting_residual == candidate.residual_record
                and statused_unresolved_evidence(fixture, candidate)
                for candidate in fixture.unresolved_candidates.values()
            )
    return False


def reconsolidation_case(
    fixture: Fixture,
    claim: ReconsolidationClaimRef,
    record: ReconsolidationStatusRecord,
    status: ReconsolidationStatus,
) -> bool:
    if not reconsolidation_status_occurrence_for(claim, record) or record.status is not status:
        return False
    cores = _evidence_cores(fixture, claim)
    index = STATUS_PRIORITY.index(status)
    return (
        cores[status]
        and all(not cores[higher] for higher in STATUS_PRIORITY[:index])
        and _record_evidence_linked(fixture, claim, record, status)
    )


def provenance_defect_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.provenance_defect)


def silent_rewrite_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.silent_rewrite)


def ordinary_read_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.ordinary_read)


def outcome_collision_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.outcome_collision)


def unrealized_disposition_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.unrealized_disposition)


def record_repaired_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.record_repaired)


def record_coarsened_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.record_coarsened)


def statused_unresolved_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.statused_unresolved)


def unstatused_conflict_case(fixture: Fixture, claim: ReconsolidationClaimRef, record: ReconsolidationStatusRecord) -> bool:
    return reconsolidation_case(fixture, claim, record, ReconsolidationStatus.unstatused_conflict)


def classify_reconsolidation_status(
    fixture: Fixture, claim_name: str
) -> tuple[
    ReconsolidationStatus,
    dict[ReconsolidationStatus, bool],
    ReconsolidationStatusRecord | None,
]:
    claim = fixture.reconsolidation_claims[claim_name]
    cores = _evidence_cores(fixture, claim)
    observed = next(
        (status for status in STATUS_PRIORITY if cores[status]),
        ReconsolidationStatus.unclassified,
    )
    records = tuple(
        record
        for record in fixture.status_records.values()
        if reconsolidation_status_record_matches_claim(claim, record)
    )
    record = next((candidate for candidate in records if candidate.status is observed), None)
    truths = {
        status: (
            record is not None
            and reconsolidation_case(fixture, claim, record, status)
        )
        for status in STATUS_PRIORITY
    }
    if observed is not ReconsolidationStatus.unclassified and not truths[observed]:
        return ReconsolidationStatus.unclassified, truths, record
    return observed, truths, record


def complete_reconsolidation_status(fixture: Fixture, claim_name: str) -> bool:
    claim = fixture.reconsolidation_claims[claim_name]
    observed, truths, record = classify_reconsolidation_status(fixture, claim_name)
    matching = tuple(
        candidate
        for candidate in fixture.status_records.values()
        if reconsolidation_status_occurrence_for(claim, candidate)
    )
    return (
        observed is not ReconsolidationStatus.unclassified
        and record is not None
        and sum(truths.values()) == 1
        and len({candidate.status for candidate in matching}) == 1
    )


def _union_values(
    before: tuple[frozenset[str], ...],
    repair: tuple[frozenset[str], ...],
) -> tuple[frozenset[str], ...]:
    return tuple(left | right for left, right in zip(before, repair, strict=True))


def _build_repair_world_carrier(
    actions: tuple[RepairAction, ...],
    residual_entries: tuple[LedgerEntry, ...],
    q_current: RecordQuotientRecord,
) -> RepairWorldCarrier:
    """Build the actual Repair-World/D4 substrate used by every outcome."""

    z_next_values = frozenset(action.z_next for action in actions)
    trajectory = DeclaredTrajectory(
        legitimate_start=lambda _tau, n: n == 0,
        supp_k=lambda left, right: right == left + 1
        or (left == 0 and right in z_next_values),
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
    defect_policy = policy("e14-defect", defect_by_time)
    audit_policy = policy("e14-audit", audit_by_time)
    move_policy = policy("e14-move", move_record_by_time)

    budget_entry = LedgerEntry("repair_budget_line", -1, F(100))
    ledger_entries = (budget_entry,) + residual_entries
    ledger_start = max((action.defect_evidence.n0 for action in actions), default=0) + 1
    ledger_times = {
        entry: ledger_start + index for index, entry in enumerate(ledger_entries)
    }
    ledger_policy = policy(
        "e14-ledger", {time: entry for entry, time in ledger_times.items()}
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

    instrument_record = "e14-instrument-record"
    instrument_policy = policy("e14-instrument", {0: instrument_record})
    occurrence = CarriedRecordOccurrence(instrument_record, CarriedRecordEvidence(
        n0=0,
        source_tag=FineSourceTag.audited_cell_records,
        generated_by_s=True,
        in_scope=True,
    ))

    moves_by_defect = {
        action.defect: RepairMove(
            sort=RepairSort.P4,
            payload=action.repair_package,
            move_record=f"move_{action.defect}",
            move_record_evidence=action.defect_evidence,
            budget_line=budget_entry,
        )
        for action in actions
    }
    audit_by_move = {
        (f"move_{action.defect}", action.z_next): action.audit_record
        for action in actions
    }
    instrument = ActiveCarriedInstrument(
        instrument="e14-repair-instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=(occurrence,),
        threshold_records=(occurrence,),
        check_rule_records=(CheckRuleRecord(occurrence, "passes"),),
        detects=lambda _z, defect: defect in moves_by_defect,
        gate_allows=lambda _z, defect, move: moves_by_defect.get(defect) == move,
        re_audits=lambda _z, move, z_next, audit: audit_by_move.get(
            (move.move_record, z_next)
        )
        == audit,
    )
    theory = TheoryPackage(
        trajectory=trajectory,
        f="e14-f",
        sigma_f="e14-sigma",
        residual_family="e14-residual-family",
        audit_access="e14-audit-access",
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

    active = ActiveFamily(support=("memory_probe",), weight={"memory_probe": F(1)})
    active_policy = policy("e14-active-family", {0: active})
    economy = ProbeEconomy(
        catalog=ProbeCatalog(("memory_probe",), True),
        active_family_policy=active_policy,
        same_family_saturated=lambda _active, _probe: False,
        exposure_cost_entry=lambda _entry, _probe, _cost: True,
        exposure_budget_entry=lambda _entry, _budget: True,
        exposure_spend_entry=lambda _entry, _spend: True,
        retirement_record_entry=lambda _entry, _probe: True,
        budget_admissible=lambda _move: True,
    )
    config = RepairWorldConfig(
        kernel=ring_kernel(max(z_next_values, default=1) + 1),
        probe_economy=economy,
        e_system=system,
        challenge_process=ChallengeProcess(recurrence_period=None),
    )
    state = RepairWorldState(
        y=0,
        q={item: _at(q_current.quotient, item) for item in ITEMS},
        L=active,
        r=ledger,
        Lambda={
            "repair": F(100),
            "repair_spend": F(0),
            "exposure": F(0),
            "maintenance": F(0),
            "risk": F(0),
        },
        A=AuditState(instrument=instrument, flags=AuditFlags(frozenset((1, 2, 3)))),
    )
    return RepairWorldCarrier(ITEMS, config, state, residual_entries)


def build_fixture() -> Fixture:
    ctx = ReconsolidationClassifierContext()
    evidence = CarriedRecordEvidence(
        n0=0,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )
    action_time = 1

    def next_action_evidence() -> CarriedRecordEvidence:
        nonlocal action_time
        current = action_time
        action_time += 1
        return CarriedRecordEvidence(
            n0=current,
            source_tag=FineSourceTag.committed_state,
            generated_by_s=True,
            in_scope=True,
        )

    claims: dict[str, MemoryClaimRecord] = {}
    memory_records: dict[str, CarriedMemoryRecord] = {}
    formations: dict[str, MemoryRecordFormationRecord] = {}
    quotients: dict[str, RecordQuotientRecord] = {}
    contexts: dict[str, RetrievalContextRecord] = {}
    families: dict[str, DeclaredRetrievalContextFamily] = {}
    transports: dict[str, RetrievalTransportRecord] = {}
    retrieval_inventories: dict[str, CompleteRetrievalTransportInventory] = {}
    conflicts: dict[str, RetrievalConflictRecord] = {}
    triggers: dict[str, ReconsolidationTrigger] = {}
    repair_packages: dict[str, RecordRepairPackage] = {}
    mutations: dict[str, RecordMutationRecord] = {}
    distinction_audits: dict[str, DistinctionSupportAuditRecord] = {}
    provenances: dict[str, MutationProvenanceRecord] = {}
    provenance_audits: dict[str, ProvenanceAuditRecord] = {}
    residuals: dict[str, ReconsolidationResidualRecord] = {}
    ledger_entries: dict[str, LedgerEntry] = {}
    dispositions: dict[str, ReconsolidationDispositionRecord] = {}
    disposition_inventories: dict[str, CompleteReconsolidationDispositionInventory] = {}
    repair_candidates: dict[str, RecordRepairCandidate] = {}
    coarsening_candidates: dict[str, RecordCoarseningCandidate] = {}
    unresolved_candidates: dict[str, StatusedUnresolvedCandidate] = {}
    outcome_inventories: dict[str, CompleteReconsolidationOutcomeInventory] = {}
    silent_candidates: dict[str, SilentRewriteCandidate] = {}
    provenance_defect_candidates: dict[str, LaunderedProvenanceCandidate] = {}
    reconsolidation_claims: dict[str, ReconsolidationClaimRef] = {}
    status_records: dict[str, ReconsolidationStatusRecord] = {}
    formation_registry: dict[int, CarriedMemoryRecord] = {}
    transport_registry: dict[int, RetrievalTransportRecord] = {}
    record_quotient_links: set[tuple[str, str]] = set()
    unsupported_pairs: dict[int, frozenset[frozenset[str]]] = {}
    f9_registry: dict[int, int] = {}
    coarsening_install_registry: set[tuple[str, str, str, str, str]] = set()
    lambda_entries: list[LedgerEntry] = []

    claim_episode = MemoryClaimRecord("claim_episode", 10, (0, 1, 0, 0))
    claim_other = MemoryClaimRecord("claim_other", 11, (0, 0, 0, 0))
    claims.update({record.name: record for record in (claim_episode, claim_other)})

    base_values = (
        frozenset(("door", "left")),
        frozenset(("door", "right")),
        frozenset(("hall",)),
        frozenset(("key",)),
    )
    m_episode = CarriedMemoryRecord(
        "m_episode", 100, 4, claim_episode, base_values, 700
    )
    m_other = CarriedMemoryRecord("m_other", 101, 4, claim_other, base_values, 701)
    memory_records.update({record.name: record for record in (m_episode, m_other)})

    def add_formation(
        name: str,
        formation_id: int,
        record: CarriedMemoryRecord,
        formed_at: int,
        carried: CarriedFact = CARRIED,
        register: bool = True,
    ) -> MemoryRecordFormationRecord:
        formation = MemoryRecordFormationRecord(
            name, formation_id, record, formed_at, carried
        )
        formations[name] = formation
        if register:
            formation_registry[formation_id] = record
        return formation

    add_formation("formation_episode", 1000, m_episode, 0)
    add_formation("formation_other", 1001, m_other, 0)

    q_current = RecordQuotientRecord("q_current", 1, ("u", "u", "v", "v"))
    q_before = RecordQuotientRecord("q_before", 2, ("A", "B", "C", "C"))
    q_after = RecordQuotientRecord("q_after", 3, ("AB", "AB", "C", "C"))
    q_collision_before = RecordQuotientRecord(
        "q_collision_before", 4, q_before.quotient
    )
    q_collision_after = RecordQuotientRecord(
        "q_collision_after", 5, q_after.quotient
    )
    q_after_same = RecordQuotientRecord("q_after_same", 6, q_before.quotient)
    q_before_wrong = RecordQuotientRecord(
        "q_before_wrong", 7, ("AB", "AB", "C", "C")
    )
    q_after_wrong = RecordQuotientRecord(
        "q_after_wrong", 8, ("A", "B", "C", "C")
    )
    for quotient in (
        q_current,
        q_before,
        q_after,
        q_collision_before,
        q_collision_after,
        q_after_same,
        q_before_wrong,
        q_after_wrong,
    ):
        quotients[quotient.name] = quotient

    t_home = ("episode_ab", "episode_ab", "home_c", "home_d")
    t_shift = ("episode_ab", "episode_ab", "shift_c", "home_d")
    t_read = t_home
    t_clear_home = ("seen_a", "seen_b", "home_c", "home_d")
    t_clear_shift = ("seen_a", "seen_b", "shift_c", "home_d")

    def add_family(
        tag: str,
        family_id: int,
        context_ids: tuple[int, int],
        transport_ids: tuple[int, int],
        maps: tuple[tuple[str, str, str, str], tuple[str, str, str, str]],
        conflict_ids: tuple[int, ...] = (),
        conflict_transports: tuple[int, ...] = (0,),
        source: CarriedMemoryRecord = m_episode,
    ) -> tuple[
        DeclaredRetrievalContextFamily,
        RetrievalTransportRecord,
        RetrievalTransportRecord,
        tuple[RetrievalConflictRecord, ...],
    ]:
        record_tag = {
            "pair_mismatch": "pair",
            "root_drift": "root",
            "wrong_direction": "wrong",
            "ledger_label": "ledger",
        }.get(tag, tag)
        first_label = "home" if tag == "scope" else "focus"
        second_label = "shift" if tag == "scope" else "peer"
        first_context = RetrievalContextRecord(
            f"c_{record_tag}_{first_label}", context_ids[0]
        )
        second_context = RetrievalContextRecord(
            f"c_{record_tag}_{second_label}", context_ids[1]
        )
        contexts[first_context.name] = first_context
        contexts[second_context.name] = second_context
        family = DeclaredRetrievalContextFamily(
            f"family_{tag}", family_id, (first_context, second_context)
        )
        families[family.name] = family
        first_transport = RetrievalTransportRecord(
            f"t_{record_tag}_{first_label}",
            transport_ids[0],
            source,
            first_context,
            q_current,
            maps[0],
            transport_ids[0] - 196,
        )
        second_transport = RetrievalTransportRecord(
            f"t_{record_tag}_{second_label}",
            transport_ids[1],
            source,
            second_context,
            q_current,
            maps[1],
            transport_ids[1] - 196,
        )
        for transport in (first_transport, second_transport):
            transports[transport.name] = transport
            transport_registry[transport.transport_id] = transport
        inventory = CompleteRetrievalTransportInventory(
            f"inventory_{tag}", source, family, (first_transport, second_transport)
        )
        retrieval_inventories[inventory.name] = inventory
        family_conflicts: list[RetrievalConflictRecord] = []
        for index, conflict_id in enumerate(conflict_ids):
            selected = (first_transport, second_transport)[conflict_transports[index]]
            conflict = RetrievalConflictRecord(
                f"conflict_{tag}" + ("_home" if len(conflict_ids) > 1 and index == 0 else "_shift" if len(conflict_ids) > 1 else ""),
                conflict_id,
                source,
                selected,
                source.claim_record,
            )
            conflicts[conflict.name] = conflict
            family_conflicts.append(conflict)
            trigger_name = f"trigger_{tag}" + ("_home" if len(conflict_ids) > 1 and index == 0 else "_shift" if len(conflict_ids) > 1 else "")
            triggers[trigger_name] = ReconsolidationTrigger(
                trigger_name, source, family, inventory, conflict
            )
        return family, first_transport, second_transport, tuple(family_conflicts)

    family_specs = (
        ("repair", 20, (101, 102), (200, 201), (t_home, t_shift), (700,), (0,)),
        ("coarsen", 21, (103, 104), (202, 203), (t_shift, t_home), (701,), (0,)),
        ("unresolved", 22, (105, 106), (204, 205), (t_shift, t_home), (702,), (0,)),
        ("collision", 23, (107, 108), (206, 207), (t_home, t_shift), (703,), (0,)),
        ("unrealized", 24, (109, 110), (208, 209), (t_home, t_shift), (704,), (0,)),
        ("silent", 25, (111, 112), (210, 211), (t_home, t_shift), (705,), (0,)),
        ("provenance", 26, (113, 114), (212, 213), (t_home, t_shift), (706,), (0,)),
        ("ordinary", 27, (115, 116), (214, 215), (t_read, t_read), (), (0,)),
        ("unstatused", 28, (117, 118), (216, 217), (t_home, t_shift), (707,), (0,)),
        ("scope", 29, (119, 120), (218, 219), (t_home, t_shift), (708, 709), (0, 1)),
        ("clear", 30, (121, 122), (220, 221), (t_clear_home, t_clear_shift), (), (0,)),
    )
    for spec in family_specs:
        add_family(*spec)
    add_family(
        "other",
        31,
        (123, 124),
        (222, 223),
        (t_home, t_shift),
        source=m_other,
    )
    control_specs = (
        ("pair_mismatch", 32, (130, 131), (230, 231), 710),
        ("root_drift", 33, (132, 133), (232, 233), 711),
        ("non_strict", 34, (134, 135), (234, 235), 712),
        ("wrong_direction", 35, (136, 137), (236, 237), 713),
        ("uncarried", 36, (138, 139), (238, 239), 714),
        ("ledger_label", 37, (140, 141), (240, 241), 715),
        ("unrelated", 38, (142, 143), (242, 243), 716),
    )
    for tag, family_id, context_ids, transport_ids, conflict_id in control_specs:
        add_family(
            tag,
            family_id,
            context_ids,
            transport_ids,
            (t_home, t_shift),
            conflict_ids=(conflict_id,),
        )

    # The reviewed malformed inventory covers both contexts; only same-context
    # disagreement fails.
    bad_focus = RetrievalContextRecord("c_bad_focus", 144)
    bad_peer = RetrievalContextRecord("c_bad_peer", 145)
    contexts.update({bad_focus.name: bad_focus, bad_peer.name: bad_peer})
    family_bad = DeclaredRetrievalContextFamily(
        "family_bad_same_context", 39, (bad_focus, bad_peer)
    )
    families[family_bad.name] = family_bad
    bad_transports = (
        RetrievalTransportRecord(
            "t_bad_focus", 224, m_episode, bad_focus, q_current, t_home, 28
        ),
        RetrievalTransportRecord(
            "t_bad_focus_disagree",
            225,
            m_episode,
            bad_focus,
            q_current,
            ("contradictory_a",) + t_home[1:],
            29,
        ),
        RetrievalTransportRecord(
            "t_bad_peer", 226, m_episode, bad_peer, q_current, t_shift, 30
        ),
    )
    for transport in bad_transports:
        transports[transport.name] = transport
        transport_registry[transport.transport_id] = transport
    retrieval_inventories["inventory_bad_same_context"] = (
        CompleteRetrievalTransportInventory(
            "inventory_bad_same_context", m_episode, family_bad, bad_transports
        )
    )

    def add_repair_candidate(
        name: str,
        trigger_name: str,
        repair_id: int,
        mutation_id: int,
        formation_id: int,
        provenance_id: int,
        z_after: int,
        repair_value: tuple[frozenset[str], ...],
        after_name: str,
        after_record_id: int | None = None,
        after_carried: CarriedFact = CARRIED,
        formation_carried: CarriedFact = CARRIED,
        register_formation: bool = True,
    ) -> RecordRepairCandidate:
        trigger = triggers[trigger_name]
        source = trigger.source_record
        package = RecordRepairPackage(
            f"repair_{name}", repair_id, trigger.conflict_record.transport_record.context_record, repair_value
        )
        after = CarriedMemoryRecord(
            after_name,
            source.record_id if after_record_id is None else after_record_id,
            source.version + 1,
            source.claim_record,
            _union_values(source.record_value, repair_value),
            source.provenance_root_id,
            after_carried,
        )
        mutation = RecordMutationRecord(
            f"mutation_{name}",
            mutation_id,
            source,
            after,
            trigger.conflict_record.transport_record.transport_id,
            trigger.conflict_record.transport_record.context_record,
            RecordMutationKind.repair,
        )
        provenance = MutationProvenanceRecord(
            f"provenance_{name}", provenance_id, mutation, source, after, source.provenance_root_id
        )
        formation = add_formation(
            f"formation_{after_name}",
            formation_id,
            after,
            trigger.conflict_record.transport_record.retrieved_at,
            formation_carried,
            register_formation,
        )
        action_record_evidence = next_action_evidence()
        action = RepairAction(
            repair_package={item: repair_value[index] for index, item in enumerate(ITEMS)},
            z_next=z_after,
            defect=f"defect_{name}",
            defect_evidence=action_record_evidence,
            audit_record=f"audit_{name}",
            audit_record_evidence=action_record_evidence,
        )
        candidate = RecordRepairCandidate(
            f"repair_evidence_{name}", trigger, package, after, formation, mutation, provenance, 0, action
        )
        repair_packages[package.name] = package
        memory_records[after.name] = after
        mutations[mutation.name] = mutation
        provenances[provenance.name] = provenance
        repair_candidates[candidate.name] = candidate
        return candidate

    repair_primary = add_repair_candidate(
        "repair",  # name preserves mutation_repair / repair_repair; alias below
        "trigger_repair",
        300,
        400,
        1002,
        500,
        1,
        (frozenset(("cue_left",)), frozenset(("cue_right",)), frozenset(), frozenset()),
        "m_repaired",
    )
    # Round A names the package repair_primary, not repair_repair.
    package_primary = replace(repair_primary.repair_package, name="repair_primary")
    repair_packages.pop(repair_primary.repair_package.name)
    repair_packages[package_primary.name] = package_primary
    repair_primary = replace(repair_primary, repair_package=package_primary)
    repair_candidates[repair_primary.name] = repair_primary

    repair_collision = add_repair_candidate(
        "collision_repair",
        "trigger_collision",
        302,
        410,
        1010,
        510,
        2,
        (frozenset(("collision_left",)), frozenset(("collision_right",)), frozenset(), frozenset()),
        "m_collision_repaired",
    )
    collision_package = replace(
        repair_collision.repair_package, name="repair_collision"
    )
    repair_packages.pop(repair_collision.repair_package.name)
    repair_packages[collision_package.name] = collision_package
    repair_collision = replace(repair_collision, repair_package=collision_package)
    repair_candidates[repair_collision.name] = repair_collision
    repair_reference = add_repair_candidate(
        "reference_realized",
        "trigger_unrealized",
        303,
        400,
        1012,
        512,
        4,
        (frozenset(("ref_left",)), frozenset(("ref_right",)), frozenset(), frozenset()),
        "m_reference_realized",
    )
    reference_package = replace(
        repair_reference.repair_package, name="repair_reference"
    )
    repair_packages.pop(repair_reference.repair_package.name)
    repair_packages[reference_package.name] = reference_package
    repair_reference = replace(repair_reference, repair_package=reference_package)
    repair_candidates[repair_reference.name] = repair_reference
    repair_scope = add_repair_candidate(
        "scope_home",
        "trigger_scope_home",
        304,
        420,
        1013,
        513,
        5,
        (frozenset(("scope_left",)), frozenset(("scope_right",)), frozenset(), frozenset()),
        "m_scope_repaired",
    )

    def add_coarsening_candidate(
        name: str,
        trigger_name: str,
        mutation_id: int,
        formation_id: int,
        provenance_id: int,
        audit_id: int,
        z_after: int,
        before: RecordQuotientRecord,
        after: RecordQuotientRecord,
        pair: tuple[str, str],
        unsupported: frozenset[frozenset[str]],
        after_name: str,
        after_values: tuple[frozenset[str], ...] | None = None,
        support_audit_name: str | None = None,
    ) -> RecordCoarseningCandidate:
        trigger = triggers[trigger_name]
        source = trigger.source_record
        record = CarriedMemoryRecord(
            after_name,
            source.record_id,
            source.version + 1,
            source.claim_record,
            after_values
            if after_values is not None
            else (
                frozenset(("door",)),
                frozenset(("door",)),
                frozenset(("hall",)),
                frozenset(("key",)),
            ),
            source.provenance_root_id,
        )
        mutation = RecordMutationRecord(
            f"mutation_{name}",
            mutation_id,
            source,
            record,
            trigger.conflict_record.transport_record.transport_id,
            trigger.conflict_record.transport_record.context_record,
            RecordMutationKind.coarsening,
        )
        audit = DistinctionSupportAuditRecord(
            support_audit_name or f"audit_{name}",
            audit_id,
            before,
            after,
            source.claim_record.claim_id,
            pair[0],
            pair[1],
        )
        provenance = MutationProvenanceRecord(
            f"provenance_{name}", provenance_id, mutation, source, record, source.provenance_root_id
        )
        formation = add_formation(
            f"formation_{after_name}", formation_id, record, trigger.conflict_record.transport_record.retrieved_at
        )
        action_record_evidence = next_action_evidence()
        action = RepairAction(
            repair_package={item: _at(after.quotient, item) for item in ITEMS},
            z_next=z_after,
            defect=f"defect_{name}",
            defect_evidence=action_record_evidence,
            audit_record=f"audit_step_{name}",
            audit_record_evidence=action_record_evidence,
        )
        candidate = RecordCoarseningCandidate(
            f"coarsening_evidence_{name}",
            trigger,
            record,
            formation,
            before,
            after,
            audit,
            mutation,
            provenance,
            0,
            action,
        )
        memory_records[record.name] = record
        mutations[mutation.name] = mutation
        distinction_audits[audit.name] = audit
        provenances[provenance.name] = provenance
        coarsening_candidates[candidate.name] = candidate
        unsupported_pairs[audit_id] = unsupported
        record_quotient_links.add((source.name, before.name))
        record_quotient_links.add((record.name, after.name))
        coarsening_install_registry.add(
            (action.defect, source.name, record.name, before.name, after.name)
        )
        return candidate

    coarsen_primary = add_coarsening_candidate(
        "coarsen",
        "trigger_coarsen",
        401,
        1003,
        501,
        500,
        1,
        q_before,
        q_after,
        ("a", "b"),
        frozenset((frozenset(("a", "b")),)),
        "m_coarsened",
        support_audit_name="audit_merge_ab",
    )
    coarsen_collision = add_coarsening_candidate(
        "collision_coarsen",
        "trigger_collision",
        411,
        1011,
        511,
        502,
        3,
        q_collision_before,
        q_collision_after,
        ("a", "b"),
        frozenset((frozenset(("a", "b")),)),
        "m_collision_coarsened",
        support_audit_name="audit_collision_ab",
    )

    def add_unresolved_candidate(
        name: str,
        trigger_name: str,
        residual_id: int,
        formation_id: int,
        current_record: CarriedMemoryRecord,
        entry_amount: Fraction,
        include_entry: bool = True,
    ) -> StatusedUnresolvedCandidate:
        trigger = triggers[trigger_name]
        residual = ReconsolidationResidualRecord(
            f"residual_{name}", residual_id, trigger.conflict_record, F(1, 3)
        )
        entry = LedgerEntry(f"led_residual_{name}", residual_id, entry_amount)
        formation = add_formation(
            f"formation_{current_record.name}_{name}",
            formation_id,
            current_record,
            trigger.conflict_record.transport_record.retrieved_at,
        )
        candidate = StatusedUnresolvedCandidate(
            f"unresolved_evidence_{name}", trigger, current_record, formation, residual, entry
        )
        memory_records[current_record.name] = current_record
        residuals[residual.name] = residual
        ledger_entries[entry.name] = entry
        unresolved_candidates[candidate.name] = candidate
        if include_entry:
            lambda_entries.append(entry)
        return candidate

    unresolved_primary = add_unresolved_candidate(
        "unresolved", "trigger_unresolved", 600, 1004, m_episode, F(1, 3)
    )
    unresolved_scope = add_unresolved_candidate(
        "scope_shift", "trigger_scope_shift", 610, 1014, m_episode, F(1, 3)
    )

    # Direct-reference ID-coincidence record: same numeric ID, different full
    # record, and no evidence in the trigger's sound outcome inventory.
    m_detached = CarriedMemoryRecord(
        "m_detached",
        100,
        5,
        claim_episode,
        base_values[:-1] + (frozenset(("key", "detached")),),
        700,
    )
    add_formation("formation_detached", 1015, m_detached, 13)
    mutation_detached = RecordMutationRecord(
        "mutation_detached",
        400,
        m_episode,
        m_detached,
        209,
        contexts["c_unrealized_peer"],
        RecordMutationKind.repair,
    )
    memory_records[m_detached.name] = m_detached
    mutations[mutation_detached.name] = mutation_detached

    def add_disposition(
        name: str,
        trigger_name: str,
        disposition_id: int,
        status: ReconsolidationDisposition,
        mutation: RecordMutationRecord | None = None,
        residual: ReconsolidationResidualRecord | None = None,
    ) -> ReconsolidationDispositionRecord:
        trigger = triggers[trigger_name]
        record = ReconsolidationDispositionRecord(
            name,
            disposition_id,
            trigger.conflict_record,
            status,
            mutation,
            residual,
        )
        dispositions[name] = record
        f9_registry[trigger.conflict_record.conflict_id] = disposition_id
        disposition_inventories[trigger_name] = (
            CompleteReconsolidationDispositionInventory(
                f"disposition_inventory_{trigger_name}", trigger.conflict_record, (record,)
            )
        )
        return record

    disp_repair = add_disposition(
        "disp_repair", "trigger_repair", 800, ReconsolidationDisposition.record_repair, repair_primary.mutation_record
    )
    disp_coarsen = add_disposition(
        "disp_coarsen", "trigger_coarsen", 801, ReconsolidationDisposition.record_coarsening, coarsen_primary.mutation_record
    )
    disp_unresolved = add_disposition(
        "disp_unresolved", "trigger_unresolved", 802, ReconsolidationDisposition.statused_unresolved, residual=unresolved_primary.residual_record
    )
    disp_detached = add_disposition(
        "disp_detached", "trigger_unrealized", 803, ReconsolidationDisposition.record_repair, mutation_detached
    )
    disp_scope_home = add_disposition(
        "disp_scope_home", "trigger_scope_home", 804, ReconsolidationDisposition.record_repair, repair_scope.mutation_record
    )
    disp_scope_shift = add_disposition(
        "disp_scope_shift", "trigger_scope_shift", 805, ReconsolidationDisposition.statused_unresolved, residual=unresolved_scope.residual_record
    )

    # Empty, complete F9 inventories for the explicit silent/unstatused paths.
    for trigger_name in ("trigger_silent", "trigger_unstatused", "trigger_collision", "trigger_provenance"):
        disposition_inventories[trigger_name] = CompleteReconsolidationDispositionInventory(
            f"disposition_inventory_{trigger_name}", triggers[trigger_name].conflict_record, ()
        )

    # Reviewed negative outcome candidates.
    pair_bad = add_coarsening_candidate(
        "pair_mismatch",
        "trigger_pair_mismatch",
        430,
        1020,
        520,
        503,
        6,
        q_before,
        q_after,
        ("c", "d"),
        frozenset((frozenset(("a", "b")),)),
        "m_pair_mismatch",
        support_audit_name="audit_merge_cd",
    )
    non_strict = add_coarsening_candidate(
        "non_strict",
        "trigger_non_strict",
        431,
        1021,
        521,
        504,
        7,
        q_before,
        q_after_same,
        ("a", "b"),
        frozenset((frozenset(("a", "b")),)),
        "m_non_strict",
    )
    wrong_direction = add_coarsening_candidate(
        "wrong_direction",
        "trigger_wrong_direction",
        432,
        1022,
        522,
        505,
        8,
        q_before_wrong,
        q_after_wrong,
        ("a", "b"),
        frozenset((frozenset(("a", "b")),)),
        "m_wrong_direction",
    )
    uncarried_fact = CarriedFact(generated_by_s=False)
    uncarried_repair = add_repair_candidate(
        "uncarried",
        "trigger_uncarried",
        305,
        433,
        1023,
        523,
        9,
        (frozenset(("cue_left",)), frozenset(("cue_right",)), frozenset(), frozenset()),
        "m_uncarried_successor",
        formation_carried=uncarried_fact,
        register_formation=False,
    )

    m_root_drift = replace(
        m_episode, name="m_root_drift", provenance_root_id=701
    )
    root_unresolved = add_unresolved_candidate(
        "root_drift", "trigger_root_drift", 601, 1024, m_root_drift, F(1, 3)
    )
    ledger_unresolved = add_unresolved_candidate(
        "missing_label", "trigger_ledger_label", 602, 1025, m_episode, F(1, 2), include_entry=False
    )
    ledger_entries.pop(ledger_unresolved.ledger_entry.name)
    label_only_entry = replace(
        ledger_unresolved.ledger_entry,
        name="led_missing_label",
        charged_metadata=True,
    )
    ledger_unresolved = replace(
        ledger_unresolved,
        ledger_entry=label_only_entry,
    )
    ledger_entries[label_only_entry.name] = label_only_entry
    unresolved_candidates[ledger_unresolved.name] = ledger_unresolved

    negative_dispositions = (
        ("disp_pair_mismatch", "trigger_pair_mismatch", 810, ReconsolidationDisposition.record_coarsening, pair_bad.mutation_record, None),
        ("disp_root_drift", "trigger_root_drift", 811, ReconsolidationDisposition.statused_unresolved, None, root_unresolved.residual_record),
        ("disp_non_strict", "trigger_non_strict", 812, ReconsolidationDisposition.record_coarsening, non_strict.mutation_record, None),
        ("disp_wrong_direction", "trigger_wrong_direction", 813, ReconsolidationDisposition.record_coarsening, wrong_direction.mutation_record, None),
        ("disp_uncarried", "trigger_uncarried", 814, ReconsolidationDisposition.record_repair, uncarried_repair.mutation_record, None),
        ("disp_ledger_label", "trigger_ledger_label", 815, ReconsolidationDisposition.statused_unresolved, None, ledger_unresolved.residual_record),
    )
    for args in negative_dispositions:
        add_disposition(*args)

    # A genuinely lawful mutation for another source/trigger cannot realize
    # the unrelated claim's direct disposition.
    m_unrelated_source = CarriedMemoryRecord(
        "m_unrelated_source", 102, 4, claim_episode, base_values, 702
    )
    memory_records[m_unrelated_source.name] = m_unrelated_source
    add_formation("formation_unrelated_source", 1030, m_unrelated_source, 0)
    add_family(
        "other_source",
        40,
        (146, 147),
        (244, 245),
        (t_home, t_shift),
        source=m_unrelated_source,
        conflict_ids=(717,),
    )
    unrelated_other = add_repair_candidate(
        "other",
        "trigger_other_source",
        306,
        440,
        1031,
        530,
        10,
        (frozenset(("other_left",)), frozenset(("other_right",)), frozenset(), frozenset()),
        "m_other_repaired",
    )
    disp_unrelated = add_disposition(
        "disp_unrelated",
        "trigger_unrelated",
        816,
        ReconsolidationDisposition.record_repair,
        unrelated_other.mutation_record,
    )

    # Sound outcome inventories. Invalid candidates are deliberately omitted;
    # completeness is computed by scanning only candidates whose full evidence
    # validates for the same trigger.
    def add_outcome(
        trigger_name: str,
        repairs: tuple[RecordMutationRecord, ...] = (),
        coarsenings: tuple[RecordMutationRecord, ...] = (),
        unresolved: tuple[ReconsolidationResidualRecord, ...] = (),
    ) -> CompleteReconsolidationOutcomeInventory:
        inventory = CompleteReconsolidationOutcomeInventory(
            f"outcome_inventory_{trigger_name}", triggers[trigger_name], repairs, coarsenings, unresolved
        )
        outcome_inventories[trigger_name] = inventory
        return inventory

    add_outcome("trigger_repair", repairs=(repair_primary.mutation_record,))
    add_outcome("trigger_coarsen", coarsenings=(coarsen_primary.mutation_record,))
    add_outcome("trigger_unresolved", unresolved=(unresolved_primary.residual_record,))
    add_outcome(
        "trigger_collision",
        repairs=(repair_collision.mutation_record,),
        coarsenings=(coarsen_collision.mutation_record,),
    )
    add_outcome("trigger_unrealized", repairs=(repair_reference.mutation_record,))
    add_outcome("trigger_scope_home", repairs=(repair_scope.mutation_record,))
    add_outcome("trigger_scope_shift", unresolved=(unresolved_scope.residual_record,))
    for trigger_name in (
        "trigger_pair_mismatch",
        "trigger_root_drift",
        "trigger_non_strict",
        "trigger_wrong_direction",
        "trigger_uncarried",
        "trigger_ledger_label",
        "trigger_unrelated",
        "trigger_silent",
        "trigger_unstatused",
    ):
        add_outcome(trigger_name)

    # Silent rewrite and laundered-provenance records.
    m_silent = replace(
        m_episode,
        name="m_silent",
        record_value=base_values[:-1] + (frozenset(("key", "false-detail")),),
    )
    memory_records[m_silent.name] = m_silent
    formation_silent = add_formation("formation_silent", 1040, m_silent, 14)
    audit_silent = ProvenanceAuditRecord(
        "audit_silent", 600, m_episode, m_silent, 210
    )
    provenance_audits[audit_silent.name] = audit_silent
    silent_candidates["silent_rewrite_silent"] = SilentRewriteCandidate(
        "silent_rewrite_silent",
        triggers["trigger_silent"],
        m_silent,
        formation_silent,
        audit_silent,
        disposition_inventories["trigger_silent"],
        outcome_inventories["trigger_silent"],
    )

    m_laundered = replace(
        m_episode,
        name="m_laundered",
        record_value=base_values[:-1] + (frozenset(("key", "false-detail")),),
    )
    memory_records[m_laundered.name] = m_laundered
    formation_laundered = add_formation("formation_laundered", 1041, m_laundered, 16)
    mutation_laundered = RecordMutationRecord(
        "mutation_laundered",
        450,
        m_episode,
        m_laundered,
        212,
        contexts["c_provenance_focus"],
        RecordMutationKind.repair,
    )
    provenance_laundered = MutationProvenanceRecord(
        "provenance_laundered",
        550,
        mutation_laundered,
        m_episode,
        m_laundered,
        999,
    )
    audit_laundered = ProvenanceAuditRecord(
        "audit_laundered", 601, m_episode, m_laundered, 212
    )
    mutations[mutation_laundered.name] = mutation_laundered
    provenances[provenance_laundered.name] = provenance_laundered
    provenance_audits[audit_laundered.name] = audit_laundered
    provenance_defect_candidates["laundered_provenance"] = (
        LaunderedProvenanceCandidate(
            "laundered_provenance",
            triggers["trigger_provenance"],
            m_laundered,
            formation_laundered,
            mutation_laundered,
            provenance_laundered,
            audit_laundered,
        )
    )

    # Every trigger without a typed F9 record still owns a complete empty
    # inventory where required by status checks.
    for trigger_name, trigger in triggers.items():
        disposition_inventories.setdefault(
            trigger_name,
            CompleteReconsolidationDispositionInventory(
                f"disposition_inventory_{trigger_name}", trigger.conflict_record, ()
            ),
        )

    def add_claim_and_status(
        claim_name: str,
        family_name: str,
        transport_name: str,
        status: ReconsolidationStatus,
        status_id: int,
        conflict: RetrievalConflictRecord | None = None,
        mutation: RecordMutationRecord | None = None,
        residual: ReconsolidationResidualRecord | None = None,
        disposition: ReconsolidationDispositionRecord | None = None,
        provenance_audit: ProvenanceAuditRecord | None = None,
        source: CarriedMemoryRecord = m_episode,
    ) -> None:
        family = families[family_name]
        transport = transports[transport_name]
        claim = ReconsolidationClaimRef(
            claim_name,
            source,
            family,
            transport,
            transport.context_record,
            source.claim_record,
        )
        record = ReconsolidationStatusRecord(
            f"status_{claim_name}",
            status_id,
            status,
            source,
            family,
            transport,
            transport.context_record,
            source.claim_record,
            conflict,
            mutation,
            residual,
            disposition,
            provenance_audit,
        )
        reconsolidation_claims[claim_name] = claim
        status_records[record.name] = record

    add_claim_and_status(
        "claim_record_repaired", "family_repair", "t_repair_focus", ReconsolidationStatus.record_repaired, 900,
        conflicts["conflict_repair"], repair_primary.mutation_record, disposition=disp_repair,
    )
    add_claim_and_status(
        "claim_record_coarsened", "family_coarsen", "t_coarsen_focus", ReconsolidationStatus.record_coarsened, 901,
        conflicts["conflict_coarsen"], coarsen_primary.mutation_record, disposition=disp_coarsen,
    )
    add_claim_and_status(
        "claim_statused_unresolved", "family_unresolved", "t_unresolved_focus", ReconsolidationStatus.statused_unresolved, 902,
        conflicts["conflict_unresolved"], residual=unresolved_primary.residual_record, disposition=disp_unresolved,
    )
    add_claim_and_status(
        "claim_outcome_collision", "family_collision", "t_collision_focus", ReconsolidationStatus.outcome_collision, 903,
        conflicts["conflict_collision"],
    )
    add_claim_and_status(
        "claim_unrealized_direct_reference", "family_unrealized", "t_unrealized_focus", ReconsolidationStatus.unrealized_disposition, 904,
        conflicts["conflict_unrealized"], disposition=disp_detached,
    )
    add_claim_and_status(
        "claim_silent_rewrite", "family_silent", "t_silent_focus", ReconsolidationStatus.silent_rewrite, 905,
        conflicts["conflict_silent"], provenance_audit=audit_silent,
    )
    add_claim_and_status(
        "claim_provenance_defect", "family_provenance", "t_provenance_focus", ReconsolidationStatus.provenance_defect, 906,
        conflicts["conflict_provenance"], provenance_audit=audit_laundered,
    )
    add_claim_and_status(
        "claim_ordinary_read", "family_ordinary", "t_ordinary_focus", ReconsolidationStatus.ordinary_read, 907,
    )
    add_claim_and_status(
        "claim_unstatused_conflict", "family_unstatused", "t_unstatused_focus", ReconsolidationStatus.unstatused_conflict, 908,
        conflicts["conflict_unstatused"],
    )
    add_claim_and_status(
        "ctrl_coarsening_audited_pair_mismatch", "family_pair_mismatch", "t_pair_focus", ReconsolidationStatus.unrealized_disposition, 909,
        conflicts["conflict_pair_mismatch"], disposition=dispositions["disp_pair_mismatch"],
    )
    add_claim_and_status(
        "ctrl_unresolved_provenance_root_mismatch", "family_root_drift", "t_root_focus", ReconsolidationStatus.unrealized_disposition, 910,
        conflicts["conflict_root_drift"], disposition=dispositions["disp_root_drift"],
    )
    add_claim_and_status(
        "ctrl_non_strict_coarsening", "family_non_strict", "t_non_strict_focus", ReconsolidationStatus.unrealized_disposition, 911,
        conflicts["conflict_non_strict"], disposition=dispositions["disp_non_strict"],
    )
    add_claim_and_status(
        "ctrl_wrong_direction_refinement", "family_wrong_direction", "t_wrong_focus", ReconsolidationStatus.unrealized_disposition, 912,
        conflicts["conflict_wrong_direction"], disposition=dispositions["disp_wrong_direction"],
    )
    add_claim_and_status(
        "ctrl_uncarried_post_retrieval_record", "family_uncarried", "t_uncarried_focus", ReconsolidationStatus.unrealized_disposition, 913,
        conflicts["conflict_uncarried"], disposition=dispositions["disp_uncarried"],
    )
    add_claim_and_status(
        "ctrl_ledger_charge_label_only", "family_ledger_label", "t_ledger_focus", ReconsolidationStatus.unrealized_disposition, 914,
        conflicts["conflict_ledger_label"], disposition=dispositions["disp_ledger_label"],
    )
    add_claim_and_status(
        "scope_home", "family_scope", "t_scope_home", ReconsolidationStatus.record_repaired, 915,
        conflicts["conflict_scope_home"], repair_scope.mutation_record, disposition=disp_scope_home,
    )
    add_claim_and_status(
        "scope_shift", "family_scope", "t_scope_shift", ReconsolidationStatus.statused_unresolved, 916,
        conflicts["conflict_scope_shift"], residual=unresolved_scope.residual_record, disposition=disp_scope_shift,
    )
    add_claim_and_status(
        "ctrl_unrelated_mutation_evidence", "family_unrelated", "t_unrelated_focus", ReconsolidationStatus.unrealized_disposition, 917,
        conflicts["conflict_unrelated"], disposition=disp_unrelated,
    )

    # No-status controls still have fully linked claim refs, but deliberately
    # no carried status record.
    for name, family_name, transport_name, source in (
        ("ctrl_no_conflict_after_transport", "family_clear", "t_clear_focus", m_episode),
        ("ctrl_conflict_for_other_claim", "family_other", "t_other_focus", m_other),
    ):
        transport = transports[transport_name]
        reconsolidation_claims[name] = ReconsolidationClaimRef(
            name, source, families[family_name], transport, transport.context_record, source.claim_record
        )

    # Build concrete, independently scoped E14 evidence for the 16 budget
    # episodes. Budget labels are attached only after each claim is complete.
    strata: list[StratumEpisode] = []
    loose_budget = BudgetMetadata(F(3), F(1), F(2), F(1))
    tight_budget = BudgetMetadata(F(1), F(1), F(1, 4), F(1))
    stratum_statuses = (
        [("L", index, ReconsolidationStatus.record_repaired) for index in range(1, 7)]
        + [("L", 7, ReconsolidationStatus.record_coarsened), ("L", 8, ReconsolidationStatus.statused_unresolved)]
        + [("T", 1, ReconsolidationStatus.record_repaired)]
        + [("T", index, ReconsolidationStatus.record_coarsened) for index in range(2, 8)]
        + [("T", 8, ReconsolidationStatus.statused_unresolved)]
    )
    for offset, (label, index, status) in enumerate(stratum_statuses):
        tag = f"stratum_{label.lower()}{index}"
        source = CarriedMemoryRecord(
            f"m_{tag}", 1000 + offset, 4, claim_episode, base_values, 2000 + offset
        )
        memory_records[source.name] = source
        add_formation(f"formation_{tag}_source", 2000 + offset * 4, source, 0)
        family, focus, _, family_conflicts = add_family(
            tag,
            100 + offset,
            (300 + offset * 2, 301 + offset * 2),
            (400 + offset * 2, 401 + offset * 2),
            (t_home, t_shift),
            source=source,
            conflict_ids=(800 + offset,),
        )
        trigger_name = f"trigger_{tag}"
        trigger = triggers[trigger_name]
        if status is ReconsolidationStatus.record_repaired:
            candidate = add_repair_candidate(
                tag,
                trigger_name,
                600 + offset,
                700 + offset,
                2001 + offset * 4,
                700 + offset,
                30 + offset,
                (frozenset((f"{tag}_left",)), frozenset((f"{tag}_right",)), frozenset(), frozenset()),
                f"m_{tag}_repaired",
            )
            disposition = add_disposition(
                f"disp_{tag}", trigger_name, 900 + offset, ReconsolidationDisposition.record_repair, candidate.mutation_record
            )
            add_outcome(trigger_name, repairs=(candidate.mutation_record,))
            mutation = candidate.mutation_record
            residual = None
        elif status is ReconsolidationStatus.record_coarsened:
            before = RecordQuotientRecord(
                f"q_{tag}_before", 100 + offset * 2, q_before.quotient
            )
            after = RecordQuotientRecord(
                f"q_{tag}_after", 101 + offset * 2, q_after.quotient
            )
            quotients[before.name] = before
            quotients[after.name] = after
            candidate = add_coarsening_candidate(
                tag,
                trigger_name,
                700 + offset,
                2001 + offset * 4,
                700 + offset,
                700 + offset,
                30 + offset,
                before,
                after,
                ("a", "b"),
                frozenset((frozenset(("a", "b")),)),
                f"m_{tag}_coarsened",
            )
            disposition = add_disposition(
                f"disp_{tag}", trigger_name, 900 + offset, ReconsolidationDisposition.record_coarsening, candidate.mutation_record
            )
            add_outcome(trigger_name, coarsenings=(candidate.mutation_record,))
            mutation = candidate.mutation_record
            residual = None
        else:
            candidate = add_unresolved_candidate(
                tag,
                trigger_name,
                1000 + offset,
                2001 + offset * 4,
                source,
                F(1, 3),
            )
            disposition = add_disposition(
                f"disp_{tag}", trigger_name, 900 + offset, ReconsolidationDisposition.statused_unresolved, residual=candidate.residual_record
            )
            add_outcome(trigger_name, unresolved=(candidate.residual_record,))
            mutation = None
            residual = candidate.residual_record
        claim_name = f"claim_{tag}"
        add_claim_and_status(
            claim_name,
            family.name,
            focus.name,
            status,
            1000 + offset,
            family_conflicts[0],
            mutation,
            residual,
            disposition,
            source=source,
        )
        strata.append(
            StratumEpisode(
                tag, claim_name, loose_budget if label == "L" else tight_budget
            )
        )

    carrier = _build_repair_world_carrier(
        tuple(
            candidate.action
            for candidate in (
                *repair_candidates.values(),
                *coarsening_candidates.values(),
            )
        ),
        tuple(lambda_entries),
        q_current,
    )
    return Fixture(
        carrier=carrier,
        ctx=ctx,
        claims=claims,
        memory_records=memory_records,
        formations=formations,
        quotients=quotients,
        contexts=contexts,
        families=families,
        transports=transports,
        retrieval_inventories=retrieval_inventories,
        conflicts=conflicts,
        triggers=triggers,
        repair_packages=repair_packages,
        mutations=mutations,
        distinction_audits=distinction_audits,
        provenances=provenances,
        provenance_audits=provenance_audits,
        residuals=residuals,
        ledger_entries=ledger_entries,
        dispositions=dispositions,
        disposition_inventories=disposition_inventories,
        repair_candidates=repair_candidates,
        coarsening_candidates=coarsening_candidates,
        unresolved_candidates=unresolved_candidates,
        outcome_inventories=outcome_inventories,
        silent_candidates=silent_candidates,
        provenance_defect_candidates=provenance_defect_candidates,
        reconsolidation_claims=reconsolidation_claims,
        status_records=status_records,
        formation_registry=formation_registry,
        transport_registry=transport_registry,
        record_quotient_links=frozenset(record_quotient_links),
        unsupported_pairs=unsupported_pairs,
        f9_registry=f9_registry,
        coarsening_install_registry=frozenset(coarsening_install_registry),
        strata=tuple(strata),
    )


def _status_rows(fixture: Fixture) -> dict[str, StatusRow]:
    rows: dict[str, StatusRow] = {}
    for claim_name in fixture.reconsolidation_claims:
        matching_records = tuple(
            record
            for record in fixture.status_records.values()
            if reconsolidation_status_record_matches_claim(
                fixture.reconsolidation_claims[claim_name], record
            )
        )
        if not matching_records:
            continue
        expected = matching_records[0].status
        observed, truths, record = classify_reconsolidation_status(fixture, claim_name)
        rows[claim_name] = StatusRow(
            claim_name, expected, observed, truths, record
        )
    return rows


def _stratum_counts(
    fixture: Fixture,
) -> dict[str, dict[ReconsolidationStatus, int]]:
    counts = {
        "loose": {status: 0 for status in STATUS_PRIORITY},
        "tight": {status: 0 for status in STATUS_PRIORITY},
    }
    for episode in fixture.strata:
        status, _, _ = classify_reconsolidation_status(fixture, episode.claim_name)
        stratum = "loose" if episode.budget.exposure_budget == F(3) else "tight"
        if status in counts[stratum]:
            counts[stratum][status] += 1
    return counts


def _control_rows(fixture: Fixture) -> dict[str, ControlRow]:
    bad_checks = retrieval_inventory_checks(
        fixture, fixture.retrieval_inventories["inventory_bad_same_context"]
    )
    bad_isolated = (
        bad_checks["completeForClaim"]
        and bad_checks["soundForClaim"]
        and bad_checks["everyContextCovered"]
        and not bad_checks["transportSingleValuedPerContext"]
        and not complete_retrieval_transport_inventory(
            fixture, fixture.retrieval_inventories["inventory_bad_same_context"]
        )
    )

    clear_claim = fixture.reconsolidation_claims[
        "ctrl_no_conflict_after_transport"
    ]
    clear_inventory = fixture.retrieval_inventories["inventory_clear"]
    clear_delta = delta_set(clear_claim.transport_record, clear_claim.claim_record)
    no_conflict = (
        context_dependent_retrieval(fixture, clear_inventory)
        and clear_delta == frozenset()
        and not _matching_triggers(fixture, clear_claim)
    )

    other_claim = fixture.reconsolidation_claims["ctrl_conflict_for_other_claim"]
    borrowed_conflict = fixture.conflicts["conflict_repair"]
    borrowed_link = (
        borrowed_conflict.source_record == other_claim.source_record
        and borrowed_conflict.transport_record == other_claim.transport_record
        and borrowed_conflict.claim_record == other_claim.claim_record
    )
    other_delta = delta_set(other_claim.transport_record, other_claim.claim_record)
    other_control = (
        not borrowed_link
        and other_delta == frozenset()
        and not _matching_triggers(fixture, other_claim)
    )

    home_status, home_truths, _ = classify_reconsolidation_status(
        fixture, "scope_home"
    )
    shift_status, shift_truths, _ = classify_reconsolidation_status(
        fixture, "scope_shift"
    )
    scope_control = (
        home_status is ReconsolidationStatus.record_repaired
        and shift_status is ReconsolidationStatus.statused_unresolved
        and sum(home_truths.values()) == 1
        and sum(shift_truths.values()) == 1
        and fixture.reconsolidation_claims["scope_home"]
        != fixture.reconsolidation_claims["scope_shift"]
    )

    counts = _stratum_counts(fixture)
    loose_repair = counts["loose"][ReconsolidationStatus.record_repaired]
    tight_repair = counts["tight"][ReconsolidationStatus.record_repaired]
    loose_coarsen = counts["loose"][ReconsolidationStatus.record_coarsened]
    tight_coarsen = counts["tight"][ReconsolidationStatus.record_coarsened]
    loose_unresolved = counts["loose"][ReconsolidationStatus.statused_unresolved]
    tight_unresolved = counts["tight"][ReconsolidationStatus.statused_unresolved]
    strata_control = (
        (loose_repair, tight_repair) == (6, 1)
        and (loose_coarsen, tight_coarsen) == (1, 6)
        and (loose_unresolved, tight_unresolved) == (1, 1)
    )

    return {
        "ctrl_transport_single_valued_same_context": ControlRow(
            "ctrl_transport_single_valued_same_context",
            "complete=true; sound=true; covered=true; single_valued=false; inventory rejected",
            "complete={completeForClaim}; sound={soundForClaim}; covered={everyContextCovered}; single_valued={transportSingleValuedPerContext}; inventory={inventory}".format(
                **bad_checks,
                inventory=complete_retrieval_transport_inventory(
                    fixture,
                    fixture.retrieval_inventories["inventory_bad_same_context"],
                ),
            ).lower(),
            bad_isolated,
        ),
        "ctrl_no_conflict_after_transport": ControlRow(
            "ctrl_no_conflict_after_transport",
            "context_dependent=true; DeltaSet={}; trigger/status absent",
            f"context_dependent={context_dependent_retrieval(fixture, clear_inventory)}; DeltaSet={sorted(map(sorted, clear_delta))}; trigger_count={len(_matching_triggers(fixture, clear_claim))}",
            no_conflict,
        ),
        "ctrl_conflict_for_other_claim": ControlRow(
            "ctrl_conflict_for_other_claim",
            "borrowed conflict link=false; own DeltaSet={}; trigger/status absent",
            f"borrowed_link={borrowed_link}; DeltaSet={sorted(map(sorted, other_delta))}; trigger_count={len(_matching_triggers(fixture, other_claim))}",
            other_control,
        ),
        "ctrl_per_retrieval_claim_scoping": ControlRow(
            "ctrl_per_retrieval_claim_scoping",
            "home=record_repaired; shift=statused_unresolved; both exactly one",
            f"home={home_status.value}; shift={shift_status.value}; home_truths={sum(home_truths.values())}; shift_truths={sum(shift_truths.values())}",
            scope_control,
        ),
        "strata_budget_memory_fate_direction": ControlRow(
            "strata_budget_memory_fate_direction",
            "repair loose/tight=6/1; coarsened loose/tight=1/6; unresolved=1/1",
            f"repair={loose_repair}/{tight_repair}; coarsened={loose_coarsen}/{tight_coarsen}; unresolved={loose_unresolved}/{tight_unresolved}",
            strata_control,
        ),
    }


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    comparisons: list[Comparison] = []
    for name in REGISTERED_COMPARISON_ORDER:
        if name.endswith(".status"):
            row = results.rows[name.removesuffix(".status")]
            comparisons.append(
                Comparison(name, row.passed, row.observed.value, row.expected.value)
            )
        else:
            control = results.controls[name]
            comparisons.append(
                Comparison(
                    name,
                    control.passed_control,
                    control.observed,
                    control.expected,
                )
            )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture, rows: dict[str, StatusRow]) -> bool:
    return all(
        row.status_record is not None
        and reconsolidation_status_occurrence_for(
            fixture.reconsolidation_claims[name], row.status_record
        )
        and complete_reconsolidation_status(fixture, name)
        for name, row in rows.items()
    )


def _no_hardcoded_status_discipline(results: SweepResults) -> bool:
    return all(
        row.observed is not ReconsolidationStatus.unclassified
        and sum(row.truths.values()) == 1
        and row.truths[row.observed]
        for row in results.rows.values()
    ) and all(control.passed_control for control in results.controls.values())


def run_e14_reconsolidation_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = _status_rows(fixture)
    controls = _control_rows(fixture)
    preliminary = SweepResults(
        rows=rows,
        controls=controls,
        comparisons=(),
        actual_scope_discipline=_actual_scope_discipline(fixture, rows),
        no_hardcoded_status_discipline=False,
    )
    checked = replace(
        preliminary,
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(preliminary),
    )
    return replace(checked, comparisons=_comparisons(checked))


def format_results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E14 Reconsolidation Sweep Results",
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
    results = run_e14_reconsolidation_sweep()
    path.write_text(format_results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    passed = sum(comparison.passed for comparison in results.comparisons)
    total = len(results.comparisons)
    print(f"E14 reconsolidation sweep: {passed}/{total} comparisons PASS")
    for comparison in results.comparisons:
        verdict = "PASS" if comparison.passed else "FAIL"
        print(
            f"{verdict}: {comparison.name}: "
            f"observed={comparison.observed} expected={comparison.expected}"
        )


if __name__ == "__main__":
    main()
