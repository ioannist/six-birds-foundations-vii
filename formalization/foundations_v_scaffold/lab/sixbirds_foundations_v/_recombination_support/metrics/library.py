from __future__ import annotations

from collections import defaultdict
from enum import Enum
from fractions import Fraction
from itertools import combinations
from math import sqrt
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import Field

from sixbirds_foundations_v._holonomy_support.analysis.transport import ClassTransportMap

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel

from ..benchmarks.loader import LoadedBenchmark, ReachableStateGraphSnapshot
from ..carriers import (
    CarrierComputationStatus,
    compute_branchwise_quotient,
    compute_current_quotient,
    compute_eta_factor_map,
    compute_predictive_quotient,
    compute_recombination_quotient,
)
from ..core.diagnostics import compute_recombination_gap as compute_runtime_recombination_gap
from ..core.recombination import (
    compute_recombination_quotient as compute_runtime_recombination_quotient,
)
from ..core.predictive import analyze_inherited_interface


class MetricScopeStatus(str, Enum):
    STABLE = "stable"
    PROVISIONAL = "provisional"


class MetricResultStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    NOT_ENOUGH_DATA = "not_enough_data"
    ERROR = "error"


class MetricInputKind(str, Enum):
    PARTITION_BUNDLE = "partition_bundle"
    REACHABLE_GRAPH = "reachable_graph"
    ROUTE_COMPOSITION_SAMPLES = "route_composition_samples"
    EMBEDDING_TRANSPORT_SAMPLES = "embedding_transport_samples"
    EMBEDDING_RECOMBINATION_SAMPLES = "embedding_recombination_samples"
    READOUT_SAMPLES = "readout_samples"
    SUPPORT_SNAPSHOT = "support_snapshot"
    PERTURBATION_BUNDLE = "perturbation_bundle"


class MetricResult(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-metric-result.v1"
    metric_name: str
    status: MetricResultStatus
    scope_status: MetricScopeStatus
    value: Any = None
    normalization: str | None = None
    units: str | None = None
    input_kind: str
    assumptions: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class PartitionBundleInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-partition-bundle.v1"
    input_kind: MetricInputKind = MetricInputKind.PARTITION_BUNDLE
    benchmark_id: str | None = None
    config_id: str | None = None
    config_path: str | None = None
    executable: bool = True
    loader_kind: str | None = None
    current_class_count: int | None = None
    predictive_class_count: int | None = None
    branchwise_class_count: int | None = None
    recombination_class_count: int | None = None
    recombination_gap_metric_name: str | None = None
    recombination_gap_value: str | None = None
    exact_max_abs_future_gap: str | None = None
    max_fiber_size: int | None = None
    eta_max_fiber_size: int | None = None
    current_element_to_class_id: dict[str, str] = Field(default_factory=dict)
    predictive_element_to_class_id: dict[str, str] = Field(default_factory=dict)
    branchwise_element_to_class_id: dict[str, str] = Field(default_factory=dict)
    recombination_element_to_class_id: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class RouteCompositionSample(SixBirdsRecombinationModel):
    route_id: str
    effect_by_source_id: dict[str, str]
    notes: list[str] = Field(default_factory=list)


class RouteCompositionSamplesInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-route-composition-samples.v1"
    input_kind: MetricInputKind = MetricInputKind.ROUTE_COMPOSITION_SAMPLES
    samples: list[RouteCompositionSample]


class EmbeddingTransportSample(SixBirdsRecombinationModel):
    transition_label: str
    source_vector: list[float]
    target_vector: list[float]


class EmbeddingTransportSamplesInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-embedding-transport-samples.v1"
    input_kind: MetricInputKind = MetricInputKind.EMBEDDING_TRANSPORT_SAMPLES
    samples: list[EmbeddingTransportSample]


class EmbeddingRecombinationSample(SixBirdsRecombinationModel):
    sample_id: str
    left_vector: list[float]
    right_vector: list[float]
    target_vector: list[float]
    left_weight: float = 1.0
    right_weight: float = 1.0


class EmbeddingRecombinationSamplesInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-embedding-recombination-samples.v1"
    input_kind: MetricInputKind = MetricInputKind.EMBEDDING_RECOMBINATION_SAMPLES
    samples: list[EmbeddingRecombinationSample]


class ReadoutSample(SixBirdsRecombinationModel):
    sample_id: str
    features: list[Any]
    label: str


class ReadoutSamplesInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-readout-samples.v1"
    input_kind: MetricInputKind = MetricInputKind.READOUT_SAMPLES
    samples: list[ReadoutSample]


class SupportSnapshotInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-support-snapshot.v1"
    input_kind: MetricInputKind = MetricInputKind.SUPPORT_SNAPSHOT
    support_ids: list[str]
    universe_ids: list[str] | None = None
    notes: list[str] = Field(default_factory=list)


class PerturbationSample(SixBirdsRecombinationModel):
    perturbation_id: str
    values: dict[str, float]


class PerturbationBundleInput(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-perturbation-bundle.v1"
    input_kind: MetricInputKind = MetricInputKind.PERTURBATION_BUNDLE
    baseline_values: dict[str, float]
    perturbations: list[PerturbationSample]


MetricInput = (
    PartitionBundleInput
    | RouteCompositionSamplesInput
    | EmbeddingTransportSamplesInput
    | EmbeddingRecombinationSamplesInput
    | ReadoutSamplesInput
    | SupportSnapshotInput
    | PerturbationBundleInput
)


def partition_bundle_from_benchmark(benchmark: LoadedBenchmark) -> PartitionBundleInput:
    """Build a reusable partition bundle from the canonical benchmark/carrier stack."""
    if not benchmark.executable:
        return PartitionBundleInput(
            benchmark_id=benchmark.benchmark_id,
            config_id=benchmark.config_id,
            config_path=benchmark.config_path,
            executable=False,
            loader_kind=benchmark.loader_kind.value,
            notes=["non-executable summary/search entries cannot supply quotient metrics"],
        )

    current = compute_current_quotient(benchmark)
    predictive = compute_predictive_quotient(benchmark)
    branchwise = compute_branchwise_quotient(benchmark)
    recombination = compute_recombination_quotient(benchmark)
    runtime_recombination = compute_runtime_recombination_quotient(
        benchmark.context,
        benchmark.config.interface_id,
        tuple(sorted(benchmark.assemblages.items(), key=lambda item: item[0])),
        benchmark.observable_family,
    )
    recombination_gap = compute_runtime_recombination_gap(runtime_recombination)
    eta = compute_eta_factor_map(benchmark)
    analysis = analyze_inherited_interface(benchmark.context, benchmark.config.interface_id)
    return PartitionBundleInput(
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        config_path=benchmark.config_path,
        executable=True,
        loader_kind=benchmark.loader_kind.value,
        current_class_count=current.class_count,
        predictive_class_count=predictive.class_count,
        branchwise_class_count=branchwise.class_count,
        recombination_class_count=recombination.class_count,
        recombination_gap_metric_name=recombination_gap.metric_name,
        recombination_gap_value=str(recombination_gap.metric_value),
        exact_max_abs_future_gap=str(analysis.exact_max_abs_future_gap),
        max_fiber_size=analysis.max_fiber_size,
        eta_max_fiber_size=eta.max_fiber_size
        if eta.status is CarrierComputationStatus.SUPPORTED
        else None,
        current_element_to_class_id=dict(current.element_to_class_id),
        predictive_element_to_class_id=dict(predictive.element_to_class_id),
        branchwise_element_to_class_id=dict(branchwise.element_to_class_id),
        recombination_element_to_class_id=dict(recombination.element_to_class_id),
        notes=[
            "partition bundle derived from the canonical benchmark loader and carrier library",
        ],
    )


def compute_recombination_gap_metric(metric_input: MetricInput) -> MetricResult:
    """Expose the canonical recombination-gap diagnostic through the metric registry."""
    expected_kind = MetricInputKind.PARTITION_BUNDLE
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="recombination_gap",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires a partition bundle carrying the exact recombination-gap diagnostic",
            ],
        )
    if not metric_input.executable:
        return _unsupported_result(
            metric_name="recombination_gap",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=metric_input.input_kind.value,
            expected_kind=expected_kind.value,
            assumptions=[
                "non-executable summaries cannot supply a canonical recombination-gap witness",
            ],
            reason="non-executable benchmark entries do not carry the runtime recombination quotient",
        )
    if metric_input.recombination_gap_value is None:
        return _not_enough_data_result(
            metric_name="recombination_gap",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=metric_input.input_kind.value,
            assumptions=[
                "partition bundle must carry recombination_gap_value to evaluate the canonical gap metric",
            ],
        )
    return MetricResult(
        metric_name="recombination_gap",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.STABLE,
        value=float(Fraction(metric_input.recombination_gap_value)),
        normalization="exact_recombination_gap",
        units="probability_gap",
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "uses the existing runtime recombination-gap diagnostic on the declared exact finite observable family",
        ],
        details={
            "metric_name": metric_input.recombination_gap_metric_name or "exact_recombination_gap",
            "branchwise_class_count": metric_input.branchwise_class_count,
            "recombination_class_count": metric_input.recombination_class_count,
        },
    )


def route_composition_samples_from_transport_maps(
    transport_maps: dict[str, ClassTransportMap],
) -> RouteCompositionSamplesInput:
    """Convert inherited class transport maps into route-composition metric samples."""
    return RouteCompositionSamplesInput(
        samples=[
            RouteCompositionSample(
                route_id=route_id,
                effect_by_source_id=dict(transport_map.class_image_by_source_id),
                notes=[
                    f"{transport_map.partition_kind} transport {transport_map.continuation_id}",
                ],
            )
            for route_id, transport_map in sorted(transport_maps.items())
        ]
    )


def support_snapshot_from_reachable_graph(
    graph: ReachableStateGraphSnapshot,
    *,
    universe_ids: list[str] | None = None,
) -> SupportSnapshotInput:
    """Build a support snapshot from a reachable-state graph artifact."""
    support_ids = sorted(
        {
            support_id
            for state in graph.states
            for support_id in state.support_distribution
        }
    )
    return SupportSnapshotInput(
        support_ids=support_ids,
        universe_ids=sorted(set(universe_ids)) if universe_ids is not None else None,
        notes=[f"derived from reachable graph {graph.benchmark_id}"],
    )


def compute_closure_defect(metric_input: MetricInput) -> MetricResult:
    """Quantify predictive residue left hidden inside the current package."""
    expected_kind = MetricInputKind.PARTITION_BUNDLE
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="closure_defect",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires current/predictive partition data on a finite exact scope",
            ],
        )
    bundle = metric_input
    if not bundle.executable:
        return _unsupported_result(
            metric_name="closure_defect",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=bundle.input_kind.value,
            expected_kind=expected_kind.value,
            assumptions=[
                "summary/search entries are not executable metric inputs",
            ],
            reason="partition bundle is marked non-executable",
        )

    gap_source = "provided_exact_gap"
    if bundle.exact_max_abs_future_gap is not None:
        gap = Fraction(bundle.exact_max_abs_future_gap)
    else:
        gap_source = "derived_split_fraction"
        gap = _derived_predictive_split_fraction(bundle)
    return MetricResult(
        metric_name="closure_defect",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.STABLE,
        value=float(gap),
        normalization="unit_interval_exact_fraction",
        units="fraction",
        input_kind=bundle.input_kind.value,
        assumptions=[
            "uses the inherited exact future-gap semantics when available",
            "falls back to the fraction of elements that live in split current fibers",
        ],
        details={
            "value_exact": str(gap),
            "source": gap_source,
            "benchmark_id": bundle.benchmark_id,
            "config_id": bundle.config_id,
            "max_fiber_size": bundle.max_fiber_size,
        },
    )


def compute_closure_deficit(metric_input: MetricInput) -> MetricResult:
    """Measure how many predictive classes are hidden by the current package."""
    expected_kind = MetricInputKind.PARTITION_BUNDLE
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="closure_deficit",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires current and predictive quotient counts on a finite exact scope",
            ],
        )
    bundle = metric_input
    if not bundle.executable:
        return _unsupported_result(
            metric_name="closure_deficit",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=bundle.input_kind.value,
            expected_kind=expected_kind.value,
            assumptions=[
                "summary/search entries are not executable metric inputs",
            ],
            reason="partition bundle is marked non-executable",
        )
    current_count = bundle.current_class_count or _count_classes(bundle.current_element_to_class_id)
    predictive_count = bundle.predictive_class_count or _count_classes(
        bundle.predictive_element_to_class_id
    )
    deficit = predictive_count - current_count
    return MetricResult(
        metric_name="closure_deficit",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.STABLE,
        value=deficit,
        normalization="predictive_minus_current_class_count",
        units="classes",
        input_kind=bundle.input_kind.value,
        assumptions=[
            "counts hidden predictive classes rather than distributional disagreement",
        ],
        details={
            "current_class_count": current_count,
            "predictive_class_count": predictive_count,
            "max_fiber_size": bundle.max_fiber_size,
        },
    )


def compute_route_mismatch(metric_input: MetricInput) -> MetricResult:
    """Measure exact macro-effect disagreement across route compositions."""
    expected_kind = MetricInputKind.ROUTE_COMPOSITION_SAMPLES
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="route_mismatch",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires route-level macro-effect samples on a shared finite source domain",
            ],
        )
    samples = metric_input.samples
    if len(samples) < 2:
        return MetricResult(
            metric_name="route_mismatch",
            status=MetricResultStatus.NOT_ENOUGH_DATA,
            scope_status=MetricScopeStatus.STABLE,
            value=None,
            normalization="pairwise_fraction_of_source_effects",
            units="fraction",
            input_kind=metric_input.input_kind.value,
            assumptions=[
                "at least two route samples are needed for pairwise comparison",
            ],
            details={"sample_count": len(samples)},
        )

    pairwise_scores: list[dict[str, Any]] = []
    best_pair: tuple[str, str] | None = None
    max_score = Fraction(0, 1)
    for left, right in combinations(samples, 2):
        source_ids = sorted(set(left.effect_by_source_id) | set(right.effect_by_source_id))
        mismatches = sum(
            1
            for source_id in source_ids
            if left.effect_by_source_id.get(source_id) != right.effect_by_source_id.get(source_id)
        )
        score = Fraction(mismatches, len(source_ids))
        pairwise_scores.append(
            {
                "left_route_id": left.route_id,
                "right_route_id": right.route_id,
                "mismatch_count": mismatches,
                "source_count": len(source_ids),
                "mismatch_fraction": str(score),
            }
        )
        if score > max_score:
            max_score = score
            best_pair = (left.route_id, right.route_id)

    return MetricResult(
        metric_name="route_mismatch",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.STABLE,
        value=float(max_score),
        normalization="max_pairwise_fraction_of_source_effects",
        units="fraction",
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "route effects are compared as exact macro-effect images on shared source classes",
        ],
        details={
            "value_exact": str(max_score),
            "pairwise_scores": pairwise_scores,
            "witness_pair": list(best_pair) if best_pair is not None else None,
        },
    )


def compute_transport_linearizability_defect(metric_input: MetricInput) -> MetricResult:
    """Fit per-transition affine transport maps and report normalized residual defect."""
    expected_kind = MetricInputKind.EMBEDDING_TRANSPORT_SAMPLES
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="transport_linearizability_defect",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires explicit embedding transport samples",
            ],
        )
    if not metric_input.samples:
        return _not_enough_data_result(
            metric_name="transport_linearizability_defect",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=["at least one embedding transport sample is required"],
        )

    try:
        defects: dict[str, float] = {}
        exact_defects: dict[str, str] = {}
        for transition_label, rows in _group_transport_rows(metric_input.samples).items():
            source_matrix = np.asarray([row.source_vector for row in rows], dtype=float)
            target_matrix = np.asarray([row.target_vector for row in rows], dtype=float)
            defect = _affine_residual_defect(source_matrix, target_matrix)
            defects[transition_label] = defect
            exact_defects[transition_label] = _format_float(defect)
    except ValueError as exc:
        return _error_result(
            metric_name="transport_linearizability_defect",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=[
                "all transport samples must share a vector dimension within each transition label",
            ],
            reason=str(exc),
        )

    overall = max(defects.values(), default=0.0)
    return MetricResult(
        metric_name="transport_linearizability_defect",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.PROVISIONAL,
        value=overall,
        normalization="max_per_transition_normalized_rmse",
        units="normalized_residual",
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "fits one affine transport map per transition label",
            "normalizes by the RMS scale of the target embeddings",
        ],
        details={
            "per_transition_defect": exact_defects,
            "transition_count": len(defects),
            "sample_count": len(metric_input.samples),
        },
    )


def compute_recombination_additivity_defect(metric_input: MetricInput) -> MetricResult:
    """Fit an affine-additive recombination law and report normalized residual defect."""
    expected_kind = MetricInputKind.EMBEDDING_RECOMBINATION_SAMPLES
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="recombination_additivity_defect",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires explicit embedding recombination samples",
            ],
        )
    if not metric_input.samples:
        return _not_enough_data_result(
            metric_name="recombination_additivity_defect",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=["at least one embedding recombination sample is required"],
        )

    try:
        basis_rows = np.asarray(
            [
                [
                    *(sample.left_weight * value for value in sample.left_vector),
                    *(sample.right_weight * value for value in sample.right_vector),
                ]
                for sample in metric_input.samples
            ],
            dtype=float,
        )
        targets = np.asarray(
            [sample.target_vector for sample in metric_input.samples],
            dtype=float,
        )
        defect = _affine_residual_defect(basis_rows, targets)
    except ValueError as exc:
        return _error_result(
            metric_name="recombination_additivity_defect",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=[
                "left, right, and target vectors must have consistent dimensions",
            ],
            reason=str(exc),
        )

    return MetricResult(
        metric_name="recombination_additivity_defect",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.PROVISIONAL,
        value=defect,
        normalization="normalized_rmse_against_affine_additive_law",
        units="normalized_residual",
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "uses the current-scope affine-additive law target ~= a*left + b*right + bias",
        ],
        details={
            "sample_count": len(metric_input.samples),
            "value_exact": _format_float(defect),
        },
    )


def compute_readout_complexity(metric_input: MetricInput) -> MetricResult:
    """Estimate the minimum coordinate count needed for deterministic finite readout."""
    expected_kind = MetricInputKind.READOUT_SAMPLES
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="readout_complexity",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires labeled readout samples over explicit coordinate features",
            ],
        )
    if not metric_input.samples:
        return _not_enough_data_result(
            metric_name="readout_complexity",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=["at least one readout sample is required"],
        )

    feature_dim = len(metric_input.samples[0].features)
    if any(len(sample.features) != feature_dim for sample in metric_input.samples):
        return _error_result(
            metric_name="readout_complexity",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=["all readout samples must have the same feature dimension"],
            reason="inconsistent feature dimensions",
        )

    best_subset: tuple[int, ...] | None = None
    for subset_size in range(1, feature_dim + 1):
        for subset in combinations(range(feature_dim), subset_size):
            if _projection_is_label_deterministic(metric_input.samples, subset):
                best_subset = subset
                break
        if best_subset is not None:
            break

    if best_subset is None:
        return _error_result(
            metric_name="readout_complexity",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=[
                "full feature vectors must at least determine labels on the sample set",
            ],
            reason="sample labels are inconsistent even under the full coordinate set",
        )

    return MetricResult(
        metric_name="readout_complexity",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.PROVISIONAL,
        value=len(best_subset),
        normalization="minimum_coordinate_subset_size",
        units="coordinates",
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "current scope uses minimum coordinate subset size as a deterministic readout surrogate",
        ],
        details={
            "feature_dim": feature_dim,
            "best_coordinate_subset": list(best_subset),
            "normalized_ratio": len(best_subset) / max(feature_dim, 1),
            "sample_count": len(metric_input.samples),
            "label_count": len({sample.label for sample in metric_input.samples}),
        },
    )


def compute_support_breadth(metric_input: MetricInput) -> MetricResult:
    """Measure support-set coverage breadth on the declared finite support."""
    expected_kind = MetricInputKind.SUPPORT_SNAPSHOT
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="support_breadth",
            scope_status=MetricScopeStatus.STABLE,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires an explicit support snapshot",
            ],
        )
    support_ids = sorted(set(metric_input.support_ids))
    universe_ids = sorted(set(metric_input.universe_ids)) if metric_input.universe_ids else None
    if universe_ids:
        value = len(support_ids) / len(universe_ids)
        normalization = "support_fraction_of_declared_universe"
        units = "fraction"
    else:
        value = len(support_ids)
        normalization = "support_count"
        units = "support_states"

    return MetricResult(
        metric_name="support_breadth",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.STABLE,
        value=value,
        normalization=normalization,
        units=units,
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "support breadth is exact on the declared finite support ids",
        ],
        details={
            "support_size": len(support_ids),
            "universe_size": len(universe_ids) if universe_ids is not None else None,
        },
    )


def compute_perturbation_robustness(
    metric_input: MetricInput,
    *,
    tolerance: float = 0.1,
) -> MetricResult:
    """Summarize metric-bundle stability under perturbed comparisons."""
    expected_kind = MetricInputKind.PERTURBATION_BUNDLE
    if not _has_input_kind(metric_input, expected_kind):
        return _unsupported_result(
            metric_name="perturbation_robustness",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=_input_kind_name(metric_input),
            expected_kind=expected_kind.value,
            assumptions=[
                "requires a baseline metric bundle plus perturbed bundle samples",
            ],
        )
    if not metric_input.perturbations:
        return _not_enough_data_result(
            metric_name="perturbation_robustness",
            scope_status=MetricScopeStatus.PROVISIONAL,
            input_kind=metric_input.input_kind.value,
            assumptions=["at least one perturbation bundle is required"],
        )

    perturbation_rows: list[dict[str, Any]] = []
    stable_count = 0
    for perturbation in metric_input.perturbations:
        shared_keys = sorted(
            set(metric_input.baseline_values).intersection(perturbation.values)
        )
        if not shared_keys:
            return _not_enough_data_result(
                metric_name="perturbation_robustness",
                scope_status=MetricScopeStatus.PROVISIONAL,
                input_kind=metric_input.input_kind.value,
                assumptions=[
                    "baseline and perturbed bundles must share at least one metric key",
                ],
            )
        normalized_deltas = [
            abs(perturbation.values[key] - metric_input.baseline_values[key])
            / max(abs(metric_input.baseline_values[key]), 1.0)
            for key in shared_keys
        ]
        max_normalized_delta = max(normalized_deltas)
        mean_normalized_delta = sum(normalized_deltas) / len(normalized_deltas)
        is_stable = max_normalized_delta <= tolerance
        stable_count += int(is_stable)
        perturbation_rows.append(
            {
                "perturbation_id": perturbation.perturbation_id,
                "shared_metric_keys": shared_keys,
                "max_normalized_delta": _format_float(max_normalized_delta),
                "mean_normalized_delta": _format_float(mean_normalized_delta),
                "stable_under_tolerance": is_stable,
            }
        )

    stable_fraction = stable_count / len(metric_input.perturbations)
    return MetricResult(
        metric_name="perturbation_robustness",
        status=MetricResultStatus.OK,
        scope_status=MetricScopeStatus.PROVISIONAL,
        value=stable_fraction,
        normalization="fraction_of_perturbations_within_tolerance",
        units="fraction",
        input_kind=metric_input.input_kind.value,
        assumptions=[
            "current scope compares metric bundles by normalized delta against the baseline",
            f"perturbations are counted stable when max normalized delta <= {tolerance}",
        ],
        details={
            "tolerance": tolerance,
            "stable_count": stable_count,
            "perturbation_count": len(metric_input.perturbations),
            "perturbations": perturbation_rows,
        },
    )


def _derived_predictive_split_fraction(bundle: PartitionBundleInput) -> Fraction:
    current_groups = _groups_by_class_id(bundle.current_element_to_class_id)
    if not current_groups:
        return Fraction(0, 1)
    split_elements = 0
    total_elements = len(bundle.current_element_to_class_id)
    for members in current_groups.values():
        predictive_classes = {
            bundle.predictive_element_to_class_id.get(member_id)
            for member_id in members
        }
        predictive_classes.discard(None)
        if len(predictive_classes) > 1:
            split_elements += len(members)
    return Fraction(split_elements, max(total_elements, 1))


def _group_transport_rows(
    rows: list[EmbeddingTransportSample],
) -> dict[str, list[EmbeddingTransportSample]]:
    grouped: dict[str, list[EmbeddingTransportSample]] = defaultdict(list)
    for row in rows:
        grouped[row.transition_label].append(row)
    return dict(grouped)


def _affine_residual_defect(source_matrix: np.ndarray, target_matrix: np.ndarray) -> float:
    if source_matrix.ndim != 2 or target_matrix.ndim != 2:
        raise ValueError("source and target matrices must both be rank-2")
    if source_matrix.shape[0] != target_matrix.shape[0]:
        raise ValueError("source and target sample counts must match")
    if source_matrix.shape[0] == 0:
        return 0.0
    design = np.concatenate(
        [source_matrix, np.ones((source_matrix.shape[0], 1), dtype=float)],
        axis=1,
    )
    coefficients, _, _, _ = np.linalg.lstsq(design, target_matrix, rcond=None)
    predicted = design @ coefficients
    residual = target_matrix - predicted
    residual_rms = sqrt(float(np.mean(np.sum(residual * residual, axis=1))))
    target_rms = sqrt(float(np.mean(np.sum(target_matrix * target_matrix, axis=1))))
    return residual_rms / max(target_rms, 1e-12)


def _projection_is_label_deterministic(
    samples: list[ReadoutSample],
    subset: tuple[int, ...],
) -> bool:
    labels_by_projection: dict[tuple[Any, ...], str] = {}
    for sample in samples:
        projection = tuple(sample.features[index] for index in subset)
        prior = labels_by_projection.get(projection)
        if prior is None:
            labels_by_projection[projection] = sample.label
            continue
        if prior != sample.label:
            return False
    return True


def _groups_by_class_id(element_to_class_id: dict[str, str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for element_id, class_id in sorted(element_to_class_id.items()):
        groups[class_id].append(element_id)
    return dict(groups)


def _count_classes(element_to_class_id: dict[str, str]) -> int:
    return len(set(element_to_class_id.values()))


def _has_input_kind(metric_input: Any, expected_kind: MetricInputKind) -> bool:
    return getattr(metric_input, "input_kind", None) == expected_kind


def _input_kind_name(metric_input: Any) -> str:
    input_kind = getattr(metric_input, "input_kind", None)
    if isinstance(input_kind, MetricInputKind):
        return input_kind.value
    if isinstance(input_kind, str):
        return input_kind
    return type(metric_input).__name__


def _unsupported_result(
    *,
    metric_name: str,
    scope_status: MetricScopeStatus,
    input_kind: str,
    expected_kind: str,
    assumptions: list[str],
    reason: str | None = None,
) -> MetricResult:
    details = {"expected_input_kind": expected_kind}
    if reason is not None:
        details["reason"] = reason
    return MetricResult(
        metric_name=metric_name,
        status=MetricResultStatus.UNSUPPORTED,
        scope_status=scope_status,
        value=None,
        normalization=None,
        units=None,
        input_kind=input_kind,
        assumptions=assumptions,
        details=details,
    )


def _not_enough_data_result(
    *,
    metric_name: str,
    scope_status: MetricScopeStatus,
    input_kind: str,
    assumptions: list[str],
) -> MetricResult:
    return MetricResult(
        metric_name=metric_name,
        status=MetricResultStatus.NOT_ENOUGH_DATA,
        scope_status=scope_status,
        value=None,
        normalization=None,
        units=None,
        input_kind=input_kind,
        assumptions=assumptions,
        details={},
    )


def _error_result(
    *,
    metric_name: str,
    scope_status: MetricScopeStatus,
    input_kind: str,
    assumptions: list[str],
    reason: str,
) -> MetricResult:
    return MetricResult(
        metric_name=metric_name,
        status=MetricResultStatus.ERROR,
        scope_status=scope_status,
        value=None,
        normalization=None,
        units=None,
        input_kind=input_kind,
        assumptions=assumptions,
        details={"reason": reason},
    )


def _format_float(value: float) -> str:
    return f"{value:.12g}"


__all__ = [
    "EmbeddingRecombinationSample",
    "EmbeddingRecombinationSamplesInput",
    "EmbeddingTransportSample",
    "EmbeddingTransportSamplesInput",
    "MetricInputKind",
    "MetricResult",
    "MetricResultStatus",
    "MetricScopeStatus",
    "PartitionBundleInput",
    "PerturbationBundleInput",
    "PerturbationSample",
    "ReadoutSample",
    "ReadoutSamplesInput",
    "RouteCompositionSample",
    "RouteCompositionSamplesInput",
    "SupportSnapshotInput",
    "compute_closure_defect",
    "compute_closure_deficit",
    "compute_perturbation_robustness",
    "compute_readout_complexity",
    "compute_recombination_additivity_defect",
    "compute_recombination_gap_metric",
    "compute_route_mismatch",
    "compute_support_breadth",
    "compute_transport_linearizability_defect",
    "partition_bundle_from_benchmark",
    "route_composition_samples_from_transport_maps",
    "support_snapshot_from_reachable_graph",
]
