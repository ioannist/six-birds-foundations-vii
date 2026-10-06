from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._holonomy_support.core import load_route_transport_package_from_config
from sixbirds_foundations_v._holonomy_support.schemas.transport import RouteTransportPackageConfig

from sixbirds_foundations_v._recombination_support.benchmarks.loader import (
    LoadedBenchmark,
    LoaderKind,
    ReachableStateGraphSnapshot,
    ReachableStateNodeSnapshot,
    build_reachable_state_graph_snapshot,
    load_benchmark,
    load_benchmark_from_config,
)
from sixbirds_foundations_v._recombination_support.carriers.library import (
    CarrierComputationStatus,
    MinimalBehavioralCarrierClass,
    MinimalBehavioralCarrierResult,
)
from sixbirds_foundations_v._recombination_support.core.assemblages import build_branch_assemblage, make_branch_member
from sixbirds_foundations_v._recombination_support.core.relative_cycle import (
    RELATIVE_CYCLE_BENCHMARK_ID,
    build_relative_cycle_case,
    build_relative_cycle_completion_observable_family,
    normalize_relative_cycle_parameters,
)
from sixbirds_foundations_v._recombination_support.core.substrate import (
    InheritedBenchmarkContext,
    load_inherited_benchmark_context,
)
from sixbirds_foundations_v._recombination_support.runner import REPO_ROOT, _uses_dynamic_relative_cycle_case, validate_config_file
from sixbirds_foundations_v._recombination_support.schemas.configs import BenchmarkRunConfig, RunConfig


def load_review_benchmark(path: str | Path) -> LoadedBenchmark:
    config = validate_config_file(path)
    return load_review_benchmark_from_config(config, config_path=Path(path))


def load_review_benchmark_from_config(
    config: RunConfig,
    *,
    config_path: str | Path | None = None,
) -> LoadedBenchmark:
    if isinstance(config, BenchmarkRunConfig) and _uses_dynamic_relative_cycle_case(config):
        return _load_dynamic_review_benchmark(config, config_path=config_path)
    return load_benchmark_from_config(config, config_path=config_path)


def compute_review_minimal_behavioral_carrier(
    benchmark: LoadedBenchmark,
) -> MinimalBehavioralCarrierResult:
    if not benchmark.executable:
        return MinimalBehavioralCarrierResult(
            status=CarrierComputationStatus.UNSUPPORTED,
            benchmark_id=benchmark.benchmark_id,
            config_id=benchmark.config_id,
            interface_id=benchmark.config.interface_id,
            loader_kind=benchmark.loader_kind.value,
            executable=benchmark.executable,
            notes=["minimal behavioral carrier requires an executable benchmark"],
        )

    graph = build_reachable_state_graph_snapshot(benchmark)
    state_ids = [state.state_id for state in sorted(graph.states, key=lambda item: item.state_id)]
    state_by_id = {state.state_id: state for state in graph.states}
    observation_signatures = {
        state_id: _review_state_observation_signature(benchmark, state_by_id[state_id])
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

    notes = [
        "review path uses reachable-state refinement on the effective benchmark runtime surface",
        "review path uses benchmark-specific observables for relative-cycle mid states and internal screen-state projections for screen states",
    ]
    if (
        benchmark.benchmark_id == RELATIVE_CYCLE_BENCHMARK_ID
        and benchmark._relative_cycle_case is not None
    ):
        notes.append(
            "dynamic relative-cycle nearby positives use a carrier-size-trimmed runtime package instead of the inherited five-state base package"
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
        notes=notes,
    )


def _load_dynamic_review_benchmark(
    config: BenchmarkRunConfig,
    *,
    config_path: str | Path | None,
) -> LoadedBenchmark:
    base_context = load_inherited_benchmark_context(config.benchmark_id)
    parameters = normalize_relative_cycle_parameters(
        carrier_size=config.carrier_size or 0,
        route_shift_delta=config.route_shift_delta or 0,
        weight_left=config.weight_left or "",
        weight_right=config.weight_right or "",
    )
    effective_package_config = _build_dynamic_relative_cycle_package_config(
        base_context.package_config,
        carrier_size=parameters.carrier_size,
    )
    effective_runtime_package = load_route_transport_package_from_config(effective_package_config)
    effective_context = InheritedBenchmarkContext(
        benchmark_id=base_context.benchmark_id,
        manifest_path=base_context.manifest_path,
        manifest=base_context.manifest,
        package_config_path=base_context.package_config_path,
        package_config=effective_package_config,
        runtime_package=effective_runtime_package,
    )
    case = build_relative_cycle_case(parameters, context=effective_context)
    observable_family = (
        build_relative_cycle_completion_observable_family(parameters)
        if "completion_partner" in config.tags
        else case.observable_family
    )
    family, variant = _infer_family_and_variant(config)
    resolved_config_path = _repo_path(config_path or "")

    loaded = LoadedBenchmark(
        loader_kind=LoaderKind.RUNNABLE_BENCHMARK,
        executable=True,
        config_kind=config.config_kind,
        config_path=resolved_config_path,
        config_id=config.config_id,
        benchmark_id=config.benchmark_id,
        family=family,
        variant=variant,
        seed=config.seed,
        tags=list(config.tags),
        config=config,
        benchmark_manifest_ref=_repo_path(base_context.manifest_path),
        transport_package_ref=_repo_path(
            base_context.package_config_path or base_context.manifest.transport_package_ref or ""
        ),
        benchmark_manifest=base_context.manifest,
        transport_package_config=effective_package_config,
        support_spec=effective_package_config.support.model_dump(mode="json"),
        state_space_spec=effective_package_config.state_space.model_dump(mode="json"),
        interface_ids=[interface.interface_id for interface in effective_package_config.interfaces],
        history_ids=[history.history_id for history in effective_package_config.histories],
        continuation_ids=[
            continuation.continuation_id for continuation in effective_package_config.continuations
        ],
        loop_ids=[loop.loop_id for loop in effective_package_config.loops],
        initial_state_ids=[history.history_id for history in effective_package_config.histories],
        admissible_generators=[
            continuation.continuation_id
            for continuation in effective_runtime_package.continuations
        ],
        generator_family=config.assemblage_family_id,
        assemblage_family_id=config.assemblage_family_id,
        observable_family_id=config.observable_family_id,
        route_readability_scenario_id=config.route_readability_scenario_id,
        visibility_scenario_id=config.visibility_scenario_id,
        carrier_size=config.carrier_size,
        route_shift_delta=config.route_shift_delta,
        weight_left=config.weight_left,
        weight_right=config.weight_right,
        notes=[
            "review dynamic relative-cycle benchmark",
            "effective runtime package trimmed to the configured carrier size",
        ],
    )
    loaded._context = effective_context
    loaded._runtime_package = effective_runtime_package
    loaded._assemblages = dict(case.assemblages)
    loaded._observable_family = observable_family
    loaded._relative_cycle_case = case
    return loaded


def _build_dynamic_relative_cycle_package_config(
    base_config: RouteTransportPackageConfig,
    *,
    carrier_size: int,
) -> RouteTransportPackageConfig:
    allowed_state_ids = (
        [f"phi_{index}" for index in range(carrier_size)]
        + ["erased_state"]
        + [f"screen_state_{index}" for index in range(carrier_size)]
    )
    allowed_histories = {f"h_mid_{index}" for index in range(carrier_size)}
    allowed_screen_events = {f"screen_{index}" for index in range(carrier_size)}

    payload = base_config.model_dump(mode="json")
    payload["package_id"] = f"{payload['package_id']}__dynamic_n{carrier_size}"
    payload["state_space"]["internal_state_ids"] = allowed_state_ids
    payload["state_space"]["support_projection"] = {
        state_id: label
        for state_id, label in payload["state_space"]["support_projection"].items()
        if state_id in set(allowed_state_ids)
    }
    filtered_event_packages = []
    for event_package in payload["event_packages"]:
        if event_package["interface_id"] == "screen":
            filtered_events = [
                event
                for event in event_package["events"]
                if event["event_id"] in allowed_screen_events
            ]
            filtered_event_packages.append(
                {
                    **event_package,
                    "events": filtered_events,
                }
            )
            continue
        filtered_event_packages.append(event_package)
    payload["event_packages"] = filtered_event_packages
    payload["histories"] = [
        history for history in payload["histories"] if history["history_id"] in allowed_histories
    ]
    payload["continuations"] = [
        _trim_continuation_kernel(continuation, allowed_state_ids)
        for continuation in payload["continuations"]
    ]
    return RouteTransportPackageConfig.model_validate(payload)


def _trim_continuation_kernel(
    continuation: dict[str, Any],
    allowed_state_ids: list[str],
) -> dict[str, Any]:
    allowed = set(allowed_state_ids)
    return {
        **continuation,
        "kernel": {
            source_state_id: {
                target_state_id: value
                for target_state_id, value in row.items()
                if target_state_id in allowed
            }
            for source_state_id, row in continuation["kernel"].items()
            if source_state_id in allowed
        },
    }


def _review_state_observation_signature(
    benchmark: LoadedBenchmark,
    state: ReachableStateNodeSnapshot,
) -> dict[str, Any]:
    if benchmark.benchmark_id == RELATIVE_CYCLE_BENCHMARK_ID:
        if state.target_interface_id == "mid" and benchmark.observable_family is not None:
            signature = _observable_family_signature(benchmark, state)
            if signature is not None:
                return signature
        if state.target_interface_id == "screen":
            signature = _relative_cycle_screen_signature(state)
            if signature is not None:
                return signature
    return _generic_event_package_signature(benchmark, state)


def _observable_family_signature(
    benchmark: LoadedBenchmark,
    state: ReachableStateNodeSnapshot,
) -> dict[str, Any] | None:
    context = benchmark.context
    family = benchmark.observable_family
    if context is None or family is None or not state.history_ids:
        return None
    member_weight = Fraction(1, len(state.history_ids))
    assemblage = build_branch_assemblage(
        context,
        state.target_interface_id,
        [
            make_branch_member(history_id, member_weight)
            for history_id in state.history_ids
        ],
    )
    observable_distributions: dict[str, dict[str, str]] = {}
    for observable in family.observables:
        distribution = observable.evaluate(context, assemblage)
        observable_distributions[observable.observable_id] = {
            event_id: str(probability)
            for event_id, probability in distribution.as_mapping().items()
        }
    return {
        "interface_id": state.target_interface_id,
        "surface_kind": "observable_family",
        "observable_family_id": family.family_id,
        "observable_distributions": dict(sorted(observable_distributions.items())),
    }


def _relative_cycle_screen_signature(
    state: ReachableStateNodeSnapshot,
) -> dict[str, Any] | None:
    probabilities_by_event_id: dict[str, Fraction] = defaultdict(lambda: Fraction(0, 1))
    for internal_state_id, value in state.internal_state_distribution.items():
        probability = Fraction(value)
        if probability == 0 or not internal_state_id.startswith("screen_state_"):
            continue
        suffix = internal_state_id.removeprefix("screen_state_")
        probabilities_by_event_id[f"screen_{suffix}"] += probability
    if not probabilities_by_event_id:
        return None
    return {
        "interface_id": state.target_interface_id,
        "surface_kind": "screen_state_projection",
        "event_distribution": {
            event_id: str(probability)
            for event_id, probability in sorted(probabilities_by_event_id.items())
        },
    }


def _generic_event_package_signature(
    benchmark: LoadedBenchmark,
    state: ReachableStateNodeSnapshot,
) -> dict[str, Any]:
    support_distribution = {
        support_id: Fraction(value)
        for support_id, value in state.support_distribution.items()
    }
    event_package = benchmark.runtime_package.get_event_package(state.target_interface_id)
    probabilities_by_event_id: dict[str, Fraction] = defaultdict(lambda: Fraction(0, 1))
    for event in event_package.events:
        for support_id, weight in zip(
            benchmark.runtime_package.support.visible_support_labels,
            event.weights,
            strict=True,
        ):
            probabilities_by_event_id[event.event_id] += support_distribution[support_id] * weight
    return {
        "interface_id": state.target_interface_id,
        "surface_kind": "event_package",
        "event_package_id": event_package.package_id,
        "event_distribution": {
            event_id: str(probability)
            for event_id, probability in sorted(probabilities_by_event_id.items())
        },
    }


def _transitions_by_state(
    graph: ReachableStateGraphSnapshot,
) -> dict[str, tuple[tuple[str, str], ...]]:
    edges_by_source: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for edge in sorted(
        graph.edges,
        key=lambda item: (item.source_state_id, item.continuation_id, item.target_state_id),
    ):
        edges_by_source[edge.source_state_id].append((edge.continuation_id, edge.target_state_id))
    return {state_id: tuple(edges) for state_id, edges in edges_by_source.items()}


def _refine_state_partition(
    *,
    state_ids: list[str],
    observation_signatures: dict[str, dict[str, Any]],
    transitions_by_state: dict[str, tuple[tuple[str, str], ...]],
) -> tuple[dict[str, str], dict[str, tuple[str, ...]], dict[str, dict[str, Any]]]:
    current_signatures = {
        state_id: _canonical_signature_key(observation_signatures[state_id])
        for state_id in state_ids
    }
    state_to_class_id, class_members = _partition_from_signatures(state_ids, current_signatures)

    while True:
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


def _canonical_signature_key(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((key, _canonical_signature_key(item)) for key, item in sorted(value.items()))
    if isinstance(value, list):
        return tuple(_canonical_signature_key(item) for item in value)
    return value


def _infer_family_and_variant(config: BenchmarkRunConfig) -> tuple[str, str]:
    config_id = config.config_id
    if config_id.startswith("interference."):
        parts = config_id.split(".")
        if len(parts) >= 3:
            return parts[1], ".".join(parts[2:])
    return config.config_id, "default"


def _repo_path(path: str | Path) -> str:
    if not path:
        return ""
    resolved = Path(path)
    try:
        return resolved.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


__all__ = [
    "compute_review_minimal_behavioral_carrier",
    "load_review_benchmark",
    "load_review_benchmark_from_config",
]
