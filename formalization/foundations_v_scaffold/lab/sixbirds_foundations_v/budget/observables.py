from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel

from sixbirds_foundations_v._recombination_support.benchmarks.loader import LoadedBenchmark
from sixbirds_foundations_v._recombination_support.core.observables import RecombinationObservableFamily, build_observable_family


class ObservableBudgetCostMode(str, Enum):
    STRUCTURAL_OBSERVABLE_ADMISSIBILITY_COST = "structural_observable_admissibility_cost"
    PROXY_UNIFORM_OBSERVABLE_STEP_COST = "proxy_uniform_observable_step_cost"


class ObservableBudgetFamily(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-observable-budget-family.v1"
    observable_budget_family_id: str
    benchmark_id: str
    config_id: str
    cost_mode: ObservableBudgetCostMode
    observable_budget_level: float
    observable_ids_in_family: list[str]
    observable_costs_by_id: dict[str, float]
    prefix_index: int
    total_observable_count: int
    notes: list[str] = Field(default_factory=list)


class ObservableBudgetBenchmarkView(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-observable-budget-view.v1"
    observable_budget_family_id: str
    cost_mode: ObservableBudgetCostMode | None = None
    observable_budget_level: float | None = None
    benchmark: LoadedBenchmark
    observable_ids_in_family: list[str]
    observable_costs_by_id: dict[str, float]
    warnings: list[str] = Field(default_factory=list)


def list_supported_observable_cost_modes() -> list[str]:
    return [mode.value for mode in ObservableBudgetCostMode]


def derive_observable_budget_families(
    benchmark: LoadedBenchmark,
    *,
    cost_mode: str | ObservableBudgetCostMode,
) -> list[ObservableBudgetFamily]:
    resolved_cost_mode = ObservableBudgetCostMode(cost_mode)
    observable_family = benchmark.observable_family
    if observable_family is None:
        return []
    cost_by_id = {
        observable.observable_id: _observable_cost(observable, resolved_cost_mode)
        for observable in observable_family.observables
    }
    ordered_observables = sorted(
        observable_family.observables,
        key=lambda observable: (
            cost_by_id[observable.observable_id],
            observable.kind.value,
            observable.observable_id,
        ),
    )
    cumulative_cost = 0.0
    families: list[ObservableBudgetFamily] = []
    for index, observable in enumerate(ordered_observables, start=1):
        cumulative_cost += cost_by_id[observable.observable_id]
        included = ordered_observables[:index]
        families.append(
            ObservableBudgetFamily(
                observable_budget_family_id=(
                    f"{benchmark.config_id}.{resolved_cost_mode.value}.prefix_{index}"
                ),
                benchmark_id=benchmark.benchmark_id or benchmark.config_id,
                config_id=benchmark.config_id,
                cost_mode=resolved_cost_mode,
                observable_budget_level=float(cumulative_cost),
                observable_ids_in_family=[item.observable_id for item in included],
                observable_costs_by_id={
                    item.observable_id: cost_by_id[item.observable_id]
                    for item in ordered_observables
                },
                prefix_index=index,
                total_observable_count=len(ordered_observables),
                notes=[
                    "derived as an ascending admissible prefix of the benchmark observable family",
                ],
            )
        )
    return families


def build_observable_budget_benchmark_view(
    benchmark: LoadedBenchmark,
    observable_budget_family_id: str,
    observable_family_override: RecombinationObservableFamily,
    *,
    cost_mode: str | ObservableBudgetCostMode | None = None,
    observable_budget_level: float | None = None,
    observable_ids_in_family: list[str] | None = None,
    observable_costs_by_id: dict[str, float] | None = None,
) -> ObservableBudgetBenchmarkView:
    derived = benchmark.model_copy(
        deep=False,
        update={
            "observable_family_id": observable_budget_family_id,
            "notes": [
                *benchmark.notes,
                f"observable budget override applied: {observable_budget_family_id}",
            ],
        },
    )
    derived._observable_family = observable_family_override
    derived._runtime_package = benchmark.runtime_package
    derived._context = benchmark.context
    derived._assemblages = benchmark.assemblages
    derived._relative_cycle_case = getattr(benchmark, "_relative_cycle_case", None)
    return ObservableBudgetBenchmarkView(
        observable_budget_family_id=observable_budget_family_id,
        cost_mode=ObservableBudgetCostMode(cost_mode) if cost_mode is not None else None,
        observable_budget_level=observable_budget_level,
        benchmark=derived,
        observable_ids_in_family=list(observable_ids_in_family or []),
        observable_costs_by_id=dict(observable_costs_by_id or {}),
    )


def build_observable_family_prefix(
    benchmark: LoadedBenchmark,
    family: ObservableBudgetFamily,
) -> RecombinationObservableFamily:
    observable_family = benchmark.observable_family
    if observable_family is None:
        raise ValueError("benchmark does not expose an observable family")
    selected_observables = [
        observable
        for observable in observable_family.observables
        if observable.observable_id in set(family.observable_ids_in_family)
    ]
    selected_observables = sorted(selected_observables, key=lambda item: item.observable_id)
    if not selected_observables:
        raise ValueError("observable budget family must retain at least one observable")
    return build_observable_family(
        family.observable_budget_family_id,
        observable_family.interface_id,
        selected_observables,
    )


def _observable_cost(observable: Any, cost_mode: ObservableBudgetCostMode) -> float:
    if cost_mode is ObservableBudgetCostMode.PROXY_UNIFORM_OBSERVABLE_STEP_COST:
        return 1.0
    base = 1.0 if observable.kind.value == "branchwise_mixing" else 2.0
    return float(base + max(0, len(observable.event_ids) - 2))


__all__ = [
    "ObservableBudgetBenchmarkView",
    "ObservableBudgetCostMode",
    "ObservableBudgetFamily",
    "build_observable_budget_benchmark_view",
    "build_observable_family_prefix",
    "derive_observable_budget_families",
    "list_supported_observable_cost_modes",
]
