"""E5 reclosure-collapse sweep against the pre-registration.

The configuration is fixed by
``formalization/notes/sweeps/E5_reclosure_collapse_predictions.md``.  The
module evaluates a deterministic 18-state ring fixture with concrete rescue
move records, exact-rational budgets, move-attributed descent readouts,
subsidy/suspension/revival witnesses, and carried status records.  Status
labels are computed from the case predicates and priority order; they are not
copied from the prediction table.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordPolicy,
    DeclaredTrajectory,
    FineSourceTag,
    carried_source,
)
from sixbirds_foundations_v.e_system import CarriedLedger
from sixbirds_foundations_v.probe_economy import (
    AcquisitionLedgerEvidence,
    ActiveFamily,
    ActiveFamilyClassification,
    AmountEntryWitness,
    ProbeCatalog,
    ProbeEconomy,
    ProbeMove,
    ProbeMoveKind,
    acquisition_strict,
    lawful_acquisition,
)
from sixbirds_foundations_v.sweeps.e3_self_maintaining_reclosure_sweep import (
    ClosureApparatus,
    ClosureMaintenanceOperator,
    MaintenanceReinstatementRecord,
    apparatus_distance,
    maintenance_reinstatement_for,
)
from sixbirds_foundations_v.worlds.repair_world import ring_kernel


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT
    / "formalization"
    / "notes"
    / "sweeps"
    / "E5_reclosure_collapse_results.md"
)

N_STATES = 18
CHALLENGE = "C_collapse"
OTHER_CHALLENGE = "C_other"
H0 = "h0"
H1 = "h1"
HORIZON_TIME = {H0: 3, H1: 4}

REGISTERED_SCENARIOS = (
    "scn_viable_self_repair",
    "scn_stressed_self_repair",
    "scn_viable_boundary_update",
    "scn_viable_acquisition",
    "scn_viable_apparatus_reclosure",
    "scn_subsidized_external_rescue",
    "scn_suspended_gated_operations",
    "scn_collapsed_recoverable",
    "scn_collapsed_irreversible",
    "scn_revived_new_lineage",
    "scn_post_withdrawal_reclassified",
)


class CollapseMoveKind(str, Enum):
    repair = "repair"
    boundary_update = "boundary_update"
    apparatus_reclosure = "apparatus_reclosure"
    acquisition = "acquisition"


class ReclosureCollapseStatus(str, Enum):
    revived = "revived"
    subsidized = "subsidized"
    suspended = "suspended"
    viable = "viable"
    stressed = "stressed"
    collapsed_recoverable = "collapsed_recoverable"
    collapsed_irreversible = "collapsed_irreversible"
    unclassified = "unclassified"


class CandidateFamily(str, Enum):
    repair = "repair"
    boundary = "boundary"
    reclosure = "reclosure"
    acquisition = "acquisition"


@dataclass(frozen=True)
class CollapseMoveRecord:
    move_id: int
    kind: CollapseMoveKind
    name: str


@dataclass(frozen=True)
class DescentReadoutRecord:
    name: str
    move_record: CollapseMoveRecord
    pre_delta: int
    post_delta: int
    spend: Fraction
    budget: Fraction
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True

    @property
    def budget_margin(self) -> Fraction:
        return self.budget - self.spend


@dataclass(frozen=True)
class RescueDescentCertificate:
    move_record: CollapseMoveRecord
    descent_for_move: CollapseMoveRecord
    descent_readout_record: DescentReadoutRecord
    probe_family_record: str = "probe_family_collapse"
    readout_for_declared_family: bool = True


@dataclass(frozen=True)
class CollapseBudgetWitness:
    move_record: CollapseMoveRecord
    spend: Fraction
    budget: Fraction
    budget_entry: str
    spend_entry: str


@dataclass(frozen=True)
class RepairRescueCandidate:
    name: str
    move_record: CollapseMoveRecord
    source: int
    target: int
    audit_record: str
    budget: CollapseBudgetWitness
    descent: RescueDescentCertificate
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class BoundaryUpdateCandidate:
    name: str
    move_record: CollapseMoveRecord
    pre_source: int
    post_target: int
    update_record: str
    budget: CollapseBudgetWitness
    descent: RescueDescentCertificate
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ApparatusReclosureCandidate:
    name: str
    move_record: CollapseMoveRecord
    t: int
    app_t: ClosureApparatus
    app_tplus1: ClosureApparatus
    operator: ClosureMaintenanceOperator
    record: MaintenanceReinstatementRecord
    budget: CollapseBudgetWitness
    descent: RescueDescentCertificate


@dataclass(frozen=True)
class AcquisitionRescueCandidate:
    name: str
    move_record: CollapseMoveRecord
    active_family: ActiveFamily[str, str]
    new_active_family: ActiveFamily[str, str]
    probe: str
    pre_classification: ActiveFamilyClassification
    post_classification: ActiveFamilyClassification
    ledger_evidence: AcquisitionLedgerEvidence[str]
    budget: CollapseBudgetWitness
    descent: RescueDescentCertificate
    risk_admissible: bool = True


@dataclass(frozen=True)
class RescueCandidate:
    name: str
    family: CandidateFamily
    payload: (
        RepairRescueCandidate
        | BoundaryUpdateCandidate
        | ApparatusReclosureCandidate
        | AcquisitionRescueCandidate
    )

    @property
    def move_record(self) -> CollapseMoveRecord:
        return self.payload.move_record


@dataclass(frozen=True)
class StatusedResidualAccrual:
    name: str
    challenge_class: str
    horizon: str
    residual_spend: Fraction
    residual_budget: Fraction
    residual_record: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class SubsidizerRescueCandidate:
    subsidizer: str
    move_record: CollapseMoveRecord
    spend: Fraction
    budget: Fraction
    readout: DescentReadoutRecord


@dataclass(frozen=True)
class ExternalSubsidyWitness:
    name: str
    subsidy_record: str
    challenge_class: str
    horizon: str
    supplied_move: SubsidizerRescueCandidate
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class SubsidyWithdrawalEvent:
    name: str
    prior_subsidy_record: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class SuspensionWitness:
    name: str
    suspension_record: str
    challenge_class: str
    horizon: str
    baseline_apparatus: ClosureApparatus
    current_apparatus: ClosureApparatus
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ReachabilityCertified:
    name: str
    challenge_class: str
    horizon: str
    unreachable: bool
    self_reachable: bool
    externally_reachable_only: bool


@dataclass(frozen=True)
class KernelCertified:
    name: str
    challenge_class: str
    horizon: str
    kernel_empty: bool
    kernel_nonempty: bool


@dataclass(frozen=True)
class RevivalWitness:
    name: str
    prior_status_ref: str
    old_lineage: str
    new_lineage: str
    reclosure_candidate: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class ReclosureCollapseStatusRecord:
    name: str
    challenge_class: str
    horizon: str
    status: ReclosureCollapseStatus
    residual_record: str | None = None
    rescue_move_record: CollapseMoveRecord | None = None
    subsidy_record: str | None = None
    suspension_record: str | None = None
    prior_status_record: str | None = None
    lineage_record: str | None = None
    reachability_record: str | None = None
    kernel_record: str | None = None
    supporting_ledger_entries: tuple[str, ...] = ()
    supporting_audit_records: tuple[str, ...] = ()
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class OrdinaryActivity:
    time: int
    name: str
    source: int
    target: int
    rescue_move: bool = False


@dataclass(frozen=True)
class Scenario:
    name: str
    challenge_class: str
    horizon: str
    declared_candidates: tuple[str, ...]
    constructible_universe: tuple[str, ...]
    status_record: str
    residual: str | None = None
    subsidy: str | None = None
    suspension: str | None = None
    reachability: str | None = None
    kernel: str | None = None
    revival: str | None = None
    ordinary_activity: tuple[OrdinaryActivity, ...] = ()


@dataclass(frozen=True)
class ScenarioRow:
    scenario: str
    complete_inventory: bool
    collapse_falsifier: bool
    collapsed_core: bool
    revived: bool
    subsidized: bool
    suspended: bool
    viable: bool
    stressed: bool
    collapsed_irreversible: bool
    collapsed_recoverable: bool
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
    scenario_rows: tuple[ScenarioRow, ...]
    controls: tuple[ControlRow, ...]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    comparisons: tuple[Comparison, ...]


@dataclass(frozen=True)
class Fixture:
    kernel: Any
    ledger: CarriedLedger[int, str]
    probe_economy: ProbeEconomy[str, str, str]
    candidates: dict[str, RescueCandidate]
    scenarios: dict[str, Scenario]
    status_records: dict[str, ReclosureCollapseStatusRecord]
    residuals: dict[str, StatusedResidualAccrual]
    subsidies: dict[str, ExternalSubsidyWitness]
    withdrawals: dict[str, SubsidyWithdrawalEvent]
    suspensions: dict[str, SuspensionWitness]
    reachability: dict[str, ReachabilityCertified]
    kernels: dict[str, KernelCertified]
    revivals: dict[str, RevivalWitness]
    active_subsidies: dict[tuple[str, str], tuple[str, ...]]
    operation_gates: tuple[tuple[int, str, bool], ...]
    challenge_schedule: tuple[tuple[int, str, bool], ...]
    carried_status_records: frozenset[str]
    ledger_entries: frozenset[str]
    audit_records: frozenset[str]
    carried_apparatus_records: frozenset[str]
    carried_gate_instruments: frozenset[str]
    carried_operator_records: frozenset[str]
    instrument_records: frozenset[str]


def _trajectory() -> DeclaredTrajectory[int]:
    return DeclaredTrajectory(
        legitimate_start=lambda _tau, n_start: n_start == 0,
        supp_k=lambda z, z_next: z_next == (z + 1) % N_STATES,
        tau=lambda n: n % N_STATES,
        step_in_scope=lambda _n: True,
        n_start=0,
    )


def _record_policy(name: str) -> CarriedRecordPolicy[int, str]:
    return CarriedRecordPolicy(
        trajectory=_trajectory(),
        coordinate_declared=lambda _rho: True,
        rho_of=lambda z: f"{name}:{z}",
        name=name,
    )


def _evidence(n0: int = 0) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )


def _right_supp(source: int, target: int) -> bool:
    return target == (source + 1) % N_STATES


def _move(name: str, move_id: int, kind: CollapseMoveKind) -> CollapseMoveRecord:
    return CollapseMoveRecord(move_id=move_id, kind=kind, name=name)


def _budget(move_record: CollapseMoveRecord, spend: Fraction, budget: Fraction) -> CollapseBudgetWitness:
    return CollapseBudgetWitness(
        move_record=move_record,
        spend=spend,
        budget=budget,
        budget_entry=f"budget:{budget}",
        spend_entry=f"spend:{spend}",
    )


def _readout(
    name: str,
    move_record: CollapseMoveRecord,
    pre_delta: int,
    post_delta: int,
    spend: Fraction,
    budget: Fraction,
) -> DescentReadoutRecord:
    return DescentReadoutRecord(
        name=f"readout:{name}",
        move_record=move_record,
        pre_delta=pre_delta,
        post_delta=post_delta,
        spend=spend,
        budget=budget,
    )


def _descent(
    move_record: CollapseMoveRecord,
    readout: DescentReadoutRecord,
    *,
    descent_for_move: CollapseMoveRecord | None = None,
) -> RescueDescentCertificate:
    return RescueDescentCertificate(
        move_record=move_record,
        descent_for_move=descent_for_move or move_record,
        descent_readout_record=readout,
    )


def _carried_ledger(entries: frozenset[str], trajectory: DeclaredTrajectory[int]) -> CarriedLedger[int, str]:
    ordered = tuple(sorted(entries))
    index = {entry: n for n, entry in enumerate(ordered)}
    return CarriedLedger(
        ledger_policy=CarriedRecordPolicy(
            trajectory=trajectory,
            coordinate_declared=lambda _rho: True,
            rho_of=lambda z: ordered[z] if 0 <= z < len(ordered) else ordered[0],
            name="ledger",
        ),
        ledger_entries=ordered,
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: _evidence(index[entry]) if entry in index else None,
    )


def _same_family_saturated(active_family: ActiveFamily[str, str], probe: str) -> bool:
    return active_family.contains(probe)


def _probe_economy(
    ledger_entries: frozenset[str],
    trajectory: DeclaredTrajectory[int],
) -> ProbeEconomy[str, str, str]:
    base = ActiveFamily(("probe_base",), {"probe_base": F(1)}, "L_base")
    stabilized = ActiveFamily(
        ("probe_base", "probe_stabilizer"),
        {"probe_base": F(1), "probe_stabilizer": F(1, 4)},
        "L_stabilized",
    )
    return ProbeEconomy(
        catalog=ProbeCatalog(("probe_base", "probe_stabilizer"), True),
        active_family_policy=CarriedRecordPolicy(
            trajectory=trajectory,
            coordinate_declared=lambda _rho: True,
            rho_of=lambda z: base if z == 0 else stabilized,
            name="active_family",
        ),
        same_family_saturated=_same_family_saturated,
        exposure_cost_entry=lambda entry, probe, amount: (
            entry in ledger_entries and probe == "probe_stabilizer" and amount == F(1, 4)
        ),
        exposure_budget_entry=lambda entry, amount: entry in ledger_entries and amount == F(1),
        exposure_spend_entry=lambda entry, amount: entry in ledger_entries and amount == F(1, 4),
        retirement_record_entry=lambda _entry, _probe: False,
        budget_admissible=lambda move: move.probe != "probe_overbudget",
    )


def _apparatus(name: str, time: int, record: str, *, boundary: int = 6, audit_data: int = 4) -> ClosureApparatus:
    return ClosureApparatus(
        name=name,
        time=time,
        gate_instrument="gate_collapse",
        threshold_records=("theta_stay", "theta_budget"),
        app_boundary=boundary,
        audit_data=audit_data,
        apparatus_record=record,
        used_ledger_entries=("budget:1",),
        used_audit_records=("reclosure_audit",),
    )


def _build_candidates(
    moves: dict[str, CollapseMoveRecord],
    ledger_entries: frozenset[str],
) -> dict[str, RescueCandidate]:
    def repair(
        name: str,
        source: int,
        target: int,
        spend: Fraction,
        budget: Fraction,
        pre_delta: int,
        post_delta: int,
        *,
        source_tag: FineSourceTag = FineSourceTag.committed_state,
        generated_by_s: bool = True,
        in_scope: bool = True,
        descent_for_move: CollapseMoveRecord | None = None,
        readout_move: CollapseMoveRecord | None = None,
    ) -> RescueCandidate:
        move_record = moves[name]
        readout = _readout(
            name,
            readout_move or move_record,
            pre_delta,
            post_delta,
            spend,
            budget,
        )
        payload = RepairRescueCandidate(
            name=name,
            move_record=move_record,
            source=source,
            target=target,
            audit_record="repair_audit",
            budget=_budget(move_record, spend, budget),
            descent=_descent(move_record, readout, descent_for_move=descent_for_move),
            source_tag=source_tag,
            generated_by_s=generated_by_s,
            in_scope=in_scope,
        )
        return RescueCandidate(name=name, family=CandidateFamily.repair, payload=payload)

    def boundary(
        name: str,
        source: int,
        target: int,
        spend: Fraction,
        budget: Fraction,
    ) -> RescueCandidate:
        move_record = moves[name]
        readout = _readout(name, move_record, 2, 0, spend, budget)
        payload = BoundaryUpdateCandidate(
            name=name,
            move_record=move_record,
            pre_source=source,
            post_target=target,
            update_record=f"boundary_update:{name}",
            budget=_budget(move_record, spend, budget),
            descent=_descent(move_record, readout),
        )
        return RescueCandidate(name=name, family=CandidateFamily.boundary, payload=payload)

    def acquisition(
        name: str,
        spend: Fraction,
        budget: Fraction,
        *,
        overbudget_probe: bool = False,
    ) -> RescueCandidate:
        move_record = moves[name]
        active = ActiveFamily(("probe_base",), {"probe_base": F(1)}, "L_base")
        probe = "probe_overbudget" if overbudget_probe else "probe_stabilizer"
        new_active = ActiveFamily(
            ("probe_base", probe),
            {"probe_base": F(1), probe: F(1, 4)},
            "L_stabilized",
        )
        evidence = AcquisitionLedgerEvidence(
            cost_entry=AmountEntryWitness("cost:probe_stabilizer", F(1, 4)),
            budget_entry=AmountEntryWitness("budget:1", F(1)),
            spend_entry=AmountEntryWitness("spend:1/4", F(1, 4)),
        )
        readout = _readout(name, move_record, 2, 0, spend, budget)
        payload = AcquisitionRescueCandidate(
            name=name,
            move_record=move_record,
            active_family=active,
            new_active_family=new_active,
            probe=probe,
            pre_classification=ActiveFamilyClassification(0, FineSourceTag.committed_state, True, True),
            post_classification=ActiveFamilyClassification(1, FineSourceTag.committed_state, True, True),
            ledger_evidence=evidence,
            budget=_budget(move_record, spend, budget),
            descent=_descent(move_record, readout),
        )
        return RescueCandidate(name=name, family=CandidateFamily.acquisition, payload=payload)

    app_t = _apparatus("app_revive_pre", 10, "app:revive:pre", boundary=5, audit_data=4)
    app_tplus1 = _apparatus("app_revive_post", 11, "app:revive:post", boundary=6, audit_data=4)
    operator = ClosureMaintenanceOperator(
        name="operator_revival",
        operator_record="operator:revival",
        outputs={10: app_tplus1},
        operator_ledger_entries=("budget:1",),
        operator_audit_records=("reclosure_audit",),
    )
    reinstatement = MaintenanceReinstatementRecord(
        name="reinstatement:revival",
        time=10,
        source_state=10,
        target_state=11,
        operator_record=operator.operator_record,
        pre_app_record=app_t.apparatus_record,
        post_app_record=app_tplus1.apparatus_record,
        output_record=app_tplus1.apparatus_record,
        reinstatement_ledger_entry="budget:1",
    )
    reclosure_move = moves["mv_reclosure_revived"]
    reclosure_payload = ApparatusReclosureCandidate(
        name="mv_reclosure_revived",
        move_record=reclosure_move,
        t=10,
        app_t=app_t,
        app_tplus1=app_tplus1,
        operator=operator,
        record=reinstatement,
        budget=_budget(reclosure_move, F(1, 2), F(1)),
        descent=_descent(reclosure_move, _readout("mv_reclosure_revived", reclosure_move, 2, 0, F(1, 2), F(1))),
    )
    viable_app_t = _apparatus(
        "app_viable_reclosure_pre",
        5,
        "app:viable_reclosure:pre",
        boundary=7,
        audit_data=4,
    )
    viable_app_tplus1 = _apparatus(
        "app_viable_reclosure_post",
        6,
        "app:viable_reclosure:post",
        boundary=8,
        audit_data=4,
    )
    viable_operator = ClosureMaintenanceOperator(
        name="operator_viable_reclosure",
        operator_record="operator:viable_reclosure",
        outputs={5: viable_app_tplus1},
        operator_ledger_entries=("budget:1",),
        operator_audit_records=("reclosure_audit",),
    )
    viable_reinstatement = MaintenanceReinstatementRecord(
        name="reinstatement:viable_reclosure",
        time=5,
        source_state=5,
        target_state=6,
        operator_record=viable_operator.operator_record,
        pre_app_record=viable_app_t.apparatus_record,
        post_app_record=viable_app_tplus1.apparatus_record,
        output_record=viable_app_tplus1.apparatus_record,
        reinstatement_ledger_entry="budget:1",
    )
    viable_reclosure_move = moves["mv_reclosure_viable"]
    viable_reclosure_payload = ApparatusReclosureCandidate(
        name="mv_reclosure_viable",
        move_record=viable_reclosure_move,
        t=5,
        app_t=viable_app_t,
        app_tplus1=viable_app_tplus1,
        operator=viable_operator,
        record=viable_reinstatement,
        budget=_budget(viable_reclosure_move, F(1, 2), F(1)),
        descent=_descent(
            viable_reclosure_move,
            _readout("mv_reclosure_viable", viable_reclosure_move, 2, 0, F(1, 2), F(1)),
        ),
    )

    candidates = {
        "mv_repair_viable": repair("mv_repair_viable", 2, 3, F(1, 4), F(1), 2, 0),
        "mv_repair_stressed": repair("mv_repair_stressed", 4, 5, F(1, 3), F(1), 2, 0),
        "mv_boundary_viable": boundary("mv_boundary_viable", 16, 17, F(1, 5), F(1)),
        "mv_acquisition_viable": acquisition("mv_acquisition_viable", F(1, 4), F(1)),
        "mv_self_sub_no_descent": repair("mv_self_sub_no_descent", 6, 7, F(1, 4), F(1), 1, 1),
        "mv_self_sub_over_budget": repair("mv_self_sub_over_budget", 7, 8, F(3, 2), F(1), 2, 0),
        "mv_recover_no_descent": repair("mv_recover_no_descent", 8, 9, F(1, 4), F(1), 1, 1),
        "mv_recover_over_budget": repair("mv_recover_over_budget", 9, 10, F(5, 4), F(1), 2, 0),
        "mv_recover_off_kernel_boundary": boundary("mv_recover_off_kernel_boundary", 8, 10, F(1, 4), F(1)),
        "mv_irrev_no_descent": repair("mv_irrev_no_descent", 11, 12, F(1, 4), F(1), 1, 1),
        "mv_irrev_over_budget_acquisition": acquisition(
            "mv_irrev_over_budget_acquisition",
            F(3, 2),
            F(1),
            overbudget_probe=True,
        ),
        "mv_reclosure_revived": RescueCandidate(
            name="mv_reclosure_revived",
            family=CandidateFamily.reclosure,
            payload=reclosure_payload,
        ),
        "mv_reclosure_viable": RescueCandidate(
            name="mv_reclosure_viable",
            family=CandidateFamily.reclosure,
            payload=viable_reclosure_payload,
        ),
        "mv_post_withdrawal_repair": repair("mv_post_withdrawal_repair", 12, 13, F(1, 4), F(1), 2, 0),
        "mv_ctrl_over_budget": repair("mv_ctrl_over_budget", 13, 14, F(3, 2), F(1), 2, 0),
        "mv_ctrl_unlinked_candidate": repair(
            "mv_ctrl_unlinked_candidate",
            14,
            15,
            F(1, 4),
            F(1),
            2,
            0,
            descent_for_move=moves["mv_ctrl_unlinked_named"],
            readout_move=moves["mv_ctrl_unlinked_named"],
        ),
        "mv_ctrl_fallback": repair(
            "mv_ctrl_fallback",
            15,
            16,
            F(1, 4),
            F(1),
            2,
            0,
            source_tag=FineSourceTag.fallback,
            generated_by_s=False,
            in_scope=False,
        ),
    }
    return candidates


def _status_record(
    name: str,
    status: ReclosureCollapseStatus,
    *,
    rescue_move_record: CollapseMoveRecord | None = None,
    residual_record: str | None = None,
    subsidy_record: str | None = None,
    suspension_record: str | None = None,
    prior_status_record: str | None = None,
    lineage_record: str | None = None,
    reachability_record: str | None = None,
    kernel_record: str | None = None,
    horizon: str = H0,
) -> ReclosureCollapseStatusRecord:
    return ReclosureCollapseStatusRecord(
        name=f"status:{name}",
        challenge_class=CHALLENGE,
        horizon=horizon,
        status=status,
        residual_record=residual_record,
        rescue_move_record=rescue_move_record,
        subsidy_record=subsidy_record,
        suspension_record=suspension_record,
        prior_status_record=prior_status_record,
        lineage_record=lineage_record,
        reachability_record=reachability_record,
        kernel_record=kernel_record,
        supporting_ledger_entries=("budget:1",),
        supporting_audit_records=("status_audit",),
    )


def build_fixture() -> Fixture:
    probe_trajectory = DeclaredTrajectory(
        legitimate_start=lambda _tau, n_start: n_start == 0,
        supp_k=lambda z, z_next: z_next == z + 1,
        tau=lambda n: n,
        step_in_scope=lambda _n: True,
        n_start=0,
    )
    moves = {
        "mv_repair_viable": _move("mv_repair_viable", 101, CollapseMoveKind.repair),
        "mv_repair_stressed": _move("mv_repair_stressed", 102, CollapseMoveKind.repair),
        "mv_boundary_viable": _move("mv_boundary_viable", 103, CollapseMoveKind.boundary_update),
        "mv_acquisition_viable": _move("mv_acquisition_viable", 104, CollapseMoveKind.acquisition),
        "mv_reclosure_viable": _move("mv_reclosure_viable", 105, CollapseMoveKind.apparatus_reclosure),
        "mv_self_sub_no_descent": _move("mv_self_sub_no_descent", 201, CollapseMoveKind.repair),
        "mv_self_sub_over_budget": _move("mv_self_sub_over_budget", 202, CollapseMoveKind.repair),
        "mv_external_subsidy": _move("mv_external_subsidy", 901, CollapseMoveKind.repair),
        "mv_suspended_probe": _move("mv_suspended_probe", 203, CollapseMoveKind.repair),
        "mv_recover_no_descent": _move("mv_recover_no_descent", 301, CollapseMoveKind.repair),
        "mv_recover_over_budget": _move("mv_recover_over_budget", 302, CollapseMoveKind.repair),
        "mv_recover_off_kernel_boundary": _move("mv_recover_off_kernel_boundary", 303, CollapseMoveKind.boundary_update),
        "mv_irrev_no_descent": _move("mv_irrev_no_descent", 401, CollapseMoveKind.repair),
        "mv_irrev_over_budget_acquisition": _move("mv_irrev_over_budget_acquisition", 402, CollapseMoveKind.acquisition),
        "mv_reclosure_revived": _move("mv_reclosure_revived", 501, CollapseMoveKind.apparatus_reclosure),
        "mv_post_withdrawal_repair": _move("mv_post_withdrawal_repair", 601, CollapseMoveKind.repair),
        "mv_ctrl_over_budget": _move("mv_ctrl_over_budget", 801, CollapseMoveKind.repair),
        "mv_ctrl_unlinked_candidate": _move("mv_ctrl_unlinked_candidate", 802, CollapseMoveKind.repair),
        "mv_ctrl_unlinked_named": _move("mv_ctrl_unlinked_named", 803, CollapseMoveKind.repair),
        "mv_ctrl_fallback": _move("mv_ctrl_fallback", 805, CollapseMoveKind.repair),
    }
    ledger_entries = frozenset(
        {
            "budget:1",
            "budget:1/2",
            "budget:1/4",
            "spend:1/5",
            "spend:1/4",
            "spend:1/3",
            "spend:1/2",
            "spend:3/2",
            "spend:5/4",
            "cost:probe_stabilizer",
        }
    )
    audit_records = frozenset(
        {
            "repair_audit",
            "boundary_audit",
            "reclosure_audit",
            "acquisition_audit",
            "status_audit",
            "subsidy_audit",
            "suspension_audit",
            "lineage_audit",
        }
    )
    candidates = _build_candidates(moves, ledger_entries)
    external_readout = _readout("mv_external_subsidy", moves["mv_external_subsidy"], 2, 0, F(1, 2), F(1))
    subsidies = {
        "subsidy_ext_1": ExternalSubsidyWitness(
            name="subsidy_ext_1",
            subsidy_record="subsidy_ext_1",
            challenge_class=CHALLENGE,
            horizon=H0,
            supplied_move=SubsidizerRescueCandidate(
                subsidizer="S_ext",
                move_record=moves["mv_external_subsidy"],
                spend=F(1, 2),
                budget=F(1),
                readout=external_readout,
            ),
        )
    }
    residuals = {
        "residual_stressed": StatusedResidualAccrual(
            "residual_stressed",
            CHALLENGE,
            H0,
            F(1, 5),
            F(1, 2),
            "residual_stressed",
        ),
        "residual_wrong_scope": StatusedResidualAccrual(
            "residual_wrong_scope",
            OTHER_CHALLENGE,
            H0,
            F(1, 5),
            F(1, 2),
            "residual_wrong_scope",
        ),
    }
    app_baseline = _apparatus("app_suspend_baseline", 3, "app:suspend:baseline")
    app_current = _apparatus("app_suspend_current", 3, "app:suspend:current")
    suspensions = {
        "suspension_ops_gate": SuspensionWitness(
            name="suspension_ops_gate",
            suspension_record="suspension_ops_gate",
            challenge_class=CHALLENGE,
            horizon=H0,
            baseline_apparatus=app_baseline,
            current_apparatus=app_current,
        )
    }
    reachability = {
        "reach_recover": ReachabilityCertified("reach_recover", CHALLENGE, H0, False, True, False),
        "reach_irrev": ReachabilityCertified("reach_irrev", CHALLENGE, H0, True, False, False),
        "reach_inconsistent": ReachabilityCertified("reach_inconsistent", CHALLENGE, H0, True, False, False),
    }
    kernels = {
        "kernel_recover": KernelCertified("kernel_recover", CHALLENGE, H0, False, True),
        "kernel_irrev": KernelCertified("kernel_irrev", CHALLENGE, H0, True, False),
        "kernel_nonempty_bad": KernelCertified("kernel_nonempty_bad", CHALLENGE, H0, False, True),
    }
    revivals = {
        "revival_new_lineage": RevivalWitness(
            name="revival_new_lineage",
            prior_status_ref="prior_subsidized_or_collapsed_1",
            old_lineage="lineage_subsidized_v1",
            new_lineage="lineage_reclosed_v2",
            reclosure_candidate="mv_reclosure_revived",
        )
    }
    withdrawals = {
        "withdraw_subsidy_ext_1": SubsidyWithdrawalEvent(
            name="withdraw_subsidy_ext_1",
            prior_subsidy_record="subsidy_ext_1",
        )
    }
    status_records = {
        "scn_viable_self_repair": _status_record(
            "viable_self_repair",
            ReclosureCollapseStatus.viable,
            rescue_move_record=moves["mv_repair_viable"],
        ),
        "scn_stressed_self_repair": _status_record(
            "stressed_self_repair",
            ReclosureCollapseStatus.stressed,
            rescue_move_record=moves["mv_repair_stressed"],
            residual_record="residual_stressed",
        ),
        "scn_viable_boundary_update": _status_record(
            "viable_boundary_update",
            ReclosureCollapseStatus.viable,
            rescue_move_record=moves["mv_boundary_viable"],
        ),
        "scn_viable_acquisition": _status_record(
            "viable_acquisition",
            ReclosureCollapseStatus.viable,
            rescue_move_record=moves["mv_acquisition_viable"],
        ),
        "scn_viable_apparatus_reclosure": _status_record(
            "viable_apparatus_reclosure",
            ReclosureCollapseStatus.viable,
            rescue_move_record=moves["mv_reclosure_viable"],
        ),
        "scn_subsidized_external_rescue": _status_record(
            "subsidized_external_rescue",
            ReclosureCollapseStatus.subsidized,
            subsidy_record="subsidy_ext_1",
        ),
        "scn_suspended_gated_operations": _status_record(
            "suspended_gated_operations",
            ReclosureCollapseStatus.suspended,
            suspension_record="suspension_ops_gate",
        ),
        "scn_collapsed_recoverable": _status_record(
            "collapsed_recoverable",
            ReclosureCollapseStatus.collapsed_recoverable,
            reachability_record="reach_recover",
            kernel_record="kernel_recover",
        ),
        "scn_collapsed_irreversible": _status_record(
            "collapsed_irreversible",
            ReclosureCollapseStatus.collapsed_irreversible,
            reachability_record="reach_irrev",
            kernel_record="kernel_irrev",
        ),
        "scn_revived_new_lineage": _status_record(
            "revived_new_lineage",
            ReclosureCollapseStatus.revived,
            rescue_move_record=moves["mv_reclosure_revived"],
            prior_status_record="prior_subsidized_or_collapsed_1",
            lineage_record="lineage_reclosed_v2",
        ),
        "scn_post_withdrawal_reclassified": _status_record(
            "post_withdrawal_reclassified",
            ReclosureCollapseStatus.viable,
            rescue_move_record=moves["mv_post_withdrawal_repair"],
            horizon=H1,
        ),
    }
    scenarios = {
        "scn_viable_self_repair": Scenario(
            "scn_viable_self_repair",
            CHALLENGE,
            H0,
            ("mv_repair_viable",),
            ("mv_repair_viable",),
            "scn_viable_self_repair",
        ),
        "scn_stressed_self_repair": Scenario(
            "scn_stressed_self_repair",
            CHALLENGE,
            H0,
            ("mv_repair_stressed",),
            ("mv_repair_stressed",),
            "scn_stressed_self_repair",
            residual="residual_stressed",
        ),
        "scn_viable_boundary_update": Scenario(
            "scn_viable_boundary_update",
            CHALLENGE,
            H0,
            ("mv_boundary_viable",),
            ("mv_boundary_viable",),
            "scn_viable_boundary_update",
        ),
        "scn_viable_acquisition": Scenario(
            "scn_viable_acquisition",
            CHALLENGE,
            H0,
            ("mv_acquisition_viable",),
            ("mv_acquisition_viable",),
            "scn_viable_acquisition",
        ),
        "scn_viable_apparatus_reclosure": Scenario(
            "scn_viable_apparatus_reclosure",
            CHALLENGE,
            H0,
            ("mv_reclosure_viable",),
            ("mv_reclosure_viable",),
            "scn_viable_apparatus_reclosure",
        ),
        "scn_subsidized_external_rescue": Scenario(
            "scn_subsidized_external_rescue",
            CHALLENGE,
            H0,
            ("mv_self_sub_no_descent", "mv_self_sub_over_budget"),
            ("mv_self_sub_no_descent", "mv_self_sub_over_budget"),
            "scn_subsidized_external_rescue",
            subsidy="subsidy_ext_1",
        ),
        "scn_suspended_gated_operations": Scenario(
            "scn_suspended_gated_operations",
            CHALLENGE,
            H0,
            (),
            (),
            "scn_suspended_gated_operations",
            suspension="suspension_ops_gate",
        ),
        "scn_collapsed_recoverable": Scenario(
            "scn_collapsed_recoverable",
            CHALLENGE,
            H0,
            ("mv_recover_no_descent", "mv_recover_over_budget"),
            ("mv_recover_no_descent", "mv_recover_over_budget"),
            "scn_collapsed_recoverable",
            reachability="reach_recover",
            kernel="kernel_recover",
            ordinary_activity=(OrdinaryActivity(3, "ordinary_tick", 0, 1),),
        ),
        "scn_collapsed_irreversible": Scenario(
            "scn_collapsed_irreversible",
            CHALLENGE,
            H0,
            ("mv_irrev_no_descent", "mv_irrev_over_budget_acquisition"),
            ("mv_irrev_no_descent", "mv_irrev_over_budget_acquisition"),
            "scn_collapsed_irreversible",
            reachability="reach_irrev",
            kernel="kernel_irrev",
        ),
        "scn_revived_new_lineage": Scenario(
            "scn_revived_new_lineage",
            CHALLENGE,
            H0,
            ("mv_reclosure_revived",),
            ("mv_reclosure_revived",),
            "scn_revived_new_lineage",
            revival="revival_new_lineage",
        ),
        "scn_post_withdrawal_reclassified": Scenario(
            "scn_post_withdrawal_reclassified",
            CHALLENGE,
            H1,
            ("mv_post_withdrawal_repair",),
            ("mv_post_withdrawal_repair",),
            "scn_post_withdrawal_reclassified",
        ),
        "ctrl_incomplete_inventory_attempt": Scenario(
            "ctrl_incomplete_inventory_attempt",
            CHALLENGE,
            H0,
            (),
            ("mv_repair_viable",),
            "scn_collapsed_recoverable",
        ),
    }
    return Fixture(
        kernel=ring_kernel(N_STATES),
        ledger=_carried_ledger(ledger_entries, probe_trajectory),
        probe_economy=_probe_economy(ledger_entries, probe_trajectory),
        candidates=candidates,
        scenarios=scenarios,
        status_records=status_records,
        residuals=residuals,
        subsidies=subsidies,
        withdrawals=withdrawals,
        suspensions=suspensions,
        reachability=reachability,
        kernels=kernels,
        revivals=revivals,
        active_subsidies={(CHALLENGE, H0): ("subsidy_ext_1",), (CHALLENGE, H1): ()},
        operation_gates=(
            (3, "self_repair", False),
            (3, "boundary_update", False),
            (3, "apparatus_reclosure", False),
            (3, "acquisition", False),
        ),
        challenge_schedule=(
            (2, CHALLENGE, True),
            (3, CHALLENGE, False),
            (3, "C_background_noise", False),
        ),
        carried_status_records=frozenset(record.name for record in status_records.values()),
        ledger_entries=ledger_entries,
        audit_records=audit_records,
        carried_apparatus_records=frozenset(
            {
                "app:revive:pre",
                "app:revive:post",
                "app:viable_reclosure:pre",
                "app:viable_reclosure:post",
                "app:suspend:baseline",
                "app:suspend:current",
            }
        ),
        carried_gate_instruments=frozenset({"gate_collapse"}),
        carried_operator_records=frozenset({"operator:revival", "operator:viable_reclosure"}),
        instrument_records=frozenset({"theta_stay", "theta_budget"}),
    )


def collapse_budget_feasible(
    fixture: Fixture,
    witness: CollapseBudgetWitness,
    move_record: CollapseMoveRecord,
) -> bool:
    return (
        witness.move_record == move_record
        and witness.budget_entry in fixture.ledger_entries
        and witness.spend_entry in fixture.ledger_entries
        and witness.spend <= witness.budget
    )


def rescue_move_credited_for_descent(
    move_record: CollapseMoveRecord,
    readout: DescentReadoutRecord,
) -> bool:
    return (
        readout.move_record == move_record
        and readout.post_delta < readout.pre_delta
        and readout.budget_margin == readout.budget - readout.spend
    )


def descent_certificate_structurally_linked(cert: RescueDescentCertificate) -> bool:
    readout = cert.descent_readout_record
    return (
        cert.descent_for_move == cert.move_record
        and cert.readout_for_declared_family is True
        and carried_source(readout.source_tag, readout.generated_by_s, readout.in_scope)
    )


def collapse_rescue_descends(candidate: RescueCandidate) -> bool:
    return (
        descent_certificate_structurally_linked(candidate.payload.descent)
        and rescue_move_credited_for_descent(
            candidate.move_record,
            candidate.payload.descent.descent_readout_record,
        )
    )


def repair_rescue_constructible(fixture: Fixture, candidate: RepairRescueCandidate) -> bool:
    return (
        candidate.move_record.kind is CollapseMoveKind.repair
        and carried_source(candidate.source_tag, candidate.generated_by_s, candidate.in_scope)
        and candidate.audit_record in fixture.audit_records
        and _right_supp(candidate.source, candidate.target)
        and descent_certificate_structurally_linked(candidate.descent)
    )


def boundary_update_constructible(fixture: Fixture, candidate: BoundaryUpdateCandidate) -> bool:
    return (
        candidate.move_record.kind is CollapseMoveKind.boundary_update
        and carried_source(candidate.source_tag, candidate.generated_by_s, candidate.in_scope)
        and candidate.update_record.startswith("boundary_update:")
        and _right_supp(candidate.pre_source, candidate.post_target)
        and descent_certificate_structurally_linked(candidate.descent)
    )


def _e3_fixture(fixture: Fixture) -> Any:
    return fixture


def apparatus_reclosure_constructible(fixture: Fixture, candidate: ApparatusReclosureCandidate) -> bool:
    return (
        candidate.move_record.kind is CollapseMoveKind.apparatus_reclosure
        and maintenance_reinstatement_for(
            _e3_fixture(fixture),
            candidate.t,
            candidate.app_t,
            candidate.app_tplus1,
            candidate.operator,
            candidate.record,
        )
        and descent_certificate_structurally_linked(candidate.descent)
    )


def candidate_acquisition(fixture: Fixture, candidate: AcquisitionRescueCandidate) -> bool:
    move = ProbeMove(
        kind=ProbeMoveKind.acquisition,
        active_family=candidate.active_family,
        new_active_family=candidate.new_active_family,
        probe=candidate.probe,
    )
    lawful = lawful_acquisition(
        fixture.probe_economy,
        fixture.ledger,
        candidate.active_family,
        candidate.probe,
        candidate.new_active_family,
        candidate.pre_classification,
        candidate.post_classification,
        candidate.ledger_evidence,
        strict=acquisition_strict(
            fixture.probe_economy.same_family_saturated,
            candidate.active_family,
            candidate.probe,
        ),
    )
    return (
        candidate.move_record.kind is CollapseMoveKind.acquisition
        and lawful
        and fixture.probe_economy.catalog.contains(candidate.probe)
        and candidate.risk_admissible is True
        and fixture.probe_economy.budget_admissible(move)
        and collapse_budget_feasible(fixture, candidate.budget, candidate.move_record)
    )


def acquisition_rescue_constructible(
    fixture: Fixture,
    candidate: AcquisitionRescueCandidate,
) -> bool:
    return (
        candidate.move_record.kind is CollapseMoveKind.acquisition
        and candidate.risk_admissible is True
        and candidate.probe in {"probe_stabilizer", "probe_overbudget"}
        and descent_certificate_structurally_linked(candidate.descent)
    )


def rescue_candidate_constructible(fixture: Fixture, candidate: RescueCandidate) -> bool:
    if candidate.family is CandidateFamily.repair:
        return repair_rescue_constructible(fixture, candidate.payload)  # type: ignore[arg-type]
    if candidate.family is CandidateFamily.boundary:
        return boundary_update_constructible(fixture, candidate.payload)  # type: ignore[arg-type]
    if candidate.family is CandidateFamily.reclosure:
        return apparatus_reclosure_constructible(fixture, candidate.payload)  # type: ignore[arg-type]
    if candidate.family is CandidateFamily.acquisition:
        return acquisition_rescue_constructible(fixture, candidate.payload)  # type: ignore[arg-type]
    return False


def collapse_rescue_admissible_in_budget(fixture: Fixture, candidate: RescueCandidate) -> bool:
    if not rescue_candidate_constructible(fixture, candidate):
        return False
    if candidate.family is CandidateFamily.acquisition:
        return candidate_acquisition(fixture, candidate.payload)  # type: ignore[arg-type]
    return collapse_budget_feasible(fixture, candidate.payload.budget, candidate.move_record)


def constructible_self_candidates(fixture: Fixture, scenario: Scenario) -> tuple[str, ...]:
    return tuple(
        name
        for name in scenario.constructible_universe
        if name in fixture.candidates and rescue_candidate_constructible(fixture, fixture.candidates[name])
    )


def complete_collapse_rescue_inventory(fixture: Fixture, scenario: Scenario) -> bool:
    return set(constructible_self_candidates(fixture, scenario)) == set(scenario.declared_candidates)


def collapse_falsifier(fixture: Fixture, scenario: Scenario) -> bool:
    if not complete_collapse_rescue_inventory(fixture, scenario):
        return False
    return any(
        name in fixture.candidates
        and rescue_candidate_constructible(fixture, fixture.candidates[name])
        and collapse_rescue_admissible_in_budget(fixture, fixture.candidates[name])
        and collapse_rescue_descends(fixture.candidates[name])
        for name in scenario.declared_candidates
    )


def collapsed_core(fixture: Fixture, scenario: Scenario) -> bool:
    return complete_collapse_rescue_inventory(fixture, scenario) and not collapse_falsifier(
        fixture,
        scenario,
    )


def statused_residual_accrual(
    fixture: Fixture,
    challenge_class: str,
    horizon: str,
) -> tuple[StatusedResidualAccrual, ...]:
    return tuple(
        residual
        for residual in fixture.residuals.values()
        if residual.challenge_class == challenge_class
        and residual.horizon == horizon
        and residual.residual_spend <= residual.residual_budget
        and carried_source(residual.source_tag, residual.generated_by_s, residual.in_scope)
    )


def scenario_statused_residuals(
    fixture: Fixture,
    scenario: Scenario,
) -> tuple[StatusedResidualAccrual, ...]:
    if scenario.residual is None:
        return ()
    residual = fixture.residuals[scenario.residual]
    return tuple(
        candidate
        for candidate in (residual,)
        if candidate.challenge_class == scenario.challenge_class
        and candidate.horizon == scenario.horizon
        and candidate.residual_spend <= candidate.residual_budget
        and carried_source(candidate.source_tag, candidate.generated_by_s, candidate.in_scope)
    )


def irreversibility_coherence(
    reach: ReachabilityCertified,
    kernel: KernelCertified,
    challenge_class: str,
    horizon: str,
) -> bool:
    return (
        reach.challenge_class == challenge_class
        and reach.horizon == horizon
        and kernel.challenge_class == challenge_class
        and kernel.horizon == horizon
        and reach.challenge_class == kernel.challenge_class
        and reach.horizon == kernel.horizon
        and reach.unreachable == kernel.kernel_empty
    )


def irreversible_collapse_input(
    reach: ReachabilityCertified,
    kernel: KernelCertified,
    challenge_class: str,
    horizon: str,
) -> bool:
    return (
        irreversibility_coherence(reach, kernel, challenge_class, horizon)
        and reach.unreachable
        and kernel.kernel_empty
    )


def recoverable_collapse_input(
    reach: ReachabilityCertified,
    kernel: KernelCertified,
    challenge_class: str,
    horizon: str,
) -> bool:
    return (
        irreversibility_coherence(reach, kernel, challenge_class, horizon)
        and (
            reach.self_reachable
            or reach.externally_reachable_only
            or kernel.kernel_nonempty
        )
        and not irreversible_collapse_input(reach, kernel, challenge_class, horizon)
    )


def subsidizer_budget_feasible(witness: ExternalSubsidyWitness) -> bool:
    move = witness.supplied_move
    return move.spend <= move.budget


def subsidizer_move_descends(witness: ExternalSubsidyWitness) -> bool:
    return rescue_move_credited_for_descent(
        witness.supplied_move.move_record,
        witness.supplied_move.readout,
    )


def not_self_carried(fixture: Fixture, scenario: Scenario, witness: ExternalSubsidyWitness) -> bool:
    return all(
        fixture.candidates[name].move_record != witness.supplied_move.move_record
        for name in constructible_self_candidates(fixture, scenario)
    )


def external_subsidy_witness(
    fixture: Fixture,
    scenario: Scenario,
    witness: ExternalSubsidyWitness,
) -> bool:
    return (
        witness.challenge_class == scenario.challenge_class
        and witness.horizon == scenario.horizon
        and carried_source(witness.source_tag, witness.generated_by_s, witness.in_scope)
        and witness.name in fixture.active_subsidies.get((scenario.challenge_class, scenario.horizon), ())
        and subsidizer_budget_feasible(witness)
        and subsidizer_move_descends(witness)
        and not_self_carried(fixture, scenario, witness)
    )


def active_external_subsidy_at(fixture: Fixture, challenge_class: str, horizon: str) -> bool:
    return any(
        external_subsidy_witness(fixture, fixture.scenarios["scn_subsidized_external_rescue"], fixture.subsidies[name])
        for name in fixture.active_subsidies.get((challenge_class, horizon), ())
    )


def no_active_external_subsidy_at(fixture: Fixture, challenge_class: str, horizon: str) -> bool:
    return not fixture.active_subsidies.get((challenge_class, horizon), ())


def operations_gated_off(fixture: Fixture, horizon: str) -> bool:
    time = HORIZON_TIME[horizon]
    rows = [entry for entry in fixture.operation_gates if entry[0] == time]
    return bool(rows) and all(enabled is False for _time, _operation, enabled in rows)


def apparatus_intact(fixture: Fixture, witness: SuspensionWitness) -> bool:
    del fixture
    return apparatus_distance(witness.current_apparatus, witness.baseline_apparatus) == F(0, 8)


def binding_operational_challenge_active(
    fixture: Fixture,
    challenge_class: str,
    horizon: str,
) -> bool:
    time = HORIZON_TIME[horizon]
    return any(
        row_time == time and challenge == challenge_class and binding is True
        for row_time, challenge, binding in fixture.challenge_schedule
    )


def suspension_witness(fixture: Fixture, scenario: Scenario, witness: SuspensionWitness) -> bool:
    return (
        witness.challenge_class == scenario.challenge_class
        and witness.horizon == scenario.horizon
        and carried_source(witness.source_tag, witness.generated_by_s, witness.in_scope)
        and apparatus_intact(fixture, witness)
        and operations_gated_off(fixture, scenario.horizon)
        and not binding_operational_challenge_active(fixture, scenario.challenge_class, scenario.horizon)
    )


def prior_status_is_subsidized_or_collapsed(ref: str) -> bool:
    return ref == "prior_subsidized_or_collapsed_1"


def revival_witness(fixture: Fixture, scenario: Scenario, witness: RevivalWitness) -> bool:
    candidate = fixture.candidates[witness.reclosure_candidate]
    return (
        carried_source(witness.source_tag, witness.generated_by_s, witness.in_scope)
        and prior_status_is_subsidized_or_collapsed(witness.prior_status_ref)
        and witness.old_lineage != witness.new_lineage
        and rescue_candidate_constructible(fixture, candidate)
        and collapse_rescue_admissible_in_budget(fixture, candidate)
        and collapse_rescue_descends(candidate)
    )


def status_occurrence_for(
    fixture: Fixture,
    scenario: Scenario,
    record: ReclosureCollapseStatusRecord,
) -> bool:
    return (
        record.challenge_class == scenario.challenge_class
        and record.horizon == scenario.horizon
        and record.name in fixture.carried_status_records
        and carried_source(record.source_tag, record.generated_by_s, record.in_scope)
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def revived_case(fixture: Fixture, scenario: Scenario, record: ReclosureCollapseStatusRecord) -> bool:
    if scenario.revival is None:
        return False
    witness = fixture.revivals[scenario.revival]
    candidate = fixture.candidates[witness.reclosure_candidate]
    return (
        status_occurrence_for(fixture, scenario, record)
        and revival_witness(fixture, scenario, witness)
        and record.status is ReclosureCollapseStatus.revived
        and record.prior_status_record == witness.prior_status_ref
        and record.lineage_record == witness.new_lineage
        and record.rescue_move_record == candidate.move_record
    )


def subsidized_case(fixture: Fixture, scenario: Scenario, record: ReclosureCollapseStatusRecord) -> bool:
    if revived_case(fixture, scenario, record) or scenario.subsidy is None:
        return False
    witness = fixture.subsidies[scenario.subsidy]
    no_self_falsifier = not any(
        name in fixture.candidates
        and rescue_candidate_constructible(fixture, fixture.candidates[name])
        and collapse_rescue_admissible_in_budget(fixture, fixture.candidates[name])
        and collapse_rescue_descends(fixture.candidates[name])
        for name in scenario.declared_candidates
    )
    return (
        status_occurrence_for(fixture, scenario, record)
        and no_self_falsifier
        and external_subsidy_witness(fixture, scenario, witness)
        and record.status is ReclosureCollapseStatus.subsidized
        and record.subsidy_record == witness.subsidy_record
    )


def suspended_case(fixture: Fixture, scenario: Scenario, record: ReclosureCollapseStatusRecord) -> bool:
    if revived_case(fixture, scenario, record) or subsidized_case(fixture, scenario, record):
        return False
    if scenario.suspension is None:
        return False
    witness = fixture.suspensions[scenario.suspension]
    return (
        status_occurrence_for(fixture, scenario, record)
        and suspension_witness(fixture, scenario, witness)
        and record.status is ReclosureCollapseStatus.suspended
        and record.suspension_record == witness.suspension_record
    )


def viable_case(fixture: Fixture, scenario: Scenario, record: ReclosureCollapseStatusRecord) -> bool:
    if (
        revived_case(fixture, scenario, record)
        or subsidized_case(fixture, scenario, record)
        or suspended_case(fixture, scenario, record)
    ):
        return False
    residuals = scenario_statused_residuals(fixture, scenario)
    if residuals:
        return False
    return (
        status_occurrence_for(fixture, scenario, record)
        and record.status is ReclosureCollapseStatus.viable
        and any(
            name in fixture.candidates
            and record.rescue_move_record == fixture.candidates[name].move_record
            and rescue_candidate_constructible(fixture, fixture.candidates[name])
            and collapse_rescue_admissible_in_budget(fixture, fixture.candidates[name])
            and collapse_rescue_descends(fixture.candidates[name])
            for name in scenario.declared_candidates
        )
    )


def stressed_case(fixture: Fixture, scenario: Scenario, record: ReclosureCollapseStatusRecord) -> bool:
    if (
        revived_case(fixture, scenario, record)
        or subsidized_case(fixture, scenario, record)
        or suspended_case(fixture, scenario, record)
        or viable_case(fixture, scenario, record)
    ):
        return False
    residuals = scenario_statused_residuals(fixture, scenario)
    return (
        status_occurrence_for(fixture, scenario, record)
        and record.status is ReclosureCollapseStatus.stressed
        and any(record.residual_record == residual.residual_record for residual in residuals)
        and any(
            name in fixture.candidates
            and record.rescue_move_record == fixture.candidates[name].move_record
            and rescue_candidate_constructible(fixture, fixture.candidates[name])
            and collapse_rescue_admissible_in_budget(fixture, fixture.candidates[name])
            and collapse_rescue_descends(fixture.candidates[name])
            for name in scenario.declared_candidates
        )
    )


def collapsed_irreversible_case(
    fixture: Fixture,
    scenario: Scenario,
    record: ReclosureCollapseStatusRecord,
) -> bool:
    if (
        revived_case(fixture, scenario, record)
        or subsidized_case(fixture, scenario, record)
        or suspended_case(fixture, scenario, record)
        or viable_case(fixture, scenario, record)
        or stressed_case(fixture, scenario, record)
    ):
        return False
    if scenario.reachability is None or scenario.kernel is None:
        return False
    reach = fixture.reachability[scenario.reachability]
    kernel = fixture.kernels[scenario.kernel]
    return (
        status_occurrence_for(fixture, scenario, record)
        and collapsed_core(fixture, scenario)
        and irreversible_collapse_input(reach, kernel, scenario.challenge_class, scenario.horizon)
        and record.status is ReclosureCollapseStatus.collapsed_irreversible
        and record.reachability_record == reach.name
        and record.kernel_record == kernel.name
        and record.rescue_move_record is None
    )


def collapsed_recoverable_case(
    fixture: Fixture,
    scenario: Scenario,
    record: ReclosureCollapseStatusRecord,
) -> bool:
    if (
        revived_case(fixture, scenario, record)
        or subsidized_case(fixture, scenario, record)
        or suspended_case(fixture, scenario, record)
        or viable_case(fixture, scenario, record)
        or stressed_case(fixture, scenario, record)
        or collapsed_irreversible_case(fixture, scenario, record)
    ):
        return False
    if scenario.reachability is None or scenario.kernel is None:
        return False
    reach = fixture.reachability[scenario.reachability]
    kernel = fixture.kernels[scenario.kernel]
    return (
        status_occurrence_for(fixture, scenario, record)
        and collapsed_core(fixture, scenario)
        and recoverable_collapse_input(reach, kernel, scenario.challenge_class, scenario.horizon)
        and record.status is ReclosureCollapseStatus.collapsed_recoverable
        and record.reachability_record == reach.name
        and record.kernel_record == kernel.name
        and record.rescue_move_record is None
    )


def classify_reclosure_collapse_status(
    fixture: Fixture,
    scenario_name: str,
) -> tuple[ReclosureCollapseStatus, dict[str, bool], ReclosureCollapseStatusRecord | None]:
    scenario = fixture.scenarios[scenario_name]
    record = fixture.status_records.get(scenario.status_record)
    if record is None or not status_occurrence_for(fixture, scenario, record):
        return ReclosureCollapseStatus.unclassified, {}, None
    truths = {
        "revived": revived_case(fixture, scenario, record),
        "subsidized": subsidized_case(fixture, scenario, record),
        "suspended": suspended_case(fixture, scenario, record),
        "viable": viable_case(fixture, scenario, record),
        "stressed": stressed_case(fixture, scenario, record),
        "collapsed_irreversible": collapsed_irreversible_case(fixture, scenario, record),
        "collapsed_recoverable": collapsed_recoverable_case(fixture, scenario, record),
    }
    for status in (
        ReclosureCollapseStatus.revived,
        ReclosureCollapseStatus.subsidized,
        ReclosureCollapseStatus.suspended,
        ReclosureCollapseStatus.viable,
        ReclosureCollapseStatus.stressed,
        ReclosureCollapseStatus.collapsed_irreversible,
        ReclosureCollapseStatus.collapsed_recoverable,
    ):
        if truths[status.value]:
            return status, truths, record
    return ReclosureCollapseStatus.unclassified, truths, record


def no_active_external_subsidy_after_withdrawal(fixture: Fixture) -> bool:
    withdrawal = fixture.withdrawals["withdraw_subsidy_ext_1"]
    return (
        carried_source(withdrawal.source_tag, withdrawal.generated_by_s, withdrawal.in_scope)
        and withdrawal.prior_subsidy_record == "subsidy_ext_1"
        and no_active_external_subsidy_at(fixture, CHALLENGE, H1)
    )


def _scenario_row(fixture: Fixture, scenario_name: str) -> ScenarioRow:
    scenario = fixture.scenarios[scenario_name]
    status, truths, record = classify_reclosure_collapse_status(fixture, scenario_name)
    row_collapsed_core = False if scenario.suspension is not None else collapsed_core(fixture, scenario)
    return ScenarioRow(
        scenario=scenario_name,
        complete_inventory=complete_collapse_rescue_inventory(fixture, scenario),
        collapse_falsifier=collapse_falsifier(fixture, scenario),
        collapsed_core=row_collapsed_core,
        revived=truths.get("revived", False) and status is ReclosureCollapseStatus.revived,
        subsidized=truths.get("subsidized", False) and status is ReclosureCollapseStatus.subsidized,
        suspended=truths.get("suspended", False) and status is ReclosureCollapseStatus.suspended,
        viable=truths.get("viable", False) and status is ReclosureCollapseStatus.viable,
        stressed=truths.get("stressed", False) and status is ReclosureCollapseStatus.stressed,
        collapsed_irreversible=truths.get("collapsed_irreversible", False)
        and status is ReclosureCollapseStatus.collapsed_irreversible,
        collapsed_recoverable=truths.get("collapsed_recoverable", False)
        and status is ReclosureCollapseStatus.collapsed_recoverable,
        status=status.value,
        carried_status_record=record.name if record else None,
    )


def _row_summary(row: ScenarioRow) -> str:
    return (
        f"complete={row.complete_inventory}; falsifier={row.collapse_falsifier}; "
        f"collapsed_core={row.collapsed_core}; status={row.status}"
    )


def _scenario_comparisons(rows: dict[str, ScenarioRow]) -> list[Comparison]:
    expected = {
        "scn_viable_self_repair": ("viable", True, True, False),
        "scn_stressed_self_repair": ("stressed", True, True, False),
        "scn_viable_boundary_update": ("viable", True, True, False),
        "scn_viable_acquisition": ("viable", True, True, False),
        "scn_viable_apparatus_reclosure": ("viable", True, True, False),
        "scn_subsidized_external_rescue": ("subsidized", True, False, True),
        "scn_suspended_gated_operations": ("suspended", True, False, False),
        "scn_collapsed_recoverable": ("collapsed_recoverable", True, False, True),
        "scn_collapsed_irreversible": ("collapsed_irreversible", True, False, True),
        "scn_revived_new_lineage": ("revived", True, True, False),
        "scn_post_withdrawal_reclassified": ("viable", True, True, False),
    }
    comparisons: list[Comparison] = []
    for name, expected_values in expected.items():
        row = rows[name]
        observed_values = (
            row.status,
            row.complete_inventory,
            row.collapse_falsifier,
            row.collapsed_core,
        )
        comparisons.append(
            Comparison(
                name=name,
                passed=observed_values == expected_values
                and sum(
                    (
                        row.revived,
                        row.subsidized,
                        row.suspended,
                        row.viable,
                        row.stressed,
                        row.collapsed_irreversible,
                        row.collapsed_recoverable,
                    )
                )
                == 1,
                observed=_row_summary(row),
                expected=(
                    f"status={expected_values[0]}; complete={expected_values[1]}; "
                    f"falsifier={expected_values[2]}; collapsed_core={expected_values[3]}"
                ),
            )
        )
    return comparisons


def _control_rows(fixture: Fixture) -> tuple[ControlRow, ...]:
    rows: list[ControlRow] = []

    overbudget = fixture.candidates["mv_ctrl_over_budget"]
    overbudget_descends = collapse_rescue_descends(overbudget)
    overbudget_budget = collapse_rescue_admissible_in_budget(fixture, overbudget)
    rows.append(
        ControlRow(
            "ctrl_over_budget_descent",
            overbudget_descends is True and overbudget_budget is False,
            f"descends={overbudget_descends}; admissible_in_budget={overbudget_budget}",
            "descends=True; admissible_in_budget=False",
        )
    )

    unlinked = fixture.candidates["mv_ctrl_unlinked_candidate"]
    unlinked_structural = descent_certificate_structurally_linked(unlinked.payload.descent)
    unlinked_credit = rescue_move_credited_for_descent(
        unlinked.move_record,
        unlinked.payload.descent.descent_readout_record,
    )
    unlinked_constructible = rescue_candidate_constructible(fixture, unlinked)
    rows.append(
        ControlRow(
            "ctrl_unlinked_descent_certificate",
            unlinked_structural is False
            and unlinked_credit is False
            and unlinked_constructible is False,
            (
                f"moveRecordLinked={unlinked_structural}; "
                f"credited={unlinked_credit}; candidate_exists={unlinked_constructible}"
            ),
            "moveRecordLinked=False; credited=False; candidate_exists=False",
        )
    )

    off_kernel = fixture.candidates["mv_recover_off_kernel_boundary"]
    off_payload = off_kernel.payload
    off_supp = _right_supp(off_payload.pre_source, off_payload.post_target)  # type: ignore[attr-defined]
    off_constructible = rescue_candidate_constructible(fixture, off_kernel)
    in_any_inventory = any(
        "mv_recover_off_kernel_boundary" in scenario.declared_candidates
        for scenario in fixture.scenarios.values()
    )
    rows.append(
        ControlRow(
            "ctrl_off_kernel_boundary",
            off_supp is False and off_constructible is False and in_any_inventory is False,
            f"suppK={off_supp}; candidate_exists={off_constructible}; in_inventory={in_any_inventory}",
            "suppK=False; candidate_exists=False; in_inventory=False",
        )
    )

    fallback = fixture.candidates["mv_ctrl_fallback"]
    fallback_payload = fallback.payload
    fallback_carried = carried_source(
        fallback_payload.source_tag,  # type: ignore[attr-defined]
        fallback_payload.generated_by_s,  # type: ignore[attr-defined]
        fallback_payload.in_scope,  # type: ignore[attr-defined]
    )
    fallback_constructible = rescue_candidate_constructible(fixture, fallback)
    rows.append(
        ControlRow(
            "ctrl_fallback_uncarried",
            fallback_carried is False and fallback_constructible is False,
            f"carried={fallback_carried}; candidate_exists={fallback_constructible}",
            "carried=False; candidate_exists=False",
        )
    )

    inconsistent_reach = fixture.reachability["reach_inconsistent"]
    inconsistent_kernel = fixture.kernels["kernel_nonempty_bad"]
    inconsistent_coherence = irreversibility_coherence(
        inconsistent_reach,
        inconsistent_kernel,
        CHALLENGE,
        H0,
    )
    inconsistent_irrev = irreversible_collapse_input(
        inconsistent_reach,
        inconsistent_kernel,
        CHALLENGE,
        H0,
    )
    rows.append(
        ControlRow(
            "ctrl_inconsistent_irreversibility",
            inconsistent_coherence is False and inconsistent_irrev is False,
            f"coherence={inconsistent_coherence}; irreversible={inconsistent_irrev}",
            "coherence=False; irreversible=False",
        )
    )

    wrong_scope_residuals = scenario_statused_residuals(
        fixture,
        fixture.scenarios["scn_viable_self_repair"],
    )
    viable_status = classify_reclosure_collapse_status(fixture, "scn_viable_self_repair")[0]
    rows.append(
        ControlRow(
            "ctrl_wrong_scope_residual",
            all(residual.name != "residual_wrong_scope" for residual in wrong_scope_residuals)
            and viable_status is ReclosureCollapseStatus.viable,
            f"scoped_residuals={[residual.name for residual in wrong_scope_residuals]}; viable_status={viable_status.value}",
            "residual_wrong_scope absent; viable_status=viable",
        )
    )

    incomplete = fixture.scenarios["ctrl_incomplete_inventory_attempt"]
    incomplete_complete = complete_collapse_rescue_inventory(fixture, incomplete)
    incomplete_constructible = constructible_self_candidates(fixture, incomplete)
    rows.append(
        ControlRow(
            "ctrl_incomplete_inventory_attempt",
            incomplete_complete is False and incomplete_constructible == ("mv_repair_viable",),
            f"complete={incomplete_complete}; constructible={incomplete_constructible}",
            "complete=False; constructible=('mv_repair_viable',)",
        )
    )

    active = fixture.scenarios["scn_collapsed_recoverable"].ordinary_activity[0]
    active_supp = _right_supp(active.source, active.target)
    active_rescue = active.rescue_move
    active_status = classify_reclosure_collapse_status(fixture, "scn_collapsed_recoverable")[0]
    active_falsifier = collapse_falsifier(fixture, fixture.scenarios["scn_collapsed_recoverable"])
    rows.append(
        ControlRow(
            "ctrl_active_collapsed_system",
            active_supp is True
            and active_rescue is False
            and active_falsifier is False
            and active_status is ReclosureCollapseStatus.collapsed_recoverable,
            (
                f"suppK={active_supp}; rescue_move={active_rescue}; "
                f"falsifier={active_falsifier}; status={active_status.value}"
            ),
            "suppK=True; rescue_move=False; falsifier=False; status=collapsed_recoverable",
        )
    )

    withdrawal_ok = (
        classify_reclosure_collapse_status(fixture, "scn_subsidized_external_rescue")[0]
        is ReclosureCollapseStatus.subsidized
        and no_active_external_subsidy_after_withdrawal(fixture)
        and not active_external_subsidy_at(fixture, CHALLENGE, H1)
        and classify_reclosure_collapse_status(fixture, "scn_post_withdrawal_reclassified")[0]
        is ReclosureCollapseStatus.viable
    )
    rows.append(
        ControlRow(
            "subsidy_withdrawal_discontinuity",
            withdrawal_ok,
            (
                "before=subsidized; "
                f"no_active_after={no_active_external_subsidy_after_withdrawal(fixture)}; "
                "after=viable"
            ),
            "before=subsidized; no_active_after=True; after=viable",
        )
    )

    return tuple(rows)


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    rows = {row.scenario: row for row in results.scenario_rows}
    comparisons = _scenario_comparisons(rows)
    comparisons.extend(
        Comparison(control.name, control.passed_control, control.observed, control.expected)
        for control in results.controls
    )
    return tuple(comparisons)


def _actual_scope_discipline(fixture: Fixture, rows: tuple[ScenarioRow, ...]) -> bool:
    return all(
        row.carried_status_record in fixture.carried_status_records
        for row in rows
        if row.status != ReclosureCollapseStatus.unclassified.value
    ) and all(
        complete_collapse_rescue_inventory(fixture, fixture.scenarios[row.scenario])
        for row in rows
    )


def _no_hardcoded_status_discipline(rows: tuple[ScenarioRow, ...]) -> bool:
    return all(
        sum(
            (
                row.revived,
                row.subsidized,
                row.suspended,
                row.viable,
                row.stressed,
                row.collapsed_irreversible,
                row.collapsed_recoverable,
            )
        )
        == 1
        for row in rows
    )


def run_e5_reclosure_collapse_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = tuple(_scenario_row(fixture, scenario_name) for scenario_name in REGISTERED_SCENARIOS)
    results = SweepResults(
        scenario_rows=rows,
        controls=_control_rows(fixture),
        actual_scope_discipline=_actual_scope_discipline(fixture, rows),
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(rows),
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E5 Reclosure Collapse Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e5_reclosure_collapse_sweep` "
        "against `formalization/notes/sweeps/E5_reclosure_collapse_predictions.md`.",
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
            "- The 18-state carrier uses Repair-World's `ring_kernel(18)` while the "
            "E5 `suppK` relation is the pre-registered right-successor relation "
            "`z' == (z + 1) % 18`.",
            "- Rescue descent is computed from each candidate's own "
            "`CollapseMoveRecord` and `DescentReadoutRecord`; a global descent "
            "fact is never sufficient.",
            "- The off-kernel and unlinked-descent controls are rejected before "
            "entering any declared candidate inventory.",
            "- Suspension is computed from concrete operation gates, E3 "
            "`apparatus_distance`, and the challenge schedule.",
            "- The subsidy-withdrawal row checks `NoActiveExternalSubsidyAt(h1)` "
            "before recomputing the post-withdrawal status.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_e5_reclosure_collapse_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    total = len(results.comparisons)
    passed = sum(1 for comparison in results.comparisons if comparison.passed)
    print(f"E5 reclosure collapse sweep: {passed}/{total} comparisons PASS")
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    if failures:
        for failure in failures:
            print(f"FAIL {failure.name}: observed {failure.observed}; expected {failure.expected}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
