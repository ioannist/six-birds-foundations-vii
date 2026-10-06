from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel


class CandidateMetricStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    NOT_ENOUGH_DATA = "not_enough_data"
    ERROR = "error"


class FrontierComparisonStatus(str, Enum):
    COMPARABLE = "comparable"
    EXCLUDED_NO_SUPPORT = "excluded_no_support"
    EXCLUDED_INCOMPLETE_SUPPORT = "excluded_incomplete_support"
    EXCLUDED_MISSING_REQUIRED_TERM = "excluded_missing_required_term"
    NON_COMPARABLE = "non_comparable"


class CandidateMetricObservation(SixBirdsRecombinationModel):
    metric_name: str
    status: CandidateMetricStatus
    scope_status: str
    value: float | int | None = None
    units: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class CandidateObservationRow(SixBirdsRecombinationModel):
    candidate_id: str
    support_atom_id: str
    benchmark_id: str
    source_kind: str
    support_cone_tags: list[str] = Field(default_factory=list)
    control_mode: str | None = None
    phase_mode: str | None = None
    strategy_id: str | None = None
    comparison_group: str | None = None
    tags: list[str] = Field(default_factory=list)
    metric_results: dict[str, CandidateMetricObservation]
    provenance: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class CandidateObservationLedger(SixBirdsRecombinationModel):
    schema_version: str = "recombination-candidate-observation-ledger.v1"
    ledger_id: str
    rows: list[CandidateObservationRow]


class FrontierTermAggregate(SixBirdsRecombinationModel):
    metric_name: str
    direction: str
    aggregation_op: str
    required: bool
    weight: float | None = None
    aggregated_value: float | None = None
    support_atom_count: int = 0
    missing_support_atom_ids: list[str] = Field(default_factory=list)
    unsupported_support_atom_ids: list[str] = Field(default_factory=list)


class ConeTransferSummary(SixBirdsRecombinationModel):
    eligible: bool
    replacement_candidates: list[str] = Field(default_factory=list)
    transfer_reason: str


class FrontierResultRow(SixBirdsRecombinationModel):
    slice_id: str
    candidate_id: str
    support_cone_id: str
    comparison_status: FrontierComparisonStatus
    aggregated_yield_vector: dict[str, float] = Field(default_factory=dict)
    aggregated_cost_vector: dict[str, float] = Field(default_factory=dict)
    term_aggregates: dict[str, FrontierTermAggregate] = Field(default_factory=dict)
    dominated_by: list[str] = Field(default_factory=list)
    dominates: list[str] = Field(default_factory=list)
    frontier_member: bool = False
    cone_equivalence_class_id: str | None = None
    transfer_summary: ConeTransferSummary
    warnings: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class ConeEquivalenceClass(SixBirdsRecombinationModel):
    slice_id: str
    support_cone_id: str
    class_id: str
    candidate_ids: list[str]
    frontier_status_transferable: bool


class FrontierEvaluationResult(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-frontier-evaluation.v1"
    slice_id: str
    support_cone_id: str
    candidate_count: int
    support_atom_count: int
    rows: list[FrontierResultRow]
    frontier_candidate_ids: list[str] = Field(default_factory=list)
    cone_equivalence_classes: list[ConeEquivalenceClass] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


__all__ = [
    "CandidateMetricObservation",
    "CandidateMetricStatus",
    "CandidateObservationLedger",
    "CandidateObservationRow",
    "ConeEquivalenceClass",
    "ConeTransferSummary",
    "FrontierComparisonStatus",
    "FrontierEvaluationResult",
    "FrontierResultRow",
    "FrontierTermAggregate",
]
