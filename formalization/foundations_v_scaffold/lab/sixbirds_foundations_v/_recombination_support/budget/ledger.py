from __future__ import annotations

from collections import Counter
from fractions import Fraction
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel

from ..benchmarks.loader import LoadedBenchmark, build_reachable_state_graph_snapshot


HONEST_DEFAULT_PHASE_MODE = "default_no_protocol_metadata"


class LowerLayerLedgerRow(SixBirdsRecombinationModel):
    support_atom_id: str
    benchmark_id: str
    run_ref: str
    config_path: str
    state_from_id: str
    state_to_id: str
    generator_id: str
    branch_id: str | None = None
    weight: str | None = None
    phase_mode: str
    strategy_id: str
    source_history_ids: list[str] = Field(default_factory=list)
    target_history_ids: list[str] = Field(default_factory=list)
    source_support_ids: list[str] = Field(default_factory=list)
    target_support_ids: list[str] = Field(default_factory=list)
    structural_features: dict[str, Any] = Field(default_factory=dict)
    proxy_features: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class LowerLayerLedger(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-lower-layer-ledger.v1"
    ledger_id: str
    benchmark_id: str
    run_ref: str
    config_path: str
    phase_mode: str
    strategy_id: str
    state_count: int
    edge_count: int
    rows: list[LowerLayerLedgerRow]
    warnings: list[str] = Field(default_factory=list)


class BudgetCandidateSelection(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-budget-candidate-selection.v1"
    candidate_id: str
    benchmark_id: str
    runtime_benchmark_id: str
    config_id: str
    config_path: str
    source_kind: str
    strategy_id: str
    phase_mode: str
    completion_status: str
    selected_representative_ids: dict[str, str] = Field(default_factory=dict)
    selected_candidate_ids: list[str] = Field(default_factory=list)
    selected_history_ids: list[str] = Field(default_factory=list)
    metric_results: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


def resolve_honest_phase_mode(benchmark: LoadedBenchmark) -> str:
    if benchmark.protocol_internalization_flag:
        return "internalized"
    return HONEST_DEFAULT_PHASE_MODE


def extract_lower_layer_ledger(
    benchmark: LoadedBenchmark,
    *,
    phase_mode: str | None = None,
    strategy_id: str = "identity_reference",
) -> LowerLayerLedger:
    graph = build_reachable_state_graph_snapshot(benchmark)
    phase_label = phase_mode or resolve_honest_phase_mode(benchmark)
    states_by_id = {state.state_id: state for state in graph.states}
    out_degree = Counter(edge.source_state_id for edge in graph.edges)

    rows: list[LowerLayerLedgerRow] = []
    for edge in graph.edges:
        source = states_by_id[edge.source_state_id]
        target = states_by_id[edge.target_state_id]
        source_support_ids = _positive_support_ids(source.support_distribution)
        target_support_ids = _positive_support_ids(target.support_distribution)
        support_shift_count = len(set(source_support_ids) ^ set(target_support_ids))
        rows.append(
            LowerLayerLedgerRow(
                support_atom_id=f"{edge.source_state_id}::{edge.continuation_id}",
                benchmark_id=benchmark.config_id,
                run_ref=f"config:{benchmark.config_id}",
                config_path=benchmark.config_path,
                state_from_id=edge.source_state_id,
                state_to_id=edge.target_state_id,
                generator_id=edge.continuation_id,
                phase_mode=phase_label,
                strategy_id=strategy_id,
                source_history_ids=list(source.history_ids),
                target_history_ids=list(target.history_ids),
                source_support_ids=source_support_ids,
                target_support_ids=target_support_ids,
                structural_features={
                    "source_history_count": len(source.history_ids),
                    "target_history_count": len(target.history_ids),
                    "source_support_size": len(source_support_ids),
                    "target_support_size": len(target_support_ids),
                    "support_shift_count": support_shift_count,
                    "source_out_degree": out_degree[edge.source_state_id],
                    "self_loop": edge.source_state_id == edge.target_state_id,
                },
                proxy_features={
                    "uniform_step_cost": 1.0,
                    "source_history_count": len(source.history_ids),
                    "target_history_count": len(target.history_ids),
                },
                provenance={
                    "step_index": edge.step_index,
                    "reachable_graph_snapshot_version": graph.snapshot_version,
                },
            )
        )

    return LowerLayerLedger(
        ledger_id=f"{benchmark.config_id}.lower_layer",
        benchmark_id=benchmark.config_id,
        run_ref=f"config:{benchmark.config_id}",
        config_path=benchmark.config_path,
        phase_mode=phase_label,
        strategy_id=strategy_id,
        state_count=graph.state_count,
        edge_count=graph.edge_count,
        rows=rows,
        warnings=[],
    )


def _positive_support_ids(distribution: dict[str, str]) -> list[str]:
    positive_ids = []
    for support_id, value in sorted(distribution.items()):
        try:
            if Fraction(value) > 0:
                positive_ids.append(support_id)
        except (ValueError, ZeroDivisionError):
            continue
    return positive_ids


__all__ = [
    "HONEST_DEFAULT_PHASE_MODE",
    "BudgetCandidateSelection",
    "LowerLayerLedger",
    "LowerLayerLedgerRow",
    "extract_lower_layer_ledger",
    "resolve_honest_phase_mode",
]
