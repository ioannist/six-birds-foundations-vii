from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel

from .ledger import BudgetCandidateSelection, LowerLayerLedger


class BudgetCostStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    NOT_ENOUGH_DATA = "not_enough_data"
    ERROR = "error"


class CandidateCostSummary(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-candidate-cost-summary.v1"
    benchmark_id: str
    candidate_id: str
    source_kind: str
    cost_mode: str
    status: BudgetCostStatus
    aggregated_cost: float | None = None
    normalization: str | None = None
    units: str | None = None
    matched_row_count: int = 0
    assumptions: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


STRUCTURAL_COST_MODE = "structural_lower_layer_cost"
PROXY_UNIFORM_COST_MODE = "proxy_uniform_step_cost"


def list_supported_cost_modes() -> list[str]:
    return [STRUCTURAL_COST_MODE, PROXY_UNIFORM_COST_MODE]


def evaluate_candidate_cost(
    candidate: BudgetCandidateSelection,
    lower_layer_ledger: LowerLayerLedger,
    *,
    cost_mode: str,
) -> CandidateCostSummary:
    if candidate.completion_status != "ok":
        return CandidateCostSummary(
            benchmark_id=candidate.benchmark_id,
            candidate_id=candidate.candidate_id,
            source_kind=candidate.source_kind,
            cost_mode=cost_mode,
            status=BudgetCostStatus.UNSUPPORTED,
            assumptions=["candidate selection must complete successfully before lower-layer costs can be aggregated"],
            details={"completion_status": candidate.completion_status},
            warnings=list(candidate.warnings),
        )

    if cost_mode == STRUCTURAL_COST_MODE:
        return _evaluate_structural_cost(candidate, lower_layer_ledger)
    if cost_mode == PROXY_UNIFORM_COST_MODE:
        return _evaluate_proxy_uniform_cost(candidate)
    return CandidateCostSummary(
        benchmark_id=candidate.benchmark_id,
        candidate_id=candidate.candidate_id,
        source_kind=candidate.source_kind,
        cost_mode=cost_mode,
        status=BudgetCostStatus.UNSUPPORTED,
        assumptions=["unknown cost modes are kept explicit in the budget ledger instead of being dropped"],
        details={"supported_cost_modes": list_supported_cost_modes()},
        warnings=[f"unsupported cost mode {cost_mode!r}"],
    )


def _evaluate_structural_cost(
    candidate: BudgetCandidateSelection,
    lower_layer_ledger: LowerLayerLedger,
) -> CandidateCostSummary:
    selected_history_ids = set(candidate.selected_history_ids)
    matched_rows = [
        row
        for row in lower_layer_ledger.rows
        if set(row.source_history_ids) & selected_history_ids
    ]
    if not matched_rows:
        return CandidateCostSummary(
            benchmark_id=candidate.benchmark_id,
            candidate_id=candidate.candidate_id,
            source_kind=candidate.source_kind,
            cost_mode=STRUCTURAL_COST_MODE,
            status=BudgetCostStatus.NOT_ENOUGH_DATA,
            normalization="sum_of_transition_shift_plus_branching_load",
            units="structural_cost_units",
            assumptions=["the current structural budget uses exact reachable-graph edge rows matched by selected source histories"],
            details={"selected_history_ids": sorted(selected_history_ids)},
            warnings=["no lower-layer rows matched the selected histories"],
        )
    step_costs = [
        float(row.structural_features.get("support_shift_count", 0))
        + float(row.structural_features.get("source_out_degree", 0))
        for row in matched_rows
    ]
    return CandidateCostSummary(
        benchmark_id=candidate.benchmark_id,
        candidate_id=candidate.candidate_id,
        source_kind=candidate.source_kind,
        cost_mode=STRUCTURAL_COST_MODE,
        status=BudgetCostStatus.OK,
        aggregated_cost=float(sum(step_costs)),
        normalization="sum_of_transition_shift_plus_branching_load",
        units="structural_cost_units",
        matched_row_count=len(matched_rows),
        assumptions=[
            "structural lower-layer cost is derived from the canonical reachable-state edge ledger",
            "each matched edge contributes support_shift_count + source_out_degree",
        ],
        details={
            "selected_history_ids": sorted(selected_history_ids),
            "matched_support_atom_ids": [row.support_atom_id for row in matched_rows],
            "per_row_costs": step_costs,
        },
    )


def _evaluate_proxy_uniform_cost(
    candidate: BudgetCandidateSelection,
) -> CandidateCostSummary:
    proxy_cost = float(len(candidate.selected_history_ids))
    return CandidateCostSummary(
        benchmark_id=candidate.benchmark_id,
        candidate_id=candidate.candidate_id,
        source_kind=candidate.source_kind,
        cost_mode=PROXY_UNIFORM_COST_MODE,
        status=BudgetCostStatus.OK,
        aggregated_cost=proxy_cost,
        normalization="selected_history_count",
        units="proxy_step_units",
        matched_row_count=len(candidate.selected_history_ids),
        assumptions=[
            "proxy uniform step cost ignores edge structure and only counts selected lower-history atoms",
        ],
        details={
            "selected_history_ids": list(candidate.selected_history_ids),
        },
    )


__all__ = [
    "BudgetCostStatus",
    "CandidateCostSummary",
    "PROXY_UNIFORM_COST_MODE",
    "STRUCTURAL_COST_MODE",
    "evaluate_candidate_cost",
    "list_supported_cost_modes",
]
