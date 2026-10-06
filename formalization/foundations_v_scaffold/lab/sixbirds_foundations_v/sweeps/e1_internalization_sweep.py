"""E1 internalization sweep against the pre-registered predictions.

The configuration is bound by
``formalization/notes/sweeps/E1_internalization_predictions.md``.  This module
evaluates that deterministic fixture with exact ``Fraction`` arithmetic.  The
enabled/ablated status comparison is deliberately generator-relative: it uses
the actual variant-specific ``S.R_S`` reachability and carried repair-family
evidence, not a generator-independent existential viability kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
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
    step,
)


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E1_internalization_results.md"
)

ITEMS = ("a", "b", "c", "d")
Q0 = {"a": "u", "b": "u", "c": "v", "d": "v"}
R_SPLIT = {"a": "a_star", "b": "b_star", "c": "rest", "d": "rest"}
R_SAME = {"a": "u", "b": "u", "c": "v", "d": "v"}
DEFECT_SPLIT = "split_ab_defect"
MOVE_RECORD_SPLIT = "move_split"
AUDIT_RECORD_SPLIT = "audit_split"
REPAIR_BUDGET_LINE = "repair-budget"
REPAIR_COST = F(2)
REPAIR_BUDGET = F(3)

C_BASE = ChallengeClass("baseline")
C_SPLIT = ChallengeClass("split_ab")

DELTA_ENDO_BAD_TAGS = frozenset(
    {
        FineSourceTag.fallback,
        FineSourceTag.unknown,
        FineSourceTag.contradictory,
        FineSourceTag.independent_pair_witness,
        FineSourceTag.simulation_trace,
        FineSourceTag.ablation_record,
    }
)


@dataclass(frozen=True)
class RepairAuditEntry:
    name: str
    source_tag: FineSourceTag
    generated_by_s: bool
    in_scope: bool
    carried: bool
    kernel_realized: bool
    in_repair_audit_entries: bool
    discharges: bool
    refinement: str
    cost: Fraction


@dataclass(frozen=True)
class HorizonStatus:
    horizon: int
    active_challenge: str
    binding: bool
    enabled_status: str
    enabled_residual: Fraction
    enabled_cumulative_spend: Fraction
    ablated_status: str
    ablated_residual: Fraction


@dataclass(frozen=True)
class DeltaDischargeRow:
    time: int
    variant: str
    pre_delta: int
    post_delta: int
    discharge: int


@dataclass(frozen=True)
class SourceCensus:
    installed_refinements: int
    committed_state: int
    generated_by_s_true: int
    in_scope_true: int
    carried: int
    kernel_realized: int
    in_repair_audit_entries: int
    delta_endo_entries: int
    fallback: int
    unknown: int
    contradictory: int
    independent_pair_witness: int
    simulation_trace: int
    ablation_record: int
    generated_by_s_false: int
    in_scope_false: int
    not_carried: int
    off_kernel: int
    audit_omitted: int


@dataclass(frozen=True)
class BudgetRow:
    time: int
    repair: str
    cost: Fraction
    cumulative_spend: Fraction
    budget_feasible: bool


@dataclass(frozen=True)
class ControlResult:
    name: str
    pre_delta: int
    post_delta: int
    discharge: int
    delta_endo_count: int
    endogenously_repairing_holds: bool
    status: str
    strict_challenge_descent: bool | None = None
    strict_self_extension: bool | None = None
    no_schedule_trap: bool | None = None
    in_repair_audit_entries: bool | None = None


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    challenge_schedule: dict[int, str]
    q1: dict[str, tuple[str, str]]
    q_same: dict[str, tuple[str, str]]
    delta_q0_split: int
    delta_q1_split: int
    delta_q0_base: int
    enabled_repair_lawful: bool
    ablated_repair_lawful: bool
    enabled_step_q: dict[str, tuple[str, str]]
    status_rows: tuple[HorizonStatus, ...]
    enabled_challenged_times: frozenset[int]
    ablated_challenged_times: frozenset[int]
    endogenous_family_valid_enabled: bool
    endogenous_family_valid_ablated: bool
    no_reachable_repair_generator_ablated: bool
    delta_rows: tuple[DeltaDischargeRow, ...]
    enabled_total_discharge: int
    ablated_total_discharge: int
    enabled_census: SourceCensus
    ablated_census: SourceCensus
    budget_rows: tuple[BudgetRow, ...]
    total_spend_enabled: Fraction
    remaining_budget_enabled: Fraction
    family_budget_feasible: bool
    controls: dict[str, ControlResult]
    generator_reachability_discipline: bool
    comparisons: tuple[Comparison, ...]


def challenge_process() -> ChallengeProcess:
    return ChallengeProcess(
        recurrence_period=1,
        default_challenge=C_BASE,
        drift_schedule={2: C_SPLIT},
        binding_states=frozenset({0, 1, 2, 3, 4}),
    )


def r_split(item: str) -> int:
    return {"a": 0, "b": 1, "c": 0, "d": 0}[item]


def delta_count(q: dict[str, Any], challenge: ChallengeClass) -> int:
    if challenge != C_SPLIT:
        return 0
    count = 0
    for idx, item in enumerate(ITEMS):
        for item_prime in ITEMS[idx + 1 :]:
            if q[item] == q[item_prime] and r_split(item) != r_split(item_prime):
                count += 1
    return count


def joined_quotient(
    q: dict[str, str], refinement: dict[str, str]
) -> dict[str, tuple[str, str]]:
    join = repair_join(lambda item: q[item], lambda item: refinement[item])
    return {item: join(item) for item in ITEMS}


def strict_challenge_descent(q_pre: dict[str, Any], q_post: dict[str, Any]) -> bool:
    return delta_count(q_post, C_SPLIT) < delta_count(q_pre, C_SPLIT)


def installs_repair_join(
    q_pre: dict[str, str],
    refinement: dict[str, str],
    q_next: dict[str, tuple[str, str]],
) -> bool:
    return joined_quotient(q_pre, refinement) == q_next


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


def _evidence(
    n0: int,
    tag: FineSourceTag = FineSourceTag.committed_state,
    *,
    generated_by_s: bool = True,
    in_scope: bool = True,
) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=tag,
        generated_by_s=generated_by_s,
        in_scope=in_scope,
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
    return ActiveFamily(support=("repair-monitor",), weight={"repair-monitor": F(1)})


def _ledger(trajectory: DeclaredTrajectory[int]) -> CarriedLedger[int, str]:
    entries = [REPAIR_BUDGET_LINE, "repair-spend"]
    entry_by_time = {0: REPAIR_BUDGET_LINE, 1: "repair-spend"}
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
    *, generator_enabled: bool
) -> tuple[
    RepairWorldConfig[str, object, str, str, str, dict[str, str], str, str],
    RepairWorldState[str, str, str, object, str, str, str, dict[str, str], str, str],
    RepairAction[str, str, str, str],
]:
    """Build the registered minimal Repair-World variant."""

    trajectory = _trajectory()
    ledger = _ledger(trajectory)
    active = _active_family()
    active_policy = _record_policy(trajectory, "active-family", {0: active, 4: active})
    economy = ProbeEconomy(
        catalog=ProbeCatalog(probes=("repair-monitor",), complete_probe_catalog=True),
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
        f="e1-f",
        sigma_f="e1-sigma",
        residual_family="e1-residuals",
        audit_access="e1-audit",
        formed_package=True,
    )
    defect_policy = _record_policy(trajectory, "defect", {2: DEFECT_SPLIT})
    move_policy = _record_policy(trajectory, "move", {2: MOVE_RECORD_SPLIT})
    audit_policy = _record_policy(trajectory, "audit", {2: AUDIT_RECORD_SPLIT})
    instrument_policy = _record_policy(trajectory, "instrument", {0: "instrument-0"})
    instrument_occurrence = CarriedRecordOccurrence(
        record="instrument-0",
        evidence=_evidence(0, FineSourceTag.audited_cell_records),
    )
    repair_move = RepairMove(
        sort=RepairSort.P4,
        payload=R_SPLIT,
        move_record=MOVE_RECORD_SPLIT,
        move_record_evidence=_evidence(2),
        budget_line=REPAIR_BUDGET_LINE,
    )
    instrument = ActiveCarriedInstrument(
        instrument="e1-instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=[instrument_occurrence],
        threshold_records=[instrument_occurrence],
        check_rule_records=[CheckRuleRecord(record=instrument_occurrence, audit="passes")],
        detects=lambda _z, defect: defect == DEFECT_SPLIT,
        gate_allows=lambda _z, defect, move: defect == DEFECT_SPLIT and move == repair_move,
        re_audits=lambda _z, _move, _z_next, audit: audit == AUDIT_RECORD_SPLIT,
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda _defect: repair_move,
        AdmissibleMove=lambda _ledger, _z, defect, move: (
            generator_enabled and defect == DEFECT_SPLIT and move == repair_move
        ),
    )
    config = RepairWorldConfig(
        kernel=_dummy_kernel(),
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
            "repair": REPAIR_BUDGET,
            "repair_spend": F(0),
            "exposure": F(0),
            "maintenance": F(0),
            "risk": F(0),
        },
        A=AuditState(instrument=instrument, flags=AuditFlags(frozenset({1, 2, 3}))),
    )
    action = RepairAction(
        repair_package=R_SPLIT,
        z_next=4,
        defect=DEFECT_SPLIT,
        defect_evidence=_evidence(2),
        audit_record=AUDIT_RECORD_SPLIT,
        audit_record_evidence=_evidence(2),
    )
    return config, state, action


def _dummy_kernel():
    # Repair actions use D4's `supp_k`; the E1 sweep does not classify status
    # through this external kernel.
    from sixbirds_foundations_v.worlds.repair_world import ring_kernel

    return ring_kernel(5)


def delta_endo(entry: RepairAuditEntry) -> bool:
    return entry.discharges and (
        entry.source_tag in DELTA_ENDO_BAD_TAGS
        or entry.generated_by_s is False
        or entry.in_scope is False
        or entry.carried is False
        or entry.kernel_realized is False
        or entry.in_repair_audit_entries is False
    )


def delta_endo_empty(entries: tuple[RepairAuditEntry, ...]) -> bool:
    return not any(delta_endo(entry) for entry in entries)


def challenged_episode_times(
    q_history: dict[int, dict[str, Any]], horizon: int
) -> frozenset[int]:
    process = challenge_process()
    return frozenset(
        time
        for time in range(horizon + 1)
        if process.challenge_at(time, 0) == C_SPLIT
        and delta_count(q_history[time], C_SPLIT) > 0
    )


def binding_by_horizon(q_history: dict[int, dict[str, Any]], horizon: int) -> bool:
    process = challenge_process()
    challenge_recurs = any(
        process.challenge_at(time, 0) == C_SPLIT for time in range(horizon + 1)
    )
    obstruction_times = challenged_episode_times(q_history, horizon)
    obstruction_nonempty = bool(obstruction_times)
    viability_relevant = obstruction_nonempty
    measured_slack_throughout = not obstruction_nonempty
    return (
        challenge_recurs
        and obstruction_nonempty
        and viability_relevant
        and not measured_slack_throughout
    )


def measured_discharge_through_horizon(
    entries_by_time: dict[int, tuple[RepairAuditEntry, ...]], horizon: int
) -> bool:
    return any(
        entry.discharges
        for time, entries in entries_by_time.items()
        if time <= horizon
        for entry in entries
    )


def residual_level(
    q_history: dict[int, dict[str, Any]],
    entries_by_time: dict[int, tuple[RepairAuditEntry, ...]],
    horizon: int,
) -> Fraction:
    residual = F(0)
    process = challenge_process()
    for time in range(horizon + 1):
        if (
            process.challenge_at(time, 0) == C_SPLIT
            and delta_count(q_history[time], C_SPLIT) > 0
        ):
            entries = entries_by_time.get(time, ())
            genuine_discharge = any(
                entry.discharges and not delta_endo(entry) for entry in entries
            )
            residual = F(0) if genuine_discharge else residual + F(1)
    return residual


def viability_descends(residual: Fraction) -> bool:
    return residual < F(3)


def _refinement_for_entry(entry: RepairAuditEntry) -> dict[str, str] | None:
    if entry.refinement == "R_split":
        return R_SPLIT
    if entry.refinement == "R_same":
        return R_SAME
    return None


def _endogenous_entry_valid(
    entry: RepairAuditEntry,
    q_pre: dict[str, str],
    q_post: dict[str, tuple[str, str]],
) -> bool:
    refinement = _refinement_for_entry(entry)
    return (
        refinement is not None
        and entry.source_tag is FineSourceTag.committed_state
        and entry.generated_by_s is True
        and entry.in_scope is True
        and entry.carried is True
        and entry.kernel_realized is True
        and entry.in_repair_audit_entries is True
        and entry.discharges is True
        and not delta_endo(entry)
        and installs_repair_join(q_pre, refinement, q_post)
        and strict_challenge_descent(q_pre, q_post)
    )


def endogenous_repair_family_valid(
    *,
    q_history: dict[int, dict[str, Any]],
    q_next_by_time: dict[int, dict[str, tuple[str, str]]],
    entries_by_time: dict[int, tuple[RepairAuditEntry, ...]],
    has_reachable_generator: bool,
    family_budget_feasible: bool,
    horizon: int,
) -> bool:
    times = challenged_episode_times(q_history, horizon)
    if not times or not has_reachable_generator or not family_budget_feasible:
        return False
    for time in times:
        entries = entries_by_time.get(time, ())
        if len(entries) != 1:
            return False
        q_post = q_next_by_time.get(time)
        if q_post is None:
            return False
        if not _endogenous_entry_valid(entries[0], q_history[time], q_post):
            return False
    for time, entries in entries_by_time.items():
        if time > horizon:
            continue
        q_post = q_next_by_time.get(time)
        if q_post is None:
            return False
        if not all(_endogenous_entry_valid(entry, q_history[time], q_post) for entry in entries):
            return False
    return True


def classify_status(
    *,
    binding: bool,
    delta_empty: bool,
    has_reachable_generator: bool,
    family_valid: bool,
    measured_discharge: bool,
    residual: Fraction,
    descends: bool,
) -> str:
    if not binding:
        return "slack"
    if not delta_empty and measured_discharge and descends and not family_valid:
        return "externally_subsidized"
    if delta_empty and measured_discharge and has_reachable_generator and family_valid:
        return "endogenously_repairing"
    residual_accrues = residual > F(0)
    collapse_residual = residual >= F(3)
    if delta_empty and not has_reachable_generator and descends and residual_accrues:
        return "stressed"
    if not has_reachable_generator and not descends and collapse_residual:
        return "collapsing"
    return "unclassified"


def _source_census(entries: tuple[RepairAuditEntry, ...]) -> SourceCensus:
    return SourceCensus(
        installed_refinements=len(entries),
        committed_state=sum(entry.source_tag is FineSourceTag.committed_state for entry in entries),
        generated_by_s_true=sum(entry.generated_by_s for entry in entries),
        in_scope_true=sum(entry.in_scope for entry in entries),
        carried=sum(entry.carried for entry in entries),
        kernel_realized=sum(entry.kernel_realized for entry in entries),
        in_repair_audit_entries=sum(entry.in_repair_audit_entries for entry in entries),
        delta_endo_entries=sum(delta_endo(entry) for entry in entries),
        fallback=sum(entry.source_tag is FineSourceTag.fallback for entry in entries),
        unknown=sum(entry.source_tag is FineSourceTag.unknown for entry in entries),
        contradictory=sum(entry.source_tag is FineSourceTag.contradictory for entry in entries),
        independent_pair_witness=sum(
            entry.source_tag is FineSourceTag.independent_pair_witness for entry in entries
        ),
        simulation_trace=sum(entry.source_tag is FineSourceTag.simulation_trace for entry in entries),
        ablation_record=sum(entry.source_tag is FineSourceTag.ablation_record for entry in entries),
        generated_by_s_false=sum(not entry.generated_by_s for entry in entries),
        in_scope_false=sum(not entry.in_scope for entry in entries),
        not_carried=sum(not entry.carried for entry in entries),
        off_kernel=sum(not entry.kernel_realized for entry in entries),
        audit_omitted=sum(not entry.in_repair_audit_entries for entry in entries),
    )


def _q_history_enabled(q1: dict[str, tuple[str, str]]) -> dict[int, dict[str, Any]]:
    return {time: (Q0 if time <= 2 else q1) for time in range(5)}


def _q_history_ablated() -> dict[int, dict[str, Any]]:
    return {time: Q0 for time in range(5)}


def _entries_through_horizon(
    entries_by_time: dict[int, tuple[RepairAuditEntry, ...]], horizon: int
) -> tuple[RepairAuditEntry, ...]:
    return tuple(
        entry
        for time, entries in entries_by_time.items()
        if time <= horizon
        for entry in entries
    )


def _status_for_horizon(
    *,
    q_history: dict[int, dict[str, Any]],
    q_next_by_time: dict[int, dict[str, tuple[str, str]]],
    entries_by_time: dict[int, tuple[RepairAuditEntry, ...]],
    has_reachable_generator: bool,
    family_budget_feasible: bool,
    horizon: int,
) -> tuple[str, Fraction, bool]:
    entries = _entries_through_horizon(entries_by_time, horizon)
    residual = residual_level(q_history, entries_by_time, horizon)
    family_valid = endogenous_repair_family_valid(
        q_history=q_history,
        q_next_by_time=q_next_by_time,
        entries_by_time=entries_by_time,
        has_reachable_generator=has_reachable_generator,
        family_budget_feasible=family_budget_feasible,
        horizon=horizon,
    )
    binding = binding_by_horizon(q_history, horizon)
    status = classify_status(
        binding=binding,
        delta_empty=delta_endo_empty(entries),
        has_reachable_generator=has_reachable_generator,
        family_valid=family_valid,
        measured_discharge=measured_discharge_through_horizon(entries_by_time, horizon),
        residual=residual,
        descends=viability_descends(residual),
    )
    return status, residual, binding


def _status_rows(
    *,
    q1: dict[str, tuple[str, str]],
    enabled_entries_by_time: dict[int, tuple[RepairAuditEntry, ...]],
    enabled_has_generator: bool,
    enabled_family_budget_feasible: bool,
    ablated_has_generator: bool,
) -> tuple[HorizonStatus, ...]:
    enabled_q_history = _q_history_enabled(q1)
    ablated_q_history = _q_history_ablated()
    enabled_q_next = {2: q1}
    ablated_entries_by_time: dict[int, tuple[RepairAuditEntry, ...]] = {}
    ablated_q_next: dict[int, dict[str, tuple[str, str]]] = {}
    process = challenge_process()
    spend_rows = _budget_rows()
    spend = {row.time: row.cumulative_spend for row in spend_rows}
    return tuple(
        (
            lambda enabled, ablated: HorizonStatus(
                horizon=horizon,
                active_challenge=process.challenge_at(horizon, 0).name,
                binding=enabled[2],
                enabled_status=enabled[0],
                enabled_residual=enabled[1],
                enabled_cumulative_spend=spend[horizon],
                ablated_status=ablated[0],
                ablated_residual=ablated[1],
            )
        )(
            _status_for_horizon(
                q_history=enabled_q_history,
                q_next_by_time=enabled_q_next,
                entries_by_time=enabled_entries_by_time,
                has_reachable_generator=enabled_has_generator,
                family_budget_feasible=enabled_family_budget_feasible,
                horizon=horizon,
            ),
            _status_for_horizon(
                q_history=ablated_q_history,
                q_next_by_time=ablated_q_next,
                entries_by_time=ablated_entries_by_time,
                has_reachable_generator=ablated_has_generator,
                family_budget_feasible=True,
                horizon=horizon,
            ),
        )
        for horizon in range(5)
    )


def _budget_rows() -> tuple[BudgetRow, ...]:
    rows: list[BudgetRow] = []
    cumulative = F(0)
    for time in range(5):
        cost = REPAIR_COST if time == 2 else F(0)
        cumulative += cost
        rows.append(
            BudgetRow(
                time=time,
                repair="rho_2" if time == 2 else "none",
                cost=cost,
                cumulative_spend=cumulative,
                budget_feasible=cumulative <= REPAIR_BUDGET,
            )
        )
    return tuple(rows)


def _delta_discharge_row(
    time: int,
    variant: str,
    q_pre: dict[str, Any],
    q_post: dict[str, Any],
) -> DeltaDischargeRow:
    pre_delta = delta_count(q_pre, C_SPLIT)
    post_delta = delta_count(q_post, C_SPLIT)
    return DeltaDischargeRow(
        time=time,
        variant=variant,
        pre_delta=pre_delta,
        post_delta=post_delta,
        discharge=pre_delta - post_delta,
    )


def _delta_discharge_rows(
    *,
    enabled_q_history: dict[int, dict[str, Any]],
    enabled_q_next: dict[int, dict[str, tuple[str, str]]],
    ablated_q_history: dict[int, dict[str, Any]],
) -> tuple[DeltaDischargeRow, ...]:
    return (
        _delta_discharge_row(2, "enabled", enabled_q_history[2], enabled_q_next[2]),
        *(
            _delta_discharge_row(time, "ablated", ablated_q_history[time], ablated_q_history[time])
            for time in (2, 3, 4)
        ),
    )


def _total_discharge(rows: tuple[DeltaDischargeRow, ...], variant: str) -> int:
    return sum(row.discharge for row in rows if row.variant == variant)


def _generator_reachability_discipline_holds(
    *,
    enabled_has_generator: bool,
    ablated_has_generator: bool,
    status_rows: tuple[HorizonStatus, ...],
) -> bool:
    return (
        enabled_has_generator is True
        and ablated_has_generator is False
        and any(
            row.binding
            and row.enabled_status == "endogenously_repairing"
            and row.ablated_status in {"stressed", "collapsing"}
            for row in status_rows
        )
    )


def _entries_are_strict_self_extensions(entries: tuple[RepairAuditEntry, ...]) -> bool:
    return bool(entries) and all(entry.refinement != "R_same" for entry in entries)


def _entries_pass_no_schedule_trap(entries: tuple[RepairAuditEntry, ...]) -> bool:
    return not any(entry.source_tag is FineSourceTag.simulation_trace for entry in entries)


def _entries_are_audit_listed(entries: tuple[RepairAuditEntry, ...]) -> bool:
    return bool(entries) and all(entry.in_repair_audit_entries for entry in entries)


def _classify_control(
    *,
    name: str,
    q_post: dict[str, tuple[str, str]],
    entries: tuple[RepairAuditEntry, ...],
    has_reachable_generator: bool,
) -> ControlResult:
    q_history = _q_history_ablated()
    entries_by_time = {2: entries}
    q_next_by_time = {2: q_post}
    horizon = 2
    residual = residual_level(q_history, entries_by_time, horizon)
    family_valid = endogenous_repair_family_valid(
        q_history=q_history,
        q_next_by_time=q_next_by_time,
        entries_by_time=entries_by_time,
        has_reachable_generator=has_reachable_generator,
        family_budget_feasible=True,
        horizon=horizon,
    )
    status = classify_status(
        binding=binding_by_horizon(q_history, horizon),
        delta_empty=delta_endo_empty(entries),
        has_reachable_generator=has_reachable_generator,
        family_valid=family_valid,
        measured_discharge=measured_discharge_through_horizon(entries_by_time, horizon),
        residual=residual,
        descends=viability_descends(residual),
    )
    return ControlResult(
        name=name,
        pre_delta=delta_count(Q0, C_SPLIT),
        post_delta=delta_count(q_post, C_SPLIT),
        discharge=delta_count(Q0, C_SPLIT) - delta_count(q_post, C_SPLIT),
        delta_endo_count=sum(delta_endo(entry) for entry in entries),
        endogenously_repairing_holds=status == "endogenously_repairing",
        status=status,
        strict_challenge_descent=strict_challenge_descent(Q0, q_post),
        strict_self_extension=_entries_are_strict_self_extensions(entries),
        no_schedule_trap=_entries_pass_no_schedule_trap(entries),
        in_repair_audit_entries=_entries_are_audit_listed(entries),
    )


def _control_results() -> dict[str, ControlResult]:
    q1 = joined_quotient(Q0, R_SPLIT)
    q_same = joined_quotient(Q0, R_SAME)
    fallback_entry = RepairAuditEntry(
        name="fallback-rho",
        source_tag=FineSourceTag.fallback,
        generated_by_s=False,
        in_scope=True,
        carried=False,
        kernel_realized=True,
        in_repair_audit_entries=True,
        discharges=True,
        refinement="R_split",
        cost=REPAIR_COST,
    )
    same_family_entry = RepairAuditEntry(
        name="same-family-rho",
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
        carried=True,
        kernel_realized=True,
        in_repair_audit_entries=True,
        discharges=False,
        refinement="R_same",
        cost=REPAIR_COST,
    )
    schedule_entry = RepairAuditEntry(
        name="schedule-trap-rho",
        source_tag=FineSourceTag.simulation_trace,
        generated_by_s=False,
        in_scope=True,
        carried=False,
        kernel_realized=True,
        in_repair_audit_entries=False,
        discharges=True,
        refinement="R_split",
        cost=REPAIR_COST,
    )
    omission_entry = RepairAuditEntry(
        name="audit-omitted-rho",
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
        carried=True,
        kernel_realized=True,
        in_repair_audit_entries=False,
        discharges=True,
        refinement="R_split",
        cost=REPAIR_COST,
    )
    return {
        "external_subsidy": _classify_control(
            name="external_subsidy",
            q_post=q1,
            entries=(fallback_entry,),
            has_reachable_generator=False,
        ),
        "same_family": _classify_control(
            name="same_family",
            q_post=q_same,
            entries=(same_family_entry,),
            has_reachable_generator=False,
        ),
        "schedule_trap": _classify_control(
            name="schedule_trap",
            q_post=q1,
            entries=(schedule_entry,),
            has_reachable_generator=False,
        ),
        "audit_omission": _classify_control(
            name="audit_omission",
            q_post=q1,
            entries=(omission_entry,),
            has_reachable_generator=False,
        ),
    }


def run_internalization_sweep() -> SweepResults:
    enabled_config, enabled_state, repair_action = build_repair_world(generator_enabled=True)
    ablated_config, ablated_state, ablated_action = build_repair_world(generator_enabled=False)
    q1 = joined_quotient(Q0, R_SPLIT)
    q_same = joined_quotient(Q0, R_SAME)
    enabled_lawful = (
        is_lawful_action(enabled_config, enabled_state, repair_action).status
        is LawfulnessStatus.lawful
    )
    ablated_lawful = (
        is_lawful_action(ablated_config, ablated_state, ablated_action).status
        is LawfulnessStatus.lawful
    )
    enabled_step_q = dict(step(enabled_config, enabled_state, repair_action).q)
    genuine_entry = RepairAuditEntry(
        name="rho_2",
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
        carried=True,
        kernel_realized=True,
        in_repair_audit_entries=True,
        discharges=True,
        refinement="R_split",
        cost=REPAIR_COST,
    )
    budget_rows = _budget_rows()
    enabled_entries_by_time = {2: (genuine_entry,)}
    ablated_entries_by_time: dict[int, tuple[RepairAuditEntry, ...]] = {}
    enabled_q_history = _q_history_enabled(q1)
    ablated_q_history = _q_history_ablated()
    enabled_q_next = {2: q1}
    enabled_family_budget_feasible = all(row.budget_feasible for row in budget_rows)
    enabled_family_valid = endogenous_repair_family_valid(
        q_history=enabled_q_history,
        q_next_by_time=enabled_q_next,
        entries_by_time=enabled_entries_by_time,
        has_reachable_generator=enabled_lawful,
        family_budget_feasible=enabled_family_budget_feasible,
        horizon=4,
    )
    ablated_family_valid = endogenous_repair_family_valid(
        q_history=ablated_q_history,
        q_next_by_time={},
        entries_by_time=ablated_entries_by_time,
        has_reachable_generator=ablated_lawful,
        family_budget_feasible=True,
        horizon=4,
    )
    status_rows = _status_rows(
        q1=q1,
        enabled_entries_by_time=enabled_entries_by_time,
        enabled_has_generator=enabled_lawful,
        enabled_family_budget_feasible=enabled_family_budget_feasible,
        ablated_has_generator=ablated_lawful,
    )
    delta_rows = _delta_discharge_rows(
        enabled_q_history=enabled_q_history,
        enabled_q_next=enabled_q_next,
        ablated_q_history=ablated_q_history,
    )
    generator_reachability_discipline = _generator_reachability_discipline_holds(
        enabled_has_generator=enabled_lawful,
        ablated_has_generator=ablated_lawful,
        status_rows=status_rows,
    )
    results = SweepResults(
        challenge_schedule={
            time: challenge_process().challenge_at(time, 0).name for time in range(5)
        },
        q1=q1,
        q_same=q_same,
        delta_q0_split=delta_count(Q0, C_SPLIT),
        delta_q1_split=delta_count(q1, C_SPLIT),
        delta_q0_base=delta_count(Q0, C_BASE),
        enabled_repair_lawful=enabled_lawful,
        ablated_repair_lawful=ablated_lawful,
        enabled_step_q=enabled_step_q,
        status_rows=status_rows,
        enabled_challenged_times=challenged_episode_times(enabled_q_history, 4),
        ablated_challenged_times=challenged_episode_times(ablated_q_history, 4),
        endogenous_family_valid_enabled=enabled_family_valid,
        endogenous_family_valid_ablated=ablated_family_valid,
        no_reachable_repair_generator_ablated=not ablated_lawful,
        delta_rows=delta_rows,
        enabled_total_discharge=_total_discharge(delta_rows, "enabled"),
        ablated_total_discharge=_total_discharge(delta_rows, "ablated"),
        enabled_census=_source_census((genuine_entry,)),
        ablated_census=_source_census(()),
        budget_rows=budget_rows,
        total_spend_enabled=budget_rows[-1].cumulative_spend,
        remaining_budget_enabled=REPAIR_BUDGET - budget_rows[-1].cumulative_spend,
        family_budget_feasible=enabled_family_budget_feasible,
        controls=_control_results(),
        generator_reachability_discipline=generator_reachability_discipline,
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    return (
        Comparison(
            "challenge switching",
            results.challenge_schedule == {
                0: "baseline",
                1: "baseline",
                2: "split_ab",
                3: "split_ab",
                4: "split_ab",
            },
            _schedule_summary(results.challenge_schedule),
            "0,1 baseline; 2,3,4 split_ab",
        ),
        Comparison(
            "split-pair DeltaCount",
            results.delta_q0_split == 1
            and results.delta_q1_split == 0
            and results.delta_q0_base == 0,
            f"Delta(Q0,C_split)={results.delta_q0_split}; "
            f"Delta(Q1,C_split)={results.delta_q1_split}; "
            f"Delta(Q0,C_base)={results.delta_q0_base}",
            "1, 0, 0",
        ),
        Comparison(
            "enabled repair action is reachable and lawful",
            results.enabled_repair_lawful
            and not results.ablated_repair_lawful
            and results.enabled_step_q == results.q1,
            f"enabled_lawful={results.enabled_repair_lawful}; "
            f"ablated_lawful={results.ablated_repair_lawful}; "
            f"step_q={results.enabled_step_q}",
            "enabled lawful; ablated not lawful; step applies Q0 vee R_split",
        ),
        Comparison(
            "matched five-way status table",
            _status_table_ok(results.status_rows),
            _status_summary(results.status_rows),
            "enabled: slack,slack,endogenous,endogenous,endogenous; "
            "ablated: slack,slack,stressed,stressed,collapsing",
        ),
        Comparison(
            "ablated stressed/collapsing exactly when binding",
            _ablated_binding_status_ok(results.status_rows),
            _binding_summary(results.status_rows),
            "binding horizons {2,3,4} have ablated statuses {stressed,stressed,collapsing}; before binding slack",
        ),
        Comparison(
            "challenged episode coverage",
            results.enabled_challenged_times == frozenset({2})
            and results.ablated_challenged_times == frozenset({2, 3, 4})
            and results.endogenous_family_valid_enabled
            and not results.endogenous_family_valid_ablated
            and results.no_reachable_repair_generator_ablated,
            f"enabled={_fmt_set(results.enabled_challenged_times)}; "
            f"ablated={_fmt_set(results.ablated_challenged_times)}; "
            f"family_enabled={results.endogenous_family_valid_enabled}; "
            f"family_ablated={results.endogenous_family_valid_ablated}; "
            f"no_generator_ablated={results.no_reachable_repair_generator_ablated}",
            "enabled {2}; ablated {2,3,4}; enabled family valid; ablated no reachable generator",
        ),
        Comparison(
            "Delta-discharge totals",
            results.enabled_total_discharge == 1 and results.ablated_total_discharge == 0,
            _delta_summary(results.delta_rows),
            "enabled total 1; ablated total 0",
        ),
        Comparison(
            "enabled source-class census",
            _enabled_census_ok(results.enabled_census),
            _census_summary(results.enabled_census),
            "one committed_state carried/kernel/audit-listed repair, Delta_endo=0, all bad-source counters 0",
        ),
        Comparison(
            "ablated source-class census",
            results.ablated_census.installed_refinements == 0
            and results.ablated_census.committed_state == 0
            and results.ablated_census.delta_endo_entries == 0,
            _census_summary(results.ablated_census),
            "installed=0, committed=0, Delta_endo=0",
        ),
        Comparison(
            "budget spend",
            results.total_spend_enabled == F(2)
            and results.remaining_budget_enabled == F(1)
            and results.family_budget_feasible,
            _budget_summary(results.budget_rows),
            "total spend 2, remaining budget 1, feasible",
        ),
        Comparison(
            "external-subsidy control",
            _external_subsidy_ok(results.controls["external_subsidy"]),
            _control_summary(results.controls["external_subsidy"]),
            "discharge 1, Delta_endo 1, not endogenous, status externally_subsidized",
        ),
        Comparison(
            "same-family saturation null",
            _same_family_ok(results.controls["same_family"]),
            _control_summary(results.controls["same_family"]),
            "discharge 0, no strict descent, no strict extension, not endogenous, status stressed",
        ),
        Comparison(
            "schedule-trap null",
            _schedule_trap_ok(results.controls["schedule_trap"]),
            _control_summary(results.controls["schedule_trap"]),
            "discharge 1, NoScheduleTrap false, Delta_endo 1, not endogenous, status externally_subsidized",
        ),
        Comparison(
            "audit-omission control",
            _audit_omission_ok(results.controls["audit_omission"]),
            _control_summary(results.controls["audit_omission"]),
            "discharge 1, audit omitted, Delta_endo 1, not endogenous, status externally_subsidized",
        ),
        Comparison(
            "generator-reachability discipline",
            results.generator_reachability_discipline,
            "status classifier uses variant-specific R_S reachability and carried family evidence",
            "not classified by a generator-independent existential kernel",
        ),
    )


def _status_table_ok(rows: tuple[HorizonStatus, ...]) -> bool:
    observed = tuple(
        (
            row.horizon,
            row.active_challenge,
            row.binding,
            row.enabled_status,
            row.enabled_residual,
            row.enabled_cumulative_spend,
            row.ablated_status,
            row.ablated_residual,
        )
        for row in rows
    )
    return observed == (
        (0, "baseline", False, "slack", F(0), F(0), "slack", F(0)),
        (1, "baseline", False, "slack", F(0), F(0), "slack", F(0)),
        (2, "split_ab", True, "endogenously_repairing", F(0), F(2), "stressed", F(1)),
        (3, "split_ab", True, "endogenously_repairing", F(0), F(2), "stressed", F(2)),
        (4, "split_ab", True, "endogenously_repairing", F(0), F(2), "collapsing", F(3)),
    )


def _ablated_binding_status_ok(rows: tuple[HorizonStatus, ...]) -> bool:
    return all(
        (
            row.ablated_status in {"stressed", "collapsing"}
            if row.binding
            else row.ablated_status == "slack"
        )
        for row in rows
    )


def _enabled_census_ok(census: SourceCensus) -> bool:
    return (
        census.installed_refinements == 1
        and census.committed_state == 1
        and census.generated_by_s_true == 1
        and census.in_scope_true == 1
        and census.carried == 1
        and census.kernel_realized == 1
        and census.in_repair_audit_entries == 1
        and census.delta_endo_entries == 0
        and census.fallback == 0
        and census.unknown == 0
        and census.contradictory == 0
        and census.independent_pair_witness == 0
        and census.simulation_trace == 0
        and census.ablation_record == 0
        and census.generated_by_s_false == 0
        and census.in_scope_false == 0
        and census.not_carried == 0
        and census.off_kernel == 0
        and census.audit_omitted == 0
    )


def _external_subsidy_ok(control: ControlResult) -> bool:
    return (
        control.pre_delta == 1
        and control.post_delta == 0
        and control.discharge == 1
        and control.delta_endo_count == 1
        and not control.endogenously_repairing_holds
        and control.status == "externally_subsidized"
    )


def _same_family_ok(control: ControlResult) -> bool:
    return (
        control.pre_delta == 1
        and control.post_delta == 1
        and control.discharge == 0
        and control.strict_challenge_descent is False
        and control.strict_self_extension is False
        and not control.endogenously_repairing_holds
        and control.status == "stressed"
    )


def _schedule_trap_ok(control: ControlResult) -> bool:
    return (
        control.pre_delta == 1
        and control.post_delta == 0
        and control.discharge == 1
        and control.no_schedule_trap is False
        and control.delta_endo_count == 1
        and not control.endogenously_repairing_holds
        and control.status == "externally_subsidized"
    )


def _audit_omission_ok(control: ControlResult) -> bool:
    return (
        control.discharge == 1
        and control.in_repair_audit_entries is False
        and control.delta_endo_count == 1
        and not control.endogenously_repairing_holds
        and control.status == "externally_subsidized"
    )


def _fmt_set(values: frozenset[int]) -> str:
    return "{" + ",".join(str(value) for value in sorted(values)) + "}"


def _schedule_summary(schedule: dict[int, str]) -> str:
    return "; ".join(f"t={time}:{challenge}" for time, challenge in sorted(schedule.items()))


def _status_summary(rows: tuple[HorizonStatus, ...]) -> str:
    return "; ".join(
        f"h={row.horizon}: challenge={row.active_challenge}, binding={row.binding}, "
        f"enabled=({row.enabled_status}, residual={row.enabled_residual}, spend={row.enabled_cumulative_spend}), "
        f"ablated=({row.ablated_status}, residual={row.ablated_residual})"
        for row in rows
    )


def _binding_summary(rows: tuple[HorizonStatus, ...]) -> str:
    return "; ".join(
        f"h={row.horizon}: binding={row.binding}, ablated={row.ablated_status}"
        for row in rows
    )


def _delta_summary(rows: tuple[DeltaDischargeRow, ...]) -> str:
    return "; ".join(
        f"{row.variant}@t={row.time}: {row.pre_delta}->{row.post_delta}, discharge={row.discharge}"
        for row in rows
    )


def _census_summary(census: SourceCensus) -> str:
    return (
        f"installed={census.installed_refinements}, committed={census.committed_state}, "
        f"generated_true={census.generated_by_s_true}, in_scope_true={census.in_scope_true}, "
        f"carried={census.carried}, kernel={census.kernel_realized}, "
        f"audit_listed={census.in_repair_audit_entries}, Delta_endo={census.delta_endo_entries}, "
        f"bad_tags=(fallback={census.fallback}, unknown={census.unknown}, "
        f"contradictory={census.contradictory}, independent={census.independent_pair_witness}, "
        f"simulation={census.simulation_trace}, ablation={census.ablation_record}), "
        f"generated_false={census.generated_by_s_false}, in_scope_false={census.in_scope_false}, "
        f"not_carried={census.not_carried}, off_kernel={census.off_kernel}, omitted={census.audit_omitted}"
    )


def _budget_summary(rows: tuple[BudgetRow, ...]) -> str:
    return "; ".join(
        f"t={row.time}: repair={row.repair}, cost={row.cost}, "
        f"cumulative={row.cumulative_spend}, feasible={row.budget_feasible}"
        for row in rows
    )


def _control_summary(control: ControlResult) -> str:
    details = [
        f"pre={control.pre_delta}",
        f"post={control.post_delta}",
        f"discharge={control.discharge}",
        f"Delta_endo={control.delta_endo_count}",
        f"endogenous={control.endogenously_repairing_holds}",
        f"status={control.status}",
    ]
    if control.strict_challenge_descent is not None:
        details.append(f"strict_descent={control.strict_challenge_descent}")
    if control.strict_self_extension is not None:
        details.append(f"strict_extension={control.strict_self_extension}")
    if control.no_schedule_trap is not None:
        details.append(f"NoScheduleTrap={control.no_schedule_trap}")
    if control.in_repair_audit_entries is not None:
        details.append(f"audit_listed={control.in_repair_audit_entries}")
    return ", ".join(details)


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E1 Internalization Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e1_internalization_sweep` against "
        "`formalization/notes/sweeps/E1_internalization_predictions.md`.",
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
            "- The status classifier is generator-relative. It uses the enabled/ablated variant's actual "
            "`S.R_S` reachability and carried repair-family evidence, not a generator-independent "
            "existential viability kernel.",
            "- The enabled repair action is checked through the Repair-World/D4 machinery: "
            "`is_lawful_action` accepts it and `step` applies D1 `repair_join` to produce `Q1`.",
            "- The ablated repair action is checked against the same world shape with `AdmissibleMove` "
            "closed for `defect_split`; `is_lawful_action` rejects it, matching "
            "`NoReachableRepairGenerator` for the registered defect.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_internalization_sweep()
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
