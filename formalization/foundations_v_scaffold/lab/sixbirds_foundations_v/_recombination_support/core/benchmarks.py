from __future__ import annotations

from sixbirds_foundations_v._holonomy_support.benchmarks import (
    REPO_ROOT,
    benchmark_manifest_path_for_id as _benchmark_manifest_path_for_id,
)
from sixbirds_foundations_v._holonomy_support.benchmarks import (
    load_benchmark_manifest_for_id as _load_benchmark_manifest_for_id,
)
from sixbirds_foundations_v._holonomy_support.validation import load_benchmark_manifest


RECOMBINATION_ONLY_BENCHMARK_MANIFESTS = {
    "protocol_trap_split_recombine": (
        REPO_ROOT / "configs" / "benchmarks" / "protocol_trap_split_recombine.benchmark.json"
    ),
    "protocol_trap_split_recombine_internalized": (
        REPO_ROOT
        / "configs"
        / "benchmarks"
        / "protocol_trap_split_recombine_internalized.benchmark.json"
    ),
    "protocol_trap_split_recombine_erased": (
        REPO_ROOT
        / "configs"
        / "benchmarks"
        / "protocol_trap_split_recombine_erased.benchmark.json"
    ),
    "relative_cycle_carrier_base": (
        REPO_ROOT / "configs" / "benchmarks" / "relative_cycle_carrier_base.benchmark.json"
    ),
    "route_marked_split_recombine": (
        REPO_ROOT / "configs" / "benchmarks" / "route_marked_split_recombine.benchmark.json"
    ),
    "route_erased_split_recombine": (
        REPO_ROOT / "configs" / "benchmarks" / "route_erased_split_recombine.benchmark.json"
    ),
}


def benchmark_manifest_path_for_id(benchmark_id: str):
    custom_path = RECOMBINATION_ONLY_BENCHMARK_MANIFESTS.get(benchmark_id)
    if custom_path is not None:
        return custom_path
    return _benchmark_manifest_path_for_id(benchmark_id)


def load_benchmark_manifest_for_id(benchmark_id: str):
    custom_path = RECOMBINATION_ONLY_BENCHMARK_MANIFESTS.get(benchmark_id)
    if custom_path is not None:
        return load_benchmark_manifest(custom_path)
    return _load_benchmark_manifest_for_id(benchmark_id)


__all__ = [
    "benchmark_manifest_path_for_id",
    "load_benchmark_manifest_for_id",
]
