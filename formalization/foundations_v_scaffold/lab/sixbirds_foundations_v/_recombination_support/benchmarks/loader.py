from __future__ import annotations

import json
from collections import deque
from enum import Enum
from fractions import Fraction
from pathlib import Path
from typing import Any

from pydantic import Field, PrivateAttr

from sixbirds_foundations_v._holonomy_support.core.exact import (
    ordered_fraction_mapping,
    project_state_distribution_to_support,
)
from sixbirds_foundations_v._holonomy_support.schemas.manifests import BenchmarkManifest
from sixbirds_foundations_v._holonomy_support.schemas.transport import RouteTransportPackageConfig

from sixbirds_foundations_v._recombination_support.core.catalog import (
    resolve_assemblage_family,
    resolve_observable_family,
    resolve_route_readability_scenario,
    resolve_visibility_scenario,
)
from sixbirds_foundations_v._recombination_support.core.relative_cycle import (
    build_relative_cycle_case,
    normalize_relative_cycle_parameters,
)
from sixbirds_foundations_v._recombination_support.core.substrate import load_inherited_benchmark_context
from sixbirds_foundations_v._recombination_support.runner import (
    REPO_ROOT,
    _is_flattening_completion_partner,
    _is_protocol_internalization_partner,
    _uses_dynamic_relative_cycle_case,
    validate_config_file,
)
from sixbirds_foundations_v._recombination_support.schemas import SixBirdsRecombinationModel
from sixbirds_foundations_v._recombination_support.schemas.configs import BenchmarkRunConfig, RunConfig, SearchRunConfig

from ..core.assemblages import BranchAssemblage
from ..core.relative_cycle import RelativeCycleCase


class LoaderKind(str, Enum):
    RUNNABLE_BENCHMARK = "runnable_benchmark"
    FAMILY_SUMMARY = "family_summary"


class LoadedBenchmark(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-benchmark-loader.v1"
    loader_kind: LoaderKind
    executable: bool
    config_kind: str
    config_path: str
    config_id: str
    benchmark_id: str | None = None
    family: str
    variant: str
    seed: int | None = None
    tags: list[str] = Field(default_factory=list)
    config: RunConfig
    benchmark_manifest_ref: str | None = None
    transport_package_ref: str | None = None
    benchmark_manifest: BenchmarkManifest | None = None
    transport_package_config: RouteTransportPackageConfig | None = None
    support_spec: dict[str, Any] | None = None
    state_space_spec: dict[str, Any] | None = None
    interface_ids: list[str] | None = None
    history_ids: list[str] | None = None
    continuation_ids: list[str] | None = None
    loop_ids: list[str] | None = None
    initial_state_ids: list[str] | None = None
    admissible_generators: list[str] | None = None
    generator_family: str | None = None
    assemblage_family_id: str | None = None
    observable_family_id: str | None = None
    route_readability_scenario_id: str | None = None
    visibility_scenario_id: str | None = None
    comparison_run_id: str | None = None
    carrier_size: int | None = None
    route_shift_delta: int | None = None
    weight_left: str | None = None
    weight_right: str | None = None
    search_space_id: str | None = None
    limit: int | None = None
    carrier_sizes: list[int] | None = None
    route_shift_deltas: list[int] | None = None
    weight_pairs: list[tuple[str, str]] | None = None
    promotion_limit: int | None = None
    anchor_carrier_size: int | None = None
    anchor_route_shift_delta: int | None = None
    anchor_weight_left: str | None = None
    anchor_weight_right: str | None = None
    noise_strengths: list[str] | None = None
    promoted_candidate_ids: list[str] | None = None
    candidate_carrier_sizes: dict[str, list[int]] | None = None
    local_weight_lefts: list[str] | None = None
    local_route_shift_deltas: list[int] | None = None
    threshold_profiles: dict[str, dict[str, str]] | None = None
    protocol_internalization_flag: bool | None = None
    completion_flag: bool | None = None
    flattening_flag: bool | None = None
    rewrite_flag: bool | None = None
    notes: list[str] = Field(default_factory=list)

    _context: Any = PrivateAttr(default=None)
    _runtime_package: Any = PrivateAttr(default=None)
    _assemblages: dict[str, BranchAssemblage] | None = PrivateAttr(default=None)
    _observable_family: Any = PrivateAttr(default=None)
    _relative_cycle_case: RelativeCycleCase | None = PrivateAttr(default=None)

    @property
    def context(self) -> Any:
        return self._context

    @property
    def runtime_package(self) -> Any:
        return self._runtime_package

    @property
    def assemblages(self) -> dict[str, BranchAssemblage]:
        if self._assemblages is None:
            raise ValueError("loaded benchmark is not executable")
        return self._assemblages

    @property
    def observable_family(self) -> Any:
        return self._observable_family


class ReachableStateNodeSnapshot(SixBirdsRecombinationModel):
    state_id: str
    history_ids: list[str]
    source_interface_id: str
    target_interface_id: str
    internal_state_distribution: dict[str, str]
    support_distribution: dict[str, str]


class ReachableStateEdgeSnapshot(SixBirdsRecombinationModel):
    step_index: int
    source_state_id: str
    continuation_id: str
    target_state_id: str


class ReachableStateTraceStepSnapshot(SixBirdsRecombinationModel):
    step_index: int
    source_state_id: str
    source_history_id: str
    continuation_id: str
    target_state_id: str
    target_history_id: str
    source_interface_id: str
    target_interface_id: str
    source_internal_state_distribution: dict[str, str]
    target_internal_state_distribution: dict[str, str]
    source_support_distribution: dict[str, str]
    target_support_distribution: dict[str, str]


class ReachableStateGraphSnapshot(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-reachable-state-graph.v1"
    benchmark_id: str
    config_id: str
    state_count: int
    edge_count: int
    initial_state_ids: list[str]
    states: list[ReachableStateNodeSnapshot]
    edges: list[ReachableStateEdgeSnapshot]
    trace_steps: list[ReachableStateTraceStepSnapshot]


class BranchMemberSnapshot(SixBirdsRecombinationModel):
    history_id: str
    weight: str
    branch_label: str | None = None


class BranchAssemblageSnapshotEntry(SixBirdsRecombinationModel):
    assemblage_id: str
    member_count: int
    total_weight: str
    members: list[BranchMemberSnapshot]


class BranchAssemblageSnapshot(SixBirdsRecombinationModel):
    snapshot_version: str = "recombination-branch-assemblage.v1"
    benchmark_id: str
    config_id: str
    interface_id: str
    assemblage_family_id: str | None = None
    branch_assemblages: list[BranchAssemblageSnapshotEntry]


def load_benchmark(path: str | Path) -> LoadedBenchmark:
    config = validate_config_file(path)
    return load_benchmark_from_config(config, config_path=Path(path))


def load_benchmark_from_config(
    config: RunConfig,
    *,
    config_path: str | Path | None = None,
) -> LoadedBenchmark:
    resolved_path = _repo_path(config_path or "")
    if isinstance(config, BenchmarkRunConfig):
        if _uses_dynamic_relative_cycle_case(config):
            return _load_dynamic_runnable_benchmark(config, resolved_path)
        return _load_static_runnable_benchmark(config, resolved_path)
    return _load_family_summary(config, resolved_path)


def build_reachable_state_graph_snapshot(
    benchmark: LoadedBenchmark,
) -> ReachableStateGraphSnapshot:
    if not benchmark.executable:
        raise ValueError("reachable-state graphs require an executable benchmark")
    package = benchmark.runtime_package
    if package is None:
        raise ValueError("loaded benchmark does not carry a runtime package")

    initial_history_ids = tuple(package.history_ids())
    ordered_generators = tuple(sorted(package.continuation_ids()))
    queue: deque[str] = deque()
    nodes_by_key: dict[tuple[str, tuple[Fraction, ...]], str] = {}
    nodes: dict[str, ReachableStateNodeSnapshot] = {}
    trace_steps: list[ReachableStateTraceStepSnapshot] = []
    edges: list[ReachableStateEdgeSnapshot] = []
    state_history_aliases: dict[str, list[str]] = {}
    runtime_state_by_id: dict[str, Any] = {}

    for history_id in initial_history_ids:
        history = package.get_history(history_id)
        node_id = _register_state_node(
            package=package,
            nodes=nodes,
            nodes_by_key=nodes_by_key,
            state_history_aliases=state_history_aliases,
            history=history,
            state_id=history_id,
            )
        if node_id not in runtime_state_by_id:
            runtime_state_by_id[node_id] = history
            queue.append(node_id)

    seen_edges: set[tuple[str, str, str]] = set()
    step_index = 0
    while queue:
        state_id = queue.popleft()
        source_history = runtime_state_by_id[state_id]
        for continuation_id in ordered_generators:
            continuation = package.get_continuation(continuation_id)
            if continuation.source_interface_id != source_history.target_interface_id:
                continue
            composed_history = package.compose_history_with_continuation_runtime(
                source_history,
                continuation,
                new_id=f"{source_history.history_id}__then__{continuation_id}",
            )
            target_state_key = _state_key_for_history(package, composed_history)
            target_state_id = nodes_by_key.get(target_state_key)
            if target_state_id is None:
                target_state_id = _register_state_node(
                    package=package,
                    nodes=nodes,
                    nodes_by_key=nodes_by_key,
                    state_history_aliases=state_history_aliases,
                    history=composed_history,
                    state_id=composed_history.history_id,
                )
                if target_state_id not in runtime_state_by_id:
                    runtime_state_by_id[target_state_id] = composed_history
                    queue.append(target_state_id)
            edge_key = (state_id, continuation_id, target_state_id)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            edges.append(
                ReachableStateEdgeSnapshot(
                    step_index=step_index,
                    source_state_id=state_id,
                    continuation_id=continuation_id,
                    target_state_id=target_state_id,
                )
            )
            trace_steps.append(
                _build_trace_step_snapshot(
                    package=package,
                    step_index=step_index,
                    source_state_id=state_id,
                    source_history=source_history,
                    continuation_id=continuation_id,
                    target_state_id=target_state_id,
                    target_history=composed_history,
                )
            )
            step_index += 1

    ordered_nodes = [nodes[state_id] for state_id in sorted(nodes)]
    return ReachableStateGraphSnapshot(
        benchmark_id=benchmark.benchmark_id or "",
        config_id=benchmark.config_id,
        state_count=len(ordered_nodes),
        edge_count=len(edges),
        initial_state_ids=list(initial_history_ids),
        states=ordered_nodes,
        edges=edges,
        trace_steps=trace_steps,
    )


def build_branch_assemblage_snapshot(
    benchmark: LoadedBenchmark,
) -> BranchAssemblageSnapshot:
    if not benchmark.executable:
        raise ValueError("branch assemblage snapshots require an executable benchmark")
    assemblages = benchmark.assemblages
    ordered_items = sorted(assemblages.items())
    entries = [
        BranchAssemblageSnapshotEntry(
            assemblage_id=assemblage_id,
            member_count=len(assemblage.members),
            total_weight=str(assemblage.total_weight),
            members=[
                BranchMemberSnapshot(
                    history_id=member.history_id,
                    weight=str(member.weight),
                    branch_label=member.branch_label,
                )
                for member in assemblage.members
            ],
        )
        for assemblage_id, assemblage in ordered_items
    ]
    return BranchAssemblageSnapshot(
        benchmark_id=benchmark.benchmark_id or "",
        config_id=benchmark.config_id,
        interface_id=benchmark.config.interface_id,
        assemblage_family_id=benchmark.assemblage_family_id,
        branch_assemblages=entries,
    )


def dump_loaded_benchmark(benchmark: LoadedBenchmark) -> dict[str, Any]:
    return benchmark.model_dump(mode="json", exclude_none=True)


def dump_reachable_state_graph_snapshot(
    graph: ReachableStateGraphSnapshot,
) -> dict[str, Any]:
    return graph.model_dump(mode="json", exclude_none=True)


def dump_branch_assemblage_snapshot(
    snapshot: BranchAssemblageSnapshot,
) -> dict[str, Any]:
    return snapshot.model_dump(mode="json", exclude_none=True)


def _load_static_runnable_benchmark(
    config: BenchmarkRunConfig,
    config_path: str,
) -> LoadedBenchmark:
    context = load_inherited_benchmark_context(config.benchmark_id)
    assemblages = resolve_assemblage_family(context, config.assemblage_family_id, config.interface_id)
    observable_family = resolve_observable_family(
        context,
        config.observable_family_id,
        config.interface_id,
    )
    if config.route_readability_scenario_id is not None:
        resolve_route_readability_scenario(config.route_readability_scenario_id)
    if config.visibility_scenario_id is not None:
        resolve_visibility_scenario(config.visibility_scenario_id)
    loaded = _build_loaded_benchmark(
        config=config,
        config_path=config_path,
        kind=LoaderKind.RUNNABLE_BENCHMARK,
        executable=True,
        benchmark_manifest=context.manifest,
        benchmark_manifest_ref=_repo_path(context.manifest_path),
        transport_package_config=context.package_config,
        transport_package_ref=_repo_path(context.package_config_path or context.manifest.transport_package_ref or ""),
        support_spec=context.package_config.support.model_dump(mode="json"),
        state_space_spec=context.package_config.state_space.model_dump(mode="json"),
        interface_ids=[interface.interface_id for interface in context.package_config.interfaces],
        history_ids=[history.history_id for history in context.package_config.histories],
        continuation_ids=[continuation.continuation_id for continuation in context.package_config.continuations],
        loop_ids=[loop.loop_id for loop in context.package_config.loops],
        initial_state_ids=[history.history_id for history in context.package_config.histories],
        admissible_generators=[continuation.continuation_id for continuation in context.runtime_package.continuations],
        generator_family=config.assemblage_family_id,
        branch_assemblages=assemblages,
        observable_family=observable_family,
        notes=[
            "exact runnable benchmark",
            f"same_support_required={context.package_config.support.same_support_required}",
        ],
    )
    loaded._context = context
    loaded._runtime_package = context.runtime_package
    loaded._assemblages = dict(assemblages)
    loaded._observable_family = observable_family
    return loaded


def _load_dynamic_runnable_benchmark(
    config: BenchmarkRunConfig,
    config_path: str,
) -> LoadedBenchmark:
    context = load_inherited_benchmark_context(config.benchmark_id)
    case = build_relative_cycle_case(
        normalize_relative_cycle_parameters(
            carrier_size=config.carrier_size or 0,
            route_shift_delta=config.route_shift_delta or 0,
            weight_left=config.weight_left or "",
            weight_right=config.weight_right or "",
        ),
        context=context,
    )
    loaded = _build_loaded_benchmark(
        config=config,
        config_path=config_path,
        kind=LoaderKind.RUNNABLE_BENCHMARK,
        executable=True,
        benchmark_manifest=context.manifest,
        benchmark_manifest_ref=_repo_path(context.manifest_path),
        transport_package_config=context.package_config,
        transport_package_ref=_repo_path(context.package_config_path or context.manifest.transport_package_ref or ""),
        support_spec=context.package_config.support.model_dump(mode="json"),
        state_space_spec=context.package_config.state_space.model_dump(mode="json"),
        interface_ids=[interface.interface_id for interface in context.package_config.interfaces],
        history_ids=[history.history_id for history in context.package_config.histories],
        continuation_ids=[continuation.continuation_id for continuation in context.package_config.continuations],
        loop_ids=[loop.loop_id for loop in context.package_config.loops],
        initial_state_ids=[history.history_id for history in context.package_config.histories],
        admissible_generators=[continuation.continuation_id for continuation in context.runtime_package.continuations],
        generator_family=config.assemblage_family_id,
        branch_assemblages=case.assemblages,
        observable_family=case.observable_family,
        notes=[
            "exact runnable benchmark",
            "dynamic relative-cycle case",
        ],
    )
    loaded._context = context
    loaded._runtime_package = context.runtime_package
    loaded._assemblages = dict(case.assemblages)
    loaded._observable_family = case.observable_family
    loaded._relative_cycle_case = case
    return loaded


def _load_family_summary(
    config: SearchRunConfig,
    config_path: str,
) -> LoadedBenchmark:
    family, variant = _infer_family_and_variant(config)
    return LoadedBenchmark(
        loader_kind=LoaderKind.FAMILY_SUMMARY,
        executable=False,
        config_kind=config.config_kind,
        config_path=config_path,
        config_id=config.config_id,
        benchmark_id=None,
        family=family,
        variant=variant,
        seed=config.seed,
        tags=[],
        config=config,
        search_space_id=config.search_space_id,
        limit=config.limit,
        carrier_sizes=list(config.carrier_sizes) if config.carrier_sizes is not None else None,
        route_shift_deltas=list(config.route_shift_deltas)
        if config.route_shift_deltas is not None
        else None,
        weight_pairs=list(config.weight_pairs) if config.weight_pairs is not None else None,
        promotion_limit=config.promotion_limit,
        comparison_run_id=config.comparison_run_id,
        anchor_carrier_size=config.anchor_carrier_size,
        anchor_route_shift_delta=config.anchor_route_shift_delta,
        anchor_weight_left=config.anchor_weight_left,
        anchor_weight_right=config.anchor_weight_right,
        noise_strengths=list(config.noise_strengths) if config.noise_strengths is not None else None,
        promoted_candidate_ids=list(config.promoted_candidate_ids)
        if config.promoted_candidate_ids is not None
        else None,
        candidate_carrier_sizes={
            key: list(values) for key, values in (config.candidate_carrier_sizes or {}).items()
        }
        if config.candidate_carrier_sizes is not None
        else None,
        local_weight_lefts=list(config.local_weight_lefts)
        if config.local_weight_lefts is not None
        else None,
        local_route_shift_deltas=list(config.local_route_shift_deltas)
        if config.local_route_shift_deltas is not None
        else None,
        threshold_profiles=config.threshold_profiles,
        protocol_internalization_flag=None,
        completion_flag=None,
        flattening_flag=None,
        rewrite_flag=None,
        notes=["non-executable family summary"],
    )


def _build_loaded_benchmark(
    *,
    config: BenchmarkRunConfig,
    config_path: str,
    kind: LoaderKind,
    executable: bool,
    benchmark_manifest: BenchmarkManifest,
    benchmark_manifest_ref: str,
    transport_package_config: RouteTransportPackageConfig,
    transport_package_ref: str,
    support_spec: dict[str, Any],
    state_space_spec: dict[str, Any],
    interface_ids: list[str],
    history_ids: list[str],
    continuation_ids: list[str],
    loop_ids: list[str],
    initial_state_ids: list[str],
    admissible_generators: list[str],
    generator_family: str | None,
    branch_assemblages: dict[str, BranchAssemblage],
    observable_family: Any,
    notes: list[str],
) -> LoadedBenchmark:
    family, variant = _infer_family_and_variant(config)
    return LoadedBenchmark(
        loader_kind=kind,
        executable=executable,
        config_kind=config.config_kind,
        config_path=config_path,
        config_id=config.config_id,
        benchmark_id=config.benchmark_id,
        family=family,
        variant=variant,
        seed=config.seed,
        tags=list(config.tags),
        config=config,
        benchmark_manifest_ref=benchmark_manifest_ref,
        transport_package_ref=transport_package_ref,
        benchmark_manifest=benchmark_manifest,
        transport_package_config=transport_package_config,
        support_spec=support_spec,
        state_space_spec=state_space_spec,
        interface_ids=interface_ids,
        history_ids=history_ids,
        continuation_ids=continuation_ids,
        loop_ids=loop_ids,
        initial_state_ids=initial_state_ids,
        admissible_generators=admissible_generators,
        generator_family=generator_family,
        assemblage_family_id=config.assemblage_family_id,
        observable_family_id=config.observable_family_id,
        route_readability_scenario_id=config.route_readability_scenario_id,
        visibility_scenario_id=config.visibility_scenario_id,
        comparison_run_id=config.comparison_run_id,
        carrier_size=config.carrier_size,
        route_shift_delta=config.route_shift_delta,
        weight_left=config.weight_left,
        weight_right=config.weight_right,
        protocol_internalization_flag=(
            True
            if _is_protocol_internalization_partner(config)
            else False
            if "protocol_trap" in config.tags
            else None
        ),
        completion_flag=(
            True
            if _is_flattening_completion_partner(config)
            else False
            if "flattening_control" in config.tags
            else None
        ),
        flattening_flag=True if "flattening_control" in config.tags else None,
        rewrite_flag=True if "rewrite" in config.tags else None,
        notes=notes,
    )


def _register_state_node(
    *,
    package: Any,
    nodes: dict[str, ReachableStateNodeSnapshot],
    nodes_by_key: dict[tuple[str, tuple[Fraction, ...]], str],
    state_history_aliases: dict[str, list[str]],
    history: Any,
    state_id: str,
) -> str:
    state_key = _state_key_for_history(package, history)
    existing = nodes_by_key.get(state_key)
    if existing is not None:
        if history.history_id not in state_history_aliases[existing]:
            state_history_aliases[existing].append(history.history_id)
            nodes[existing] = nodes[existing].model_copy(
                update={"history_ids": list(state_history_aliases[existing])}
            )
        return existing
    support_distribution = _support_distribution_for_history(package, history)
    node = ReachableStateNodeSnapshot(
        state_id=state_id,
        history_ids=[history.history_id],
        source_interface_id=history.source_interface_id,
        target_interface_id=history.target_interface_id,
        internal_state_distribution=_fraction_mapping_to_json(
            ordered_fraction_mapping(
                package.state_space.internal_state_ids,
                history.probabilities,
            )
        ),
        support_distribution=_fraction_mapping_to_json(support_distribution),
    )
    nodes[state_id] = node
    nodes_by_key[state_key] = state_id
    state_history_aliases[state_id] = [history.history_id]
    return state_id


def _build_trace_step_snapshot(
    *,
    package: Any,
    step_index: int,
    source_state_id: str,
    source_history: Any,
    continuation_id: str,
    target_state_id: str,
    target_history: Any,
) -> ReachableStateTraceStepSnapshot:
    return ReachableStateTraceStepSnapshot(
        step_index=step_index,
        source_state_id=source_state_id,
        source_history_id=source_history.history_id,
        continuation_id=continuation_id,
        target_state_id=target_state_id,
        target_history_id=target_history.history_id,
        source_interface_id=source_history.target_interface_id,
        target_interface_id=target_history.target_interface_id,
        source_internal_state_distribution=_fraction_mapping_to_json(
            ordered_fraction_mapping(
                package.state_space.internal_state_ids,
                source_history.probabilities,
            )
        ),
        target_internal_state_distribution=_fraction_mapping_to_json(
            ordered_fraction_mapping(
                package.state_space.internal_state_ids,
                target_history.probabilities,
            )
        ),
        source_support_distribution=_fraction_mapping_to_json(
            _support_distribution_for_history(package, source_history)
        ),
        target_support_distribution=_fraction_mapping_to_json(
            _support_distribution_for_history(package, target_history)
        ),
    )


def _support_distribution_for_history(package: Any, history: Any) -> dict[str, Fraction]:
    projected = project_state_distribution_to_support(
        history.probabilities,
        state_ids=package.state_space.internal_state_ids,
        support_labels=package.support.visible_support_labels,
        support_projection=package.state_space.support_projection,
    )
    return dict(ordered_fraction_mapping(package.support.visible_support_labels, projected))


def _state_key_for_history(package: Any, history: Any) -> tuple[str, tuple[Fraction, ...]]:
    return (history.target_interface_id, tuple(history.probabilities))


def _fraction_mapping_to_json(values: dict[str, Fraction] | Any) -> dict[str, str]:
    return {key: str(value) for key, value in dict(values).items()}


def _infer_family_and_variant(config: BenchmarkRunConfig | SearchRunConfig) -> tuple[str, str]:
    config_id = config.config_id
    if config_id.startswith("interference."):
        parts = config_id.split(".")
        if len(parts) >= 3:
            return parts[1], ".".join(parts[2:])
    if isinstance(config, SearchRunConfig):
        if config.search_space_id == "cyclic_relative_carrier_space":
            return "cyclic_relative_carrier", "summary"
        if config.search_space_id == "relative_cycle_dissipative_collapse":
            return "dissipative_washout", "summary"
        return config.search_space_id, "summary"
    return config.config_id, "default"


def _repo_path(path: str | Path) -> str:
    if not path:
        return ""
    resolved = Path(path)
    try:
        return resolved.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "BranchAssemblageSnapshot",
    "BranchAssemblageSnapshotEntry",
    "BranchMemberSnapshot",
    "LoadedBenchmark",
    "LoaderKind",
    "ReachableStateEdgeSnapshot",
    "ReachableStateGraphSnapshot",
    "ReachableStateNodeSnapshot",
    "ReachableStateTraceStepSnapshot",
    "build_branch_assemblage_snapshot",
    "build_reachable_state_graph_snapshot",
    "dump_branch_assemblage_snapshot",
    "dump_loaded_benchmark",
    "dump_reachable_state_graph_snapshot",
    "load_benchmark",
    "load_benchmark_from_config",
]
