from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sixbirds_foundations_v._recombination_support.schemas.configs import BenchmarkRunConfig, SearchRunConfig

from .relative_cycle import enumerate_relative_cycle_parameters


NULL_SPACE_SEARCH_ID = "branchwise_factorized_null_space"
CYCLIC_SPACE_SEARCH_ID = "cyclic_relative_carrier_space"


@dataclass(frozen=True)
class SearchCaseSpec:
    case_id: str
    search_space_id: str
    benchmark_id: str
    interface_id: str
    kind: str
    parameters: dict[str, Any]
    benchmark_config_path: Path | None = None
    assemblage_family_id: str | None = None
    observable_family_id: str | None = None
    route_readability_scenario_id: str | None = None
    visibility_scenario_id: str | None = None


def enumerate_branchwise_factorized_null_space(
    *,
    repo_root: Path,
) -> tuple[SearchCaseSpec, ...]:
    config_paths = (
        repo_root / "configs" / "recombination" / "benchmarks" / "flat_classical_mixture_baseline.json",
        repo_root / "configs" / "recombination" / "benchmarks" / "latent_memory_only_control.json",
        repo_root / "configs" / "recombination" / "benchmarks" / "route_marked_suppression.json",
    )
    cases: list[SearchCaseSpec] = []
    for config_path in config_paths:
        config = BenchmarkRunConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
        cases.append(
            SearchCaseSpec(
                case_id=config.config_id,
                search_space_id=NULL_SPACE_SEARCH_ID,
                benchmark_id=config.benchmark_id,
                interface_id=config.interface_id,
                kind="benchmark-config",
                parameters={"config_id": config.config_id},
                benchmark_config_path=config_path,
                assemblage_family_id=config.assemblage_family_id,
                observable_family_id=config.observable_family_id,
                route_readability_scenario_id=config.route_readability_scenario_id,
                visibility_scenario_id=config.visibility_scenario_id,
            )
        )
    return tuple(cases)


def enumerate_cyclic_relative_carrier_space(
    config: SearchRunConfig,
) -> tuple[SearchCaseSpec, ...]:
    parameters = enumerate_relative_cycle_parameters(
        carrier_sizes=config.carrier_sizes,
        route_shift_deltas=config.route_shift_deltas,
        weight_pairs=config.weight_pairs,
    )
    return tuple(
        SearchCaseSpec(
            case_id=parameter.case_id,
            search_space_id=CYCLIC_SPACE_SEARCH_ID,
            benchmark_id="relative_cycle_carrier_base",
            interface_id="mid",
            kind="relative-cycle-parameter",
            parameters={
                "carrier_size": parameter.carrier_size,
                "route_shift_left": parameter.route_shift_left,
                "route_shift_right": parameter.route_shift_right,
                "route_shift_delta": parameter.route_shift_delta,
                "weight_left": str(parameter.weight_left),
                "weight_right": str(parameter.weight_right),
            },
        )
        for parameter in parameters
    )


def enumerate_search_space(
    config: SearchRunConfig,
    *,
    repo_root: Path,
) -> tuple[SearchCaseSpec, ...]:
    if config.search_space_id == NULL_SPACE_SEARCH_ID:
        return enumerate_branchwise_factorized_null_space(repo_root=repo_root)
    if config.search_space_id == CYCLIC_SPACE_SEARCH_ID:
        return enumerate_cyclic_relative_carrier_space(config)
    raise ValueError(f"unsupported bounded search space {config.search_space_id}")


__all__ = [
    "CYCLIC_SPACE_SEARCH_ID",
    "NULL_SPACE_SEARCH_ID",
    "SearchCaseSpec",
    "enumerate_branchwise_factorized_null_space",
    "enumerate_cyclic_relative_carrier_space",
    "enumerate_search_space",
]
