from __future__ import annotations

from collections import defaultdict
from enum import Enum
from fractions import Fraction
from typing import Any

from sixbirds_foundations_v._holonomy_support.analysis import (
    InterfacePartition,
    compute_current_partition,
    compute_current_signature,
    compute_future_signature,
    compute_predictive_partition,
)
from pydantic import Field

from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel

from ..benchmarks.loader import (
    LoadedBenchmark,
    ReachableStateGraphSnapshot,
    ReachableStateNodeSnapshot,
    build_reachable_state_graph_snapshot,
)
from ..core.branchwise import (
    BranchwiseQuotientResult,
    branchwise_summary_payload,
    compute_branchwise_quotient as compute_runtime_branchwise_quotient,
)
from ..core.recombination import (
    RecombinationQuotientResult,
    recombination_quotient_payload,
    recombination_signature_payload,
    compute_recombination_quotient as compute_runtime_recombination_quotient,
)


class CarrierComputationStatus(str, Enum):
    SUPPORTED = "supported"
    UNSUPPORTED = "unsupported"
    REFINEMENT_FAILED = "refinement_failed"


class QuotientClassSummary(SixBirdsRecombinationModel):
    class_id: str
    member_ids: list[str]
    representative_id: str
    signature: Any


class QuotientResult(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-quotient.v1"
    quotient_id: str
    status: CarrierComputationStatus
    benchmark_id: str | None = None
    config_id: str
    interface_id: str | None = None
    loader_kind: str
    executable: bool
    domain_kind: str
    class_count: int = 0
    classes: list[QuotientClassSummary] = Field(default_factory=list)
    element_to_class_id: dict[str, str] = Field(default_factory=dict)
    signatures_by_element_id: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class FactorMapResult(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-factor-map.v1"
    map_id: str
    status: CarrierComputationStatus
    source_quotient_id: str
    target_quotient_id: str
    refinement_holds: bool
    map_defined: bool
    source_class_to_target_class: dict[str, str] = Field(default_factory=dict)
    fiber_sizes_by_target_class: dict[str, int] = Field(default_factory=dict)
    max_fiber_size: int = 0
    is_surjective: bool = False
    notes: list[str] = Field(default_factory=list)


class MinimalBehavioralCarrierClass(SixBirdsRecombinationModel):
    class_id: str
    member_state_ids: list[str]
    representative_state_id: str
    observation_signature: dict[str, Any]
    transition_signature: dict[str, str]


class MinimalBehavioralCarrierResult(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-minimal-behavioral-carrier.v1"
    status: CarrierComputationStatus
    benchmark_id: str | None = None
    config_id: str
    interface_id: str | None = None
    loader_kind: str
    executable: bool
    domain_kind: str = "reachable_state"
    state_count: int = 0
    class_count: int = 0
    initial_state_ids: list[str] = Field(default_factory=list)
    state_to_class_id: dict[str, str] = Field(default_factory=dict)
    classes: list[MinimalBehavioralCarrierClass] = Field(default_factory=list)
    transport_by_class_id: dict[str, dict[str, str]] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


def compute_current_quotient(benchmark: LoadedBenchmark) -> QuotientResult:
    """Compute the current quotient `Q` on the benchmark's declared interface histories."""
    if not benchmark.executable:
        return _unsupported_quotient(
            benchmark,
            quotient_id="Q",
            domain_kind="interface_history",
            reason="current quotient requires an executable loaded benchmark",
        )
    partition = compute_current_partition(benchmark.runtime_package, benchmark.config.interface_id)
    signatures_by_history_id = {
        history_id: _jsonable_signature(
            compute_current_signature(
                benchmark.runtime_package,
                history_id,
                interface_id=benchmark.config.interface_id,
            ).signature_key
        )
        for history_id in partition.history_to_class_id
    }
    return _interface_partition_to_result(
        benchmark,
        quotient_id="Q",
        partition=partition,
        signatures_by_element_id=signatures_by_history_id,
        notes=[
            "current quotient on declared interface histories",
            "current observables reuse inherited holonomy-memory event-package signatures",
        ],
    )


def compute_predictive_quotient(benchmark: LoadedBenchmark) -> QuotientResult:
    """Compute the predictive quotient `M` on the benchmark's declared interface histories."""
    if not benchmark.executable:
        return _unsupported_quotient(
            benchmark,
            quotient_id="M",
            domain_kind="interface_history",
            reason="predictive quotient requires an executable loaded benchmark",
        )
    partition = compute_predictive_partition(
        benchmark.runtime_package,
        benchmark.config.interface_id,
    )
    signatures_by_history_id = {
        history_id: _jsonable_signature(
            compute_future_signature(
                benchmark.runtime_package,
                history_id,
                interface_id=benchmark.config.interface_id,
            ).signature_key
        )
        for history_id in partition.history_to_class_id
    }
    return _interface_partition_to_result(
        benchmark,
        quotient_id="M",
        partition=partition,
        signatures_by_element_id=signatures_by_history_id,
        notes=[
            "predictive quotient on declared interface histories",
            "finite exact scope reuses inherited holonomy-memory continuation/event signatures",
        ],
    )


def compute_branchwise_quotient(benchmark: LoadedBenchmark) -> QuotientResult:
    """Compute the branchwise quotient `K` on the loaded benchmark's assemblage family."""
    if not benchmark.executable:
        return _unsupported_quotient(
            benchmark,
            quotient_id="K",
            domain_kind="branch_assemblage",
            reason="branchwise quotient requires an executable loaded benchmark",
        )
    quotient = compute_runtime_branchwise_quotient(
        benchmark.context,
        benchmark.config.interface_id,
        _ordered_assemblage_items(benchmark),
    )
    return _branchwise_quotient_to_result(benchmark, quotient)


def compute_recombination_quotient(benchmark: LoadedBenchmark) -> QuotientResult:
    """Compute the recombination quotient `R` on the loaded benchmark's assemblage family."""
    if not benchmark.executable:
        return _unsupported_quotient(
            benchmark,
            quotient_id="R",
            domain_kind="branch_assemblage",
            reason="recombination quotient requires an executable loaded benchmark",
        )
    quotient = compute_runtime_recombination_quotient(
        benchmark.context,
        benchmark.config.interface_id,
        _ordered_assemblage_items(benchmark),
        benchmark.observable_family,
    )
    return _recombination_quotient_to_result(benchmark, quotient)


def compute_factor_map(
    source: QuotientResult,
    target: QuotientResult,
    *,
    map_id: str,
) -> FactorMapResult:
    """Construct the induced factor map when the source quotient refines the target quotient."""
    if source.status is not CarrierComputationStatus.SUPPORTED:
        return _unsupported_factor_map(
            map_id,
            source,
            target,
            reason=f"source quotient {source.quotient_id} is not supported",
        )
    if target.status is not CarrierComputationStatus.SUPPORTED:
        return _unsupported_factor_map(
            map_id,
            source,
            target,
            reason=f"target quotient {target.quotient_id} is not supported",
        )
    if source.domain_kind != target.domain_kind:
        return _unsupported_factor_map(
            map_id,
            source,
            target,
            reason="source and target quotients live on different domains",
        )

    source_elements = set(source.element_to_class_id)
    target_elements = set(target.element_to_class_id)
    if source_elements != target_elements:
        return _unsupported_factor_map(
            map_id,
            source,
            target,
            reason="source and target quotients do not cover the same element ids",
        )

    source_class_to_target_class: dict[str, str] = {}
    fiber_sizes_by_target_class: dict[str, int] = defaultdict(int)
    for source_class in source.classes:
        target_class_ids = {
            target.element_to_class_id[element_id] for element_id in source_class.member_ids
        }
        if len(target_class_ids) != 1:
            return FactorMapResult(
                map_id=map_id,
                status=CarrierComputationStatus.REFINEMENT_FAILED,
                source_quotient_id=source.quotient_id,
                target_quotient_id=target.quotient_id,
                refinement_holds=False,
                map_defined=False,
                notes=[
                    f"{source.quotient_id} does not refine {target.quotient_id}",
                ],
            )
        target_class_id = next(iter(target_class_ids))
        source_class_to_target_class[source_class.class_id] = target_class_id
        fiber_sizes_by_target_class[target_class_id] += 1

    target_class_ids = {item.class_id for item in target.classes}
    return FactorMapResult(
        map_id=map_id,
        status=CarrierComputationStatus.SUPPORTED,
        source_quotient_id=source.quotient_id,
        target_quotient_id=target.quotient_id,
        refinement_holds=True,
        map_defined=True,
        source_class_to_target_class=source_class_to_target_class,
        fiber_sizes_by_target_class=dict(sorted(fiber_sizes_by_target_class.items())),
        max_fiber_size=max(fiber_sizes_by_target_class.values(), default=0),
        is_surjective=set(fiber_sizes_by_target_class) == target_class_ids,
        notes=[f"constructed induced map {map_id} from {source.quotient_id} to {target.quotient_id}"],
    )


def compute_pi_factor_map(benchmark: LoadedBenchmark) -> FactorMapResult:
    """Compute `pi : M -> Q` when the predictive quotient refines the current quotient."""
    predictive = compute_predictive_quotient(benchmark)
    current = compute_current_quotient(benchmark)
    return compute_factor_map(predictive, current, map_id="pi")


def compute_eta_factor_map(benchmark: LoadedBenchmark) -> FactorMapResult:
    """Compute `eta : R -> K` when the recombination quotient refines the branchwise quotient."""
    recombination = compute_recombination_quotient(benchmark)
    branchwise = compute_branchwise_quotient(benchmark)
    return compute_factor_map(recombination, branchwise, map_id="eta")


def compute_minimal_behavioral_carrier(
    benchmark: LoadedBenchmark,
) -> MinimalBehavioralCarrierResult:
    """Compute the finite reachable-image minimal behavioral carrier `Lambda*`."""
    if not benchmark.executable:
        return _unsupported_minimal_carrier(
            benchmark,
            reason="minimal behavioral carrier requires an executable loaded benchmark",
        )

    graph = build_reachable_state_graph_snapshot(benchmark)
    state_ids = [state.state_id for state in sorted(graph.states, key=lambda item: item.state_id)]
    state_by_id = {state.state_id: state for state in graph.states}
    observation_signatures = {
        state_id: _state_observation_signature(benchmark, state_by_id[state_id])
        for state_id in state_ids
    }
    transitions_by_state = _transitions_by_state(graph)
    class_by_state, members_by_class, signature_by_class = _refine_state_partition(
        state_ids=state_ids,
        observation_signatures=observation_signatures,
        transitions_by_state=transitions_by_state,
    )

    transport_by_class_id: dict[str, dict[str, str]] = {}
    classes: list[MinimalBehavioralCarrierClass] = []
    for class_id in sorted(members_by_class):
        member_state_ids = list(members_by_class[class_id])
        representative_state_id = member_state_ids[0]
        transition_signature = dict(signature_by_class[class_id]["transition_signature"])
        transport_by_class_id[class_id] = transition_signature
        classes.append(
            MinimalBehavioralCarrierClass(
                class_id=class_id,
                member_state_ids=member_state_ids,
                representative_state_id=representative_state_id,
                observation_signature=signature_by_class[class_id]["observation_signature"],
                transition_signature=transition_signature,
            )
        )

    return MinimalBehavioralCarrierResult(
        status=CarrierComputationStatus.SUPPORTED,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        interface_id=benchmark.config.interface_id,
        loader_kind=benchmark.loader_kind.value,
        executable=benchmark.executable,
        state_count=len(state_ids),
        class_count=len(classes),
        initial_state_ids=list(graph.initial_state_ids),
        state_to_class_id=dict(sorted(class_by_state.items())),
        classes=classes,
        transport_by_class_id=transport_by_class_id,
        notes=[
            "finite exact interpretation uses reachable-state observations plus continuation-labeled successor classes",
            "the refinement terminates at the first stable partition on the finite reachable graph",
        ],
    )


def _interface_partition_to_result(
    benchmark: LoadedBenchmark,
    *,
    quotient_id: str,
    partition: InterfacePartition,
    signatures_by_element_id: dict[str, Any],
    notes: list[str],
) -> QuotientResult:
    class_signatures = {
        equivalence_class.class_id: _jsonable_signature(equivalence_class.signature_key)
        for equivalence_class in partition.classes
    }
    return QuotientResult(
        quotient_id=quotient_id,
        status=CarrierComputationStatus.SUPPORTED,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        interface_id=partition.interface_id,
        loader_kind=benchmark.loader_kind.value,
        executable=benchmark.executable,
        domain_kind="interface_history",
        class_count=partition.class_count,
        classes=[
            QuotientClassSummary(
                class_id=equivalence_class.class_id,
                member_ids=list(equivalence_class.member_history_ids),
                representative_id=equivalence_class.representative_history_id,
                signature=class_signatures[equivalence_class.class_id],
            )
            for equivalence_class in partition.classes
        ],
        element_to_class_id=dict(sorted(partition.history_to_class_id.items())),
        signatures_by_element_id=dict(sorted(signatures_by_element_id.items())),
        notes=notes,
    )


def _branchwise_quotient_to_result(
    benchmark: LoadedBenchmark,
    quotient: BranchwiseQuotientResult,
) -> QuotientResult:
    return QuotientResult(
        quotient_id="K",
        status=CarrierComputationStatus.SUPPORTED,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        interface_id=quotient.interface_id,
        loader_kind=benchmark.loader_kind.value,
        executable=benchmark.executable,
        domain_kind="branch_assemblage",
        class_count=quotient.class_count,
        classes=[
            QuotientClassSummary(
                class_id=equivalence_class.class_id,
                member_ids=list(equivalence_class.assemblage_ids),
                representative_id=equivalence_class.assemblage_ids[0],
                signature=branchwise_summary_payload(equivalence_class.summary)["entries"],
            )
            for equivalence_class in quotient.classes
        ],
        element_to_class_id=dict(sorted(quotient.assemblage_to_class_id.items())),
        signatures_by_element_id={
            assemblage_id: branchwise_summary_payload(summary)["entries"]
            for assemblage_id, summary in sorted(quotient.summaries_by_assemblage_id.items())
        },
        notes=[
            "branchwise quotient uses weighted multisets of predictive classes",
        ],
    )


def _recombination_quotient_to_result(
    benchmark: LoadedBenchmark,
    quotient: RecombinationQuotientResult,
) -> QuotientResult:
    payload = recombination_quotient_payload(quotient)
    return QuotientResult(
        quotient_id="R",
        status=CarrierComputationStatus.SUPPORTED,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        interface_id=quotient.interface_id,
        loader_kind=benchmark.loader_kind.value,
        executable=benchmark.executable,
        domain_kind="branch_assemblage",
        class_count=quotient.class_count,
        classes=[
            QuotientClassSummary(
                class_id=equivalence_class.class_id,
                member_ids=list(equivalence_class.assemblage_ids),
                representative_id=equivalence_class.assemblage_ids[0],
                signature=recombination_signature_payload(equivalence_class.signature),
            )
            for equivalence_class in quotient.classes
        ],
        element_to_class_id=dict(sorted(quotient.assemblage_to_r_class_id.items())),
        signatures_by_element_id={
            assemblage_id: recombination_signature_payload(signature)
            for assemblage_id, signature in sorted(quotient.signatures_by_assemblage_id.items())
        },
        notes=[
            "recombination quotient reuses the active observable-family evaluation semantics",
            f"includes_certified_branchwise_mixing={payload['includes_certified_branchwise_mixing']}",
        ],
    )


def _unsupported_quotient(
    benchmark: LoadedBenchmark,
    *,
    quotient_id: str,
    domain_kind: str,
    reason: str,
) -> QuotientResult:
    return QuotientResult(
        quotient_id=quotient_id,
        status=CarrierComputationStatus.UNSUPPORTED,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        interface_id=getattr(benchmark.config, "interface_id", None),
        loader_kind=benchmark.loader_kind.value,
        executable=benchmark.executable,
        domain_kind=domain_kind,
        notes=[reason],
    )


def _unsupported_factor_map(
    map_id: str,
    source: QuotientResult,
    target: QuotientResult,
    *,
    reason: str,
) -> FactorMapResult:
    return FactorMapResult(
        map_id=map_id,
        status=CarrierComputationStatus.UNSUPPORTED,
        source_quotient_id=source.quotient_id,
        target_quotient_id=target.quotient_id,
        refinement_holds=False,
        map_defined=False,
        notes=[reason],
    )


def _unsupported_minimal_carrier(
    benchmark: LoadedBenchmark,
    *,
    reason: str,
) -> MinimalBehavioralCarrierResult:
    return MinimalBehavioralCarrierResult(
        status=CarrierComputationStatus.UNSUPPORTED,
        benchmark_id=benchmark.benchmark_id,
        config_id=benchmark.config_id,
        interface_id=getattr(benchmark.config, "interface_id", None),
        loader_kind=benchmark.loader_kind.value,
        executable=benchmark.executable,
        notes=[reason],
    )


def _ordered_assemblage_items(
    benchmark: LoadedBenchmark,
) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted(benchmark.assemblages.items()))


def _jsonable_signature(signature: Any) -> Any:
    if isinstance(signature, Fraction):
        return str(signature)
    if isinstance(signature, tuple):
        return [_jsonable_signature(item) for item in signature]
    if isinstance(signature, list):
        return [_jsonable_signature(item) for item in signature]
    if isinstance(signature, dict):
        return {str(key): _jsonable_signature(value) for key, value in signature.items()}
    return signature


def _transitions_by_state(
    graph: ReachableStateGraphSnapshot,
) -> dict[str, tuple[tuple[str, str], ...]]:
    edges_by_source: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for edge in sorted(
        graph.edges,
        key=lambda item: (item.source_state_id, item.continuation_id, item.target_state_id),
    ):
        edges_by_source[edge.source_state_id].append(
            (edge.continuation_id, edge.target_state_id)
        )
    return {state_id: tuple(edges) for state_id, edges in edges_by_source.items()}


def _state_observation_signature(
    benchmark: LoadedBenchmark,
    state: ReachableStateNodeSnapshot,
) -> dict[str, Any]:
    support_distribution = {
        support_id: Fraction(value)
        for support_id, value in state.support_distribution.items()
    }
    event_package = benchmark.runtime_package.get_event_package(state.target_interface_id)
    probabilities_by_event_id: dict[str, str] = {}
    for event in event_package.events:
        probability = Fraction(0, 1)
        for support_id, weight in zip(
            benchmark.runtime_package.support.visible_support_labels,
            event.weights,
            strict=True,
        ):
            probability += support_distribution[support_id] * weight
        probabilities_by_event_id[event.event_id] = str(probability)
    return {
        "interface_id": state.target_interface_id,
        "event_package_id": event_package.package_id,
        "event_distribution": dict(sorted(probabilities_by_event_id.items())),
    }


def _refine_state_partition(
    *,
    state_ids: list[str],
    observation_signatures: dict[str, dict[str, Any]],
    transitions_by_state: dict[str, tuple[tuple[str, str], ...]],
) -> tuple[dict[str, str], dict[str, tuple[str, ...]], dict[str, dict[str, Any]]]:
    current_signatures = {
        state_id: (
            observation_signatures[state_id]["interface_id"],
            tuple(observation_signatures[state_id]["event_distribution"].items()),
        )
        for state_id in state_ids
    }
    state_to_class_id, class_members = _partition_from_signatures(state_ids, current_signatures)

    while True:
        # Refine by observation plus continuation-labeled successor classes until stable.
        refined_signatures = {}
        for state_id in state_ids:
            refined_signatures[state_id] = (
                current_signatures[state_id],
                tuple(
                    (continuation_id, state_to_class_id[target_state_id])
                    for continuation_id, target_state_id in transitions_by_state.get(state_id, ())
                ),
            )
        next_state_to_class_id, next_class_members = _partition_from_signatures(
            state_ids,
            refined_signatures,
        )
        if next_state_to_class_id == state_to_class_id:
            class_signature_details = {
                class_id: {
                    "observation_signature": observation_signatures[members[0]],
                    "transition_signature": {
                        continuation_id: state_to_class_id[target_state_id]
                        for continuation_id, target_state_id in transitions_by_state.get(
                            members[0],
                            (),
                        )
                    },
                }
                for class_id, members in next_class_members.items()
            }
            return next_state_to_class_id, next_class_members, class_signature_details
        state_to_class_id = next_state_to_class_id
        class_members = next_class_members
        current_signatures = refined_signatures


def _partition_from_signatures(
    state_ids: list[str],
    signatures_by_state_id: dict[str, Any],
) -> tuple[dict[str, str], dict[str, tuple[str, ...]]]:
    members_by_signature: dict[Any, list[str]] = {}
    ordered_signatures: list[Any] = []
    for state_id in state_ids:
        signature = signatures_by_state_id[state_id]
        if signature not in members_by_signature:
            members_by_signature[signature] = []
            ordered_signatures.append(signature)
        members_by_signature[signature].append(state_id)

    state_to_class_id: dict[str, str] = {}
    class_members: dict[str, tuple[str, ...]] = {}
    for index, signature in enumerate(ordered_signatures):
        class_id = f"L{index}"
        members = tuple(members_by_signature[signature])
        class_members[class_id] = members
        for state_id in members:
            state_to_class_id[state_id] = class_id
    return state_to_class_id, class_members


__all__ = [
    "CarrierComputationStatus",
    "FactorMapResult",
    "MinimalBehavioralCarrierClass",
    "MinimalBehavioralCarrierResult",
    "QuotientClassSummary",
    "QuotientResult",
    "compute_branchwise_quotient",
    "compute_current_quotient",
    "compute_eta_factor_map",
    "compute_factor_map",
    "compute_minimal_behavioral_carrier",
    "compute_pi_factor_map",
    "compute_predictive_quotient",
    "compute_recombination_quotient",
]
