from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import FrozenSliceConfig, SixBirdsRecombinationModel

from sixbirds_foundations_v._recombination_support.benchmarks.loader import load_benchmark
from sixbirds_foundations_v._recombination_support.completion import (
    CompletionInputKind,
    CompletionRequest,
    CompletionSourceKind,
    CompletionStatus,
    apply_completion_request,
    build_completion_source_surface,
)
from sixbirds_foundations_v._recombination_support.frontier import (
    CandidateMetricObservation,
    CandidateMetricStatus,
    CandidateObservationLedger,
    CandidateObservationRow,
    FrontierEvaluationResult,
    FrontierResultRow,
    evaluate_frozen_slice,
)
from sixbirds_foundations_v._recombination_support.schemas.registry import validate_artifact
from sixbirds_foundations_v._recombination_support.sweeps.ticket9 import _evaluate_metric_results, _selected_candidates
from .costs import (
    BudgetCostStatus,
    CandidateCostSummary,
    evaluate_candidate_cost,
)
from .estimators import (
    FINITE_DIFFERENCE_ESTIMATOR,
    ShadowPriceEstimate,
    estimate_shadow_prices,
)
from .ledger import (
    HONEST_DEFAULT_PHASE_MODE,
    BudgetCandidateSelection,
    LowerLayerLedger,
    extract_lower_layer_ledger,
    resolve_honest_phase_mode,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
BUDGET_DEMO_CONFIG_PATH = (
    REPO_ROOT / "configs" / "recombination" / "budgets" / "erasure_recovery_anchor_demo.json"
)
BUDGET_SWEEP_LEDGER_PATH = REPO_ROOT / "results" / "derived" / "ticket13_budget_sweep_ledger.json"
BUDGET_SUMMARY_PATH = REPO_ROOT / "results" / "derived" / "ticket13_budget_demo_summary.json"
SHADOW_PRICE_PATH = REPO_ROOT / "results" / "derived" / "ticket13_shadow_price_estimates.json"


class BudgetDemoConfig(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-budget-demo-config.v1"
    benchmark_config_path: str
    slice_config_path: str
    source_kinds: list[str]
    cost_modes: list[str]
    budget_levels_by_cost_mode: dict[str, list[float]]
    estimator_ids: list[str]
    fixed_strategy_id: str = "identity_reference"
    fixed_phase_mode: str | None = None
    notes: list[str] = Field(default_factory=list)


def load_budget_demo_config(path: str | Path = BUDGET_DEMO_CONFIG_PATH) -> BudgetDemoConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return BudgetDemoConfig.model_validate(payload)


def build_budget_candidate_inputs(
    *,
    benchmark_config_path: str,
    source_kinds: list[str],
    strategy_id: str = "identity_reference",
    phase_mode: str | None = None,
    repo_root: Path | None = None,
) -> tuple[LowerLayerLedger, list[BudgetCandidateSelection], CandidateObservationLedger]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    benchmark = load_benchmark(resolved_repo_root / benchmark_config_path)
    phase_label = phase_mode or resolve_honest_phase_mode(benchmark)
    lower_layer_ledger = extract_lower_layer_ledger(
        benchmark,
        phase_mode=phase_label,
        strategy_id=strategy_id,
    )

    selections: list[BudgetCandidateSelection] = []
    observation_rows: list[CandidateObservationRow] = []
    support_atom_id = benchmark.config_id
    for source_kind_name in source_kinds:
        source_kind = CompletionSourceKind(source_kind_name)
        surface = build_completion_source_surface(benchmark, source_kind)
        completion_result = apply_completion_request(
            CompletionRequest(
                input_kind=CompletionInputKind.BENCHMARK_REQUEST,
                source_kind=source_kind,
                strategy_id=strategy_id,
                config_path=benchmark_config_path,
            ),
            benchmark=benchmark,
        )
        candidate_id = source_kind.value
        if completion_result.status is CompletionStatus.OK:
            selected_candidates = _selected_candidates(surface, completion_result)
            metric_payloads = _evaluate_metric_results(
                benchmark=benchmark,
                source_surface=surface,
                completion_result=completion_result,
            )
            selected_history_ids = sorted(
                {
                    member_id
                    for candidate in selected_candidates.values()
                    for member_id in candidate.lower_member_ids
                }
            )
            selected_candidate_ids = sorted(
                {candidate.candidate_id for candidate in selected_candidates.values()}
            )
            observation_rows.append(
                CandidateObservationRow(
                    candidate_id=candidate_id,
                    support_atom_id=support_atom_id,
                    benchmark_id=benchmark.config_id,
                    source_kind=source_kind.value,
                    phase_mode=phase_label,
                    strategy_id=strategy_id,
                    comparison_group=benchmark.config_id,
                    tags=sorted({*benchmark.tags, "budget-demo", "ticket13"}),
                    support_cone_tags=["ticket13", "budget-demo"],
                    metric_results={
                        metric_name: _metric_observation_from_payload(metric_payload)
                        for metric_name, metric_payload in metric_payloads.items()
                    },
                    provenance={
                        "config_path": benchmark.config_path,
                        "runtime_benchmark_id": benchmark.benchmark_id or benchmark.config_id,
                        "completion_snapshot_version": completion_result.snapshot_version,
                    },
                    notes=["ticket13 budget candidate observation row"],
                )
            )
        else:
            metric_payloads = {}
            selected_history_ids = []
            selected_candidate_ids = []
        selections.append(
            BudgetCandidateSelection(
                candidate_id=candidate_id,
                benchmark_id=benchmark.config_id,
                runtime_benchmark_id=benchmark.benchmark_id or benchmark.config_id,
                config_id=benchmark.config_id,
                config_path=benchmark.config_path,
                source_kind=source_kind.value,
                strategy_id=strategy_id,
                phase_mode=phase_label,
                completion_status=completion_result.status.value,
                selected_representative_ids=dict(completion_result.representative_mapping),
                selected_candidate_ids=selected_candidate_ids,
                selected_history_ids=selected_history_ids,
                metric_results=metric_payloads,
                provenance={
                    "completion_result_ref": f"completion:{source_kind.value}:{strategy_id}",
                    "support_atom_id": support_atom_id,
                },
                warnings=list(completion_result.warnings),
            )
        )

    observation_ledger = CandidateObservationLedger(
        ledger_id=f"{benchmark.config_id}.ticket13.candidates",
        rows=observation_rows,
    )
    return lower_layer_ledger, selections, observation_ledger


def run_budget_sweep(
    *,
    benchmark_id: str,
    slice_config: FrozenSliceConfig,
    candidate_ledger: CandidateObservationLedger,
    candidate_selections: list[BudgetCandidateSelection],
    lower_layer_ledger: LowerLayerLedger,
    cost_modes: list[str],
    budget_levels_by_cost_mode: dict[str, list[float]],
) -> dict[str, Any]:
    row_metric_vectors = {
        row.candidate_id: _slice_vectors_from_row(row, slice_config)
        for row in candidate_ledger.rows
    }
    cost_summaries_by_mode: dict[str, dict[str, CandidateCostSummary]] = {}
    rows: list[dict[str, Any]] = []

    for cost_mode in cost_modes:
        cost_summaries = {
            selection.candidate_id: evaluate_candidate_cost(
                selection,
                lower_layer_ledger,
                cost_mode=cost_mode,
            )
            for selection in candidate_selections
        }
        cost_summaries_by_mode[cost_mode] = cost_summaries
        for budget_level in sorted(float(level) for level in budget_levels_by_cost_mode.get(cost_mode, [])):
            feasible_candidate_ids = sorted(
                candidate_id
                for candidate_id, summary in cost_summaries.items()
                if summary.status is BudgetCostStatus.OK
                and summary.aggregated_cost is not None
                and float(summary.aggregated_cost) <= budget_level
            )
            feasible_rows = [
                row
                for row in candidate_ledger.rows
                if row.candidate_id in feasible_candidate_ids
            ]
            frontier_result = _evaluate_feasible_frontier(
                slice_config=slice_config,
                source_ledger=candidate_ledger,
                feasible_rows=feasible_rows,
                budget_level=budget_level,
                cost_mode=cost_mode,
            )
            frontier_rows_by_candidate = (
                {row.candidate_id: row for row in frontier_result.rows}
                if frontier_result is not None
                else {}
            )
            for selection in sorted(candidate_selections, key=lambda item: item.candidate_id):
                cost_summary = cost_summaries[selection.candidate_id]
                frontier_row = frontier_rows_by_candidate.get(selection.candidate_id)
                rows.append(
                    {
                        "benchmark_id": benchmark_id,
                        "slice_id": slice_config.slice_id,
                        "candidate_id": selection.candidate_id,
                        "support_cone_id": slice_config.support_cone.support_cone_id,
                        "source_kind": selection.source_kind,
                        "strategy_id": selection.strategy_id,
                        "phase_mode": selection.phase_mode,
                        "cost_mode": cost_mode,
                        "budget_level": budget_level,
                        "feasibility_status": _feasibility_status(
                            selection=selection,
                            cost_summary=cost_summary,
                            budget_level=budget_level,
                        ),
                        "aggregated_budget_cost": cost_summary.aggregated_cost,
                        "frontier_member_flag": bool(frontier_row.frontier_member) if frontier_row else False,
                        "frontier_comparison_status": (
                            frontier_row.comparison_status.value if frontier_row is not None else None
                        ),
                        "yield_vector": row_metric_vectors.get(selection.candidate_id, {}).get("yield", {}),
                        "cost_vector": row_metric_vectors.get(selection.candidate_id, {}).get("cost", {}),
                        "cost_summary": cost_summary.model_dump(mode="json"),
                        "provenance": {
                            "config_path": selection.config_path,
                            "selected_history_ids": list(selection.selected_history_ids),
                            "frontier_snapshot_version": (
                                frontier_result.snapshot_version if frontier_result is not None else None
                            ),
                        },
                        "warnings": list(selection.warnings) + list(cost_summary.warnings),
                    }
                )

    return {
        "schema_version": "ticket13-budget-sweep-ledger.v1",
        "benchmark_id": benchmark_id,
        "slice_id": slice_config.slice_id,
        "row_count": len(rows),
        "rows": rows,
        "cost_summaries_by_mode": {
            cost_mode: {
                candidate_id: summary.model_dump(mode="json")
                for candidate_id, summary in summaries.items()
            }
            for cost_mode, summaries in cost_summaries_by_mode.items()
        },
    }


def generate_ticket13_budget_demo_artifacts(
    *,
    repo_root: Path | None = None,
    demo_config_path: str | Path = BUDGET_DEMO_CONFIG_PATH,
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or REPO_ROOT).resolve()
    demo_config = load_budget_demo_config(demo_config_path)
    slice_config = validate_artifact("frozen-slice", resolved_repo_root / demo_config.slice_config_path)
    assert isinstance(slice_config, FrozenSliceConfig)

    lower_layer_ledger, candidate_selections, candidate_ledger = build_budget_candidate_inputs(
        benchmark_config_path=demo_config.benchmark_config_path,
        source_kinds=list(demo_config.source_kinds),
        strategy_id=demo_config.fixed_strategy_id,
        phase_mode=demo_config.fixed_phase_mode,
        repo_root=resolved_repo_root,
    )
    sweep_payload = run_budget_sweep(
        benchmark_id=candidate_selections[0].benchmark_id if candidate_selections else "unknown",
        slice_config=slice_config,
        candidate_ledger=candidate_ledger,
        candidate_selections=candidate_selections,
        lower_layer_ledger=lower_layer_ledger,
        cost_modes=list(demo_config.cost_modes),
        budget_levels_by_cost_mode=dict(demo_config.budget_levels_by_cost_mode),
    )
    estimates: list[ShadowPriceEstimate] = []
    for estimator_id in demo_config.estimator_ids:
        estimates.extend(
            estimate_shadow_prices(
                sweep_payload["rows"],
                estimator_id=estimator_id,
                target_yield_term=slice_config.yield_terms[0].metric_name,
            )
        )

    summary_payload = {
        "schema_version": "ticket13-budget-demo-summary.v1",
        "benchmark_id": candidate_selections[0].benchmark_id if candidate_selections else "unknown",
        "benchmark_config_path": demo_config.benchmark_config_path,
        "slice_id": slice_config.slice_id,
        "slice_config_path": demo_config.slice_config_path,
        "fixed_strategy_id": demo_config.fixed_strategy_id,
        "fixed_phase_mode": candidate_selections[0].phase_mode if candidate_selections else HONEST_DEFAULT_PHASE_MODE,
        "candidate_source_kinds_attempted": list(demo_config.source_kinds),
        "cost_modes_run": list(demo_config.cost_modes),
        "budget_grid_used": dict(demo_config.budget_levels_by_cost_mode),
        "structural_and_proxy_completed": {
            cost_mode: all(
                row["cost_summary"]["status"] == "ok"
                for row in sweep_payload["rows"]
                if row["cost_mode"] == cost_mode
            )
            for cost_mode in demo_config.cost_modes
        },
        "supported_estimator_ids": list(demo_config.estimator_ids),
        "candidate_selections": [selection.model_dump(mode="json") for selection in candidate_selections],
        "per_cost_mode_takeaways": _per_cost_mode_takeaways(
            sweep_payload["rows"],
            target_yield_term=slice_config.yield_terms[0].metric_name,
        ),
        "lower_layer_ledger": lower_layer_ledger.model_dump(mode="json"),
        "candidate_observation_ledger": candidate_ledger.model_dump(mode="json"),
    }

    BUDGET_SWEEP_LEDGER_PATH.write_text(
        json.dumps(sweep_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    SHADOW_PRICE_PATH.write_text(
        json.dumps(
            {
                "schema_version": "ticket13-shadow-price-estimates.v1",
                "estimates": [estimate.model_dump(mode="json") for estimate in estimates],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    BUDGET_SUMMARY_PATH.write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "summary_path": BUDGET_SUMMARY_PATH,
        "ledger_path": BUDGET_SWEEP_LEDGER_PATH,
        "shadow_price_path": SHADOW_PRICE_PATH,
    }


def _metric_observation_from_payload(payload: dict[str, Any]) -> CandidateMetricObservation:
    return CandidateMetricObservation(
        metric_name=str(payload["metric_name"]),
        status=CandidateMetricStatus(str(payload["status"])),
        scope_status=str(payload["scope_status"]),
        value=payload.get("value"),
        units=payload.get("units"),
        details=dict(payload.get("details", {})),
    )


def _slice_vectors_from_row(
    row: CandidateObservationRow,
    slice_config: FrozenSliceConfig,
) -> dict[str, dict[str, float]]:
    yield_vector: dict[str, float] = {}
    cost_vector: dict[str, float] = {}
    for term in slice_config.yield_terms:
        metric = row.metric_results.get(term.metric_name)
        if metric is not None and metric.status is CandidateMetricStatus.OK and metric.value is not None:
            yield_vector[term.metric_name] = float(metric.value)
    for term in slice_config.cost_terms:
        metric = row.metric_results.get(term.metric_name)
        if metric is not None and metric.status is CandidateMetricStatus.OK and metric.value is not None:
            cost_vector[term.metric_name] = float(metric.value)
    return {"yield": yield_vector, "cost": cost_vector}


def _evaluate_feasible_frontier(
    *,
    slice_config: FrozenSliceConfig,
    source_ledger: CandidateObservationLedger,
    feasible_rows: list[CandidateObservationRow],
    budget_level: float,
    cost_mode: str,
) -> FrontierEvaluationResult | None:
    if not feasible_rows:
        return None
    feasible_ledger = CandidateObservationLedger(
        ledger_id=f"{source_ledger.ledger_id}.{cost_mode}.{budget_level}",
        rows=feasible_rows,
    )
    return evaluate_frozen_slice(slice_config, feasible_ledger)


def _feasibility_status(
    *,
    selection: BudgetCandidateSelection,
    cost_summary: CandidateCostSummary,
    budget_level: float,
) -> str:
    if selection.completion_status != "ok":
        return "unsupported_candidate"
    if cost_summary.status is BudgetCostStatus.UNSUPPORTED:
        return "unsupported_cost_mode"
    if cost_summary.status is BudgetCostStatus.NOT_ENOUGH_DATA:
        return "not_enough_cost_data"
    if cost_summary.aggregated_cost is None:
        return "not_costed"
    if float(cost_summary.aggregated_cost) <= budget_level:
        return "feasible"
    return "infeasible_budget"


def _per_cost_mode_takeaways(
    rows: list[dict[str, Any]],
    *,
    target_yield_term: str,
) -> dict[str, Any]:
    takeaways: dict[str, Any] = {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["cost_mode"], []).append(row)
    for cost_mode, mode_rows in sorted(grouped.items()):
        frontier_rows = [row for row in mode_rows if row["frontier_member_flag"]]
        best_by_budget: dict[str, Any] = {}
        for row in frontier_rows:
            budget_key = str(row["budget_level"])
            current = best_by_budget.get(budget_key)
            value = row["yield_vector"].get(target_yield_term)
            if value is None:
                continue
            if current is None or float(value) > float(current["best_yield"]):
                best_by_budget[budget_key] = {
                    "best_yield": value,
                    "candidate_id": row["candidate_id"],
                }
        takeaways[cost_mode] = {
            "frontier_candidate_ids": sorted({row["candidate_id"] for row in frontier_rows}),
            "best_yield_by_budget": best_by_budget,
            "feasible_budget_levels": sorted(
                {
                    row["budget_level"]
                    for row in mode_rows
                    if row["feasibility_status"] == "feasible"
                }
            ),
        }
    return takeaways


__all__ = [
    "BUDGET_DEMO_CONFIG_PATH",
    "BUDGET_SUMMARY_PATH",
    "BUDGET_SWEEP_LEDGER_PATH",
    "BudgetDemoConfig",
    "SHADOW_PRICE_PATH",
    "build_budget_candidate_inputs",
    "generate_ticket13_budget_demo_artifacts",
    "load_budget_demo_config",
    "run_budget_sweep",
]
