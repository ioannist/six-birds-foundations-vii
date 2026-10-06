from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from .common import (
    SixBirdsRecombinationModel,
    ensure_nonempty_string,
    ensure_optional_nonempty_string,
    ensure_unique_strings,
)
from .enums import FrozenSliceConfigVersion


class BenchmarkRunConfig(SixBirdsRecombinationModel):
    schema_version: Literal["recombination-benchmark-run-config.v1"]
    config_kind: Literal["benchmark-run"]
    config_id: str
    benchmark_id: str
    interface_id: str
    assemblage_family_id: str
    observable_family_id: str
    route_readability_scenario_id: str | None = None
    visibility_scenario_id: str | None = None
    comparison_run_id: str | None = None
    carrier_size: int | None = Field(default=None, ge=2)
    route_shift_delta: int | None = Field(default=None, ge=1)
    weight_left: str | None = None
    weight_right: str | None = None
    seed: int = 0
    run_id: str | None = None
    generate_plot_artifacts: bool = False
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_config(self) -> "BenchmarkRunConfig":
        ensure_nonempty_string(self.config_id, "config_id")
        ensure_nonempty_string(self.benchmark_id, "benchmark_id")
        ensure_nonempty_string(self.interface_id, "interface_id")
        ensure_nonempty_string(self.assemblage_family_id, "assemblage_family_id")
        ensure_nonempty_string(self.observable_family_id, "observable_family_id")
        ensure_optional_nonempty_string(
            self.route_readability_scenario_id,
            "route_readability_scenario_id",
        )
        ensure_optional_nonempty_string(
            self.visibility_scenario_id,
            "visibility_scenario_id",
        )
        ensure_optional_nonempty_string(self.comparison_run_id, "comparison_run_id")
        ensure_optional_nonempty_string(self.weight_left, "weight_left")
        ensure_optional_nonempty_string(self.weight_right, "weight_right")
        ensure_optional_nonempty_string(self.run_id, "run_id")
        relative_cycle_fields = (
            self.carrier_size,
            self.route_shift_delta,
            self.weight_left,
            self.weight_right,
        )
        if any(value is not None for value in relative_cycle_fields) and not all(
            value is not None for value in relative_cycle_fields
        ):
            raise ValueError(
                "carrier_size, route_shift_delta, weight_left, and weight_right must be provided together"
            )
        ensure_unique_strings(self.tags, "tags")
        for tag in self.tags:
            ensure_nonempty_string(tag, "tags")
        return self


class SearchRunConfig(SixBirdsRecombinationModel):
    schema_version: Literal["recombination-search-run-config.v1"]
    config_kind: Literal["search-run"]
    config_id: str
    search_space_id: str
    seed: int = 0
    limit: int = Field(default=10, ge=1)
    carrier_sizes: list[int] | None = None
    route_shift_deltas: list[int] | None = None
    weight_pairs: list[tuple[str, str]] | None = None
    promotion_limit: int | None = Field(default=None, ge=1)
    comparison_run_id: str | None = None
    anchor_carrier_size: int | None = Field(default=None, ge=2)
    anchor_route_shift_delta: int | None = Field(default=None, ge=1)
    anchor_weight_left: str | None = None
    anchor_weight_right: str | None = None
    noise_strengths: list[str] | None = None
    promoted_candidate_ids: list[str] | None = None
    candidate_carrier_sizes: dict[str, list[int]] | None = None
    local_weight_lefts: list[str] | None = None
    local_route_shift_deltas: list[int] | None = None
    threshold_profiles: dict[str, dict[str, str]] | None = None

    @model_validator(mode="after")
    def validate_config(self) -> "SearchRunConfig":
        ensure_nonempty_string(self.config_id, "config_id")
        ensure_nonempty_string(self.search_space_id, "search_space_id")
        if self.carrier_sizes is not None:
            for carrier_size in self.carrier_sizes:
                if carrier_size < 2:
                    raise ValueError("carrier_sizes must be at least 2")
        if self.route_shift_deltas is not None:
            for route_shift_delta in self.route_shift_deltas:
                if route_shift_delta < 1:
                    raise ValueError("route_shift_deltas must be positive")
        if self.weight_pairs is not None:
            for weight_pair in self.weight_pairs:
                if len(weight_pair) != 2:
                    raise ValueError("weight_pairs entries must contain exactly two weights")
                ensure_nonempty_string(weight_pair[0], "weight_pairs")
                ensure_nonempty_string(weight_pair[1], "weight_pairs")
        ensure_optional_nonempty_string(self.comparison_run_id, "comparison_run_id")
        ensure_optional_nonempty_string(self.anchor_weight_left, "anchor_weight_left")
        ensure_optional_nonempty_string(self.anchor_weight_right, "anchor_weight_right")
        if self.noise_strengths is not None:
            for noise_strength in self.noise_strengths:
                ensure_nonempty_string(noise_strength, "noise_strengths")
        if self.promoted_candidate_ids is not None:
            ensure_unique_strings(self.promoted_candidate_ids, "promoted_candidate_ids")
            for candidate_id in self.promoted_candidate_ids:
                ensure_nonempty_string(candidate_id, "promoted_candidate_ids")
        if self.candidate_carrier_sizes is not None:
            for candidate_id, carrier_sizes in self.candidate_carrier_sizes.items():
                ensure_nonempty_string(candidate_id, "candidate_carrier_sizes")
                if not carrier_sizes:
                    raise ValueError("candidate_carrier_sizes entries must be non-empty")
                for carrier_size in carrier_sizes:
                    if carrier_size < 2:
                        raise ValueError("candidate_carrier_sizes must be at least 2")
        if self.local_weight_lefts is not None:
            for weight_left in self.local_weight_lefts:
                ensure_nonempty_string(weight_left, "local_weight_lefts")
        if self.local_route_shift_deltas is not None:
            for route_shift_delta in self.local_route_shift_deltas:
                if route_shift_delta < 1:
                    raise ValueError("local_route_shift_deltas must be positive")
        if self.threshold_profiles is not None:
            for profile_name, thresholds in self.threshold_profiles.items():
                ensure_nonempty_string(profile_name, "threshold_profiles")
                required_fields = (
                    "min_recombination_gap",
                    "min_visibility_recovery_gap",
                    "max_route_readability",
                )
                for field_name in required_fields:
                    if field_name not in thresholds:
                        raise ValueError(
                            f"threshold profile {profile_name!r} is missing {field_name!r}"
                        )
                    ensure_nonempty_string(
                        thresholds[field_name],
                        f"threshold_profiles[{profile_name!r}][{field_name!r}]",
                    )
        return self


class FrozenSliceSupportConeFilters(SixBirdsRecombinationModel):
    benchmark_ids: list[str] | None = None
    source_kinds: list[str] | None = None
    control_modes: list[str] | None = None
    phase_modes: list[str] | None = None
    strategy_ids: list[str] | None = None
    comparison_groups: list[str] | None = None
    tags: list[str] | None = None

    @model_validator(mode="after")
    def validate_filters(self) -> "FrozenSliceSupportConeFilters":
        for field_name in (
            "benchmark_ids",
            "source_kinds",
            "control_modes",
            "phase_modes",
            "strategy_ids",
            "comparison_groups",
            "tags",
        ):
            values = getattr(self, field_name)
            if values is None:
                continue
            ensure_unique_strings(values, field_name)
            for value in values:
                ensure_nonempty_string(value, field_name)
        return self


class FrozenSliceSupportCone(SixBirdsRecombinationModel):
    support_cone_id: str
    support_atom_ids: list[str] = Field(default_factory=list)
    filters: FrozenSliceSupportConeFilters | None = None
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_support_cone(self) -> "FrozenSliceSupportCone":
        ensure_nonempty_string(self.support_cone_id, "support_cone_id")
        ensure_unique_strings(self.support_atom_ids, "support_atom_ids")
        for value in self.support_atom_ids + self.notes:
            ensure_nonempty_string(value, "support_cone entries")
        has_filter_payload = False
        if self.filters is not None:
            has_filter_payload = any(
                getattr(self.filters, field_name)
                for field_name in (
                    "benchmark_ids",
                    "source_kinds",
                    "control_modes",
                    "phase_modes",
                    "strategy_ids",
                    "comparison_groups",
                    "tags",
                )
            )
        if not self.support_atom_ids and not has_filter_payload:
            raise ValueError(
                "support_cone requires explicit support_atom_ids or at least one structured filter"
            )
        return self


class FrozenSliceTerm(SixBirdsRecombinationModel):
    metric_name: str
    aggregation_op: Literal["mean", "sum", "min", "max"]
    required: bool = True
    weight: float | None = Field(default=None, gt=0)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_term(self) -> "FrozenSliceTerm":
        ensure_nonempty_string(self.metric_name, "metric_name")
        for note in self.notes:
            ensure_nonempty_string(note, "notes")
        return self


class FrozenSliceAggregationPolicy(SixBirdsRecombinationModel):
    missing_optional_term_policy: Literal["ignore"] = "ignore"
    excluded_candidate_policy: Literal["exclude"] = "exclude"


class FrozenSliceConfig(SixBirdsRecombinationModel):
    schema_version: FrozenSliceConfigVersion = FrozenSliceConfigVersion.V2
    config_kind: Literal["frozen-slice"] = "frozen-slice"
    config_id: str
    slice_id: str
    benchmark_id: str | None = None
    interface_id: str | None = None
    support_cone: FrozenSliceSupportCone
    yield_terms: list[FrozenSliceTerm] = Field(default_factory=list)
    cost_terms: list[FrozenSliceTerm] = Field(default_factory=list)
    aggregation_policy: FrozenSliceAggregationPolicy | None = None
    comparison_tolerance: float | None = Field(default=None, ge=0)
    cone_equivalence_tolerance: float | None = Field(default=None, ge=0)
    reference_run_id: str | None = None
    notes: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_config(self) -> "FrozenSliceConfig":
        ensure_nonempty_string(self.config_id, "config_id")
        ensure_nonempty_string(self.slice_id, "slice_id")
        ensure_optional_nonempty_string(self.benchmark_id, "benchmark_id")
        ensure_optional_nonempty_string(self.interface_id, "interface_id")
        ensure_optional_nonempty_string(self.reference_run_id, "reference_run_id")
        ensure_unique_strings(self.tags, "tags")
        for value in self.tags + self.notes:
            ensure_nonempty_string(value, "frozen slice config notes/tags")
        if not self.yield_terms and not self.cost_terms:
            raise ValueError("frozen-slice config requires at least one yield term or cost term")
        return self


RunConfig = BenchmarkRunConfig | SearchRunConfig


__all__ = [
    "BenchmarkRunConfig",
    "FrozenSliceConfig",
    "RunConfig",
    "SearchRunConfig",
]
