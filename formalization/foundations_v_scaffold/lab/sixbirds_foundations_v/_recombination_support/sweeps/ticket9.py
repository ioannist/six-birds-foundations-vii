from __future__ import annotations

import json
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._recombination_support.benchmarks.loader import load_benchmark
from sixbirds_foundations_v._recombination_support.completion import (
    COMPLETION_STRATEGIES,
    CompletionInputKind,
    CompletionRequest,
    CompletionSourceKind,
    FlatteningControlMode,
    apply_completion_request,
    build_completion_source_surface,
)
from sixbirds_foundations_v._recombination_support.metrics import (
    EmbeddingRecombinationSample,
    EmbeddingRecombinationSamplesInput,
    MetricResultStatus,
    ReadoutSample,
    ReadoutSamplesInput,
    RouteCompositionSample,
    RouteCompositionSamplesInput,
    SupportSnapshotInput,
)
from sixbirds_foundations_v._recombination_support.metrics.registry import METRIC_REGISTRY, evaluate_metric, get_metric_spec
from sixbirds_foundations_v._recombination_support.validation.ticket6 import (
    EXACT_CONFIG_PATHS,
    SUMMARY_CONFIG_PATHS,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

PLAN_PATH_NAME = "ticket9_sweep_plan.json"
LEDGER_PATH_NAME = "ticket9_lift_sweep_ledger.json"
FLAG_PATH_NAME = "ticket9_material_lift_dependence_flags.json"

SOURCE_KINDS = (
    CompletionSourceKind.RECOMBINATION_QUOTIENT,
    CompletionSourceKind.BRANCHWISE_QUOTIENT,
    CompletionSourceKind.MINIMAL_BEHAVIORAL_CARRIER,
)

PRIMARY_METRICS = (
    "closure_defect",
    "closure_deficit",
    "readout_complexity",
    "recombination_additivity_defect",
)
SECONDARY_METRICS = (
    "route_mismatch",
    "transport_linearizability_defect",
    "support_breadth",
)
ALL_SWEEP_METRICS = PRIMARY_METRICS + SECONDARY_METRICS

BASELINE_STRATEGY_ID = "identity_reference"
MATERIAL_DELTA_THRESHOLD = 0.05
NEAR_TIE_THRESHOLD = 1e-9

METRIC_DIRECTION = {
    "closure_defect": "smaller_is_better",
    "closure_deficit": "smaller_is_better",
    "readout_complexity": "smaller_is_better",
    "recombination_additivity_defect": "smaller_is_better",
    "route_mismatch": "smaller_is_better",
    "transport_linearizability_defect": "smaller_is_better",
    "support_breadth": "larger_is_better",
}


def generate_ticket9_lift_sweep_artifacts(
    *,
    repo_root: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, Path]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    resolved_output_root = (output_root or resolved_repo_root).resolve()
    derived_root = resolved_output_root / "results" / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)

    plan_payload = _build_sweep_plan(resolved_repo_root)
    rows, unit_summaries = _run_exact_sweep(resolved_repo_root)
    non_executable_entries = _build_non_executable_summary_entries(resolved_repo_root)
    benchmark_flags = _build_benchmark_flags(unit_summaries, non_executable_entries)
    branch_decision = _compute_branch_decision(benchmark_flags)

    ledger_payload = {
        "schema_version": "ticket9-lift-sweep-ledger.v1",
        "baseline_strategy_id": BASELINE_STRATEGY_ID,
        "branch_decision": branch_decision,
        "materiality_policy": {
            "primary_metrics": list(PRIMARY_METRICS),
            "secondary_metrics": list(SECONDARY_METRICS),
            "material_delta_threshold": MATERIAL_DELTA_THRESHOLD,
            "near_tie_threshold": NEAR_TIE_THRESHOLD,
            "directions": dict(METRIC_DIRECTION),
            "unit_status_rule": (
                "material_lift_dependent iff at least one primary metric is comparable across at least two strategies and max abs delta vs identity_reference exceeds threshold"
            ),
        },
        "row_count": len(rows),
        "rows": rows,
        "unit_summaries": unit_summaries,
        "non_executable_entries": non_executable_entries,
    }
    flags_payload = {
        "schema_version": "ticket9-material-lift-flags.v1",
        "branch_decision": branch_decision,
        "counts": {
            "applicable_exact_runnable_benchmark_count": len(EXACT_CONFIG_PATHS),
            "material_lift_dependent_benchmark_count": sum(
                1
                for entry in benchmark_flags
                if entry["overall_status"] == "material_lift_dependence"
            ),
            "diagnostic_only_count": sum(
                1 for entry in benchmark_flags if entry["overall_status"] == "diagnostic_only"
            ),
            "non_executable_count": sum(
                1
                for entry in benchmark_flags
                if entry["overall_status"] == "not_applicable_non_executable"
            ),
            "insufficient_support_count": sum(
                1
                for entry in benchmark_flags
                if entry["overall_status"] == "insufficient_support"
            ),
        },
        "benchmarks": benchmark_flags,
    }

    plan_path = derived_root / PLAN_PATH_NAME
    ledger_path = derived_root / LEDGER_PATH_NAME
    flags_path = derived_root / FLAG_PATH_NAME
    plan_path.write_text(json.dumps(plan_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    flags_path.write_text(json.dumps(flags_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "plan_path": plan_path,
        "ledger_path": ledger_path,
        "flags_path": flags_path,
        "flag_path": flags_path,
    }


def _build_sweep_plan(repo_root: Path) -> dict[str, Any]:
    exact_entries = []
    for benchmark_id, config_rel in EXACT_CONFIG_PATHS.items():
        config_path = repo_root / config_rel
        benchmark = load_benchmark(config_path)
        control_modes = ["none"]
        if benchmark.flattening_flag:
            control_modes.append("paired_flattening_control")
        source_entries = []
        for source_kind in SOURCE_KINDS:
            source_entries.append(
                {
                    "source_kind": source_kind.value,
                    "control_modes": list(control_modes),
                    "strategy_ids": sorted(COMPLETION_STRATEGIES),
                    "metrics_attempted": list(ALL_SWEEP_METRICS),
                    "deliberate_exclusions": _source_kind_exclusions(source_kind),
                }
            )
        exact_entries.append(
            {
                "benchmark_id": benchmark_id,
                "config_path": config_rel,
                "source_entries": source_entries,
            }
        )
    non_executable_entries = [
        {
            "benchmark_id": benchmark_id,
            "config_path": config_rel,
            "status": "not_applicable_non_executable",
            "reason": "summary/search entry is not executable and is therefore excluded from the raw completion sweep",
        }
        for benchmark_id, config_rel in SUMMARY_CONFIG_PATHS.items()
    ]
    return {
        "schema_version": "ticket9-sweep-plan.v1",
        "baseline_strategy_id": BASELINE_STRATEGY_ID,
        "sweep_unit": ["benchmark_id", "source_kind", "control_mode"],
        "source_kinds_used": [kind.value for kind in SOURCE_KINDS],
        "primary_metrics": list(PRIMARY_METRICS),
        "secondary_metrics": list(SECONDARY_METRICS),
        "exact_runnable_benchmarks": exact_entries,
        "non_executable_entries": non_executable_entries,
        "deliberate_global_exclusions": [
            {
                "path": "predictive_quotient",
                "reason": "Ticket 9 targets carrier-level representative-selection surfaces rather than interface-history selection.",
            }
        ],
    }


def _run_exact_sweep(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    unit_rows: dict[tuple[str, str, str], list[dict[str, Any]]] = {}

    for benchmark_id, config_rel in EXACT_CONFIG_PATHS.items():
        benchmark = load_benchmark(repo_root / config_rel)
        control_modes = [FlatteningControlMode.NONE]
        if benchmark.flattening_flag:
            control_modes.append(FlatteningControlMode.PAIRED_FLATTENING_CONTROL)
        for source_kind in SOURCE_KINDS:
            source_surface = build_completion_source_surface(benchmark, source_kind)
            for control_mode in control_modes:
                unit_key = (benchmark_id, source_kind.value, control_mode.value)
                for strategy_id in sorted(COMPLETION_STRATEGIES):
                    request = CompletionRequest(
                        input_kind=CompletionInputKind.BENCHMARK_REQUEST,
                        source_kind=source_kind,
                        strategy_id=strategy_id,
                        config_path=config_rel,
                        flattening_mode=control_mode,
                    )
                    completion_result = apply_completion_request(request, benchmark=benchmark)
                    metric_results = _evaluate_metrics_for_row(
                        benchmark_id=benchmark_id,
                        source_kind=source_kind,
                        source_surface=source_surface,
                        completion_result=completion_result,
                    )
                    row = {
                        "benchmark_id": benchmark_id,
                        "config_path": config_rel,
                        "source_kind": source_kind.value,
                        "control_mode": control_mode.value,
                        "strategy_id": strategy_id,
                        "completion_status": completion_result.status.value,
                        "metric_results": metric_results,
                        "provenance": completion_result.provenance.model_dump(
                            mode="json",
                            exclude_none=True,
                        ),
                        "contributes_to_primary_materiality": False,
                    }
                    rows.append(row)
                    unit_rows.setdefault(unit_key, []).append(row)

    unit_summaries = [
        _summarize_unit_rows(unit_key, grouped_rows)
        for unit_key, grouped_rows in sorted(unit_rows.items())
    ]
    summary_by_key = {
        (entry["benchmark_id"], entry["source_kind"], entry["control_mode"]): entry
        for entry in unit_summaries
    }
    for row in rows:
        row["contributes_to_primary_materiality"] = summary_by_key[
            (row["benchmark_id"], row["source_kind"], row["control_mode"])
        ]["overall_status"] == "material_lift_dependent"
    return rows, unit_summaries


def _evaluate_metrics_for_row(
    *,
    benchmark_id: str,
    source_kind: CompletionSourceKind,
    source_surface: Any,
    completion_result: Any,
) -> dict[str, Any]:
    metric_results: dict[str, Any] = {}
    for metric_name in ALL_SWEEP_METRICS:
        spec = get_metric_spec(metric_name)
        if completion_result.status.value != "ok":
            metric_results[metric_name] = _unsupported_metric_record(
                metric_name,
                spec.scope_status.value,
                reason=f"completion status is {completion_result.status.value}",
            )
            continue
        metric_input, adapter_note = _build_metric_input_for_metric(
            metric_name=metric_name,
            source_kind=source_kind,
            source_surface=source_surface,
            completion_result=completion_result,
        )
        if metric_input is None:
            metric_results[metric_name] = _unsupported_metric_record(
                metric_name,
                spec.scope_status.value,
                reason=adapter_note,
            )
            continue
        result = evaluate_metric(metric_name, metric_input)
        payload = result.model_dump(mode="json", exclude_none=True)
        payload["adapter_note"] = adapter_note
        metric_results[metric_name] = payload
    return metric_results


def _evaluate_metric_results(
    *,
    benchmark: Any,
    source_surface: Any,
    completion_result: Any,
) -> dict[str, Any]:
    del benchmark
    return _evaluate_metrics_for_row(
        benchmark_id=str(getattr(source_surface, "benchmark_id", "unknown")),
        source_kind=source_surface.source_kind,
        source_surface=source_surface,
        completion_result=completion_result,
    )


def _build_metric_input_for_metric(
    *,
    metric_name: str,
    source_kind: CompletionSourceKind,
    source_surface: Any,
    completion_result: Any,
) -> tuple[Any | None, str]:
    selected_candidates = _selected_candidates(source_surface, completion_result)
    if metric_name in {"closure_defect", "closure_deficit"}:
        if source_kind not in {
            CompletionSourceKind.BRANCHWISE_QUOTIENT,
            CompletionSourceKind.RECOMBINATION_QUOTIENT,
        }:
            return None, "closure metrics currently require assemblage-backed source kinds"
        return _completion_partition_bundle(selected_candidates), "completion-selected lower members"
    if metric_name == "readout_complexity":
        return _completion_readout_samples(selected_candidates), "completion structural feature rows"
    if metric_name == "recombination_additivity_defect":
        if source_kind not in {
            CompletionSourceKind.BRANCHWISE_QUOTIENT,
            CompletionSourceKind.RECOMBINATION_QUOTIENT,
        }:
            return None, "recombination-additivity surrogate currently requires assemblage-backed source kinds"
        return _completion_recombination_samples(selected_candidates), "selected representative structural embeddings"
    if metric_name == "route_mismatch":
        if source_kind not in {
            CompletionSourceKind.BRANCHWISE_QUOTIENT,
            CompletionSourceKind.RECOMBINATION_QUOTIENT,
        }:
            return None, "route mismatch currently requires assemblage-backed source kinds"
        return _completion_route_samples(selected_candidates), "predictive decomposition route samples"
    if metric_name == "support_breadth":
        return _completion_support_snapshot(source_surface, completion_result), "selected lower-member support coverage"
    if metric_name == "transport_linearizability_defect":
        return None, "transport embeddings are not yet exposed by completion outputs in Ticket 9"
    return None, "metric not mapped for Ticket 9"


def _completion_partition_bundle(selected_candidates: dict[str, Any]) -> Any:
    from sixbirds_foundations_v._recombination_support.metrics import PartitionBundleInput

    current_element_to_class_id: dict[str, str] = {}
    predictive_element_to_class_id: dict[str, str] = {}
    for class_id, candidate in selected_candidates.items():
        decomposition = candidate.details.get("predictive_decomposition")
        if decomposition:
            for row in decomposition:
                history_id = str(row["history_id"])
                element_id = f"{class_id}::{history_id}"
                current_element_to_class_id[element_id] = class_id
                predictive_element_to_class_id[element_id] = str(row["predictive_class_id"])
        else:
            signature_key = repr(candidate.predictive_signature_key)
            for member_id in candidate.lower_member_ids:
                element_id = f"{class_id}::{member_id}"
                current_element_to_class_id[element_id] = class_id
                predictive_element_to_class_id[element_id] = signature_key
    return PartitionBundleInput(
        executable=True,
        current_element_to_class_id=current_element_to_class_id,
        predictive_element_to_class_id=predictive_element_to_class_id,
    )


def _completion_readout_samples(selected_candidates: dict[str, Any]) -> ReadoutSamplesInput:
    samples = []
    for class_id, candidate in selected_candidates.items():
        features = _candidate_structural_embedding(candidate)
        samples.append(
            ReadoutSample(
                sample_id=class_id,
                features=features,
                label=class_id,
            )
        )
    return ReadoutSamplesInput(samples=samples)


def _completion_recombination_samples(
    selected_candidates: dict[str, Any],
) -> EmbeddingRecombinationSamplesInput | None:
    if len(selected_candidates) < 3:
        return None
    embeddings = {
        class_id: _candidate_structural_embedding(candidate)
        for class_id, candidate in selected_candidates.items()
    }
    ordered_class_ids = list(selected_candidates)
    samples = []
    for sample_index, (left_id, right_id, target_id) in enumerate(
        permutations(ordered_class_ids, 3)
    ):
        samples.append(
            EmbeddingRecombinationSample(
                sample_id=f"triple_{sample_index}",
                left_vector=embeddings[left_id],
                right_vector=embeddings[right_id],
                target_vector=embeddings[target_id],
                left_weight=1.0,
                right_weight=1.0,
            )
        )
    return EmbeddingRecombinationSamplesInput(samples=samples)


def _completion_route_samples(
    selected_candidates: dict[str, Any],
) -> RouteCompositionSamplesInput:
    samples: list[RouteCompositionSample] = []
    for class_id, candidate in selected_candidates.items():
        decomposition = candidate.details.get("predictive_decomposition")
        if decomposition:
            effect_by_source_id = {
                str(row["history_id"]): str(row["predictive_class_id"])
                for row in decomposition
            }
        else:
            effect_by_source_id = {
                member_id: repr(candidate.predictive_signature_key)
                for member_id in candidate.lower_member_ids
            }
        samples.append(
            RouteCompositionSample(
                route_id=f"{class_id}:{candidate.candidate_id}",
                effect_by_source_id=effect_by_source_id,
            )
        )
    return RouteCompositionSamplesInput(samples=samples)


def _completion_support_snapshot(source_surface: Any, completion_result: Any) -> SupportSnapshotInput:
    selected_candidates = _selected_candidates(source_surface, completion_result)
    selected_support = sorted(
        {
            member_id
            for candidate in selected_candidates.values()
            for member_id in candidate.lower_member_ids
        }
    )
    universe = sorted(
        {
            member_id
            for completion_class in source_surface.classes
            for candidate in completion_class.candidates
            for member_id in candidate.lower_member_ids
        }
    )
    return SupportSnapshotInput(support_ids=selected_support, universe_ids=universe)


def _candidate_structural_embedding(candidate: Any) -> list[float]:
    atom_values = _atom_values(candidate.candidate_signature if candidate.candidate_signature is not None else candidate.predictive_signature_key)
    fraction_values = []
    for value in atom_values:
        try:
            fraction_values.append(Fraction(value))
        except (ValueError, ZeroDivisionError):
            continue
    mixed_fraction_count = sum(
        1 for value in fraction_values if value not in {Fraction(0, 1), Fraction(1, 1)}
    )
    half_probability_count = sum(1 for value in fraction_values if value == Fraction(1, 2))
    return [
        float(candidate.branch_member_count or 0),
        float(len(candidate.lower_member_ids)),
        float(len(atom_values)),
        float(mixed_fraction_count),
        float(half_probability_count),
    ]


def _atom_values(value: Any) -> list[str]:
    atoms: list[str] = []
    if isinstance(value, dict):
        for key in sorted(value):
            atoms.extend(_atom_values(value[key]))
    elif isinstance(value, list):
        for item in value:
            atoms.extend(_atom_values(item))
    else:
        atoms.append(str(value))
    return atoms


def _selected_candidates(source_surface: Any, completion_result: Any) -> dict[str, Any]:
    candidates: dict[str, Any] = {}
    candidate_lookup = {
        (completion_class.class_id, candidate.candidate_id): candidate
        for completion_class in source_surface.classes
        for candidate in completion_class.candidates
    }
    for completion_class in source_surface.classes:
        candidate_id = completion_result.representative_mapping.get(completion_class.class_id)
        if candidate_id is None:
            continue
        candidates[completion_class.class_id] = candidate_lookup[
            (completion_class.class_id, candidate_id)
        ]
    return candidates


@dataclass(frozen=True)
class _UnsupportedMetricInput:
    input_kind: str


def _comparison_basis(metric_name: str) -> str:
    return METRIC_DIRECTION[metric_name]


def _comparison_value(metric_name: str, value: Any) -> float:
    del metric_name
    return float(value)


def _relation_to_baseline(
    *,
    metric_name: str,
    current_value: float,
    baseline_value: float,
) -> str:
    delta = current_value - baseline_value
    if abs(delta) <= NEAR_TIE_THRESHOLD:
        return "tie"
    direction = METRIC_DIRECTION[metric_name]
    if direction == "smaller_is_better":
        return "better" if current_value < baseline_value else "worse"
    return "better" if current_value > baseline_value else "worse"


def _summarize_unit_rows(
    unit_key: tuple[str, str, str],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    benchmark_id, source_kind, control_mode = unit_key
    baseline_row = next(row for row in rows if row["strategy_id"] == BASELINE_STRATEGY_ID)
    metric_statuses: dict[str, dict[str, Any]] = {}
    primary_comparable_metrics: list[str] = []
    secondary_comparable_metrics: list[str] = []
    material_metrics: list[str] = []
    best_strategy_by_metric: dict[str, str] = {}

    for metric_name in ALL_SWEEP_METRICS:
        baseline_metric = baseline_row["metric_results"][metric_name]
        comparable_rows = [
            row
            for row in rows
            if row["metric_results"][metric_name]["status"] == MetricResultStatus.OK.value
        ]
        values_by_strategy = {
            row["strategy_id"]: row["metric_results"][metric_name]["value"]
            for row in comparable_rows
        }
        for row in rows:
            row["metric_results"][metric_name]["comparison"] = _metric_comparison_payload(
                metric_name,
                row["metric_results"][metric_name],
                baseline_metric,
            )
        if len(comparable_rows) < 2:
            continue
        values = [float(value) for value in values_by_strategy.values()]
        max_abs_delta = max(
            abs(float(value) - float(baseline_metric["value"])) for value in values_by_strategy.values()
        )
        better_strategy = _best_strategy_for_metric(metric_name, values_by_strategy)
        metric_statuses[metric_name] = {
            "supported_strategy_ids": sorted(values_by_strategy),
            "max_abs_delta_vs_identity_reference": max_abs_delta,
            "best_strategy_id": better_strategy,
        }
        if metric_name in PRIMARY_METRICS:
            primary_comparable_metrics.append(metric_name)
            if max_abs_delta > MATERIAL_DELTA_THRESHOLD:
                material_metrics.append(metric_name)
        else:
            secondary_comparable_metrics.append(metric_name)
        best_strategy_by_metric[metric_name] = better_strategy

    if material_metrics:
        overall_status = "material_lift_dependent"
    elif primary_comparable_metrics:
        overall_status = "weak_or_none"
    elif secondary_comparable_metrics:
        overall_status = "diagnostic_only"
    else:
        overall_status = "insufficient_support"

    return {
        "benchmark_id": benchmark_id,
        "source_kind": source_kind,
        "control_mode": control_mode,
        "overall_status": overall_status,
        "primary_comparable_metrics": primary_comparable_metrics,
        "secondary_comparable_metrics": secondary_comparable_metrics,
        "material_metrics": material_metrics,
        "best_strategy_by_metric": best_strategy_by_metric,
        "metric_statuses": metric_statuses,
    }


def _metric_comparison_payload(
    metric_name: str,
    metric_payload: dict[str, Any],
    baseline_metric: dict[str, Any],
) -> dict[str, Any]:
    if (
        metric_payload["status"] != MetricResultStatus.OK.value
        or baseline_metric["status"] != MetricResultStatus.OK.value
    ):
        return {
            "comparison_status": "not_comparable",
            "delta_vs_identity_reference": None,
            "relation_to_identity_reference": "n/a",
        }
    current_value = float(metric_payload["value"])
    baseline_value = float(baseline_metric["value"])
    delta = current_value - baseline_value
    abs_delta = abs(delta)
    if abs_delta <= NEAR_TIE_THRESHOLD:
        relation = "tie"
    else:
        direction = METRIC_DIRECTION[metric_name]
        if direction == "smaller_is_better":
            relation = "better" if current_value < baseline_value else "worse"
        else:
            relation = "better" if current_value > baseline_value else "worse"
    return {
        "comparison_status": "compared",
        "delta_vs_identity_reference": delta,
        "abs_delta_vs_identity_reference": abs_delta,
        "comparison_basis": _comparison_basis(metric_name),
        "relation_to_identity_reference": relation,
    }


def _best_strategy_for_metric(metric_name: str, values_by_strategy: dict[str, Any]) -> str:
    direction = METRIC_DIRECTION[metric_name]
    if direction == "smaller_is_better":
        return min(
            values_by_strategy,
            key=lambda strategy_id: (float(values_by_strategy[strategy_id]), strategy_id),
        )
    return max(
        values_by_strategy,
        key=lambda strategy_id: (float(values_by_strategy[strategy_id]), strategy_id),
    )


def _build_non_executable_summary_entries(repo_root: Path) -> list[dict[str, Any]]:
    entries = []
    for benchmark_id, config_rel in SUMMARY_CONFIG_PATHS.items():
        benchmark = load_benchmark(repo_root / config_rel)
        entries.append(
            {
                "benchmark_id": benchmark_id,
                "config_path": config_rel,
                "loader_kind": benchmark.loader_kind.value,
                "overall_status": "not_applicable_non_executable",
                "reason": "summary/search entry is not executable and therefore excluded from the raw completion sweep",
            }
        )
    return entries


def _build_benchmark_flags(
    unit_summaries: list[dict[str, Any]],
    non_executable_entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    units_by_benchmark: dict[str, list[dict[str, Any]]] = {}
    for unit in unit_summaries:
        units_by_benchmark.setdefault(unit["benchmark_id"], []).append(unit)

    flags: list[dict[str, Any]] = []
    for benchmark_id in EXACT_CONFIG_PATHS:
        units = units_by_benchmark.get(benchmark_id, [])
        if any(unit["overall_status"] == "material_lift_dependent" for unit in units):
            overall_status = "material_lift_dependence"
        elif any(unit["overall_status"] == "weak_or_none" for unit in units):
            overall_status = "weak_or_none"
        elif any(unit["overall_status"] == "diagnostic_only" for unit in units):
            overall_status = "diagnostic_only"
        else:
            overall_status = "insufficient_support"
        material_units = [
            {
                "source_kind": unit["source_kind"],
                "control_mode": unit["control_mode"],
                "material_metrics": unit["material_metrics"],
            }
            for unit in units
            if unit["overall_status"] == "material_lift_dependent"
        ]
        material_metrics = sorted(
            {
                metric_name
                for unit in units
                for metric_name in unit["material_metrics"]
            }
        )
        flags.append(
            {
                "benchmark_id": benchmark_id,
                "overall_status": overall_status,
                "supporting_sweep_units": material_units
                if material_units
                else [
                    {
                        "source_kind": unit["source_kind"],
                        "control_mode": unit["control_mode"],
                        "material_metrics": [],
                    }
                    for unit in units
                    if unit["overall_status"] in {"weak_or_none", "diagnostic_only"}
                ],
                "primary_metrics_with_material_deltas": material_metrics,
                "best_strategy_shifts": {
                    unit["source_kind"] + ":" + unit["control_mode"]: unit["best_strategy_by_metric"]
                    for unit in units
                    if unit["best_strategy_by_metric"]
                },
                "reason": _benchmark_reason(overall_status),
            }
        )
    flags.extend(non_executable_entries)
    return flags


def _benchmark_reason(overall_status: str) -> str:
    return {
        "material_lift_dependence": "at least one sweep unit exceeded the primary materiality threshold relative to identity_reference",
        "weak_or_none": "primary metrics were comparable but did not show material deltas beyond the configured threshold",
        "diagnostic_only": "only secondary metrics were meaningfully comparable for the applicable sweep units",
        "insufficient_support": "no sweep unit exposed enough comparable metric support for a fair Route-B decision",
    }[overall_status]


def _compute_branch_decision(benchmark_flags: list[dict[str, Any]]) -> str:
    exact_flags = [entry for entry in benchmark_flags if entry["benchmark_id"] in EXACT_CONFIG_PATHS]
    material_count = sum(
        1 for entry in exact_flags if entry["overall_status"] == "material_lift_dependence"
    )
    comparable_primary_count = sum(
        1
        for entry in exact_flags
        if entry["overall_status"] in {"material_lift_dependence", "weak_or_none"}
    )
    if material_count >= 2:
        return "ROUTE_B_SIGNAL_PRESENT"
    if comparable_primary_count == 0:
        return "INCONCLUSIVE"
    return "ROUTE_B_WEAK"


def _unsupported_metric_record(
    metric_name: str,
    scope_status: str,
    *,
    reason: str,
) -> dict[str, Any]:
    spec = get_metric_spec(metric_name)
    expected_input_kind = (
        spec.required_input_kinds[0].value if spec.required_input_kinds else "n/a"
    )
    return {
        "metric_name": metric_name,
        "status": MetricResultStatus.UNSUPPORTED.value,
        "scope_status": scope_status,
        "value": None,
        "input_kind": "n/a",
        "details": {
            "expected_input_kind": expected_input_kind,
            "reason": reason,
        },
    }


def _source_kind_exclusions(source_kind: CompletionSourceKind) -> list[dict[str, str]]:
    if source_kind is CompletionSourceKind.MINIMAL_BEHAVIORAL_CARRIER:
        return [
            {
                "strategy_id": "max_weight_representative",
                "reason": "minimal behavioral carrier candidates do not expose branch weights in Ticket 8",
            },
            {
                "metric_name": "closure_defect",
                "reason": "closure metrics are not yet defined on minimal-carrier completion outputs",
            },
            {
                "metric_name": "closure_deficit",
                "reason": "closure metrics are not yet defined on minimal-carrier completion outputs",
            },
        ]
    return []


generate_ticket9_artifacts = generate_ticket9_lift_sweep_artifacts
FLAGS_PATH_NAME = FLAG_PATH_NAME

__all__ = [
    "FLAG_PATH_NAME",
    "FLAGS_PATH_NAME",
    "LEDGER_PATH_NAME",
    "PLAN_PATH_NAME",
    "_UnsupportedMetricInput",
    "_comparison_basis",
    "_comparison_value",
    "_evaluate_metric_results",
    "_relation_to_baseline",
    "_selected_candidates",
    "generate_ticket9_artifacts",
    "generate_ticket9_lift_sweep_artifacts",
]
