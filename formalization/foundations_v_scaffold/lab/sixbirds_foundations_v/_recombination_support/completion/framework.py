from __future__ import annotations

from enum import Enum
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType
from typing import Any

from sixbirds_foundations_v._holonomy_support.core.exact import compose_row_stochastic_kernels
from sixbirds_foundations_v._holonomy_support.core.runtime import ContinuationKernelRuntime, RouteTransportPackage
from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel

from ..benchmarks.loader import (
    LoadedBenchmark,
    ReachableStateGraphSnapshot,
    build_reachable_state_graph_snapshot,
    load_benchmark,
)
from ..core.observables import build_observable_family
from ..core.substrate import InheritedBenchmarkContext
from ..carriers import (
    CarrierComputationStatus,
    MinimalBehavioralCarrierResult,
    QuotientResult,
    compute_branchwise_quotient,
    compute_minimal_behavioral_carrier,
    compute_predictive_quotient,
    compute_recombination_quotient,
)


class CompletionStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    NOT_ENOUGH_DATA = "not_enough_data"
    ERROR = "error"


class CompletionInputKind(str, Enum):
    BENCHMARK_REQUEST = "benchmark_request"
    SOURCE_SURFACE_REQUEST = "source_surface_request"


class CompletionSourceKind(str, Enum):
    PREDICTIVE_QUOTIENT = "predictive_quotient"
    BRANCHWISE_QUOTIENT = "branchwise_quotient"
    RECOMBINATION_QUOTIENT = "recombination_quotient"
    MINIMAL_BEHAVIORAL_CARRIER = "minimal_behavioral_carrier"


class CompletionFamilyId(str, Enum):
    DECLARED_COMPLETION_FAMILY = "declared_completion_family"
    REACHABLE_CONTINUATION_EXPANSION = "reachable_continuation_expansion"
    PAIRED_OBSERVABLE_ENRICHMENT = "paired_observable_enrichment"


class CompletionFamilyStatus(str, Enum):
    OK = "ok"
    UNSUPPORTED = "unsupported"
    NOT_ENOUGH_DATA = "not_enough_data"
    ARTIFACT_CONTEXT_EXCLUDED = "artifact_context_excluded"


class FlatteningControlMode(str, Enum):
    NONE = "none"
    PAIRED_FLATTENING_CONTROL = "paired_flattening_control"


class CompletionCandidate(SixBirdsRecombinationModel):
    candidate_id: str
    candidate_type: str
    lower_member_ids: list[str] = Field(default_factory=list)
    branch_member_count: int | None = None
    total_weight: str | None = None
    max_member_weight: str | None = None
    predictive_signature_key: Any = None
    candidate_signature: Any = None
    details: dict[str, Any] = Field(default_factory=dict)


class CompletionClassSurface(SixBirdsRecombinationModel):
    class_id: str
    default_representative_id: str
    candidates: list[CompletionCandidate]
    notes: list[str] = Field(default_factory=list)


class CompletionSourceSurface(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-completion-source-surface.v1"
    source_kind: CompletionSourceKind
    benchmark_id: str | None = None
    config_id: str | None = None
    config_path: str | None = None
    source_result_ref: str
    class_count: int
    executable: bool = True
    classes: list[CompletionClassSurface]
    warnings: list[str] = Field(default_factory=list)


class CompletionMetricInputHints(SixBirdsRecombinationModel):
    supports_partition_bundle: bool
    supports_route_composition_samples: bool
    supports_embedding_transport_samples: bool
    supports_embedding_recombination_samples: bool
    supports_support_snapshot: bool
    suggested_metric_names: list[str] = Field(default_factory=list)


class FlatteningControlProvenance(SixBirdsRecombinationModel):
    mode: FlatteningControlMode
    active: bool
    benchmark_has_flattening_flag: bool = False
    partner_config_path: str | None = None
    partner_config_id: str | None = None
    partner_benchmark_id: str | None = None
    partner_source_kind: str | None = None
    partner_strategy_id: str | None = None
    partner_representative_mapping: dict[str, str] = Field(default_factory=dict)
    shared_class_ids: list[str] = Field(default_factory=list)
    shared_representatives_match: bool | None = None
    warnings: list[str] = Field(default_factory=list)


class CompletionProvenance(SixBirdsRecombinationModel):
    strategy_id: str
    strategy_registry_path: str
    family_id: CompletionFamilyId = CompletionFamilyId.DECLARED_COMPLETION_FAMILY
    family_registry_path: str
    benchmark_id: str | None = None
    config_id: str | None = None
    config_path: str | None = None
    source_kind: str
    source_result_ref: str
    candidate_pool_sizes_by_class: dict[str, int] = Field(default_factory=dict)
    deterministic_tie_break_rule: str
    weight_source: str | None = None
    feature_basis: str | None = None
    fallback_used: str | None = None
    family_effect_summary: dict[str, Any] = Field(default_factory=dict)
    flattening_control: FlatteningControlProvenance
    warnings: list[str] = Field(default_factory=list)


class ClassCompletionSelection(SixBirdsRecombinationModel):
    class_id: str
    selected_representative_id: str
    candidate_count: int
    candidate_ids: list[str]
    tie_break_rule: str
    score_summary: dict[str, Any] = Field(default_factory=dict)


class CompletionResult(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-completion-result.v1"
    strategy_id: str
    family_id: CompletionFamilyId = CompletionFamilyId.DECLARED_COMPLETION_FAMILY
    family_status: CompletionFamilyStatus = CompletionFamilyStatus.OK
    status: CompletionStatus
    input_kind: CompletionInputKind
    source_kind: CompletionSourceKind
    benchmark_id: str | None = None
    config_id: str | None = None
    config_path: str | None = None
    representative_mapping: dict[str, str] = Field(default_factory=dict)
    representative_candidate_counts: dict[str, int] = Field(default_factory=dict)
    class_selections: list[ClassCompletionSelection] = Field(default_factory=list)
    deterministic_tie_break_metadata: dict[str, str] = Field(default_factory=dict)
    induced_lower_level_transport_summary: dict[str, Any] | None = None
    metric_input_hints: CompletionMetricInputHints
    provenance: CompletionProvenance
    warnings: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class CompletionRequest(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-completion-request.v1"
    input_kind: CompletionInputKind
    source_kind: CompletionSourceKind
    strategy_id: str
    family_id: CompletionFamilyId = CompletionFamilyId.DECLARED_COMPLETION_FAMILY
    config_path: str | None = None
    source_surface: CompletionSourceSurface | None = None
    strategy_parameters: dict[str, Any] = Field(default_factory=dict)
    flattening_mode: FlatteningControlMode = FlatteningControlMode.NONE
    flattening_parameters: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = None


class CompletionFamilyBenchmarkView(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-completion-family-view.v1"
    family_id: CompletionFamilyId
    status: CompletionFamilyStatus
    benchmark: LoadedBenchmark | None = None
    effect_summary: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


TICKET27_FLATTENING_PARTNER_NOTE_PREFIX = "ticket27_flattening_partner_config_path="


def apply_completion_request(
    request: CompletionRequest,
    *,
    benchmark: LoadedBenchmark | None = None,
    _allow_flattening_recursion: bool = True,
) -> CompletionResult:
    """Apply a named representative-selection strategy to a benchmark-backed or synthetic source."""
    from .registry import (
        DEFAULT_FAMILY_REGISTRY_PATH,
        DEFAULT_STRATEGY_REGISTRY_PATH,
        get_strategy_spec,
    )

    strategy_spec = get_strategy_spec(request.strategy_id)
    warnings: list[str] = []

    try:
        surface, resolved_benchmark, family_view = _resolve_source_surface(
            request,
            benchmark=benchmark,
        )
    except Exception as exc:
        return _error_result(
            request,
            reason=str(exc),
            registry_path=DEFAULT_STRATEGY_REGISTRY_PATH,
            family_registry_path=DEFAULT_FAMILY_REGISTRY_PATH,
        )

    warnings.extend(family_view.warnings)

    if family_view.status is not CompletionFamilyStatus.OK:
        reason = "; ".join(family_view.warnings) if family_view.warnings else (
            f"completion family {request.family_id.value} is {family_view.status.value}"
        )
        return _unsupported_result(
            request,
            benchmark=resolved_benchmark,
            surface=surface,
            registry_path=DEFAULT_STRATEGY_REGISTRY_PATH,
            family_registry_path=DEFAULT_FAMILY_REGISTRY_PATH,
            family_status=family_view.status,
            family_effect_summary=family_view.effect_summary,
            reason=reason,
        )

    if not surface.executable and request.input_kind is CompletionInputKind.BENCHMARK_REQUEST:
        return _unsupported_result(
            request,
            benchmark=resolved_benchmark,
            surface=surface,
            registry_path=DEFAULT_STRATEGY_REGISTRY_PATH,
            family_registry_path=DEFAULT_FAMILY_REGISTRY_PATH,
            family_status=family_view.status,
            family_effect_summary=family_view.effect_summary,
            reason="completion requires an executable benchmark-backed source surface",
        )

    if request.source_kind not in strategy_spec.supported_source_kinds:
        return _unsupported_result(
            request,
            benchmark=resolved_benchmark,
            surface=surface,
            registry_path=DEFAULT_STRATEGY_REGISTRY_PATH,
            family_registry_path=DEFAULT_FAMILY_REGISTRY_PATH,
            family_status=family_view.status,
            family_effect_summary=family_view.effect_summary,
            reason=(
                f"strategy {request.strategy_id} does not support source kind "
                f"{request.source_kind.value}"
            ),
        )

    class_selections: list[ClassCompletionSelection] = []
    representative_mapping: dict[str, str] = {}
    candidate_counts: dict[str, int] = {}
    fallback_by_class: dict[str, str] = {}
    tie_break_rule = strategy_spec.default_tie_break_rule
    for completion_class in surface.classes:
        try:
            selection = strategy_spec.strategy(completion_class, request)
        except ValueError as exc:
            return _unsupported_result(
                request,
                benchmark=resolved_benchmark,
                surface=surface,
                registry_path=DEFAULT_STRATEGY_REGISTRY_PATH,
                family_registry_path=DEFAULT_FAMILY_REGISTRY_PATH,
                family_status=family_view.status,
                family_effect_summary=family_view.effect_summary,
                reason=str(exc),
            )
        representative_mapping[completion_class.class_id] = selection.selected_candidate_id
        candidate_ids = [candidate.candidate_id for candidate in completion_class.candidates]
        candidate_counts[completion_class.class_id] = len(candidate_ids)
        class_selections.append(
            ClassCompletionSelection(
                class_id=completion_class.class_id,
                selected_representative_id=selection.selected_candidate_id,
                candidate_count=len(candidate_ids),
                candidate_ids=candidate_ids,
                tie_break_rule=selection.tie_break_rule,
                score_summary=selection.score_summary,
            )
        )
        if selection.fallback_used is not None:
            fallback_by_class[completion_class.class_id] = selection.fallback_used
        tie_break_rule = selection.tie_break_rule

    flattening_provenance = _build_flattening_control_provenance(
        request,
        benchmark=resolved_benchmark,
        representative_mapping=representative_mapping,
        _allow_flattening_recursion=_allow_flattening_recursion,
    )
    warnings.extend(surface.warnings)
    warnings.extend(flattening_provenance.warnings)

    return CompletionResult(
        strategy_id=request.strategy_id,
        family_id=request.family_id,
        family_status=family_view.status,
        status=CompletionStatus.OK,
        input_kind=request.input_kind,
        source_kind=request.source_kind,
        benchmark_id=surface.benchmark_id,
        config_id=surface.config_id,
        config_path=surface.config_path,
        representative_mapping=representative_mapping,
        representative_candidate_counts=candidate_counts,
        class_selections=class_selections,
        deterministic_tie_break_metadata={
            "strategy_deterministic": str(strategy_spec.deterministic).lower(),
            "tie_break_rule": tie_break_rule,
        },
        induced_lower_level_transport_summary=_build_transport_summary(
            resolved_benchmark,
            request.source_kind,
        ),
        metric_input_hints=_build_metric_input_hints(
            benchmark=resolved_benchmark,
            source_kind=request.source_kind,
        ),
        provenance=CompletionProvenance(
            strategy_id=request.strategy_id,
            strategy_registry_path=_repo_relative(DEFAULT_STRATEGY_REGISTRY_PATH),
            family_id=request.family_id,
            family_registry_path=_repo_relative(DEFAULT_FAMILY_REGISTRY_PATH),
            benchmark_id=surface.benchmark_id,
            config_id=surface.config_id,
            config_path=surface.config_path,
            source_kind=request.source_kind.value,
            source_result_ref=surface.source_result_ref,
            candidate_pool_sizes_by_class=candidate_counts,
            deterministic_tie_break_rule=tie_break_rule,
            weight_source=strategy_spec.weight_source,
            feature_basis=strategy_spec.feature_basis,
            fallback_used=(
                ", ".join(
                    f"{class_id}:{fallback_reason}"
                    for class_id, fallback_reason in sorted(fallback_by_class.items())
                )
                if fallback_by_class
                else None
            ),
            family_effect_summary=family_view.effect_summary,
            flattening_control=flattening_provenance,
            warnings=warnings,
        ),
        warnings=warnings,
        details={
            "strategy_parameters": request.strategy_parameters,
            "flattening_parameters": request.flattening_parameters,
            "source_surface_class_count": surface.class_count,
            "fallback_by_class": fallback_by_class,
        },
    )


def build_completion_source_surface(
    benchmark: LoadedBenchmark,
    source_kind: CompletionSourceKind,
) -> CompletionSourceSurface:
    """Build the canonical completion source surface from the benchmark/carrier stack."""
    if not benchmark.executable:
        return CompletionSourceSurface(
            source_kind=source_kind,
            benchmark_id=benchmark.benchmark_id,
            config_id=benchmark.config_id,
            config_path=benchmark.config_path,
            source_result_ref=f"carrier:{source_kind.value}",
            class_count=0,
            executable=False,
            classes=[],
            warnings=[
                "summary/search entries do not expose executable completion source surfaces",
            ],
        )
    if source_kind is CompletionSourceKind.PREDICTIVE_QUOTIENT:
        return _surface_from_predictive_quotient(benchmark)
    if source_kind is CompletionSourceKind.BRANCHWISE_QUOTIENT:
        return _surface_from_assemblage_quotient(
            benchmark,
            source_kind=source_kind,
            quotient=compute_branchwise_quotient(benchmark),
        )
    if source_kind is CompletionSourceKind.RECOMBINATION_QUOTIENT:
        return _surface_from_assemblage_quotient(
            benchmark,
            source_kind=source_kind,
            quotient=compute_recombination_quotient(benchmark),
        )
    return _surface_from_minimal_behavioral_carrier(benchmark)


def list_supported_source_kinds() -> list[str]:
    return [kind.value for kind in CompletionSourceKind]


def _resolve_source_surface(
    request: CompletionRequest,
    *,
    benchmark: LoadedBenchmark | None,
) -> tuple[CompletionSourceSurface, LoadedBenchmark | None, CompletionFamilyBenchmarkView]:
    if request.input_kind is CompletionInputKind.SOURCE_SURFACE_REQUEST:
        if request.source_surface is None:
            raise ValueError("source_surface_request requires source_surface")
        family_view = CompletionFamilyBenchmarkView(
            family_id=request.family_id,
            status=CompletionFamilyStatus.OK,
            benchmark=benchmark,
            effect_summary={"mode": "external_source_surface"},
            warnings=[],
        )
        return request.source_surface, benchmark, family_view
    resolved_benchmark = benchmark
    if resolved_benchmark is None:
        if request.config_path is None:
            raise ValueError("benchmark_request requires config_path or benchmark")
        resolved_benchmark = load_benchmark(_resolve_path(request.config_path))
    family_view = build_completion_family_benchmark_view(
        resolved_benchmark,
        request.family_id,
    )
    benchmark_for_surface = family_view.benchmark or resolved_benchmark
    if benchmark_for_surface is None:
        raise ValueError("benchmark-backed completion family resolution produced no benchmark")
    surface = build_completion_source_surface(benchmark_for_surface, request.source_kind)
    return surface, family_view.benchmark, family_view


def build_completion_family_benchmark_view(
    benchmark: LoadedBenchmark,
    family_id: CompletionFamilyId,
) -> CompletionFamilyBenchmarkView:
    normalized_family_id = CompletionFamilyId(family_id)
    if normalized_family_id is CompletionFamilyId.DECLARED_COMPLETION_FAMILY:
        return CompletionFamilyBenchmarkView(
            family_id=normalized_family_id,
            status=CompletionFamilyStatus.OK,
            benchmark=benchmark,
            effect_summary={
                "family_mode": normalized_family_id.value,
                "continuation_count": len(benchmark.continuation_ids or []),
                "observable_count": len(
                    benchmark.observable_family.observables if benchmark.observable_family else ()
                ),
                "changed": False,
            },
        )
    if normalized_family_id is CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION:
        return _build_reachable_continuation_expansion_view(benchmark)
    if normalized_family_id is CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT:
        return _build_paired_observable_enrichment_view(benchmark)
    raise ValueError(f"unknown completion family id {family_id}")


def _surface_from_predictive_quotient(
    benchmark: LoadedBenchmark,
) -> CompletionSourceSurface:
    quotient = compute_predictive_quotient(benchmark)
    return CompletionSourceSurface(
        source_kind=CompletionSourceKind.PREDICTIVE_QUOTIENT,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        config_path=benchmark.config_path,
        source_result_ref="carrier:predictive_quotient",
        class_count=quotient.class_count,
        classes=[
            CompletionClassSurface(
                class_id=equivalence_class.class_id,
                default_representative_id=equivalence_class.representative_id,
                candidates=[
                    CompletionCandidate(
                        candidate_id=history_id,
                        candidate_type="history",
                        lower_member_ids=[history_id],
                        branch_member_count=1,
                        predictive_signature_key=quotient.signatures_by_element_id.get(history_id),
                        candidate_signature=quotient.signatures_by_element_id.get(history_id),
                        details={},
                    )
                    for history_id in equivalence_class.member_ids
                ],
            )
            for equivalence_class in quotient.classes
        ],
    )


def _surface_from_assemblage_quotient(
    benchmark: LoadedBenchmark,
    *,
    source_kind: CompletionSourceKind,
    quotient: QuotientResult,
) -> CompletionSourceSurface:
    predictive = compute_predictive_quotient(benchmark)
    candidate_by_id = {
        assemblage_id: _assemblage_candidate(
            benchmark,
            assemblage_id,
            predictive,
            quotient.signatures_by_element_id.get(assemblage_id),
        )
        for assemblage_id in quotient.element_to_class_id
    }
    return CompletionSourceSurface(
        source_kind=source_kind,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        config_path=benchmark.config_path,
        source_result_ref=f"carrier:{source_kind.value}",
        class_count=quotient.class_count,
        classes=[
            CompletionClassSurface(
                class_id=equivalence_class.class_id,
                default_representative_id=equivalence_class.representative_id,
                candidates=[
                    candidate_by_id[candidate_id]
                    for candidate_id in equivalence_class.member_ids
                ],
            )
            for equivalence_class in quotient.classes
        ],
    )


def _surface_from_minimal_behavioral_carrier(
    benchmark: LoadedBenchmark,
) -> CompletionSourceSurface:
    carrier = compute_minimal_behavioral_carrier(benchmark)
    if carrier.status is not CarrierComputationStatus.SUPPORTED:
        return CompletionSourceSurface(
            source_kind=CompletionSourceKind.MINIMAL_BEHAVIORAL_CARRIER,
            benchmark_id=benchmark.benchmark_id,
            config_id=benchmark.config_id,
            config_path=benchmark.config_path,
            source_result_ref="carrier:minimal_behavioral_carrier",
            class_count=0,
            executable=False,
            classes=[],
            warnings=[carrier.notes[0] if carrier.notes else "minimal behavioral carrier unavailable"],
        )
    graph = build_reachable_state_graph_snapshot(benchmark)
    state_by_id = {state.state_id: state for state in graph.states}
    return CompletionSourceSurface(
        source_kind=CompletionSourceKind.MINIMAL_BEHAVIORAL_CARRIER,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        config_path=benchmark.config_path,
        source_result_ref="carrier:minimal_behavioral_carrier",
        class_count=carrier.class_count,
        classes=[
            CompletionClassSurface(
                class_id=carrier_class.class_id,
                default_representative_id=carrier_class.representative_state_id,
                candidates=[
                    CompletionCandidate(
                        candidate_id=state_id,
                        candidate_type="reachable_state",
                        lower_member_ids=list(state_by_id[state_id].history_ids),
                        branch_member_count=len(state_by_id[state_id].history_ids),
                        predictive_signature_key={
                            "history_ids": list(state_by_id[state_id].history_ids),
                            "support_distribution": dict(
                                state_by_id[state_id].support_distribution
                            ),
                        },
                        candidate_signature={
                            "history_ids": list(state_by_id[state_id].history_ids),
                            "support_distribution": dict(
                                state_by_id[state_id].support_distribution
                            ),
                        },
                        details={
                            "source_interface_id": state_by_id[state_id].source_interface_id,
                            "target_interface_id": state_by_id[state_id].target_interface_id,
                        },
                    )
                    for state_id in carrier_class.member_state_ids
                ],
            )
            for carrier_class in carrier.classes
        ],
    )


def _assemblage_candidate(
    benchmark: LoadedBenchmark,
    assemblage_id: str,
    predictive: QuotientResult,
    candidate_signature: Any,
) -> CompletionCandidate:
    assemblage = benchmark.assemblages[assemblage_id]
    predictive_decomposition = [
        (
            predictive.element_to_class_id[member.history_id],
            str(member.weight),
            member.history_id,
        )
        for member in assemblage.members
    ]
    max_member_weight = max((member.weight for member in assemblage.members), default=Fraction(0, 1))
    return CompletionCandidate(
        candidate_id=assemblage_id,
        candidate_type="branch_assemblage",
        lower_member_ids=[member.history_id for member in assemblage.members],
        branch_member_count=len(assemblage.members),
        total_weight=str(assemblage.total_weight),
        max_member_weight=str(max_member_weight),
        predictive_signature_key=predictive_decomposition,
        candidate_signature=candidate_signature,
        details={
            "predictive_decomposition": [
                {
                    "predictive_class_id": class_id,
                    "weight": weight,
                    "history_id": history_id,
                }
                for class_id, weight, history_id in predictive_decomposition
            ],
        },
    )


def _build_metric_input_hints(
    *,
    benchmark: LoadedBenchmark | None,
    source_kind: CompletionSourceKind,
) -> CompletionMetricInputHints:
    executable = bool(benchmark is not None and benchmark.executable)
    supports_partition_bundle = executable
    supports_route_samples = executable and source_kind in {
        CompletionSourceKind.BRANCHWISE_QUOTIENT,
        CompletionSourceKind.RECOMBINATION_QUOTIENT,
    }
    suggested_metric_names: list[str] = []
    if supports_partition_bundle:
        suggested_metric_names.extend(["closure_defect", "closure_deficit"])
    if supports_route_samples:
        suggested_metric_names.append("route_mismatch")
    if executable:
        suggested_metric_names.append("support_breadth")
    return CompletionMetricInputHints(
        supports_partition_bundle=supports_partition_bundle,
        supports_route_composition_samples=supports_route_samples,
        supports_embedding_transport_samples=False,
        supports_embedding_recombination_samples=False,
        supports_support_snapshot=executable,
        suggested_metric_names=suggested_metric_names,
    )


def _build_transport_summary(
    benchmark: LoadedBenchmark | None,
    source_kind: CompletionSourceKind,
) -> dict[str, Any] | None:
    if benchmark is None or not benchmark.executable:
        return None
    return {
        "available": True,
        "source_kind": source_kind.value,
        "continuation_count": len(benchmark.continuation_ids or []),
        "admissible_generator_count": len(benchmark.admissible_generators or []),
    }


def _build_flattening_control_provenance(
    request: CompletionRequest,
    *,
    benchmark: LoadedBenchmark | None,
    representative_mapping: dict[str, str],
    _allow_flattening_recursion: bool,
) -> FlatteningControlProvenance:
    if request.flattening_mode is FlatteningControlMode.NONE:
        return FlatteningControlProvenance(mode=request.flattening_mode, active=False)
    warnings: list[str] = []
    if benchmark is None:
        warnings.append("flattening control hook requires a benchmark-backed request")
        return FlatteningControlProvenance(
            mode=request.flattening_mode,
            active=False,
            warnings=warnings,
        )
    if not benchmark.flattening_flag:
        warnings.append("benchmark does not advertise flattening-control metadata")
        return FlatteningControlProvenance(
            mode=request.flattening_mode,
            active=False,
            benchmark_has_flattening_flag=False,
            warnings=warnings,
        )
    partner_path = _resolve_flattening_partner_path(
        benchmark.config_path,
        notes=benchmark.notes,
    )
    if partner_path is None:
        warnings.append("no paired flattening-control benchmark could be resolved")
        return FlatteningControlProvenance(
            mode=request.flattening_mode,
            active=False,
            benchmark_has_flattening_flag=True,
            warnings=warnings,
        )
    if not _allow_flattening_recursion:
        return FlatteningControlProvenance(
            mode=request.flattening_mode,
            active=True,
            benchmark_has_flattening_flag=True,
            partner_config_path=_repo_relative(partner_path),
        )

    partner_benchmark = load_benchmark(partner_path)
    partner_request = CompletionRequest(
        input_kind=CompletionInputKind.BENCHMARK_REQUEST,
        source_kind=request.source_kind,
        strategy_id=request.strategy_id,
        family_id=request.family_id,
        config_path=_repo_relative(partner_path),
        strategy_parameters=request.strategy_parameters,
        flattening_mode=FlatteningControlMode.NONE,
    )
    partner_result = apply_completion_request(
        partner_request,
        benchmark=partner_benchmark,
        _allow_flattening_recursion=False,
    )
    shared_class_ids = sorted(
        set(representative_mapping).intersection(partner_result.representative_mapping)
    )
    shared_representatives_match = None
    if shared_class_ids:
        shared_representatives_match = all(
            representative_mapping[class_id]
            == partner_result.representative_mapping[class_id]
            for class_id in shared_class_ids
        )
    return FlatteningControlProvenance(
        mode=request.flattening_mode,
        active=True,
        benchmark_has_flattening_flag=True,
        partner_config_path=_repo_relative(partner_path),
        partner_config_id=partner_benchmark.config_id,
        partner_benchmark_id=partner_benchmark.benchmark_id,
        partner_source_kind=request.source_kind.value,
        partner_strategy_id=request.strategy_id,
        partner_representative_mapping=partner_result.representative_mapping,
        shared_class_ids=shared_class_ids,
        shared_representatives_match=shared_representatives_match,
        warnings=partner_result.warnings,
    )


def _resolve_flattening_partner_path(
    config_path: str | None,
    *,
    notes: list[str] | None = None,
) -> Path | None:
    override_path = _ticket27_flattening_partner_override(notes)
    if override_path is not None:
        return override_path
    if config_path is None:
        return None
    path = _resolve_path(config_path)
    if path.name == "reference_positive.json":
        return path.with_name("completion_partner.json")
    if path.name == "completion_partner.json":
        return path.with_name("reference_positive.json")
    return None


def _ticket27_flattening_partner_override(notes: list[str] | None) -> Path | None:
    if not notes:
        return None
    for note in notes:
        if note.startswith(TICKET27_FLATTENING_PARTNER_NOTE_PREFIX):
            return _resolve_path(
                note.removeprefix(TICKET27_FLATTENING_PARTNER_NOTE_PREFIX).strip()
            )
    return None


def _build_reachable_continuation_expansion_view(
    benchmark: LoadedBenchmark,
) -> CompletionFamilyBenchmarkView:
    if not benchmark.executable or benchmark.runtime_package is None:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION,
            status=CompletionFamilyStatus.UNSUPPORTED,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION.value,
                "changed": False,
            },
            warnings=["reachable continuation expansion requires an executable benchmark"],
        )
    expanded_continuations, added_ids, truncated = _expand_continuation_family(
        benchmark.runtime_package,
    )
    if truncated:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION,
            status=CompletionFamilyStatus.NOT_ENOUGH_DATA,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION.value,
                "changed": False,
                "added_continuation_ids": [],
            },
            warnings=[
                "exact finite continuation closure exceeded the current bounded expansion limit",
            ],
        )
    if not added_ids:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION,
            status=CompletionFamilyStatus.OK,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION.value,
                "changed": False,
                "added_continuation_ids": [],
                "continuation_count_before": len(benchmark.continuation_ids or []),
                "continuation_count_after": len(benchmark.continuation_ids or []),
            },
        )
    runtime_package = _clone_runtime_package_with_continuations(
        benchmark.runtime_package,
        expanded_continuations,
    )
    cloned = _clone_benchmark_view(
        benchmark,
        runtime_package=runtime_package,
        observable_family=benchmark.observable_family,
        continuation_ids=[continuation.continuation_id for continuation in expanded_continuations],
        admissible_generators=[continuation.continuation_id for continuation in expanded_continuations],
        notes=list(benchmark.notes)
        + [
            "completion family reachable_continuation_expansion applied",
        ],
    )
    return CompletionFamilyBenchmarkView(
        family_id=CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION,
        status=CompletionFamilyStatus.OK,
        benchmark=cloned,
        effect_summary={
            "family_mode": CompletionFamilyId.REACHABLE_CONTINUATION_EXPANSION.value,
            "changed": True,
            "continuation_count_before": len(benchmark.continuation_ids or []),
            "continuation_count_after": len(cloned.continuation_ids or []),
            "added_continuation_ids": added_ids,
        },
    )


def _build_paired_observable_enrichment_view(
    benchmark: LoadedBenchmark,
) -> CompletionFamilyBenchmarkView:
    if not benchmark.executable or benchmark.observable_family is None:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
            status=CompletionFamilyStatus.UNSUPPORTED,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT.value,
                "changed": False,
            },
            warnings=["paired observable enrichment requires an executable observable-backed benchmark"],
        )
    partner_path = _resolve_flattening_partner_path(
        benchmark.config_path,
        notes=benchmark.notes,
    )
    if partner_path is None:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
            status=CompletionFamilyStatus.UNSUPPORTED,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT.value,
                "changed": False,
            },
            warnings=[
                "paired observable enrichment requires flattening/completion partner metadata",
            ],
        )
    partner_benchmark = load_benchmark(partner_path)
    if not partner_benchmark.executable or partner_benchmark.observable_family is None:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
            status=CompletionFamilyStatus.UNSUPPORTED,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT.value,
                "changed": False,
            },
            warnings=["paired benchmark does not expose an executable observable family"],
        )
    observable_family, added_ids = _merge_observable_families(
        benchmark,
        partner_benchmark,
    )
    if not added_ids:
        return CompletionFamilyBenchmarkView(
            family_id=CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
            status=CompletionFamilyStatus.OK,
            benchmark=benchmark,
            effect_summary={
                "family_mode": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT.value,
                "changed": False,
                "partner_config_path": _repo_relative(partner_path),
                "observable_count_before": len(benchmark.observable_family.observables),
                "observable_count_after": len(benchmark.observable_family.observables),
                "added_observable_ids": [],
            },
        )
    cloned = _clone_benchmark_view(
        benchmark,
        runtime_package=benchmark.runtime_package,
        observable_family=observable_family,
        continuation_ids=list(benchmark.continuation_ids or []),
        admissible_generators=list(benchmark.admissible_generators or []),
        notes=list(benchmark.notes)
        + [
            "completion family paired_observable_enrichment applied",
        ],
    )
    return CompletionFamilyBenchmarkView(
        family_id=CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT,
        status=CompletionFamilyStatus.OK,
        benchmark=cloned,
        effect_summary={
            "family_mode": CompletionFamilyId.PAIRED_OBSERVABLE_ENRICHMENT.value,
            "changed": True,
            "partner_config_path": _repo_relative(partner_path),
            "partner_config_id": partner_benchmark.config_id,
            "observable_count_before": len(benchmark.observable_family.observables),
            "observable_count_after": len(observable_family.observables),
            "added_observable_ids": added_ids,
        },
    )


def _expand_continuation_family(
    runtime_package: RouteTransportPackage,
    *,
    max_continuations: int = 32,
) -> tuple[tuple[ContinuationKernelRuntime, ...], list[str], bool]:
    continuations = list(runtime_package.continuations)
    signatures = {
        _continuation_signature_key(continuation)
        for continuation in continuations
    }
    added_ids: list[str] = []
    changed = True
    while changed:
        changed = False
        current = list(continuations)
        for first in current:
            for second in current:
                if first.target_interface_id != second.source_interface_id:
                    continue
                composed = ContinuationKernelRuntime(
                    continuation_id=f"{first.continuation_id}__then__{second.continuation_id}",
                    source_interface_id=first.source_interface_id,
                    target_interface_id=second.target_interface_id,
                    kernel=compose_row_stochastic_kernels(first.kernel, second.kernel),
                )
                signature = _continuation_signature_key(composed)
                if signature in signatures:
                    continue
                continuations.append(composed)
                signatures.add(signature)
                added_ids.append(composed.continuation_id)
                changed = True
                if len(continuations) > max_continuations:
                    return tuple(runtime_package.continuations), [], True
    continuations.sort(key=lambda continuation: continuation.continuation_id)
    return tuple(continuations), added_ids, False


def _continuation_signature_key(
    continuation: ContinuationKernelRuntime,
) -> tuple[str, str, tuple[tuple[str, ...], ...]]:
    return (
        continuation.source_interface_id,
        continuation.target_interface_id,
        tuple(
            tuple(str(entry) for entry in row)
            for row in continuation.kernel
        ),
    )


def _clone_runtime_package_with_continuations(
    runtime_package: RouteTransportPackage,
    continuations: tuple[ContinuationKernelRuntime, ...],
) -> RouteTransportPackage:
    return RouteTransportPackage(
        package_id=runtime_package.package_id,
        support=runtime_package.support,
        state_space=runtime_package.state_space,
        interfaces=runtime_package.interfaces,
        event_packages=runtime_package.event_packages,
        histories=runtime_package.histories,
        continuations=continuations,
        loops=runtime_package.loops,
        interface_by_id=runtime_package.interface_by_id,
        event_package_by_interface_id=runtime_package.event_package_by_interface_id,
        history_by_id=runtime_package.history_by_id,
        continuation_by_id=MappingProxyType(
            {
                continuation.continuation_id: continuation
                for continuation in continuations
            }
        ),
        loop_by_id=runtime_package.loop_by_id,
    )


def _merge_observable_families(
    benchmark: LoadedBenchmark,
    partner_benchmark: LoadedBenchmark,
):
    if benchmark.observable_family.interface_id != partner_benchmark.observable_family.interface_id:
        raise ValueError("paired observable enrichment requires matching interface ids")
    merged_observables = []
    seen_ids: set[str] = set()
    added_ids: list[str] = []
    for observable in benchmark.observable_family.observables:
        merged_observables.append(observable)
        seen_ids.add(observable.observable_id)
    for observable in partner_benchmark.observable_family.observables:
        if observable.observable_id in seen_ids:
            continue
        merged_observables.append(observable)
        seen_ids.add(observable.observable_id)
        added_ids.append(observable.observable_id)
    observable_family = build_observable_family(
        family_id=(
            f"{benchmark.observable_family.family_id}__paired_with__"
            f"{partner_benchmark.observable_family.family_id}"
        ),
        interface_id=benchmark.observable_family.interface_id,
        observables=merged_observables,
    )
    return observable_family, added_ids


def _clone_benchmark_view(
    benchmark: LoadedBenchmark,
    *,
    runtime_package: RouteTransportPackage | None,
    observable_family: Any,
    continuation_ids: list[str],
    admissible_generators: list[str],
    notes: list[str],
) -> LoadedBenchmark:
    cloned = benchmark.model_copy(
        update={
            "continuation_ids": continuation_ids,
            "admissible_generators": admissible_generators,
            "observable_family_id": (
                observable_family.family_id if observable_family is not None else benchmark.observable_family_id
            ),
            "notes": notes,
        }
    )
    if benchmark.context is not None and runtime_package is not None:
        cloned._context = InheritedBenchmarkContext(
            benchmark_id=benchmark.context.benchmark_id,
            manifest_path=benchmark.context.manifest_path,
            manifest=benchmark.context.manifest,
            package_config_path=benchmark.context.package_config_path,
            package_config=benchmark.context.package_config,
            runtime_package=runtime_package,
        )
    else:
        cloned._context = benchmark.context
    cloned._runtime_package = runtime_package
    cloned._assemblages = benchmark._assemblages
    cloned._observable_family = observable_family
    cloned._relative_cycle_case = benchmark._relative_cycle_case
    return cloned


def _unsupported_result(
    request: CompletionRequest,
    *,
    benchmark: LoadedBenchmark | None,
    surface: CompletionSourceSurface,
    registry_path: Path,
    family_registry_path: Path,
    family_status: CompletionFamilyStatus,
    family_effect_summary: dict[str, Any],
    reason: str,
) -> CompletionResult:
    warnings = list(surface.warnings)
    warnings.append(reason)
    return CompletionResult(
        strategy_id=request.strategy_id,
        family_id=request.family_id,
        family_status=family_status,
        status=CompletionStatus.UNSUPPORTED,
        input_kind=request.input_kind,
        source_kind=request.source_kind,
        benchmark_id=surface.benchmark_id if surface.benchmark_id is not None else getattr(benchmark, "benchmark_id", None),
        config_id=surface.config_id if surface.config_id is not None else getattr(benchmark, "config_id", None),
        config_path=surface.config_path if surface.config_path is not None else request.config_path,
        representative_mapping={},
        representative_candidate_counts={},
        class_selections=[],
        deterministic_tie_break_metadata={},
        induced_lower_level_transport_summary=_build_transport_summary(benchmark, request.source_kind),
        metric_input_hints=_build_metric_input_hints(benchmark=benchmark, source_kind=request.source_kind),
        provenance=CompletionProvenance(
            strategy_id=request.strategy_id,
            strategy_registry_path=_repo_relative(registry_path),
            family_id=request.family_id,
            family_registry_path=_repo_relative(family_registry_path),
            benchmark_id=surface.benchmark_id,
            config_id=surface.config_id,
            config_path=surface.config_path,
            source_kind=request.source_kind.value,
            source_result_ref=surface.source_result_ref,
            candidate_pool_sizes_by_class={},
            deterministic_tie_break_rule="n/a",
            family_effect_summary=family_effect_summary,
            flattening_control=FlatteningControlProvenance(
                mode=request.flattening_mode,
                active=False,
                warnings=warnings,
            ),
            warnings=warnings,
        ),
        warnings=warnings,
        details={"reason": reason},
    )


def _error_result(
    request: CompletionRequest,
    *,
    reason: str,
    registry_path: Path,
    family_registry_path: Path,
) -> CompletionResult:
    warnings = [reason]
    return CompletionResult(
        strategy_id=request.strategy_id,
        family_id=request.family_id,
        family_status=CompletionFamilyStatus.UNSUPPORTED,
        status=CompletionStatus.ERROR,
        input_kind=request.input_kind,
        source_kind=request.source_kind,
        benchmark_id=None,
        config_id=None,
        config_path=request.config_path,
        representative_mapping={},
        representative_candidate_counts={},
        class_selections=[],
        deterministic_tie_break_metadata={},
        induced_lower_level_transport_summary=None,
        metric_input_hints=CompletionMetricInputHints(
            supports_partition_bundle=False,
            supports_route_composition_samples=False,
            supports_embedding_transport_samples=False,
            supports_embedding_recombination_samples=False,
            supports_support_snapshot=False,
            suggested_metric_names=[],
        ),
        provenance=CompletionProvenance(
            strategy_id=request.strategy_id,
            strategy_registry_path=_repo_relative(registry_path),
            family_id=request.family_id,
            family_registry_path=_repo_relative(family_registry_path),
            source_kind=request.source_kind.value,
            source_result_ref=f"carrier:{request.source_kind.value}",
            candidate_pool_sizes_by_class={},
            deterministic_tie_break_rule="n/a",
            family_effect_summary={},
            flattening_control=FlatteningControlProvenance(
                mode=request.flattening_mode,
                active=False,
                warnings=warnings,
            ),
            warnings=warnings,
        ),
        warnings=warnings,
        details={"reason": reason},
    )


def _resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return Path(__file__).resolve().parents[3] / path


def _repo_relative(path: Path) -> str:
    repo_root = Path(__file__).resolve().parents[3]
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


__all__ = [
    "CompletionCandidate",
    "CompletionFamilyBenchmarkView",
    "CompletionFamilyId",
    "CompletionFamilyStatus",
    "CompletionClassSurface",
    "CompletionInputKind",
    "CompletionMetricInputHints",
    "CompletionProvenance",
    "CompletionRequest",
    "CompletionResult",
    "CompletionSourceKind",
    "CompletionSourceSurface",
    "CompletionStatus",
    "FlatteningControlMode",
    "FlatteningControlProvenance",
    "apply_completion_request",
    "build_completion_family_benchmark_view",
    "build_completion_source_surface",
    "list_supported_source_kinds",
]
