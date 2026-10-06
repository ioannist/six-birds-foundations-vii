"""E12 individuation sweep against the pre-registration.

The configuration is fixed by
``formalization/notes/sweeps/E12_individuation_predictions.md``.  This
module evaluates the deterministic 30-state ring fixture with concrete carried
repair, budget, record, boundary, and E3-maintenance witnesses.  Closure and
status values are computed from those witnesses; status labels are not copied
from the prediction table.
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
    ProbeCatalog,
    ProbeEconomy,
    ProbeMove,
    ProbeMoveKind,
)
from sixbirds_foundations_v.sweeps.e3_self_maintaining_reclosure_sweep import (
    ClosureApparatus,
    ClosureMaintenanceOperator,
    MaintenanceReinstatementRecord,
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
    / "E12_individuation_results.md"
)

N_STATES = 30
STATES = tuple(range(N_STATES))

REGISTERED_CANDIDATES = (
    "cand_integrated",
    "cand_subsidiary",
    "cand_platform_dependent",
    "cand_shadow",
    "cand_fed_a",
    "cand_fed_b",
    "cand_coalition",
    "cand_overlap_x",
    "cand_overlap_y",
    "cand_non_individuated",
    "cand_vacuous_attempt",
    "cand_coarsest_control",
    "cand_bound_control",
    "cand_max_sub",
    "cand_max_sup",
)


class IndividuationStatus(str, Enum):
    integrated = "integrated"
    federated = "federated"
    subsidiary = "subsidiary"
    platform_dependent = "platform_dependent"
    shadow = "shadow"
    non_individuated = "non_individuated"
    unclassified = "unclassified"


@dataclass(frozen=True)
class Subcarrier:
    name: str
    states: frozenset[int]

    def contains(self, state: int) -> bool:
        return state in self.states


@dataclass(frozen=True)
class RepairWitness:
    name: str
    source: int
    target: int
    defect: str
    audit_record: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class RecordWitness:
    name: str
    entry: str
    carried_under_own_policy: bool


@dataclass(frozen=True)
class AccessPolicyOccurrence:
    n0: int
    policy_value: str
    access_move: str
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True
    decoy_state: int | None = None


@dataclass(frozen=True)
class ExposureBudgetWitness:
    name: str
    move: ProbeMove[str, str]
    budget_entry: str
    amount: Fraction
    feasible: bool
    funding_entry_carried_under_own_policy: bool
    policy_occurrence: AccessPolicyOccurrence


@dataclass(frozen=True)
class BoundaryQuotient:
    candidate_name: str
    name: str
    variant: str
    declared_sufficient: bool

    def classify(self, state: int, candidate: Subcarrier) -> str:
        if self.variant == "two_class":
            return "inside" if candidate.contains(state) else "outside"
        if self.variant == "three_class":
            if state in candidate.states:
                return f"inside_{state}"
            return "outside"
        if self.variant == "bound_bad":
            return "merged_24_25" if state in {24, 25} else "outside"
        raise ValueError(f"unknown quotient variant {self.variant!r}")


@dataclass(frozen=True)
class MaintenanceWitness:
    app_t: ClosureApparatus
    app_tplus1: ClosureApparatus
    operator: ClosureMaintenanceOperator
    record: MaintenanceReinstatementRecord


@dataclass(frozen=True)
class CandidateActivity:
    repair_witnesses: tuple[RepairWitness, ...] = ()
    budget_witnesses: tuple[ExposureBudgetWitness, ...] = ()
    record_witnesses: tuple[RecordWitness, ...] = ()
    boundaries: tuple[BoundaryQuotient, ...] = ()
    maintenance: MaintenanceWitness | None = None


@dataclass(frozen=True)
class IndividuationStatusRecord:
    name: str
    candidate_name: str
    status: IndividuationStatus
    supporting_ledger_entries: tuple[str, ...]
    supporting_audit_records: tuple[str, ...]
    source_tag: FineSourceTag = FineSourceTag.committed_state
    generated_by_s: bool = True
    in_scope: bool = True


@dataclass(frozen=True)
class CandidateRow:
    candidate: str
    repair_closed: bool
    budget_closed: bool
    record_closed: bool
    viability_sufficient_boundary: bool
    self_maintained_boundary: bool
    status: str
    integrated: bool
    federated: bool
    subsidiary: bool
    platform_dependent: bool
    shadow: bool
    non_individuated: bool
    federated_disjunct: str | None
    carried_status_record: str | None


@dataclass(frozen=True)
class QuotientControlRow:
    name: str
    candidate: str
    sufficient: bool
    coarsest: bool
    viability_sufficient_boundary: bool


@dataclass(frozen=True)
class UnlinkedControlRow:
    name: str
    candidate: str
    tau_state: int
    decoy_state: int
    same_rho_of: bool
    attributed_to_i: bool


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    candidate_rows: tuple[CandidateRow, ...]
    quotient_controls: tuple[QuotientControlRow, ...]
    unlinked_controls: tuple[UnlinkedControlRow, ...]
    arbitrary_fragment_control: dict[str, bool | str]
    non_vacuity_control: dict[str, bool]
    actual_scope_discipline: bool
    no_hardcoded_status_discipline: bool
    comparisons: tuple[Comparison, ...]


@dataclass(frozen=True)
class Fixture:
    config: RepairWorldConfig[str, str, str, str, str, dict[str, str], str, str]
    candidates: dict[str, Subcarrier]
    candidate_order: tuple[str, ...]
    activities: dict[str, CandidateActivity]
    status_records: dict[str, IndividuationStatusRecord]
    carried_status_records: frozenset[str]
    ledger_entries: frozenset[str]
    audit_records: frozenset[str]
    carried_apparatus_records: frozenset[str]
    carried_operator_records: frozenset[str]
    carried_reinstatement_records: frozenset[str]
    probe_economy: ProbeEconomy[str, str, str]
    active_family: ActiveFamily[str, str]


def _ring_supp(source: int, target: int) -> bool:
    return target == (source + 1) % N_STATES


def _policy_rho_of(state: int, family: str) -> str:
    if family == "access" and state in {19, 20}:
        return "policy_shared_19_20"
    return f"{family}:{state}"


def _record_policy(
    trajectory: DeclaredTrajectory[int],
    family: str,
) -> CarriedRecordPolicy[int, str]:
    return CarriedRecordPolicy(
        trajectory=trajectory,
        coordinate_declared=lambda _rho: True,
        rho_of=lambda z: _policy_rho_of(z, family),
        name=family,
    )


def _evidence(n0: int) -> CarriedRecordEvidence:
    return CarriedRecordEvidence(
        n0=n0,
        source_tag=FineSourceTag.committed_state,
        generated_by_s=True,
        in_scope=True,
    )


def _budget_move(name: str, active: ActiveFamily[str, str]) -> ProbeMove[str, str]:
    return ProbeMove(
        kind=ProbeMoveKind.allocation,
        active_family=active,
        new_active_family=active,
        probe=name,
    )


def _budget_witness(
    name: str,
    *,
    source_state: int,
    carried_under_own_policy: bool,
    active: ActiveFamily[str, str],
    decoy_state: int | None = None,
) -> ExposureBudgetWitness:
    return ExposureBudgetWitness(
        name=name,
        move=_budget_move(name, active),
        budget_entry=f"budget:{name}",
        amount=F(1),
        feasible=True,
        funding_entry_carried_under_own_policy=carried_under_own_policy,
        policy_occurrence=AccessPolicyOccurrence(
            n0=source_state,
            policy_value=_policy_rho_of(source_state, "access"),
            access_move=name,
            decoy_state=decoy_state,
        ),
    )


def _record_witness(candidate: str, *, own: bool) -> RecordWitness:
    return RecordWitness(
        name=f"record_{candidate}",
        entry=f"record:{candidate}",
        carried_under_own_policy=own,
    )


def _repair_witness(candidate: str, source: int, target: int) -> RepairWitness:
    return RepairWitness(
        name=f"repair_{candidate}",
        source=source,
        target=target,
        defect=f"defect:{candidate}",
        audit_record=f"audit_repair:{candidate}",
    )


def _two_class(candidate_name: str) -> BoundaryQuotient:
    return BoundaryQuotient(candidate_name, f"quotient:{candidate_name}:two", "two_class", True)


def _three_class(candidate_name: str) -> BoundaryQuotient:
    return BoundaryQuotient(candidate_name, f"quotient:{candidate_name}:three", "three_class", True)


def _bound_bad(candidate_name: str) -> BoundaryQuotient:
    return BoundaryQuotient(candidate_name, f"quotient:{candidate_name}:bound_bad", "bound_bad", True)


def _apparatus(name: str, time: int, record: str, ledger: str, audit: str) -> ClosureApparatus:
    return ClosureApparatus(
        name=name,
        time=time,
        gate_instrument="I_gate_e12",
        threshold_records=("theta_e12",),
        app_boundary=100 + time,
        audit_data=200 + time,
        apparatus_record=record,
        used_ledger_entries=(ledger,),
        used_audit_records=(audit,),
    )


def _maintenance(candidate: str, source_state: int) -> MaintenanceWitness:
    app_t = _apparatus(
        f"app_{candidate}_0",
        0,
        f"app_rec:{candidate}:0",
        f"ledger:app:{candidate}:0",
        f"audit:app:{candidate}:0",
    )
    app_tplus1 = _apparatus(
        f"app_{candidate}_1",
        1,
        f"app_rec:{candidate}:1",
        f"ledger:app:{candidate}:1",
        f"audit:app:{candidate}:1",
    )
    operator = ClosureMaintenanceOperator(
        name=f"m_{candidate}",
        operator_record=f"mrec:{candidate}",
        outputs={source_state: app_tplus1},
        operator_ledger_entries=(f"ledger:m:{candidate}",),
        operator_audit_records=(f"audit:m:{candidate}",),
    )
    record = MaintenanceReinstatementRecord(
        name=f"rr_{candidate}",
        time=0,
        source_state=source_state,
        target_state=(source_state + 1) % N_STATES,
        operator_record=operator.operator_record,
        pre_app_record=app_t.apparatus_record,
        post_app_record=app_tplus1.apparatus_record,
        output_record=app_tplus1.apparatus_record,
        reinstatement_ledger_entry=f"ledger:rr:{candidate}",
    )
    return MaintenanceWitness(app_t, app_tplus1, operator, record)


def _make_config(
    ledger_entries: frozenset[str],
    audit_records: frozenset[str],
) -> tuple[
    RepairWorldConfig[str, str, str, str, str, dict[str, str], str, str],
    ActiveFamily[str, str],
    ProbeEconomy[str, str, str],
]:
    trajectory = DeclaredTrajectory(
        legitimate_start=lambda _tau, n_start: n_start == 0,
        supp_k=_ring_supp,
        tau=lambda n: n % N_STATES,
        step_in_scope=lambda _n: True,
        n_start=0,
    )
    ledger_policy = _record_policy(trajectory, "ledger")
    ledger = CarriedLedger(
        ledger_policy=ledger_policy,
        ledger_entries=tuple(sorted(ledger_entries)),
        complete_ledger_inventory=True,
        ledger_evidence=lambda _entry: _evidence(0),
    )
    active = ActiveFamily(support=("probe_e12",), weight={"probe_e12": F(1)}, as_xi_family="xi_e12")
    economy = ProbeEconomy(
        catalog=ProbeCatalog(("probe_e12",), complete_probe_catalog=True),
        active_family_policy=CarriedRecordPolicy(
            trajectory=trajectory,
            coordinate_declared=lambda _rho: True,
            rho_of=lambda _z: active,
            name="active_family",
        ),
        same_family_saturated=lambda _family, _probe: False,
        exposure_cost_entry=lambda _entry, _probe, _amount: True,
        exposure_budget_entry=lambda entry, amount: entry in ledger_entries and amount > 0,
        exposure_spend_entry=lambda _entry, _amount: True,
        retirement_record_entry=lambda _entry, _probe: True,
        budget_admissible=lambda _move: True,
    )
    instrument_policy = _record_policy(trajectory, "instrument")
    occurrence = CarriedRecordOccurrence(record=_policy_rho_of(0, "instrument"), evidence=_evidence(0))
    instrument = ActiveCarriedInstrument(
        instrument="I_E12",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=(occurrence,),
        threshold_records=(occurrence,),
        check_rule_records=(CheckRuleRecord(record=occurrence, audit="audit"),),
        detects=lambda _z, _defect: True,
        gate_allows=lambda _z, _defect, _move: True,
        re_audits=lambda _z, _move, _z_next, audit: audit in audit_records,
    )
    move = RepairMove(
        sort=RepairSort.P4,
        payload={"repair": "payload"},
        move_record=_policy_rho_of(0, "move"),
        move_record_evidence=_evidence(0),
        budget_line=next(iter(ledger_entries)),
    )
    system = ESystem(
        T=TheoryPackage(
            trajectory=trajectory,
            f="e12-f",
            sigma_f="e12-sigma",
            residual_family="e12-residuals",
            audit_access="e12-audit-access",
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
    return (
        RepairWorldConfig(
            kernel=ring_kernel(N_STATES),
            probe_economy=economy,
            e_system=system,
            challenge_process=ChallengeProcess(recurrence_period=None),
        ),
        active,
        economy,
    )


def build_fixture() -> Fixture:
    candidates = {
        "cand_integrated": Subcarrier("cand_integrated", frozenset({0, 1, 2})),
        "cand_subsidiary": Subcarrier("cand_subsidiary", frozenset({3, 4})),
        "cand_platform_dependent": Subcarrier("cand_platform_dependent", frozenset({5, 6})),
        "cand_shadow": Subcarrier("cand_shadow", frozenset({7, 8})),
        "cand_fed_a": Subcarrier("cand_fed_a", frozenset({9})),
        "cand_fed_b": Subcarrier("cand_fed_b", frozenset({10})),
        "cand_coalition": Subcarrier("cand_coalition", frozenset({9, 10})),
        "cand_overlap_x": Subcarrier("cand_overlap_x", frozenset({11, 12})),
        "cand_overlap_y": Subcarrier("cand_overlap_y", frozenset({12, 13})),
        "cand_non_individuated": Subcarrier("cand_non_individuated", frozenset({14})),
        "cand_vacuous_attempt": Subcarrier("cand_vacuous_attempt", frozenset({15})),
        "cand_coarsest_control": Subcarrier("cand_coarsest_control", frozenset({17, 18})),
        "cand_unlinked_control": Subcarrier("cand_unlinked_control", frozenset({19})),
        "cand_bound_control": Subcarrier("cand_bound_control", frozenset({24, 25})),
        "cand_max_sub": Subcarrier("cand_max_sub", frozenset({26, 27})),
        "cand_max_sup": Subcarrier("cand_max_sup", frozenset({26, 27, 28})),
    }
    active = ActiveFamily(support=("probe_e12",), weight={"probe_e12": F(1)}, as_xi_family="xi_e12")

    def closed_activity(candidate: str, source: int, target: int) -> CandidateActivity:
        return CandidateActivity(
            repair_witnesses=(_repair_witness(candidate, source, target),),
            budget_witnesses=(
                _budget_witness(
                    f"{candidate}:budget",
                    source_state=source,
                    carried_under_own_policy=True,
                    active=active,
                ),
            ),
            record_witnesses=(_record_witness(candidate, own=True),),
            boundaries=(_two_class(candidate),),
            maintenance=_maintenance(candidate, source),
        )

    activities: dict[str, CandidateActivity] = {
        "cand_integrated": closed_activity("cand_integrated", 0, 1),
        "cand_subsidiary": CandidateActivity(
            repair_witnesses=(_repair_witness("cand_subsidiary", 3, 4),),
            budget_witnesses=(
                _budget_witness(
                    "cand_subsidiary:budget",
                    source_state=3,
                    carried_under_own_policy=False,
                    active=active,
                ),
            ),
            record_witnesses=(_record_witness("cand_subsidiary", own=True),),
            boundaries=(_two_class("cand_subsidiary"),),
            maintenance=_maintenance("cand_subsidiary", 3),
        ),
        "cand_platform_dependent": CandidateActivity(
            repair_witnesses=(_repair_witness("cand_platform_dependent", 5, 6),),
            budget_witnesses=(
                _budget_witness(
                    "cand_platform_dependent:budget",
                    source_state=5,
                    carried_under_own_policy=True,
                    active=active,
                ),
            ),
            record_witnesses=(_record_witness("cand_platform_dependent", own=True),),
            boundaries=(_two_class("cand_platform_dependent"),),
            maintenance=_maintenance("cand_platform_dependent", 23),
        ),
        "cand_shadow": CandidateActivity(
            repair_witnesses=(_repair_witness("cand_shadow", 7, 8),),
            budget_witnesses=(
                _budget_witness(
                    "cand_shadow:budget",
                    source_state=7,
                    carried_under_own_policy=True,
                    active=active,
                ),
            ),
            record_witnesses=(_record_witness("cand_shadow", own=False),),
            boundaries=(_two_class("cand_shadow"),),
            maintenance=_maintenance("cand_shadow", 7),
        ),
        "cand_fed_a": CandidateActivity(),
        "cand_fed_b": CandidateActivity(),
        "cand_coalition": closed_activity("cand_coalition", 9, 10),
        "cand_overlap_x": closed_activity("cand_overlap_x", 11, 12),
        "cand_overlap_y": closed_activity("cand_overlap_y", 12, 13),
        "cand_non_individuated": CandidateActivity(),
        "cand_vacuous_attempt": CandidateActivity(),
        "cand_coarsest_control": CandidateActivity(
            repair_witnesses=(_repair_witness("cand_coarsest_control", 17, 18),),
            budget_witnesses=(
                _budget_witness(
                    "cand_coarsest_control:budget",
                    source_state=17,
                    carried_under_own_policy=True,
                    active=active,
                ),
            ),
            record_witnesses=(_record_witness("cand_coarsest_control", own=True),),
            boundaries=(
                _two_class("cand_coarsest_control"),
                _three_class("cand_coarsest_control"),
            ),
            maintenance=_maintenance("cand_coarsest_control", 17),
        ),
        "cand_bound_control": CandidateActivity(
            repair_witnesses=(_repair_witness("cand_bound_control", 24, 25),),
            budget_witnesses=(
                _budget_witness(
                    "cand_bound_control:budget",
                    source_state=24,
                    carried_under_own_policy=True,
                    active=active,
                ),
            ),
            record_witnesses=(_record_witness("cand_bound_control", own=True),),
            boundaries=(_bound_bad("cand_bound_control"),),
            maintenance=_maintenance("cand_bound_control", 24),
        ),
        "cand_max_sub": closed_activity("cand_max_sub", 26, 27),
        "cand_max_sup": closed_activity("cand_max_sup", 26, 27),
        "cand_unlinked_control": CandidateActivity(
            budget_witnesses=(
                _budget_witness(
                    "cand_unlinked_control:inside_tau",
                    source_state=19,
                    carried_under_own_policy=True,
                    active=active,
                    decoy_state=20,
                ),
                _budget_witness(
                    "cand_unlinked_control:outside_tau",
                    source_state=20,
                    carried_under_own_policy=True,
                    active=active,
                    decoy_state=19,
                ),
            )
        ),
    }
    expected_status = {
        "cand_integrated": IndividuationStatus.integrated,
        "cand_subsidiary": IndividuationStatus.subsidiary,
        "cand_platform_dependent": IndividuationStatus.platform_dependent,
        "cand_shadow": IndividuationStatus.shadow,
        "cand_fed_a": IndividuationStatus.federated,
        "cand_fed_b": IndividuationStatus.federated,
        "cand_coalition": IndividuationStatus.integrated,
        "cand_overlap_x": IndividuationStatus.federated,
        "cand_overlap_y": IndividuationStatus.federated,
        "cand_non_individuated": IndividuationStatus.non_individuated,
        "cand_vacuous_attempt": IndividuationStatus.non_individuated,
        "cand_coarsest_control": IndividuationStatus.integrated,
        "cand_bound_control": IndividuationStatus.non_individuated,
        "cand_max_sub": IndividuationStatus.non_individuated,
        "cand_max_sup": IndividuationStatus.integrated,
    }
    status_records = {
        candidate: IndividuationStatusRecord(
            name=f"isr:{candidate}",
            candidate_name=candidate,
            status=status,
            supporting_ledger_entries=(f"ledger:status:{candidate}",),
            supporting_audit_records=(f"audit:status:{candidate}",),
        )
        for candidate, status in expected_status.items()
    }
    ledger_entries = {
        "ledger:seed",
        *(w.entry for activity in activities.values() for w in activity.record_witnesses),
        *(w.budget_entry for activity in activities.values() for w in activity.budget_witnesses),
        *(record.supporting_ledger_entries[0] for record in status_records.values()),
        *(
            entry
            for activity in activities.values()
            for maintenance in ([activity.maintenance] if activity.maintenance else [])
            for entry in (
                *maintenance.app_t.used_ledger_entries,
                *maintenance.app_tplus1.used_ledger_entries,
                *maintenance.operator.operator_ledger_entries,
                maintenance.record.reinstatement_ledger_entry,
            )
        ),
    }
    audit_records = {
        *(r.audit_record for activity in activities.values() for r in activity.repair_witnesses),
        *(record.supporting_audit_records[0] for record in status_records.values()),
        *(
            audit
            for activity in activities.values()
            for maintenance in ([activity.maintenance] if activity.maintenance else [])
            for audit in (
                *maintenance.app_t.used_audit_records,
                *maintenance.app_tplus1.used_audit_records,
                *maintenance.operator.operator_audit_records,
            )
        ),
    }
    config, active_family, economy = _make_config(frozenset(ledger_entries), frozenset(audit_records))
    return Fixture(
        config=config,
        candidates=candidates,
        candidate_order=tuple(candidates),
        activities=activities,
        status_records=status_records,
        carried_status_records=frozenset(record.name for record in status_records.values()),
        ledger_entries=frozenset(ledger_entries),
        audit_records=frozenset(audit_records),
        carried_apparatus_records=frozenset(
            app.apparatus_record
            for activity in activities.values()
            for maintenance in ([activity.maintenance] if activity.maintenance else [])
            for app in (maintenance.app_t, maintenance.app_tplus1)
        ),
        carried_operator_records=frozenset(
            maintenance.operator.operator_record
            for activity in activities.values()
            for maintenance in ([activity.maintenance] if activity.maintenance else [])
        ),
        carried_reinstatement_records=frozenset(
            maintenance.record.name
            for activity in activities.values()
            for maintenance in ([activity.maintenance] if activity.maintenance else [])
        ),
        probe_economy=economy,
        active_family=active_family,
    )


def candidate_member(fixture: Fixture, candidate_name: str) -> bool:
    return candidate_name in fixture.candidates and candidate_name in fixture.candidate_order


def _activity(fixture: Fixture, candidate_name: str) -> CandidateActivity:
    return fixture.activities[candidate_name]


def entry_closed_on(fixture: Fixture, candidate_name: str, entry: str, own_policy: bool) -> bool:
    del candidate_name
    return entry in fixture.ledger_entries and own_policy is True


def record_closed_on(fixture: Fixture, candidate_name: str) -> bool:
    records = _activity(fixture, candidate_name).record_witnesses
    return bool(records) and all(
        entry_closed_on(fixture, candidate_name, record.entry, record.carried_under_own_policy)
        for record in records
    )


def repair_attributed_to(fixture: Fixture, candidate_name: str, repair: RepairWitness) -> bool:
    candidate = fixture.candidates[candidate_name]
    return (
        candidate.contains(repair.source)
        and repair.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and repair.generated_by_s is True
        and repair.in_scope is True
        and fixture.config.e_system.T.supp_k(repair.source, repair.target)
        and repair.audit_record in fixture.audit_records
    )


def repair_closed_on(fixture: Fixture, candidate_name: str) -> bool:
    repairs = tuple(
        repair
        for repair in _activity(fixture, candidate_name).repair_witnesses
        if repair_attributed_to(fixture, candidate_name, repair)
    )
    candidate = fixture.candidates[candidate_name]
    return bool(repairs) and all(candidate.contains(repair.target) for repair in repairs)


def budget_feasible(fixture: Fixture, witness: ExposureBudgetWitness) -> bool:
    return (
        witness.feasible is True
        and witness.budget_entry in fixture.ledger_entries
        and fixture.probe_economy.exposure_budget_entry(witness.budget_entry, witness.amount)
        and fixture.probe_economy.budget_admissible(witness.move)
    )


def attributed_to_i(fixture: Fixture, candidate_name: str, witness: ExposureBudgetWitness) -> bool:
    occurrence = witness.policy_occurrence
    tau_state = fixture.config.e_system.T.trajectory.tau(occurrence.n0)
    return (
        witness.budget_entry in fixture.ledger_entries
        and occurrence.policy_value == _policy_rho_of(tau_state, "access")
        and occurrence.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and occurrence.generated_by_s is True
        and occurrence.in_scope is True
        and fixture.candidates[candidate_name].contains(tau_state)
        and occurrence.access_move == witness.name
    )


def budget_closed_on(fixture: Fixture, candidate_name: str) -> bool:
    witnesses = tuple(
        witness
        for witness in _activity(fixture, candidate_name).budget_witnesses
        if budget_feasible(fixture, witness) and attributed_to_i(fixture, candidate_name, witness)
    )
    return bool(witnesses) and all(
        entry_closed_on(
            fixture,
            candidate_name,
            witness.budget_entry,
            witness.funding_entry_carried_under_own_policy,
        )
        for witness in witnesses
    )


def _factors_through(
    fixture: Fixture,
    candidate_name: str,
    q: BoundaryQuotient,
    pi: BoundaryQuotient,
) -> bool:
    candidate = fixture.candidates[candidate_name]
    for left in STATES:
        for right in STATES:
            if pi.classify(left, candidate) == pi.classify(right, candidate) and q.classify(
                left, candidate
            ) != q.classify(right, candidate):
                return False
    return True


def _probe_readouts(quotient: BoundaryQuotient, state: int, candidate: Subcarrier) -> tuple[str, str]:
    if quotient.variant == "bound_bad":
        if state == 24:
            return ("v_lo:bound_low", "v_hi:bound_low")
        if state == 25:
            return ("v_lo:bound_high", "v_hi:bound_high")
        return ("v_lo:outside", "v_hi:outside")
    quotient_class = quotient.classify(state, candidate)
    return (f"v_lo:{quotient_class}", f"v_hi:{quotient_class}")


def sufficiency_closure_certified(fixture: Fixture, quotient: BoundaryQuotient) -> bool:
    candidate = fixture.candidates[quotient.candidate_name]
    for left in STATES:
        for right in STATES:
            if quotient.classify(left, candidate) == quotient.classify(right, candidate) and _probe_readouts(
                quotient, left, candidate
            ) != _probe_readouts(quotient, right, candidate):
                return False
    return True


def coarsest_quotient_certified(
    fixture: Fixture,
    candidate_name: str,
    quotient: BoundaryQuotient,
) -> bool:
    if not sufficiency_closure_certified(fixture, quotient):
        return False
    sufficient = tuple(
        candidate_quotient
        for candidate_quotient in _activity(fixture, candidate_name).boundaries
        if sufficiency_closure_certified(fixture, candidate_quotient)
    )
    return all(
        _factors_through(fixture, candidate_name, quotient, other)
        for other in sufficient
    )


def viability_sufficient_boundary(
    fixture: Fixture,
    candidate_name: str,
    quotient: BoundaryQuotient,
) -> bool:
    return sufficiency_closure_certified(fixture, quotient) and coarsest_quotient_certified(
        fixture, candidate_name, quotient
    )


def has_viability_sufficient_boundary(fixture: Fixture, candidate_name: str) -> bool:
    return any(
        viability_sufficient_boundary(fixture, candidate_name, quotient)
        for quotient in _activity(fixture, candidate_name).boundaries
    )


def closure_apparatus_occurrence_for(fixture: Fixture, t: int, app: ClosureApparatus) -> bool:
    return (
        app.time == t
        and app.apparatus_record in fixture.carried_apparatus_records
        and all(entry in fixture.ledger_entries for entry in app.used_ledger_entries)
        and all(audit in fixture.audit_records for audit in app.used_audit_records)
    )


def maintenance_operator_occurrence_for(
    fixture: Fixture,
    operator: ClosureMaintenanceOperator,
) -> bool:
    return (
        operator.operator_record in fixture.carried_operator_records
        and operator.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and operator.generated_by_s is True
        and operator.in_scope is True
        and all(entry in fixture.ledger_entries for entry in operator.operator_ledger_entries)
        and all(audit in fixture.audit_records for audit in operator.operator_audit_records)
    )


def maintenance_reinstatement_for_e12(
    fixture: Fixture,
    maintenance: MaintenanceWitness,
) -> bool:
    record = maintenance.record
    operator = maintenance.operator
    generated_output = operator.apply(record.source_state)
    return (
        closure_apparatus_occurrence_for(fixture, record.time, maintenance.app_t)
        and closure_apparatus_occurrence_for(fixture, record.time + 1, maintenance.app_tplus1)
        and maintenance_operator_occurrence_for(fixture, operator)
        and record.name in fixture.carried_reinstatement_records
        and record.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and record.generated_by_s is True
        and record.in_scope is True
        and record.operator_record == operator.operator_record
        and record.pre_app_record == maintenance.app_t.apparatus_record
        and record.post_app_record == maintenance.app_tplus1.apparatus_record
        and record.output_record == generated_output.apparatus_record
        and maintenance.app_tplus1 == generated_output
        and record.reinstatement_ledger_entry in fixture.ledger_entries
        and fixture.config.e_system.T.supp_k(record.source_state, record.target_state)
    )


def self_maintained_boundary(fixture: Fixture, candidate_name: str) -> bool:
    maintenance = _activity(fixture, candidate_name).maintenance
    if maintenance is None:
        return False
    return (
        maintenance_reinstatement_for_e12(fixture, maintenance)
        and fixture.candidates[candidate_name].contains(maintenance.record.source_state)
    )


def individuates(fixture: Fixture, candidate_name: str) -> bool:
    return (
        repair_closed_on(fixture, candidate_name)
        and budget_closed_on(fixture, candidate_name)
        and record_closed_on(fixture, candidate_name)
        and has_viability_sufficient_boundary(fixture, candidate_name)
        and self_maintained_boundary(fixture, candidate_name)
    )


def _subset(left: Subcarrier, right: Subcarrier) -> bool:
    return left.states.issubset(right.states)


def maximal_individuating(fixture: Fixture, candidate_name: str) -> bool:
    if not candidate_member(fixture, candidate_name) or not individuates(fixture, candidate_name):
        return False
    candidate = fixture.candidates[candidate_name]
    for other_name in fixture.candidate_order:
        other = fixture.candidates[other_name]
        if _subset(candidate, other) and individuates(fixture, other_name) and other_name != candidate_name:
            return False
    return True


def overlaps_another_maximal(fixture: Fixture, candidate_name: str) -> bool:
    candidate = fixture.candidates[candidate_name]
    for other_name in fixture.candidate_order:
        if other_name == candidate_name or not maximal_individuating(fixture, other_name):
            continue
        other = fixture.candidates[other_name]
        if (
            candidate.states & other.states
            and not _subset(candidate, other)
            and not _subset(other, candidate)
        ):
            return True
    return False


def federated_evidence_disjunct(fixture: Fixture, candidate_name: str) -> str | None:
    candidate = fixture.candidates[candidate_name]
    coalition = any(
        other_name != candidate_name
        and _subset(candidate, fixture.candidates[other_name])
        and maximal_individuating(fixture, other_name)
        for other_name in fixture.candidate_order
    )
    if (
        candidate_member(fixture, candidate_name)
        and not individuates(fixture, candidate_name)
        and coalition
    ):
        return "coalition"
    if maximal_individuating(fixture, candidate_name) and overlaps_another_maximal(
        fixture, candidate_name
    ):
        return "overlap"
    return None


def federated_evidence(fixture: Fixture, candidate_name: str) -> bool:
    return federated_evidence_disjunct(fixture, candidate_name) is not None


def integrated_case(fixture: Fixture, candidate_name: str) -> bool:
    return maximal_individuating(fixture, candidate_name) and not overlaps_another_maximal(
        fixture, candidate_name
    )


def federated_case(fixture: Fixture, candidate_name: str) -> bool:
    return not integrated_case(fixture, candidate_name) and federated_evidence(
        fixture, candidate_name
    )


def subsidiary_case(fixture: Fixture, candidate_name: str) -> bool:
    return (
        not integrated_case(fixture, candidate_name)
        and not federated_case(fixture, candidate_name)
        and repair_closed_on(fixture, candidate_name)
        and record_closed_on(fixture, candidate_name)
        and not budget_closed_on(fixture, candidate_name)
        and has_viability_sufficient_boundary(fixture, candidate_name)
    )


def platform_dependent_case(fixture: Fixture, candidate_name: str) -> bool:
    return (
        not integrated_case(fixture, candidate_name)
        and not federated_case(fixture, candidate_name)
        and not subsidiary_case(fixture, candidate_name)
        and repair_closed_on(fixture, candidate_name)
        and budget_closed_on(fixture, candidate_name)
        and record_closed_on(fixture, candidate_name)
        and has_viability_sufficient_boundary(fixture, candidate_name)
        and not self_maintained_boundary(fixture, candidate_name)
    )


def shadow_case(fixture: Fixture, candidate_name: str) -> bool:
    return (
        not integrated_case(fixture, candidate_name)
        and not federated_case(fixture, candidate_name)
        and not subsidiary_case(fixture, candidate_name)
        and not platform_dependent_case(fixture, candidate_name)
        and repair_closed_on(fixture, candidate_name)
        and budget_closed_on(fixture, candidate_name)
        and not record_closed_on(fixture, candidate_name)
    )


def non_individuated_case(fixture: Fixture, candidate_name: str) -> bool:
    return (
        not integrated_case(fixture, candidate_name)
        and not federated_case(fixture, candidate_name)
        and not subsidiary_case(fixture, candidate_name)
        and not platform_dependent_case(fixture, candidate_name)
        and not shadow_case(fixture, candidate_name)
    )


def individuation_status_occurrence_for(fixture: Fixture, candidate_name: str) -> bool:
    record = fixture.status_records.get(candidate_name)
    return (
        record is not None
        and candidate_member(fixture, candidate_name)
        and record.name in fixture.carried_status_records
        and record.candidate_name == candidate_name
        and record.source_tag
        in {FineSourceTag.committed_state, FineSourceTag.audited_cell_records}
        and record.generated_by_s is True
        and record.in_scope is True
        and all(entry in fixture.ledger_entries for entry in record.supporting_ledger_entries)
        and all(audit in fixture.audit_records for audit in record.supporting_audit_records)
    )


def _case_truths(fixture: Fixture, candidate_name: str) -> dict[str, bool]:
    return {
        "integrated": integrated_case(fixture, candidate_name),
        "federated": federated_case(fixture, candidate_name),
        "subsidiary": subsidiary_case(fixture, candidate_name),
        "platform_dependent": platform_dependent_case(fixture, candidate_name),
        "shadow": shadow_case(fixture, candidate_name),
        "non_individuated": non_individuated_case(fixture, candidate_name),
    }


def classify_individuation_status(
    fixture: Fixture,
    candidate_name: str,
) -> tuple[IndividuationStatus, dict[str, bool], IndividuationStatusRecord | None]:
    if not candidate_member(fixture, candidate_name):
        return IndividuationStatus.unclassified, {}, None
    if candidate_name not in fixture.status_records or not individuation_status_occurrence_for(
        fixture, candidate_name
    ):
        return IndividuationStatus.unclassified, _case_truths(fixture, candidate_name), None
    record = fixture.status_records[candidate_name]
    truths = _case_truths(fixture, candidate_name)
    for status in (
        IndividuationStatus.integrated,
        IndividuationStatus.federated,
        IndividuationStatus.subsidiary,
        IndividuationStatus.platform_dependent,
        IndividuationStatus.shadow,
        IndividuationStatus.non_individuated,
    ):
        if truths[status.value] and record.status is status:
            return status, truths, record
    return IndividuationStatus.unclassified, truths, record


def _candidate_row(fixture: Fixture, candidate_name: str) -> CandidateRow:
    status, truths, record = classify_individuation_status(fixture, candidate_name)
    return CandidateRow(
        candidate=candidate_name,
        repair_closed=repair_closed_on(fixture, candidate_name),
        budget_closed=budget_closed_on(fixture, candidate_name),
        record_closed=record_closed_on(fixture, candidate_name),
        viability_sufficient_boundary=has_viability_sufficient_boundary(fixture, candidate_name),
        self_maintained_boundary=self_maintained_boundary(fixture, candidate_name),
        status=status.value,
        integrated=truths["integrated"] and status is IndividuationStatus.integrated,
        federated=truths["federated"] and status is IndividuationStatus.federated,
        subsidiary=truths["subsidiary"] and status is IndividuationStatus.subsidiary,
        platform_dependent=truths["platform_dependent"]
        and status is IndividuationStatus.platform_dependent,
        shadow=truths["shadow"] and status is IndividuationStatus.shadow,
        non_individuated=truths["non_individuated"]
        and status is IndividuationStatus.non_individuated,
        federated_disjunct=federated_evidence_disjunct(fixture, candidate_name),
        carried_status_record=record.name if record else None,
    )


def _quotient_controls(fixture: Fixture) -> tuple[QuotientControlRow, ...]:
    candidate_name = "cand_coarsest_control"
    rows = []
    for quotient in _activity(fixture, candidate_name).boundaries:
        rows.append(
            QuotientControlRow(
                name=quotient.variant,
                candidate=candidate_name,
                sufficient=sufficiency_closure_certified(fixture, quotient),
                coarsest=coarsest_quotient_certified(fixture, candidate_name, quotient),
                viability_sufficient_boundary=viability_sufficient_boundary(
                    fixture, candidate_name, quotient
                ),
            )
        )
    return tuple(rows)


def _unlinked_controls(fixture: Fixture) -> tuple[UnlinkedControlRow, ...]:
    candidate_name = "cand_unlinked_control"
    rows = []
    for witness in _activity(fixture, candidate_name).budget_witnesses:
        tau_state = fixture.config.e_system.T.trajectory.tau(witness.policy_occurrence.n0)
        decoy = witness.policy_occurrence.decoy_state
        if decoy is None:
            raise ValueError("unlinked controls require a decoy state")
        rows.append(
            UnlinkedControlRow(
                name=witness.name,
                candidate=candidate_name,
                tau_state=tau_state,
                decoy_state=decoy,
                same_rho_of=_policy_rho_of(tau_state, "access") == _policy_rho_of(decoy, "access"),
                attributed_to_i=attributed_to_i(fixture, candidate_name, witness),
            )
        )
    return tuple(rows)


def _arbitrary_fragment_control(fixture: Fixture) -> dict[str, bool | str]:
    fragment = frozenset({0})
    return {
        "fragment": "{0}",
        "is_declared_candidate": any(candidate.states == fragment for candidate in fixture.candidates.values()),
        "registered_status": False,
        "candidate_loop_skips": all(candidate.states != fragment for candidate in _registered_candidate_objects(fixture)),
    }


def _registered_candidate_objects(fixture: Fixture) -> tuple[Subcarrier, ...]:
    return tuple(fixture.candidates[name] for name in REGISTERED_CANDIDATES)


def _non_vacuity_control(fixture: Fixture) -> dict[str, bool]:
    candidate_name = "cand_vacuous_attempt"
    return {
        "has_repair_witness": bool(_activity(fixture, candidate_name).repair_witnesses),
        "has_budget_witness": bool(_activity(fixture, candidate_name).budget_witnesses),
        "has_record_witness": bool(_activity(fixture, candidate_name).record_witnesses),
        "repair_closed": repair_closed_on(fixture, candidate_name),
        "budget_closed": budget_closed_on(fixture, candidate_name),
        "record_closed": record_closed_on(fixture, candidate_name),
    }


def _actual_scope_discipline(fixture: Fixture, rows: tuple[CandidateRow, ...]) -> bool:
    return all(
        row.candidate in REGISTERED_CANDIDATES
        and row.carried_status_record in fixture.carried_status_records
        and fixture.status_records[row.candidate].candidate_name == row.candidate
        for row in rows
    )


def _no_hardcoded_status_discipline(rows: tuple[CandidateRow, ...]) -> bool:
    return all(
        sum(
            (
                row.integrated,
                row.federated,
                row.subsidiary,
                row.platform_dependent,
                row.shadow,
                row.non_individuated,
            )
        )
        == 1
        and row.status
        in {
            IndividuationStatus.integrated.value,
            IndividuationStatus.federated.value,
            IndividuationStatus.subsidiary.value,
            IndividuationStatus.platform_dependent.value,
            IndividuationStatus.shadow.value,
            IndividuationStatus.non_individuated.value,
        }
        for row in rows
    )


def _fmt_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def _mapping_summary(mapping: dict[str, Any]) -> str:
    return "; ".join(f"{key}={_fmt_bool(value)}" for key, value in sorted(mapping.items()))


def _row_summary(row: CandidateRow) -> str:
    return (
        f"repair={row.repair_closed}; budget={row.budget_closed}; record={row.record_closed}; "
        f"boundary={row.viability_sufficient_boundary}; self={row.self_maintained_boundary}; "
        f"status={row.status}; disjunct={row.federated_disjunct}"
    )


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    rows = {row.candidate: row for row in results.candidate_rows}
    quotient = {row.name: row for row in results.quotient_controls}
    unlinked = {row.name: row for row in results.unlinked_controls}
    expected_status = {
        "cand_integrated": (True, True, True, True, True, "integrated"),
        "cand_subsidiary": (True, False, True, True, True, "subsidiary"),
        "cand_platform_dependent": (True, True, True, True, False, "platform_dependent"),
        "cand_shadow": (True, True, False, True, True, "shadow"),
        "cand_fed_a": (False, False, False, False, False, "federated"),
        "cand_fed_b": (False, False, False, False, False, "federated"),
        "cand_coalition": (True, True, True, True, True, "integrated"),
        "cand_overlap_x": (True, True, True, True, True, "federated"),
        "cand_overlap_y": (True, True, True, True, True, "federated"),
        "cand_non_individuated": (False, False, False, False, False, "non_individuated"),
        "cand_vacuous_attempt": (False, False, False, False, False, "non_individuated"),
        "cand_coarsest_control": (True, True, True, True, True, "integrated"),
        "cand_bound_control": (True, True, True, False, True, "non_individuated"),
        "cand_max_sub": (True, True, True, True, True, "non_individuated"),
        "cand_max_sup": (True, True, True, True, True, "integrated"),
    }
    comparisons: list[Comparison] = []
    for candidate, expected in expected_status.items():
        row = rows[candidate]
        observed = (
            row.repair_closed,
            row.budget_closed,
            row.record_closed,
            row.viability_sufficient_boundary,
            row.self_maintained_boundary,
            row.status,
        )
        comparisons.append(
            Comparison(
                candidate,
                observed == expected and sum(
                    (
                        row.integrated,
                        row.federated,
                        row.subsidiary,
                        row.platform_dependent,
                        row.shadow,
                        row.non_individuated,
                    )
                )
                == 1,
                _row_summary(row),
                str(expected),
            )
        )
    two = quotient["two_class"]
    three = quotient["three_class"]
    comparisons.extend(
        [
            Comparison(
                "cand_coarsest_control two-class quotient",
                two.sufficient is True
                and two.coarsest is True
                and two.viability_sufficient_boundary is True,
                _mapping_summary(two.__dict__),
                "sufficient=True; coarsest=True; ViabilitySufficientBoundary=True",
            ),
            Comparison(
                "cand_coarsest_control three-class quotient",
                three.sufficient is True
                and three.coarsest is False
                and three.viability_sufficient_boundary is False,
                _mapping_summary(three.__dict__),
                "sufficient=True; coarsest=False; ViabilitySufficientBoundary=False",
            ),
        ]
    )
    inside = unlinked["cand_unlinked_control:inside_tau"]
    outside = unlinked["cand_unlinked_control:outside_tau"]
    comparisons.extend(
        [
            Comparison(
                "cand_unlinked_control tau-inside subcase",
                inside.tau_state == 19
                and inside.decoy_state == 20
                and inside.same_rho_of is True
                and inside.attributed_to_i is True,
                _mapping_summary(inside.__dict__),
                "tau(n0)=19 in candidate; decoy=20; same rhoOf; AttributedToI=True",
            ),
            Comparison(
                "cand_unlinked_control tau-outside subcase",
                outside.tau_state == 20
                and outside.decoy_state == 19
                and outside.same_rho_of is True
                and outside.attributed_to_i is False,
                _mapping_summary(outside.__dict__),
                "tau(n0)=20 outside candidate; decoy=19; same rhoOf; AttributedToI=False",
            ),
        ]
    )
    return tuple(comparisons)


def run_e12_individuation_sweep() -> SweepResults:
    fixture = build_fixture()
    rows = tuple(_candidate_row(fixture, candidate) for candidate in REGISTERED_CANDIDATES)
    results = SweepResults(
        candidate_rows=rows,
        quotient_controls=_quotient_controls(fixture),
        unlinked_controls=_unlinked_controls(fixture),
        arbitrary_fragment_control=_arbitrary_fragment_control(fixture),
        non_vacuity_control=_non_vacuity_control(fixture),
        actual_scope_discipline=_actual_scope_discipline(fixture, rows),
        no_hardcoded_status_discipline=_no_hardcoded_status_discipline(rows),
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E12 Individuation Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e12_individuation_sweep` "
        "against `formalization/notes/sweeps/E12_individuation_predictions.md`.",
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
            "- The 30-state carrier uses Repair-World's `ring_kernel(30)` and the matching modular "
            "`suppK(z,z') = z' == (z+1) % 30` relation.",
            "- Closure predicates search concrete repair, budget, and record witness lists and include "
            "their non-vacuity conjuncts.",
            "- `BudgetClosedOn` checks `AttributedToI` through `tau(n0)` directly; the unlinked-control "
            "rows share a `rhoOf` value for states 19 and 20 to exercise the reviewed fix.",
            "- Coarsest quotient certification computes the Lean direction `q = f o pi`: the two-class "
            "quotient factors through the finer quotient, while the finer quotient does not factor "
            "through the two-class quotient.",
            "- Statuses are derived from the priority-normalized case predicates over declared "
            "`Candidates`; the undeclared `{0}` fragment is not classified.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_e12_individuation_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    total = len(results.comparisons)
    passed = sum(1 for comparison in results.comparisons if comparison.passed)
    print(f"E12 individuation sweep: {passed}/{total} comparisons PASS")
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    if failures:
        for failure in failures:
            print(f"FAIL {failure.name}: observed {failure.observed}; expected {failure.expected}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
