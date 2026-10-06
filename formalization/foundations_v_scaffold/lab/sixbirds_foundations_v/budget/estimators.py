from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel


class ShadowPriceStatus(str, Enum):
    OK = "ok"
    NOT_ENOUGH_DATA = "not_enough_data"
    UNSUPPORTED = "unsupported"
    ERROR = "error"


class ShadowPriceEstimate(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-shadow-price-estimate.v1"
    benchmark_id: str
    slice_id: str
    source_kind: str | None = None
    cost_mode: str
    estimator_id: str
    target_yield_term: str
    budget_interval_or_level: str
    status: ShadowPriceStatus
    value: float | None = None
    assumptions: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


FINITE_DIFFERENCE_ESTIMATOR = "frontier_finite_difference_price"
OBSERVABLE_BUDGET_BOUNDARY_ESTIMATOR = "observable_budget_boundary_finite_difference_price"


def list_supported_estimators() -> list[str]:
    return [FINITE_DIFFERENCE_ESTIMATOR, OBSERVABLE_BUDGET_BOUNDARY_ESTIMATOR]


def estimate_shadow_prices(
    sweep_rows: list[dict[str, Any]],
    *,
    estimator_id: str,
    target_yield_term: str,
) -> list[ShadowPriceEstimate]:
    if estimator_id == OBSERVABLE_BUDGET_BOUNDARY_ESTIMATOR:
        return _estimate_observable_budget_boundary_prices(
            sweep_rows=sweep_rows,
            estimator_id=estimator_id,
            target_yield_term=target_yield_term,
        )
    if estimator_id != FINITE_DIFFERENCE_ESTIMATOR:
        benchmark_id = sweep_rows[0]["benchmark_id"] if sweep_rows else "unknown"
        slice_id = sweep_rows[0]["slice_id"] if sweep_rows else "unknown"
        return [
                ShadowPriceEstimate(
                    benchmark_id=benchmark_id,
                    slice_id=slice_id,
                    source_kind=None,
                    cost_mode="unknown",
                    estimator_id=estimator_id,
                target_yield_term=target_yield_term,
                budget_interval_or_level="none",
                status=ShadowPriceStatus.UNSUPPORTED,
                assumptions=["only frontier_finite_difference_price is implemented at current scope"],
                warnings=[f"unsupported estimator {estimator_id!r}"],
            )
        ]

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in sweep_rows:
        key = (row["benchmark_id"], row["slice_id"], row["cost_mode"])
        grouped.setdefault(key, []).append(row)

    estimates: list[ShadowPriceEstimate] = []
    for (benchmark_id, slice_id, cost_mode), rows in sorted(grouped.items()):
        best_yield_by_budget: dict[float, dict[str, Any]] = {}
        for row in rows:
            budget_level = float(row["budget_level"])
            if not row.get("frontier_member_flag"):
                continue
            if row.get("feasibility_status") != "feasible":
                continue
            value = row.get("yield_vector", {}).get(target_yield_term)
            if value is None:
                continue
            current = best_yield_by_budget.get(budget_level)
            if current is None or float(value) > float(current["value"]):
                best_yield_by_budget[budget_level] = {
                    "value": float(value),
                    "candidate_id": row["candidate_id"],
                }
        ordered_levels = sorted(best_yield_by_budget)
        if len(ordered_levels) < 2:
            estimates.append(
                ShadowPriceEstimate(
                    benchmark_id=benchmark_id,
                    slice_id=slice_id,
                    source_kind=None,
                    cost_mode=cost_mode,
                    estimator_id=estimator_id,
                    target_yield_term=target_yield_term,
                    budget_interval_or_level="insufficient_levels",
                    status=ShadowPriceStatus.NOT_ENOUGH_DATA,
                    assumptions=[
                        "finite-difference price needs at least two budget levels with frontier yield support",
                    ],
                    details={"supported_budget_levels": ordered_levels},
                )
            )
            continue
        for lower, upper in zip(ordered_levels, ordered_levels[1:]):
            lower_payload = best_yield_by_budget[lower]
            upper_payload = best_yield_by_budget[upper]
            delta_budget = upper - lower
            delta_yield = upper_payload["value"] - lower_payload["value"]
            value = delta_yield / delta_budget if delta_budget else None
            estimates.append(
                ShadowPriceEstimate(
                    benchmark_id=benchmark_id,
                    slice_id=slice_id,
                    source_kind=str(upper_payload["candidate_id"]),
                    cost_mode=cost_mode,
                    estimator_id=estimator_id,
                    target_yield_term=target_yield_term,
                    budget_interval_or_level=f"{lower}->{upper}",
                    status=ShadowPriceStatus.OK if value is not None else ShadowPriceStatus.ERROR,
                    value=value,
                    assumptions=[
                        "shadow price is the marginal frontier-yield change across adjacent budget levels",
                        "the current demo uses a single-yield frozen slice so the finite difference is unambiguous",
                    ],
                    details={
                        "delta_budget": delta_budget,
                        "delta_yield": delta_yield,
                        "lower_frontier_candidate_id": lower_payload["candidate_id"],
                        "upper_frontier_candidate_id": upper_payload["candidate_id"],
                    },
                )
            )
    return estimates


def _estimate_observable_budget_boundary_prices(
    *,
    sweep_rows: list[dict[str, Any]],
    estimator_id: str,
    target_yield_term: str,
) -> list[ShadowPriceEstimate]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in sweep_rows:
        key = (
            row["benchmark_id"],
            row.get("source_kind", "unknown"),
            row["cost_mode"],
        )
        grouped.setdefault(key, []).append(row)

    estimates: list[ShadowPriceEstimate] = []
    for (benchmark_id, source_kind, cost_mode), rows in sorted(grouped.items()):
        best_by_level: dict[float, dict[str, Any]] = {}
        for row in rows:
            metric_result = row.get("metric_results", {}).get(target_yield_term)
            if metric_result is None or metric_result.get("status") != "ok":
                continue
            level = float(row["observable_budget_level"])
            value = float(metric_result["value"])
            current = best_by_level.get(level)
            if current is None or value > current["value"]:
                best_by_level[level] = {
                    "value": value,
                    "family_id": row["observable_budget_family_id"],
                    "rk_separation_present": bool(row.get("rk_separation_present")),
                }
        ordered_levels = sorted(best_by_level)
        if len(ordered_levels) < 2:
            estimates.append(
                ShadowPriceEstimate(
                    benchmark_id=benchmark_id,
                    slice_id="observable_budget_boundary",
                    source_kind=source_kind,
                    cost_mode=cost_mode,
                    estimator_id=estimator_id,
                    target_yield_term=target_yield_term,
                    budget_interval_or_level="insufficient_levels",
                    status=ShadowPriceStatus.NOT_ENOUGH_DATA,
                    assumptions=[
                        "observable-budget boundary price needs at least two admissible family levels with supported recombination-gap values",
                    ],
                    details={"supported_budget_levels": ordered_levels},
                )
            )
            continue
        for lower, upper in zip(ordered_levels, ordered_levels[1:]):
            lower_payload = best_by_level[lower]
            upper_payload = best_by_level[upper]
            delta_budget = upper - lower
            delta_yield = upper_payload["value"] - lower_payload["value"]
            value = delta_yield / delta_budget if delta_budget else None
            estimates.append(
                ShadowPriceEstimate(
                    benchmark_id=benchmark_id,
                    slice_id="observable_budget_boundary",
                    source_kind=source_kind,
                    cost_mode=cost_mode,
                    estimator_id=estimator_id,
                    target_yield_term=target_yield_term,
                    budget_interval_or_level=f"{lower}->{upper}",
                    status=ShadowPriceStatus.OK if value is not None else ShadowPriceStatus.ERROR,
                    value=value,
                    assumptions=[
                        "shadow price is the marginal recombination-gap change across adjacent observable-budget levels",
                        "observable-budget families are deterministic admissible prefixes of the benchmark observable family",
                    ],
                    details={
                        "delta_budget": delta_budget,
                        "delta_yield": delta_yield,
                        "lower_family_id": lower_payload["family_id"],
                        "upper_family_id": upper_payload["family_id"],
                        "lower_rk_separation_present": lower_payload["rk_separation_present"],
                        "upper_rk_separation_present": upper_payload["rk_separation_present"],
                    },
                )
            )
    return estimates


__all__ = [
    "FINITE_DIFFERENCE_ESTIMATOR",
    "OBSERVABLE_BUDGET_BOUNDARY_ESTIMATOR",
    "ShadowPriceEstimate",
    "ShadowPriceStatus",
    "estimate_shadow_prices",
    "list_supported_estimators",
]
