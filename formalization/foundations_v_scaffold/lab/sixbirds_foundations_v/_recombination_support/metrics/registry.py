from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .library import (
    MetricInputKind,
    MetricResult,
    MetricResultStatus,
    MetricScopeStatus,
    compute_closure_defect,
    compute_closure_deficit,
    compute_perturbation_robustness,
    compute_readout_complexity,
    compute_recombination_additivity_defect,
    compute_recombination_gap_metric,
    compute_route_mismatch,
    compute_support_breadth,
    compute_transport_linearizability_defect,
)


MetricEvaluator = Callable[..., MetricResult]


def _frontier_scaffold_only_metric(metric_name: str) -> MetricEvaluator:
    def _evaluate(metric_input: Any, **_: Any) -> MetricResult:
        input_kind = getattr(metric_input, "input_kind", "frontier_observation")
        if hasattr(input_kind, "value"):
            input_kind = input_kind.value
        return MetricResult(
            metric_name=metric_name,
            status=MetricResultStatus.UNSUPPORTED,
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=str(input_kind),
            assumptions=[
                "ticket27 slice-scaffold metrics are populated directly from the candidate observation ledger",
            ],
            details={"reason": "frontier_scaffold_only_metric"},
        )

    return _evaluate


@dataclass(frozen=True)
class MetricSpec:
    metric_name: str
    scope_status: MetricScopeStatus
    required_input_kinds: tuple[MetricInputKind, ...]
    output_fields: tuple[str, ...]
    default_parameters: dict[str, Any]
    assumption_note: str
    enabled_by_default: bool
    evaluator: MetricEvaluator

    def export_payload(self) -> dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "scope_status": self.scope_status.value,
            "required_input_kinds": [kind.value for kind in self.required_input_kinds],
            "output_fields": list(self.output_fields),
            "default_parameters": dict(self.default_parameters),
            "assumption_note": self.assumption_note,
            "enabled_by_default": self.enabled_by_default,
        }


DEFAULT_METRIC_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "configs"
    / "recombination"
    / "metrics"
    / "default_metric_registry.json"
)

METRIC_REGISTRY: dict[str, MetricSpec] = {
    "closure_defect": MetricSpec(
        metric_name="closure_defect",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.PARTITION_BUNDLE,),
        output_fields=("value", "details.value_exact", "details.max_fiber_size"),
        default_parameters={},
        assumption_note="Uses the inherited exact future-gap semantics when available; otherwise falls back to split-fiber fraction.",
        enabled_by_default=True,
        evaluator=compute_closure_defect,
    ),
    "closure_deficit": MetricSpec(
        metric_name="closure_deficit",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.PARTITION_BUNDLE,),
        output_fields=("value", "details.current_class_count", "details.predictive_class_count"),
        default_parameters={},
        assumption_note="Counts predictive-class excess over the current quotient on the same finite domain.",
        enabled_by_default=True,
        evaluator=compute_closure_deficit,
    ),
    "route_mismatch": MetricSpec(
        metric_name="route_mismatch",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.ROUTE_COMPOSITION_SAMPLES,),
        output_fields=("value", "details.witness_pair", "details.pairwise_scores"),
        default_parameters={},
        assumption_note="Compares exact macro-effect images across route compositions on a shared source-class domain.",
        enabled_by_default=True,
        evaluator=compute_route_mismatch,
    ),
    "recombination_gap": MetricSpec(
        metric_name="recombination_gap",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.PARTITION_BUNDLE,),
        output_fields=(
            "value",
            "details.metric_name",
            "details.branchwise_class_count",
            "details.recombination_class_count",
        ),
        default_parameters={},
        assumption_note="Uses the existing exact runtime recombination-gap diagnostic on the declared observable family.",
        enabled_by_default=True,
        evaluator=compute_recombination_gap_metric,
    ),
    "transport_linearizability_defect": MetricSpec(
        metric_name="transport_linearizability_defect",
        scope_status=MetricScopeStatus.PROVISIONAL,
        required_input_kinds=(MetricInputKind.EMBEDDING_TRANSPORT_SAMPLES,),
        output_fields=("value", "details.per_transition_defect"),
        default_parameters={},
        assumption_note="Fits one affine transport map per transition label and reports normalized residuals.",
        enabled_by_default=True,
        evaluator=compute_transport_linearizability_defect,
    ),
    "recombination_additivity_defect": MetricSpec(
        metric_name="recombination_additivity_defect",
        scope_status=MetricScopeStatus.PROVISIONAL,
        required_input_kinds=(MetricInputKind.EMBEDDING_RECOMBINATION_SAMPLES,),
        output_fields=("value", "details.value_exact", "details.sample_count"),
        default_parameters={},
        assumption_note="Uses the current-scope affine-additive surrogate target ~= a*left + b*right + bias.",
        enabled_by_default=True,
        evaluator=compute_recombination_additivity_defect,
    ),
    "readout_complexity": MetricSpec(
        metric_name="readout_complexity",
        scope_status=MetricScopeStatus.PROVISIONAL,
        required_input_kinds=(MetricInputKind.READOUT_SAMPLES,),
        output_fields=("value", "details.best_coordinate_subset", "details.normalized_ratio"),
        default_parameters={},
        assumption_note="Uses minimum coordinate subset size as the current-scope deterministic readout surrogate.",
        enabled_by_default=True,
        evaluator=compute_readout_complexity,
    ),
    "support_breadth": MetricSpec(
        metric_name="support_breadth",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value", "details.support_size", "details.universe_size"),
        default_parameters={},
        assumption_note="Exact on the declared finite support ids; returns a fraction if a universe is supplied.",
        enabled_by_default=True,
        evaluator=compute_support_breadth,
    ),
    "perturbation_robustness": MetricSpec(
        metric_name="perturbation_robustness",
        scope_status=MetricScopeStatus.PROVISIONAL,
        required_input_kinds=(MetricInputKind.PERTURBATION_BUNDLE,),
        output_fields=("value", "details.tolerance", "details.perturbations"),
        default_parameters={"tolerance": 0.1},
        assumption_note="Current scope compares normalized deltas against a baseline metric bundle; this is not yet the full sweep semantics.",
        enabled_by_default=True,
        evaluator=compute_perturbation_robustness,
    ),
    "ticket27_flagship_gate_supported_count": MetricSpec(
        metric_name="ticket27_flagship_gate_supported_count",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric("ticket27_flagship_gate_supported_count"),
    ),
    "ticket27_flagship_non_fallback_supported_count": MetricSpec(
        metric_name="ticket27_flagship_non_fallback_supported_count",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric("ticket27_flagship_non_fallback_supported_count"),
    ),
    "ticket27_preserved_required_control_contrast_count": MetricSpec(
        metric_name="ticket27_preserved_required_control_contrast_count",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric(
            "ticket27_preserved_required_control_contrast_count"
        ),
    ),
    "ticket27_nearby_positive_supported_count": MetricSpec(
        metric_name="ticket27_nearby_positive_supported_count",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric("ticket27_nearby_positive_supported_count"),
    ),
    "ticket27_best_common_flagship_burden": MetricSpec(
        metric_name="ticket27_best_common_flagship_burden",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric("ticket27_best_common_flagship_burden"),
    ),
    "ticket27_fallback_involved": MetricSpec(
        metric_name="ticket27_fallback_involved",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric("ticket27_fallback_involved"),
    ),
    "ticket27_route_complexity_penalty": MetricSpec(
        metric_name="ticket27_route_complexity_penalty",
        scope_status=MetricScopeStatus.STABLE,
        required_input_kinds=(MetricInputKind.SUPPORT_SNAPSHOT,),
        output_fields=("value",),
        default_parameters={},
        assumption_note="Frontier-only ledger metric for ticket27 slice scaffolding.",
        enabled_by_default=False,
        evaluator=_frontier_scaffold_only_metric("ticket27_route_complexity_penalty"),
    ),
}


def get_metric_spec(metric_name: str) -> MetricSpec:
    return METRIC_REGISTRY[metric_name]


def metric_registry_payload() -> dict[str, Any]:
    return {
        "schema_version": "recombination-default-metric-registry.v1",
        "ticket_scope": "ticket7",
        "note": "This registry file is a project config artifact, not a Ticket 2 canonical schema kind.",
        "metrics": [
            METRIC_REGISTRY[metric_name].export_payload()
            for metric_name in sorted(METRIC_REGISTRY)
        ],
    }


def evaluate_metric(metric_name: str, metric_input: Any, **kwargs: Any) -> MetricResult:
    spec = get_metric_spec(metric_name)
    return spec.evaluator(metric_input, **kwargs)


__all__ = [
    "DEFAULT_METRIC_REGISTRY_PATH",
    "METRIC_REGISTRY",
    "MetricSpec",
    "evaluate_metric",
    "get_metric_spec",
    "metric_registry_payload",
]
