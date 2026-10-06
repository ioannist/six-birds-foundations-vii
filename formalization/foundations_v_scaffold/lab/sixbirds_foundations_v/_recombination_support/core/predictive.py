from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sixbirds_foundations_v._holonomy_support.analysis import (
    DiscrepancyMetricResult,
    InterfacePartition,
    compute_current_loop_action,
    compute_current_partition,
    compute_exact_max_abs_future_gap,
    compute_predictive_loop_action,
    compute_predictive_partition,
    enumerate_memory_witnesses,
    predictive_refines_current,
    resolve_interface_history_ids,
)

from .substrate import InheritedBenchmarkContext


@dataclass(frozen=True)
class InheritedInterfaceAnalysis:
    benchmark_id: str
    interface_id: str
    history_ids: tuple[str, ...]
    history_count: int
    current_partition: InterfacePartition
    current_quotient_size: int
    predictive_partition: InterfacePartition
    predictive_quotient_size: int
    witness_count: int
    max_fiber_size: int
    discrepancy_result: DiscrepancyMetricResult
    exact_max_abs_future_gap: Fraction
    loop_action_score_current: Fraction
    loop_action_score_predictive: Fraction
    current_loop_is_trivial: bool | None
    predictive_loop_is_nontrivial: bool | None
    applicable_loop_ids: tuple[str, ...]
    predictive_refines_current: bool


def analyze_inherited_interface(
    context: InheritedBenchmarkContext,
    interface_id: str,
) -> InheritedInterfaceAnalysis:
    package = context.runtime_package
    history_ids = resolve_interface_history_ids(package, interface_id)
    current_partition = compute_current_partition(package, interface_id, history_ids)
    predictive_partition = compute_predictive_partition(package, interface_id, history_ids)
    witnesses = enumerate_memory_witnesses(package, interface_id, history_ids)
    discrepancy = compute_exact_max_abs_future_gap(package, interface_id, history_ids)
    loop_scores = _compute_loop_scores(context, interface_id, history_ids)
    return InheritedInterfaceAnalysis(
        benchmark_id=context.benchmark_id,
        interface_id=interface_id,
        history_ids=history_ids,
        history_count=len(history_ids),
        current_partition=current_partition,
        current_quotient_size=current_partition.class_count,
        predictive_partition=predictive_partition,
        predictive_quotient_size=predictive_partition.class_count,
        witness_count=len(witnesses),
        max_fiber_size=_compute_max_fiber_size(current_partition, predictive_partition),
        discrepancy_result=discrepancy,
        exact_max_abs_future_gap=discrepancy.metric_value,
        loop_action_score_current=loop_scores[0],
        loop_action_score_predictive=loop_scores[1],
        current_loop_is_trivial=loop_scores[2],
        predictive_loop_is_nontrivial=loop_scores[3],
        applicable_loop_ids=loop_scores[4],
        predictive_refines_current=predictive_refines_current(
            current_partition,
            predictive_partition,
        ),
    )


def interface_analysis_payload(
    analysis: InheritedInterfaceAnalysis,
) -> dict[str, object]:
    return {
        "benchmark_id": analysis.benchmark_id,
        "interface_id": analysis.interface_id,
        "history_count": analysis.history_count,
        "current_quotient_size": analysis.current_quotient_size,
        "predictive_quotient_size": analysis.predictive_quotient_size,
        "witness_count": analysis.witness_count,
        "max_fiber_size": analysis.max_fiber_size,
        "discrepancy_metric_name": analysis.discrepancy_result.metric_name.value,
        "discrepancy_metric_value": float(analysis.exact_max_abs_future_gap),
        "loop_action_score_current_quotient": float(analysis.loop_action_score_current),
        "loop_action_score_predictive_quotient": float(
            analysis.loop_action_score_predictive
        ),
    }


def _compute_loop_scores(
    context: InheritedBenchmarkContext,
    interface_id: str,
    history_ids: tuple[str, ...],
) -> tuple[Fraction, Fraction, bool | None, bool | None, tuple[str, ...]]:
    package = context.runtime_package
    applicable_loop_ids = tuple(
        loop_id
        for loop_id in context.manifest.loops_to_test
        if package.get_loop(loop_id).interface_id == interface_id
    )
    if not applicable_loop_ids:
        return Fraction(0, 1), Fraction(0, 1), None, None, ()

    current_actions = tuple(
        compute_current_loop_action(package, loop_id, history_ids)
        for loop_id in applicable_loop_ids
    )
    predictive_actions = tuple(
        compute_predictive_loop_action(package, loop_id, history_ids)
        for loop_id in applicable_loop_ids
    )
    return (
        max(
            (action.moved_class_fraction for action in current_actions),
            default=Fraction(0, 1),
        ),
        max(
            (action.moved_class_fraction for action in predictive_actions),
            default=Fraction(0, 1),
        ),
        all(action.is_trivial for action in current_actions),
        any(not action.is_trivial for action in predictive_actions),
        applicable_loop_ids,
    )


def _compute_max_fiber_size(
    current_partition: InterfacePartition,
    predictive_partition: InterfacePartition,
) -> int:
    max_fiber_size = 0
    for current_class in current_partition.classes:
        predictive_class_ids = {
            predictive_partition.history_to_class_id[history_id]
            for history_id in current_class.member_history_ids
        }
        max_fiber_size = max(max_fiber_size, len(predictive_class_ids))
    return max_fiber_size


__all__ = [
    "InheritedInterfaceAnalysis",
    "analyze_inherited_interface",
    "interface_analysis_payload",
]
