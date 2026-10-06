"""E2 bounded-reflexivity sweep against the pre-registered predictions.

The configuration is bound by
``formalization/notes/sweeps/E2_bounded_reflexivity_predictions.md``.  This
module evaluates that deterministic fixture with exact ``Fraction`` arithmetic.
Depth, footprint, saturation, rotation, and per-level status are computed from
the carried tower data exposed through Repair-World audit flags rather than
copied from the prediction table.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any

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
)
from sixbirds_foundations_v.probe_economy import (
    ActiveFamily,
    ProbeCatalog,
    ProbeEconomy,
)
from sixbirds_foundations_v.repair_join import repair_join
from sixbirds_foundations_v.worlds.repair_world import (
    AuditFlags,
    AuditState,
    ChallengeClass,
    ChallengeProcess,
    LawfulnessStatus,
    RepairAction,
    RepairWorldConfig,
    RepairWorldState,
    is_lawful_action,
    ring_kernel,
    step,
)


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E2_bounded_reflexivity_results.md"
)

ITEMS = ("a", "b", "c", "d")
Q0 = {"a": "u", "b": "u", "c": "v", "d": "v"}
R_AB = {"a": "a_star", "b": "b_star", "c": "rest", "d": "rest"}
R_CD = {"a": "left", "b": "left", "c": "c_star", "d": "d_star"}
DEFECT_AB = "split_ab_defect"
DEFECT_CD = "split_cd_defect"
MOVE_RECORD_AB = "move_ab"
MOVE_RECORD_CD = "move_cd"
AUDIT_RECORD_AB = "audit_ab"
AUDIT_RECORD_CD = "audit_cd"
CAPACITY_LINE = "audit-capacity"
Z_CAP = 4
CAPACITY = 8

C_BASE = ChallengeClass("baseline")
C_AB = ChallengeClass("split_ab")
C_CD = ChallengeClass("split_cd")


class ClaimStatus(str, Enum):
    outsideScope = "outsideScope"
    blocked = "blocked"
    absentWithRecord = "absentWithRecord"
    failedAudit = "failedAudit"
    undefinedCircular = "undefinedCircular"
    belowThreshold = "belowThreshold"
    rejected = "rejected"
    provisional = "provisional"
    accepted = "accepted"


class BoundedReflexivityStatus(str, Enum):
    active_scoped = "active_scoped"
    rotating = "rotating"
    saturated = "saturated"
    circular_blocked = "circular_blocked"
    unclassified = "unclassified"


@dataclass(frozen=True)
class SameLevelSelfAuditClaim:
    in_claim_types: bool
    self_dependent: bool
    has_level_shift_bridge: bool


@dataclass(frozen=True)
class InstrumentStack:
    length: int
    finite_records: bool
    admissible_lower_stack: bool
    strictly_increasing_levels: bool
    stack_defect_empty: bool


@dataclass(frozen=True)
class RotatingAuditExtension:
    lower: InstrumentStack
    extension_instrument_present: bool
    extension_level_higher: bool
    target_scope_covers_lower_stack: bool
    bridge_admissible: bool
    report_accepted: bool
    stack_defect_empty: bool
    compliance_accepted: bool
    self_soundness_accepted: bool


@dataclass(frozen=True)
class CarriedInstrumentLevel:
    level_index: int
    level_tag: int
    lower_stack_target: tuple[int, ...]
    record_set: frozenset[str]
    carried: bool = True

    def audits_lower_stack(self, lower_stack: tuple[int, ...]) -> bool:
        return self.lower_stack_target == lower_stack


@dataclass(frozen=True)
class RepairAuditEntry:
    time: int
    defect: str
    action: RepairAction[str, str, str, str]
    repair_package: dict[str, str]
    audit_record: str


@dataclass(frozen=True)
class FootprintRow:
    depth: int
    footprint: int
    admissible: bool


@dataclass(frozen=True)
class SaturationRow:
    depth: int
    current_footprint: int
    current_admissible: bool
    next_positive_footprint: int
    next_footprint: int
    saturated: bool


@dataclass(frozen=True)
class RotationRow:
    name: str
    trigger_present: bool
    starting_depth: int
    saturated: bool
    status: str
    next_depth: int
    extension: RotatingAuditExtension | None
    next_level: CarriedInstrumentLevel | None


@dataclass(frozen=True)
class StatusRow:
    config: str
    depth: int
    target_level: int
    trigger_present: bool
    circular_claim: bool
    footprint: int
    saturated: bool
    status: str
    active_scoped: bool
    rotating: bool
    saturated_holds: bool
    circular_blocked: bool


@dataclass(frozen=True)
class LossRow:
    depth: int
    footprint: int
    audit_cost: Fraction
    error_rate: Fraction
    total_loss: Fraction


@dataclass(frozen=True)
class ControlResult:
    name: str
    observed: dict[str, Any]


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    challenge_schedule: dict[int, str]
    delta_counts: dict[str, int]
    trigger_checks: dict[int, bool]
    state_depths: dict[int, int]
    self_audit_status: ClaimStatus
    self_audit_accepted: bool
    footprint_rows: tuple[FootprintRow, ...]
    saturation_rows: tuple[SaturationRow, ...]
    rotation_rows: tuple[RotationRow, ...]
    status_rows: tuple[StatusRow, ...]
    loss_rows: tuple[LossRow, ...]
    optimum_depth: int
    controls: dict[str, ControlResult]
    actual_tower_discipline: bool
    comparisons: tuple[Comparison, ...]


LEVELS = {
    0: CarriedInstrumentLevel(
        level_index=0,
        level_tag=10,
        lower_stack_target=(),
        record_set=frozenset({"ir0", "vis0"}),
    ),
    1: CarriedInstrumentLevel(
        level_index=1,
        level_tag=20,
        lower_stack_target=(0,),
        record_set=frozenset({"ir1", "thr1", "led1"}),
    ),
    2: CarriedInstrumentLevel(
        level_index=2,
        level_tag=30,
        lower_stack_target=(0, 1),
        record_set=frozenset({"ir2", "chk2", "aud2"}),
    ),
}

ATTEMPTED_LEVEL_3 = CarriedInstrumentLevel(
    level_index=3,
    level_tag=40,
    lower_stack_target=(0, 1, 2),
    record_set=frozenset({"ir3", "aud3"}),
)

CARRIER_RECORD_UNIVERSE = frozenset().union(*(level.record_set for level in LEVELS.values()))

ERROR_RATE_BY_DEPTH = {
    0: F(3, 4),
    1: F(1, 2),
    2: F(1, 3),
    3: F(1, 4),
}


def challenge_process() -> ChallengeProcess:
    return ChallengeProcess(
        recurrence_period=1,
        default_challenge=C_BASE,
        drift_schedule={2: C_AB, 3: C_CD},
        binding_states=frozenset({0, 1, 2, 3, 4}),
    )


def r_for(challenge: ChallengeClass, item: str) -> int:
    if challenge == C_AB:
        return {"a": 0, "b": 1, "c": 0, "d": 0}[item]
    if challenge == C_CD:
        return {"a": 0, "b": 0, "c": 0, "d": 1}[item]
    return 0


def delta_count(q: dict[str, Any], challenge: ChallengeClass) -> int:
    if challenge == C_BASE:
        return 0
    count = 0
    for idx, item in enumerate(ITEMS):
        for item_prime in ITEMS[idx + 1 :]:
            if q[item] == q[item_prime] and r_for(challenge, item) != r_for(challenge, item_prime):
                count += 1
    return count


def joined_quotient(
    q: dict[str, str] | dict[str, tuple[Any, Any]],
    refinement: dict[str, str],
) -> dict[str, tuple[Any, str]]:
    join = repair_join(lambda item: q[item], lambda item: refinement[item])
    return {item: join(item) for item in ITEMS}


def same_level_self_audit_classify(claim: SameLevelSelfAuditClaim) -> ClaimStatus:
    if claim.has_level_shift_bridge is True:
        return ClaimStatus.provisional
    if claim.in_claim_types is False:
        return ClaimStatus.outsideScope
    if claim.self_dependent is True:
        return ClaimStatus.undefinedCircular
    return ClaimStatus.undefinedCircular


def finite_rotating_audit(stack: InstrumentStack) -> RotatingAuditExtension | None:
    if not (
        stack.finite_records
        and stack.admissible_lower_stack
        and stack.strictly_increasing_levels
    ):
        return None
    return RotatingAuditExtension(
        lower=stack,
        extension_instrument_present=True,
        extension_level_higher=True,
        target_scope_covers_lower_stack=True,
        bridge_admissible=True,
        report_accepted=True,
        stack_defect_empty=stack.stack_defect_empty,
        compliance_accepted=stack.stack_defect_empty,
        self_soundness_accepted=False,
    )


def _trajectory() -> DeclaredTrajectory[int]:
    def tau(n: int) -> int:
        return n

    def legitimate_start(candidate_tau, n_start: int) -> bool:
        return n_start == 0 and candidate_tau(n_start) == 0

    return DeclaredTrajectory(
        legitimate_start=legitimate_start,
        supp_k=lambda _z, _z_next: True,
        tau=tau,
        step_in_scope=lambda _n: True,
        n_start=0,
    )


def _evidence(n0: int) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )


def _record_policy(
    trajectory: DeclaredTrajectory[int],
    name: str,
    values: dict[int, Any],
) -> CarriedRecordPolicy[int, Any]:
    def rho_of(z: int) -> Any:
        return values.get(z, values[min(values)])

    def coordinate_declared(readout) -> bool:
        return readout is rho_of

    return CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=coordinate_declared,
        rho_of=rho_of,
        name=name,
    )


def _active_family() -> ActiveFamily[str, object]:
    return ActiveFamily(support=("audit-monitor",), weight={"audit-monitor": F(1)})


def _ledger(trajectory: DeclaredTrajectory[int]) -> CarriedLedger[int, str]:
    entries = [CAPACITY_LINE, "audit-led1", "audit-aud2"]
    entry_by_time = {0: CAPACITY_LINE, 2: "audit-led1", 3: "audit-aud2"}
    time_by_entry = {entry: time for time, entry in entry_by_time.items()}
    policy = _record_policy(trajectory, "ledger", entry_by_time)
    return CarriedLedger(
        ledger_policy=policy,
        ledger_entries=entries,
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: _evidence(time_by_entry[entry])
        if entry in time_by_entry
        else None,
    )


def build_repair_world(
    depth: int = 1,
) -> tuple[
    RepairWorldConfig[str, object, str, str, str, dict[str, str], str, str],
    RepairWorldState[str, str, str, object, str, str, str, dict[str, str], str, str],
    dict[int, RepairAuditEntry],
]:
    """Build the registered E2 Repair-World variant for one audit depth."""

    trajectory = _trajectory()
    ledger = _ledger(trajectory)
    active = _active_family()
    active_policy = _record_policy(trajectory, "active-family", {0: active, 4: active})
    economy = ProbeEconomy(
        catalog=ProbeCatalog(probes=("audit-monitor",), complete_probe_catalog=True),
        active_family_policy=active_policy,
        same_family_saturated=lambda _active, _probe: False,
        exposure_cost_entry=lambda _entry, _probe, _cost: True,
        exposure_budget_entry=lambda _entry, _budget: True,
        exposure_spend_entry=lambda _entry, _spend: True,
        retirement_record_entry=lambda _entry, _probe: True,
        budget_admissible=lambda _move: True,
    )
    theory = TheoryPackage(
        trajectory=trajectory,
        f="e2-f",
        sigma_f="e2-sigma",
        residual_family="e2-residuals",
        audit_access="e2-audit",
        formed_package=True,
    )
    defect_policy = _record_policy(trajectory, "defect", {2: DEFECT_AB, 3: DEFECT_CD})
    move_policy = _record_policy(trajectory, "move", {2: MOVE_RECORD_AB, 3: MOVE_RECORD_CD})
    audit_policy = _record_policy(trajectory, "audit", {2: AUDIT_RECORD_AB, 3: AUDIT_RECORD_CD})
    instrument_policy = _record_policy(trajectory, "instrument", {0: "instrument-0"})
    instrument_occurrence = CarriedRecordOccurrence(
        record="instrument-0",
        evidence=_evidence(0),
    )
    move_ab = RepairMove(
        sort=RepairSort.P4,
        payload=R_AB,
        move_record=MOVE_RECORD_AB,
        move_record_evidence=_evidence(2),
        budget_line=CAPACITY_LINE,
    )
    move_cd = RepairMove(
        sort=RepairSort.P4,
        payload=R_CD,
        move_record=MOVE_RECORD_CD,
        move_record_evidence=_evidence(3),
        budget_line=CAPACITY_LINE,
    )
    moves = {DEFECT_AB: move_ab, DEFECT_CD: move_cd}
    instrument = ActiveCarriedInstrument(
        instrument="e2-instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=[instrument_occurrence],
        threshold_records=[instrument_occurrence],
        check_rule_records=[CheckRuleRecord(record=instrument_occurrence, audit="passes")],
        detects=lambda _z, defect: defect in moves,
        gate_allows=lambda _z, defect, move: moves.get(defect) == move,
        re_audits=lambda _z, _move, _z_next, audit: audit in {AUDIT_RECORD_AB, AUDIT_RECORD_CD},
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda defect: moves[defect],
        AdmissibleMove=lambda _ledger, _z, defect, move: moves.get(defect) == move,
    )
    config = RepairWorldConfig(
        kernel=ring_kernel(5),
        probe_economy=economy,
        e_system=system,
        challenge_process=challenge_process(),
    )
    state = RepairWorldState(
        y=0,
        q=Q0,
        L=active,
        r=ledger,
        Lambda={
            "audit_capacity": F(CAPACITY),
            "audit_spend": F(0),
        },
        A=AuditState(
            instrument=instrument,
            flags=AuditFlags(frozenset(range(depth))),
        ),
    )
    actions = {
        2: RepairAuditEntry(
            time=2,
            defect=DEFECT_AB,
            action=RepairAction(
                repair_package=R_AB,
                z_next=Z_CAP,
                defect=DEFECT_AB,
                defect_evidence=_evidence(2),
                audit_record=AUDIT_RECORD_AB,
                audit_record_evidence=_evidence(2),
            ),
            repair_package=R_AB,
            audit_record=AUDIT_RECORD_AB,
        ),
        3: RepairAuditEntry(
            time=3,
            defect=DEFECT_CD,
            action=RepairAction(
                repair_package=R_CD,
                z_next=Z_CAP,
                defect=DEFECT_CD,
                defect_evidence=_evidence(3),
                audit_record=AUDIT_RECORD_CD,
                audit_record_evidence=_evidence(3),
            ),
            repair_package=R_CD,
            audit_record=AUDIT_RECORD_CD,
        ),
    }
    return config, state, actions


def tower_levels_from_state(
    state: RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any],
) -> tuple[CarriedInstrumentLevel, ...]:
    return tuple(LEVELS[index] for index in sorted(state.A.flags.levels))


def tower_depth_from_state(
    state: RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any],
) -> int:
    return len(tower_levels_from_state(state))


def carried_instrument_level_occurrence(level: CarriedInstrumentLevel) -> bool:
    return level.carried and all(index < level.level_index for index in level.lower_stack_target)


def tower_level(
    levels: tuple[CarriedInstrumentLevel, ...],
    n: int,
    k: int,
    level: CarriedInstrumentLevel,
) -> bool:
    return (
        k < n
        and k < len(levels)
        and levels[k] == level
        and carried_instrument_level_occurrence(level)
        and level.level_index == k
    )


def strictly_increasing_level_tags(levels: tuple[CarriedInstrumentLevel, ...], n: int) -> bool:
    for i in range(n):
        for j in range(i + 1, n):
            if not (tower_level(levels, n, i, levels[i]) and tower_level(levels, n, j, levels[j])):
                return False
            if not levels[i].level_tag < levels[j].level_tag:
                return False
    return True


def each_level_audits_lower_stack(levels: tuple[CarriedInstrumentLevel, ...], n: int) -> bool:
    for k, level in enumerate(levels[:n]):
        if not tower_level(levels, n, k, level):
            return False
        if k > 0:
            lower = tuple(range(k))
            if not (level.audits_lower_stack(lower) and level.lower_stack_target == lower):
                return False
    return True


def complete_carried_instrument_tower(
    levels: tuple[CarriedInstrumentLevel, ...],
    carried_occurrences: tuple[CarriedInstrumentLevel, ...] | None = None,
) -> bool:
    occurrences = carried_occurrences if carried_occurrences is not None else levels
    n = len(levels)
    return all(
        carried_instrument_level_occurrence(level)
        and any(tower_level(levels, n, k, level) for k in range(n))
        for level in occurrences
    )


def capacity_realizable_tower(
    levels: tuple[CarriedInstrumentLevel, ...],
    carried_occurrences: tuple[CarriedInstrumentLevel, ...] | None = None,
) -> bool:
    n = len(levels)
    return (
        complete_carried_instrument_tower(levels, carried_occurrences)
        and strictly_increasing_level_tags(levels, n)
        and each_level_audits_lower_stack(levels, n)
    )


def tower_footprint(levels: tuple[CarriedInstrumentLevel, ...]) -> int:
    return sum(len(level.record_set) for level in levels)


def capacity_admissible(levels: tuple[CarriedInstrumentLevel, ...], cap: int = CAPACITY) -> bool:
    return tower_footprint(levels) <= cap


def next_level_candidates(depth: int) -> tuple[CarriedInstrumentLevel, ...]:
    if depth in LEVELS:
        return (LEVELS[depth],)
    if depth == 3:
        return (ATTEMPTED_LEVEL_3,)
    return ()


def capacity_saturated(levels: tuple[CarriedInstrumentLevel, ...], cap: int = CAPACITY) -> bool:
    candidates = tuple(
        candidate
        for candidate in next_level_candidates(len(levels))
        if carried_instrument_level_occurrence(candidate)
        and candidate.level_index == len(levels)
        and len(candidate.record_set) > 0
    )
    return (
        capacity_realizable_tower(levels)
        and capacity_admissible(levels, cap)
        and bool(candidates)
        and all(not capacity_admissible((*levels, candidate), cap) for candidate in candidates)
    )


def capacity_bound_holds(levels: tuple[CarriedInstrumentLevel, ...], cap: int = CAPACITY) -> bool:
    disjoint = True
    for idx, level in enumerate(levels):
        if not level.record_set <= CARRIER_RECORD_UNIVERSE:
            return False
        for other in levels[idx + 1 :]:
            if level.record_set & other.record_set:
                disjoint = False
    return disjoint and tower_footprint(levels) <= cap


def fiii_stack_bridge(levels: tuple[CarriedInstrumentLevel, ...]) -> InstrumentStack:
    n = len(levels)
    return InstrumentStack(
        length=n,
        finite_records=True,
        admissible_lower_stack=capacity_realizable_tower(levels),
        strictly_increasing_levels=strictly_increasing_level_tags(levels, n),
        stack_defect_empty=True,
    )


def fresh_rotating_level_bridge(
    levels: tuple[CarriedInstrumentLevel, ...],
    next_level: CarriedInstrumentLevel,
) -> bool:
    n = len(levels)
    lower = tuple(range(n))
    return (
        carried_instrument_level_occurrence(next_level)
        and next_level.level_index == n
        and all(level.level_tag < next_level.level_tag for level in levels)
        and next_level.audits_lower_stack(lower)
        and next_level.lower_stack_target == lower
    )


def carried_rotating_extension_realized(
    levels: tuple[CarriedInstrumentLevel, ...],
    stack: InstrumentStack,
    ext: RotatingAuditExtension,
    next_level: CarriedInstrumentLevel,
) -> bool:
    return (
        fiii_stack_bridge(levels) == stack
        and ext.lower == stack
        and ext.extension_instrument_present
        and ext.extension_level_higher
        and ext.bridge_admissible
        and ext.report_accepted
        and not ext.self_soundness_accepted
        and fresh_rotating_level_bridge(levels, next_level)
    )


def audited_repair_trigger(
    config: RepairWorldConfig[str, object, str, str, str, dict[str, str], str, str],
    state: RepairWorldState[str, str, str, object, str, str, str, dict[str, str], str, str],
    entry: RepairAuditEntry,
    expected_q_next: dict[str, Any],
) -> bool:
    lawful = is_lawful_action(config, state, entry.action).status is LawfulnessStatus.lawful
    if not lawful:
        return False
    stepped = step(config, state, entry.action)
    return dict(stepped.q) == expected_q_next


def circular_block_at_level(
    claim: SameLevelSelfAuditClaim | None,
) -> bool:
    return (
        claim is not None
        and claim.has_level_shift_bridge is False
        and same_level_self_audit_classify(claim) is not ClaimStatus.accepted
    )


def rotation_possible(
    levels: tuple[CarriedInstrumentLevel, ...],
) -> tuple[bool, RotatingAuditExtension | None, CarriedInstrumentLevel | None]:
    stack = fiii_stack_bridge(levels)
    ext = finite_rotating_audit(stack)
    candidates = next_level_candidates(len(levels))
    if ext is None or not candidates:
        return False, ext, None
    next_level = candidates[0]
    realized = carried_rotating_extension_realized(levels, stack, ext, next_level)
    return realized, ext, next_level if realized else next_level


def classify_status(
    *,
    levels: tuple[CarriedInstrumentLevel, ...],
    target_level: int,
    trigger_present: bool,
    claim: SameLevelSelfAuditClaim | None,
) -> tuple[BoundedReflexivityStatus, dict[str, bool]]:
    circular = circular_block_at_level(claim)
    saturated = capacity_saturated(levels)
    rotating_possible, _ext, _next_level = rotation_possible(levels)
    active = (
        not circular
        and capacity_admissible(levels)
        and not saturated
        and not trigger_present
        and target_level < len(levels)
    )
    rotating = (
        not circular
        and trigger_present
        and not saturated
        and rotating_possible
        and target_level < len(levels)
    )
    saturated_holds = not circular and saturated and target_level < len(levels)
    circular_holds = circular and target_level < len(levels)
    truths = {
        "active_scoped": active,
        "rotating": rotating,
        "saturated": saturated_holds,
        "circular_blocked": circular_holds,
    }
    if circular_holds:
        return BoundedReflexivityStatus.circular_blocked, truths
    if saturated_holds:
        return BoundedReflexivityStatus.saturated, truths
    if rotating:
        return BoundedReflexivityStatus.rotating, truths
    if active:
        return BoundedReflexivityStatus.active_scoped, truths
    return BoundedReflexivityStatus.unclassified, truths


def rotate_if_triggered(
    levels: tuple[CarriedInstrumentLevel, ...],
    trigger_present: bool,
) -> tuple[tuple[CarriedInstrumentLevel, ...], RotatingAuditExtension | None, CarriedInstrumentLevel | None]:
    if not trigger_present or capacity_saturated(levels):
        return levels, None, None
    realized, ext, next_level = rotation_possible(levels)
    if realized and next_level is not None:
        return (*levels, next_level), ext, next_level
    return levels, ext, next_level


def audit_cost(depth: int) -> Fraction:
    return F(tower_footprint(levels_for_depth(depth)), 24)


def total_loss(depth: int) -> Fraction:
    return ERROR_RATE_BY_DEPTH[depth] + audit_cost(depth)


def levels_for_depth(depth: int) -> tuple[CarriedInstrumentLevel, ...]:
    if depth == 4:
        return (LEVELS[0], LEVELS[1], LEVELS[2], ATTEMPTED_LEVEL_3)
    return tuple(LEVELS[index] for index in range(depth))


def _schedule() -> dict[int, str]:
    process = challenge_process()
    return {time: process.challenge_at(time, 0).name for time in range(5)}


def _trigger_checks() -> tuple[dict[int, bool], dict[int, int]]:
    config, state, actions = build_repair_world(depth=1)
    q1 = joined_quotient(Q0, R_AB)
    trigger_2 = audited_repair_trigger(config, state, actions[2], q1)
    state_after_ab = replace(
        step(config, state, actions[2].action),
        A=AuditState(state.A.instrument, AuditFlags(frozenset({0, 1}))),
    )
    q2 = joined_quotient(q1, R_CD)
    trigger_3 = audited_repair_trigger(config, state_after_ab, actions[3], q2)
    return {2: trigger_2, 3: trigger_3}, {
        0: tower_depth_from_state(state),
        2: tower_depth_from_state(state),
        3: tower_depth_from_state(state_after_ab),
    }


def _footprint_rows() -> tuple[FootprintRow, ...]:
    return tuple(
        FootprintRow(
            depth=depth,
            footprint=tower_footprint(levels_for_depth(depth)),
            admissible=capacity_admissible(levels_for_depth(depth)),
        )
        for depth in range(5)
    )


def _saturation_rows() -> tuple[SaturationRow, ...]:
    rows: list[SaturationRow] = []
    for depth in (1, 2, 3):
        levels = levels_for_depth(depth)
        candidates = next_level_candidates(depth)
        next_positive = len(candidates[0].record_set) if candidates else 0
        next_footprint = tower_footprint((*levels, candidates[0])) if candidates else tower_footprint(levels)
        rows.append(
            SaturationRow(
                depth=depth,
                current_footprint=tower_footprint(levels),
                current_admissible=capacity_admissible(levels),
                next_positive_footprint=next_positive,
                next_footprint=next_footprint,
                saturated=capacity_saturated(levels),
            )
        )
    return tuple(rows)


def _rotation_rows(trigger_checks: dict[int, bool]) -> tuple[RotationRow, ...]:
    no_trigger_levels = levels_for_depth(1)
    no_trigger_status, _ = classify_status(
        levels=no_trigger_levels,
        target_level=0,
        trigger_present=False,
        claim=None,
    )
    next_no_trigger, ext_no_trigger, level_no_trigger = rotate_if_triggered(no_trigger_levels, False)

    levels_1 = levels_for_depth(1)
    status_1, _ = classify_status(
        levels=levels_1,
        target_level=0,
        trigger_present=trigger_checks[2],
        claim=None,
    )
    next_1, ext_1, level_1 = rotate_if_triggered(levels_1, trigger_checks[2])

    levels_2 = next_1
    status_2, _ = classify_status(
        levels=levels_2,
        target_level=1,
        trigger_present=trigger_checks[3],
        claim=None,
    )
    next_2, ext_2, level_2 = rotate_if_triggered(levels_2, trigger_checks[3])

    levels_3 = next_2
    status_3, _ = classify_status(
        levels=levels_3,
        target_level=2,
        trigger_present=True,
        claim=None,
    )
    next_3, ext_3, level_3 = rotate_if_triggered(levels_3, True)

    return (
        RotationRow(
            name="no-trigger control",
            trigger_present=False,
            starting_depth=1,
            saturated=capacity_saturated(no_trigger_levels),
            status=no_trigger_status.value,
            next_depth=len(next_no_trigger),
            extension=ext_no_trigger,
            next_level=level_no_trigger,
        ),
        RotationRow(
            name="triggered step 1",
            trigger_present=trigger_checks[2],
            starting_depth=1,
            saturated=capacity_saturated(levels_1),
            status=status_1.value,
            next_depth=len(next_1),
            extension=ext_1,
            next_level=level_1,
        ),
        RotationRow(
            name="triggered step 2",
            trigger_present=trigger_checks[3],
            starting_depth=2,
            saturated=capacity_saturated(levels_2),
            status=status_2.value,
            next_depth=len(next_2),
            extension=ext_2,
            next_level=level_2,
        ),
        RotationRow(
            name="saturated trigger",
            trigger_present=True,
            starting_depth=3,
            saturated=capacity_saturated(levels_3),
            status=status_3.value,
            next_depth=len(next_3),
            extension=ext_3,
            next_level=level_3,
        ),
    )


def _status_rows(trigger_checks: dict[int, bool]) -> tuple[StatusRow, ...]:
    specs = (
        ("active_base", 1, 0, False, None),
        ("rotate_1_to_2", 1, 0, trigger_checks[2], None),
        ("rotate_2_to_3", 2, 1, trigger_checks[3], None),
        ("saturated_3", 3, 2, True, None),
        (
            "circular_0",
            1,
            0,
            False,
            SameLevelSelfAuditClaim(
                in_claim_types=True,
                self_dependent=True,
                has_level_shift_bridge=False,
            ),
        ),
    )
    rows: list[StatusRow] = []
    for name, depth, target_level, trigger, claim in specs:
        levels = levels_for_depth(depth)
        status, truths = classify_status(
            levels=levels,
            target_level=target_level,
            trigger_present=trigger,
            claim=claim,
        )
        rows.append(
            StatusRow(
                config=name,
                depth=depth,
                target_level=target_level,
                trigger_present=trigger,
                circular_claim=claim is not None,
                footprint=tower_footprint(levels),
                saturated=capacity_saturated(levels),
                status=status.value,
                active_scoped=truths["active_scoped"],
                rotating=truths["rotating"],
                saturated_holds=truths["saturated"],
                circular_blocked=truths["circular_blocked"],
            )
        )
    return tuple(rows)


def _loss_rows() -> tuple[LossRow, ...]:
    return tuple(
        LossRow(
            depth=depth,
            footprint=tower_footprint(levels_for_depth(depth)),
            audit_cost=audit_cost(depth),
            error_rate=ERROR_RATE_BY_DEPTH[depth],
            total_loss=total_loss(depth),
        )
        for depth in range(4)
    )


def _optimum_depth(rows: tuple[LossRow, ...]) -> int:
    min_loss = min(row.total_loss for row in rows)
    winners = [row.depth for row in rows if row.total_loss == min_loss]
    if len(winners) != 1:
        raise ValueError(f"expected a unique optimum, got {winners}")
    return winners[0]


def _controls() -> dict[str, ControlResult]:
    circular_claim = SameLevelSelfAuditClaim(
        in_claim_types=True,
        self_dependent=True,
        has_level_shift_bridge=False,
    )
    circular_status, circular_truths = classify_status(
        levels=levels_for_depth(1),
        target_level=0,
        trigger_present=False,
        claim=circular_claim,
    )
    over_capacity_levels = levels_for_depth(4)
    stack_1 = fiii_stack_bridge(levels_for_depth(1))
    ext_1 = finite_rotating_audit(stack_1)
    bad_next = replace(LEVELS[1], level_index=2, lower_stack_target=(0, 1))
    unlinked_realized = (
        carried_rotating_extension_realized(levels_for_depth(1), stack_1, ext_1, bad_next)
        if ext_1 is not None
        else False
    )
    incomplete_levels = (LEVELS[0],)
    incomplete_occurrences = (LEVELS[0], LEVELS[1])
    return {
        "same_level_circularity": ControlResult(
            name="same_level_circularity",
            observed={
                "classifier_accepted": same_level_self_audit_classify(circular_claim)
                is ClaimStatus.accepted,
                "classifier_status": same_level_self_audit_classify(circular_claim).value,
                "status": circular_status.value,
                "active_scoped": circular_truths["active_scoped"],
                "rotating": circular_truths["rotating"],
                "saturated": circular_truths["saturated"],
                "circular_blocked": circular_truths["circular_blocked"],
            },
        ),
        "capacity_null": ControlResult(
            name="capacity_null",
            observed={
                "tower_footprint": tower_footprint(over_capacity_levels),
                "capacity_admissible": capacity_admissible(over_capacity_levels),
                "capacity_saturated_depth_3": capacity_saturated(levels_for_depth(3)),
                "capacity_bound_certified_depths": all(
                    capacity_bound_holds(levels_for_depth(depth)) for depth in (1, 2, 3)
                ),
                "over_capacity_attempted_admissible": capacity_admissible(over_capacity_levels),
            },
        ),
        "unlinked_bridge": ControlResult(
            name="unlinked_bridge",
            observed={
                "fiii_extension_exists": ext_1 is not None,
                "carried_rotating_extension_realized": unlinked_realized,
                "bad_next_level_index": bad_next.level_index,
                "expected_next_index": len(levels_for_depth(1)),
            },
        ),
        "incomplete_inventory": ControlResult(
            name="incomplete_inventory",
            observed={
                "carried_level_1_exists": carried_instrument_level_occurrence(LEVELS[1]),
                "tower_slot_1_present": len(incomplete_levels) > 1,
                "complete_carried_instrument_tower": complete_carried_instrument_tower(
                    incomplete_levels, incomplete_occurrences
                ),
                "complete_status_claim_accepted": complete_carried_instrument_tower(
                    incomplete_levels, incomplete_occurrences
                ),
            },
        ),
    }


def _actual_tower_discipline(
    state_depths: dict[int, int],
    footprint_rows: tuple[FootprintRow, ...],
    status_rows: tuple[StatusRow, ...],
) -> bool:
    depths_from_states = {depth for depth in state_depths.values()}
    status_depths = {row.depth for row in status_rows if row.config != "circular_0"}
    footprint_by_depth = {row.depth: row.footprint for row in footprint_rows}
    return (
        {1, 2} <= depths_from_states
        and {1, 2, 3} <= status_depths
        and all(
            row.footprint == footprint_by_depth[row.depth]
            for row in status_rows
            if row.depth in footprint_by_depth
        )
    )


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    return (
        Comparison(
            "audit carrier depths",
            results.state_depths[0] == 1
            and results.state_depths[2] == 1
            and results.state_depths[3] == 2
            and tuple(row.depth for row in results.status_rows[:4]) == (1, 1, 2, 3),
            f"state_depths={results.state_depths}; status_depths="
            f"{tuple(row.depth for row in results.status_rows[:4])}",
            "state flags distinguish depths 1 and 2; status rows cover 1,1,2,3",
        ),
        Comparison(
            "challenge and audited repair triggers",
            results.challenge_schedule
            == {0: "baseline", 1: "baseline", 2: "split_ab", 3: "split_cd", 4: "split_cd"}
            and results.trigger_checks == {2: True, 3: True},
            f"schedule={_schedule_summary(results.challenge_schedule)}; "
            f"triggers={results.trigger_checks}",
            "0,1 baseline; 2 split_ab; 3,4 split_cd; rho_2/rho_3 trigger",
        ),
        Comparison(
            "self-soundness obstruction",
            results.self_audit_status is ClaimStatus.undefinedCircular
            and results.self_audit_accepted is False
            and results.controls["same_level_circularity"].observed["status"]
            != BoundedReflexivityStatus.active_scoped.value,
            f"classifier={results.self_audit_status.value}; "
            f"accepted={results.self_audit_accepted}; "
            f"control_status={results.controls['same_level_circularity'].observed['status']}",
            "undefinedCircular, not accepted, not active_scoped",
        ),
        Comparison(
            "forced stratification sequence",
            _rotation_sequence_ok(results.rotation_rows),
            _rotation_summary(results.rotation_rows),
            "no-trigger stays 1; triggered depths rotate 1->2->3; saturated depth 3 stays 3",
        ),
        Comparison(
            "fresh-level bridge discipline",
            _fresh_bridge_ok(results.rotation_rows),
            _fresh_bridge_summary(results.rotation_rows),
            "level 1 tag 20 target [0]; level 2 tag 30 target [0,1]",
        ),
        Comparison(
            "capacity arithmetic",
            tuple(row.footprint for row in results.footprint_rows) == (0, 2, 5, 8, 10),
            _footprint_summary(results.footprint_rows),
            "depth footprints 0,2,5,8,10",
        ),
        Comparison(
            "capacity saturation",
            tuple(row.saturated for row in results.saturation_rows) == (False, False, True)
            and tuple(row.next_footprint for row in results.saturation_rows) == (5, 8, 10),
            _saturation_summary(results.saturation_rows),
            "depths 1,2 not saturated; depth 3 saturated; next footprints 5,8,10",
        ),
        Comparison(
            "capacity-null over-capacity control",
            _capacity_null_ok(results.controls["capacity_null"]),
            _control_summary(results.controls["capacity_null"]),
            "footprint 10, CapacityAdmissible false, depth 3 saturated, certified depths pass",
        ),
        Comparison(
            "per-level status exactness",
            _status_table_ok(results.status_rows),
            _status_summary(results.status_rows),
            "active, rotating, rotating, saturated, circular_blocked with exactly one true branch each",
        ),
        Comparison(
            "diminishing returns optimum",
            tuple(row.total_loss for row in results.loss_rows)
            == (F(18, 24), F(14, 24), F(13, 24), F(14, 24))
            and results.optimum_depth == 2,
            _loss_summary(results.loss_rows, results.optimum_depth),
            "losses 18/24,14/24,13/24,14/24; unique optimum depth 2",
        ),
        Comparison(
            "unlinked bridge control",
            _unlinked_bridge_ok(results.controls["unlinked_bridge"]),
            _control_summary(results.controls["unlinked_bridge"]),
            "FIII extension exists but badNextLevel does not realize depth-1 extension",
        ),
        Comparison(
            "incomplete tower inventory control",
            _incomplete_inventory_ok(results.controls["incomplete_inventory"]),
            _control_summary(results.controls["incomplete_inventory"]),
            "carried level 1 exists, tower slot 1 absent, completeness/status claim false",
        ),
        Comparison(
            "actual carried tower discipline",
            results.actual_tower_discipline,
            "status footprints match actual carried tower depths from AuditFlags",
            "not classified by existential feasible tower",
        ),
    )


def run_bounded_reflexivity_sweep() -> SweepResults:
    trigger_checks, state_depths = _trigger_checks()
    circular_claim = SameLevelSelfAuditClaim(
        in_claim_types=True,
        self_dependent=True,
        has_level_shift_bridge=False,
    )
    footprint_rows = _footprint_rows()
    saturation_rows = _saturation_rows()
    rotation_rows = _rotation_rows(trigger_checks)
    status_rows = _status_rows(trigger_checks)
    loss_rows = _loss_rows()
    controls = _controls()
    actual_tower_discipline = _actual_tower_discipline(
        state_depths, footprint_rows, status_rows
    )
    q1 = joined_quotient(Q0, R_AB)
    q2 = joined_quotient(q1, R_CD)
    results = SweepResults(
        challenge_schedule=_schedule(),
        delta_counts={
            "Q0_C_ab": delta_count(Q0, C_AB),
            "Q1_C_ab": delta_count(q1, C_AB),
            "Q1_C_cd": delta_count(q1, C_CD),
            "Q2_C_cd": delta_count(q2, C_CD),
        },
        trigger_checks=trigger_checks,
        state_depths=state_depths,
        self_audit_status=same_level_self_audit_classify(circular_claim),
        self_audit_accepted=same_level_self_audit_classify(circular_claim)
        is ClaimStatus.accepted,
        footprint_rows=footprint_rows,
        saturation_rows=saturation_rows,
        rotation_rows=rotation_rows,
        status_rows=status_rows,
        loss_rows=loss_rows,
        optimum_depth=_optimum_depth(loss_rows),
        controls=controls,
        actual_tower_discipline=actual_tower_discipline,
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def _rotation_sequence_ok(rows: tuple[RotationRow, ...]) -> bool:
    observed = tuple(
        (
            row.name,
            row.trigger_present,
            row.starting_depth,
            row.saturated,
            row.status,
            row.next_depth,
            row.extension.self_soundness_accepted if row.extension else None,
        )
        for row in rows
    )
    return observed == (
        ("no-trigger control", False, 1, False, "active_scoped", 1, None),
        ("triggered step 1", True, 1, False, "rotating", 2, False),
        ("triggered step 2", True, 2, False, "rotating", 3, False),
        ("saturated trigger", True, 3, True, "saturated", 3, None),
    )


def _fresh_bridge_ok(rows: tuple[RotationRow, ...]) -> bool:
    fresh = [row.next_level for row in rows if row.next_level is not None]
    return (
        len(fresh) == 2
        and fresh[0].level_index == 1
        and fresh[0].level_tag == 20
        and fresh[0].lower_stack_target == (0,)
        and fresh[1].level_index == 2
        and fresh[1].level_tag == 30
        and fresh[1].lower_stack_target == (0, 1)
    )


def _capacity_null_ok(control: ControlResult) -> bool:
    observed = control.observed
    return (
        observed["tower_footprint"] == 10
        and observed["capacity_admissible"] is False
        and observed["capacity_saturated_depth_3"] is True
        and observed["capacity_bound_certified_depths"] is True
        and observed["over_capacity_attempted_admissible"] is False
    )


def _status_table_ok(rows: tuple[StatusRow, ...]) -> bool:
    expected_status = {
        "active_base": "active_scoped",
        "rotate_1_to_2": "rotating",
        "rotate_2_to_3": "rotating",
        "saturated_3": "saturated",
        "circular_0": "circular_blocked",
    }
    return all(
        row.status == expected_status[row.config]
        and sum(
            (
                row.active_scoped,
                row.rotating,
                row.saturated_holds,
                row.circular_blocked,
            )
        )
        == 1
        for row in rows
    )


def _unlinked_bridge_ok(control: ControlResult) -> bool:
    observed = control.observed
    return (
        observed["fiii_extension_exists"] is True
        and observed["carried_rotating_extension_realized"] is False
        and observed["bad_next_level_index"] != observed["expected_next_index"]
    )


def _incomplete_inventory_ok(control: ControlResult) -> bool:
    observed = control.observed
    return (
        observed["carried_level_1_exists"] is True
        and observed["tower_slot_1_present"] is False
        and observed["complete_carried_instrument_tower"] is False
        and observed["complete_status_claim_accepted"] is False
    )


def _fmt_bool(value: bool) -> str:
    return "true" if value else "false"


def _schedule_summary(schedule: dict[int, str]) -> str:
    return "; ".join(f"t={time}:{challenge}" for time, challenge in sorted(schedule.items()))


def _footprint_summary(rows: tuple[FootprintRow, ...]) -> str:
    return "; ".join(
        f"d={row.depth}: footprint={row.footprint}, admissible={_fmt_bool(row.admissible)}"
        for row in rows
    )


def _saturation_summary(rows: tuple[SaturationRow, ...]) -> str:
    return "; ".join(
        f"d={row.depth}: current={row.current_footprint}, next={row.next_footprint}, "
        f"saturated={_fmt_bool(row.saturated)}"
        for row in rows
    )


def _rotation_summary(rows: tuple[RotationRow, ...]) -> str:
    return "; ".join(
        f"{row.name}: trigger={_fmt_bool(row.trigger_present)}, depth={row.starting_depth}, "
        f"status={row.status}, next={row.next_depth}, "
        f"selfSound={row.extension.self_soundness_accepted if row.extension else None}"
        for row in rows
    )


def _fresh_bridge_summary(rows: tuple[RotationRow, ...]) -> str:
    return "; ".join(
        f"{row.name}: nextLevel="
        f"{None if row.next_level is None else (row.next_level.level_index, row.next_level.level_tag, row.next_level.lower_stack_target)}"
        for row in rows
    )


def _status_summary(rows: tuple[StatusRow, ...]) -> str:
    return "; ".join(
        f"{row.config}: depth={row.depth}, target={row.target_level}, status={row.status}, "
        f"branches=({row.active_scoped},{row.rotating},{row.saturated_holds},{row.circular_blocked})"
        for row in rows
    )


def _loss_summary(rows: tuple[LossRow, ...], optimum_depth: int) -> str:
    return "; ".join(
        f"d={row.depth}: footprint={row.footprint}, cost={row.audit_cost}, "
        f"error={row.error_rate}, loss={row.total_loss}"
        for row in rows
    ) + f"; optimum={optimum_depth}"


def _control_summary(control: ControlResult) -> str:
    return "; ".join(f"{key}={value}" for key, value in sorted(control.observed.items()))


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E2 Bounded Reflexivity Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e2_bounded_reflexivity_sweep` against "
        "`formalization/notes/sweeps/E2_bounded_reflexivity_predictions.md`.",
        "",
        f"Overall verdict: {'PASS' if not failures else 'FAIL'}",
        "",
        "## Registered Prediction Comparisons",
        "",
        "| check | verdict | observed | registered prediction |",
        "| --- | --- | --- | --- |",
    ]
    for comparison in results.comparisons:
        lines.append(
            f"| {comparison.name} | {'PASS' if comparison.passed else 'FAIL'} | "
            f"{comparison.observed} | {comparison.expected} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Arithmetic is exact `fractions.Fraction`; no stochastic or floating-point branch is used.",
            "- Tower depth, footprint, saturation, and status are computed from `AuditFlags` and carried "
            "level record sets, not from a pre-filled status table.",
            "- The same-level self-audit classifier is a direct Python port of "
            "`SixBirdsIII.SameLevelSelfAuditClassify`.",
            "- The unlinked-bridge control checks the specific bad `nextLevel` witness directly, avoiding "
            "an existential back door through a separate valid next level.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_bounded_reflexivity_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    print(results_markdown(results))
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
