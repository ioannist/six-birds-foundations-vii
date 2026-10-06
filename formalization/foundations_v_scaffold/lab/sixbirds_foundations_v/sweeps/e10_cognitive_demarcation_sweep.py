"""E10 cognitive-demarcation sweep against the pre-registered predictions.

The fixed fixture is specified in
``formalization/notes/sweeps/E10_cognitive_demarcation_predictions.md``. This
module mirrors the Lean status apparatus in
``SixBirdsFoundationsV.Laws.E10CognitiveDemarcation``: all status labels are
computed from carried package records, package-owned Delta reductions, shared
top-down-channel comparators, and priority-normalized claim-scoped cases.
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
    / "E10_cognitive_demarcation_results.md"
)

REGISTERED_COMPARISON_ORDER = (
    "claim_pkg_nav_cognitive.status",
    "claim_pkg_passive_non_cognitive.status",
    "claim_pkg_schedule_trap.status",
    "claim_pkg_external_scaffold.status",
    "claim_pkg_structural_path.status",
    "claim_pkg_decodable.status",
    "claim_pkg_repair_no_gate.status",
    "claim_pkg_gate_no_repair.status",
    "claim_intention_clean.status",
    "claim_intention_neutral.status",
    "claim_intention_posthoc.status",
    "claim_intention_approximate.status",
    "claim_intention_target_incoherent.status",
    "claim_goal_clean.status",
    "claim_goal_neutral.status",
    "claim_goal_reward_proxy_only.status",
    "claim_goal_route_unstable.status",
    "ctrl_support_for_intervention_linkage",
    "ctrl_main_claim_scoping",
    "ctrl_decodable_priority_blocks_cognitive.status",
    "ctrl_schedule_priority_blocks_cognitive.status",
    "ctrl_post_hoc_priority_blocks_intention.status",
    "ctrl_reward_proxy_priority_blocks_goal.status",
    "ctrl_every_route_evaluated_universal.status",
    "ctrl_uncarried_intention_rejected.status",
    "ctrl_uncarried_goal_rejected.status",
)


class AccessActionKind(str, Enum):
    access = "access"
    action = "action"


class ClaimStatus(str, Enum):
    accepted = "accepted"
    blocked = "blocked"


class CognitiveStatus(str, Enum):
    schedule_trap = "schedule_trap"
    scaffolding = "scaffolding"
    structural_path_only = "structural_path_only"
    decodable_correlate = "decodable_correlate"
    repair_without_gate = "repair_without_gate"
    gate_without_repair = "gate_without_repair"
    cognitive = "cognitive"
    non_cognitive = "non_cognitive"
    unclassified = "unclassified"


class IntentionStatus(str, Enum):
    post_hoc_intention = "post_hoc_intention"
    approximate_support_defect = "approximate_support_defect"
    target_incoherent_restriction = "target_incoherent_restriction"
    intention = "intention"
    not_intention = "not_intention"
    unclassified = "unclassified"


class GoalStatus(str, Enum):
    reward_proxy_only = "reward_proxy_only"
    route_unstable = "route_unstable"
    goal = "goal"
    not_goal = "not_goal"
    unclassified = "unclassified"


@dataclass(frozen=True)
class Carrier:
    name: str
    states: tuple[str, ...]

    def supp_k(self, source: str, target: str) -> bool:
        if source not in self.states or target not in self.states:
            return False
        return self.states[(self.states.index(source) + 1) % len(self.states)] == target


@dataclass(frozen=True)
class CognitiveChallengeClass:
    name: str
    class_id: int


@dataclass(frozen=True)
class TargetClassRecord:
    name: str
    record_id: int
    challenge_class: str


@dataclass(frozen=True)
class CognitivePackageRecord:
    name: str
    record_id: int
    package_value_id: int
    declared_class: str
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class PackageFormationRecord:
    name: str
    record_id: int
    package_record: str
    formed_at: int = 0
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class PackageInvocationRecord:
    name: str
    record_id: int
    package_record: str
    challenge_class: str
    invoked_at: int = 0
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class PackageQuotientRecord:
    name: str
    record_id: int
    challenge_class: str


@dataclass(frozen=True)
class DescentWitnessRecord:
    name: str
    record_id: int
    package: str
    before_quotient: str
    after_quotient: str
    challenge_class: str
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class KernelSupportRecord:
    name: str
    record_id: int
    kind: AccessActionKind
    package_record: str
    challenge_class: str
    support_id: int
    support_set: frozenset[str]
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class PackageInterventionRecord:
    name: str
    record_id: int
    package_record: str
    package_value_id: int
    intervention_index: int
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class MatchedControlRecord:
    name: str
    record_id: int
    intervention_a: str
    intervention_b: str
    challenge_class: str
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class TopDownChannelRecord:
    name: str
    structural_path_present: bool
    macro_record_present: bool = True
    substrate_record_present: bool = True
    intervention_gate: bool = True
    matched_controls_gate: bool = True
    feasibility_gate: bool = True
    source_gate: bool = True
    visibility_gate: bool = True
    audit_gate: bool = True
    no_smuggling_gate: bool = True
    effect_gate: bool = True
    comparator_finite: bool = True
    threshold_finite: bool = True
    nonclaim_recorded: bool = True
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class TopDownGateCandidate:
    name: str
    package: str
    challenge_class: str
    channel_record: str
    intervention1: str
    intervention2: str
    matched_controls: str
    support1: str
    support2: str


@dataclass(frozen=True)
class DecodabilityReadoutRecord:
    name: str
    record_id: int
    package_record: str
    decoded_class: str


@dataclass(frozen=True)
class ExogenousScheduleRecord:
    name: str
    record_id: int
    challenge_class: str
    schedule_id: int


@dataclass(frozen=True)
class StructuralPathRecord:
    name: str
    record_id: int
    package_record: str
    challenge_class: str
    channel_record: str
    support1: str
    support2: str


@dataclass(frozen=True)
class ActionSupportRestrictionRecord:
    name: str
    record_id: int
    theta: str
    target_class: str
    unrestricted_support: str
    restricted_support: str
    restriction_time: int
    outcome_time: int
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class FutureProbeRecord:
    name: str
    record_id: int
    target_class: str
    probe_index: int
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class TargetQuotientRecord:
    name: str
    record_id: int
    theta: str
    target_class: str
    quotient_id: int
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class RouteSubstitutionRecord:
    name: str
    record_id: int
    route_index: int
    target_class: str
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class RouteEvaluationRecord:
    name: str
    record_id: int
    route: str
    target_quotient: str
    before_quotient: str
    after_quotient: str
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class RewardProxyRecord:
    name: str
    record_id: int
    theta: str
    proxy_value: Fraction
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class CognitiveClaimRef:
    name: str
    package: str
    challenge_class: str


@dataclass(frozen=True)
class IntentionClaimRef:
    name: str
    theta: str
    target_class: str


@dataclass(frozen=True)
class GoalClaimRef:
    name: str
    theta: str
    target_class: str


@dataclass(frozen=True)
class CognitiveStatusRecord:
    name: str
    status: CognitiveStatus
    package_record: str | None
    challenge_class: str | None
    formation_record: str | None = None
    invocation_record: str | None = None
    descent_record: str | None = None
    channel_record: str | None = None
    decodability_record: str | None = None
    schedule_record: str | None = None
    structural_path_record: str | None = None
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class IntentionStatusRecord:
    name: str
    status: IntentionStatus
    theta: str | None
    target_class: str | None
    restriction_record: str | None = None
    channel_record: str | None = None
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class GoalStatusRecord:
    name: str
    status: GoalStatus
    theta: str | None
    target_class: str | None
    target_quotient: str | None = None
    reward_proxy: str | None = None
    route_evaluations: tuple[str, ...] = ()
    carried: bool = True
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class CognitiveDemarcationClassifierContext:
    def package_installs_quotient(
        self,
        fixture: Fixture,
        package: str,
        q_before: str,
        q_after: str,
    ) -> bool:
        return fixture.install_map.get((package, q_before)) == q_after

    def delta_nonempty(self, fixture: Fixture, quotient: str, challenge_class: str) -> bool:
        return bool(fixture.delta_splits.get((quotient, challenge_class), frozenset()))

    def delta_strictly_reduced_by(
        self,
        fixture: Fixture,
        q_before: str,
        q_after: str,
        challenge_class: str,
    ) -> bool:
        before = fixture.delta_splits.get((q_before, challenge_class), frozenset())
        after = fixture.delta_splits.get((q_after, challenge_class), frozenset())
        return bool(before) and after < before

    def kernel_support_differs(self, fixture: Fixture, support1: str, support2: str) -> bool:
        first = fixture.supports[support1]
        second = fixture.supports[support2]
        return (
            first.package_record == second.package_record
            and first.challenge_class == second.challenge_class
            and first.kind is second.kind
            and first.support_set != second.support_set
        )

    def support_for_intervention(self, fixture: Fixture, support: str, intervention: str) -> bool:
        support_record = fixture.supports[support]
        intervention_record = fixture.interventions[intervention]
        return (
            support_record.package_record == intervention_record.package_record
            and fixture.support_link.get(intervention) == support
        )

    def channel_certifies_kernel_comparison(
        self,
        fixture: Fixture,
        channel: str,
        matched: str,
        support1: str,
        support2: str,
    ) -> bool:
        matched_record = fixture.matched_controls[matched]
        return (
            top_down_channel_claim_status(fixture.channels[channel]) is ClaimStatus.accepted
            and self.support_for_intervention(fixture, support1, matched_record.intervention_a)
            and self.support_for_intervention(fixture, support2, matched_record.intervention_b)
            and self.kernel_support_differs(fixture, support1, support2)
        )

    def decodes_package(self, readout: DecodabilityReadoutRecord, package: str, challenge_class: str) -> bool:
        return readout.package_record == package and readout.decoded_class == challenge_class

    def schedule_explains_kernel_change(
        self,
        fixture: Fixture,
        schedule: str,
        support_before: str,
        support_after: str,
    ) -> bool:
        schedule_record = fixture.schedules[schedule]
        return fixture.schedule_support_change.get((support_before, support_after)) == schedule_record.schedule_id

    def support_strict_subset(self, fixture: Fixture, restricted: str, unrestricted: str) -> bool:
        return fixture.supports[restricted].support_set < fixture.supports[unrestricted].support_set

    def target_coherent_under_probe(
        self,
        fixture: Fixture,
        target: str,
        probe: str,
        restriction: str,
    ) -> bool:
        return fixture.target_probe_coherence.get((target, probe, restriction), False)

    def approximate_support_restriction(self, fixture: Fixture, restriction: str) -> bool:
        return restriction in fixture.approximate_restriction_ids

    def route_evaluation_targets(self, evaluation: RouteEvaluationRecord, route: str, target: str) -> bool:
        return evaluation.route == route and evaluation.target_quotient == target

    def route_selection_persists(
        self,
        fixture: Fixture,
        target: str,
        evaluations: tuple[str, ...],
    ) -> bool:
        return all(
            fixture.evaluations[eval_name].target_quotient == target
            for eval_name in evaluations
        ) and fixture.persistence_flags.get(target, False)

    def reward_proxy_explains_selection(
        self,
        fixture: Fixture,
        proxy: str,
        target: str,
    ) -> bool:
        proxy_record = fixture.reward_proxies[proxy]
        target_record = fixture.target_quotients[target]
        return proxy_record.theta == target_record.theta and proxy_record.proxy_value > 0


@dataclass(frozen=True)
class Fixture:
    carrier: Carrier
    ctx: CognitiveDemarcationClassifierContext
    classes: dict[str, CognitiveChallengeClass]
    target_classes: dict[str, TargetClassRecord]
    packages: dict[str, CognitivePackageRecord]
    formations: dict[str, PackageFormationRecord]
    invocations: dict[str, PackageInvocationRecord]
    quotients: dict[str, PackageQuotientRecord]
    descents: dict[str, DescentWitnessRecord]
    supports: dict[str, KernelSupportRecord]
    interventions: dict[str, PackageInterventionRecord]
    matched_controls: dict[str, MatchedControlRecord]
    channels: dict[str, TopDownChannelRecord]
    gates: dict[str, TopDownGateCandidate]
    readouts: dict[str, DecodabilityReadoutRecord]
    schedules: dict[str, ExogenousScheduleRecord]
    structural_paths: dict[str, StructuralPathRecord]
    restrictions: dict[str, ActionSupportRestrictionRecord]
    probes: dict[str, FutureProbeRecord]
    target_quotients: dict[str, TargetQuotientRecord]
    routes: dict[str, RouteSubstitutionRecord]
    evaluations: dict[str, RouteEvaluationRecord]
    reward_proxies: dict[str, RewardProxyRecord]
    cognitive_claims: dict[str, CognitiveClaimRef]
    intention_claims: dict[str, IntentionClaimRef]
    goal_claims: dict[str, GoalClaimRef]
    cognitive_status_records: dict[str, CognitiveStatusRecord]
    intention_status_records: dict[str, IntentionStatusRecord]
    goal_status_records: dict[str, GoalStatusRecord]
    install_map: dict[tuple[str, str], str]
    delta_splits: dict[tuple[str, str], frozenset[str]]
    support_link: dict[str, str]
    gate_inventory: dict[tuple[str, str], tuple[str, ...]]
    repair_inventory: dict[tuple[str, str], tuple[str, ...]]
    provenance_inventory: dict[str, tuple[tuple[str, str], ...]]
    schedule_support_change: dict[tuple[str, str], int]
    schedule_witness_supports: dict[tuple[str, str], tuple[str, str]]
    restriction_probes: dict[str, tuple[str, ...]]
    target_probe_coherence: dict[tuple[str, str, str], bool]
    approximate_restriction_ids: frozenset[str]
    route_sets: dict[str, tuple[str, ...]]
    route_evaluation_sets: dict[str, tuple[str, ...]]
    persistence_flags: dict[str, bool]
    route_persistence_inventory: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class StatusRow:
    name: str
    expected: str
    observed: str
    truths: dict[str, bool]
    status_record: object | None

    @property
    def passed(self) -> bool:
        return self.observed == self.expected


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


def top_down_channel_accepted_bool(channel: TopDownChannelRecord) -> bool:
    return (
        channel.structural_path_present
        and channel.macro_record_present
        and channel.substrate_record_present
        and channel.comparator_finite
        and channel.threshold_finite
        and channel.nonclaim_recorded
        and channel.intervention_gate
        and channel.matched_controls_gate
        and channel.feasibility_gate
        and channel.source_gate
        and channel.visibility_gate
        and channel.audit_gate
        and channel.no_smuggling_gate
        and channel.effect_gate
    )


def top_down_channel_claim_status(channel: TopDownChannelRecord) -> ClaimStatus:
    return ClaimStatus.accepted if top_down_channel_accepted_bool(channel) else ClaimStatus.blocked


def struct_down(channel: TopDownChannelRecord) -> bool:
    return channel.structural_path_present


def package_carried_provenance(fixture: Fixture, package_name: str) -> bool:
    package = fixture.packages[package_name]
    formation = fixture.formations.get(f"form_{package_name}")
    invocation = fixture.invocations.get(f"invoke_{package_name}")
    return (
        formation is not None
        and invocation is not None
        and formation.package_record == package_name
        and invocation.package_record == package_name
        and invocation.challenge_class == package.declared_class
        and _record_carried(package)
        and _record_carried(formation)
        and _record_carried(invocation)
    )


def no_carried_package_provenance_for(fixture: Fixture, package_name: str) -> bool:
    return fixture.provenance_inventory.get(package_name, ()) == () and not package_carried_provenance(fixture, package_name)


def package_repair_descent(
    fixture: Fixture,
    descent_name: str,
    package_name: str,
    challenge_class: str,
) -> bool:
    descent = fixture.descents[descent_name]
    package = fixture.packages[package_name]
    return (
        descent.package == package_name
        and descent.challenge_class == challenge_class
        and package.declared_class == challenge_class
        and _record_carried(descent)
        and fixture.ctx.delta_nonempty(fixture, descent.before_quotient, challenge_class)
        and fixture.ctx.package_installs_quotient(
            fixture,
            package_name,
            descent.before_quotient,
            descent.after_quotient,
        )
        and fixture.ctx.delta_strictly_reduced_by(
            fixture,
            descent.before_quotient,
            descent.after_quotient,
            challenge_class,
        )
    )


def no_package_repair_descent_for(fixture: Fixture, package_name: str, challenge_class: str) -> bool:
    return fixture.repair_inventory.get((package_name, challenge_class), ()) == ()


def top_down_kernel_gate_certified(
    fixture: Fixture,
    gate_name: str,
    package_name: str,
    challenge_class: str,
) -> bool:
    gate = fixture.gates[gate_name]
    int1 = fixture.interventions[gate.intervention1]
    int2 = fixture.interventions[gate.intervention2]
    matched = fixture.matched_controls[gate.matched_controls]
    support1 = fixture.supports[gate.support1]
    support2 = fixture.supports[gate.support2]
    channel = fixture.channels[gate.channel_record]
    return (
        gate.package == package_name
        and gate.challenge_class == challenge_class
        and int1.package_record == package_name
        and int2.package_record == package_name
        and matched.intervention_a == gate.intervention1
        and matched.intervention_b == gate.intervention2
        and int1.package_value_id != int2.package_value_id
        and int1.intervention_index != int2.intervention_index
        and matched.challenge_class == challenge_class
        and support1.package_record == package_name
        and support2.package_record == package_name
        and support1.challenge_class == challenge_class
        and support2.challenge_class == challenge_class
        and _record_carried(int1)
        and _record_carried(int2)
        and _record_carried(matched)
        and _record_carried(support1)
        and _record_carried(support2)
        and _record_carried(channel)
        and fixture.ctx.support_for_intervention(fixture, gate.support1, gate.intervention1)
        and fixture.ctx.support_for_intervention(fixture, gate.support2, gate.intervention2)
        and fixture.ctx.channel_certifies_kernel_comparison(
            fixture,
            gate.channel_record,
            gate.matched_controls,
            gate.support1,
            gate.support2,
        )
        and top_down_channel_accepted_bool(channel)
        and top_down_channel_claim_status(channel) is ClaimStatus.accepted
        and fixture.ctx.kernel_support_differs(fixture, gate.support1, gate.support2)
    )


def no_accepted_top_down_gate_for(fixture: Fixture, package_name: str, challenge_class: str) -> bool:
    return fixture.gate_inventory.get((package_name, challenge_class), ()) == ()


def support_restriction_in_advance(
    fixture: Fixture,
    restriction_name: str,
    theta: str,
    target_class: str,
) -> bool:
    restriction = fixture.restrictions[restriction_name]
    return (
        restriction.theta == theta
        and restriction.target_class == target_class
        and fixture.supports[restriction.unrestricted_support].kind is AccessActionKind.action
        and fixture.supports[restriction.restricted_support].kind is AccessActionKind.action
        and restriction.restriction_time < restriction.outcome_time
        and _record_carried(restriction)
        and _record_carried(fixture.supports[restriction.unrestricted_support])
        and _record_carried(fixture.supports[restriction.restricted_support])
        and fixture.ctx.support_strict_subset(
            fixture,
            restriction.restricted_support,
            restriction.unrestricted_support,
        )
    )


def target_coherence_under_future_probes(
    fixture: Fixture,
    theta: str,
    target_class: str,
    restriction_name: str,
) -> bool:
    probes = fixture.restriction_probes.get(restriction_name, ())
    return bool(probes) and all(
        fixture.probes[probe].target_class == target_class
        and _record_carried(fixture.probes[probe])
        and fixture.ctx.target_coherent_under_probe(fixture, target_class, probe, restriction_name)
        for probe in probes
    )


def intention_evidence(fixture: Fixture, theta: str, target_class: str, restriction_name: str) -> bool:
    restriction = fixture.restrictions[restriction_name]
    target = fixture.target_classes[target_class]
    gate_names = fixture.gate_inventory.get((theta, target.challenge_class), ())
    return (
        package_carried_provenance(fixture, theta)
        and any(
            top_down_kernel_gate_certified(fixture, gate, theta, target.challenge_class)
            and fixture.gates[gate].support1 == restriction.unrestricted_support
            and fixture.gates[gate].support2 == restriction.restricted_support
            for gate in gate_names
        )
        and support_restriction_in_advance(fixture, restriction_name, theta, target_class)
        and target_coherence_under_future_probes(fixture, theta, target_class, restriction_name)
    )


def goal_target_selection(fixture: Fixture, target_name: str, theta: str, target_class: str) -> bool:
    target = fixture.target_quotients[target_name]
    return (
        target.theta == theta
        and target.target_class == target_class
        and _record_carried(target)
    )


def route_substitution_evaluation(
    fixture: Fixture,
    target_name: str,
    route_name: str,
    eval_name: str,
) -> bool:
    route = fixture.routes[route_name]
    target = fixture.target_quotients[target_name]
    eval_record = fixture.evaluations[eval_name]
    return (
        fixture.ctx.route_evaluation_targets(eval_record, route_name, target_name)
        and route.target_class == target.target_class
        and _record_carried(route)
        and _record_carried(eval_record)
        and (
            fixture.ctx.delta_nonempty(fixture, eval_record.before_quotient, fixture.target_classes[route.target_class].challenge_class)
            or fixture.ctx.delta_strictly_reduced_by(
                fixture,
                eval_record.before_quotient,
                eval_record.after_quotient,
                fixture.target_classes[route.target_class].challenge_class,
            )
        )
    )


def every_route_evaluated(fixture: Fixture, target_name: str, routes: tuple[str, ...], evaluations: tuple[str, ...]) -> bool:
    for route in routes:
        if not any(
            route_substitution_evaluation(fixture, target_name, route, eval_name)
            and eval_name in evaluations
            for eval_name in fixture.evaluations
        ):
            return False
    return True


def route_substitution_persistence_certified(
    fixture: Fixture,
    theta: str,
    target_class: str,
    target_name: str,
) -> bool:
    routes = fixture.route_sets.get(target_name, ())
    evaluations = fixture.route_evaluation_sets.get(target_name, ())
    return (
        goal_target_selection(fixture, target_name, theta, target_class)
        and len(set(routes)) >= 2
        and all(_record_carried(fixture.routes[route]) for route in routes)
        and every_route_evaluated(fixture, target_name, routes, evaluations)
        and all(_record_carried(fixture.evaluations[eval_name]) for eval_name in evaluations)
        and fixture.ctx.route_selection_persists(fixture, target_name, evaluations)
    )


def no_route_persistence_for(fixture: Fixture, target_name: str) -> bool:
    return fixture.route_persistence_inventory.get(target_name, ()) == ()


def goal_evidence(fixture: Fixture, theta: str, target_class: str, target_name: str) -> bool:
    target = fixture.target_classes[target_class]
    return (
        package_carried_provenance(fixture, theta)
        and any(
            top_down_kernel_gate_certified(fixture, gate, theta, target.challenge_class)
            for gate in fixture.gate_inventory.get((theta, target.challenge_class), ())
        )
        and route_substitution_persistence_certified(fixture, theta, target_class, target_name)
    )


def cognitive_status_record_matches_claim(
    claim: CognitiveClaimRef,
    record: CognitiveStatusRecord,
) -> bool:
    return record.package_record == claim.package and record.challenge_class == claim.challenge_class


def cognitive_status_occurrence_for(
    fixture: Fixture,
    claim: CognitiveClaimRef,
    record: CognitiveStatusRecord,
) -> bool:
    return cognitive_status_record_matches_claim(claim, record) and _record_carried(record)


def intention_status_record_matches_claim(
    claim: IntentionClaimRef,
    record: IntentionStatusRecord,
) -> bool:
    return record.theta == claim.theta and record.target_class == claim.target_class


def intention_status_occurrence_for(
    fixture: Fixture,
    claim: IntentionClaimRef,
    record: IntentionStatusRecord,
) -> bool:
    return intention_status_record_matches_claim(claim, record) and _record_carried(record)


def goal_status_record_matches_claim(claim: GoalClaimRef, record: GoalStatusRecord) -> bool:
    return record.theta == claim.theta and record.target_class == claim.target_class


def goal_status_occurrence_for(fixture: Fixture, claim: GoalClaimRef, record: GoalStatusRecord) -> bool:
    return goal_status_record_matches_claim(claim, record) and _record_carried(record)


def schedule_trap_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    if not (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.schedule_trap
        and record.schedule_record is not None
    ):
        return False
    schedule = fixture.schedules[record.schedule_record]
    supports = fixture.schedule_witness_supports.get((record.schedule_record, claim.package))
    return (
        schedule.challenge_class == claim.challenge_class
        and supports is not None
        and fixture.supports[supports[0]].package_record == claim.package
        and fixture.supports[supports[1]].package_record == claim.package
        and fixture.supports[supports[0]].challenge_class == claim.challenge_class
        and fixture.supports[supports[1]].challenge_class == claim.challenge_class
        and fixture.ctx.schedule_explains_kernel_change(fixture, record.schedule_record, supports[0], supports[1])
        and no_accepted_top_down_gate_for(fixture, claim.package, claim.challenge_class)
    )


def scaffolding_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    return (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.scaffolding
        and not schedule_trap_case(fixture, claim, record)
        and fixture.packages[claim.package].declared_class == claim.challenge_class
        and no_carried_package_provenance_for(fixture, claim.package)
    )


def structural_path_only_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    if not (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.structural_path_only
        and not schedule_trap_case(fixture, claim, record)
        and not scaffolding_case(fixture, claim, record)
        and record.structural_path_record is not None
    ):
        return False
    path = fixture.structural_paths[record.structural_path_record]
    channel = fixture.channels[path.channel_record]
    support1 = fixture.supports[path.support1]
    support2 = fixture.supports[path.support2]
    return (
        path.package_record == claim.package
        and path.challenge_class == claim.challenge_class
        and support1.package_record == claim.package
        and support2.package_record == claim.package
        and support1.challenge_class == claim.challenge_class
        and support2.challenge_class == claim.challenge_class
        and struct_down(channel)
        and top_down_channel_claim_status(channel) is ClaimStatus.blocked
        and fixture.ctx.kernel_support_differs(fixture, path.support1, path.support2)
    )


def decodable_correlate_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    return (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.decodable_correlate
        and not schedule_trap_case(fixture, claim, record)
        and not scaffolding_case(fixture, claim, record)
        and not structural_path_only_case(fixture, claim, record)
        and record.decodability_record is not None
        and fixture.ctx.decodes_package(
            fixture.readouts[record.decodability_record],
            claim.package,
            claim.challenge_class,
        )
        and no_accepted_top_down_gate_for(fixture, claim.package, claim.challenge_class)
    )


def repair_without_gate_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    return (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.repair_without_gate
        and not schedule_trap_case(fixture, claim, record)
        and not scaffolding_case(fixture, claim, record)
        and not structural_path_only_case(fixture, claim, record)
        and not decodable_correlate_case(fixture, claim, record)
        and record.descent_record is not None
        and package_repair_descent(fixture, record.descent_record, claim.package, claim.challenge_class)
        and no_accepted_top_down_gate_for(fixture, claim.package, claim.challenge_class)
    )


def gate_without_repair_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    return (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.gate_without_repair
        and not schedule_trap_case(fixture, claim, record)
        and not scaffolding_case(fixture, claim, record)
        and not structural_path_only_case(fixture, claim, record)
        and not decodable_correlate_case(fixture, claim, record)
        and not repair_without_gate_case(fixture, claim, record)
        and record.channel_record is not None
        and any(
            fixture.gates[gate].channel_record == record.channel_record
            and top_down_kernel_gate_certified(fixture, gate, claim.package, claim.challenge_class)
            for gate in fixture.gates
        )
        and no_package_repair_descent_for(fixture, claim.package, claim.challenge_class)
    )


def cognitive_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    return (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.cognitive
        and not schedule_trap_case(fixture, claim, record)
        and not scaffolding_case(fixture, claim, record)
        and not structural_path_only_case(fixture, claim, record)
        and not decodable_correlate_case(fixture, claim, record)
        and not repair_without_gate_case(fixture, claim, record)
        and not gate_without_repair_case(fixture, claim, record)
        and record.descent_record is not None
        and record.channel_record is not None
        and package_carried_provenance(fixture, claim.package)
        and package_repair_descent(fixture, record.descent_record, claim.package, claim.challenge_class)
        and any(
            fixture.gates[gate].channel_record == record.channel_record
            and top_down_kernel_gate_certified(fixture, gate, claim.package, claim.challenge_class)
            for gate in fixture.gates
        )
    )


def non_cognitive_case(fixture: Fixture, claim: CognitiveClaimRef, record: CognitiveStatusRecord) -> bool:
    return (
        cognitive_status_occurrence_for(fixture, claim, record)
        and record.status is CognitiveStatus.non_cognitive
        and not schedule_trap_case(fixture, claim, record)
        and not scaffolding_case(fixture, claim, record)
        and not structural_path_only_case(fixture, claim, record)
        and not decodable_correlate_case(fixture, claim, record)
        and not repair_without_gate_case(fixture, claim, record)
        and not gate_without_repair_case(fixture, claim, record)
        and not cognitive_case(fixture, claim, record)
    )


COGNITIVE_CASES = {
    CognitiveStatus.schedule_trap.value: schedule_trap_case,
    CognitiveStatus.scaffolding.value: scaffolding_case,
    CognitiveStatus.structural_path_only.value: structural_path_only_case,
    CognitiveStatus.decodable_correlate.value: decodable_correlate_case,
    CognitiveStatus.repair_without_gate.value: repair_without_gate_case,
    CognitiveStatus.gate_without_repair.value: gate_without_repair_case,
    CognitiveStatus.cognitive.value: cognitive_case,
    CognitiveStatus.non_cognitive.value: non_cognitive_case,
}


def post_hoc_intention_case(fixture: Fixture, claim: IntentionClaimRef, record: IntentionStatusRecord) -> bool:
    if not (
        intention_status_occurrence_for(fixture, claim, record)
        and record.status is IntentionStatus.post_hoc_intention
        and record.restriction_record is not None
    ):
        return False
    restriction = fixture.restrictions[record.restriction_record]
    return (
        restriction.theta == claim.theta
        and restriction.target_class == claim.target_class
        and _record_carried(restriction)
        and not (restriction.restriction_time < restriction.outcome_time)
    )


def approximate_support_defect_case(fixture: Fixture, claim: IntentionClaimRef, record: IntentionStatusRecord) -> bool:
    if not (
        intention_status_occurrence_for(fixture, claim, record)
        and record.status is IntentionStatus.approximate_support_defect
        and not post_hoc_intention_case(fixture, claim, record)
        and record.restriction_record is not None
    ):
        return False
    restriction = fixture.restrictions[record.restriction_record]
    return (
        restriction.theta == claim.theta
        and restriction.target_class == claim.target_class
        and _record_carried(restriction)
        and fixture.ctx.approximate_support_restriction(fixture, record.restriction_record)
        and not fixture.ctx.support_strict_subset(fixture, restriction.restricted_support, restriction.unrestricted_support)
    )


def target_incoherent_restriction_case(
    fixture: Fixture,
    claim: IntentionClaimRef,
    record: IntentionStatusRecord,
) -> bool:
    if not (
        intention_status_occurrence_for(fixture, claim, record)
        and record.status is IntentionStatus.target_incoherent_restriction
        and not post_hoc_intention_case(fixture, claim, record)
        and not approximate_support_defect_case(fixture, claim, record)
        and record.restriction_record is not None
    ):
        return False
    restriction = fixture.restrictions[record.restriction_record]
    probes = fixture.restriction_probes.get(record.restriction_record, ())
    return (
        restriction.theta == claim.theta
        and restriction.target_class == claim.target_class
        and _record_carried(restriction)
        and any(
            fixture.probes[probe].target_class == claim.target_class
            and _record_carried(fixture.probes[probe])
            and not fixture.ctx.target_coherent_under_probe(
                fixture,
                claim.target_class,
                probe,
                record.restriction_record,
            )
            for probe in probes
        )
    )


def intention_case(fixture: Fixture, claim: IntentionClaimRef, record: IntentionStatusRecord) -> bool:
    return (
        intention_status_occurrence_for(fixture, claim, record)
        and record.status is IntentionStatus.intention
        and not post_hoc_intention_case(fixture, claim, record)
        and not approximate_support_defect_case(fixture, claim, record)
        and not target_incoherent_restriction_case(fixture, claim, record)
        and record.restriction_record is not None
        and intention_evidence(fixture, claim.theta, claim.target_class, record.restriction_record)
    )


def not_intention_case(fixture: Fixture, claim: IntentionClaimRef, record: IntentionStatusRecord) -> bool:
    return (
        intention_status_occurrence_for(fixture, claim, record)
        and record.status is IntentionStatus.not_intention
        and not post_hoc_intention_case(fixture, claim, record)
        and not approximate_support_defect_case(fixture, claim, record)
        and not target_incoherent_restriction_case(fixture, claim, record)
        and not intention_case(fixture, claim, record)
    )


INTENTION_CASES = {
    IntentionStatus.post_hoc_intention.value: post_hoc_intention_case,
    IntentionStatus.approximate_support_defect.value: approximate_support_defect_case,
    IntentionStatus.target_incoherent_restriction.value: target_incoherent_restriction_case,
    IntentionStatus.intention.value: intention_case,
    IntentionStatus.not_intention.value: not_intention_case,
}


def reward_proxy_only_case(fixture: Fixture, claim: GoalClaimRef, record: GoalStatusRecord) -> bool:
    return (
        goal_status_occurrence_for(fixture, claim, record)
        and record.status is GoalStatus.reward_proxy_only
        and record.reward_proxy is not None
        and record.target_quotient is not None
        and goal_target_selection(fixture, record.target_quotient, claim.theta, claim.target_class)
        and _record_carried(fixture.reward_proxies[record.reward_proxy])
        and fixture.ctx.reward_proxy_explains_selection(fixture, record.reward_proxy, record.target_quotient)
        and no_route_persistence_for(fixture, record.target_quotient)
    )


def route_unstable_case(fixture: Fixture, claim: GoalClaimRef, record: GoalStatusRecord) -> bool:
    if not (
        goal_status_occurrence_for(fixture, claim, record)
        and record.status is GoalStatus.route_unstable
        and not reward_proxy_only_case(fixture, claim, record)
        and record.target_quotient is not None
    ):
        return False
    routes = fixture.route_sets.get(record.target_quotient, ())
    evaluations = tuple(record.route_evaluations)
    return (
        goal_target_selection(fixture, record.target_quotient, claim.theta, claim.target_class)
        and len(set(routes)) >= 2
        and every_route_evaluated(fixture, record.target_quotient, routes, evaluations)
        and all(_record_carried(fixture.routes[route]) for route in routes)
        and all(_record_carried(fixture.evaluations[eval_name]) for eval_name in evaluations)
        and not fixture.ctx.route_selection_persists(fixture, record.target_quotient, evaluations)
    )


def goal_case(fixture: Fixture, claim: GoalClaimRef, record: GoalStatusRecord) -> bool:
    return (
        goal_status_occurrence_for(fixture, claim, record)
        and record.status is GoalStatus.goal
        and not reward_proxy_only_case(fixture, claim, record)
        and not route_unstable_case(fixture, claim, record)
        and record.target_quotient is not None
        and tuple(record.route_evaluations) == fixture.route_evaluation_sets.get(record.target_quotient, ())
        and goal_evidence(fixture, claim.theta, claim.target_class, record.target_quotient)
    )


def not_goal_case(fixture: Fixture, claim: GoalClaimRef, record: GoalStatusRecord) -> bool:
    return (
        goal_status_occurrence_for(fixture, claim, record)
        and record.status is GoalStatus.not_goal
        and not reward_proxy_only_case(fixture, claim, record)
        and not route_unstable_case(fixture, claim, record)
        and not goal_case(fixture, claim, record)
    )


GOAL_CASES = {
    GoalStatus.reward_proxy_only.value: reward_proxy_only_case,
    GoalStatus.route_unstable.value: route_unstable_case,
    GoalStatus.goal.value: goal_case,
    GoalStatus.not_goal.value: not_goal_case,
}


def _matching_cognitive_records(fixture: Fixture, claim: CognitiveClaimRef) -> tuple[CognitiveStatusRecord, ...]:
    return tuple(
        record
        for record in fixture.cognitive_status_records.values()
        if cognitive_status_occurrence_for(fixture, claim, record)
    )


def classify_cognitive_status(
    fixture: Fixture,
    claim_name: str,
) -> tuple[CognitiveStatus, dict[str, bool], CognitiveStatusRecord | None]:
    claim = fixture.cognitive_claims[claim_name]
    records = _matching_cognitive_records(fixture, claim)
    truths = {name: False for name in COGNITIVE_CASES}
    for record in records:
        for name, fn in COGNITIVE_CASES.items():
            if fn(fixture, claim, record):
                truths[name] = True
                return CognitiveStatus(name), truths, record
    return CognitiveStatus.unclassified, truths, records[0] if records else None


def classify_intention_status(
    fixture: Fixture,
    claim_name: str,
) -> tuple[IntentionStatus, dict[str, bool], IntentionStatusRecord | None]:
    claim = fixture.intention_claims[claim_name]
    records = tuple(
        record
        for record in fixture.intention_status_records.values()
        if intention_status_occurrence_for(fixture, claim, record)
    )
    truths = {name: False for name in INTENTION_CASES}
    for record in records:
        for name, fn in INTENTION_CASES.items():
            if fn(fixture, claim, record):
                truths[name] = True
                return IntentionStatus(name), truths, record
    return IntentionStatus.unclassified, truths, records[0] if records else None


def classify_goal_status(
    fixture: Fixture,
    claim_name: str,
) -> tuple[GoalStatus, dict[str, bool], GoalStatusRecord | None]:
    claim = fixture.goal_claims[claim_name]
    records = tuple(
        record
        for record in fixture.goal_status_records.values()
        if goal_status_occurrence_for(fixture, claim, record)
    )
    truths = {name: False for name in GOAL_CASES}
    for record in records:
        for name, fn in GOAL_CASES.items():
            if fn(fixture, claim, record):
                truths[name] = True
                return GoalStatus(name), truths, record
    return GoalStatus.unclassified, truths, records[0] if records else None


EXPECTED_COGNITIVE_STATUSES = {
    "claim_pkg_nav_cognitive": CognitiveStatus.cognitive,
    "claim_pkg_passive_non_cognitive": CognitiveStatus.non_cognitive,
    "claim_pkg_schedule_trap": CognitiveStatus.schedule_trap,
    "claim_pkg_external_scaffold": CognitiveStatus.scaffolding,
    "claim_pkg_structural_path": CognitiveStatus.structural_path_only,
    "claim_pkg_decodable": CognitiveStatus.decodable_correlate,
    "claim_pkg_repair_no_gate": CognitiveStatus.repair_without_gate,
    "claim_pkg_gate_no_repair": CognitiveStatus.gate_without_repair,
    "ctrl_decodable_priority_blocks_cognitive": CognitiveStatus.decodable_correlate,
    "ctrl_schedule_priority_blocks_cognitive": CognitiveStatus.schedule_trap,
}

EXPECTED_INTENTION_STATUSES = {
    "claim_intention_clean": IntentionStatus.intention,
    "claim_intention_neutral": IntentionStatus.not_intention,
    "claim_intention_posthoc": IntentionStatus.post_hoc_intention,
    "claim_intention_approximate": IntentionStatus.approximate_support_defect,
    "claim_intention_target_incoherent": IntentionStatus.target_incoherent_restriction,
    "ctrl_post_hoc_priority_blocks_intention": IntentionStatus.post_hoc_intention,
    "ctrl_uncarried_intention_rejected": IntentionStatus.not_intention,
}

EXPECTED_GOAL_STATUSES = {
    "claim_goal_clean": GoalStatus.goal,
    "claim_goal_neutral": GoalStatus.not_goal,
    "claim_goal_reward_proxy_only": GoalStatus.reward_proxy_only,
    "claim_goal_route_unstable": GoalStatus.route_unstable,
    "ctrl_reward_proxy_priority_blocks_goal": GoalStatus.reward_proxy_only,
    "ctrl_every_route_evaluated_universal": GoalStatus.not_goal,
    "ctrl_uncarried_goal_rejected": GoalStatus.not_goal,
}


def _accepted_channel(name: str) -> TopDownChannelRecord:
    return TopDownChannelRecord(name=name, structural_path_present=True)


def _structural_only_channel(name: str) -> TopDownChannelRecord:
    return TopDownChannelRecord(
        name=name,
        structural_path_present=True,
        intervention_gate=False,
        effect_gate=False,
    )


def build_fixture() -> Fixture:
    ctx = CognitiveDemarcationClassifierContext()
    classes = {
        "C_nav": CognitiveChallengeClass("C_nav", 1),
        "C_memory": CognitiveChallengeClass("C_memory", 2),
        "C_planning": CognitiveChallengeClass("C_planning", 3),
        "C_other": CognitiveChallengeClass("C_other", 4),
    }
    target_classes = {
        "T_nav": TargetClassRecord("T_nav", 101, "C_nav"),
        "T_plan": TargetClassRecord("T_plan", 102, "C_planning"),
        "T_other": TargetClassRecord("T_other", 103, "C_other"),
    }

    packages: dict[str, CognitivePackageRecord] = {
        "pkg_nav_cognitive": CognitivePackageRecord("pkg_nav_cognitive", 10, 10, "C_nav"),
        "pkg_passive_memory": CognitivePackageRecord("pkg_passive_memory", 11, 11, "C_memory"),
        "pkg_schedule_trap": CognitivePackageRecord("pkg_schedule_trap", 12, 12, "C_nav"),
        "pkg_external_scaffold": CognitivePackageRecord("pkg_external_scaffold", 13, 13, "C_nav", carried=False),
        "pkg_structural_path": CognitivePackageRecord("pkg_structural_path", 14, 14, "C_nav"),
        "pkg_decodable": CognitivePackageRecord("pkg_decodable", 15, 15, "C_memory"),
        "pkg_repair_no_gate": CognitivePackageRecord("pkg_repair_no_gate", 16, 16, "C_nav"),
        "pkg_gate_no_repair": CognitivePackageRecord("pkg_gate_no_repair", 17, 17, "C_nav"),
        "pkg_priority_decodable": CognitivePackageRecord("pkg_priority_decodable", 18, 18, "C_memory"),
        "pkg_priority_schedule": CognitivePackageRecord("pkg_priority_schedule", 19, 19, "C_nav"),
        "pkg_other_repair": CognitivePackageRecord("pkg_other_repair", 20, 20, "C_other"),
        "theta_intention": CognitivePackageRecord("theta_intention", 30, 30, "C_planning"),
        "theta_neutral": CognitivePackageRecord("theta_neutral", 31, 31, "C_planning"),
        "theta_posthoc": CognitivePackageRecord("theta_posthoc", 32, 32, "C_planning"),
        "theta_approx": CognitivePackageRecord("theta_approx", 33, 33, "C_planning"),
        "theta_incoherent": CognitivePackageRecord("theta_incoherent", 34, 34, "C_planning"),
        "theta_priority_posthoc": CognitivePackageRecord("theta_priority_posthoc", 35, 35, "C_planning"),
        "theta_uncarried_intention": CognitivePackageRecord("theta_uncarried_intention", 36, 36, "C_planning", carried=False),
        "theta_goal": CognitivePackageRecord("theta_goal", 40, 40, "C_planning"),
        "theta_not_goal": CognitivePackageRecord("theta_not_goal", 41, 41, "C_planning"),
        "theta_reward_proxy": CognitivePackageRecord("theta_reward_proxy", 42, 42, "C_planning"),
        "theta_route_unstable": CognitivePackageRecord("theta_route_unstable", 43, 43, "C_planning"),
        "theta_missing_eval": CognitivePackageRecord("theta_missing_eval", 44, 44, "C_planning"),
        "theta_priority_reward": CognitivePackageRecord("theta_priority_reward", 45, 45, "C_planning"),
        "theta_uncarried_goal": CognitivePackageRecord("theta_uncarried_goal", 46, 46, "C_planning", carried=False),
    }
    formations = {
        f"form_{name}": PackageFormationRecord(f"form_{name}", 1000 + pkg.record_id, name, carried=pkg.carried)
        for name, pkg in packages.items()
    }
    invocations = {
        f"invoke_{name}": PackageInvocationRecord(
            f"invoke_{name}",
            2000 + pkg.record_id,
            name,
            pkg.declared_class,
            carried=pkg.carried,
        )
        for name, pkg in packages.items()
    }

    quotient_names = {
        "q_nav_before": "C_nav",
        "q_nav_after": "C_nav",
        "q_repair_before": "C_nav",
        "q_repair_after": "C_nav",
        "q_pr_dec_before": "C_memory",
        "q_pr_dec_after": "C_memory",
        "q_pr_sched_before": "C_nav",
        "q_pr_sched_after": "C_nav",
        "q_other_before": "C_other",
        "q_other_after": "C_other",
        "q_goal_before_a": "C_planning",
        "q_goal_after_a": "C_planning",
        "q_goal_before_b": "C_planning",
        "q_goal_after_b": "C_planning",
        "q_unstable_before_a": "C_planning",
        "q_unstable_after_a": "C_planning",
        "q_unstable_before_b": "C_planning",
        "q_unstable_after_b": "C_planning",
        "q_missing_before_a": "C_planning",
        "q_missing_after_a": "C_planning",
        "q_missing_before_b": "C_planning",
        "q_uncarried_goal_before_a": "C_planning",
        "q_uncarried_goal_after_a": "C_planning",
        "q_uncarried_goal_before_b": "C_planning",
        "q_uncarried_goal_after_b": "C_planning",
    }
    quotients = {
        name: PackageQuotientRecord(name, index, challenge)
        for index, (name, challenge) in enumerate(quotient_names.items(), start=1)
    }
    descents = {
        "desc_nav_cognitive": DescentWitnessRecord("desc_nav_cognitive", 1, "pkg_nav_cognitive", "q_nav_before", "q_nav_after", "C_nav"),
        "desc_repair_no_gate": DescentWitnessRecord("desc_repair_no_gate", 2, "pkg_repair_no_gate", "q_repair_before", "q_repair_after", "C_nav"),
        "desc_priority_decodable": DescentWitnessRecord("desc_priority_decodable", 3, "pkg_priority_decodable", "q_pr_dec_before", "q_pr_dec_after", "C_memory"),
        "desc_priority_schedule": DescentWitnessRecord("desc_priority_schedule", 4, "pkg_priority_schedule", "q_pr_sched_before", "q_pr_sched_after", "C_nav"),
        "desc_other_real": DescentWitnessRecord("desc_other_real", 5, "pkg_other_repair", "q_other_before", "q_other_after", "C_other"),
    }
    delta_splits = {
        ("q_nav_before", "C_nav"): frozenset({"a", "b", "c"}),
        ("q_nav_after", "C_nav"): frozenset({"a"}),
        ("q_repair_before", "C_nav"): frozenset({"d", "e"}),
        ("q_repair_after", "C_nav"): frozenset({"d"}),
        ("q_pr_dec_before", "C_memory"): frozenset({"m1", "m2"}),
        ("q_pr_dec_after", "C_memory"): frozenset({"m1"}),
        ("q_pr_sched_before", "C_nav"): frozenset({"s1", "s2"}),
        ("q_pr_sched_after", "C_nav"): frozenset({"s1"}),
        ("q_other_before", "C_other"): frozenset({"x", "y"}),
        ("q_other_after", "C_other"): frozenset({"x"}),
        ("q_goal_before_a", "C_planning"): frozenset({"r1", "r2"}),
        ("q_goal_after_a", "C_planning"): frozenset({"r1"}),
        ("q_goal_before_b", "C_planning"): frozenset({"r3", "r4"}),
        ("q_goal_after_b", "C_planning"): frozenset({"r3"}),
        ("q_unstable_before_a", "C_planning"): frozenset({"u1", "u2"}),
        ("q_unstable_after_a", "C_planning"): frozenset({"u1"}),
        ("q_unstable_before_b", "C_planning"): frozenset({"u3", "u4"}),
        ("q_unstable_after_b", "C_planning"): frozenset({"u3"}),
        ("q_missing_before_a", "C_planning"): frozenset({"m1", "m2"}),
        ("q_missing_after_a", "C_planning"): frozenset({"m1"}),
        ("q_missing_before_b", "C_planning"): frozenset({"m3", "m4"}),
        ("q_uncarried_goal_before_a", "C_planning"): frozenset({"cg1", "cg2"}),
        ("q_uncarried_goal_after_a", "C_planning"): frozenset({"cg1"}),
        ("q_uncarried_goal_before_b", "C_planning"): frozenset({"cg3", "cg4"}),
        ("q_uncarried_goal_after_b", "C_planning"): frozenset({"cg3"}),
    }
    install_map = {
        ("pkg_nav_cognitive", "q_nav_before"): "q_nav_after",
        ("pkg_repair_no_gate", "q_repair_before"): "q_repair_after",
        ("pkg_priority_decodable", "q_pr_dec_before"): "q_pr_dec_after",
        ("pkg_priority_schedule", "q_pr_sched_before"): "q_pr_sched_after",
        ("pkg_other_repair", "q_other_before"): "q_other_after",
    }

    supports = {
        "supp_nav_val0": KernelSupportRecord("supp_nav_val0", 300, AccessActionKind.access, "pkg_nav_cognitive", "C_nav", 300, frozenset({"n0", "n1", "n2"})),
        "supp_nav_val1": KernelSupportRecord("supp_nav_val1", 301, AccessActionKind.access, "pkg_nav_cognitive", "C_nav", 301, frozenset({"n0", "n2"})),
        "supp_gate_val0": KernelSupportRecord("supp_gate_val0", 302, AccessActionKind.access, "pkg_gate_no_repair", "C_nav", 302, frozenset({"g0", "g1"})),
        "supp_gate_val1": KernelSupportRecord("supp_gate_val1", 303, AccessActionKind.access, "pkg_gate_no_repair", "C_nav", 303, frozenset({"g0"})),
        "supp_action_unrestricted": KernelSupportRecord("supp_action_unrestricted", 304, AccessActionKind.action, "theta_intention", "C_planning", 304, frozenset({"act0", "act1", "act2"})),
        "supp_action_restricted": KernelSupportRecord("supp_action_restricted", 305, AccessActionKind.action, "theta_intention", "C_planning", 305, frozenset({"act1"})),
        "supp_action_approx": KernelSupportRecord("supp_action_approx", 306, AccessActionKind.action, "theta_approx", "C_planning", 306, frozenset({"act0", "act1", "act2"})),
        "supp_action_posthoc": KernelSupportRecord("supp_action_posthoc", 307, AccessActionKind.action, "theta_posthoc", "C_planning", 307, frozenset({"act1"})),
        "supp_goal_route0": KernelSupportRecord("supp_goal_route0", 308, AccessActionKind.action, "theta_goal", "C_planning", 308, frozenset({"route0", "route1"})),
        "supp_goal_route1": KernelSupportRecord("supp_goal_route1", 309, AccessActionKind.action, "theta_goal", "C_planning", 309, frozenset({"route1"})),
        "supp_wrong_for_intervention": KernelSupportRecord("supp_wrong_for_intervention", 310, AccessActionKind.access, "pkg_nav_cognitive", "C_nav", 310, frozenset({"n0", "n1"})),
        "supp_sched_before": KernelSupportRecord("supp_sched_before", 311, AccessActionKind.access, "pkg_schedule_trap", "C_nav", 311, frozenset({"s0", "s1"})),
        "supp_sched_after": KernelSupportRecord("supp_sched_after", 312, AccessActionKind.access, "pkg_schedule_trap", "C_nav", 312, frozenset({"s1"})),
        "supp_struct_before": KernelSupportRecord("supp_struct_before", 313, AccessActionKind.access, "pkg_structural_path", "C_nav", 313, frozenset({"st0", "st1"})),
        "supp_struct_after": KernelSupportRecord("supp_struct_after", 314, AccessActionKind.access, "pkg_structural_path", "C_nav", 314, frozenset({"st1"})),
        "supp_priority_sched_before": KernelSupportRecord("supp_priority_sched_before", 315, AccessActionKind.access, "pkg_priority_schedule", "C_nav", 315, frozenset({"ps0", "ps1"})),
        "supp_priority_sched_after": KernelSupportRecord("supp_priority_sched_after", 316, AccessActionKind.access, "pkg_priority_schedule", "C_nav", 316, frozenset({"ps1"})),
    }
    interventions = {
        "int_nav_value0": PackageInterventionRecord("int_nav_value0", 400, "pkg_nav_cognitive", 0, 0),
        "int_nav_value1": PackageInterventionRecord("int_nav_value1", 401, "pkg_nav_cognitive", 1, 1),
        "int_gate_value0": PackageInterventionRecord("int_gate_value0", 402, "pkg_gate_no_repair", 0, 0),
        "int_gate_value1": PackageInterventionRecord("int_gate_value1", 403, "pkg_gate_no_repair", 1, 1),
        "int_intention_value0": PackageInterventionRecord("int_intention_value0", 404, "theta_intention", 0, 0),
        "int_intention_value1": PackageInterventionRecord("int_intention_value1", 405, "theta_intention", 1, 1),
        "int_goal_value0": PackageInterventionRecord("int_goal_value0", 406, "theta_goal", 0, 0),
        "int_goal_value1": PackageInterventionRecord("int_goal_value1", 407, "theta_goal", 1, 1),
    }
    matched_controls = {
        "match_nav": MatchedControlRecord("match_nav", 500, "int_nav_value0", "int_nav_value1", "C_nav"),
        "match_gate": MatchedControlRecord("match_gate", 501, "int_gate_value0", "int_gate_value1", "C_nav"),
        "match_intention": MatchedControlRecord("match_intention", 502, "int_intention_value0", "int_intention_value1", "C_planning"),
        "match_goal": MatchedControlRecord("match_goal", 503, "int_goal_value0", "int_goal_value1", "C_planning"),
    }
    channels = {
        "tdc_accept_nav": _accepted_channel("tdc_accept_nav"),
        "tdc_accept_intention": _accepted_channel("tdc_accept_intention"),
        "tdc_accept_goal": _accepted_channel("tdc_accept_goal"),
        "tdc_structural_only": _structural_only_channel("tdc_structural_only"),
    }
    gates = {
        "gate_nav_cognitive": TopDownGateCandidate("gate_nav_cognitive", "pkg_nav_cognitive", "C_nav", "tdc_accept_nav", "int_nav_value0", "int_nav_value1", "match_nav", "supp_nav_val0", "supp_nav_val1"),
        "gate_gate_no_repair": TopDownGateCandidate("gate_gate_no_repair", "pkg_gate_no_repair", "C_nav", "tdc_accept_nav", "int_gate_value0", "int_gate_value1", "match_gate", "supp_gate_val0", "supp_gate_val1"),
        "gate_intention": TopDownGateCandidate("gate_intention", "theta_intention", "C_planning", "tdc_accept_intention", "int_intention_value0", "int_intention_value1", "match_intention", "supp_action_unrestricted", "supp_action_restricted"),
        "gate_goal": TopDownGateCandidate("gate_goal", "theta_goal", "C_planning", "tdc_accept_goal", "int_goal_value0", "int_goal_value1", "match_goal", "supp_goal_route0", "supp_goal_route1"),
    }
    support_link = {
        "int_nav_value0": "supp_nav_val0",
        "int_nav_value1": "supp_nav_val1",
        "int_gate_value0": "supp_gate_val0",
        "int_gate_value1": "supp_gate_val1",
        "int_intention_value0": "supp_action_unrestricted",
        "int_intention_value1": "supp_action_restricted",
        "int_goal_value0": "supp_goal_route0",
        "int_goal_value1": "supp_goal_route1",
    }

    readouts = {
        "readout_decodable": DecodabilityReadoutRecord("readout_decodable", 600, "pkg_decodable", "C_memory"),
        "readout_priority_decodable": DecodabilityReadoutRecord("readout_priority_decodable", 601, "pkg_priority_decodable", "C_memory"),
    }
    schedules = {"schedule_nav_exogenous": ExogenousScheduleRecord("schedule_nav_exogenous", 700, "C_nav", 700)}
    structural_paths = {
        "path_structural_only": StructuralPathRecord("path_structural_only", 800, "pkg_structural_path", "C_nav", "tdc_structural_only", "supp_struct_before", "supp_struct_after")
    }
    restrictions = {
        "restrict_intention": ActionSupportRestrictionRecord("restrict_intention", 900, "theta_intention", "T_plan", "supp_action_unrestricted", "supp_action_restricted", 2, 5),
        "restrict_posthoc": ActionSupportRestrictionRecord("restrict_posthoc", 901, "theta_posthoc", "T_plan", "supp_action_unrestricted", "supp_action_restricted", 8, 5),
        "restrict_approx": ActionSupportRestrictionRecord("restrict_approx", 902, "theta_approx", "T_plan", "supp_action_unrestricted", "supp_action_approx", 2, 5),
        "restrict_incoherent": ActionSupportRestrictionRecord("restrict_incoherent", 903, "theta_incoherent", "T_plan", "supp_action_unrestricted", "supp_action_restricted", 2, 5),
        "restrict_priority_posthoc": ActionSupportRestrictionRecord("restrict_priority_posthoc", 904, "theta_priority_posthoc", "T_plan", "supp_action_unrestricted", "supp_action_restricted", 9, 5),
        "restrict_uncarried_intention": ActionSupportRestrictionRecord("restrict_uncarried_intention", 905, "theta_uncarried_intention", "T_plan", "supp_action_unrestricted", "supp_action_restricted", 2, 5),
    }
    probes = {
        "probe_plan_ok_1": FutureProbeRecord("probe_plan_ok_1", 1001, "T_plan", 1),
        "probe_plan_ok_2": FutureProbeRecord("probe_plan_ok_2", 1002, "T_plan", 2),
        "probe_plan_bad": FutureProbeRecord("probe_plan_bad", 1003, "T_plan", 3),
    }
    target_quotients = {
        "target_goal_plan": TargetQuotientRecord("target_goal_plan", 900, "theta_goal", "T_plan", 900),
        "target_neutral_plan": TargetQuotientRecord("target_neutral_plan", 901, "theta_not_goal", "T_plan", 901),
        "target_reward_plan": TargetQuotientRecord("target_reward_plan", 902, "theta_reward_proxy", "T_plan", 902),
        "target_unstable_plan": TargetQuotientRecord("target_unstable_plan", 903, "theta_route_unstable", "T_plan", 903),
        "target_missing_eval_plan": TargetQuotientRecord("target_missing_eval_plan", 904, "theta_missing_eval", "T_plan", 904),
        "target_priority_reward_plan": TargetQuotientRecord("target_priority_reward_plan", 905, "theta_priority_reward", "T_plan", 905),
        "target_uncarried_goal_plan": TargetQuotientRecord("target_uncarried_goal_plan", 906, "theta_uncarried_goal", "T_plan", 906),
    }
    routes = {
        "route_goal_a": RouteSubstitutionRecord("route_goal_a", 1101, 1, "T_plan"),
        "route_goal_b": RouteSubstitutionRecord("route_goal_b", 1102, 2, "T_plan"),
        "route_unstable_a": RouteSubstitutionRecord("route_unstable_a", 1103, 1, "T_plan"),
        "route_unstable_b": RouteSubstitutionRecord("route_unstable_b", 1104, 2, "T_plan"),
        "route_missing_a": RouteSubstitutionRecord("route_missing_a", 1105, 1, "T_plan"),
        "route_missing_b": RouteSubstitutionRecord("route_missing_b", 1106, 2, "T_plan"),
        "route_uncarried_goal_a": RouteSubstitutionRecord("route_uncarried_goal_a", 1107, 1, "T_plan"),
        "route_uncarried_goal_b": RouteSubstitutionRecord("route_uncarried_goal_b", 1108, 2, "T_plan"),
    }
    evaluations = {
        "eval_goal_a": RouteEvaluationRecord("eval_goal_a", 1201, "route_goal_a", "target_goal_plan", "q_goal_before_a", "q_goal_after_a"),
        "eval_goal_b": RouteEvaluationRecord("eval_goal_b", 1202, "route_goal_b", "target_goal_plan", "q_goal_before_b", "q_goal_after_b"),
        "eval_unstable_a": RouteEvaluationRecord("eval_unstable_a", 1203, "route_unstable_a", "target_unstable_plan", "q_unstable_before_a", "q_unstable_after_a"),
        "eval_unstable_b": RouteEvaluationRecord("eval_unstable_b", 1204, "route_unstable_b", "target_unstable_plan", "q_unstable_before_b", "q_unstable_after_b"),
        "eval_missing_a": RouteEvaluationRecord("eval_missing_a", 1205, "route_missing_a", "target_missing_eval_plan", "q_missing_before_a", "q_missing_after_a"),
        "eval_uncarried_goal_a": RouteEvaluationRecord("eval_uncarried_goal_a", 1206, "route_uncarried_goal_a", "target_uncarried_goal_plan", "q_uncarried_goal_before_a", "q_uncarried_goal_after_a"),
        "eval_uncarried_goal_b": RouteEvaluationRecord("eval_uncarried_goal_b", 1207, "route_uncarried_goal_b", "target_uncarried_goal_plan", "q_uncarried_goal_before_b", "q_uncarried_goal_after_b"),
    }
    reward_proxies = {
        "reward_proxy_only_plan": RewardProxyRecord("reward_proxy_only_plan", 1301, "theta_reward_proxy", F(7, 10)),
        "reward_priority_plan": RewardProxyRecord("reward_priority_plan", 1302, "theta_priority_reward", F(9, 10)),
    }
    gate_inventory = {
        ("pkg_nav_cognitive", "C_nav"): ("gate_nav_cognitive",),
        ("pkg_gate_no_repair", "C_nav"): ("gate_gate_no_repair",),
        ("theta_intention", "C_planning"): ("gate_intention",),
        ("theta_goal", "C_planning"): ("gate_goal",),
    }
    repair_inventory = {
        ("pkg_nav_cognitive", "C_nav"): ("desc_nav_cognitive",),
        ("pkg_repair_no_gate", "C_nav"): ("desc_repair_no_gate",),
        ("pkg_priority_decodable", "C_memory"): ("desc_priority_decodable",),
        ("pkg_priority_schedule", "C_nav"): ("desc_priority_schedule",),
        ("pkg_other_repair", "C_other"): ("desc_other_real",),
    }
    provenance_inventory = {
        name: ((f"form_{name}", f"invoke_{name}"),)
        for name, package in packages.items()
        if package.carried
    }
    provenance_inventory["pkg_external_scaffold"] = ()
    provenance_inventory["theta_uncarried_intention"] = ()
    provenance_inventory["theta_uncarried_goal"] = ()

    cognitive_claims = {
        "claim_pkg_nav_cognitive": CognitiveClaimRef("claim_pkg_nav_cognitive", "pkg_nav_cognitive", "C_nav"),
        "claim_pkg_passive_non_cognitive": CognitiveClaimRef("claim_pkg_passive_non_cognitive", "pkg_passive_memory", "C_memory"),
        "claim_pkg_schedule_trap": CognitiveClaimRef("claim_pkg_schedule_trap", "pkg_schedule_trap", "C_nav"),
        "claim_pkg_external_scaffold": CognitiveClaimRef("claim_pkg_external_scaffold", "pkg_external_scaffold", "C_nav"),
        "claim_pkg_structural_path": CognitiveClaimRef("claim_pkg_structural_path", "pkg_structural_path", "C_nav"),
        "claim_pkg_decodable": CognitiveClaimRef("claim_pkg_decodable", "pkg_decodable", "C_memory"),
        "claim_pkg_repair_no_gate": CognitiveClaimRef("claim_pkg_repair_no_gate", "pkg_repair_no_gate", "C_nav"),
        "claim_pkg_gate_no_repair": CognitiveClaimRef("claim_pkg_gate_no_repair", "pkg_gate_no_repair", "C_nav"),
        "ctrl_decodable_priority_blocks_cognitive": CognitiveClaimRef("ctrl_decodable_priority_blocks_cognitive", "pkg_priority_decodable", "C_memory"),
        "ctrl_schedule_priority_blocks_cognitive": CognitiveClaimRef("ctrl_schedule_priority_blocks_cognitive", "pkg_priority_schedule", "C_nav"),
        "ctrl_wrong_class_claim": CognitiveClaimRef("ctrl_wrong_class_claim", "pkg_other_repair", "C_nav"),
    }
    intention_claims = {
        "claim_intention_clean": IntentionClaimRef("claim_intention_clean", "theta_intention", "T_plan"),
        "claim_intention_neutral": IntentionClaimRef("claim_intention_neutral", "theta_neutral", "T_plan"),
        "claim_intention_posthoc": IntentionClaimRef("claim_intention_posthoc", "theta_posthoc", "T_plan"),
        "claim_intention_approximate": IntentionClaimRef("claim_intention_approximate", "theta_approx", "T_plan"),
        "claim_intention_target_incoherent": IntentionClaimRef("claim_intention_target_incoherent", "theta_incoherent", "T_plan"),
        "ctrl_post_hoc_priority_blocks_intention": IntentionClaimRef("ctrl_post_hoc_priority_blocks_intention", "theta_priority_posthoc", "T_plan"),
        "ctrl_uncarried_intention_rejected": IntentionClaimRef("ctrl_uncarried_intention_rejected", "theta_uncarried_intention", "T_plan"),
    }
    goal_claims = {
        "claim_goal_clean": GoalClaimRef("claim_goal_clean", "theta_goal", "T_plan"),
        "claim_goal_neutral": GoalClaimRef("claim_goal_neutral", "theta_not_goal", "T_plan"),
        "claim_goal_reward_proxy_only": GoalClaimRef("claim_goal_reward_proxy_only", "theta_reward_proxy", "T_plan"),
        "claim_goal_route_unstable": GoalClaimRef("claim_goal_route_unstable", "theta_route_unstable", "T_plan"),
        "ctrl_reward_proxy_priority_blocks_goal": GoalClaimRef("ctrl_reward_proxy_priority_blocks_goal", "theta_priority_reward", "T_plan"),
        "ctrl_every_route_evaluated_universal": GoalClaimRef("ctrl_every_route_evaluated_universal", "theta_missing_eval", "T_plan"),
        "ctrl_uncarried_goal_rejected": GoalClaimRef("ctrl_uncarried_goal_rejected", "theta_uncarried_goal", "T_plan"),
    }
    cognitive_status_records = {
        "status_pkg_nav_cognitive": CognitiveStatusRecord("status_pkg_nav_cognitive", CognitiveStatus.cognitive, "pkg_nav_cognitive", "C_nav", descent_record="desc_nav_cognitive", channel_record="tdc_accept_nav"),
        "status_pkg_passive_non_cognitive": CognitiveStatusRecord("status_pkg_passive_non_cognitive", CognitiveStatus.non_cognitive, "pkg_passive_memory", "C_memory"),
        "status_pkg_schedule_trap": CognitiveStatusRecord("status_pkg_schedule_trap", CognitiveStatus.schedule_trap, "pkg_schedule_trap", "C_nav", schedule_record="schedule_nav_exogenous"),
        "status_pkg_external_scaffold": CognitiveStatusRecord("status_pkg_external_scaffold", CognitiveStatus.scaffolding, "pkg_external_scaffold", "C_nav"),
        "status_pkg_structural_path": CognitiveStatusRecord("status_pkg_structural_path", CognitiveStatus.structural_path_only, "pkg_structural_path", "C_nav", structural_path_record="path_structural_only"),
        "status_pkg_decodable": CognitiveStatusRecord("status_pkg_decodable", CognitiveStatus.decodable_correlate, "pkg_decodable", "C_memory", decodability_record="readout_decodable"),
        "status_pkg_repair_no_gate": CognitiveStatusRecord("status_pkg_repair_no_gate", CognitiveStatus.repair_without_gate, "pkg_repair_no_gate", "C_nav", descent_record="desc_repair_no_gate"),
        "status_pkg_gate_no_repair": CognitiveStatusRecord("status_pkg_gate_no_repair", CognitiveStatus.gate_without_repair, "pkg_gate_no_repair", "C_nav", channel_record="tdc_accept_nav"),
        "status_priority_decodable": CognitiveStatusRecord("status_priority_decodable", CognitiveStatus.decodable_correlate, "pkg_priority_decodable", "C_memory", decodability_record="readout_priority_decodable"),
        "status_priority_schedule": CognitiveStatusRecord("status_priority_schedule", CognitiveStatus.schedule_trap, "pkg_priority_schedule", "C_nav", schedule_record="schedule_nav_exogenous"),
        "status_wrong_class_non_cognitive": CognitiveStatusRecord("status_wrong_class_non_cognitive", CognitiveStatus.non_cognitive, "pkg_other_repair", "C_nav"),
    }
    intention_status_records = {
        "status_intention_clean": IntentionStatusRecord("status_intention_clean", IntentionStatus.intention, "theta_intention", "T_plan", restriction_record="restrict_intention", channel_record="tdc_accept_intention"),
        "status_intention_neutral": IntentionStatusRecord("status_intention_neutral", IntentionStatus.not_intention, "theta_neutral", "T_plan"),
        "status_intention_posthoc": IntentionStatusRecord("status_intention_posthoc", IntentionStatus.post_hoc_intention, "theta_posthoc", "T_plan", restriction_record="restrict_posthoc"),
        "status_intention_approximate": IntentionStatusRecord("status_intention_approximate", IntentionStatus.approximate_support_defect, "theta_approx", "T_plan", restriction_record="restrict_approx"),
        "status_intention_target_incoherent": IntentionStatusRecord("status_intention_target_incoherent", IntentionStatus.target_incoherent_restriction, "theta_incoherent", "T_plan", restriction_record="restrict_incoherent"),
        "status_priority_posthoc": IntentionStatusRecord("status_priority_posthoc", IntentionStatus.post_hoc_intention, "theta_priority_posthoc", "T_plan", restriction_record="restrict_priority_posthoc"),
        "status_uncarried_intention": IntentionStatusRecord("status_uncarried_intention", IntentionStatus.not_intention, "theta_uncarried_intention", "T_plan", restriction_record="restrict_uncarried_intention"),
    }
    goal_status_records = {
        "status_goal_clean": GoalStatusRecord("status_goal_clean", GoalStatus.goal, "theta_goal", "T_plan", target_quotient="target_goal_plan", route_evaluations=("eval_goal_a", "eval_goal_b")),
        "status_goal_neutral": GoalStatusRecord("status_goal_neutral", GoalStatus.not_goal, "theta_not_goal", "T_plan", target_quotient="target_neutral_plan"),
        "status_goal_reward_proxy_only": GoalStatusRecord("status_goal_reward_proxy_only", GoalStatus.reward_proxy_only, "theta_reward_proxy", "T_plan", target_quotient="target_reward_plan", reward_proxy="reward_proxy_only_plan"),
        "status_goal_route_unstable": GoalStatusRecord("status_goal_route_unstable", GoalStatus.route_unstable, "theta_route_unstable", "T_plan", target_quotient="target_unstable_plan", route_evaluations=("eval_unstable_a", "eval_unstable_b")),
        "status_priority_reward": GoalStatusRecord("status_priority_reward", GoalStatus.reward_proxy_only, "theta_priority_reward", "T_plan", target_quotient="target_priority_reward_plan", reward_proxy="reward_priority_plan"),
        "status_missing_route_eval": GoalStatusRecord("status_missing_route_eval", GoalStatus.not_goal, "theta_missing_eval", "T_plan", target_quotient="target_missing_eval_plan", route_evaluations=("eval_missing_a",)),
        "status_uncarried_goal": GoalStatusRecord("status_uncarried_goal", GoalStatus.not_goal, "theta_uncarried_goal", "T_plan", target_quotient="target_uncarried_goal_plan", route_evaluations=("eval_uncarried_goal_a", "eval_uncarried_goal_b")),
    }

    return Fixture(
        carrier=Carrier("S", tuple(f"z{i}" for i in range(10))),
        ctx=ctx,
        classes=classes,
        target_classes=target_classes,
        packages=packages,
        formations=formations,
        invocations=invocations,
        quotients=quotients,
        descents=descents,
        supports=supports,
        interventions=interventions,
        matched_controls=matched_controls,
        channels=channels,
        gates=gates,
        readouts=readouts,
        schedules=schedules,
        structural_paths=structural_paths,
        restrictions=restrictions,
        probes=probes,
        target_quotients=target_quotients,
        routes=routes,
        evaluations=evaluations,
        reward_proxies=reward_proxies,
        cognitive_claims=cognitive_claims,
        intention_claims=intention_claims,
        goal_claims=goal_claims,
        cognitive_status_records=cognitive_status_records,
        intention_status_records=intention_status_records,
        goal_status_records=goal_status_records,
        install_map=install_map,
        delta_splits=delta_splits,
        support_link=support_link,
        gate_inventory=gate_inventory,
        repair_inventory=repair_inventory,
        provenance_inventory=provenance_inventory,
        schedule_support_change={
            ("supp_sched_before", "supp_sched_after"): 700,
            ("supp_priority_sched_before", "supp_priority_sched_after"): 700,
        },
        schedule_witness_supports={
            ("schedule_nav_exogenous", "pkg_schedule_trap"): ("supp_sched_before", "supp_sched_after"),
            ("schedule_nav_exogenous", "pkg_priority_schedule"): (
                "supp_priority_sched_before",
                "supp_priority_sched_after",
            ),
        },
        restriction_probes={
            "restrict_intention": ("probe_plan_ok_1", "probe_plan_ok_2"),
            "restrict_posthoc": ("probe_plan_ok_1",),
            "restrict_approx": ("probe_plan_ok_1",),
            "restrict_incoherent": ("probe_plan_bad",),
            "restrict_priority_posthoc": ("probe_plan_ok_1",),
            "restrict_uncarried_intention": ("probe_plan_ok_1",),
        },
        target_probe_coherence={
            ("T_plan", "probe_plan_ok_1", "restrict_intention"): True,
            ("T_plan", "probe_plan_ok_2", "restrict_intention"): True,
            ("T_plan", "probe_plan_ok_1", "restrict_posthoc"): True,
            ("T_plan", "probe_plan_ok_1", "restrict_approx"): True,
            ("T_plan", "probe_plan_bad", "restrict_incoherent"): False,
            ("T_plan", "probe_plan_ok_1", "restrict_priority_posthoc"): True,
            ("T_plan", "probe_plan_ok_1", "restrict_uncarried_intention"): True,
        },
        approximate_restriction_ids=frozenset({"restrict_approx"}),
        route_sets={
            "target_goal_plan": ("route_goal_a", "route_goal_b"),
            "target_unstable_plan": ("route_unstable_a", "route_unstable_b"),
            "target_missing_eval_plan": ("route_missing_a", "route_missing_b"),
            "target_uncarried_goal_plan": ("route_uncarried_goal_a", "route_uncarried_goal_b"),
        },
        route_evaluation_sets={
            "target_goal_plan": ("eval_goal_a", "eval_goal_b"),
            "target_unstable_plan": ("eval_unstable_a", "eval_unstable_b"),
            "target_missing_eval_plan": ("eval_missing_a",),
            "target_uncarried_goal_plan": ("eval_uncarried_goal_a", "eval_uncarried_goal_b"),
        },
        persistence_flags={
            "target_goal_plan": True,
            "target_unstable_plan": False,
            "target_missing_eval_plan": False,
            "target_uncarried_goal_plan": True,
        },
        route_persistence_inventory={
            "target_reward_plan": (),
            "target_priority_reward_plan": (),
        },
    )


def _status_rows(fixture: Fixture) -> dict[str, StatusRow]:
    rows: dict[str, StatusRow] = {}
    for name, expected in EXPECTED_COGNITIVE_STATUSES.items():
        observed, truths, record = classify_cognitive_status(fixture, name)
        rows[name] = StatusRow(name, expected.value, observed.value, truths, record)
    for name, expected in EXPECTED_INTENTION_STATUSES.items():
        observed, truths, record = classify_intention_status(fixture, name)
        rows[name] = StatusRow(name, expected.value, observed.value, truths, record)
    for name, expected in EXPECTED_GOAL_STATUSES.items():
        observed, truths, record = classify_goal_status(fixture, name)
        rows[name] = StatusRow(name, expected.value, observed.value, truths, record)
    return rows


def _control_rows(fixture: Fixture) -> dict[str, ControlRow]:
    good_link = fixture.ctx.support_for_intervention(fixture, "supp_nav_val0", "int_nav_value0")
    bad_link = fixture.ctx.support_for_intervention(fixture, "supp_wrong_for_intervention", "int_nav_value0")
    bad_gate = fixture.ctx.channel_certifies_kernel_comparison(
        fixture,
        "tdc_accept_nav",
        "match_nav",
        "supp_wrong_for_intervention",
        "supp_nav_val1",
    )
    support_control = good_link and not bad_link and not bad_gate

    record = fixture.cognitive_status_records["status_pkg_nav_cognitive"]
    exact_claim = fixture.cognitive_claims["claim_pkg_nav_cognitive"]
    wrong_class_same_package = CognitiveClaimRef("wrong_class_same_package", "pkg_nav_cognitive", "C_other")
    wrong_class_claim = fixture.cognitive_claims["ctrl_wrong_class_claim"]
    wrong_class_status = classify_cognitive_status(fixture, "ctrl_wrong_class_claim")[0]
    desc_other_valid = package_repair_descent(fixture, "desc_other_real", "pkg_other_repair", "C_other")
    desc_other_wrong = package_repair_descent(fixture, "desc_other_real", "pkg_other_repair", "C_nav")
    scoping_control = (
        cognitive_status_record_matches_claim(exact_claim, record)
        and not cognitive_status_record_matches_claim(wrong_class_same_package, record)
        and wrong_class_status is CognitiveStatus.non_cognitive
        and desc_other_valid
        and not desc_other_wrong
        and cognitive_status_record_matches_claim(
            wrong_class_claim,
            fixture.cognitive_status_records["status_wrong_class_non_cognitive"],
        )
    )

    return {
        "ctrl_support_for_intervention_linkage": ControlRow(
            "ctrl_support_for_intervention_linkage",
            "good support link true; wrong support link false; bad gate false",
            f"good={good_link}; wrong={bad_link}; bad_gate={bad_gate}",
            support_control,
        ),
        "ctrl_main_claim_scoping": ControlRow(
            "ctrl_main_claim_scoping",
            "exact package/class scoping holds; wrong-class real C_other repair queried under C_nav yields non_cognitive",
            f"exact={cognitive_status_record_matches_claim(exact_claim, record)}; wrong_same_package={cognitive_status_record_matches_claim(wrong_class_same_package, record)}; desc_other_valid={desc_other_valid}; desc_other_wrong={desc_other_wrong}; wrong_status={wrong_class_status.value}",
            scoping_control,
        ),
    }


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    comparisons: list[Comparison] = []
    for name in REGISTERED_COMPARISON_ORDER:
        if name.endswith(".status"):
            row = results.rows[name.removesuffix(".status")]
            comparisons.append(Comparison(name, row.passed, row.observed, row.expected))
        else:
            control = results.controls[name]
            comparisons.append(
                Comparison(name, control.passed_control, control.observed, control.expected)
            )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture, rows: dict[str, StatusRow]) -> bool:
    for name, row in rows.items():
        if row.status_record is None:
            return False
        if name in fixture.cognitive_claims:
            if not cognitive_status_occurrence_for(fixture, fixture.cognitive_claims[name], row.status_record):
                return False
        elif name in fixture.intention_claims:
            if not intention_status_occurrence_for(fixture, fixture.intention_claims[name], row.status_record):
                return False
        elif name in fixture.goal_claims:
            if not goal_status_occurrence_for(fixture, fixture.goal_claims[name], row.status_record):
                return False
    return True


def _no_hardcoded_status_discipline(results: SweepResults) -> bool:
    return all(
        row.observed != "unclassified"
        and sum(row.truths.values()) == 1
        and row.truths.get(row.observed, False) is True
        for row in results.rows.values()
    ) and all(control.passed_control for control in results.controls.values())


def run_e10_cognitive_demarcation_sweep() -> SweepResults:
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
    return replace(checked, comparisons=_comparisons(checked))


def format_results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E10 Cognitive Demarcation Sweep Results",
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
    results = run_e10_cognitive_demarcation_sweep()
    path.write_text(format_results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    passed = sum(1 for comparison in results.comparisons if comparison.passed)
    total = len(results.comparisons)
    print(f"E10 cognitive demarcation sweep: {passed}/{total} comparisons PASS")
    for comparison in results.comparisons:
        verdict = "PASS" if comparison.passed else "FAIL"
        print(
            f"{verdict}: {comparison.name}: "
            f"observed={comparison.observed} expected={comparison.expected}"
        )


if __name__ == "__main__":
    main()
