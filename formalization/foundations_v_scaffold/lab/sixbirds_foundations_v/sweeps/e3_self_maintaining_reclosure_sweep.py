"""E3 self-maintaining-reclosure sweep against the pre-registration.

The configuration is bound by
``formalization/notes/sweeps/E3_self_maintaining_reclosure_predictions.md``.
This module evaluates that deterministic fixture with exact ``Fraction``
arithmetic.  Maintenance status, ``Delta_maint`` controls, ablation curves, and
the E2 regress bridge are computed from carried apparatus/operator/status
records rather than copied from the prediction table.
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
from sixbirds_foundations_v.sweeps.e2_bounded_reflexivity_sweep import (
    CAPACITY as E2_CAPACITY,
    ClaimStatus,
    SameLevelSelfAuditClaim,
    levels_for_depth,
    run_bounded_reflexivity_sweep,
    same_level_self_audit_classify,
    tower_footprint as e2_tower_footprint,
)
from sixbirds_foundations_v.worlds.repair_world import (
    AuditFlags,
    AuditState,
    ChallengeClass,
    ChallengeProcess,
    LawfulnessStatus,
    MaintenanceAction,
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
    / "E3_self_maintaining_reclosure_results.md"
)

ITEMS = ("a", "b", "c", "d")
Q0 = {"a": "u", "b": "u", "c": "v", "d": "v"}
R_APP_BOUNDARY = {"a": "app_ok", "b": "app_ok", "c": "app_ok", "d": "app_ok"}
DEFECT_APP_BOUNDARY = "defect_app_boundary"
MOVE_APP_BOUNDARY = "move_app_boundary"
AUDIT_APP_BOUNDARY = "audit_app_boundary"
CAPACITY_LINE = "audit-capacity"

C_APP_BASE = ChallengeClass("apparatus_baseline")
C_APP_BOUNDARY = ChallengeClass("apparatus_boundary_drift")
EPSILON_APP = F(1, 4)
EPSILON_OBJ = F(1, 4)


class MaintenanceClosureStatus(str, Enum):
    crystal_grade = "crystal_grade"
    maintained_closure = "maintained_closure"
    subsidized_closure = "subsidized_closure"
    decaying_closure = "decaying_closure"
    unclassified = "unclassified"


@dataclass(frozen=True)
class ClosureApparatus:
    name: str
    time: int
    gate_instrument: str
    threshold_records: tuple[str, ...]
    app_boundary: int
    audit_data: int
    apparatus_record: str
    used_ledger_entries: tuple[str, ...]
    used_audit_records: tuple[str, ...]


@dataclass(frozen=True)
class ObjectClosureState:
    name: str
    time: int
    closure_components: tuple[str, ...]


@dataclass(frozen=True)
class ClosureMaintenanceOperator:
    name: str
    operator_record: str
    outputs: dict[int, ClosureApparatus]
    operator_ledger_entries: tuple[str, ...]
    operator_audit_records: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True

    def apply(self, source_state: int) -> ClosureApparatus:
        return self.outputs[source_state]


@dataclass(frozen=True)
class MaintenanceReinstatementRecord:
    name: str
    time: int
    source_state: int
    target_state: int
    operator_record: str
    pre_app_record: str
    post_app_record: str
    output_record: str
    reinstatement_ledger_entry: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True
    history_member: bool = True


@dataclass(frozen=True)
class MaintenanceStatusRecord:
    name: str
    time: int
    horizon: int
    status: MaintenanceClosureStatus
    object_fixed_point_record: str
    apparatus_record: str
    maintenance_operator_record: str | None
    reinstatement_record: MaintenanceReinstatementRecord | None
    apparatus_distance_record: str
    supporting_ledger_entries: tuple[str, ...]
    supporting_audit_records: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class Scenario:
    name: str
    t: int
    horizon: int
    challenge: ChallengeClass
    app_t: ClosureApparatus
    app_tplus1: ClosureApparatus
    status_record: MaintenanceStatusRecord
    operator: ClosureMaintenanceOperator | None
    reinstatement: MaintenanceReinstatementRecord | None
    object_fixed: bool = False
    object_coherent: bool = False
    object_transient: bool = False
    challenge_free: bool = False
    challenge_at: bool = False
    apparatus_repair_occurrence: bool = False
    stable_without_maintenance: bool = False
    decay_exceeds_tolerance: bool = False
    external_reinstated: bool = False
    no_valid_reinstatement: bool = False
    operator_accounts: bool = False
    audited_by_tower: bool = False
    e2_regress_stop: bool = False
    subsidized_candidates: tuple[
        tuple[ClosureApparatus, ClosureApparatus, MaintenanceReinstatementRecord | None, str],
        ...,
    ] = ()


@dataclass(frozen=True)
class DeltaControlRow:
    name: str
    record: MaintenanceReinstatementRecord | None
    component: str
    maintenance_reinstatement_for: bool
    delta_nonempty: bool
    delta_branch: str | None
    subsidized_witness: bool
    maintained_closure: bool
    subsidized_closure: bool


@dataclass(frozen=True)
class StatusRow:
    name: str
    status_record: str
    status: str
    crystal_grade: bool
    maintained_closure: bool
    subsidized_closure: bool
    decaying_closure: bool


@dataclass(frozen=True)
class AblationResult:
    name: str
    maintained_apparatus_curve: tuple[Fraction, ...]
    apparatus_curve: tuple[Fraction, ...]
    object_curve: tuple[Fraction, ...]
    separates: bool
    first_separation_time: int | None


@dataclass(frozen=True)
class E2BridgeResult:
    audited_by_tower: bool
    capacity_realizable: bool
    capacity_admissible: bool
    footprint: int
    cap: int
    bound_holds: bool
    e2_status: str
    same_level_claim_accepted: bool
    regress_stopped: bool


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    challenge_schedule: dict[int, str]
    repair_action_lawful: bool
    maintenance_actions: dict[str, bool]
    distances: dict[str, Fraction]
    theorem_rows: dict[str, dict[str, bool]]
    status_rows: tuple[StatusRow, ...]
    e2_bridge: E2BridgeResult
    ablation_pass: AblationResult
    ablation_fail: AblationResult
    delta_controls: tuple[DeltaControlRow, ...]
    unlinked_control: dict[str, bool]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    comparisons: tuple[Comparison, ...]


@dataclass(frozen=True)
class Fixture:
    config: RepairWorldConfig[str, object, str, str, str, dict[str, str], str, str]
    states: dict[str, RepairWorldState[str, str, str, object, str, str, str, dict[str, str], str, str]]
    repair_action: RepairAction[str, str, str, str]
    apparatus: dict[str, ClosureApparatus]
    operators: dict[str, ClosureMaintenanceOperator]
    reinstatements: dict[str, MaintenanceReinstatementRecord]
    statuses: dict[str, MaintenanceStatusRecord]
    scenarios: dict[str, Scenario]
    carried_apparatus_records: frozenset[str]
    carried_operator_records: frozenset[str]
    carried_status_records: frozenset[str]
    ledger_entries: frozenset[str]
    audit_records: frozenset[str]
    instrument_records: frozenset[str]
    carried_gate_instruments: frozenset[str]


def challenge_process() -> ChallengeProcess:
    return ChallengeProcess(
        recurrence_period=1,
        default_challenge=C_APP_BASE,
        drift_schedule={2: C_APP_BOUNDARY},
        binding_states=frozenset({0, 1, 2, 3, 4, 5}),
    )


def _trajectory() -> DeclaredTrajectory[int]:
    def tau(n: int) -> int:
        return n

    def legitimate_start(candidate_tau, n_start: int) -> bool:
        return n_start == 0 and candidate_tau(n_start) == 0

    return DeclaredTrajectory(
        legitimate_start=legitimate_start,
        supp_k=lambda z, z_next: z_next == z + 1,
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
    return ActiveFamily(support=("apparatus-monitor",), weight={"apparatus-monitor": F(1)})


def _ledger(trajectory: DeclaredTrajectory[int], entries: tuple[str, ...]) -> CarriedLedger[int, str]:
    entry_by_time = {index: entry for index, entry in enumerate(entries)}
    time_by_entry = {entry: index for index, entry in entry_by_time.items()}
    policy = _record_policy(trajectory, "ledger", entry_by_time)
    return CarriedLedger(
        ledger_policy=policy,
        ledger_entries=list(entries),
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: _evidence(time_by_entry[entry])
        if entry in time_by_entry
        else None,
    )


def _apparatus_records() -> dict[str, ClosureApparatus]:
    return {
        "app_0": ClosureApparatus(
            "app_0",
            0,
            "I_gate",
            ("theta_gate", "theta_budget"),
            10,
            100,
            "app_rec_0",
            ("led_app_0",),
            ("aud_app_0",),
        ),
        "app_1": ClosureApparatus(
            "app_1",
            1,
            "I_gate",
            ("theta_gate", "theta_budget"),
            10,
            101,
            "app_rec_1",
            ("led_app_1",),
            ("aud_app_1",),
        ),
        "app_2_pre": ClosureApparatus(
            "app_2_pre",
            2,
            "I_gate",
            ("theta_gate", "theta_budget"),
            20,
            200,
            "app_rec_2_pre",
            ("led_app_2_pre",),
            ("aud_app_2_pre",),
        ),
        "app_2_post": ClosureApparatus(
            "app_2_post",
            3,
            "I_gate",
            ("theta_gate", "theta_budget"),
            21,
            200,
            "app_rec_2_post",
            ("led_app_2_post",),
            ("aud_app_2_post",),
        ),
        "app_crystal_0": ClosureApparatus(
            "app_crystal_0",
            0,
            "I_gate_crystal",
            ("theta_crystal",),
            30,
            300,
            "app_rec_crystal_0",
            ("led_app_crystal",),
            ("aud_app_crystal",),
        ),
        "app_decay_0": ClosureApparatus(
            "app_decay_0",
            0,
            "I_gate_decay",
            ("theta_decay",),
            40,
            400,
            "app_rec_decay_0",
            ("led_app_decay",),
            ("aud_app_decay",),
        ),
        "app_decay_1": ClosureApparatus(
            "app_decay_1",
            1,
            "I_gate_decay",
            ("theta_decay_drifted",),
            44,
            404,
            "app_rec_decay_1",
            ("led_app_decay_1",),
            ("aud_app_decay_1",),
        ),
        "app_wrong": ClosureApparatus(
            "app_wrong",
            1,
            "I_gate_wrong",
            ("theta_wrong",),
            99,
            999,
            "app_rec_wrong",
            ("led_app_1",),
            ("aud_app_1",),
        ),
    }


def _all_ledger_entries(apps: dict[str, ClosureApparatus]) -> tuple[str, ...]:
    entries = {
        CAPACITY_LINE,
        "led_m_keep",
        "led_m_repair",
        "led_rr_keep",
        "led_rr_repair",
        "led_status_maint_free",
        "led_status_maint_challenged",
        "led_status_crystal",
        "led_status_subsidized",
        "led_status_decay",
    }
    for app in apps.values():
        entries.update(app.used_ledger_entries)
    for entry in (
        "led_rr_fallback",
        "led_rr_off_kernel",
        "led_rr_out_scope",
        "led_rr_non_carried",
        "led_rr_omitted",
        "led_rr_unlinked",
    ):
        entries.add(entry)
    return tuple(sorted(entries))


def _all_audit_records(apps: dict[str, ClosureApparatus]) -> frozenset[str]:
    records = {
        "aud_m_keep",
        "aud_m_repair",
        "aud_status_maint_free",
        "aud_status_maint_challenged",
        "aud_status_crystal",
        "aud_status_subsidized",
        "aud_status_decay",
        AUDIT_APP_BOUNDARY,
    }
    for app in apps.values():
        records.update(app.used_audit_records)
    return frozenset(records)


def build_fixture() -> Fixture:
    apps = _apparatus_records()
    ledger_entries = frozenset(_all_ledger_entries(apps))
    audit_records = _all_audit_records(apps)
    trajectory = _trajectory()
    ledger = _ledger(trajectory, tuple(sorted(ledger_entries)))
    active = _active_family()
    active_policy = _record_policy(trajectory, "active-family", {0: active, 5: active})
    economy = ProbeEconomy(
        catalog=ProbeCatalog(probes=("apparatus-monitor",), complete_probe_catalog=True),
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
        f="e3-f",
        sigma_f="e3-sigma",
        residual_family="e3-residuals",
        audit_access="e3-audit",
        formed_package=True,
    )
    defect_policy = _record_policy(trajectory, "defect", {2: DEFECT_APP_BOUNDARY})
    move_policy = _record_policy(trajectory, "move", {2: MOVE_APP_BOUNDARY})
    audit_policy = _record_policy(trajectory, "audit", {2: AUDIT_APP_BOUNDARY})
    instrument_policy = _record_policy(
        trajectory,
        "instrument",
        {
            0: "instrument-0",
            1: "theta_gate",
            2: "theta_budget",
            3: "theta_crystal",
            4: "theta_decay",
            5: "theta_decay_drifted",
        },
    )
    instrument_occurrences = {
        record: CarriedRecordOccurrence(record=record, evidence=_evidence(index))
        for index, record in enumerate(
            (
                "instrument-0",
                "theta_gate",
                "theta_budget",
                "theta_crystal",
                "theta_decay",
                "theta_decay_drifted",
            )
        )
    }
    move = RepairMove(
        sort=RepairSort.P4,
        payload=R_APP_BOUNDARY,
        move_record=MOVE_APP_BOUNDARY,
        move_record_evidence=_evidence(2),
        budget_line=CAPACITY_LINE,
    )
    moves = {DEFECT_APP_BOUNDARY: move}
    instrument = ActiveCarriedInstrument(
        instrument="e3-instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=[instrument_occurrences["instrument-0"]],
        threshold_records=[
            instrument_occurrences["theta_gate"],
            instrument_occurrences["theta_budget"],
        ],
        check_rule_records=[
            CheckRuleRecord(record=instrument_occurrences["instrument-0"], audit="passes")
        ],
        detects=lambda _z, defect: defect in moves,
        gate_allows=lambda _z, defect, candidate_move: moves.get(defect) == candidate_move,
        re_audits=lambda _z, _move, _z_next, audit: audit == AUDIT_APP_BOUNDARY,
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda defect: moves[defect],
        AdmissibleMove=lambda _ledger, _z, defect, candidate_move: moves.get(defect)
        == candidate_move,
    )
    config = RepairWorldConfig(
        kernel=ring_kernel(6),
        probe_economy=economy,
        e_system=system,
        challenge_process=challenge_process(),
    )

    def audit_state(_app: ClosureApparatus) -> AuditState[str, str, dict[str, str], str, str, str]:
        return AuditState(instrument=instrument, flags=AuditFlags(frozenset({0})))

    states = {
        "app_0": RepairWorldState(
            y=0,
            q=Q0,
            L=active,
            r=ledger,
            Lambda={"audit_capacity": F(E2_CAPACITY), "audit_spend": F(0)},
            A=audit_state(apps["app_0"]),
        ),
        "app_2_pre": RepairWorldState(
            y=2,
            q=Q0,
            L=active,
            r=ledger,
            Lambda={"audit_capacity": F(E2_CAPACITY), "audit_spend": F(0)},
            A=audit_state(apps["app_2_pre"]),
        ),
    }
    repair_action = RepairAction(
        repair_package=R_APP_BOUNDARY,
        z_next=3,
        defect=DEFECT_APP_BOUNDARY,
        defect_evidence=_evidence(2),
        audit_record=AUDIT_APP_BOUNDARY,
        audit_record_evidence=_evidence(2),
    )
    operators = {
        "m_keep": ClosureMaintenanceOperator(
            "m_keep",
            "m_keep_record",
            {0: apps["app_1"]},
            ("led_m_keep",),
            ("aud_m_keep",),
        ),
        "m_repair": ClosureMaintenanceOperator(
            "m_repair",
            "m_repair_record",
            {2: apps["app_2_post"]},
            ("led_m_repair",),
            ("aud_m_repair",),
        ),
    }
    reinstatements = {
        "rr_keep": MaintenanceReinstatementRecord(
            "rr_keep",
            0,
            0,
            1,
            "m_keep_record",
            "app_rec_0",
            "app_rec_1",
            "app_rec_1",
            "led_rr_keep",
        ),
        "rr_repair": MaintenanceReinstatementRecord(
            "rr_repair",
            2,
            2,
            3,
            "m_repair_record",
            "app_rec_2_pre",
            "app_rec_2_post",
            "app_rec_2_post",
            "led_rr_repair",
        ),
    }
    statuses = {
        "msr_maint_free": MaintenanceStatusRecord(
            "msr_maint_free",
            0,
            5,
            MaintenanceClosureStatus.maintained_closure,
            "ofp_0_5",
            "app_rec_1",
            "m_keep_record",
            reinstatements["rr_keep"],
            "dist_app0_app1_1_over_8",
            ("led_status_maint_free",),
            ("aud_status_maint_free",),
        ),
        "msr_maint_challenged": MaintenanceStatusRecord(
            "msr_maint_challenged",
            2,
            5,
            MaintenanceClosureStatus.maintained_closure,
            "ofp_2_5",
            "app_rec_2_post",
            "m_repair_record",
            reinstatements["rr_repair"],
            "dist_app2pre_app2post_1_over_8",
            ("led_status_maint_challenged",),
            ("aud_status_maint_challenged",),
        ),
        "msr_crystal": MaintenanceStatusRecord(
            "msr_crystal",
            0,
            5,
            MaintenanceClosureStatus.crystal_grade,
            "ofp_crystal",
            "app_rec_crystal_0",
            None,
            None,
            "dist_crystal",
            ("led_status_crystal",),
            ("aud_status_crystal",),
        ),
        "msr_subsidized_fallback": MaintenanceStatusRecord(
            "msr_subsidized_fallback",
            2,
            5,
            MaintenanceClosureStatus.subsidized_closure,
            "ofp_subsidized",
            "app_rec_2_post",
            None,
            None,
            "dist_subsidized",
            ("led_status_subsidized",),
            ("aud_status_subsidized",),
        ),
        "msr_decay": MaintenanceStatusRecord(
            "msr_decay",
            0,
            5,
            MaintenanceClosureStatus.decaying_closure,
            "ofp_decay",
            "app_rec_decay_1",
            None,
            None,
            "dist_decay",
            ("led_status_decay",),
            ("aud_status_decay",),
        ),
    }
    rr_fallback = replace(
        reinstatements["rr_repair"],
        name="rr_fallback",
        source_tag=FineSourceTag.fallback,
        reinstatement_ledger_entry="led_rr_fallback",
    )
    statuses["msr_subsidized_fallback"] = replace(
        statuses["msr_subsidized_fallback"], reinstatement_record=rr_fallback
    )
    scenarios = {
        "maintained_free": Scenario(
            "maintained_free",
            0,
            5,
            C_APP_BASE,
            apps["app_0"],
            apps["app_1"],
            statuses["msr_maint_free"],
            operators["m_keep"],
            reinstatements["rr_keep"],
            object_fixed=True,
            object_coherent=True,
            challenge_free=True,
        ),
        "maintained_challenged": Scenario(
            "maintained_challenged",
            2,
            5,
            C_APP_BOUNDARY,
            apps["app_2_pre"],
            apps["app_2_post"],
            statuses["msr_maint_challenged"],
            operators["m_repair"],
            reinstatements["rr_repair"],
            object_fixed=True,
            object_coherent=True,
            challenge_at=True,
            apparatus_repair_occurrence=True,
            audited_by_tower=True,
            e2_regress_stop=True,
        ),
        "crystal_stable": Scenario(
            "crystal_stable",
            0,
            5,
            C_APP_BASE,
            apps["app_crystal_0"],
            apps["app_crystal_0"],
            statuses["msr_crystal"],
            None,
            None,
            object_fixed=True,
            object_coherent=True,
            stable_without_maintenance=True,
        ),
        "subsidized_fallback": Scenario(
            "subsidized_fallback",
            2,
            5,
            C_APP_BOUNDARY,
            apps["app_2_pre"],
            apps["app_2_post"],
            statuses["msr_subsidized_fallback"],
            operators["m_repair"],
            rr_fallback,
            object_fixed=True,
            subsidized_candidates=((apps["app_2_pre"], apps["app_2_post"], rr_fallback, "theta_budget"),),
        ),
        "decaying_no_repair": Scenario(
            "decaying_no_repair",
            0,
            5,
            C_APP_BASE,
            apps["app_decay_0"],
            apps["app_decay_1"],
            statuses["msr_decay"],
            None,
            None,
            object_transient=True,
            no_valid_reinstatement=True,
            decay_exceeds_tolerance=True,
        ),
    }
    return Fixture(
        config=config,
        states=states,
        repair_action=repair_action,
        apparatus=apps,
        operators=operators,
        reinstatements={**reinstatements, "rr_fallback": rr_fallback},
        statuses=statuses,
        scenarios=scenarios,
        carried_apparatus_records=frozenset(app.apparatus_record for app in apps.values()),
        carried_operator_records=frozenset(op.operator_record for op in operators.values()),
        carried_status_records=frozenset(
            {status.name for status in statuses.values()}
            | {
                "msr_absent_record",
                "msr_fallback_source",
                "msr_off_kernel",
                "msr_out_of_scope",
                "msr_non_carried",
                "msr_audit_omission",
            }
        ),
        ledger_entries=ledger_entries,
        audit_records=audit_records,
        instrument_records=frozenset(
            {
                "theta_gate",
                "theta_budget",
                "theta_crystal",
                "theta_decay",
                "theta_decay_drifted",
            }
        ),
        carried_gate_instruments=frozenset({"I_gate", "I_gate_crystal", "I_gate_decay"}),
    )


def maintenance_action_for(
    fixture: Fixture,
    state_name: str,
    app_tplus1: ClosureApparatus,
    operator: ClosureMaintenanceOperator,
    record: MaintenanceReinstatementRecord,
) -> MaintenanceAction[str]:
    state = fixture.states[state_name]
    return MaintenanceAction(
        operator=operator,
        source_state=record.source_state,
        target_state=record.target_state,
        current_audit_state=state.A,
        claimed_next_apparatus=app_tplus1,
        source_tag=record.source_tag,
        generated_by_s=record.generated_by_s,
        in_scope=record.in_scope,
        reinstatement_ledger_entry=record.reinstatement_ledger_entry,
    )


def closure_apparatus_occurrence_for(fixture: Fixture, t: int, app: ClosureApparatus) -> bool:
    return (
        app.time == t
        and app.apparatus_record in fixture.carried_apparatus_records
        and app.gate_instrument in fixture.carried_gate_instruments
        and all(record in fixture.instrument_records for record in app.threshold_records)
        and all(entry in fixture.ledger_entries for entry in app.used_ledger_entries)
        and all(record in fixture.audit_records for record in app.used_audit_records)
    )


def maintenance_operator_occurrence_for(
    fixture: Fixture,
    _t: int,
    operator: ClosureMaintenanceOperator,
) -> bool:
    return (
        operator.operator_record in fixture.carried_operator_records
        and operator.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and operator.generated_by_s is True
        and operator.in_scope is True
        and all(entry in fixture.ledger_entries for entry in operator.operator_ledger_entries)
        and all(record in fixture.audit_records for record in operator.operator_audit_records)
    )


def supp_k(source_state: int, target_state: int) -> bool:
    return target_state == source_state + 1


def maintenance_reinstatement_for(
    fixture: Fixture,
    t: int,
    app_t: ClosureApparatus,
    app_tplus1: ClosureApparatus,
    operator: ClosureMaintenanceOperator,
    record: MaintenanceReinstatementRecord,
) -> bool:
    return (
        closure_apparatus_occurrence_for(fixture, t, app_t)
        and closure_apparatus_occurrence_for(fixture, t + 1, app_tplus1)
        and maintenance_operator_occurrence_for(fixture, t, operator)
        and record.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and record.generated_by_s is True
        and record.in_scope is True
        and record.time == t
        and record.operator_record == operator.operator_record
        and record.pre_app_record == app_t.apparatus_record
        and record.post_app_record == app_tplus1.apparatus_record
        and record.output_record == operator.apply(record.source_state).apparatus_record
        and app_tplus1 == operator.apply(record.source_state)
        and app_tplus1.apparatus_record == operator.apply(record.source_state).apparatus_record
        and record.reinstatement_ledger_entry in fixture.ledger_entries
        and supp_k(record.source_state, record.target_state)
    )


def apparatus_distance(app_prime: ClosureApparatus, app: ClosureApparatus) -> Fraction:
    changes = (
        app_prime.gate_instrument != app.gate_instrument,
        app_prime.threshold_records != app.threshold_records,
        app_prime.app_boundary != app.app_boundary,
        app_prime.audit_data != app.audit_data,
    )
    return F(sum(1 for changed in changes if changed), 8)


def challenge_free_at(fixture: Fixture, t: int, y: int = 0) -> bool:
    return fixture.config.challenge_process.challenge_at(t, y) == C_APP_BASE


def closure_apparatus_challenge_at(fixture: Fixture, challenge: ChallengeClass, t: int) -> bool:
    return fixture.config.challenge_process.challenge_at(t, t) == challenge


def repair_action_lawful_and_steps(fixture: Fixture) -> bool:
    state = fixture.states["app_2_pre"]
    lawful = is_lawful_action(fixture.config, state, fixture.repair_action).status
    if lawful is not LawfulnessStatus.lawful:
        return False
    stepped = step(fixture.config, state, fixture.repair_action)
    join = repair_join(lambda item: Q0[item], lambda item: R_APP_BOUNDARY[item])
    return dict(stepped.q) == {item: join(item) for item in ITEMS}


def apparatus_level_repair_occurrence(fixture: Fixture, scenario: Scenario) -> bool:
    return (
        scenario.apparatus_repair_occurrence
        and repair_action_lawful_and_steps(fixture)
        and scenario.reinstatement is not None
        and scenario.operator is not None
        and maintenance_reinstatement_for(
            fixture,
            scenario.t,
            scenario.app_t,
            scenario.app_tplus1,
            scenario.operator,
            scenario.reinstatement,
        )
    )


def apparatus_maintained_step(fixture: Fixture, scenario: Scenario) -> bool:
    if scenario.operator is None or scenario.reinstatement is None:
        return False
    if not maintenance_reinstatement_for(
        fixture,
        scenario.t,
        scenario.app_t,
        scenario.app_tplus1,
        scenario.operator,
        scenario.reinstatement,
    ):
        return False
    challenge_free_branch = (
        scenario.challenge_free
        and challenge_free_at(fixture, scenario.t)
        and apparatus_distance(scenario.app_tplus1, scenario.app_t) <= EPSILON_APP
    )
    challenge_branch = (
        scenario.challenge_at
        and closure_apparatus_challenge_at(fixture, scenario.challenge, scenario.t)
        and apparatus_level_repair_occurrence(fixture, scenario)
    )
    return challenge_free_branch or challenge_branch


def object_level_fixed_point(fixture: Fixture, scenario: Scenario) -> bool:
    del fixture
    return scenario.object_fixed and scenario.object_coherent


def two_level_fixed_point(fixture: Fixture, scenario: Scenario) -> bool:
    return object_level_fixed_point(fixture, scenario) and apparatus_maintained_step(
        fixture, scenario
    )


def required_component(app: ClosureApparatus, component: str) -> bool:
    return component in {
        "gateInstrument",
        "AppBoundary",
        "auditData",
        *app.threshold_records,
    }


def delta_bad_source_tag(tag: FineSourceTag) -> bool:
    return tag in {
        FineSourceTag.fallback,
        FineSourceTag.unknown,
        FineSourceTag.contradictory,
        FineSourceTag.independent_pair_witness,
        FineSourceTag.simulation_trace,
        FineSourceTag.ablation_record,
    }


def delta_maint(
    fixture: Fixture,
    t: int,
    app_t: ClosureApparatus,
    app_tplus1: ClosureApparatus,
    component: str,
    record: MaintenanceReinstatementRecord | None,
    operator: ClosureMaintenanceOperator | None,
) -> tuple[bool, str | None]:
    if not required_component(app_tplus1, component):
        return False, None
    if record is None:
        return True, "absent_record"
    if delta_bad_source_tag(record.source_tag):
        return True, "bad_source_tag"
    if record.generated_by_s is False:
        return True, "generatedByS_false"
    if record.in_scope is False:
        return True, "out_of_scope"
    if operator is None or not maintenance_operator_occurrence_for(fixture, t, operator):
        return True, "operator_non_occurrence"
    if not supp_k(record.source_state, record.target_state):
        return True, "off_kernel"
    if not maintenance_reinstatement_for(fixture, t, app_t, app_tplus1, operator, record):
        return True, "maintenance_reinstatement_for_failure"
    if record.history_member is False:
        return True, "history_omission"
    return False, None


def delta_maint_empty(
    fixture: Fixture,
    t: int,
    app_t: ClosureApparatus,
    app_tplus1: ClosureApparatus,
    records: tuple[tuple[MaintenanceReinstatementRecord | None, ClosureMaintenanceOperator | None], ...],
) -> bool:
    components = ("gateInstrument", *app_tplus1.threshold_records, "AppBoundary", "auditData")
    return all(
        not delta_maint(fixture, t, app_t, app_tplus1, component, record, operator)[0]
        for component in components
        for record, operator in records
    )


def subsidized_reinstatement_witness(
    fixture: Fixture,
    t: int,
    app_t: ClosureApparatus,
    app_tplus1: ClosureApparatus,
    maybe_record: MaintenanceReinstatementRecord | None,
    component: str,
    operator: ClosureMaintenanceOperator | None,
) -> tuple[bool, str | None]:
    nonempty, branch = delta_maint(
        fixture, t, app_t, app_tplus1, component, maybe_record, operator
    )
    if not nonempty:
        return False, None
    if maybe_record is None:
        return branch == "absent_record", branch
    return branch in {
        "bad_source_tag",
        "generatedByS_false",
        "out_of_scope",
        "operator_non_occurrence",
        "maintenance_reinstatement_for_failure",
        "off_kernel",
        "history_omission",
    }, branch


def maintenance_audit_regress_stopped_by_e2(fixture: Fixture, scenario: Scenario) -> E2BridgeResult:
    e2_results = run_bounded_reflexivity_sweep()
    levels = levels_for_depth(3)
    footprint = e2_tower_footprint(levels)
    cap = E2_CAPACITY
    e2_status = next(row.status for row in e2_results.status_rows if row.config == "saturated_3")
    claim = SameLevelSelfAuditClaim(
        in_claim_types=True,
        self_dependent=True,
        has_level_shift_bridge=False,
    )
    same_level_claim_accepted = same_level_self_audit_classify(claim) is ClaimStatus.accepted
    audited = (
        scenario.operator is not None
        and scenario.reinstatement is not None
        and maintenance_operator_occurrence_for(fixture, scenario.t, scenario.operator)
        and apparatus_level_repair_occurrence(fixture, scenario)
        and e2_results.comparisons[0].passed
    )
    capacity_realizable = all(
        row.passed
        for row in e2_results.comparisons
        if row.name in {"capacity arithmetic", "capacity saturation"}
    )
    capacity_admissible = footprint <= cap
    regress_stopped = (
        audited
        and capacity_realizable
        and capacity_admissible
        and e2_status == "saturated"
        and not same_level_claim_accepted
    )
    return E2BridgeResult(
        audited_by_tower=audited,
        capacity_realizable=capacity_realizable,
        capacity_admissible=capacity_admissible,
        footprint=footprint,
        cap=cap,
        bound_holds=footprint <= cap,
        e2_status=e2_status,
        same_level_claim_accepted=same_level_claim_accepted,
        regress_stopped=regress_stopped,
    )


def no_subsidized_witnesses(fixture: Fixture, scenario: Scenario) -> bool:
    return all(
        not subsidized_reinstatement_witness(
            fixture, scenario.t, app_t, app_tplus1, maybe_record, component, scenario.operator
        )[0]
        for app_t, app_tplus1, maybe_record, component in scenario.subsidized_candidates
    )


def maintained_closure_evidence(fixture: Fixture, scenario: Scenario) -> bool:
    if scenario.operator is None or scenario.reinstatement is None:
        return False
    records = ((scenario.reinstatement, scenario.operator),)
    conditional = True
    if scenario.audited_by_tower:
        conditional = maintenance_audit_regress_stopped_by_e2(fixture, scenario).regress_stopped
    return (
        two_level_fixed_point(fixture, scenario)
        and apparatus_maintained_step(fixture, scenario)
        and delta_maint_empty(
            fixture, scenario.t, scenario.app_t, scenario.app_tplus1, records
        )
        and no_subsidized_witnesses(fixture, scenario)
        and conditional
    )


def maintenance_status_occurrence_for(fixture: Fixture, scenario: Scenario) -> bool:
    record = scenario.status_record
    return (
        record.name in fixture.carried_status_records
        and record.time == scenario.t
        and record.horizon == scenario.horizon
        and record.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and record.generated_by_s is True
        and record.in_scope is True
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def crystal_grade_case(fixture: Fixture, scenario: Scenario) -> bool:
    return (
        maintenance_status_occurrence_for(fixture, scenario)
        and scenario.status_record.status is MaintenanceClosureStatus.crystal_grade
        and scenario.status_record.reinstatement_record is None
        and scenario.status_record.maintenance_operator_record is None
        and scenario.object_fixed
        and scenario.object_coherent
        and not scenario.operator_accounts
        and scenario.reinstatement is None
        and no_subsidized_witnesses(fixture, scenario)
        and scenario.stable_without_maintenance
        and not scenario.decay_exceeds_tolerance
    )


def maintained_closure_case(fixture: Fixture, scenario: Scenario) -> bool:
    record = scenario.status_record
    return (
        maintenance_status_occurrence_for(fixture, scenario)
        and record.status is MaintenanceClosureStatus.maintained_closure
        and scenario.operator is not None
        and scenario.reinstatement is not None
        and record.reinstatement_record == scenario.reinstatement
        and record.maintenance_operator_record == scenario.operator.operator_record
        and maintenance_reinstatement_for(
            fixture,
            scenario.t,
            scenario.app_t,
            scenario.app_tplus1,
            scenario.operator,
            scenario.reinstatement,
        )
        and maintained_closure_evidence(fixture, scenario)
    )


def subsidized_closure_case(fixture: Fixture, scenario: Scenario) -> bool:
    record = scenario.status_record
    witness = any(
        subsidized_reinstatement_witness(
            fixture, scenario.t, app_t, app_tplus1, maybe_record, component, scenario.operator
        )[0]
        and record.reinstatement_record == maybe_record
        for app_t, app_tplus1, maybe_record, component in scenario.subsidized_candidates
    )
    return (
        maintenance_status_occurrence_for(fixture, scenario)
        and record.status is MaintenanceClosureStatus.subsidized_closure
        and record.maintenance_operator_record is None
        and scenario.object_fixed
        and witness
        and not maintained_closure_case(fixture, scenario)
    )


def decaying_closure_case(fixture: Fixture, scenario: Scenario) -> bool:
    return (
        maintenance_status_occurrence_for(fixture, scenario)
        and scenario.status_record.status is MaintenanceClosureStatus.decaying_closure
        and scenario.status_record.reinstatement_record is None
        and scenario.status_record.maintenance_operator_record is None
        and scenario.object_transient
        and scenario.reinstatement is None
        and no_subsidized_witnesses(fixture, scenario)
        and scenario.no_valid_reinstatement
        and not scenario.external_reinstated
        and scenario.decay_exceeds_tolerance
        and not scenario.stable_without_maintenance
    )


def classify_maintenance_status(
    fixture: Fixture,
    scenario: Scenario,
) -> tuple[MaintenanceClosureStatus, dict[str, bool]]:
    truths = {
        "crystal_grade": crystal_grade_case(fixture, scenario),
        "maintained_closure": maintained_closure_case(fixture, scenario),
        "subsidized_closure": subsidized_closure_case(fixture, scenario),
        "decaying_closure": decaying_closure_case(fixture, scenario),
    }
    for status in (
        MaintenanceClosureStatus.crystal_grade,
        MaintenanceClosureStatus.maintained_closure,
        MaintenanceClosureStatus.subsidized_closure,
        MaintenanceClosureStatus.decaying_closure,
    ):
        if truths[status.value]:
            return status, truths
    return MaintenanceClosureStatus.unclassified, truths


def _status_rows(fixture: Fixture) -> tuple[StatusRow, ...]:
    rows: list[StatusRow] = []
    for name in (
        "maintained_free",
        "maintained_challenged",
        "crystal_stable",
        "subsidized_fallback",
        "decaying_no_repair",
    ):
        scenario = fixture.scenarios[name]
        status, truths = classify_maintenance_status(fixture, scenario)
        rows.append(
            StatusRow(
                name=name,
                status_record=scenario.status_record.name,
                status=status.value,
                crystal_grade=truths["crystal_grade"],
                maintained_closure=truths["maintained_closure"],
                subsidized_closure=truths["subsidized_closure"],
                decaying_closure=truths["decaying_closure"],
            )
        )
    return tuple(rows)


def _theorem_rows(fixture: Fixture) -> dict[str, dict[str, bool]]:
    rows: dict[str, dict[str, bool]] = {}
    for name in ("maintained_free", "maintained_challenged"):
        scenario = fixture.scenarios[name]
        rows[name] = {
            "object_fixed": scenario.object_fixed,
            "object_coherent": scenario.object_coherent,
            "closure_occurrence_pre": closure_apparatus_occurrence_for(
                fixture, scenario.t, scenario.app_t
            ),
            "closure_occurrence_post": closure_apparatus_occurrence_for(
                fixture, scenario.t + 1, scenario.app_tplus1
            ),
            "operator_occurrence": scenario.operator is not None
            and maintenance_operator_occurrence_for(fixture, scenario.t, scenario.operator),
            "maintenance_reinstatement_for": scenario.operator is not None
            and scenario.reinstatement is not None
            and maintenance_reinstatement_for(
                fixture,
                scenario.t,
                scenario.app_t,
                scenario.app_tplus1,
                scenario.operator,
                scenario.reinstatement,
            ),
            "apparatus_maintained_step": apparatus_maintained_step(fixture, scenario),
            "delta_maint_empty": scenario.operator is not None
            and scenario.reinstatement is not None
            and delta_maint_empty(
                fixture,
                scenario.t,
                scenario.app_t,
                scenario.app_tplus1,
                ((scenario.reinstatement, scenario.operator),),
            ),
            "no_subsidized_witness": no_subsidized_witnesses(fixture, scenario),
            "regress_conditional": (
                maintenance_audit_regress_stopped_by_e2(fixture, scenario).regress_stopped
                if scenario.audited_by_tower
                else True
            ),
            "two_level_fixed_point": two_level_fixed_point(fixture, scenario),
            "maintained_closure_holds": maintained_closure_case(fixture, scenario),
        }
    return rows


def _delta_controls(fixture: Fixture) -> tuple[DeltaControlRow, ...]:
    base = fixture.reinstatements["rr_keep"]
    controls: tuple[tuple[str, MaintenanceReinstatementRecord | None], ...] = (
        ("absent_record", None),
        (
            "fallback_source",
            replace(
                base,
                name="rr_fallback",
                source_tag=FineSourceTag.fallback,
                reinstatement_ledger_entry="led_rr_fallback",
            ),
        ),
        (
            "off_kernel",
            replace(
                base,
                name="rr_off_kernel",
                target_state=3,
                reinstatement_ledger_entry="led_rr_off_kernel",
            ),
        ),
        (
            "out_of_scope",
            replace(
                base,
                name="rr_out_scope",
                in_scope=False,
                reinstatement_ledger_entry="led_rr_out_scope",
            ),
        ),
        (
            "non_carried",
            replace(
                base,
                name="rr_non_carried",
                generated_by_s=False,
                reinstatement_ledger_entry="led_rr_non_carried",
            ),
        ),
        (
            "audit_omission",
            replace(
                base,
                name="rr_omitted",
                history_member=False,
                reinstatement_ledger_entry="led_rr_omitted",
            ),
        ),
    )
    rows: list[DeltaControlRow] = []
    app_t = fixture.apparatus["app_0"]
    app_tplus1 = fixture.apparatus["app_1"]
    operator = fixture.operators["m_keep"]
    component = "theta_budget"
    for name, record in controls:
        mrf = (
            False
            if record is None
            else maintenance_reinstatement_for(fixture, 0, app_t, app_tplus1, operator, record)
        )
        delta, branch = delta_maint(fixture, 0, app_t, app_tplus1, component, record, operator)
        subsidy, _subsidy_branch = subsidized_reinstatement_witness(
            fixture, 0, app_t, app_tplus1, record, component, operator
        )
        scenario = Scenario(
            name,
            0,
            5,
            C_APP_BASE,
            app_t,
            app_tplus1,
            replace(
                fixture.statuses["msr_subsidized_fallback"],
                name=f"msr_{name}",
                time=0,
                apparatus_record=app_tplus1.apparatus_record,
                reinstatement_record=record,
            ),
            operator,
            record,
            object_fixed=True,
            subsidized_candidates=((app_t, app_tplus1, record, component),),
        )
        rows.append(
            DeltaControlRow(
                name=name,
                record=record,
                component=component,
                maintenance_reinstatement_for=mrf,
                delta_nonempty=delta,
                delta_branch=branch,
                subsidized_witness=subsidy,
                maintained_closure=maintained_closure_case(fixture, scenario),
                subsidized_closure=subsidized_closure_case(fixture, scenario),
            )
        )
    return tuple(rows)


def _unlinked_control(fixture: Fixture) -> dict[str, bool]:
    app_t = fixture.apparatus["app_0"]
    app_tplus1 = fixture.apparatus["app_1"]
    app_wrong = fixture.apparatus["app_wrong"]
    operator = replace(
        fixture.operators["m_keep"],
        outputs={0: app_wrong},
    )
    record = replace(
        fixture.reinstatements["rr_keep"],
        name="rr_unlinked",
        output_record="app_rec_wrong",
        reinstatement_ledger_entry="led_rr_unlinked",
    )
    state = fixture.states["app_0"]
    action = MaintenanceAction(
        operator=operator,
        source_state=record.source_state,
        target_state=record.target_state,
        current_audit_state=state.A,
        claimed_next_apparatus=app_tplus1,
        source_tag=record.source_tag,
        generated_by_s=record.generated_by_s,
        in_scope=record.in_scope,
        reinstatement_ledger_entry=record.reinstatement_ledger_entry,
    )
    return {
        "carried_operator_shaped_record_exists": maintenance_operator_occurrence_for(
            fixture, 0, fixture.operators["m_keep"]
        ),
        "carried_next_apparatus_record_exists": closure_apparatus_occurrence_for(
            fixture, 1, app_tplus1
        ),
        "full_output_equality": app_tplus1 == operator.apply(record.source_state),
        "maintenance_action_lawful": is_lawful_action(fixture.config, state, action).status
        is LawfulnessStatus.lawful,
        "maintenance_reinstatement_for": maintenance_reinstatement_for(
            fixture, 0, app_t, app_tplus1, operator, record
        ),
        "apparatus_maintained_step": apparatus_maintained_step(
            fixture,
            Scenario(
                "unlinked",
                0,
                5,
                C_APP_BASE,
                app_t,
                app_tplus1,
                fixture.statuses["msr_maint_free"],
                operator,
                record,
                object_fixed=True,
                object_coherent=True,
                challenge_free=True,
            ),
        ),
    }


def _maintenance_action_checks(fixture: Fixture) -> dict[str, bool]:
    keep = maintenance_action_for(
        fixture,
        "app_0",
        fixture.apparatus["app_1"],
        fixture.operators["m_keep"],
        fixture.reinstatements["rr_keep"],
    )
    repair = maintenance_action_for(
        fixture,
        "app_2_pre",
        fixture.apparatus["app_2_post"],
        fixture.operators["m_repair"],
        fixture.reinstatements["rr_repair"],
    )
    keep_state = fixture.states["app_0"]
    repair_state = fixture.states["app_2_pre"]
    keep_lawful = is_lawful_action(fixture.config, keep_state, keep).status is LawfulnessStatus.lawful
    repair_lawful = (
        is_lawful_action(fixture.config, repair_state, repair).status is LawfulnessStatus.lawful
    )
    keep_step = step(fixture.config, keep_state, keep)
    repair_step = step(fixture.config, repair_state, repair)
    return {
        "rr_keep": keep_lawful and keep_step.y == 1 and keep_step.A == keep_state.A,
        "rr_repair": repair_lawful
        and repair_step.y == 3
        and repair_step.A == repair_state.A,
    }


def object_distance(state: ObjectClosureState, baseline: ObjectClosureState) -> Fraction:
    changes = sum(
        1
        for current, base in zip(state.closure_components, baseline.closure_components)
        if current != base
    )
    return F(changes, 16)


def _apparatus_with_changes(
    baseline: ClosureApparatus,
    *,
    name: str,
    time: int,
    gate_instrument: str | None = None,
    threshold_records: tuple[str, ...] | None = None,
    app_boundary: int | None = None,
    audit_data: int | None = None,
) -> ClosureApparatus:
    return replace(
        baseline,
        name=name,
        time=time,
        gate_instrument=gate_instrument
        if gate_instrument is not None
        else baseline.gate_instrument,
        threshold_records=threshold_records
        if threshold_records is not None
        else baseline.threshold_records,
        app_boundary=app_boundary if app_boundary is not None else baseline.app_boundary,
        audit_data=audit_data if audit_data is not None else baseline.audit_data,
        apparatus_record=f"{baseline.apparatus_record}_{name}",
        used_ledger_entries=(f"led_{name}",),
        used_audit_records=(f"aud_{name}",),
    )


def _object_state(name: str, time: int, drifted_components: int) -> ObjectClosureState:
    components = tuple(
        f"obj_{index}_drifted" if index < drifted_components else f"obj_{index}_base"
        for index in range(5)
    )
    return ObjectClosureState(name, time, components)


def _fixed_reference_apparatus_curve(
    records: tuple[ClosureApparatus, ...],
    baseline: ClosureApparatus,
) -> tuple[Fraction, ...]:
    return tuple(apparatus_distance(record, baseline) for record in records)


def _cumulative_transition_apparatus_curve(
    records: tuple[ClosureApparatus, ...],
) -> tuple[Fraction, ...]:
    values = [F(0)]
    total = F(0)
    for previous, current in zip(records, records[1:]):
        total += apparatus_distance(current, previous)
        values.append(total)
    return tuple(values)


def _fixed_reference_object_curve(
    records: tuple[ObjectClosureState, ...],
    baseline: ObjectClosureState,
) -> tuple[Fraction, ...]:
    return tuple(object_distance(record, baseline) for record in records)


def curves_separate(
    apparatus_curve: tuple[Fraction, ...],
    object_curve: tuple[Fraction, ...],
    epsilon_app: Fraction = EPSILON_APP,
    epsilon_obj: Fraction = EPSILON_OBJ,
) -> tuple[bool, int | None]:
    for time, (app_value, obj_value) in enumerate(zip(apparatus_curve, object_curve)):
        if app_value > epsilon_app and obj_value <= epsilon_obj:
            return True, time
    return False, None


def _ablation_results() -> tuple[AblationResult, AblationResult]:
    app_baseline = ClosureApparatus(
        "ablation_app_0",
        0,
        "I_ablation",
        ("theta_ablation",),
        50,
        500,
        "app_rec_ablation_0",
        ("led_ablation_0",),
        ("aud_ablation_0",),
    )
    maintained_records = (
        app_baseline,
        *(
            _apparatus_with_changes(
                app_baseline,
                name=f"maintained_app_{time}",
                time=time,
                audit_data=500 + time,
            )
            for time in range(1, 6)
        ),
    )
    ablated_records = (
        app_baseline,
        _apparatus_with_changes(app_baseline, name="ablated_app_1", time=1, audit_data=501),
        _apparatus_with_changes(
            app_baseline,
            name="ablated_app_2",
            time=2,
            threshold_records=("theta_ablation_drifted",),
            app_boundary=51,
            audit_data=501,
        ),
        _apparatus_with_changes(
            app_baseline,
            name="ablated_app_3",
            time=3,
            gate_instrument="I_ablation_drifted",
            threshold_records=("theta_ablation_drifted",),
            app_boundary=51,
            audit_data=501,
        ),
        _apparatus_with_changes(
            app_baseline,
            name="ablated_app_4",
            time=4,
            gate_instrument="I_ablation_drifted",
            threshold_records=("theta_ablation_drifted",),
            app_boundary=51,
            audit_data=502,
        ),
        _apparatus_with_changes(
            app_baseline,
            name="ablated_app_5",
            time=5,
            gate_instrument="I_ablation_drifted",
            threshold_records=("theta_ablation_drifted",),
            app_boundary=52,
            audit_data=502,
        ),
    )
    object_records = tuple(
        _object_state(f"object_pass_{time}", time, drifted)
        for time, drifted in enumerate((0, 1, 1, 2, 3, 5))
    )
    maintained_curve = _fixed_reference_apparatus_curve(maintained_records, app_baseline)
    ablated_curve = _cumulative_transition_apparatus_curve(ablated_records)
    object_curve = _fixed_reference_object_curve(object_records, object_records[0])
    separates, first = curves_separate(ablated_curve, object_curve)
    pass_result = AblationResult(
        "maintained_ablation_pass",
        maintained_apparatus_curve=maintained_curve,
        apparatus_curve=ablated_curve,
        object_curve=object_curve,
        separates=separates,
        first_separation_time=first,
    )
    crystal_baseline = ClosureApparatus(
        "crystal_ablation_app_0",
        0,
        "I_crystal_ablation",
        ("theta_crystal_ablation",),
        60,
        600,
        "app_rec_crystal_ablation_0",
        ("led_crystal_ablation_0",),
        ("aud_crystal_ablation_0",),
    )
    crystal_records = (
        crystal_baseline,
        _apparatus_with_changes(
            crystal_baseline,
            name="crystal_ablation_app_1",
            time=1,
            audit_data=601,
        ),
        _apparatus_with_changes(
            crystal_baseline,
            name="crystal_ablation_app_2",
            time=2,
            audit_data=601,
        ),
        _apparatus_with_changes(
            crystal_baseline,
            name="crystal_ablation_app_3",
            time=3,
            audit_data=601,
        ),
        _apparatus_with_changes(
            crystal_baseline,
            name="crystal_ablation_app_4",
            time=4,
            audit_data=601,
        ),
        _apparatus_with_changes(
            crystal_baseline,
            name="crystal_ablation_app_5",
            time=5,
            audit_data=601,
        ),
    )
    fail_object_records = tuple(
        _object_state(f"object_fail_{time}", time, drifted)
        for time, drifted in enumerate((0, 1, 1, 2, 2, 2))
    )
    fail_curve = _cumulative_transition_apparatus_curve(crystal_records)
    fail_object_curve = _fixed_reference_object_curve(
        fail_object_records, fail_object_records[0]
    )
    fail_separates, fail_first = curves_separate(fail_curve, fail_object_curve)
    fail_result = AblationResult(
        "crystal_ablation_fail",
        maintained_apparatus_curve=(),
        apparatus_curve=fail_curve,
        object_curve=fail_object_curve,
        separates=fail_separates,
        first_separation_time=fail_first,
    )
    return pass_result, fail_result


def _distances(fixture: Fixture) -> dict[str, Fraction]:
    return {
        "app_1_vs_app_0": apparatus_distance(fixture.apparatus["app_1"], fixture.apparatus["app_0"]),
        "app_2_post_vs_app_2_pre": apparatus_distance(
            fixture.apparatus["app_2_post"], fixture.apparatus["app_2_pre"]
        ),
        "app_decay_1_vs_app_decay_0": apparatus_distance(
            fixture.apparatus["app_decay_1"], fixture.apparatus["app_decay_0"]
        ),
        "identical": apparatus_distance(fixture.apparatus["app_0"], fixture.apparatus["app_0"]),
    }


def _actual_scope_discipline(fixture: Fixture, status_rows: tuple[StatusRow, ...]) -> bool:
    return all(
        fixture.scenarios[row.name].status_record.name in fixture.carried_status_records
        and row.status == fixture.scenarios[row.name].status_record.status.value
        for row in status_rows
    )


def _no_hardcoded_status_discipline(status_rows: tuple[StatusRow, ...]) -> bool:
    return all(
        sum(
            (
                row.crystal_grade,
                row.maintained_closure,
                row.subsidized_closure,
                row.decaying_closure,
            )
        )
        == 1
        and row.status
        in {
            MaintenanceClosureStatus.crystal_grade.value,
            MaintenanceClosureStatus.maintained_closure.value,
            MaintenanceClosureStatus.subsidized_closure.value,
            MaintenanceClosureStatus.decaying_closure.value,
        }
        for row in status_rows
    )


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    controls = {row.name: row for row in results.delta_controls}
    return (
        Comparison(
            "fixture and carried objects",
            results.challenge_schedule
            == {
                0: "apparatus_baseline",
                1: "apparatus_baseline",
                2: "apparatus_boundary_drift",
                3: "apparatus_boundary_drift",
                4: "apparatus_boundary_drift",
                5: "apparatus_boundary_drift",
            }
            and results.maintenance_actions == {"rr_keep": True, "rr_repair": True},
            f"schedule={_mapping_summary(results.challenge_schedule)}; "
            f"maintenance_actions={results.maintenance_actions}",
            "registered challenge schedule and lawful rr_keep/rr_repair maintenance actions",
        ),
        Comparison(
            "full reinstatement equality",
            results.theorem_rows["maintained_free"]["maintenance_reinstatement_for"]
            and results.theorem_rows["maintained_challenged"]["maintenance_reinstatement_for"]
            and results.unlinked_control["maintenance_reinstatement_for"] is False,
            f"rr_keep={results.theorem_rows['maintained_free']['maintenance_reinstatement_for']}; "
            f"rr_repair={results.theorem_rows['maintained_challenged']['maintenance_reinstatement_for']}; "
            f"unlinked={results.unlinked_control['maintenance_reinstatement_for']}",
            "rr_keep/rr_repair pass; rr_unlinked fails full apparatus equality",
        ),
        Comparison(
            "challenge-free two-level fixed point",
            _theorem_row_ok(results.theorem_rows["maintained_free"])
            and results.distances["app_1_vs_app_0"] == F(1, 8),
            _theorem_summary(results.theorem_rows["maintained_free"])
            + f"; distance={results.distances['app_1_vs_app_0']}",
            "all maintained evidence conjuncts true; distance 1/8 <= 1/4",
        ),
        Comparison(
            "challenged maintained apparatus repair",
            _theorem_row_ok(results.theorem_rows["maintained_challenged"])
            and results.repair_action_lawful,
            _theorem_summary(results.theorem_rows["maintained_challenged"])
            + f"; repair_action_lawful={results.repair_action_lawful}",
            "E1-style repair witnesses and maintained evidence true",
        ),
        Comparison(
            "four-way maintenance status partition",
            _status_table_ok(results.status_rows),
            _status_summary(results.status_rows),
            "maintained, maintained, crystal, subsidized, decaying with exactly one true branch each",
        ),
        Comparison(
            "E2 regress-stop bridge",
            results.e2_bridge.regress_stopped
            and results.e2_bridge.footprint == 8
            and results.e2_bridge.cap == 8
            and results.e2_bridge.e2_status == "saturated"
            and results.e2_bridge.same_level_claim_accepted is False,
            _e2_bridge_summary(results.e2_bridge),
            "E2 depth-3 tower: 8 <= 8, saturated, same-level claim not accepted",
        ),
        Comparison(
            "ablation separation pass",
            results.ablation_pass.separates is True
            and results.ablation_pass.first_separation_time == 2
            and results.ablation_pass.maintained_apparatus_curve
            == (F(0), F(1, 8), F(1, 8), F(1, 8), F(1, 8), F(1, 8))
            and all(
                value <= EPSILON_APP
                for value in results.ablation_pass.maintained_apparatus_curve
            )
            and results.ablation_pass.apparatus_curve
            == (F(0), F(1, 8), F(3, 8), F(1, 2), F(5, 8), F(3, 4))
            and results.ablation_pass.object_curve
            == (F(0), F(1, 16), F(1, 16), F(1, 8), F(3, 16), F(5, 16)),
            _ablation_summary(results.ablation_pass),
            "maintained curve stays within tolerance; ablated curve separates first at time 2",
        ),
        Comparison(
            "ablation fail control",
            results.ablation_fail.separates is False
            and results.ablation_fail.first_separation_time is None
            and all(value <= EPSILON_APP for value in results.ablation_fail.apparatus_curve),
            _ablation_summary(results.ablation_fail),
            "crystal-grade fail control never separates",
        ),
        Comparison(
            "absent-record Delta_maint control",
            _delta_control_ok(controls["absent_record"], False, "absent_record"),
            _delta_summary(controls["absent_record"]),
            "MRF false, Delta nonempty via absent branch, subsidized not maintained",
        ),
        Comparison(
            "fallback-source Delta_maint control",
            _delta_control_ok(controls["fallback_source"], False, "bad_source_tag"),
            _delta_summary(controls["fallback_source"]),
            "fallback source tag produces subsidized closure",
        ),
        Comparison(
            "off-kernel Delta_maint control",
            _delta_control_ok(controls["off_kernel"], False, "off_kernel"),
            _delta_summary(controls["off_kernel"]),
            "suppK failure produces subsidized closure",
        ),
        Comparison(
            "out-of-scope Delta_maint control",
            _delta_control_ok(controls["out_of_scope"], False, "out_of_scope"),
            _delta_summary(controls["out_of_scope"]),
            "inScope false produces subsidized closure",
        ),
        Comparison(
            "non-carried Delta_maint control",
            _delta_control_ok(controls["non_carried"], False, "generatedByS_false"),
            _delta_summary(controls["non_carried"]),
            "generatedByS false produces subsidized closure",
        ),
        Comparison(
            "audit-omission Delta_maint control",
            _delta_control_ok(controls["audit_omission"], True, "history_omission"),
            _delta_summary(controls["audit_omission"]),
            "MRF true, Delta nonempty via history omission, subsidized not maintained",
        ),
        Comparison(
            "unlinked output evidence control",
            results.unlinked_control["carried_operator_shaped_record_exists"]
            and results.unlinked_control["carried_next_apparatus_record_exists"]
            and results.unlinked_control["full_output_equality"] is False
            and results.unlinked_control["maintenance_action_lawful"] is False
            and results.unlinked_control["apparatus_maintained_step"] is False,
            _mapping_summary(results.unlinked_control),
            "carried records exist, but full output equality/action/MRF/step all reject",
        ),
        Comparison(
            "actual carried maintenance scope",
            results.actual_scope_discipline,
            "all status rows use carried status records and actual scenario witnesses",
            "not classified by existential feasible operator/status",
        ),
        Comparison(
            "future sweep anti-hardcoding guard",
            results.no_hardcoded_status_discipline,
            "all status rows have exactly one computed branch truth",
            "statuses and pass/fail rows computed from fixture predicates",
        ),
    )


def run_self_maintaining_reclosure_sweep() -> SweepResults:
    fixture = build_fixture()
    schedule = {
        time: fixture.config.challenge_process.challenge_at(time, time).name
        for time in range(6)
    }
    maintenance_actions = _maintenance_action_checks(fixture)
    theorem_rows = _theorem_rows(fixture)
    status_rows = _status_rows(fixture)
    e2_bridge = maintenance_audit_regress_stopped_by_e2(
        fixture, fixture.scenarios["maintained_challenged"]
    )
    ablation_pass, ablation_fail = _ablation_results()
    delta_controls = _delta_controls(fixture)
    unlinked = _unlinked_control(fixture)
    results = SweepResults(
        challenge_schedule=schedule,
        repair_action_lawful=repair_action_lawful_and_steps(fixture),
        maintenance_actions=maintenance_actions,
        distances=_distances(fixture),
        theorem_rows=theorem_rows,
        status_rows=status_rows,
        e2_bridge=e2_bridge,
        ablation_pass=ablation_pass,
        ablation_fail=ablation_fail,
        delta_controls=delta_controls,
        unlinked_control=unlinked,
        actual_scope_discipline=_actual_scope_discipline(fixture, status_rows),
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(status_rows),
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def _theorem_row_ok(row: dict[str, bool]) -> bool:
    return all(row.values())


def _status_table_ok(rows: tuple[StatusRow, ...]) -> bool:
    expected = {
        "maintained_free": "maintained_closure",
        "maintained_challenged": "maintained_closure",
        "crystal_stable": "crystal_grade",
        "subsidized_fallback": "subsidized_closure",
        "decaying_no_repair": "decaying_closure",
    }
    return all(
        row.status == expected[row.name]
        and sum(
            (
                row.crystal_grade,
                row.maintained_closure,
                row.subsidized_closure,
                row.decaying_closure,
            )
        )
        == 1
        for row in rows
    )


def _delta_control_ok(row: DeltaControlRow, mrf_expected: bool, branch: str) -> bool:
    return (
        row.maintenance_reinstatement_for is mrf_expected
        and row.delta_nonempty is True
        and row.delta_branch == branch
        and row.subsidized_witness is True
        and row.maintained_closure is False
        and row.subsidized_closure is True
    )


def _fmt_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def _mapping_summary(mapping: dict[Any, Any]) -> str:
    return "; ".join(f"{key}={value}" for key, value in sorted(mapping.items()))


def _theorem_summary(row: dict[str, bool]) -> str:
    return "; ".join(f"{key}={value}" for key, value in sorted(row.items()))


def _status_summary(rows: tuple[StatusRow, ...]) -> str:
    return "; ".join(
        f"{row.name}: status={row.status}, branches="
        f"({row.crystal_grade},{row.maintained_closure},{row.subsidized_closure},{row.decaying_closure})"
        for row in rows
    )


def _delta_summary(row: DeltaControlRow) -> str:
    return (
        f"MRF={row.maintenance_reinstatement_for}; Delta={row.delta_nonempty}; "
        f"branch={row.delta_branch}; Subsidy={row.subsidized_witness}; "
        f"maintained={row.maintained_closure}; subsidized={row.subsidized_closure}"
    )


def _ablation_summary(result: AblationResult) -> str:
    maintained = (
        f"maintained=({','.join(_fmt_fraction(value) for value in result.maintained_apparatus_curve)}); "
        if result.maintained_apparatus_curve
        else ""
    )
    return (
        maintained
        + f"apparatus=({','.join(_fmt_fraction(value) for value in result.apparatus_curve)}); "
        f"object=({','.join(_fmt_fraction(value) for value in result.object_curve)}); "
        f"separates={result.separates}; first={result.first_separation_time}"
    )


def _e2_bridge_summary(result: E2BridgeResult) -> str:
    return (
        f"audited={result.audited_by_tower}; realizable={result.capacity_realizable}; "
        f"admissible={result.capacity_admissible}; footprint={result.footprint}; "
        f"cap={result.cap}; status={result.e2_status}; "
        f"sameLevelAccepted={result.same_level_claim_accepted}; stopped={result.regress_stopped}"
    )


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E3 Self-Maintaining Reclosure Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e3_self_maintaining_reclosure_sweep` "
        "against `formalization/notes/sweeps/E3_self_maintaining_reclosure_predictions.md`.",
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
            "- Maintenance lawfulness checks full apparatus-output equality, D3 source fields, ledger "
            "membership, and `S.T.suppK` through the shared Repair-World `MaintenanceAction` path.",
            "- `Delta_maint` is computed separately from `MaintenanceReinstatementFor`; the audit-omission "
            "control has `MaintenanceReinstatementFor = True` and fails only through the history-membership "
            "disjunct.",
            "- Ablation curves are derived from concrete per-time apparatus records and concrete object "
            "drift records, then checked by `curves_separate`; the maintained apparatus curve is part of "
            "the PASS/FAIL comparison.",
            "- Maintenance statuses are derived from branch evidence and carried status records; no status "
            "row is copied directly from the pre-registration table.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_self_maintaining_reclosure_sweep()
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
