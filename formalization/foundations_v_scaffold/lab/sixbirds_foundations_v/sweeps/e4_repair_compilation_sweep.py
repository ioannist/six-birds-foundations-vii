"""E4 repair-compilation sweep against the pre-registration.

The configuration is fixed by
``formalization/notes/sweeps/E4_repair_compilation_predictions.md``.  This
module evaluates a deterministic 20-state ring fixture with concrete repeated
repair invocations, compiled-operator candidates, FIII top-down channel gates,
a Python mirror of FIII promotion gates, and carried status records.  Status
labels are computed from the candidate fields and priority-normalized cases;
they are not copied from the prediction table.
"""

from __future__ import annotations

from dataclasses import dataclass
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
    same_family_saturated,
)
from sixbirds_foundations_v.sweeps.e11_institutional_rewrite_sweep import (
    TopDownChannelRecord,
    accepted_top_down_record,
    structural_only_top_down_record,
    top_down_channel_accepted_bool,
)
from sixbirds_foundations_v.worlds.repair_world import (
    ChallengeProcess,
    RepairWorldConfig,
    ring_kernel,
)


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E4_repair_compilation_results.md"
)

N_STATES = 20
STATES = tuple(range(N_STATES))
WINDOW_CLASS = "C_main"
WINDOW_REFINEMENT = "R_main"
OTHER_CLASS = "C_other"
THRESHOLD = F(1, 10)
IDEMPOTENCE_BOUND = F(1, 100)

REGISTERED_CANDIDATE_OPTS = (
    None,
    "cand_compiled",
    "cand_compiled_support_gate",
    "cand_mis_compiled",
    "cand_decompiled",
    "cand_compiling_blocked_channel",
    "cand_compiling_promotion_rejected",
    "cand_compiling_memory_only",
    "cand_compiling_same_family",
    "cand_compiling_unverified_descent",
    "cand_statused_obstruction",
)


class ConstructionRejected(ValueError):
    """Raised for E4 construction-level non-vacuity failures."""


class GateStatus(str, Enum):
    pass_ = "pass"
    fail = "fail"
    not_required = "notRequired"
    not_checked = "notChecked"
    outside_scope = "outsideScope"


class StrictGateStatus(str, Enum):
    strict_pass = "strictPass"
    non_strict_pass = "nonStrictPass"
    not_required = "notRequired"
    not_checked = "notChecked"
    bad_audit = "badAudit"
    outside_scope = "outsideScope"


class PromotionStatus(str, Enum):
    candidate = "candidate"
    accepted = "accepted"
    strict = "strict"
    non_strict = "nonStrict"
    failed_descent = "failedDescent"
    failed_stability = "failedStability"
    failed_audit = "failedAudit"
    failed_no_smuggling = "failedNoSmuggling"
    local_only = "localOnly"
    globally_obstructed = "globallyObstructed"
    outside_scope = "outsideScope"


class CompilationStatus(str, Enum):
    exposed = "exposed"
    decompiled = "decompiled"
    compiled = "compiled"
    mis_compiled = "mis_compiled"
    compiling = "compiling"
    unclassified = "unclassified"


class ObstructionClassification(str, Enum):
    accepted_brittleness = "accepted_brittleness"
    repaired = "repaired"


@dataclass(frozen=True)
class PromotionGateResults:
    suff: GateStatus
    desc: GateStatus
    stab: GateStatus
    ctrl: GateStatus
    nosmuggle: GateStatus
    vis: GateStatus
    audit: GateStatus
    strict: StrictGateStatus
    locglob: GateStatus


@dataclass(frozen=True)
class PromotionBridgeData:
    name: str
    admissible: bool
    gates: PromotionGateResults


@dataclass(frozen=True)
class InvocationWitness:
    time: int
    source: int
    target: int
    payload_value: Fraction
    repair_refinement: str
    audit_entry: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class CompilationCandidateWindow:
    name: str
    challenge_class: str
    repair_refinement: str
    episode_times: tuple[int, ...]
    invocations: dict[int, InvocationWitness]
    obstruction_pre: dict[int, frozenset[tuple[str, str]]]
    obstruction_post: dict[int, frozenset[tuple[str, str]]]
    future_invocations_after: dict[int, tuple[InvocationWitness, ...]]


@dataclass(frozen=True)
class MemoryOnlyComparatorCertified:
    name: str
    repair_descent_pairs: frozenset[tuple[str, str]]
    memory_only_pairs: frozenset[tuple[str, str]]

    @property
    def survives_control(self) -> bool:
        return self.memory_only_pairs != self.repair_descent_pairs


@dataclass(frozen=True)
class CompiledOperatorCandidate:
    name: str
    challenge_class: str
    repair_refinement: str
    move_sort: RepairSort
    move_record: str
    move_payload: str
    decompilation_record: str
    annotation_carried: bool
    channel_record: str
    promotion_data: str
    memory_only: MemoryOnlyComparatorCertified
    saturated_predicate: Any
    active_family: ActiveFamily[str, str]
    probe: str
    descent_residuals: frozenset[tuple[str, str]]
    silent_future_invocations: tuple[InvocationWitness, ...]
    decompilation_event_record: str | None
    out_of_class_split_pair: tuple[str, str] | None
    lawful_kernel_realized: bool = True


@dataclass(frozen=True)
class DecompilationEventRecord:
    name: str
    candidate_name: str
    reverts_record: str
    carried: bool


@dataclass(frozen=True)
class ObstructionStatusRecord:
    name: str
    candidate_name: str
    for_class: str
    split_pair: tuple[str, str]
    assigned_status: ObstructionClassification
    carried: bool


@dataclass(frozen=True)
class CompilationStatusRecord:
    name: str
    window_ref: tuple[str, str]
    candidate_ref: str | None
    status: CompilationStatus
    supporting_ledger_entries: tuple[str, ...]
    supporting_audit_records: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class CandidateRow:
    candidate_opt: str
    attributed: bool
    lawful: bool | None
    descent: bool | None
    silent: bool | None
    decompilation_event: bool | None
    out_of_class_witness: bool | None
    exposed: bool
    decompiled: bool
    compiled: bool
    mis_compiled: bool
    compiling: bool
    status: str
    carried_status_record: str | None


@dataclass(frozen=True)
class ControlRow:
    name: str
    passed_control: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    candidate_rows: tuple[CandidateRow, ...]
    controls: tuple[ControlRow, ...]
    brittleness_holds: bool
    window_obstruction_reducing: bool
    window_idempotence_stable: bool
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    comparisons: tuple[Comparison, ...]


@dataclass(frozen=True)
class Fixture:
    config: RepairWorldConfig[str, str, str, str, str, dict[str, str], str, str]
    window: CompilationCandidateWindow
    candidates: dict[str, CompiledOperatorCandidate]
    scope_windows: dict[str, CompilationCandidateWindow]
    channel_records: dict[str, TopDownChannelRecord]
    promotion_data: dict[str, PromotionBridgeData]
    decompilation_events: dict[str, DecompilationEventRecord]
    obstruction_status_records: dict[str, ObstructionStatusRecord]
    status_records: dict[str | None, CompilationStatusRecord]
    carried_compiled_records: frozenset[str]
    carried_decompilation_records: frozenset[str]
    carried_status_records: frozenset[str]
    ledger_entries: frozenset[str]
    audit_records: frozenset[str]
    active_family: ActiveFamily[str, str]


def core_gate_acceptable_bool(gate: GateStatus) -> bool:
    return gate in {GateStatus.pass_, GateStatus.not_required}


def required_core_gates_pass_bool(gates: PromotionGateResults) -> bool:
    return (
        gates.suff is GateStatus.pass_
        and gates.ctrl is GateStatus.pass_
        and gates.nosmuggle is GateStatus.pass_
        and gates.vis is GateStatus.pass_
        and gates.audit is GateStatus.pass_
        and core_gate_acceptable_bool(gates.desc)
        and core_gate_acceptable_bool(gates.stab)
    )


def promotion_accepted_core_bool(data: PromotionBridgeData) -> bool:
    return data.admissible and required_core_gates_pass_bool(data.gates)


def promote(data: PromotionBridgeData) -> PromotionStatus:
    if promotion_accepted_core_bool(data):
        if data.gates.strict is StrictGateStatus.strict_pass:
            return PromotionStatus.strict
        if data.gates.strict is StrictGateStatus.non_strict_pass:
            return PromotionStatus.non_strict
        return PromotionStatus.accepted
    return PromotionStatus.candidate


def accepted_promotion_family(status: PromotionStatus) -> bool:
    return status in {
        PromotionStatus.accepted,
        PromotionStatus.strict,
        PromotionStatus.non_strict,
    }


def _ring_supp(source: int, target: int) -> bool:
    return target == (source + 1) % N_STATES


def _record_policy(
    trajectory: DeclaredTrajectory[int],
    family: str,
) -> CarriedRecordPolicy[int, str]:
    return CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=lambda _rho: True,
        rho_of=lambda z: f"{family}:{z}",
        name=family,
    )


def _evidence(n0: int) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )


def _make_config(
    ledger_entries: frozenset[str],
    audit_records: frozenset[str],
) -> RepairWorldConfig[str, str, str, str, str, dict[str, str], str, str]:
    trajectory = DeclaredTrajectory(
        legitimate_start=lambda _tau, n_start: n_start == 0,
        supp_k=_ring_supp,
        tau=lambda n: n % N_STATES,
        step_in_scope=lambda _n: True,
        n_start=0,
    )
    ledger = CarriedLedger(
        ledger_policy=_record_policy(trajectory, "ledger"),
        ledger_entries=tuple(sorted(ledger_entries)),
        complete_ledger_inventory=True,
        ledger_evidence=lambda _entry: _evidence(0),
    )
    instrument_occurrence = CarriedRecordOccurrence(
        record="instrument:e4",
        evidence=_evidence(0),
    )
    instrument = ActiveCarriedInstrument(
        instrument="I_E4",
        instrument_record_policy=_record_policy(trajectory, "instrument"),
        records_are_complete_inventory=True,
        visibility_records=(instrument_occurrence,),
        threshold_records=(instrument_occurrence,),
        check_rule_records=(CheckRuleRecord(record=instrument_occurrence, audit="audit:instrument:e4"),),
        detects=lambda _z, _defect: True,
        gate_allows=lambda _z, _defect, _move: True,
        re_audits=lambda _z, _move, _z_next, audit: audit in audit_records,
    )
    move = RepairMove(
        sort=RepairSort.P1,
        payload={"compiled": "payload"},
        move_record="move:generator:e4",
        move_record_evidence=_evidence(0),
        budget_line="ledger:seed",
    )
    system = ESystem(
        T=TheoryPackage(
            trajectory=trajectory,
            f="e4-f",
            sigma_f="e4-sigma",
            residual_family="e4-residuals",
            audit_access="e4-audit-access",
            formed_package=True,
        ),
        defect_record_policy=_record_policy(trajectory, "defect"),
        move_record_policy=_record_policy(trajectory, "move"),
        audit_record_policy=_record_policy(trajectory, "audit"),
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda _defect: move,
        AdmissibleMove=lambda _ledger, _z, _defect, _move: True,
    )
    return RepairWorldConfig(
        kernel=ring_kernel(N_STATES),
        probe_economy=None,
        e_system=system,
        challenge_process=ChallengeProcess(recurrence_period=None),
    )


def _pass_gates(strict: StrictGateStatus = StrictGateStatus.strict_pass) -> PromotionGateResults:
    return PromotionGateResults(
        suff=GateStatus.pass_,
        desc=GateStatus.not_required,
        stab=GateStatus.not_required,
        ctrl=GateStatus.pass_,
        nosmuggle=GateStatus.pass_,
        vis=GateStatus.pass_,
        audit=GateStatus.pass_,
        strict=strict,
        locglob=GateStatus.not_required,
    )


def _rejected_gates() -> PromotionGateResults:
    return PromotionGateResults(
        suff=GateStatus.pass_,
        desc=GateStatus.not_required,
        stab=GateStatus.not_required,
        ctrl=GateStatus.fail,
        nosmuggle=GateStatus.pass_,
        vis=GateStatus.pass_,
        audit=GateStatus.pass_,
        strict=StrictGateStatus.strict_pass,
        locglob=GateStatus.not_required,
    )


def _build_window(
    name: str,
    episode_times: tuple[int, ...],
    *,
    payload_values: dict[int, Fraction] | None = None,
    obstruction_pre: dict[int, frozenset[tuple[str, str]]] | None = None,
    obstruction_post: dict[int, frozenset[tuple[str, str]]] | None = None,
) -> CompilationCandidateWindow:
    if len(episode_times) < 2:
        raise ConstructionRejected("CompilationCandidateWindow requires at least two invocations")
    invocations = {
        time: InvocationWitness(
            time=time,
            source=time,
            target=(time + 1) % N_STATES,
            payload_value=payload_values[time]
            if payload_values is not None
            else F(100 + time, 10000),
            repair_refinement=WINDOW_REFINEMENT,
            audit_entry=f"audit:window:{time}",
        )
        for time in episode_times
    }
    obstruction_pairs = (
        ("a", "b"),
        ("b", "c"),
        ("c", "d"),
    )
    default_pre = {
        0: frozenset(obstruction_pairs[:3]),
        1: frozenset(obstruction_pairs[:2]),
        2: frozenset(obstruction_pairs[:1]),
    }
    default_post = {
        0: frozenset(obstruction_pairs[:2]),
        1: frozenset(obstruction_pairs[:1]),
        2: frozenset(),
    }
    pre = obstruction_pre if obstruction_pre is not None else default_pre
    post = obstruction_post if obstruction_post is not None else default_post
    return CompilationCandidateWindow(
        name=name,
        challenge_class=WINDOW_CLASS,
        repair_refinement=WINDOW_REFINEMENT,
        episode_times=episode_times,
        invocations=invocations,
        obstruction_pre=pre,
        obstruction_post=post,
        future_invocations_after={2: ()},
    )


def build_window_too_short() -> CompilationCandidateWindow:
    return _build_window("window_too_short", (0,))


def build_window_no_obstruction_reduction() -> CompilationCandidateWindow:
    return _build_window(
        "window_no_obstruction_reduction",
        (0, 1),
        obstruction_pre={
            0: frozenset({("a", "b")}),
            1: frozenset({("b", "c")}),
        },
        obstruction_post={
            0: frozenset({("a", "b"), ("new", "split")}),
            1: frozenset(),
        },
    )


def build_window_payload_drift() -> CompilationCandidateWindow:
    return _build_window(
        "window_payload_drift",
        (0, 1, 2),
        payload_values={
            0: F(0),
            1: F(1, 4),
            2: F(1, 2),
        },
    )


def _memory(name: str, *, reproduced_by_memory_only: bool) -> MemoryOnlyComparatorCertified:
    repaired = frozenset({("a", "b")})
    memory = repaired if reproduced_by_memory_only else frozenset()
    return MemoryOnlyComparatorCertified(name, repaired, memory)


def _same_family_saturated_from_active_family(
    active_family: ActiveFamily[str, str],
    probe: str,
) -> bool:
    return probe in active_family.support and active_family.weight.get(probe) == F(1)


def _candidate(
    name: str,
    *,
    move_sort: RepairSort = RepairSort.P1,
    channel_record: str = "td_accepted_stack",
    promotion_data: str = "promotion:accepted",
    memory_only: MemoryOnlyComparatorCertified,
    probe: str | None = None,
    descent_residuals: frozenset[tuple[str, str]] = frozenset(),
    silent: bool = True,
    decompilation_event: bool = False,
    out_of_class_split_pair: tuple[str, str] | None = None,
    challenge_class: str = WINDOW_CLASS,
    repair_refinement: str = WINDOW_REFINEMENT,
) -> CompiledOperatorCandidate:
    if move_sort not in {RepairSort.P1, RepairSort.P2}:
        raise ConstructionRejected("CompiledOperatorRecord requires move.sort P1 or P2")
    return CompiledOperatorCandidate(
        name=name,
        challenge_class=challenge_class,
        repair_refinement=repair_refinement,
        move_sort=move_sort,
        move_record=f"move:{name}",
        move_payload=f"payload:{name}",
        decompilation_record=f"decompile:{name}",
        annotation_carried=True,
        channel_record=channel_record,
        promotion_data=promotion_data,
        memory_only=memory_only,
        saturated_predicate=_same_family_saturated_from_active_family,
        active_family=ActiveFamily(
            support=("probe_e4",),
            weight={"probe_e4": F(1)},
            as_xi_family="xi_e4",
        ),
        probe=probe if probe is not None else f"probe:{name}",
        descent_residuals=descent_residuals,
        silent_future_invocations=() if silent else (
            InvocationWitness(
                time=3,
                source=3,
                target=4,
                payload_value=F(103, 10000),
                repair_refinement=repair_refinement,
                audit_entry="audit:future:3",
            ),
        ),
        decompilation_event_record=f"decomp_event:{name}" if decompilation_event else None,
        out_of_class_split_pair=out_of_class_split_pair,
    )


def build_wrong_sort_candidate() -> CompiledOperatorCandidate:
    return _candidate(
        "cand_wrong_sort",
        move_sort=RepairSort.P3,
        memory_only=_memory("memory:wrong_sort", reproduced_by_memory_only=False),
    )


def build_fixture() -> Fixture:
    window = _build_window("window_main", (0, 1, 2))
    scope_windows = {
        "window_no_obstruction_reduction": build_window_no_obstruction_reduction(),
        "window_payload_drift": build_window_payload_drift(),
    }
    channel_records = {
        "td_accepted_stack": accepted_top_down_record("td_accepted_stack"),
        "td_structural_only": structural_only_top_down_record(),
    }
    promotion_data = {
        "promotion:accepted": PromotionBridgeData("promotion:accepted", True, _pass_gates()),
        "promotion:rejected": PromotionBridgeData("promotion:rejected", True, _rejected_gates()),
    }
    candidates = {
        "cand_compiled": _candidate(
            "cand_compiled",
            memory_only=_memory("memory:cand_compiled", reproduced_by_memory_only=False),
        ),
        "cand_compiled_support_gate": _candidate(
            "cand_compiled_support_gate",
            move_sort=RepairSort.P2,
            memory_only=_memory("memory:cand_compiled_support_gate", reproduced_by_memory_only=False),
        ),
        "cand_mis_compiled": _candidate(
            "cand_mis_compiled",
            memory_only=_memory("memory:cand_mis_compiled", reproduced_by_memory_only=False),
            out_of_class_split_pair=("x", "y"),
        ),
        "cand_decompiled": _candidate(
            "cand_decompiled",
            memory_only=_memory("memory:cand_decompiled", reproduced_by_memory_only=False),
            decompilation_event=True,
        ),
        "cand_compiling_blocked_channel": _candidate(
            "cand_compiling_blocked_channel",
            channel_record="td_structural_only",
            memory_only=_memory("memory:blocked_channel", reproduced_by_memory_only=False),
        ),
        "cand_compiling_promotion_rejected": _candidate(
            "cand_compiling_promotion_rejected",
            promotion_data="promotion:rejected",
            memory_only=_memory("memory:promotion_rejected", reproduced_by_memory_only=False),
        ),
        "cand_compiling_memory_only": _candidate(
            "cand_compiling_memory_only",
            memory_only=_memory("memory:memory_only", reproduced_by_memory_only=True),
        ),
        "cand_compiling_same_family": _candidate(
            "cand_compiling_same_family",
            memory_only=_memory("memory:same_family", reproduced_by_memory_only=False),
            probe="probe_e4",
        ),
        "cand_compiling_unverified_descent": _candidate(
            "cand_compiling_unverified_descent",
            memory_only=_memory("memory:unverified_descent", reproduced_by_memory_only=False),
            descent_residuals=frozenset({("a", "b")}),
        ),
        "cand_statused_obstruction": _candidate(
            "cand_statused_obstruction",
            memory_only=_memory("memory:statused_obstruction", reproduced_by_memory_only=False),
            out_of_class_split_pair=("x", "y"),
        ),
        "cand_unattributed": _candidate(
            "cand_unattributed",
            memory_only=_memory("memory:unattributed", reproduced_by_memory_only=False),
            challenge_class="C_other_window",
            repair_refinement="R_other",
        ),
    }
    decompilation_events = {
        candidate.name: DecompilationEventRecord(
            name=candidate.decompilation_event_record,
            candidate_name=candidate.name,
            reverts_record=candidate.decompilation_record,
            carried=True,
        )
        for candidate in candidates.values()
        if candidate.decompilation_event_record is not None
    }
    obstruction_status_records = {
        "cand_statused_obstruction": ObstructionStatusRecord(
            name="obstruction_status:cand_statused_obstruction",
            candidate_name="cand_statused_obstruction",
            for_class=OTHER_CLASS,
            split_pair=("x", "y"),
            assigned_status=ObstructionClassification.accepted_brittleness,
            carried=True,
        )
    }
    expected_status = {
        None: CompilationStatus.exposed,
        "cand_compiled": CompilationStatus.compiled,
        "cand_compiled_support_gate": CompilationStatus.compiled,
        "cand_mis_compiled": CompilationStatus.mis_compiled,
        "cand_decompiled": CompilationStatus.decompiled,
        "cand_compiling_blocked_channel": CompilationStatus.compiling,
        "cand_compiling_promotion_rejected": CompilationStatus.compiling,
        "cand_compiling_memory_only": CompilationStatus.compiling,
        "cand_compiling_same_family": CompilationStatus.compiling,
        "cand_compiling_unverified_descent": CompilationStatus.compiling,
        "cand_statused_obstruction": CompilationStatus.compiled,
    }
    status_records = {
        candidate_name: CompilationStatusRecord(
            name=f"csr:{candidate_name if candidate_name is not None else 'none'}",
            window_ref=(WINDOW_CLASS, WINDOW_REFINEMENT),
            candidate_ref=None
            if candidate_name is None
            else candidates[candidate_name].move_record,
            status=status,
            supporting_ledger_entries=(
                f"ledger:status:{candidate_name if candidate_name is not None else 'none'}",
            ),
            supporting_audit_records=(
                f"audit:status:{candidate_name if candidate_name is not None else 'none'}",
            ),
        )
        for candidate_name, status in expected_status.items()
    }
    ledger_entries = {
        "ledger:seed",
        *(record.supporting_ledger_entries[0] for record in status_records.values()),
    }
    audit_records = {
        "audit:instrument:e4",
        *(invocation.audit_entry for invocation in window.invocations.values()),
        *(
            invocation.audit_entry
            for scope_window in scope_windows.values()
            for invocation in scope_window.invocations.values()
        ),
        *(record.supporting_audit_records[0] for record in status_records.values()),
    }
    config = _make_config(frozenset(ledger_entries), frozenset(audit_records))
    return Fixture(
        config=config,
        window=window,
        candidates=candidates,
        scope_windows=scope_windows,
        channel_records=channel_records,
        promotion_data=promotion_data,
        decompilation_events=decompilation_events,
        obstruction_status_records=obstruction_status_records,
        status_records=status_records,
        carried_compiled_records=frozenset(candidate.move_record for candidate in candidates.values()),
        carried_decompilation_records=frozenset(
            candidate.decompilation_record for candidate in candidates.values()
        ),
        carried_status_records=frozenset(record.name for record in status_records.values()),
        ledger_entries=frozenset(ledger_entries),
        audit_records=frozenset(audit_records),
        active_family=ActiveFamily(
            support=("probe_e4",),
            weight={"probe_e4": F(1)},
            as_xi_family="xi_e4",
        ),
    )


def endogenous_invocation_occurrence(
    fixture: Fixture,
    invocation: InvocationWitness,
) -> bool:
    return (
        invocation.source_tag is FineSourceTag.committed_state
        and invocation.generated_by_s is True
        and invocation.in_scope is True
        and invocation.repair_refinement == fixture.window.repair_refinement
        and fixture.config.e_system.T.supp_k(invocation.source, invocation.target)
        and invocation.audit_entry in fixture.audit_records
    )


def compilation_candidate_window(fixture: Fixture, window: CompilationCandidateWindow) -> bool:
    return (
        len(window.episode_times) >= 2
        and all(time in window.invocations for time in window.episode_times)
        and all(
            endogenous_invocation_occurrence(fixture, window.invocations[time])
            for time in window.episode_times
        )
    )


def obstruction_reducing_across_window(
    fixture: Fixture,
    window: CompilationCandidateWindow,
) -> bool:
    del fixture
    return all(
        window.obstruction_post[time].issubset(window.obstruction_pre[time])
        and len(window.obstruction_post[time]) < len(window.obstruction_pre[time])
        for time in window.episode_times
    )


def idempotence_stable_across_window(
    window: CompilationCandidateWindow,
    threshold: Fraction = THRESHOLD,
) -> bool:
    payloads = tuple(window.invocations[time].payload_value for time in window.episode_times)
    return all(abs(left - right) <= threshold for left in payloads for right in payloads)


def compiled_operator_record_attributed_to(
    fixture: Fixture,
    window: CompilationCandidateWindow,
    candidate: CompiledOperatorCandidate,
) -> bool:
    return (
        candidate.challenge_class == window.challenge_class
        and candidate.repair_refinement == window.repair_refinement
        and candidate.move_record in fixture.carried_compiled_records
    )


def decompilation_event_exists(
    fixture: Fixture,
    candidate: CompiledOperatorCandidate,
) -> bool:
    event = fixture.decompilation_events.get(candidate.name)
    return (
        event is not None
        and event.candidate_name == candidate.name
        and event.reverts_record == candidate.decompilation_record
        and event.carried is True
    )


def compilation_lawful(
    fixture: Fixture,
    candidate: CompiledOperatorCandidate,
) -> bool:
    channel = fixture.channel_records[candidate.channel_record]
    promotion_data = fixture.promotion_data[candidate.promotion_data]
    return (
        top_down_channel_accepted_bool(channel) is True
        and channel.effect_gate is True
        and accepted_promotion_family(promote(promotion_data)) is True
        and candidate.memory_only.survives_control is True
        and not same_family_saturated(
            candidate.saturated_predicate,
            candidate.active_family,
            candidate.probe,
        )
        and candidate.annotation_carried is True
    )


def compiled_descent(candidate: CompiledOperatorCandidate) -> bool:
    return not candidate.descent_residuals


def higher_package_goes_silent(
    fixture: Fixture,
    window: CompilationCandidateWindow,
    candidate: CompiledOperatorCandidate,
    after_time: int = 2,
) -> bool:
    return (
        not candidate.silent_future_invocations
        and not window.future_invocations_after.get(after_time, ())
    )


def carried_obstruction_status_for(
    fixture: Fixture,
    candidate: CompiledOperatorCandidate,
    split_pair: tuple[str, str],
) -> bool:
    record = fixture.obstruction_status_records.get(candidate.name)
    return (
        record is not None
        and record.candidate_name == candidate.name
        and record.for_class == OTHER_CLASS
        and record.split_pair == split_pair
        and record.carried is True
    )


def out_of_class_obstruction_witness(
    fixture: Fixture,
    candidate: CompiledOperatorCandidate,
) -> bool:
    return (
        candidate.out_of_class_split_pair is not None
        and not carried_obstruction_status_for(
            fixture,
            candidate,
            candidate.out_of_class_split_pair,
        )
    )


def exposed_case(fixture: Fixture, candidate_opt: str | None) -> bool:
    del fixture
    return candidate_opt is None


def decompiled_case(
    fixture: Fixture,
    window: CompilationCandidateWindow,
    candidate: CompiledOperatorCandidate,
) -> bool:
    return (
        not exposed_case(fixture, candidate.name)
        and compiled_operator_record_attributed_to(fixture, window, candidate)
        and decompilation_event_exists(fixture, candidate)
    )


def compiled_case(
    fixture: Fixture,
    window: CompilationCandidateWindow,
    candidate: CompiledOperatorCandidate,
) -> bool:
    return (
        not exposed_case(fixture, candidate.name)
        and not decompiled_case(fixture, window, candidate)
        and compiled_operator_record_attributed_to(fixture, window, candidate)
        and compilation_lawful(fixture, candidate)
        and compiled_descent(candidate)
        and higher_package_goes_silent(fixture, window, candidate)
        and not out_of_class_obstruction_witness(fixture, candidate)
    )


def mis_compiled_case(
    fixture: Fixture,
    window: CompilationCandidateWindow,
    candidate: CompiledOperatorCandidate,
) -> bool:
    return (
        not exposed_case(fixture, candidate.name)
        and not decompiled_case(fixture, window, candidate)
        and compiled_operator_record_attributed_to(fixture, window, candidate)
        and compilation_lawful(fixture, candidate)
        and compiled_descent(candidate)
        and higher_package_goes_silent(fixture, window, candidate)
        and out_of_class_obstruction_witness(fixture, candidate)
    )


def compiling_case(
    fixture: Fixture,
    window: CompilationCandidateWindow,
    candidate: CompiledOperatorCandidate,
) -> bool:
    return (
        not exposed_case(fixture, candidate.name)
        and not decompiled_case(fixture, window, candidate)
        and not compiled_case(fixture, window, candidate)
        and not mis_compiled_case(fixture, window, candidate)
        and compiled_operator_record_attributed_to(fixture, window, candidate)
    )


def compilation_status_occurrence_for(
    fixture: Fixture,
    candidate_opt: str | None,
    record: CompilationStatusRecord,
) -> bool:
    expected_ref = None
    if candidate_opt is not None:
        expected_ref = fixture.candidates[candidate_opt].move_record
    return (
        record.window_ref == (fixture.window.challenge_class, fixture.window.repair_refinement)
        and record.candidate_ref == expected_ref
        and record.name in fixture.carried_status_records
        and record.source_tag is FineSourceTag.committed_state
        and record.generated_by_s is True
        and record.in_scope is True
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def classify_compilation_status(
    fixture: Fixture,
    candidate_opt: str | None,
) -> tuple[CompilationStatus, dict[str, bool], CompilationStatusRecord | None]:
    record = fixture.status_records.get(candidate_opt)
    occurrence = record is not None and compilation_status_occurrence_for(
        fixture,
        candidate_opt,
        record,
    )
    if candidate_opt is None:
        truths = {
            "exposed": exposed_case(fixture, None),
            "decompiled": False,
            "compiled": False,
            "mis_compiled": False,
            "compiling": False,
        }
        status = CompilationStatus.exposed if occurrence and truths["exposed"] else CompilationStatus.unclassified
        return status, truths, record if occurrence else None

    candidate = fixture.candidates[candidate_opt]
    truths = {
        "exposed": False,
        "decompiled": decompiled_case(fixture, fixture.window, candidate),
        "compiled": compiled_case(fixture, fixture.window, candidate),
        "mis_compiled": mis_compiled_case(fixture, fixture.window, candidate),
        "compiling": compiling_case(fixture, fixture.window, candidate),
    }
    for status in (
        CompilationStatus.decompiled,
        CompilationStatus.compiled,
        CompilationStatus.mis_compiled,
        CompilationStatus.compiling,
    ):
        if occurrence and truths[status.value]:
            return status, truths, record
    return CompilationStatus.unclassified, truths, record if occurrence else None


def e4_brittleness_instance(fixture: Fixture) -> bool:
    candidate = fixture.candidates["cand_mis_compiled"]
    split_pair = candidate.out_of_class_split_pair
    return split_pair is not None and out_of_class_obstruction_witness(fixture, candidate)


def _candidate_row(fixture: Fixture, candidate_opt: str | None) -> CandidateRow:
    status, truths, record = classify_compilation_status(fixture, candidate_opt)
    candidate = fixture.candidates.get(candidate_opt) if candidate_opt is not None else None
    return CandidateRow(
        candidate_opt="none" if candidate_opt is None else candidate_opt,
        attributed=None if candidate is None else compiled_operator_record_attributed_to(
            fixture,
            fixture.window,
            candidate,
        ),
        lawful=None if candidate is None else compilation_lawful(fixture, candidate),
        descent=None if candidate is None else compiled_descent(candidate),
        silent=None if candidate is None else higher_package_goes_silent(
            fixture,
            fixture.window,
            candidate,
        ),
        decompilation_event=None if candidate is None else decompilation_event_exists(
            fixture,
            candidate,
        ),
        out_of_class_witness=None if candidate is None else out_of_class_obstruction_witness(
            fixture,
            candidate,
        ),
        exposed=truths["exposed"] and status is CompilationStatus.exposed,
        decompiled=truths["decompiled"] and status is CompilationStatus.decompiled,
        compiled=truths["compiled"] and status is CompilationStatus.compiled,
        mis_compiled=truths["mis_compiled"] and status is CompilationStatus.mis_compiled,
        compiling=truths["compiling"] and status is CompilationStatus.compiling,
        status=status.value,
        carried_status_record=record.name if record else None,
    )


def _structural_controls(fixture: Fixture) -> tuple[ControlRow, ...]:
    rows: list[ControlRow] = []
    try:
        build_window_too_short()
        rows.append(ControlRow("window_too_short", False, "constructed", "construction rejected"))
    except ConstructionRejected as exc:
        rows.append(ControlRow("window_too_short", True, str(exc), "construction rejected"))

    try:
        build_wrong_sort_candidate()
        rows.append(ControlRow("cand_wrong_sort", False, "constructed", "construction rejected"))
    except ConstructionRejected as exc:
        rows.append(ControlRow("cand_wrong_sort", True, str(exc), "construction rejected"))

    no_reduction = fixture.scope_windows["window_no_obstruction_reduction"]
    no_reduction_constructible = compilation_candidate_window(fixture, no_reduction)
    no_reduction_obstruction = obstruction_reducing_across_window(fixture, no_reduction)
    no_reduction_idempotence = idempotence_stable_across_window(no_reduction)
    rows.append(
        ControlRow(
            "window_no_obstruction_reduction",
            no_reduction_constructible is True
            and no_reduction_obstruction is False
            and no_reduction_idempotence is True,
            (
                f"constructible={no_reduction_constructible}; "
                f"obstruction_reducing={no_reduction_obstruction}; "
                f"idempotence_stable={no_reduction_idempotence}"
            ),
            "constructible=True; obstruction_reducing=False; idempotence_stable=True",
        )
    )

    payload_drift = fixture.scope_windows["window_payload_drift"]
    payload_drift_constructible = compilation_candidate_window(fixture, payload_drift)
    payload_drift_obstruction = obstruction_reducing_across_window(fixture, payload_drift)
    payload_drift_idempotence = idempotence_stable_across_window(payload_drift)
    rows.append(
        ControlRow(
            "window_payload_drift",
            payload_drift_constructible is True
            and payload_drift_obstruction is True
            and payload_drift_idempotence is False,
            (
                f"constructible={payload_drift_constructible}; "
                f"obstruction_reducing={payload_drift_obstruction}; "
                f"idempotence_stable={payload_drift_idempotence}"
            ),
            "constructible=True; obstruction_reducing=True; idempotence_stable=False",
        )
    )

    candidate = fixture.candidates["cand_unattributed"]
    attributed = compiled_operator_record_attributed_to(fixture, fixture.window, candidate)
    status, truths, _record = classify_compilation_status(fixture, "cand_unattributed")
    rows.append(
        ControlRow(
            "cand_unattributed",
            attributed is False
            and status is CompilationStatus.unclassified
            and not any(truths.values()),
            f"attributed={attributed}; status={status.value}; truths={truths}",
            "attributed=False; status=unclassified",
        )
    )
    return tuple(rows)


def _fmt_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _row_summary(row: CandidateRow) -> str:
    return (
        f"attributed={_fmt_bool(row.attributed)}; lawful={_fmt_bool(row.lawful)}; "
        f"descent={_fmt_bool(row.descent)}; silent={_fmt_bool(row.silent)}; "
        f"decompilation={_fmt_bool(row.decompilation_event)}; "
        f"out_of_class={_fmt_bool(row.out_of_class_witness)}; status={row.status}"
    )


def _candidate_comparisons(rows: dict[str, CandidateRow]) -> list[Comparison]:
    expected = {
        "none": ("exposed", None, None, None, None, None),
        "cand_compiled": ("compiled", True, True, True, False, False),
        "cand_compiled_support_gate": ("compiled", True, True, True, False, False),
        "cand_mis_compiled": ("mis_compiled", True, True, True, False, True),
        "cand_decompiled": ("decompiled", True, True, True, True, False),
        "cand_compiling_blocked_channel": ("compiling", False, True, True, False, False),
        "cand_compiling_promotion_rejected": ("compiling", False, True, True, False, False),
        "cand_compiling_memory_only": ("compiling", False, True, True, False, False),
        "cand_compiling_same_family": ("compiling", False, True, True, False, False),
        "cand_compiling_unverified_descent": ("compiling", True, False, True, False, False),
        "cand_statused_obstruction": ("compiled", True, True, True, False, False),
    }
    comparisons: list[Comparison] = []
    for name, expected_values in expected.items():
        row = rows[name]
        observed = (
            row.status,
            row.lawful,
            row.descent,
            row.silent,
            row.decompilation_event,
            row.out_of_class_witness,
        )
        expected_status, lawful, descent, silent, decomp, witness = expected_values
        comparisons.append(
            Comparison(
                name,
                observed == expected_values
                and sum((row.exposed, row.decompiled, row.compiled, row.mis_compiled, row.compiling))
                == 1,
                _row_summary(row),
                (
                    f"status={expected_status}; lawful={_fmt_bool(lawful)}; "
                    f"descent={_fmt_bool(descent)}; silent={_fmt_bool(silent)}; "
                    f"decompilation={_fmt_bool(decomp)}; out_of_class={_fmt_bool(witness)}"
                ),
            )
        )
    return comparisons


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    rows = {row.candidate_opt: row for row in results.candidate_rows}
    comparisons = _candidate_comparisons(rows)
    comparisons.extend(
        Comparison(control.name, control.passed_control, control.observed, control.expected)
        for control in results.controls
    )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture, rows: tuple[CandidateRow, ...]) -> bool:
    return all(
        row.carried_status_record in fixture.carried_status_records
        for row in rows
        if row.status != CompilationStatus.unclassified.value
    ) and all(
        candidate.move_record in fixture.carried_compiled_records
        and candidate.channel_record in fixture.channel_records
        and candidate.promotion_data in fixture.promotion_data
        for candidate in fixture.candidates.values()
    )


def _no_hardcoded_status_discipline(rows: tuple[CandidateRow, ...]) -> bool:
    return all(
        sum((row.exposed, row.decompiled, row.compiled, row.mis_compiled, row.compiling)) == 1
        for row in rows
    )


def run_e4_repair_compilation_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = tuple(_candidate_row(fixture, candidate_opt) for candidate_opt in REGISTERED_CANDIDATE_OPTS)
    results = SweepResults(
        candidate_rows=rows,
        controls=_structural_controls(fixture),
        brittleness_holds=e4_brittleness_instance(fixture),
        window_obstruction_reducing=obstruction_reducing_across_window(fixture, fixture.window),
        window_idempotence_stable=idempotence_stable_across_window(fixture.window),
        actual_scope_discipline=_actual_scope_discipline(fixture, rows),
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(rows),
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E4 Repair Compilation Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e4_repair_compilation_sweep` "
        "against `formalization/notes/sweeps/E4_repair_compilation_predictions.md`.",
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
            "- The 20-state carrier uses Repair-World's `ring_kernel(20)` and the matching "
            "`suppK(z,z') = z' == (z+1) % 20` relation.",
            "- The shared window has three committed, generated, in-scope invocation witnesses; "
            "obstruction reduction and idempotence stability are computed from concrete split-pair "
            "sets and exact `Fraction` payload values.",
            "- `CompilationLawful` is computed from each candidate's own channel record, promotion "
            "data, memory-only comparator, same-family saturation predicate, and carried annotation.",
            "- The FIII promotion mirror follows `Promotion.lean`: accepted families are exactly "
            "`accepted`, `strict`, and `nonStrict` results of `Promote`.",
            "- The compiled/mis-compiled split uses the same lawful/descent/silent positive core and "
            "differs only by the unstatused out-of-class obstruction existential.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_e4_repair_compilation_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    total = len(results.comparisons)
    passed = sum(1 for comparison in results.comparisons if comparison.passed)
    print(f"E4 repair compilation sweep: {passed}/{total} comparisons PASS")
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    if failures:
        for failure in failures:
            print(f"FAIL {failure.name}: observed {failure.observed}; expected {failure.expected}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
