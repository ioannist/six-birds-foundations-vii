from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from sixbirds_foundations_v._recombination_support.metrics.registry import METRIC_REGISTRY
from sixbirds_foundations_v._recombination_support.schemas import FrozenSliceConfig

from .models import (
    CandidateMetricStatus,
    CandidateObservationLedger,
    CandidateObservationRow,
    ConeTransferSummary,
    FrontierComparisonStatus,
    FrontierEvaluationResult,
    FrontierResultRow,
    FrontierTermAggregate,
)
from .transfer import assign_cone_equivalence_classes


def load_candidate_observation_ledger(path: str | Path) -> CandidateObservationLedger:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return CandidateObservationLedger.model_validate(payload)


def evaluate_frozen_slice(
    slice_config: FrozenSliceConfig,
    ledger: CandidateObservationLedger,
) -> FrontierEvaluationResult:
    support_rows = [row for row in ledger.rows if _row_in_support_cone(row, slice_config)]
    support_atom_ids = sorted({row.support_atom_id for row in support_rows})
    rows_by_candidate: dict[str, list[CandidateObservationRow]] = defaultdict(list)
    for row in support_rows:
        rows_by_candidate[row.candidate_id].append(row)

    result_rows: list[FrontierResultRow] = []
    for candidate_id in sorted(rows_by_candidate):
        candidate_rows = sorted(
            rows_by_candidate[candidate_id],
            key=lambda item: (item.support_atom_id, item.benchmark_id, item.source_kind),
        )
        result_rows.append(
            _evaluate_candidate(
                slice_config=slice_config,
                candidate_id=candidate_id,
                rows=candidate_rows,
                support_atom_ids=support_atom_ids,
            )
        )

    comparable_rows = [
        row for row in result_rows if row.comparison_status is FrontierComparisonStatus.COMPARABLE
    ]
    dominance = _compute_dominance(
        comparable_rows,
        comparison_tolerance=slice_config.comparison_tolerance or 0.0,
    )
    updated_rows = []
    for row in result_rows:
        dominates = sorted(dominance["dominates"].get(row.candidate_id, set()))
        dominated_by = sorted(dominance["dominated_by"].get(row.candidate_id, set()))
        updated_rows.append(
            row.model_copy(
                update={
                    "dominates": dominates,
                    "dominated_by": dominated_by,
                    "frontier_member": (
                        row.comparison_status is FrontierComparisonStatus.COMPARABLE
                        and not dominated_by
                    ),
                }
            )
        )
    result = FrontierEvaluationResult(
        slice_id=slice_config.slice_id,
        support_cone_id=slice_config.support_cone.support_cone_id,
        candidate_count=len(updated_rows),
        support_atom_count=len(support_atom_ids),
        rows=updated_rows,
        frontier_candidate_ids=sorted(
            [row.candidate_id for row in updated_rows if row.frontier_member]
        ),
        warnings=(
            ["no support rows matched the selected support cone"]
            if not support_rows
            else []
        ),
    )
    return assign_cone_equivalence_classes(
        result,
        tolerance=slice_config.cone_equivalence_tolerance or 0.0,
    )


def _evaluate_candidate(
    *,
    slice_config: FrozenSliceConfig,
    candidate_id: str,
    rows: list[CandidateObservationRow],
    support_atom_ids: list[str],
) -> FrontierResultRow:
    warnings: list[str] = []
    if not rows:
        return _excluded_row(
            slice_config=slice_config,
            candidate_id=candidate_id,
            status=FrontierComparisonStatus.EXCLUDED_NO_SUPPORT,
            warnings=["candidate has no rows on the selected support cone"],
        )

    present_support_atoms = {row.support_atom_id for row in rows}
    missing_support_atoms = [atom_id for atom_id in support_atom_ids if atom_id not in present_support_atoms]
    if missing_support_atoms:
        return _excluded_row(
            slice_config=slice_config,
            candidate_id=candidate_id,
            status=FrontierComparisonStatus.EXCLUDED_INCOMPLETE_SUPPORT,
            warnings=[f"candidate is missing support atoms {missing_support_atoms} on the cone"],
        )

    aggregated_yield_vector: dict[str, float] = {}
    aggregated_cost_vector: dict[str, float] = {}
    term_aggregates: dict[str, FrontierTermAggregate] = {}

    for direction, terms in (("yield", slice_config.yield_terms), ("cost", slice_config.cost_terms)):
        for term in terms:
            aggregate = _aggregate_term(term, rows, support_atom_ids=support_atom_ids, direction=direction)
            term_aggregates[term.metric_name] = aggregate
            if aggregate.aggregated_value is None and term.required:
                return _excluded_row(
                    slice_config=slice_config,
                    candidate_id=candidate_id,
                    status=FrontierComparisonStatus.EXCLUDED_MISSING_REQUIRED_TERM,
                    warnings=[
                        f"required term {term.metric_name} is missing or unsupported on the cone"
                    ],
                    term_aggregates=term_aggregates,
                )
            if aggregate.aggregated_value is None:
                warnings.append(
                    f"optional term {term.metric_name} was ignored because it had no supported values"
                )
                continue
            if direction == "yield":
                aggregated_yield_vector[term.metric_name] = aggregate.aggregated_value
            else:
                aggregated_cost_vector[term.metric_name] = aggregate.aggregated_value

    return FrontierResultRow(
        slice_id=slice_config.slice_id,
        candidate_id=candidate_id,
        support_cone_id=slice_config.support_cone.support_cone_id,
        comparison_status=FrontierComparisonStatus.COMPARABLE,
        aggregated_yield_vector=aggregated_yield_vector,
        aggregated_cost_vector=aggregated_cost_vector,
        term_aggregates=term_aggregates,
        transfer_summary=ConeTransferSummary(
            eligible=False,
            replacement_candidates=[],
            transfer_reason="cone-equivalence not computed yet",
        ),
        warnings=warnings,
        provenance={
            "support_atom_ids": support_atom_ids,
            "source_row_count": len(rows),
        },
    )


def _aggregate_term(
    term: Any,
    rows: list[CandidateObservationRow],
    *,
    support_atom_ids: list[str],
    direction: str,
) -> FrontierTermAggregate:
    supported_values: list[float] = []
    missing_support_atom_ids: list[str] = []
    unsupported_support_atom_ids: list[str] = []
    for support_atom_id in support_atom_ids:
        row = next(item for item in rows if item.support_atom_id == support_atom_id)
        metric = row.metric_results.get(term.metric_name)
        if metric is None:
            missing_support_atom_ids.append(support_atom_id)
            continue
        if metric.status is not CandidateMetricStatus.OK or metric.value is None:
            unsupported_support_atom_ids.append(support_atom_id)
            continue
        supported_values.append(float(metric.value))
    aggregated_value = None if not supported_values else _aggregate_values(supported_values, term.aggregation_op)
    return FrontierTermAggregate(
        metric_name=term.metric_name,
        direction=direction,
        aggregation_op=term.aggregation_op,
        required=term.required,
        weight=term.weight,
        aggregated_value=aggregated_value,
        support_atom_count=len(supported_values),
        missing_support_atom_ids=missing_support_atom_ids,
        unsupported_support_atom_ids=unsupported_support_atom_ids,
    )


def _aggregate_values(values: list[float], aggregation_op: str) -> float:
    if aggregation_op == "mean":
        return float(mean(values))
    if aggregation_op == "sum":
        return float(sum(values))
    if aggregation_op == "min":
        return float(min(values))
    if aggregation_op == "max":
        return float(max(values))
    raise ValueError(f"unsupported aggregation op {aggregation_op!r}")


def _compute_dominance(
    rows: list[FrontierResultRow],
    *,
    comparison_tolerance: float,
) -> dict[str, dict[str, set[str]]]:
    dominated_by: dict[str, set[str]] = defaultdict(set)
    dominates: dict[str, set[str]] = defaultdict(set)
    for left in rows:
        for right in rows:
            if left.candidate_id == right.candidate_id:
                continue
            if _dominates(left, right, tolerance=comparison_tolerance):
                dominates[left.candidate_id].add(right.candidate_id)
                dominated_by[right.candidate_id].add(left.candidate_id)
    return {"dominated_by": dominated_by, "dominates": dominates}


def _dominates(
    left: FrontierResultRow,
    right: FrontierResultRow,
    *,
    tolerance: float,
) -> bool:
    strictly_better = False
    all_term_names = sorted(
        set(left.aggregated_yield_vector)
        | set(left.aggregated_cost_vector)
        | set(right.aggregated_yield_vector)
        | set(right.aggregated_cost_vector)
    )
    if not all_term_names:
        return False
    for metric_name in all_term_names:
        if metric_name in left.aggregated_yield_vector or metric_name in right.aggregated_yield_vector:
            if metric_name not in left.aggregated_yield_vector or metric_name not in right.aggregated_yield_vector:
                return False
            left_value = left.aggregated_yield_vector[metric_name]
            right_value = right.aggregated_yield_vector[metric_name]
            if left_value + tolerance < right_value:
                return False
            if left_value > right_value + tolerance:
                strictly_better = True
            continue
        if metric_name not in left.aggregated_cost_vector or metric_name not in right.aggregated_cost_vector:
            return False
        left_value = left.aggregated_cost_vector[metric_name]
        right_value = right.aggregated_cost_vector[metric_name]
        if left_value > right_value + tolerance:
            return False
        if left_value + tolerance < right_value:
            strictly_better = True
    return strictly_better


def _excluded_row(
    *,
    slice_config: FrozenSliceConfig,
    candidate_id: str,
    status: FrontierComparisonStatus,
    warnings: list[str],
    term_aggregates: dict[str, FrontierTermAggregate] | None = None,
) -> FrontierResultRow:
    return FrontierResultRow(
        slice_id=slice_config.slice_id,
        candidate_id=candidate_id,
        support_cone_id=slice_config.support_cone.support_cone_id,
        comparison_status=status,
        term_aggregates=term_aggregates or {},
        transfer_summary=ConeTransferSummary(
            eligible=False,
            replacement_candidates=[],
            transfer_reason="candidate is not comparable on this slice",
        ),
        warnings=warnings,
        provenance={},
    )


def _row_in_support_cone(row: CandidateObservationRow, slice_config: FrozenSliceConfig) -> bool:
    cone = slice_config.support_cone
    if cone.support_atom_ids and row.support_atom_id not in cone.support_atom_ids:
        return False
    filters = cone.filters
    if filters is None:
        return True
    return (
        _match_optional_list(row.benchmark_id, filters.benchmark_ids)
        and _match_optional_list(row.source_kind, filters.source_kinds)
        and _match_optional_list(row.control_mode, filters.control_modes)
        and _match_optional_list(row.phase_mode, filters.phase_modes)
        and _match_optional_list(row.strategy_id, filters.strategy_ids)
        and _match_optional_list(row.comparison_group, filters.comparison_groups)
        and _match_tags(row.tags, filters.tags)
    )


def _match_optional_list(value: str | None, allowed: list[str] | None) -> bool:
    if allowed is None:
        return True
    return value in allowed


def _match_tags(values: list[str], required_tags: list[str] | None) -> bool:
    if required_tags is None:
        return True
    return set(required_tags).issubset(set(values))


def validate_frozen_slice_metric_names(slice_config: FrozenSliceConfig) -> None:
    for term in [*slice_config.yield_terms, *slice_config.cost_terms]:
        if term.metric_name not in METRIC_REGISTRY:
            raise ValueError(
                f"unknown frozen-slice metric_name {term.metric_name!r} in slice {slice_config.slice_id!r}"
            )


__all__ = [
    "evaluate_frozen_slice",
    "load_candidate_observation_ledger",
    "validate_frozen_slice_metric_names",
]
