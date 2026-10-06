"""E6+E9 probe-shop sweep against the pre-registered predictions.

The configuration is bound by
``formalization/notes/sweeps/E6_E9_probe_shop_predictions.md``.  This module is
not a solver framework; it evaluates that fixed configuration with exact
``Fraction`` arithmetic, except for the explicitly registered salience
eigenvalue branch.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from sixbirds_foundations_v.probe_economy import (
    ActiveFamily,
    ProbeCatalog,
    acquisition_strict,
)
from sixbirds_foundations_v.xi import (
    Mat,
    adequacyResidual,
    conditionalCurrencyDM_L,
    conditionalCurrencyMD_L,
    conditionalCurrencyMM_L,
    diagonalPseudoInverse,
    is_same_family_saturated,
    mat,
    matMul,
    traceMat,
    zeroMat,
)


F = Fraction

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESULTS_PATH = (
    REPO_ROOT / "formalization" / "notes" / "sweeps" / "E6_E9_probe_shop_results.md"
)

SALIENCE_SEED = 0


@dataclass(frozen=True)
class BaseCandidateResult:
    name: str
    saturated: bool
    conditional_currency: Mat
    discharge: Fraction


@dataclass(frozen=True)
class AllocationOptimum:
    budget: Fraction
    weight: tuple[Fraction, Fraction]
    discharge: Fraction
    residual_trace: Fraction
    marginal_ratios: tuple[Fraction, Fraction]
    ties: tuple[tuple[Fraction, Fraction], ...]


@dataclass(frozen=True)
class FiniteDifferenceRow:
    budget: Fraction
    delta: Fraction
    side: str
    ratio_a: Fraction
    ratio_b: Fraction
    spread: Fraction


@dataclass(frozen=True)
class AcquisitionCandidateResult:
    name: str
    saturated: bool
    acquisition_strict: bool
    conditional_currency: Mat
    discharge: Fraction
    cost: Fraction
    ratio: Fraction


@dataclass(frozen=True)
class JointBudgetResult:
    budget: Fraction
    allocation: tuple[Fraction, Fraction]
    acquisitions: tuple[str, ...]
    total_discharge: Fraction
    allocation_degraded: bool
    acquisition_active: bool


@dataclass(frozen=True)
class SalienceResult:
    label: str
    residual: Mat
    top_direction: str
    top_magnitude: Fraction
    eigenvalues: tuple[float, ...]
    top_eigenvector: tuple[float, ...]


@dataclass(frozen=True)
class Comparison:
    name: str
    passed: bool
    observed: str
    expected: str


@dataclass(frozen=True)
class SweepResults:
    base_residual: Mat
    base_saturated: tuple[BaseCandidateResult, ...]
    base_strict: tuple[BaseCandidateResult, ...]
    allocation_optima: dict[Fraction, AllocationOptimum]
    finite_differences: tuple[FiniteDifferenceRow, ...]
    allocation_closed_form_ok: bool
    allocation_increment_floor: Fraction
    saturated_candidates: tuple[AcquisitionCandidateResult, ...]
    strict_candidates: tuple[AcquisitionCandidateResult, ...]
    joint_budget: dict[Fraction, JointBudgetResult]
    slack_allocation: AllocationOptimum
    proxy_discharge_by_budget: dict[Fraction, Fraction]
    proxy_residual_trace: Fraction
    salience_base: SalienceResult
    salience_shift_b: SalienceResult
    salience_config_hash: str
    salience_output_hash: str
    comparisons: tuple[Comparison, ...]


C_BASE = mat([[1, 0], [0, 2]])
L_BASE = mat([[1, 1]])
D_BASE_1D = mat([[1, 0]])
KLLDAGGER_BASE = mat([["2/3"]])

C = mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
L_OWNED = mat([[1, 0, 0], [0, 1, 0]])
D = mat([[3, 0, 0], [0, 2, 0], [0, 0, "1/2"]])
D_SHIFT_B = mat([[3, 0, 0], [0, 4, 0], [0, 0, "1/2"]])
KLLDAGGER_SPAN = mat([[1, 0], [0, 1]])
KMMLDAGGER_ONE = mat([[1]])

CATALOG = ProbeCatalog(
    probes=("A", "B", "A2", "AB", "B2", "C", "AC", "BC"),
    complete_probe_catalog=True,
)
ACTIVE_FAMILY = ActiveFamily(
    support=("A", "B"),
    weight={"A": F(2), "B": F(1)},
    as_xi_family=L_OWNED,
)

SATURATED_CANDIDATES: tuple[tuple[str, Mat, Mat, Fraction], ...] = (
    ("A2", mat([[2, 0, 0]]), mat([[2, 0]]), F(1, 10)),
    ("AB", mat([[1, 1, 0]]), mat([[1, 1]]), F(1, 10)),
    ("B2", mat([[0, 2, 0]]), mat([[0, 2]]), F(1, 10)),
)

STRICT_CANDIDATES: tuple[tuple[str, Mat, Mat, Fraction], ...] = (
    ("C", mat([[0, 0, 1]]), mat([[0, 0]]), F(1)),
    ("AC", mat([[1, 0, 1]]), mat([[1, 0]]), F(2)),
    ("BC", mat([[0, 1, 1]]), mat([[0, 1]]), F(4)),
)


def rho(t: Fraction) -> Fraction:
    return t / (1 + t)


def kll_dagger_alloc(weight: tuple[Fraction, Fraction]) -> Mat:
    w_a, w_b = weight
    return mat([[rho(w_a), 0], [0, rho(w_b)]])


def residual_matrix(weight: tuple[Fraction, Fraction], target: Mat = D) -> Mat:
    return adequacyResidual(C, L_OWNED, target, kll_dagger_alloc(weight))


def residual_trace(weight: tuple[Fraction, Fraction], target: Mat = D) -> Fraction:
    return traceMat(residual_matrix(weight, target))


def closed_form_residual_trace(weight: tuple[Fraction, Fraction]) -> Fraction:
    w_a, w_b = weight
    return F(9) * (1 - rho(w_a)) + F(4) * (1 - rho(w_b)) + F(1, 4)


def allocation_discharge(weight: tuple[Fraction, Fraction]) -> Fraction:
    w_a, w_b = weight
    return F(9) * rho(w_a) + F(4) * rho(w_b)


def marginal_ratios(weight: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    w_a, w_b = weight
    return (F(9) / (1 + w_a) ** 2, F(4) / (1 + w_b) ** 2)


def finite_difference_ratios(
    weight: tuple[Fraction, Fraction],
    delta: Fraction,
    *,
    side: str,
) -> tuple[Fraction, Fraction]:
    w_a, w_b = weight
    if side == "forward":
        return (
            F(9) / ((1 + w_a) * (1 + w_a + delta)),
            F(4) / ((1 + w_b) * (1 + w_b + delta)),
        )
    if side == "left":
        return (
            F(9) / ((1 + w_a) * (1 + w_a - delta)),
            F(4) / ((1 + w_b) * (1 + w_b - delta)),
        )
    raise ValueError(f"unknown finite-difference side: {side}")


def grid_weights(budget: Fraction) -> tuple[tuple[Fraction, Fraction], ...]:
    weights: list[tuple[Fraction, Fraction]] = []
    for i in range(11):
        w_a = F(i, 5)
        for j in range(6):
            w_b = F(j, 5)
            if w_a + w_b <= budget:
                weights.append((w_a, w_b))
    return tuple(weights)


def allocation_argmax(budget: Fraction) -> AllocationOptimum:
    candidates = grid_weights(budget)
    if not candidates:
        raise ValueError("allocation grid is empty")
    best_discharge = max(allocation_discharge(weight) for weight in candidates)
    ties = tuple(
        weight for weight in candidates if allocation_discharge(weight) == best_discharge
    )
    best = ties[-1]
    return AllocationOptimum(
        budget=budget,
        weight=best,
        discharge=best_discharge,
        residual_trace=residual_trace(best),
        marginal_ratios=marginal_ratios(best),
        ties=ties,
    )


def xi_contraction_discharge(
    currency: Mat,
    active: Mat,
    target: Mat,
    candidate: Mat,
    kll_dagger: Mat,
    kmm_l_dagger: Mat | None = None,
) -> Fraction:
    if kmm_l_dagger is None:
        kmm_l_dagger = diagonalPseudoInverse(
            conditionalCurrencyMM_L(currency, active, candidate, kll_dagger)
        )
    return traceMat(
        matMul(
            matMul(
                conditionalCurrencyDM_L(currency, active, target, candidate, kll_dagger),
                kmm_l_dagger,
            ),
            conditionalCurrencyMD_L(currency, active, target, candidate, kll_dagger),
        )
    )


def _base_sanity() -> tuple[Mat, tuple[BaseCandidateResult, ...], tuple[BaseCandidateResult, ...]]:
    base_residual = adequacyResidual(C_BASE, L_BASE, D_BASE_1D, KLLDAGGER_BASE)
    saturated: list[BaseCandidateResult] = []
    for name, candidate, witness in (
        ("2L", mat([[2, 2]]), mat([[2]])),
        ("1L", mat([[1, 1]]), mat([[1]])),
    ):
        saturated.append(
            BaseCandidateResult(
                name=name,
                saturated=is_same_family_saturated(
                    C_BASE, L_BASE, D_BASE_1D, candidate, KLLDAGGER_BASE, witness
                ),
                conditional_currency=conditionalCurrencyDM_L(
                    C_BASE, L_BASE, D_BASE_1D, candidate, KLLDAGGER_BASE
                ),
                discharge=xi_contraction_discharge(
                    C_BASE, L_BASE, D_BASE_1D, candidate, KLLDAGGER_BASE
                ),
            )
        )

    strict: list[BaseCandidateResult] = []
    for name, candidate, witness in (
        ("second_factor", mat([[0, 1]]), mat([[0]])),
        ("first_factor", mat([[1, 0]]), mat([[0]])),
        ("contrast", mat([[1, -1]]), mat([[1]])),
    ):
        strict.append(
            BaseCandidateResult(
                name=name,
                saturated=is_same_family_saturated(
                    C_BASE, L_BASE, D_BASE_1D, candidate, KLLDAGGER_BASE, witness
                ),
                conditional_currency=conditionalCurrencyDM_L(
                    C_BASE, L_BASE, D_BASE_1D, candidate, KLLDAGGER_BASE
                ),
                discharge=xi_contraction_discharge(
                    C_BASE, L_BASE, D_BASE_1D, candidate, KLLDAGGER_BASE
                ),
            )
        )
    return base_residual, tuple(saturated), tuple(strict)


def _finite_difference_rows(
    optima: dict[Fraction, AllocationOptimum],
) -> tuple[FiniteDifferenceRow, ...]:
    rows: list[FiniteDifferenceRow] = []
    for budget in (F(1), F(2), F(3)):
        side = "left" if budget == 3 else "forward"
        for delta in (F(1, 5), F(1, 10), F(1, 20)):
            ratio_a, ratio_b = finite_difference_ratios(
                optima[budget].weight, delta, side=side
            )
            rows.append(
                FiniteDifferenceRow(
                    budget=budget,
                    delta=delta,
                    side=side,
                    ratio_a=ratio_a,
                    ratio_b=ratio_b,
                    spread=abs(ratio_a - ratio_b),
                )
            )
    return tuple(rows)


def _allocation_closed_form_ok() -> bool:
    return all(
        residual_trace(weight) == closed_form_residual_trace(weight)
        for weight in grid_weights(F(3))
    )


def _allocation_increment_floor() -> Fraction:
    step = F(1, 5)
    ratios: list[Fraction] = []
    for weight in grid_weights(F(3)):
        w_a, w_b = weight
        if w_a + step <= 2:
            ratios.append(
                (allocation_discharge((w_a + step, w_b)) - allocation_discharge(weight))
                / step
            )
        if w_b + step <= 1:
            ratios.append(
                (allocation_discharge((w_a, w_b + step)) - allocation_discharge(weight))
                / step
            )
    return min(ratios)


def _catalog_results() -> tuple[
    tuple[AcquisitionCandidateResult, ...],
    tuple[AcquisitionCandidateResult, ...],
]:
    saturated_results: list[AcquisitionCandidateResult] = []
    strict_results: list[AcquisitionCandidateResult] = []

    for name, candidate, witness, cost in SATURATED_CANDIDATES:
        saturated = is_same_family_saturated(C, L_OWNED, D, candidate, KLLDAGGER_SPAN, witness)
        strict = acquisition_strict(
            lambda _active, probe_name, *, _name=name, _sat=saturated: (
                probe_name == _name and _sat
            ),
            ACTIVE_FAMILY,
            name,
        )
        discharge = xi_contraction_discharge(C, L_OWNED, D, candidate, KLLDAGGER_SPAN)
        saturated_results.append(
            AcquisitionCandidateResult(
                name=name,
                saturated=saturated,
                acquisition_strict=strict,
                conditional_currency=conditionalCurrencyDM_L(
                    C, L_OWNED, D, candidate, KLLDAGGER_SPAN
                ),
                discharge=discharge,
                cost=cost,
                ratio=F(0) if cost == 0 else discharge / cost,
            )
        )

    for name, candidate, witness, cost in STRICT_CANDIDATES:
        saturated = is_same_family_saturated(C, L_OWNED, D, candidate, KLLDAGGER_SPAN, witness)
        strict = acquisition_strict(
            lambda _active, probe_name, *, _name=name, _sat=saturated: (
                probe_name == _name and _sat
            ),
            ACTIVE_FAMILY,
            name,
        )
        discharge = xi_contraction_discharge(
            C, L_OWNED, D, candidate, KLLDAGGER_SPAN, KMMLDAGGER_ONE
        )
        strict_results.append(
            AcquisitionCandidateResult(
                name=name,
                saturated=saturated,
                acquisition_strict=strict,
                conditional_currency=conditionalCurrencyDM_L(
                    C, L_OWNED, D, candidate, KLLDAGGER_SPAN
                ),
                discharge=discharge,
                cost=cost,
                ratio=discharge / cost,
            )
        )

    return tuple(saturated_results), tuple(strict_results)


def _joint_budget_sweep(
    strict_candidates: tuple[AcquisitionCandidateResult, ...],
) -> dict[Fraction, JointBudgetResult]:
    results: dict[Fraction, JointBudgetResult] = {}
    acquisition_options: tuple[AcquisitionCandidateResult | None, ...] = (None, *strict_candidates)
    for budget in (F(0), F(1), F(2), F(3), F(4)):
        best: tuple[Fraction, tuple[Fraction, Fraction], AcquisitionCandidateResult | None] | None = None
        for weight in grid_weights(budget):
            allocation_cost = weight[0] + weight[1]
            for acquisition in acquisition_options:
                acquisition_cost = F(0) if acquisition is None else acquisition.cost
                if allocation_cost + acquisition_cost > budget:
                    continue
                total_discharge = allocation_discharge(weight) + (
                    F(0) if acquisition is None else acquisition.discharge
                )
                candidate = (total_discharge, weight, acquisition)
                if best is None or _joint_choice_key(candidate) > _joint_choice_key(best):
                    best = candidate
        if best is None:
            raise ValueError(f"no joint choice found for budget {budget}")
        total_discharge, weight, acquisition = best
        results[budget] = JointBudgetResult(
            budget=budget,
            allocation=weight,
            acquisitions=() if acquisition is None else (acquisition.name,),
            total_discharge=total_discharge,
            allocation_degraded=weight != (F(2), F(1)),
            acquisition_active=acquisition is not None,
        )
    return results


def _joint_choice_key(
    choice: tuple[Fraction, tuple[Fraction, Fraction], AcquisitionCandidateResult | None]
) -> tuple[Fraction, Fraction, str]:
    discharge, weight, acquisition = choice
    acquisition_name = "" if acquisition is None else acquisition.name
    # Prefer lower spend and lexicographically earlier acquisition names only as
    # deterministic tie-breakers after exact discharge.
    spend = weight[0] + weight[1] + (F(0) if acquisition is None else acquisition.cost)
    return (discharge, -spend, acquisition_name)


def _matrix_to_float_array(matrix_value: Mat) -> np.ndarray:
    return np.array([[float(entry) for entry in row] for row in matrix_value], dtype=float)


def _top_salience(label: str, target: Mat) -> SalienceResult:
    np.random.seed(SALIENCE_SEED)
    residual = residual_matrix((F(2), F(1)), target)
    eigenvalues, eigenvectors = np.linalg.eigh(_matrix_to_float_array(residual))
    top_index = int(np.argmax(eigenvalues))
    top_vector = eigenvectors[:, top_index]
    coordinate_index = int(np.argmax(np.abs(top_vector)))
    direction = ("A", "B", "C")[coordinate_index]
    top_magnitude = Fraction(str(round(float(eigenvalues[top_index]), 12)))
    return SalienceResult(
        label=label,
        residual=residual,
        top_direction=direction,
        top_magnitude=top_magnitude,
        eigenvalues=tuple(float(value) for value in eigenvalues),
        top_eigenvector=tuple(float(value) for value in top_vector),
    )


def _fraction_to_json(value: Fraction) -> str:
    return str(value)


def _matrix_to_json(matrix_value: Mat) -> list[list[str]]:
    return [[_fraction_to_json(entry) for entry in row] for row in matrix_value]


def _salience_hashes(base: SalienceResult, shift_b: SalienceResult) -> tuple[str, str]:
    config = {
        "seed": SALIENCE_SEED,
        "C": _matrix_to_json(C),
        "L_owned": _matrix_to_json(L_OWNED),
        "D": _matrix_to_json(D),
        "D_shift_B": _matrix_to_json(D_SHIFT_B),
        "full_allocation": ["2", "1"],
        "Omega": _matrix_to_json(zeroMat(3, 3)),
    }
    output = {
        "base": {
            "direction": base.top_direction,
            "magnitude": str(base.top_magnitude),
            "residual": _matrix_to_json(base.residual),
        },
        "shift_b": {
            "direction": shift_b.top_direction,
            "magnitude": str(shift_b.top_magnitude),
            "residual": _matrix_to_json(shift_b.residual),
        },
    }
    config_hash = hashlib.sha256(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    output_hash = hashlib.sha256(
        json.dumps(output, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return config_hash, output_hash


def _proxy_discharge_by_budget() -> dict[Fraction, Fraction]:
    proxy = (F(0), F(1))
    return {budget: allocation_discharge(proxy) for budget in (F(1), F(2), F(3), F(4))}


def run_probe_shop_sweep() -> SweepResults:
    base_residual, base_saturated, base_strict = _base_sanity()
    allocation_optima = {
        budget: allocation_argmax(budget) for budget in (F(1), F(2), F(3), F(4))
    }
    finite_differences = _finite_difference_rows(allocation_optima)
    saturated_candidates, strict_candidates = _catalog_results()
    joint_budget = _joint_budget_sweep(strict_candidates)
    salience_base = _top_salience("base", D)
    salience_shift_b = _top_salience("shift_B", D_SHIFT_B)
    salience_config_hash, salience_output_hash = _salience_hashes(
        salience_base, salience_shift_b
    )
    results = SweepResults(
        base_residual=base_residual,
        base_saturated=base_saturated,
        base_strict=base_strict,
        allocation_optima=allocation_optima,
        finite_differences=finite_differences,
        allocation_closed_form_ok=_allocation_closed_form_ok(),
        allocation_increment_floor=_allocation_increment_floor(),
        saturated_candidates=saturated_candidates,
        strict_candidates=strict_candidates,
        joint_budget=joint_budget,
        slack_allocation=allocation_optima[F(4)],
        proxy_discharge_by_budget=_proxy_discharge_by_budget(),
        proxy_residual_trace=residual_trace((F(0), F(1))),
        salience_base=salience_base,
        salience_shift_b=salience_shift_b,
        salience_config_hash=salience_config_hash,
        salience_output_hash=salience_output_hash,
        comparisons=(),
    )
    return SweepResults(**{**results.__dict__, "comparisons": _comparisons(results)})


def _comparisons(results: SweepResults) -> tuple[Comparison, ...]:
    comparisons = [
        Comparison(
            "base adequacy residual",
            results.base_residual == mat([["1/3"]]),
            _format_matrix(results.base_residual),
            "[[1/3]]",
        ),
        Comparison(
            "base same-family candidates saturated with zero conditional currency",
            all(
                item.saturated and item.conditional_currency == zeroMat(1, 1)
                for item in results.base_saturated
            ),
            ", ".join(
                f"{item.name}: saturated={item.saturated}, DM={_format_matrix(item.conditional_currency)}"
                for item in results.base_saturated
            ),
            "all saturated with DM=[[0]]",
        ),
        Comparison(
            "base strict candidates discharge 1/3 and are not saturated",
            all(
                item.discharge == F(1, 3) and not item.saturated
                for item in results.base_strict
            ),
            ", ".join(
                f"{item.name}: saturated={item.saturated}, discharge={_fmt(item.discharge)}"
                for item in results.base_strict
            ),
            "all not saturated, discharge=1/3",
        ),
        Comparison(
            "allocation xi residual matches closed form over registered grid",
            results.allocation_closed_form_ok,
            str(results.allocation_closed_form_ok),
            "True",
        ),
        Comparison(
            "allocation argmax weights and exact ratios",
            all(
                results.allocation_optima[budget].weight == expected_weight
                and results.allocation_optima[budget].marginal_ratios
                == (expected_ratio, expected_ratio)
                for budget, expected_weight, expected_ratio in (
                    (F(1), (F(4, 5), F(1, 5)), F(25, 9)),
                    (F(2), (F(7, 5), F(3, 5)), F(25, 16)),
                    (F(3), (F(2), F(1)), F(1)),
                )
            ),
            _allocation_summary(results.allocation_optima),
            "B=1:(4/5,1/5),25/9; B=2:(7/5,3/5),25/16; B=3:(2,1),1",
        ),
        Comparison(
            "finite-difference delta=1/20 registered table",
            _finite_delta_registered_ok(results.finite_differences),
            _finite_delta_summary(results.finite_differences, F(1, 20)),
            "B=1:100/37,8/3,4/111; B=2:75/49,50/33,25/1617; "
            "B=3:60/59,40/39,20/2301",
        ),
        Comparison(
            "finite-difference spreads shrink as delta refines",
            _finite_spreads_shrink(results.finite_differences),
            _finite_spread_sequence_summary(results.finite_differences),
            "spread(1/5) > spread(1/10) > spread(1/20) for B=1,2,3",
        ),
        Comparison(
            "slack collapse at B_alloc=4",
            results.slack_allocation.weight == (F(2), F(1))
            and results.slack_allocation.discharge == F(8),
            f"weight={_fmt_weight(results.slack_allocation.weight)}, "
            f"discharge={_fmt(results.slack_allocation.discharge)}",
            "weight=(2,1), discharge=8, marginal floor=0",
        ),
        Comparison(
            "same-family acquisition candidates excluded",
            all(
                item.saturated and not item.acquisition_strict and item.discharge == 0
                for item in results.saturated_candidates
            ),
            _candidate_summary(results.saturated_candidates),
            "all saturated, not strict, discharge=0",
        ),
        Comparison(
            "strict acquisition candidates frontier",
            tuple((item.name, item.discharge, item.ratio) for item in results.strict_candidates)
            == (("C", F(1, 4), F(1, 4)), ("AC", F(1, 4), F(1, 8)), ("BC", F(1, 4), F(1, 16))),
            _candidate_summary(results.strict_candidates),
            "C:1/4 > AC:1/8 > BC:1/16 with discharge=1/4 each",
        ),
        Comparison(
            "allocation increment floor before cap",
            results.allocation_increment_floor == F(15, 14),
            _fmt(results.allocation_increment_floor),
            "15/14",
        ),
        Comparison(
            "joint arbitration ordering",
            results.joint_budget[F(4)].acquisitions == ("C",)
            and not results.joint_budget[F(3)].acquisition_active
            and not results.joint_budget[F(3)].allocation_degraded
            and all(results.joint_budget[b].allocation_degraded for b in (F(0), F(1), F(2))),
            _joint_summary(results.joint_budget),
            "acquisition active only at B=4; halts at B=3; allocation degrades only below B=3",
        ),
        Comparison(
            "proxy exact discharge and residual trace",
            results.proxy_discharge_by_budget
            == {F(1): F(2), F(2): F(2), F(3): F(2), F(4): F(2)}
            and results.allocation_optima[F(1)].discharge == F(14, 3)
            and results.allocation_optima[F(2)].discharge == F(27, 4)
            and results.allocation_optima[F(3)].discharge == F(8)
            and results.allocation_optima[F(4)].discharge == F(8)
            and results.allocation_optima[F(3)].residual_trace == F(21, 4)
            and results.proxy_residual_trace == F(45, 4),
            _proxy_summary(results),
            "KKT discharge 14/3->27/4->8->8; proxy discharge=2; "
            "B=3 residuals 21/4 vs 45/4",
        ),
        Comparison(
            "salience direction and magnitude",
            results.salience_base.top_direction == "A"
            and results.salience_base.top_magnitude == F(3)
            and results.salience_shift_b.top_direction == "B"
            and results.salience_shift_b.top_magnitude == F(8),
            f"base={results.salience_base.top_direction}:{_fmt(results.salience_base.top_magnitude)}, "
            f"shift_B={results.salience_shift_b.top_direction}:{_fmt(results.salience_shift_b.top_magnitude)}",
            "base A:3, shift_B B:8",
        ),
    ]
    return tuple(comparisons)


def _finite_delta_registered_ok(rows: Iterable[FiniteDifferenceRow]) -> bool:
    expected = {
        F(1): (F(100, 37), F(8, 3), F(4, 111)),
        F(2): (F(75, 49), F(50, 33), F(25, 1617)),
        F(3): (F(60, 59), F(40, 39), F(20, 2301)),
    }
    observed = {
        row.budget: (row.ratio_a, row.ratio_b, row.spread)
        for row in rows
        if row.delta == F(1, 20)
    }
    return observed == expected


def _finite_spreads_shrink(rows: Iterable[FiniteDifferenceRow]) -> bool:
    by_budget: dict[Fraction, dict[Fraction, Fraction]] = {}
    for row in rows:
        by_budget.setdefault(row.budget, {})[row.delta] = row.spread
    return all(
        spreads[F(1, 5)] > spreads[F(1, 10)] > spreads[F(1, 20)]
        for spreads in by_budget.values()
    )


def _fmt(value: Fraction) -> str:
    return str(value)


def _fmt_weight(weight: tuple[Fraction, Fraction]) -> str:
    return f"({_fmt(weight[0])},{_fmt(weight[1])})"


def _format_matrix(matrix_value: Mat) -> str:
    return "[" + ", ".join("[" + ", ".join(_fmt(entry) for entry in row) + "]" for row in matrix_value) + "]"


def _allocation_summary(optima: dict[Fraction, AllocationOptimum]) -> str:
    return "; ".join(
        f"B={_fmt(budget)}: w={_fmt_weight(optimum.weight)}, "
        f"discharge={_fmt(optimum.discharge)}, ratios=({_fmt(optimum.marginal_ratios[0])},"
        f"{_fmt(optimum.marginal_ratios[1])})"
        for budget, optimum in sorted(optima.items())
    )


def _finite_delta_summary(rows: Iterable[FiniteDifferenceRow], delta: Fraction) -> str:
    return "; ".join(
        f"B={_fmt(row.budget)}: A={_fmt(row.ratio_a)}, B={_fmt(row.ratio_b)}, "
        f"spread={_fmt(row.spread)}"
        for row in rows
        if row.delta == delta
    )


def _finite_spread_sequence_summary(rows: Iterable[FiniteDifferenceRow]) -> str:
    by_budget: dict[Fraction, list[FiniteDifferenceRow]] = {}
    for row in rows:
        by_budget.setdefault(row.budget, []).append(row)
    parts: list[str] = []
    for budget in sorted(by_budget):
        ordered = sorted(by_budget[budget], key=lambda row: row.delta, reverse=True)
        parts.append(
            f"B={_fmt(budget)}: "
            + " > ".join(_fmt(row.spread) for row in ordered)
        )
    return "; ".join(parts)


def _candidate_summary(candidates: Iterable[AcquisitionCandidateResult]) -> str:
    return "; ".join(
        f"{item.name}: saturated={item.saturated}, strict={item.acquisition_strict}, "
        f"DM={_format_matrix(item.conditional_currency)}, discharge={_fmt(item.discharge)}, "
        f"ratio={_fmt(item.ratio)}"
        for item in candidates
    )


def _joint_summary(joint: dict[Fraction, JointBudgetResult]) -> str:
    return "; ".join(
        f"B={_fmt(budget)}: alloc={_fmt_weight(result.allocation)}, "
        f"acq={','.join(result.acquisitions) if result.acquisitions else 'none'}, "
        f"total={_fmt(result.total_discharge)}"
        for budget, result in sorted(joint.items())
    )


def _proxy_summary(results: SweepResults) -> str:
    proxy = ", ".join(
        f"B={_fmt(budget)}:{_fmt(value)}"
        for budget, value in sorted(results.proxy_discharge_by_budget.items())
    )
    return (
        f"KKT={_allocation_summary(results.allocation_optima)}; "
        f"proxy={proxy}; proxy_residual={_fmt(results.proxy_residual_trace)}"
    )


def results_markdown(results: SweepResults) -> str:
    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    lines = [
        "# E6+E9 Probe-Shop Sweep Results",
        "",
        "Generated by `sixbirds_foundations_v.sweeps.e6_e9_probe_shop` against "
        "`formalization/notes/sweeps/E6_E9_probe_shop_predictions.md`.",
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
            "## Salience Reproducibility",
            "",
            f"- seed: `{SALIENCE_SEED}`",
            f"- config hash: `{results.salience_config_hash}`",
            f"- output hash: `{results.salience_output_hash}`",
            f"- base eigenvalues: `{tuple(round(value, 12) for value in results.salience_base.eigenvalues)}`",
            f"- base top eigenvector: `{tuple(round(value, 12) for value in results.salience_base.top_eigenvector)}`",
            f"- shifted eigenvalues: `{tuple(round(value, 12) for value in results.salience_shift_b.eigenvalues)}`",
            f"- shifted top eigenvector: `{tuple(round(value, 12) for value in results.salience_shift_b.top_eigenvector)}`",
            "",
            "## Notes",
            "",
            "- Exact arithmetic uses `fractions.Fraction` throughout, except the registered "
            "salience eigen branch.",
            "- Allocation residuals are computed with `adequacyResidual`; the closed form is "
            "checked only as an internal consistency condition.",
            "- Acquisition strictness and same-family saturation use the xi "
            "`is_same_family_saturated` checker.",
            "",
        ]
    )
    return "\n".join(lines)


def write_results_report(path: Path = DEFAULT_RESULTS_PATH) -> SweepResults:
    results = run_probe_shop_sweep()
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

