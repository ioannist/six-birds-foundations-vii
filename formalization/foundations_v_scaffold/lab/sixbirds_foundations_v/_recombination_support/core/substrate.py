from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sixbirds_foundations_v._holonomy_support.benchmarks import resolve_repo_relative_path
from sixbirds_foundations_v._holonomy_support.core import (
    EventPackageRuntime,
    HistoryDistributionRuntime,
    InterfaceRuntime,
    RouteTransportPackage,
    SupportRuntime,
    load_route_transport_package_from_config,
)
from sixbirds_foundations_v._holonomy_support.schemas.manifests import BenchmarkManifest
from sixbirds_foundations_v._holonomy_support.schemas.transport import RouteTransportPackageConfig

from .benchmarks import benchmark_manifest_path_for_id, load_benchmark_manifest_for_id


@dataclass(frozen=True)
class InheritedBenchmarkContext:
    benchmark_id: str
    manifest_path: Path
    manifest: BenchmarkManifest
    package_config_path: Path | None
    package_config: RouteTransportPackageConfig
    runtime_package: RouteTransportPackage


def load_inherited_benchmark_context(benchmark_id: str) -> InheritedBenchmarkContext:
    manifest_path = benchmark_manifest_path_for_id(benchmark_id)
    manifest = load_benchmark_manifest_for_id(benchmark_id)
    package_config_path: Path | None = None
    if manifest.transport_package is not None:
        package_config = manifest.transport_package
    else:
        if manifest.transport_package_ref is None:
            raise ValueError(
                f"benchmark manifest {manifest_path} does not specify a transport package"
            )
        package_config_path = resolve_repo_relative_path(manifest.transport_package_ref)
        package_config = RouteTransportPackageConfig.model_validate_json(
            package_config_path.read_text(encoding="utf-8")
        )
    runtime_package = load_route_transport_package_from_config(package_config)
    return InheritedBenchmarkContext(
        benchmark_id=benchmark_id,
        manifest_path=manifest_path,
        manifest=manifest,
        package_config_path=package_config_path,
        package_config=package_config,
        runtime_package=runtime_package,
    )


__all__ = [
    "EventPackageRuntime",
    "HistoryDistributionRuntime",
    "InheritedBenchmarkContext",
    "InterfaceRuntime",
    "RouteTransportPackage",
    "SupportRuntime",
    "load_inherited_benchmark_context",
]
