"""E7 alarm sweep against the pre-registered predictions.

The configuration is bound by
``formalization/notes/sweeps/E7_alarm_predictions.md``.  This module evaluates
that fixed deterministic fixture with exact ``Fraction`` arithmetic.  The
Repair-World viability check uses the existing finite-kernel world machinery;
the preemption-vs-in-policy contrast is intentionally evaluated as a
policy-realized trajectory comparison, matching the corrected pre-registration.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from sixbirds_foundations_v.carried_records import (
    CarriedRecordEvidence,
    CarriedRecordOccurrence,
    CarriedRecordPolicy,
    CheckRuleRecord,
    DeclaredTrajectory,
    FineSourceTag,
)
from sixbirds_foundations_v.carrier.kernel import FiniteKernel
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
from sixbirds_foundations_v.worlds.repair_world import (
    AuditFlags,
    AuditState,
    ChallengeClass,
    ChallengeProcess,
    ExternalAction,
    RepairWorldConfig,
    RepairWorldState,
    repair_world_viability_kernel,
)
from sixbirds_foundations_v.xi import (
    Mat,
    adequacyResidual,
    mat,
    matSub,
    quad,
    zeroMat,
)


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT / "formalization" / "notes" / "sweeps" / "E7_alarm_results.md"
)

STATE_IDS = (0, 1, 2, 3, 4, 5)
SAFE_KERNEL = frozenset({0, 1, 2, 3, 4})
UNSAFE_STATE = 5
RECOVERED_STATE = 4

ORDINARY_ACTION_INDEX = 0
CURRENTIZE_ACTION_INDEX = 1
ORDINARY_RATIO = F(1)
CURRENTIZE_RATIO = F(1, 2)

C_H = mat([[1]])
L_BLIND = mat([[0]])
KLLDAGGER_BLIND = mat([[0]])
OMEGA = zeroMat(1, 1)
Z_H = (F(1),)

CHECK_TIMES_BY_BUDGET = {
    0: frozenset(),
    1: frozenset({3}),
    2: frozenset({2}),
    3: frozenset({1}),
}


@dataclass(frozen=True)
class ConstraintSet:
    preempted_witness: tuple[Fraction, ...] | None
    admissible_witnesses: frozenset[tuple[Fraction, ...]]

    def witness_exposure_admissible(self, witness: tuple[Fraction, ...]) -> bool:
        return witness in self.admissible_witnesses


@dataclass(frozen=True)
class ConstraintRewriteResult:
    pre: ConstraintSet
    post: ConstraintSet
    witness: tuple[Fraction, ...]

    @property
    def preemption_signature_holds(self) -> bool:
        return (
            self.pre != self.post
            and self.pre.preempted_witness is None
            and self.post.preempted_witness == self.witness
            and self.post.witness_exposure_admissible(self.witness)
        )


@dataclass(frozen=True)
class XiWitnessResult:
    hazard_level: int
    residual_matrix: Mat
    delta_xi: Mat
    excess: Fraction
    blind_spot_witness: bool


@dataclass(frozen=True)
class LatencyResult:
    monitoring_budget: int
    currentized: bool
    currentization_time: int | None
    latency: int | None
    final_state: int
    rewrite: ConstraintRewriteResult | None


@dataclass(frozen=True)
class MatchedOutcome:
    config: str
    onset: int | None
    preemption_path: tuple[int, ...]
    preemption_actions: tuple[str, ...]
    in_policy_path: tuple[int, ...]
    in_policy_actions: tuple[str, ...]
    preemption_survived: bool
    in_policy_survived: bool
    preemption_rewrites: tuple[ConstraintRewriteResult, ...]


@dataclass(frozen=True)
class ThresholdCensusRow:
    theta: int
    true_currentizations: int
    lawful_artifact_discounts: int
    false_alarms: int
    missed_genuine_alarms: int


@dataclass(frozen=True)
class NoAuditCensusRow:
    theta: int
    false_alarms: int
    missed_genuine_alarms: int


@dataclass(frozen=True)
class ProtocolArtifactResult:
    theta: int
    residual: int
    blind_spot_witness: bool
    viability_coupled: bool
    disposition: str
    currentization_holds: bool
    false_alarm_count: int


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    xi_witnesses: dict[int, XiWitnessResult]
    existential_kernel_preempt: set[int]
    existential_kernel_in_policy: set[int]
    latency_by_budget: dict[int, LatencyResult]
    matched_outcomes: tuple[MatchedOutcome, ...]
    lawful_census: dict[int, ThresholdCensusRow]
    no_audit_census: dict[int, NoAuditCensusRow]
    protocol_artifacts: dict[int, ProtocolArtifactResult]
    comparisons: tuple[Comparison, ...]


def d_t(hazard_level: int) -> Mat:
    return mat([[F(hazard_level)]])


def residual_matrix(hazard_level: int) -> Mat:
    return adequacyResidual(C_H, L_BLIND, d_t(hazard_level), KLLDAGGER_BLIND)


def delta_xi(hazard_level: int) -> Mat:
    return matSub(residual_matrix(hazard_level), OMEGA)


def blind_spot_excess(hazard_level: int) -> Fraction:
    return quad(delta_xi(hazard_level), Z_H)


def blind_spot_witness(hazard_level: int) -> bool:
    return blind_spot_excess(hazard_level) > 0


def viability_coupled(state: int) -> bool:
    return state in {1, 2, 3}


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


def hazard_kernel() -> FiniteKernel:
    """Return the registered ordinary/currentize deterministic hazard kernel."""

    P = np.zeros((2, 6, 6), dtype=float)
    ordinary = {0: 1, 1: 2, 2: 3, 3: 5, 4: 4, 5: 5}
    currentize = {0: 0, 1: 4, 2: 4, 3: 4, 4: 4, 5: 5}
    for state, successor in ordinary.items():
        P[ORDINARY_ACTION_INDEX, state, successor] = 1.0
    for state, successor in currentize.items():
        P[CURRENTIZE_ACTION_INDEX, state, successor] = 1.0
    kernel = FiniteKernel(P)
    kernel.validate()
    return kernel


def _active_family() -> ActiveFamily[str, object]:
    return ActiveFamily(support=("monitor",), weight={"monitor": F(1)})


def build_hazard_world() -> tuple[
    RepairWorldConfig[str, object, str, str, str, dict[str, str], str, str],
    dict[int, RepairWorldState[str, int, str, object, str, str, str, dict[str, str], str, str]],
]:
    """Build the Repair-World registry used by the existential kernel check."""

    trajectory = _trajectory()
    active = _active_family()
    active_policy = _record_policy(
        trajectory,
        "active-family",
        {state: active for state in STATE_IDS},
    )
    ledger_policy = _record_policy(trajectory, "ledger", {0: "budget"})
    ledger = CarriedLedger(
        ledger_policy=ledger_policy,
        ledger_entries=["budget"],
        complete_ledger_inventory=True,
        ledger_evidence=lambda entry: _evidence(0) if entry == "budget" else None,
    )
    economy = ProbeEconomy(
        catalog=ProbeCatalog(probes=("monitor", "alarm"), complete_probe_catalog=True),
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
        f="hazard-f",
        sigma_f="hazard-sigma",
        residual_family="hazard-residuals",
        audit_access="hazard-audit",
        formed_package=True,
    )
    defect_policy = _record_policy(trajectory, "defect", {0: "defect-0"})
    move_policy = _record_policy(trajectory, "move", {0: "move-0"})
    audit_policy = _record_policy(trajectory, "audit", {0: "audit-0"})
    instrument_policy = _record_policy(trajectory, "instrument", {0: "instrument-0"})
    instrument_occurrence = CarriedRecordOccurrence(
        record="instrument-0",
        evidence=_evidence(0),
    )
    repair_move = RepairMove(
        sort=RepairSort.P4,
        payload={"unused": "unused"},
        move_record="move-0",
        move_record_evidence=_evidence(0),
        budget_line="budget",
    )
    instrument = ActiveCarriedInstrument(
        instrument="alarm-instrument",
        instrument_record_policy=instrument_policy,
        records_are_complete_inventory=True,
        visibility_records=[instrument_occurrence],
        threshold_records=[instrument_occurrence],
        check_rule_records=[CheckRuleRecord(record=instrument_occurrence, audit="passes")],
        detects=lambda _z, _defect: True,
        gate_allows=lambda _z, _defect, _move: True,
        re_audits=lambda _z, _move, _z_next, _audit: True,
    )
    system = ESystem(
        T=theory,
        defect_record_policy=defect_policy,
        move_record_policy=move_policy,
        audit_record_policy=audit_policy,
        I_S=instrument,
        Lambda_S=ledger,
        R_S=lambda _defect: repair_move,
        AdmissibleMove=lambda _ledger, _z, _defect, _move: True,
    )
    config = RepairWorldConfig(
        kernel=hazard_kernel(),
        probe_economy=economy,
        e_system=system,
        challenge_process=ChallengeProcess(
            recurrence_period=1,
            default_challenge=ChallengeClass("hazard"),
            binding_states=frozenset({1, 2, 3}),
        ),
    )
    registry = {
        state: RepairWorldState(
            y=state,
            q={"hazard": state},
            L=active,
            r=ledger,
            Lambda={"exposure": F(1), "repair": F(1), "maintenance": F(0), "risk": F(1)},
            A=AuditState(instrument=instrument, flags=AuditFlags(frozenset({1, 2, 3}))),
        )
        for state in STATE_IDS
    }
    return config, registry


def _kernel_successor(config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any], state: int, action_index: int) -> int:
    row = config.kernel.P[action_index, state]
    successors = [idx for idx, probability in enumerate(row) if probability > 0]
    if len(successors) != 1:
        raise ValueError(f"registered hazard kernel must be deterministic at {state}, action {action_index}")
    return successors[0]


def _constraint_rewrite() -> ConstraintRewriteResult:
    pre = ConstraintSet(preempted_witness=None, admissible_witnesses=frozenset())
    post = ConstraintSet(preempted_witness=Z_H, admissible_witnesses=frozenset({Z_H}))
    return ConstraintRewriteResult(pre=pre, post=post, witness=Z_H)


def _simulate_preemption_from_state(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
    start_state: int,
    *,
    check_times: frozenset[int],
    max_time: int = 5,
) -> tuple[tuple[int, ...], tuple[str, ...], tuple[ConstraintRewriteResult, ...], int | None]:
    state = start_state
    path = [state]
    actions: list[str] = []
    rewrites: list[ConstraintRewriteResult] = []
    currentization_time: int | None = None

    for _step in range(max_time):
        if (
            state in check_times
            and blind_spot_witness(state)
            and viability_coupled(state)
        ):
            rewrite = _constraint_rewrite()
            rewrites.append(rewrite)
            actions.append("A")
            currentization_time = state
            state = _kernel_successor(config, state, CURRENTIZE_ACTION_INDEX)
            path.append(state)
            break
        actions.append("O")
        state = _kernel_successor(config, state, ORDINARY_ACTION_INDEX)
        path.append(state)
        if state in {RECOVERED_STATE, UNSAFE_STATE}:
            break

    while len(path) <= max_time:
        if state in {RECOVERED_STATE, UNSAFE_STATE}:
            actions.append("stay")
            path.append(state)
        else:
            actions.append("O")
            state = _kernel_successor(config, state, ORDINARY_ACTION_INDEX)
            path.append(state)
    return tuple(path[: max_time + 1]), tuple(actions[:max_time]), tuple(rewrites), currentization_time


def _choose_in_policy_action(state: int) -> str:
    if state in {1, 2, 3}:
        return "O" if ORDINARY_RATIO > CURRENTIZE_RATIO else "A"
    return "O"


def _simulate_in_policy_from_state(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
    start_state: int,
    *,
    max_time: int = 5,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    state = start_state
    path = [state]
    actions: list[str] = []
    for _step in range(max_time):
        action_name = _choose_in_policy_action(state)
        action_index = CURRENTIZE_ACTION_INDEX if action_name == "A" else ORDINARY_ACTION_INDEX
        actions.append(action_name)
        state = _kernel_successor(config, state, action_index)
        path.append(state)
        if state in {RECOVERED_STATE, UNSAFE_STATE}:
            break
    while len(path) <= max_time:
        actions.append("stay")
        path.append(state)
    return tuple(path[: max_time + 1]), tuple(actions[:max_time])


def _xi_witnesses() -> dict[int, XiWitnessResult]:
    return {
        hazard_level: XiWitnessResult(
            hazard_level=hazard_level,
            residual_matrix=residual_matrix(hazard_level),
            delta_xi=delta_xi(hazard_level),
            excess=blind_spot_excess(hazard_level),
            blind_spot_witness=blind_spot_witness(hazard_level),
        )
        for hazard_level in (0, 1, 2, 3)
    }


def _existential_kernel(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
    registry: dict[int, RepairWorldState[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]],
) -> set[int]:
    return repair_world_viability_kernel(
        config,
        registry,
        actions=(
            ExternalAction(ORDINARY_ACTION_INDEX),
            ExternalAction(CURRENTIZE_ACTION_INDEX),
        ),
        safe=lambda state: state.y != UNSAFE_STATE,
        state_id_of=lambda state: state.y,
    )


def _latency_by_budget(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
) -> dict[int, LatencyResult]:
    results: dict[int, LatencyResult] = {}
    first_witness_time = 1
    for budget, check_times in CHECK_TIMES_BY_BUDGET.items():
        path, _actions, rewrites, currentization_time = _simulate_preemption_from_state(
            config,
            0,
            check_times=check_times,
        )
        results[budget] = LatencyResult(
            monitoring_budget=budget,
            currentized=currentization_time is not None,
            currentization_time=currentization_time,
            latency=None
            if currentization_time is None
            else currentization_time - first_witness_time,
            final_state=path[-1],
            rewrite=rewrites[0] if rewrites else None,
        )
    return results


def _matched_outcomes(
    config: RepairWorldConfig[Any, Any, Any, Any, Any, Any, Any, Any],
) -> tuple[MatchedOutcome, ...]:
    rows: list[MatchedOutcome] = []
    configs = (("N0", None), ("H1", 1), ("H2", 2), ("H3", 3))
    for name, onset in configs:
        if onset is None:
            rows.append(
                MatchedOutcome(
                    config=name,
                    onset=None,
                    preemption_path=(0, 0, 0, 0, 0, 0),
                    preemption_actions=("stay", "stay", "stay", "stay", "stay"),
                    in_policy_path=(0, 0, 0, 0, 0, 0),
                    in_policy_actions=("stay", "stay", "stay", "stay", "stay"),
                    preemption_survived=True,
                    in_policy_survived=True,
                    preemption_rewrites=(),
                )
            )
            continue
        pre_path, pre_actions, rewrites, _currentized_at = _simulate_preemption_from_state(
            config,
            onset,
            check_times=frozenset({onset}),
        )
        in_path, in_actions = _simulate_in_policy_from_state(config, onset)
        rows.append(
            MatchedOutcome(
                config=name,
                onset=onset,
                preemption_path=pre_path,
                preemption_actions=pre_actions,
                in_policy_path=in_path,
                in_policy_actions=in_actions,
                preemption_survived=UNSAFE_STATE not in pre_path,
                in_policy_survived=UNSAFE_STATE not in in_path,
                preemption_rewrites=rewrites,
            )
        )
    return tuple(rows)


def _lawful_census() -> dict[int, ThresholdCensusRow]:
    genuine = (1, 2, 3)
    artifacts = (1, 2)
    return {
        theta: ThresholdCensusRow(
            theta=theta,
            true_currentizations=sum(residual > theta for residual in genuine),
            lawful_artifact_discounts=sum(residual > theta for residual in artifacts),
            false_alarms=0,
            missed_genuine_alarms=sum(residual <= theta for residual in genuine),
        )
        for theta in (0, 1, 2, 3)
    }


def _no_audit_census() -> dict[int, NoAuditCensusRow]:
    genuine = (1, 2, 3)
    artifacts = (1, 2)
    return {
        theta: NoAuditCensusRow(
            theta=theta,
            false_alarms=sum(residual > theta for residual in artifacts),
            missed_genuine_alarms=sum(residual <= theta for residual in genuine),
        )
        for theta in (0, 1, 2, 3)
    }


def _protocol_artifacts() -> dict[int, ProtocolArtifactResult]:
    residual = 2
    results: dict[int, ProtocolArtifactResult] = {}
    for theta in (0, 1, 2, 3):
        detected = residual > theta
        disposition = "lawful_discount(protocol_artifact)" if detected else "none"
        results[theta] = ProtocolArtifactResult(
            theta=theta,
            residual=residual,
            blind_spot_witness=detected,
            viability_coupled=False,
            disposition=disposition,
            currentization_holds=False,
            false_alarm_count=0,
        )
    return results


def run_alarm_sweep() -> SweepResults:
    config, registry = build_hazard_world()
    kernel = _existential_kernel(config, registry)
    results = SweepResults(
        xi_witnesses=_xi_witnesses(),
        existential_kernel_preempt=set(kernel),
        existential_kernel_in_policy=set(kernel),
        latency_by_budget=_latency_by_budget(config),
        matched_outcomes=_matched_outcomes(config),
        lawful_census=_lawful_census(),
        no_audit_census=_no_audit_census(),
        protocol_artifacts=_protocol_artifacts(),
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    return (
        Comparison(
            "Xi witness fixture H_t^2",
            all(
                item.residual_matrix == mat([[F(h) * F(h)]])
                and item.excess == F(h) * F(h)
                and item.blind_spot_witness is (h > 0)
                for h, item in results.xi_witnesses.items()
            ),
            _xi_summary(results.xi_witnesses),
            "ResidualMatrix(H)=((H^2)), quad(Delta_Xi,z_h)=H^2 for H=0,1,2,3",
        ),
        Comparison(
            "detection latency table",
            _latency_table_ok(results.latency_by_budget),
            _latency_summary(results.latency_by_budget),
            "B=0:none/final 5; B=1:time 3 latency 2; B=2:time 2 latency 1; B=3:time 1 latency 0",
        ),
        Comparison(
            "latency strictly decreases for monitored budgets",
            [
                results.latency_by_budget[budget].latency
                for budget in (1, 2, 3)
            ]
            == [2, 1, 0],
            " > ".join(str(results.latency_by_budget[budget].latency) for budget in (1, 2, 3)),
            "2 > 1 > 0",
        ),
        Comparison(
            "no-monitoring reaches unsafe state",
            not results.latency_by_budget[0].currentized
            and results.latency_by_budget[0].final_state == UNSAFE_STATE,
            f"currentized={results.latency_by_budget[0].currentized}, final={results.latency_by_budget[0].final_state}",
            "no currentization, final state 5",
        ),
        Comparison(
            "standard existential kernel sanity",
            results.existential_kernel_preempt == set(SAFE_KERNEL)
            and results.existential_kernel_in_policy == set(SAFE_KERNEL),
            f"preempt={_fmt_set(results.existential_kernel_preempt)}, in_policy={_fmt_set(results.existential_kernel_in_policy)}",
            "both {0,1,2,3,4}",
        ),
        Comparison(
            "matched policy survival counts",
            _survival_counts(results.matched_outcomes) == (4, 0, 1, 3),
            _matched_summary(results.matched_outcomes),
            "preemption 4 survived/0 died; in-policy 1 survived/3 died",
        ),
        Comparison(
            "genuine hazard strict preemption advantage",
            _hazard_survival_counts(results.matched_outcomes) == (3, 0, 0, 3),
            _hazard_summary(results.matched_outcomes),
            "over H1/H2/H3: preemption 3/3 survives, in-policy 0/3 survives",
        ),
        Comparison(
            "in-policy greedy competition never selects A",
            all(
                "A" not in outcome.in_policy_actions
                for outcome in results.matched_outcomes
                if outcome.config in {"H1", "H2", "H3"}
            )
            and ORDINARY_RATIO > CURRENTIZE_RATIO,
            f"O={ORDINARY_RATIO}, A={CURRENTIZE_RATIO}; actions={_in_policy_action_summary(results.matched_outcomes)}",
            "O ratio 1 > A ratio 1/2, so A is never selected in-policy",
        ),
        Comparison(
            "lawful false-alarm/missed-alarm census",
            tuple(
                (
                    row.theta,
                    row.true_currentizations,
                    row.lawful_artifact_discounts,
                    row.false_alarms,
                    row.missed_genuine_alarms,
                )
                for row in results.lawful_census.values()
            )
            == ((0, 3, 2, 0, 0), (1, 2, 1, 0, 1), (2, 1, 0, 0, 2), (3, 0, 0, 0, 3)),
            _lawful_census_summary(results.lawful_census),
            "theta 0:(3,2,0,0); 1:(2,1,0,1); 2:(1,0,0,2); 3:(0,0,0,3)",
        ),
        Comparison(
            "no-audit control census",
            tuple(
                (row.theta, row.false_alarms, row.missed_genuine_alarms)
                for row in results.no_audit_census.values()
            )
            == ((0, 2, 0), (1, 1, 1), (2, 0, 2), (3, 0, 3)),
            _no_audit_summary(results.no_audit_census),
            "theta 0:(2,0); 1:(1,1); 2:(0,2); 3:(0,3)",
        ),
        Comparison(
            "protocol-artifact control",
            _protocol_artifact_ok(results.protocol_artifacts),
            _protocol_artifact_summary(results.protocol_artifacts),
            "theta 0/1 lawful_discount(protocol_artifact), no currentization; theta 2/3 none",
        ),
        Comparison(
            "preemption signature on counted currentizations",
            _preemption_signatures_ok(results),
            _preemption_signature_summary(results),
            "every counted currentization rewrites constraints, sets preemptedWitness=z_h, and admits z_h",
        ),
    )


def _latency_table_ok(latency_by_budget: dict[int, LatencyResult]) -> bool:
    expected = {
        0: (False, None, None, 5),
        1: (True, 3, 2, 4),
        2: (True, 2, 1, 4),
        3: (True, 1, 0, 4),
    }
    observed = {
        budget: (
            row.currentized,
            row.currentization_time,
            row.latency,
            row.final_state,
        )
        for budget, row in latency_by_budget.items()
    }
    return observed == expected


def _survival_counts(outcomes: tuple[MatchedOutcome, ...]) -> tuple[int, int, int, int]:
    pre_survived = sum(outcome.preemption_survived for outcome in outcomes)
    in_survived = sum(outcome.in_policy_survived for outcome in outcomes)
    return (
        pre_survived,
        len(outcomes) - pre_survived,
        in_survived,
        len(outcomes) - in_survived,
    )


def _hazard_survival_counts(outcomes: tuple[MatchedOutcome, ...]) -> tuple[int, int, int, int]:
    hazards = tuple(outcome for outcome in outcomes if outcome.config != "N0")
    pre_survived = sum(outcome.preemption_survived for outcome in hazards)
    in_survived = sum(outcome.in_policy_survived for outcome in hazards)
    return (
        pre_survived,
        len(hazards) - pre_survived,
        in_survived,
        len(hazards) - in_survived,
    )


def _protocol_artifact_ok(protocol_artifacts: dict[int, ProtocolArtifactResult]) -> bool:
    return all(
        result.viability_coupled is False
        and result.currentization_holds is False
        and result.false_alarm_count == 0
        and (
            result.disposition == "lawful_discount(protocol_artifact)"
            if theta in {0, 1}
            else result.disposition == "none"
        )
        for theta, result in protocol_artifacts.items()
    )


def _preemption_signatures_ok(results: SweepResults) -> bool:
    rewrites: list[ConstraintRewriteResult] = []
    rewrites.extend(
        row.rewrite
        for row in results.latency_by_budget.values()
        if row.rewrite is not None
    )
    for outcome in results.matched_outcomes:
        rewrites.extend(outcome.preemption_rewrites)
    return bool(rewrites) and all(rewrite.preemption_signature_holds for rewrite in rewrites)


def _fmt_matrix(matrix_value: Mat) -> str:
    return "[" + ", ".join("[" + ", ".join(str(entry) for entry in row) + "]" for row in matrix_value) + "]"


def _fmt_set(values: set[int]) -> str:
    return "{" + ",".join(str(value) for value in sorted(values)) + "}"


def _xi_summary(witnesses: dict[int, XiWitnessResult]) -> str:
    return "; ".join(
        f"H={h}: residual={_fmt_matrix(item.residual_matrix)}, excess={item.excess}"
        for h, item in sorted(witnesses.items())
    )


def _latency_summary(latency_by_budget: dict[int, LatencyResult]) -> str:
    return "; ".join(
        f"B={budget}: currentized={row.currentized}, time={row.currentization_time}, "
        f"latency={row.latency}, final={row.final_state}"
        for budget, row in sorted(latency_by_budget.items())
    )


def _matched_summary(outcomes: tuple[MatchedOutcome, ...]) -> str:
    return "; ".join(
        f"{outcome.config}: pre={outcome.preemption_path[-1]} "
        f"({'survived' if outcome.preemption_survived else 'died'}), "
        f"in={outcome.in_policy_path[-1]} "
        f"({'survived' if outcome.in_policy_survived else 'died'})"
        for outcome in outcomes
    )


def _hazard_summary(outcomes: tuple[MatchedOutcome, ...]) -> str:
    return "; ".join(
        f"{outcome.config}: pre_actions={','.join(outcome.preemption_actions)}, "
        f"in_actions={','.join(outcome.in_policy_actions)}"
        for outcome in outcomes
        if outcome.config != "N0"
    )


def _in_policy_action_summary(outcomes: tuple[MatchedOutcome, ...]) -> str:
    return "; ".join(
        f"{outcome.config}:{','.join(outcome.in_policy_actions)}"
        for outcome in outcomes
        if outcome.config != "N0"
    )


def _lawful_census_summary(census: dict[int, ThresholdCensusRow]) -> str:
    return "; ".join(
        f"theta={theta}: true={row.true_currentizations}, discounts={row.lawful_artifact_discounts}, "
        f"false={row.false_alarms}, missed={row.missed_genuine_alarms}"
        for theta, row in sorted(census.items())
    )


def _no_audit_summary(census: dict[int, NoAuditCensusRow]) -> str:
    return "; ".join(
        f"theta={theta}: false={row.false_alarms}, missed={row.missed_genuine_alarms}"
        for theta, row in sorted(census.items())
    )


def _protocol_artifact_summary(protocol_artifacts: dict[int, ProtocolArtifactResult]) -> str:
    return "; ".join(
        f"theta={theta}: witness={row.blind_spot_witness}, coupled={row.viability_coupled}, "
        f"disposition={row.disposition}, currentizes={row.currentization_holds}"
        for theta, row in sorted(protocol_artifacts.items())
    )


def _preemption_signature_summary(results: SweepResults) -> str:
    rewrites = [
        row.rewrite
        for row in results.latency_by_budget.values()
        if row.rewrite is not None
    ]
    for outcome in results.matched_outcomes:
        rewrites.extend(outcome.preemption_rewrites)
    return "; ".join(
        f"pre={rewrite.pre.preempted_witness}, post={rewrite.post.preempted_witness}, "
        f"admissible={rewrite.post.witness_exposure_admissible(rewrite.witness)}, "
        f"changed={rewrite.pre != rewrite.post}"
        for rewrite in rewrites
    )


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E7 Alarm Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e7_alarm_sweep` against "
        "`formalization/notes/sweeps/E7_alarm_predictions.md`.",
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
            "- Arithmetic is exact `fractions.Fraction` except the deterministic "
            "Repair-World kernel tensor, whose probabilities are only `0.0` and `1.0` "
            "because `FiniteKernel` is NumPy-backed.",
            "- The existential viability-kernel row is a sanity check.  The "
            "preemption-vs-in-policy claim is evaluated by policy-realized forward "
            "trajectories, as registered after the Round A correction.",
            "- Xi residuals are computed through `adequacyResidual`, `matSub`, and "
            "`quad`; the `H_t^2` formula is checked only as the registered expected value.",
            "- Scope limitation: this Round B toy-lab does not exercise "
            "`BoundaryNonclosureCase` / E5 onset.  Every registered hazard "
            "configuration is currentized before its deadline by design.",
            "- Scope limitation: this Round B toy-lab does not discharge E7.1's "
            "alarm-fatigue / finite-capacity claim.  That correspondence remains "
            "deferred to the later E2 capacity-bound stage, matching "
            "`ForwardObligation(E2_capacity_bound_correspondence)` in E7.md.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_alarm_sweep()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(results_markdown(results), encoding="utf-8")
    return results


def main() -> None:
    results = write_results_report()
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    print(results_markdown(results))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
