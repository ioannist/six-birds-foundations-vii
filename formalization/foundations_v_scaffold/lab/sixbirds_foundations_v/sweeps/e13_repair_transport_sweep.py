"""E13 repair-transport sweep against the pre-registered predictions.

The fixed fixture is specified in
``formalization/notes/sweeps/E13_repair_transport_predictions.md``.  This
module mirrors the Lean status apparatus in
``SixBirdsFoundationsV.Laws.E13RepairTransport``: all status labels are
computed from two-carrier records, paid bridge evidence, target-owned Delta
reductions, shared classifier comparators, and priority-normalized cases.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
from pathlib import Path

from sixbirds_foundations_v.carried_records import FineSourceTag, carried_source


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E13_repair_transport_results.md"
)

REGISTERED_COMPARISON_ORDER = (
    "claim_comm_clean.status",
    "claim_teach_absent_capacity.status",
    "claim_force_null.status",
    "claim_symbol_stable.status",
    "claim_scaffolded_no_capacity.status",
    "claim_primed_no_capacity.status",
    "claim_influence_different_class.status",
    "reject_unpaid_bridge.status",
    "reject_uncarried_target_repair.status",
    "reject_role_preservation_failure.status",
    "reject_symbol_context_instability.status",
    "reject_symbol_role_drift.status",
    "reject_saturation_relabel.status",
    "reject_parameter_channel_only.status",
    "reject_flow_crossing_no_bridge.status",
    "ctrl_shared_comparator_bundle_nontrivial",
    "ctrl_transport_claim_kind_scoping",
    "ctrl_claim_independence",
    "ctrl_falsifier_claim_linkage",
)


class TransportClaimKind(str, Enum):
    communication = "communication"
    teaching = "teaching"
    symbol = "symbol"


class RepairTransportStatus(str, Enum):
    coercion_null = "coercion_null"
    symbolic = "symbolic"
    taught = "taught"
    communicated = "communicated"
    scaffolded_or_primed = "scaffolded_or_primed"
    influence_only = "influence_only"
    transport_rejected = "transport_rejected"
    unclassified = "unclassified"


class ResponseMode(str, Enum):
    observed_free_response = "observed_free_response"
    fully_forced_response = "fully_forced_response"
    scaffolded_response = "scaffolded_response"
    primed_response = "primed_response"


@dataclass(frozen=True)
class Carrier:
    name: str
    states: tuple[str, ...]

    def supp_k(self, source: str, target: str) -> bool:
        if source not in self.states or target not in self.states:
            return False
        return self.states[(self.states.index(source) + 1) % len(self.states)] == target


@dataclass(frozen=True)
class ChallengeClassRecord:
    name: str
    challenge_id: int
    taxonomy_id: int


@dataclass(frozen=True)
class RepairRoleRecord:
    name: str
    role_id: int
    challenge_class: str
    package_kind: int = 0


@dataclass(frozen=True)
class TransportTokenRecord:
    name: str
    source_carrier: str
    target_carrier: str
    emitted_for: str
    source_package_ref: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class SourceRepairPackageRecord:
    name: str
    source_challenge: str
    role_record: str
    emitted_token: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class MoveRecord:
    name: str


@dataclass(frozen=True)
class TargetRepairRecord:
    name: str
    receipt_token: str
    target_challenge: str
    induced_move: str
    role_record: str
    pre_splits: frozenset[str]
    post_splits: frozenset[str]
    q_after_installed_move: str
    carried: bool
    lawful: bool
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class BridgeChannelRecord:
    name: str


@dataclass(frozen=True)
class InterCarrierBridgeRecord:
    name: str
    bridge_id: int
    source_carrier: str
    target_carrier: str
    channel_record: str
    carried_by_a: bool = True
    carried_by_b: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class LedgerEntry:
    name: str
    bridge_ref: int
    amount: Fraction
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class BridgeDefectRecord:
    name: str
    bridge_ref: int
    cost: Fraction
    source_ledger_entry: str
    target_ledger_entry: str


@dataclass(frozen=True)
class InterfaceAccessRecord:
    name: str
    bridge_ref: str
    taxonomy_ref: str
    side: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class TaxonomyRecord:
    name: str
    taxonomy_id: int
    class_records: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ForceScheduleRecord:
    name: str
    force_level: int
    aid_present: bool
    cue_only: bool


@dataclass(frozen=True)
class FreeResponseOpportunityRecord:
    name: str


@dataclass(frozen=True)
class FreeResponseCensusRecord:
    name: str
    interaction: str
    force_schedule: str
    opportunities: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class InteractionForcingRecord:
    name: str
    token: str
    target_carrier: str
    response_mode: ResponseMode
    force_schedule: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class AAbsenceProbeSchedule:
    name: str
    challenge_class: str
    probe_times: tuple[int, ...]
    a_present: dict[int, bool]
    bridge_open: dict[int, bool]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ContextReadoutRecord:
    name: str


@dataclass(frozen=True)
class TransportContextRecord:
    name: str
    challenge_class: str
    context_readout: str


@dataclass(frozen=True)
class ContextFamilyRecord:
    name: str
    contexts: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class BRoleStateRecord:
    name: str
    active_roles_by_family: dict[str, frozenset[str]]
    context_family_ref: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ContextualRepairReactivationRecord:
    name: str
    token: str
    source_package: str
    bridge: str
    context: str
    target_repair: str


@dataclass(frozen=True)
class TransportClaimRef:
    name: str
    kind: TransportClaimKind
    token: str
    source_package: str
    bridge: str
    target_class: str | None = None
    family: str | None = None


@dataclass(frozen=True)
class RepairTransportStatusRecord:
    name: str
    claim_kind: TransportClaimKind
    token_record: str
    source_package_record: str
    target_repair_record: str | None
    context_family_record: str | None
    forcing_record: str | None
    bridge_record: str | None
    status: RepairTransportStatus
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class RepairTransportClassifierContext:
    taxonomy: str

    def bridge_discharges(
        self,
        defect: BridgeDefectRecord,
        source_entry: LedgerEntry,
        target_entry: LedgerEntry,
    ) -> bool:
        return (
            source_entry.bridge_ref == defect.bridge_ref
            and target_entry.bridge_ref == defect.bridge_ref
            and source_entry.amount + target_entry.amount >= defect.cost
        )

    def same_class(self, fixture: Fixture, source_class: str, target_class: str) -> bool:
        source = fixture.challenge_classes[source_class]
        target = fixture.challenge_classes[target_class]
        return (
            source.taxonomy_id == target.taxonomy_id
            and source.challenge_id == target.challenge_id
        )

    def role_preserves(
        self,
        fixture: Fixture,
        source_package_name: str,
        target_repair_name: str,
    ) -> bool:
        package = fixture.source_packages[source_package_name]
        target = fixture.target_repairs[target_repair_name]
        source_role = fixture.roles[package.role_record]
        target_role = fixture.roles[target.role_record]
        return (
            source_role.role_id == target_role.role_id
            and source_role.challenge_class == package.source_challenge
            and target_role.challenge_class == target.target_challenge
        )

    def role_active_before(
        self,
        state: BRoleStateRecord,
        role_name: str,
        family_name: str,
    ) -> bool:
        return role_name in state.active_roles_by_family.get(family_name, frozenset())

    def role_active_after(
        self,
        state: BRoleStateRecord,
        role_name: str,
        family_name: str,
    ) -> bool:
        return role_name in state.active_roles_by_family.get(family_name, frozenset())

    def force_mode(
        self,
        schedule: ForceScheduleRecord,
        opportunities: tuple[str, ...],
    ) -> ResponseMode:
        if not opportunities and schedule.force_level == 1:
            return ResponseMode.fully_forced_response
        if opportunities and schedule.force_level == 0 and schedule.aid_present:
            return ResponseMode.scaffolded_response
        if opportunities and schedule.force_level == 0 and schedule.cue_only:
            return ResponseMode.primed_response
        if opportunities and schedule.force_level == 0:
            return ResponseMode.observed_free_response
        return ResponseMode.observed_free_response

    def quotient_installed_by_move(self, target_repair: TargetRepairRecord) -> bool:
        return target_repair.q_after_installed_move == target_repair.induced_move


@dataclass(frozen=True)
class Fixture:
    carrier_a: Carrier
    carrier_b: Carrier
    ctx: RepairTransportClassifierContext
    challenge_classes: dict[str, ChallengeClassRecord]
    roles: dict[str, RepairRoleRecord]
    tokens: dict[str, TransportTokenRecord]
    source_packages: dict[str, SourceRepairPackageRecord]
    moves: dict[str, MoveRecord]
    target_repairs: dict[str, TargetRepairRecord]
    bridges: dict[str, InterCarrierBridgeRecord]
    defects: dict[str, BridgeDefectRecord]
    source_ledgers: dict[str, LedgerEntry]
    target_ledgers: dict[str, LedgerEntry]
    access_records: dict[str, InterfaceAccessRecord]
    taxonomies: dict[str, TaxonomyRecord]
    force_schedules: dict[str, ForceScheduleRecord]
    opportunities: dict[str, FreeResponseOpportunityRecord]
    censuses: dict[str, FreeResponseCensusRecord]
    interactions: dict[str, InteractionForcingRecord]
    absence_schedules: dict[str, AAbsenceProbeSchedule]
    context_readouts: dict[str, ContextReadoutRecord]
    contexts: dict[str, TransportContextRecord]
    families: dict[str, ContextFamilyRecord]
    role_states: dict[str, BRoleStateRecord]
    reactivations: dict[str, ContextualRepairReactivationRecord]
    claims: dict[str, TransportClaimRef]
    status_records: dict[str, RepairTransportStatusRecord]
    forced_delta_pairs: dict[str, tuple[frozenset[str], frozenset[str]]]
    flow_crossings: frozenset[str]


@dataclass(frozen=True)
class StatusRow:
    name: str
    claim_name: str
    expected: RepairTransportStatus
    observed: RepairTransportStatus
    truths: dict[str, bool]
    status_record: RepairTransportStatusRecord | None

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


def _carried(
    source_tag: FineSourceTag = FineSourceTag.committed_state,
    generated_by_s: bool = True,
    in_scope: bool = True,
) -> bool:
    return carried_source(source_tag, generated_by_s, in_scope)


def _record_carried(record: object) -> bool:
    return bool(
        getattr(record, "carried", True)
        and _carried(
            getattr(record, "source_tag", FineSourceTag.committed_state),
            getattr(record, "generated_by_s", True),
            getattr(record, "in_scope", True),
        )
    )


def _target_repair_carried(target: TargetRepairRecord) -> bool:
    return target.carried and _record_carried(target)


def bridge_defects_paid(fixture: Fixture, bridge_name: str) -> bool:
    bridge = fixture.bridges[bridge_name]
    if not (
        bridge.carried_by_a
        and bridge.carried_by_b
        and _record_carried(bridge)
    ):
        return False
    for defect in fixture.defects.values():
        if defect.bridge_ref != bridge.bridge_id:
            continue
        source = fixture.source_ledgers.get(defect.source_ledger_entry)
        target = fixture.target_ledgers.get(defect.target_ledger_entry)
        if source is None or target is None:
            continue
        if not (_record_carried(source) and _record_carried(target)):
            continue
        if fixture.ctx.bridge_discharges(defect, source, target):
            return True
    return False


def inter_carrier_bridge(fixture: Fixture, bridge_name: str) -> bool:
    bridge = fixture.bridges[bridge_name]
    return (
        bridge.source_carrier == fixture.carrier_a.name
        and bridge.target_carrier == fixture.carrier_b.name
        and bridge_defects_paid(fixture, bridge_name)
    )


def interface_mediation_certified(fixture: Fixture, bridge_name: str) -> bool:
    if not inter_carrier_bridge(fixture, bridge_name):
        return False
    taxonomy = fixture.ctx.taxonomy
    has_source = any(
        access.side == "A"
        and access.bridge_ref == bridge_name
        and access.taxonomy_ref == taxonomy
        and _record_carried(access)
        for access in fixture.access_records.values()
    )
    has_target = any(
        access.side == "B"
        and access.bridge_ref == bridge_name
        and access.taxonomy_ref == taxonomy
        and _record_carried(access)
        for access in fixture.access_records.values()
    )
    return has_source and has_target and _record_carried(fixture.taxonomies[taxonomy])


def same_transport_challenge_class(
    fixture: Fixture,
    source_class: str,
    target_class: str,
) -> bool:
    taxonomy = fixture.taxonomies[fixture.ctx.taxonomy]
    return (
        source_class in taxonomy.class_records
        and target_class in taxonomy.class_records
        and fixture.ctx.same_class(fixture, source_class, target_class)
    )


def transport_delta_reduction(
    fixture: Fixture,
    target_repair_name: str,
) -> bool:
    target = fixture.target_repairs[target_repair_name]
    return (
        fixture.ctx.quotient_installed_by_move(target)
        and target.post_splits < target.pre_splits
    )


def role_preserving_transport(
    fixture: Fixture,
    source_package_name: str,
    target_repair_name: str,
) -> bool:
    return fixture.ctx.role_preserves(fixture, source_package_name, target_repair_name)


def induced_b_repair(
    fixture: Fixture,
    bridge_name: str,
    source_package_name: str,
    token_name: str,
    target_repair_name: str,
) -> bool:
    bridge = fixture.bridges[bridge_name]
    package = fixture.source_packages[source_package_name]
    token = fixture.tokens[token_name]
    target = fixture.target_repairs[target_repair_name]
    return (
        package.emitted_token == token_name
        and target.receipt_token == token_name
        and bridge.source_carrier == token.source_carrier
        and bridge.target_carrier == token.target_carrier
        and same_transport_challenge_class(
            fixture,
            package.source_challenge,
            target.target_challenge,
        )
        and _target_repair_carried(target)
        and target.lawful
        and transport_delta_reduction(fixture, target_repair_name)
    )


def communication_transport_evidence(
    fixture: Fixture,
    bridge_name: str,
    source_package_name: str,
    token_name: str,
    target_repair_name: str,
) -> bool:
    return (
        inter_carrier_bridge(fixture, bridge_name)
        and induced_b_repair(
            fixture,
            bridge_name,
            source_package_name,
            token_name,
            target_repair_name,
        )
        and interface_mediation_certified(fixture, bridge_name)
        and role_preserving_transport(fixture, source_package_name, target_repair_name)
        and _record_carried(fixture.source_packages[source_package_name])
        and _record_carried(fixture.tokens[token_name])
    )


def different_class_influence_evidence(
    fixture: Fixture,
    bridge_name: str,
    source_package_name: str,
    token_name: str,
    target_repair_name: str,
) -> bool:
    bridge = fixture.bridges[bridge_name]
    package = fixture.source_packages[source_package_name]
    token = fixture.tokens[token_name]
    target = fixture.target_repairs[target_repair_name]
    return (
        inter_carrier_bridge(fixture, bridge_name)
        and package.emitted_token == token_name
        and target.receipt_token == token_name
        and bridge.source_carrier == token.source_carrier
        and bridge.target_carrier == token.target_carrier
        and _record_carried(package)
        and _record_carried(token)
        and _target_repair_carried(target)
        and target.lawful
        and transport_delta_reduction(fixture, target_repair_name)
        and not same_transport_challenge_class(
            fixture,
            package.source_challenge,
            target.target_challenge,
        )
    )


def b_committed_repair_in_a_absence(
    fixture: Fixture,
    schedule_name: str,
    target_repair_name: str,
) -> bool:
    schedule = fixture.absence_schedules[schedule_name]
    target = fixture.target_repairs[target_repair_name]
    return (
        bool(schedule.probe_times)
        and _record_carried(schedule)
        and all(not schedule.a_present[t] and not schedule.bridge_open[t] for t in schedule.probe_times)
        and same_transport_challenge_class(
            fixture,
            schedule.challenge_class,
            target.target_challenge,
        )
        and 5 in schedule.probe_times
        and _target_repair_carried(target)
        and target.source_tag is FineSourceTag.committed_state
        and target.generated_by_s
        and target.in_scope
        and target.lawful
        and transport_delta_reduction(fixture, target_repair_name)
    )


def teaching_capacity_evidence(
    fixture: Fixture,
    bridge_name: str,
    source_package_name: str,
    token_name: str,
    initial_repair_name: str,
    schedule_name: str,
    subsequent_repair_name: str,
) -> bool:
    package = fixture.source_packages[source_package_name]
    initial = fixture.target_repairs[initial_repair_name]
    subsequent = fixture.target_repairs[subsequent_repair_name]
    return (
        communication_transport_evidence(
            fixture,
            bridge_name,
            source_package_name,
            token_name,
            initial_repair_name,
        )
        and same_transport_challenge_class(
            fixture,
            package.source_challenge,
            initial.target_challenge,
        )
        and b_committed_repair_in_a_absence(fixture, schedule_name, subsequent_repair_name)
        and same_transport_challenge_class(
            fixture,
            package.source_challenge,
            subsequent.target_challenge,
        )
        and fixture.roles[subsequent.role_record].role_id
        == fixture.roles[package.role_record].role_id
    )


def find_teaching_capacity_evidence(
    fixture: Fixture,
    bridge_name: str,
    source_package_name: str,
    token_name: str,
    initial_repair_name: str,
) -> bool:
    package = fixture.source_packages[source_package_name]
    for schedule_name in fixture.absence_schedules:
        for subsequent_name, subsequent in fixture.target_repairs.items():
            if subsequent_name == initial_repair_name:
                continue
            if subsequent.receipt_token != token_name:
                continue
            if not same_transport_challenge_class(
                fixture,
                package.source_challenge,
                subsequent.target_challenge,
            ):
                continue
            if fixture.roles[subsequent.role_record].role_id != fixture.roles[package.role_record].role_id:
                continue
            if teaching_capacity_evidence(
                fixture,
                bridge_name,
                source_package_name,
                token_name,
                initial_repair_name,
                schedule_name,
                subsequent_name,
            ):
                return True
    return False


def computed_response_mode(fixture: Fixture, interaction_name: str) -> ResponseMode:
    interaction = fixture.interactions[interaction_name]
    census = next(
        c for c in fixture.censuses.values() if c.interaction == interaction_name
    )
    schedule = fixture.force_schedules[interaction.force_schedule]
    return fixture.ctx.force_mode(schedule, census.opportunities)


def fully_forced_interaction(fixture: Fixture, interaction_name: str) -> bool:
    interaction = fixture.interactions[interaction_name]
    census = next(
        (c for c in fixture.censuses.values() if c.interaction == interaction_name),
        None,
    )
    if census is None:
        return False
    computed = computed_response_mode(fixture, interaction_name)
    return (
        _record_carried(interaction)
        and _record_carried(census)
        and census.force_schedule == interaction.force_schedule
        and computed is interaction.response_mode
        and interaction.response_mode is ResponseMode.fully_forced_response
        and census.opportunities == ()
    )


def no_b_committed_transported_repair(fixture: Fixture, token_name: str) -> bool:
    return not any(
        target.receipt_token == token_name
        and target.source_tag is FineSourceTag.committed_state
        and _target_repair_carried(target)
        for target in fixture.target_repairs.values()
    )


def coercion_null_certified(
    fixture: Fixture,
    interaction_name: str,
    token_name: str,
) -> bool:
    interaction = fixture.interactions[interaction_name]
    before, after = fixture.forced_delta_pairs.get(token_name, (frozenset(), frozenset()))
    return (
        fully_forced_interaction(fixture, interaction_name)
        and interaction.token == token_name
        and no_b_committed_transported_repair(fixture, token_name)
        and before == after
    )


def scaffolded_or_primed_interaction(
    fixture: Fixture,
    interaction_name: str,
) -> bool:
    interaction = fixture.interactions[interaction_name]
    census = next(
        (c for c in fixture.censuses.values() if c.interaction == interaction_name),
        None,
    )
    if census is None:
        return False
    computed = computed_response_mode(fixture, interaction_name)
    return (
        _record_carried(interaction)
        and _record_carried(census)
        and census.force_schedule == interaction.force_schedule
        and computed is interaction.response_mode
        and interaction.response_mode
        in {ResponseMode.scaffolded_response, ResponseMode.primed_response}
    )


def no_a_absent_b_committed_capacity(
    fixture: Fixture,
    source_package_name: str,
    token_name: str,
) -> bool:
    package = fixture.source_packages[source_package_name]
    for schedule_name in fixture.absence_schedules:
        for target_name, target in fixture.target_repairs.items():
            if target.receipt_token != token_name:
                continue
            if not same_transport_challenge_class(
                fixture,
                package.source_challenge,
                target.target_challenge,
            ):
                continue
            if fixture.roles[target.role_record].role_id != fixture.roles[package.role_record].role_id:
                continue
            if b_committed_repair_in_a_absence(fixture, schedule_name, target_name):
                return False
    return True


def scaffolding_or_priming_witness(
    fixture: Fixture,
    interaction_name: str,
    token_name: str,
    source_package_name: str,
    claim_class_name: str,
) -> bool:
    if not scaffolded_or_primed_interaction(fixture, interaction_name):
        return False
    interaction = fixture.interactions[interaction_name]
    package = fixture.source_packages[source_package_name]
    behavior_improves = any(
        target.receipt_token == token_name
        and same_transport_challenge_class(
            fixture,
            claim_class_name,
            target.target_challenge,
        )
        and transport_delta_reduction(fixture, target.name)
        for target in fixture.target_repairs.values()
    )
    return (
        interaction.token == token_name
        and same_transport_challenge_class(
            fixture,
            package.source_challenge,
            claim_class_name,
        )
        and behavior_improves
        and no_a_absent_b_committed_capacity(fixture, source_package_name, token_name)
    )


def context_family_declared(fixture: Fixture, family_name: str) -> bool:
    family = fixture.families[family_name]
    return len(family.contexts) >= 2 and _record_carried(family)


def contextual_repair_reactivation(
    fixture: Fixture,
    reactivation_name: str,
    bridge_name: str,
    token_name: str,
    source_package_name: str,
    context_name: str,
) -> bool:
    reactivation = fixture.reactivations.get(reactivation_name)
    if reactivation is None:
        return False
    package = fixture.source_packages[source_package_name]
    token = fixture.tokens[token_name]
    context = fixture.contexts[context_name]
    target = fixture.target_repairs[reactivation.target_repair]
    return (
        reactivation.token == token_name
        and reactivation.source_package == source_package_name
        and reactivation.bridge == bridge_name
        and reactivation.context == context_name
        and inter_carrier_bridge(fixture, bridge_name)
        and interface_mediation_certified(fixture, bridge_name)
        and same_transport_challenge_class(
            fixture,
            package.source_challenge,
            context.challenge_class,
        )
        and package.emitted_token == token_name
        and _record_carried(package)
        and _record_carried(token)
        and target.receipt_token == token_name
        and _target_repair_carried(target)
        and target.lawful
        and role_preserving_transport(fixture, source_package_name, reactivation.target_repair)
        and transport_delta_reduction(fixture, reactivation.target_repair)
    )


def current_structure_already_carries_role(
    fixture: Fixture,
    source_package_name: str,
    family_name: str,
) -> bool:
    package = fixture.source_packages[source_package_name]
    pre = fixture.role_states.get(f"pre_{source_package_name}")
    post = fixture.role_states.get(f"post_{source_package_name}")
    if pre is None or post is None:
        return False
    return (
        _record_carried(pre)
        and _record_carried(post)
        and pre.context_family_ref == family_name
        and post.context_family_ref == family_name
        and fixture.ctx.role_active_before(pre, package.role_record, family_name)
        and fixture.ctx.role_active_after(post, package.role_record, family_name)
    )


def symbol_saturation_strict(
    fixture: Fixture,
    bridge_name: str,
    token_name: str,
    source_package_name: str,
    family_name: str,
) -> bool:
    family = fixture.families[family_name]
    genuine = any(
        contextual_repair_reactivation(
            fixture,
            reactivation_name,
            bridge_name,
            token_name,
            source_package_name,
            context,
        )
        for context in family.contexts
        for reactivation_name in fixture.reactivations
    )
    return (
        not current_structure_already_carries_role(
            fixture,
            source_package_name,
            family_name,
        )
        and genuine
    )


def symbolic_repair_evidence(
    fixture: Fixture,
    bridge_name: str,
    token_name: str,
    source_package_name: str,
    family_name: str,
) -> bool:
    if not context_family_declared(fixture, family_name):
        return False
    family = fixture.families[family_name]
    reactivated_targets: list[TargetRepairRecord] = []
    for context in family.contexts:
        valid_for_context = [
            fixture.target_repairs[reactivation.target_repair]
            for reactivation_name, reactivation in fixture.reactivations.items()
            if contextual_repair_reactivation(
                fixture,
                reactivation_name,
                bridge_name,
                token_name,
                source_package_name,
                context,
            )
        ]
        if not valid_for_context:
            return False
        reactivated_targets.append(valid_for_context[0])
    role_ids = {
        fixture.roles[target.role_record].role_id for target in reactivated_targets
    }
    return (
        len(role_ids) == 1
        and symbol_saturation_strict(
            fixture,
            bridge_name,
            token_name,
            source_package_name,
            family_name,
        )
    )


def transport_status_record_matches_claim(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    if not (
        record.claim_kind is claim.kind
        and record.token_record == claim.token
        and record.source_package_record == claim.source_package
        and record.bridge_record == claim.bridge
    ):
        return False
    if claim.kind is TransportClaimKind.communication:
        if record.context_family_record is not None or record.target_repair_record is None:
            return False
        target = fixture.target_repairs[record.target_repair_record]
        return target.receipt_token == claim.token and target.target_challenge == claim.target_class
    if claim.kind is TransportClaimKind.teaching:
        if record.context_family_record is not None or record.target_repair_record is None:
            return False
        target = fixture.target_repairs[record.target_repair_record]
        return target.target_challenge == claim.target_class
    if claim.kind is TransportClaimKind.symbol:
        return (
            record.context_family_record == claim.family
            and record.target_repair_record is None
        )
    return False


def repair_transport_status_occurrence_for(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return transport_status_record_matches_claim(fixture, claim, record) and _record_carried(record)


def transport_claim_allows_scaffold_or_prime(claim: TransportClaimRef) -> bool:
    return claim.kind in {
        TransportClaimKind.communication,
        TransportClaimKind.teaching,
    }


def coercion_null_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and record.status is RepairTransportStatus.coercion_null
        and record.forcing_record is not None
        and fully_forced_interaction(fixture, record.forcing_record)
        and coercion_null_certified(fixture, record.forcing_record, record.token_record)
    )


def symbolic_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and not coercion_null_case(fixture, claim, record)
        and record.status is RepairTransportStatus.symbolic
        and claim.kind is TransportClaimKind.symbol
        and record.context_family_record == claim.family
        and claim.family is not None
        and symbolic_repair_evidence(
            fixture,
            claim.bridge,
            claim.token,
            claim.source_package,
            claim.family,
        )
    )


def taught_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    if not (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and not coercion_null_case(fixture, claim, record)
        and not symbolic_case(fixture, claim, record)
        and record.status is RepairTransportStatus.taught
        and claim.kind is TransportClaimKind.teaching
        and record.target_repair_record is not None
    ):
        return False
    return find_teaching_capacity_evidence(
        fixture,
        claim.bridge,
        claim.source_package,
        claim.token,
        record.target_repair_record,
    )


def communicated_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and not coercion_null_case(fixture, claim, record)
        and not symbolic_case(fixture, claim, record)
        and not taught_case(fixture, claim, record)
        and record.status is RepairTransportStatus.communicated
        and record.target_repair_record is not None
        and communication_transport_evidence(
            fixture,
            claim.bridge,
            claim.source_package,
            claim.token,
            record.target_repair_record,
        )
    )


def scaffolded_or_primed_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and not coercion_null_case(fixture, claim, record)
        and not symbolic_case(fixture, claim, record)
        and not taught_case(fixture, claim, record)
        and not communicated_case(fixture, claim, record)
        and record.status is RepairTransportStatus.scaffolded_or_primed
        and transport_claim_allows_scaffold_or_prime(claim)
        and record.forcing_record is not None
        and scaffolding_or_priming_witness(
            fixture,
            record.forcing_record,
            claim.token,
            claim.source_package,
            claim.target_class or fixture.source_packages[claim.source_package].source_challenge,
        )
    )


def influence_only_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and not coercion_null_case(fixture, claim, record)
        and not symbolic_case(fixture, claim, record)
        and not taught_case(fixture, claim, record)
        and not communicated_case(fixture, claim, record)
        and not scaffolded_or_primed_case(fixture, claim, record)
        and record.status is RepairTransportStatus.influence_only
        and record.target_repair_record is not None
        and different_class_influence_evidence(
            fixture,
            claim.bridge,
            claim.source_package,
            claim.token,
            record.target_repair_record,
        )
    )


def transport_rejected_case(
    fixture: Fixture,
    claim: TransportClaimRef,
    record: RepairTransportStatusRecord,
) -> bool:
    return (
        repair_transport_status_occurrence_for(fixture, claim, record)
        and not coercion_null_case(fixture, claim, record)
        and not symbolic_case(fixture, claim, record)
        and not taught_case(fixture, claim, record)
        and not communicated_case(fixture, claim, record)
        and not scaffolded_or_primed_case(fixture, claim, record)
        and not influence_only_case(fixture, claim, record)
        and record.status is RepairTransportStatus.transport_rejected
    )


CASE_FUNCTIONS = {
    "coercion_null": coercion_null_case,
    "symbolic": symbolic_case,
    "taught": taught_case,
    "communicated": communicated_case,
    "scaffolded_or_primed": scaffolded_or_primed_case,
    "influence_only": influence_only_case,
    "transport_rejected": transport_rejected_case,
}


def matching_records(
    fixture: Fixture,
    claim: TransportClaimRef,
) -> tuple[RepairTransportStatusRecord, ...]:
    return tuple(
        record
        for record in fixture.status_records.values()
        if repair_transport_status_occurrence_for(fixture, claim, record)
    )


def classify_repair_transport_status(
    fixture: Fixture,
    claim_name: str,
) -> tuple[RepairTransportStatus, dict[str, bool], RepairTransportStatusRecord | None]:
    claim = fixture.claims[claim_name]
    records = matching_records(fixture, claim)
    truths = {name: False for name in CASE_FUNCTIONS}
    for record in records:
        for name, fn in CASE_FUNCTIONS.items():
            if fn(fixture, claim, record):
                truths[name] = True
                return RepairTransportStatus(name), truths, record
    return RepairTransportStatus.unclassified, truths, records[0] if records else None


def complete_repair_transport_status(fixture: Fixture, claim_name: str) -> bool:
    claim = fixture.claims[claim_name]
    records = matching_records(fixture, claim)
    if not records:
        return False
    statuses = {record.status for record in records}
    if len(statuses) != 1:
        return False
    status, truths, _record = classify_repair_transport_status(fixture, claim_name)
    return status is not RepairTransportStatus.unclassified and sum(truths.values()) == 1


def same_class_falsifier_linked(
    fixture: Fixture,
    claim_name: str,
    bridge_name: str,
    source_package_name: str,
    token_name: str,
    target_repair_name: str,
) -> bool:
    claim = fixture.claims[claim_name]
    package = fixture.source_packages[source_package_name]
    return (
        different_class_influence_evidence(
            fixture,
            bridge_name,
            source_package_name,
            token_name,
            target_repair_name,
        )
        and claim
        == TransportClaimRef(
            name=claim.name,
            kind=TransportClaimKind.communication,
            token=token_name,
            source_package=source_package_name,
            bridge=bridge_name,
            target_class=package.source_challenge,
        )
    )


def coercion_null_falsifier_linked(
    fixture: Fixture,
    claim_name: str,
    token_name: str,
) -> bool:
    claim = fixture.claims[claim_name]
    return claim.kind in {TransportClaimKind.communication, TransportClaimKind.teaching} and claim.token == token_name


def scaffolding_falsifier_linked(
    fixture: Fixture,
    claim_name: str,
    token_name: str,
    source_package_name: str,
    bridge_name: str,
    claimed_class_name: str,
) -> bool:
    claim = fixture.claims[claim_name]
    return (
        claim
        == TransportClaimRef(
            name=claim.name,
            kind=TransportClaimKind.teaching,
            token=token_name,
            source_package=source_package_name,
            bridge=bridge_name,
            target_class=claimed_class_name,
        )
    )


def symbol_falsifier_linked(
    fixture: Fixture,
    claim_name: str,
    token_name: str,
    source_package_name: str,
    bridge_name: str,
    family_name: str,
) -> bool:
    claim = fixture.claims[claim_name]
    return (
        claim
        == TransportClaimRef(
            name=claim.name,
            kind=TransportClaimKind.symbol,
            token=token_name,
            source_package=source_package_name,
            bridge=bridge_name,
            family=family_name,
        )
    )


def build_fixture() -> Fixture:
    carrier_a = Carrier("carrier_A", ("A0", "A1", "A2", "A3"))
    carrier_b = Carrier("carrier_B", tuple(f"B{i}" for i in range(8)))
    ctx = RepairTransportClassifierContext(taxonomy="taxonomy_transport_v1")

    challenge_classes = {
        "C_navigation": ChallengeClassRecord("C_navigation", 1, 1),
        "C_power": ChallengeClassRecord("C_power", 2, 1),
        "C_language": ChallengeClassRecord("C_language", 3, 1),
    }
    roles = {
        "role_nav_filter": RepairRoleRecord("role_nav_filter", 10, "C_navigation"),
        "role_power_filter": RepairRoleRecord("role_power_filter", 20, "C_power"),
        "role_lang_handle": RepairRoleRecord("role_lang_handle", 30, "C_language"),
        "role_other_handle": RepairRoleRecord("role_other_handle", 31, "C_language"),
    }

    nav_rows = {
        "comm": "clean communication",
        "teach": "teaching",
        "force": "coercion-null",
        "scaffold": "scaffolding",
        "prime": "priming",
        "influence": "influence",
        "unpaid": "unpaid bridge rejection",
        "uncarried": "uncarried repair rejection",
        "role_drift": "role-preservation rejection",
        "parameter": "parameter-channel rejection",
        "flow": "flow-crossing rejection",
    }
    tokens = {
        f"tok_nav_{suffix}": TransportTokenRecord(
            f"tok_nav_{suffix}",
            "carrier_A",
            "carrier_B",
            "C_navigation",
            f"pkg_nav_{suffix}",
        )
        for suffix in nav_rows
    }
    tokens.update(
        {
            f"tok_symbol_{suffix}": TransportTokenRecord(
                f"tok_symbol_{suffix}",
                "carrier_A",
                "carrier_B",
                "C_language",
                f"pkg_lang_{suffix}",
            )
            for suffix in ("stable", "instability", "role_drift", "saturation")
        }
    )
    source_packages = {
        f"pkg_nav_{suffix}": SourceRepairPackageRecord(
            f"pkg_nav_{suffix}",
            "C_navigation",
            "role_nav_filter",
            f"tok_nav_{suffix}",
        )
        for suffix in nav_rows
    }
    source_packages.update(
        {
            f"pkg_lang_{suffix}": SourceRepairPackageRecord(
                f"pkg_lang_{suffix}",
                "C_language",
                "role_lang_handle",
                f"tok_symbol_{suffix}",
            )
            for suffix in ("stable", "instability", "role_drift", "saturation")
        }
    )

    moves = {
        name: MoveRecord(name)
        for name in (
            "mv_nav_clean",
            "mv_nav_teach_initial",
            "mv_nav_later",
            "mv_nav_scaffold",
            "mv_nav_prime",
            "mv_nav_force_placeholder",
            "mv_nav_unpaid",
            "mv_nav_parameter_stub",
            "mv_nav_flow_stub",
            "mv_power",
            "mv_nav_uncarried",
            "mv_nav_drift",
            "mv_symbol_c1",
            "mv_symbol_c2",
            "mv_symbol_c2_drift",
        )
    }
    target_repairs = {
        "repair_nav_clean": TargetRepairRecord(
            "repair_nav_clean",
            "tok_nav_comm",
            "C_navigation",
            "mv_nav_clean",
            "role_nav_filter",
            frozenset({"p01", "p02", "p03"}),
            frozenset({"p01"}),
            "mv_nav_clean",
            True,
            True,
        ),
        "repair_nav_teach_initial": TargetRepairRecord(
            "repair_nav_teach_initial",
            "tok_nav_teach",
            "C_navigation",
            "mv_nav_teach_initial",
            "role_nav_filter",
            frozenset({"p04", "p05", "p06"}),
            frozenset({"p04", "p05"}),
            "mv_nav_teach_initial",
            True,
            True,
        ),
        "repair_nav_later_capacity": TargetRepairRecord(
            "repair_nav_later_capacity",
            "tok_nav_teach",
            "C_navigation",
            "mv_nav_later",
            "role_nav_filter",
            frozenset({"p04", "p05"}),
            frozenset({"p04"}),
            "mv_nav_later",
            True,
            True,
        ),
        "repair_nav_scaffold_immediate": TargetRepairRecord(
            "repair_nav_scaffold_immediate",
            "tok_nav_scaffold",
            "C_navigation",
            "mv_nav_scaffold",
            "role_nav_filter",
            frozenset({"p07", "p08"}),
            frozenset({"p07"}),
            "mv_nav_scaffold",
            True,
            True,
            source_tag=FineSourceTag.audited_cell_records,
        ),
        "repair_nav_prime_immediate": TargetRepairRecord(
            "repair_nav_prime_immediate",
            "tok_nav_prime",
            "C_navigation",
            "mv_nav_prime",
            "role_nav_filter",
            frozenset({"p09", "p12"}),
            frozenset({"p09"}),
            "mv_nav_prime",
            True,
            True,
            source_tag=FineSourceTag.audited_cell_records,
        ),
        "repair_nav_force_placeholder": TargetRepairRecord(
            "repair_nav_force_placeholder",
            "tok_nav_force",
            "C_navigation",
            "mv_nav_force_placeholder",
            "role_nav_filter",
            frozenset(),
            frozenset(),
            "mv_nav_force_placeholder",
            False,
            False,
            source_tag=FineSourceTag.fallback,
            generated_by_s=False,
            in_scope=False,
        ),
        "repair_nav_unpaid": TargetRepairRecord(
            "repair_nav_unpaid",
            "tok_nav_unpaid",
            "C_navigation",
            "mv_nav_unpaid",
            "role_nav_filter",
            frozenset({"p13", "p14"}),
            frozenset({"p13"}),
            "mv_nav_unpaid",
            True,
            True,
        ),
        "repair_nav_parameter_stub": TargetRepairRecord(
            "repair_nav_parameter_stub",
            "tok_nav_parameter",
            "C_navigation",
            "mv_nav_parameter_stub",
            "role_nav_filter",
            frozenset(),
            frozenset(),
            "mv_nav_parameter_stub",
            False,
            False,
            source_tag=FineSourceTag.fallback,
            generated_by_s=False,
            in_scope=False,
        ),
        "repair_nav_flow_stub": TargetRepairRecord(
            "repair_nav_flow_stub",
            "tok_nav_flow",
            "C_navigation",
            "mv_nav_flow_stub",
            "role_nav_filter",
            frozenset(),
            frozenset(),
            "mv_nav_flow_stub",
            False,
            False,
            source_tag=FineSourceTag.fallback,
            generated_by_s=False,
            in_scope=False,
        ),
        "repair_power_influence": TargetRepairRecord(
            "repair_power_influence",
            "tok_nav_influence",
            "C_power",
            "mv_power",
            "role_power_filter",
            frozenset({"p10", "p11"}),
            frozenset({"p10"}),
            "mv_power",
            True,
            True,
        ),
        "repair_nav_uncarried": TargetRepairRecord(
            "repair_nav_uncarried",
            "tok_nav_uncarried",
            "C_navigation",
            "mv_nav_uncarried",
            "role_nav_filter",
            frozenset({"p20", "p21"}),
            frozenset({"p20"}),
            "mv_nav_uncarried",
            False,
            True,
        ),
        "repair_nav_role_drift": TargetRepairRecord(
            "repair_nav_role_drift",
            "tok_nav_role_drift",
            "C_navigation",
            "mv_nav_drift",
            "role_power_filter",
            frozenset({"p30", "p31"}),
            frozenset({"p30"}),
            "mv_nav_drift",
            True,
            True,
        ),
        "repair_symbol_ctx1": TargetRepairRecord(
            "repair_symbol_ctx1",
            "tok_symbol_stable",
            "C_language",
            "mv_symbol_c1",
            "role_lang_handle",
            frozenset({"s1", "s2"}),
            frozenset({"s1"}),
            "mv_symbol_c1",
            True,
            True,
        ),
        "repair_symbol_ctx2": TargetRepairRecord(
            "repair_symbol_ctx2",
            "tok_symbol_stable",
            "C_language",
            "mv_symbol_c2",
            "role_lang_handle",
            frozenset({"s3", "s4"}),
            frozenset({"s3"}),
            "mv_symbol_c2",
            True,
            True,
        ),
        "repair_symbol_ctx2_drift": TargetRepairRecord(
            "repair_symbol_ctx2_drift",
            "tok_symbol_role_drift",
            "C_language",
            "mv_symbol_c2_drift",
            "role_other_handle",
            frozenset({"s3", "s4"}),
            frozenset({"s3"}),
            "mv_symbol_c2_drift",
            True,
            True,
        ),
    }

    bridges = {
        "bridge_paid_ab": InterCarrierBridgeRecord(
            "bridge_paid_ab",
            10,
            "carrier_A",
            "carrier_B",
            "channel_ab_main",
        ),
        "bridge_unpaid_ab": InterCarrierBridgeRecord(
            "bridge_unpaid_ab",
            11,
            "carrier_A",
            "carrier_B",
            "channel_ab_unpaid",
        ),
        "bridge_flow_unlinked_ab": InterCarrierBridgeRecord(
            "bridge_flow_unlinked_ab",
            12,
            "carrier_A",
            "carrier_B",
            "channel_boundary_flow_only",
            carried_by_a=False,
            carried_by_b=False,
            source_tag=FineSourceTag.fallback,
            generated_by_s=False,
            in_scope=False,
        ),
    }
    source_ledgers = {
        "ledger_A_paid": LedgerEntry("ledger_A_paid", 10, F(3, 5)),
        "ledger_A_unpaid": LedgerEntry("ledger_A_unpaid", 11, F(1, 5)),
    }
    target_ledgers = {
        "ledger_B_paid": LedgerEntry("ledger_B_paid", 10, F(2, 5)),
        "ledger_B_unpaid": LedgerEntry("ledger_B_unpaid", 11, F(1, 5)),
    }
    defects = {
        "def_paid_ab": BridgeDefectRecord(
            "def_paid_ab",
            10,
            F(1),
            "ledger_A_paid",
            "ledger_B_paid",
        ),
        "def_unpaid_ab": BridgeDefectRecord(
            "def_unpaid_ab",
            11,
            F(1),
            "ledger_A_unpaid",
            "ledger_B_unpaid",
        ),
    }
    access_records = {
        "access_A_paid": InterfaceAccessRecord(
            "access_A_paid",
            "bridge_paid_ab",
            "taxonomy_transport_v1",
            "A",
        ),
        "access_B_paid": InterfaceAccessRecord(
            "access_B_paid",
            "bridge_paid_ab",
            "taxonomy_transport_v1",
            "B",
        ),
    }
    taxonomies = {
        "taxonomy_transport_v1": TaxonomyRecord(
            "taxonomy_transport_v1",
            1,
            ("C_navigation", "C_power", "C_language"),
        )
    }

    force_schedules = {
        "sched_force_full": ForceScheduleRecord("sched_force_full", 1, False, False),
        "sched_scaffold": ForceScheduleRecord("sched_scaffold", 0, True, False),
        "sched_prime": ForceScheduleRecord("sched_prime", 0, False, True),
        "sched_free": ForceScheduleRecord("sched_free", 0, False, False),
    }
    opportunities = {
        "free_choice_1": FreeResponseOpportunityRecord("free_choice_1"),
        "free_choice_2": FreeResponseOpportunityRecord("free_choice_2"),
    }
    interactions = {
        "force_full_nav": InteractionForcingRecord(
            "force_full_nav",
            "tok_nav_force",
            "carrier_B",
            ResponseMode.fully_forced_response,
            "sched_force_full",
        ),
        "force_scaffold_nav": InteractionForcingRecord(
            "force_scaffold_nav",
            "tok_nav_scaffold",
            "carrier_B",
            ResponseMode.scaffolded_response,
            "sched_scaffold",
        ),
        "force_prime_nav": InteractionForcingRecord(
            "force_prime_nav",
            "tok_nav_prime",
            "carrier_B",
            ResponseMode.primed_response,
            "sched_prime",
        ),
        "force_free_nav": InteractionForcingRecord(
            "force_free_nav",
            "tok_nav_teach",
            "carrier_B",
            ResponseMode.observed_free_response,
            "sched_free",
        ),
    }
    censuses = {
        "census_force_full": FreeResponseCensusRecord(
            "census_force_full",
            "force_full_nav",
            "sched_force_full",
            (),
        ),
        "census_scaffold": FreeResponseCensusRecord(
            "census_scaffold",
            "force_scaffold_nav",
            "sched_scaffold",
            ("free_choice_1",),
        ),
        "census_prime": FreeResponseCensusRecord(
            "census_prime",
            "force_prime_nav",
            "sched_prime",
            ("free_choice_1",),
        ),
        "census_free": FreeResponseCensusRecord(
            "census_free",
            "force_free_nav",
            "sched_free",
            ("free_choice_1", "free_choice_2"),
        ),
    }
    absence_schedules = {
        "schedule_A_absent_nav": AAbsenceProbeSchedule(
            "schedule_A_absent_nav",
            "C_navigation",
            (5, 6),
            {5: False, 6: False},
            {5: False, 6: False},
        )
    }

    context_readouts = {
        "readout_lang_prompt": ContextReadoutRecord("readout_lang_prompt"),
        "readout_lang_tool": ContextReadoutRecord("readout_lang_tool"),
    }
    contexts = {
        "ctx_lang_prompt": TransportContextRecord(
            "ctx_lang_prompt",
            "C_language",
            "readout_lang_prompt",
        ),
        "ctx_lang_tool": TransportContextRecord(
            "ctx_lang_tool",
            "C_language",
            "readout_lang_tool",
        ),
    }
    families = {
        "family_language": ContextFamilyRecord(
            "family_language",
            ("ctx_lang_prompt", "ctx_lang_tool"),
        )
    }
    role_states = {
        "pre_pkg_lang_stable": BRoleStateRecord(
            "pre_pkg_lang_stable",
            {"family_language": frozenset()},
            "family_language",
        ),
        "post_pkg_lang_stable": BRoleStateRecord(
            "post_pkg_lang_stable",
            {"family_language": frozenset({"role_lang_handle"})},
            "family_language",
        ),
        "pre_pkg_lang_instability": BRoleStateRecord(
            "pre_pkg_lang_instability",
            {"family_language": frozenset()},
            "family_language",
        ),
        "post_pkg_lang_instability": BRoleStateRecord(
            "post_pkg_lang_instability",
            {"family_language": frozenset({"role_lang_handle"})},
            "family_language",
        ),
        "pre_pkg_lang_role_drift": BRoleStateRecord(
            "pre_pkg_lang_role_drift",
            {"family_language": frozenset()},
            "family_language",
        ),
        "post_pkg_lang_role_drift": BRoleStateRecord(
            "post_pkg_lang_role_drift",
            {"family_language": frozenset({"role_lang_handle", "role_other_handle"})},
            "family_language",
        ),
        "pre_pkg_lang_saturation": BRoleStateRecord(
            "pre_pkg_lang_saturation",
            {"family_language": frozenset({"role_lang_handle"})},
            "family_language",
        ),
        "post_pkg_lang_saturation": BRoleStateRecord(
            "post_pkg_lang_saturation",
            {"family_language": frozenset({"role_lang_handle"})},
            "family_language",
        ),
    }
    reactivations = {
        "react_stable_prompt": ContextualRepairReactivationRecord(
            "react_stable_prompt",
            "tok_symbol_stable",
            "pkg_lang_stable",
            "bridge_paid_ab",
            "ctx_lang_prompt",
            "repair_symbol_ctx1",
        ),
        "react_stable_tool": ContextualRepairReactivationRecord(
            "react_stable_tool",
            "tok_symbol_stable",
            "pkg_lang_stable",
            "bridge_paid_ab",
            "ctx_lang_tool",
            "repair_symbol_ctx2",
        ),
        "react_instability_prompt": ContextualRepairReactivationRecord(
            "react_instability_prompt",
            "tok_symbol_instability",
            "pkg_lang_instability",
            "bridge_paid_ab",
            "ctx_lang_prompt",
            "repair_symbol_ctx1",
        ),
        "react_drift_prompt": ContextualRepairReactivationRecord(
            "react_drift_prompt",
            "tok_symbol_role_drift",
            "pkg_lang_role_drift",
            "bridge_paid_ab",
            "ctx_lang_prompt",
            "repair_symbol_ctx1",
        ),
        "react_drift_tool": ContextualRepairReactivationRecord(
            "react_drift_tool",
            "tok_symbol_role_drift",
            "pkg_lang_role_drift",
            "bridge_paid_ab",
            "ctx_lang_tool",
            "repair_symbol_ctx2_drift",
        ),
        "react_saturation_prompt": ContextualRepairReactivationRecord(
            "react_saturation_prompt",
            "tok_symbol_saturation",
            "pkg_lang_saturation",
            "bridge_paid_ab",
            "ctx_lang_prompt",
            "repair_symbol_ctx1",
        ),
        "react_saturation_tool": ContextualRepairReactivationRecord(
            "react_saturation_tool",
            "tok_symbol_saturation",
            "pkg_lang_saturation",
            "bridge_paid_ab",
            "ctx_lang_tool",
            "repair_symbol_ctx2",
        ),
    }

    claims = {
        "claim_comm_clean": TransportClaimRef(
            "claim_comm_clean",
            TransportClaimKind.communication,
            "tok_nav_comm",
            "pkg_nav_comm",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "claim_teach_absent_capacity": TransportClaimRef(
            "claim_teach_absent_capacity",
            TransportClaimKind.teaching,
            "tok_nav_teach",
            "pkg_nav_teach",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "claim_force_null": TransportClaimRef(
            "claim_force_null",
            TransportClaimKind.communication,
            "tok_nav_force",
            "pkg_nav_force",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "claim_symbol_stable": TransportClaimRef(
            "claim_symbol_stable",
            TransportClaimKind.symbol,
            "tok_symbol_stable",
            "pkg_lang_stable",
            "bridge_paid_ab",
            family="family_language",
        ),
        "claim_scaffolded_no_capacity": TransportClaimRef(
            "claim_scaffolded_no_capacity",
            TransportClaimKind.teaching,
            "tok_nav_scaffold",
            "pkg_nav_scaffold",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "claim_primed_no_capacity": TransportClaimRef(
            "claim_primed_no_capacity",
            TransportClaimKind.communication,
            "tok_nav_prime",
            "pkg_nav_prime",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "claim_influence_different_class": TransportClaimRef(
            "claim_influence_different_class",
            TransportClaimKind.communication,
            "tok_nav_influence",
            "pkg_nav_influence",
            "bridge_paid_ab",
            target_class="C_power",
        ),
        "reject_unpaid_bridge": TransportClaimRef(
            "reject_unpaid_bridge",
            TransportClaimKind.communication,
            "tok_nav_unpaid",
            "pkg_nav_unpaid",
            "bridge_unpaid_ab",
            target_class="C_navigation",
        ),
        "reject_uncarried_target_repair": TransportClaimRef(
            "reject_uncarried_target_repair",
            TransportClaimKind.communication,
            "tok_nav_uncarried",
            "pkg_nav_uncarried",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "reject_role_preservation_failure": TransportClaimRef(
            "reject_role_preservation_failure",
            TransportClaimKind.communication,
            "tok_nav_role_drift",
            "pkg_nav_role_drift",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "reject_symbol_context_instability": TransportClaimRef(
            "reject_symbol_context_instability",
            TransportClaimKind.symbol,
            "tok_symbol_instability",
            "pkg_lang_instability",
            "bridge_paid_ab",
            family="family_language",
        ),
        "reject_symbol_role_drift": TransportClaimRef(
            "reject_symbol_role_drift",
            TransportClaimKind.symbol,
            "tok_symbol_role_drift",
            "pkg_lang_role_drift",
            "bridge_paid_ab",
            family="family_language",
        ),
        "reject_saturation_relabel": TransportClaimRef(
            "reject_saturation_relabel",
            TransportClaimKind.symbol,
            "tok_symbol_saturation",
            "pkg_lang_saturation",
            "bridge_paid_ab",
            family="family_language",
        ),
        "reject_parameter_channel_only": TransportClaimRef(
            "reject_parameter_channel_only",
            TransportClaimKind.communication,
            "tok_nav_parameter",
            "pkg_nav_parameter",
            "bridge_paid_ab",
            target_class="C_navigation",
        ),
        "reject_flow_crossing_no_bridge": TransportClaimRef(
            "reject_flow_crossing_no_bridge",
            TransportClaimKind.communication,
            "tok_nav_flow",
            "pkg_nav_flow",
            "bridge_flow_unlinked_ab",
            target_class="C_navigation",
        ),
    }

    def record(
        name: str,
        claim_name: str,
        status: RepairTransportStatus,
        target: str | None,
        family: str | None,
        forcing: str | None,
    ) -> RepairTransportStatusRecord:
        claim = claims[claim_name]
        return RepairTransportStatusRecord(
            name,
            claim.kind,
            claim.token,
            claim.source_package,
            target,
            family,
            forcing,
            claim.bridge,
            status,
        )

    status_records = {
        "status_comm_clean": record(
            "status_comm_clean",
            "claim_comm_clean",
            RepairTransportStatus.communicated,
            "repair_nav_clean",
            None,
            None,
        ),
        "status_teach_absent_capacity": record(
            "status_teach_absent_capacity",
            "claim_teach_absent_capacity",
            RepairTransportStatus.taught,
            "repair_nav_teach_initial",
            None,
            None,
        ),
        "status_force_null": record(
            "status_force_null",
            "claim_force_null",
            RepairTransportStatus.coercion_null,
            "repair_nav_force_placeholder",
            None,
            "force_full_nav",
        ),
        "status_symbol_stable": record(
            "status_symbol_stable",
            "claim_symbol_stable",
            RepairTransportStatus.symbolic,
            None,
            "family_language",
            None,
        ),
        "status_scaffolded_no_capacity": record(
            "status_scaffolded_no_capacity",
            "claim_scaffolded_no_capacity",
            RepairTransportStatus.scaffolded_or_primed,
            "repair_nav_scaffold_immediate",
            None,
            "force_scaffold_nav",
        ),
        "status_primed_no_capacity": record(
            "status_primed_no_capacity",
            "claim_primed_no_capacity",
            RepairTransportStatus.scaffolded_or_primed,
            "repair_nav_prime_immediate",
            None,
            "force_prime_nav",
        ),
        "status_influence_different_class": record(
            "status_influence_different_class",
            "claim_influence_different_class",
            RepairTransportStatus.influence_only,
            "repair_power_influence",
            None,
            None,
        ),
        "status_unpaid_bridge": record(
            "status_unpaid_bridge",
            "reject_unpaid_bridge",
            RepairTransportStatus.transport_rejected,
            "repair_nav_unpaid",
            None,
            None,
        ),
        "status_uncarried_target_repair": record(
            "status_uncarried_target_repair",
            "reject_uncarried_target_repair",
            RepairTransportStatus.transport_rejected,
            "repair_nav_uncarried",
            None,
            None,
        ),
        "status_role_preservation_failure": record(
            "status_role_preservation_failure",
            "reject_role_preservation_failure",
            RepairTransportStatus.transport_rejected,
            "repair_nav_role_drift",
            None,
            None,
        ),
        "status_symbol_context_instability": record(
            "status_symbol_context_instability",
            "reject_symbol_context_instability",
            RepairTransportStatus.transport_rejected,
            None,
            "family_language",
            None,
        ),
        "status_symbol_role_drift": record(
            "status_symbol_role_drift",
            "reject_symbol_role_drift",
            RepairTransportStatus.transport_rejected,
            None,
            "family_language",
            None,
        ),
        "status_saturation_relabel": record(
            "status_saturation_relabel",
            "reject_saturation_relabel",
            RepairTransportStatus.transport_rejected,
            None,
            "family_language",
            None,
        ),
        "status_parameter_channel_only": record(
            "status_parameter_channel_only",
            "reject_parameter_channel_only",
            RepairTransportStatus.transport_rejected,
            "repair_nav_parameter_stub",
            None,
            None,
        ),
        "status_flow_crossing_no_bridge": record(
            "status_flow_crossing_no_bridge",
            "reject_flow_crossing_no_bridge",
            RepairTransportStatus.transport_rejected,
            "repair_nav_flow_stub",
            None,
            None,
        ),
    }

    return Fixture(
        carrier_a=carrier_a,
        carrier_b=carrier_b,
        ctx=ctx,
        challenge_classes=challenge_classes,
        roles=roles,
        tokens=tokens,
        source_packages=source_packages,
        moves=moves,
        target_repairs=target_repairs,
        bridges=bridges,
        defects=defects,
        source_ledgers=source_ledgers,
        target_ledgers=target_ledgers,
        access_records=access_records,
        taxonomies=taxonomies,
        force_schedules=force_schedules,
        opportunities=opportunities,
        censuses=censuses,
        interactions=interactions,
        absence_schedules=absence_schedules,
        context_readouts=context_readouts,
        contexts=contexts,
        families=families,
        role_states=role_states,
        reactivations=reactivations,
        claims=claims,
        status_records=status_records,
        forced_delta_pairs={
            "tok_nav_force": (frozenset(), frozenset()),
        },
        flow_crossings=frozenset({"flow_boundary_crossing_1"}),
    )


EXPECTED_STATUSES = {
    "claim_comm_clean": RepairTransportStatus.communicated,
    "claim_teach_absent_capacity": RepairTransportStatus.taught,
    "claim_force_null": RepairTransportStatus.coercion_null,
    "claim_symbol_stable": RepairTransportStatus.symbolic,
    "claim_scaffolded_no_capacity": RepairTransportStatus.scaffolded_or_primed,
    "claim_primed_no_capacity": RepairTransportStatus.scaffolded_or_primed,
    "claim_influence_different_class": RepairTransportStatus.influence_only,
    "reject_unpaid_bridge": RepairTransportStatus.transport_rejected,
    "reject_uncarried_target_repair": RepairTransportStatus.transport_rejected,
    "reject_role_preservation_failure": RepairTransportStatus.transport_rejected,
    "reject_symbol_context_instability": RepairTransportStatus.transport_rejected,
    "reject_symbol_role_drift": RepairTransportStatus.transport_rejected,
    "reject_saturation_relabel": RepairTransportStatus.transport_rejected,
    "reject_parameter_channel_only": RepairTransportStatus.transport_rejected,
    "reject_flow_crossing_no_bridge": RepairTransportStatus.transport_rejected,
}


def _status_rows(fixture: Fixture) -> dict[str, StatusRow]:
    rows: dict[str, StatusRow] = {}
    for name, expected in EXPECTED_STATUSES.items():
        observed, truths, record = classify_repair_transport_status(fixture, name)
        rows[name] = StatusRow(
            name=name,
            claim_name=name,
            expected=expected,
            observed=observed,
            truths=truths,
            status_record=record,
        )
    return rows


def _control_rows(fixture: Fixture) -> dict[str, ControlRow]:
    force_accepts = (
        computed_response_mode(fixture, "force_full_nav") is ResponseMode.fully_forced_response
        and computed_response_mode(fixture, "force_scaffold_nav") is ResponseMode.scaffolded_response
        and computed_response_mode(fixture, "force_prime_nav") is ResponseMode.primed_response
    )
    role_accepts = role_preserving_transport(fixture, "pkg_nav_comm", "repair_nav_clean")
    role_rejects = not role_preserving_transport(
        fixture,
        "pkg_nav_role_drift",
        "repair_nav_role_drift",
    )
    bridge_accepts = bridge_defects_paid(fixture, "bridge_paid_ab")
    bridge_rejects = not bridge_defects_paid(fixture, "bridge_unpaid_ab")
    shared_passed = force_accepts and role_accepts and role_rejects and bridge_accepts and bridge_rejects

    comm_claim = fixture.claims["claim_comm_clean"]
    comm_record = fixture.status_records["status_comm_clean"]
    teaching_same = TransportClaimRef(
        "ctrl_teaching_same_refs",
        TransportClaimKind.teaching,
        "tok_nav_comm",
        "pkg_nav_comm",
        "bridge_paid_ab",
        target_class="C_navigation",
    )
    symbol_same = TransportClaimRef(
        "ctrl_symbol_same_refs",
        TransportClaimKind.symbol,
        "tok_nav_comm",
        "pkg_nav_comm",
        "bridge_paid_ab",
        family="family_language",
    )
    scoping_passed = (
        transport_status_record_matches_claim(fixture, comm_claim, comm_record)
        and not transport_status_record_matches_claim(fixture, teaching_same, comm_record)
        and not transport_status_record_matches_claim(fixture, symbol_same, comm_record)
    )

    independence_passed = (
        classify_repair_transport_status(fixture, "claim_comm_clean")[0]
        is RepairTransportStatus.communicated
        and classify_repair_transport_status(fixture, "claim_symbol_stable")[0]
        is RepairTransportStatus.symbolic
        and fixture.claims["claim_comm_clean"].token != fixture.claims["claim_symbol_stable"].token
    )

    falsifier_passed = not symbol_falsifier_linked(
        fixture,
        "claim_comm_clean",
        "tok_symbol_stable",
        "pkg_lang_stable",
        "bridge_unpaid_ab",
        "family_language",
    )

    return {
        "ctrl_shared_comparator_bundle_nontrivial": ControlRow(
            "ctrl_shared_comparator_bundle_nontrivial",
            "shared ctx_main computes both accepting and rejecting comparator results",
            f"force={force_accepts}; role_accept={role_accepts}; role_reject={role_rejects}; bridge_accept={bridge_accepts}; bridge_reject={bridge_rejects}",
            shared_passed,
        ),
        "ctrl_transport_claim_kind_scoping": ControlRow(
            "ctrl_transport_claim_kind_scoping",
            "communication record matches only communication claim, not teaching/symbol claims",
            f"comm={transport_status_record_matches_claim(fixture, comm_claim, comm_record)}; teaching={transport_status_record_matches_claim(fixture, teaching_same, comm_record)}; symbol={transport_status_record_matches_claim(fixture, symbol_same, comm_record)}",
            scoping_passed,
        ),
        "ctrl_claim_independence": ControlRow(
            "ctrl_claim_independence",
            "distinct claims keep independent statuses",
            "claim_comm_clean=communicated; claim_symbol_stable=symbolic",
            independence_passed,
        ),
        "ctrl_falsifier_claim_linkage": ControlRow(
            "ctrl_falsifier_claim_linkage",
            "mismatched-token/bridge falsifier linkage is false",
            f"claimLinked={not falsifier_passed}",
            falsifier_passed,
        ),
    }


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    comparisons: list[Comparison] = []
    for name in REGISTERED_COMPARISON_ORDER:
        if name.endswith(".status"):
            row_name = name.removesuffix(".status")
            row = results.rows[row_name]
            comparisons.append(
                Comparison(
                    name=name,
                    passed=row.passed,
                    observed=row.observed.value,
                    expected=row.expected.value,
                )
            )
        else:
            control = results.controls[name]
            comparisons.append(
                Comparison(
                    name=name,
                    passed=control.passed_control,
                    observed=control.observed,
                    expected=control.expected,
                )
            )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture, rows: dict[str, StatusRow]) -> bool:
    return all(
        row.status_record is not None
        and repair_transport_status_occurrence_for(
            fixture,
            fixture.claims[row.claim_name],
            row.status_record,
        )
        for row in rows.values()
    )


def _no_hardcoded_status_discipline(results: SweepResults) -> bool:
    return all(
        row.observed is not RepairTransportStatus.unclassified
        and sum(row.truths.values()) == 1
        and row.truths.get(row.observed.value, False) is True
        for row in results.rows.values()
    ) and all(control.passed_control for control in results.controls.values())


def run_e13_repair_transport_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = _status_rows(fixture)
    controls = _control_rows(fixture)
    placeholder = SweepResults(
        rows=rows,
        controls=controls,
        comparisons=(),
        actual_scope_discipline=_actual_scope_discipline(fixture, rows),
        no_hardcoded_status_discipline=False,
    )
    checked = replace(
        placeholder,
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(placeholder),
    )
    comparisons = _comparisons(checked)
    return replace(checked, comparisons=comparisons)


def format_results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E13 Repair Transport Sweep Results",
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
    results = run_e13_repair_transport_sweep()
    path.write_text(format_results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = run_e13_repair_transport_sweep()
    passed = sum(1 for comparison in results.comparisons if comparison.passed)
    total = len(results.comparisons)
    print(f"E13 repair transport sweep: {passed}/{total} comparisons PASS")
    for comparison in results.comparisons:
        verdict = "PASS" if comparison.passed else "FAIL"
        print(
            f"{verdict}: {comparison.name}: "
            f"observed={comparison.observed} expected={comparison.expected}"
        )


if __name__ == "__main__":
    main()
