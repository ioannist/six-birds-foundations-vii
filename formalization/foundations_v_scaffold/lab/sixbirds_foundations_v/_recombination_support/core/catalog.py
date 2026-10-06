from __future__ import annotations

from typing import Mapping

from .assemblages import BranchAssemblage, build_branch_assemblage, make_branch_member
from .observables import (
    EventDistribution,
    RecombinationObservableFamily,
    build_event_distribution,
    build_observable_family,
    make_branchwise_mixing_observable,
    make_history_sensitive_observable,
)
from .substrate import InheritedBenchmarkContext
from .relative_cycle import (
    build_relative_cycle_case,
    build_relative_cycle_completion_observable_family,
    build_relative_cycle_visibility_scenario,
    default_anchor_parameters,
)


ASSEMBLAGE_FAMILY_IDS = (
    "flat_classical_mixture_baseline_family",
    "flat_branchwise_only_family",
    "flat_strict_refinement_family",
    "latent_memory_only_control_family",
    "latent_nontrivial_family",
    "protocol_trap_internalized_family",
    "protocol_trap_erasure_recovery_family",
    "protocol_trap_uninternalized_family",
    "relative_cycle_anchor_completion_partner_family",
    "relative_cycle_anchor_positive_family",
    "route_erasure_recovery_family",
    "route_marked_suppression_family",
)

OBSERVABLE_FAMILY_IDS = (
    "flat_classical_mixture_baseline_observable_family",
    "flat_branchwise_only_observable_family",
    "flat_strict_refinement_observable_family",
    "latent_memory_only_control_observable_family",
    "latent_nontrivial_observable_family",
    "protocol_trap_observable_family",
    "protocol_trap_erasure_recovery_observable_family",
    "relative_cycle_anchor_completion_partner_observable_family",
    "relative_cycle_anchor_positive_observable_family",
    "route_erasure_recovery_observable_family",
    "route_marked_suppression_observable_family",
)

ROUTE_READABILITY_SCENARIO_IDS = (
    "perfect_binary_route_recovery",
    "relative_cycle_anchor_readability",
    "route_erasure_readability",
    "route_marker_readability",
    "unreadable_binary_route_recovery",
)

VISIBILITY_SCENARIO_IDS = (
    "binary_visibility_recovery",
    "relative_cycle_anchor_screen_visibility",
    "route_eraser_screen_visibility",
    "route_marker_screen_visibility",
)

SEARCH_SPACE_IDS = (
    "toy_recombination_catalog",
    "branchwise_factorized_null_space",
    "cyclic_relative_carrier_space",
    "relative_cycle_positive_family",
    "relative_cycle_dissipative_collapse",
    "promoted_candidates_robustness",
)


def resolve_assemblage_family(
    context: InheritedBenchmarkContext,
    assemblage_family_id: str,
    interface_id: str,
) -> dict[str, BranchAssemblage]:
    if interface_id != "mid":
        raise ValueError(
            f"built-in assemblage families are currently defined only for interface mid, not {interface_id}"
        )
    if assemblage_family_id == "flat_branchwise_only_family":
        _require_benchmark(context, "flat_control", assemblage_family_id)
        return _flat_family(context)
    if assemblage_family_id == "flat_classical_mixture_baseline_family":
        _require_benchmark(context, "flat_control", assemblage_family_id)
        return _flat_family(context)
    if assemblage_family_id == "flat_strict_refinement_family":
        _require_benchmark(context, "flat_control", assemblage_family_id)
        return _flat_family(context)
    if assemblage_family_id == "latent_nontrivial_family":
        _require_benchmark(context, "latent_memory_base", assemblage_family_id)
        return _latent_family(context)
    if assemblage_family_id == "latent_memory_only_control_family":
        _require_benchmark(context, "latent_memory_base", assemblage_family_id)
        return _latent_family(context)
    if assemblage_family_id == "protocol_trap_uninternalized_family":
        _require_benchmark(context, "protocol_trap_split_recombine", assemblage_family_id)
        return _protocol_trap_family(context)
    if assemblage_family_id == "protocol_trap_internalized_family":
        _require_benchmark(
            context,
            "protocol_trap_split_recombine_internalized",
            assemblage_family_id,
        )
        return _protocol_trap_family(context)
    if assemblage_family_id == "protocol_trap_erasure_recovery_family":
        _require_benchmark(
            context,
            "protocol_trap_split_recombine_erased",
            assemblage_family_id,
        )
        return _protocol_erasure_recovery_family(context)
    if assemblage_family_id == "relative_cycle_anchor_positive_family":
        _require_benchmark(context, "relative_cycle_carrier_base", assemblage_family_id)
        return _relative_cycle_anchor_family(context)
    if assemblage_family_id == "relative_cycle_anchor_completion_partner_family":
        _require_benchmark(context, "relative_cycle_carrier_base", assemblage_family_id)
        return _relative_cycle_anchor_family(context)
    if assemblage_family_id == "route_marked_suppression_family":
        _require_benchmark(context, "route_marked_split_recombine", assemblage_family_id)
        return _route_marked_family(context)
    if assemblage_family_id == "route_erasure_recovery_family":
        _require_benchmark(context, "route_erased_split_recombine", assemblage_family_id)
        return _route_erasure_family(context)
    raise ValueError(f"unknown assemblage_family_id {assemblage_family_id}")


def resolve_observable_family(
    context: InheritedBenchmarkContext,
    observable_family_id: str,
    interface_id: str,
) -> RecombinationObservableFamily:
    if interface_id != "mid":
        raise ValueError(
            f"built-in observable families are currently defined only for interface mid, not {interface_id}"
        )
    if observable_family_id == "flat_branchwise_only_observable_family":
        _require_benchmark(context, "flat_control", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "flat_mix",
                    "mid",
                    {"C0": {"quiet": "1/4", "loud": "3/4"}},
                )
            ],
        )
    if observable_family_id == "flat_classical_mixture_baseline_observable_family":
        _require_benchmark(context, "flat_control", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "flat_classical_mix",
                    "mid",
                    {"C0": {"quiet": "1/4", "loud": "3/4"}},
                )
            ],
        )
    if observable_family_id == "flat_strict_refinement_observable_family":
        _require_benchmark(context, "flat_control", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "flat_mix",
                    "mid",
                    {"C0": {"quiet": 1}},
                ),
                make_history_sensitive_observable(
                    "flat_history",
                    "mid",
                    {
                        "h_mid_0": {"red": 1, "blue": 0},
                        "h_mid_1": {"red": 0, "blue": 1},
                    },
                ),
            ],
        )
    if observable_family_id == "latent_nontrivial_observable_family":
        _require_benchmark(context, "latent_memory_base", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "latent_mix",
                    "mid",
                    {
                        "C0": {"red": 1, "blue": 0},
                        "C1": {"red": 0, "blue": 1},
                    },
                ),
                make_history_sensitive_observable(
                    "latent_history",
                    "mid",
                    {
                        "h_mid_0": {"red": 1, "blue": 0},
                        "h_mid_1": {"red": 0, "blue": 1},
                    },
                ),
            ],
        )
    if observable_family_id == "latent_memory_only_control_observable_family":
        _require_benchmark(context, "latent_memory_base", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "latent_memory_only_mix",
                    "mid",
                    {
                        "C0": {"red": 1, "blue": 0},
                        "C1": {"red": 0, "blue": 1},
                    },
                )
            ],
        )
    if observable_family_id == "protocol_trap_observable_family":
        expected_benchmarks = {
            "protocol_trap_split_recombine",
            "protocol_trap_split_recombine_internalized",
        }
        if context.benchmark_id not in expected_benchmarks:
            raise ValueError(
                f"{observable_family_id} requires one of {sorted(expected_benchmarks)}, got {context.benchmark_id}"
            )
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "protocol_trap_screen_mix",
                    "mid",
                    {
                        "C0": {"screen_left": "1/2", "screen_right": "1/2"},
                        "C1": {"screen_left": "1/2", "screen_right": "1/2"},
                    },
                ),
                make_history_sensitive_observable(
                    "protocol_trap_hidden_scheduler_readout",
                    "mid",
                    {
                        "h_mid_0": {"screen_left": 1, "screen_right": 0},
                        "h_mid_1": {"screen_left": 0, "screen_right": 1},
                    },
                ),
            ],
        )
    if observable_family_id == "protocol_trap_erasure_recovery_observable_family":
        _require_benchmark(
            context,
            "protocol_trap_split_recombine_erased",
            observable_family_id,
        )
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "protocol_erased_mix",
                    "mid",
                    {
                        "C0": {"erased_signal": "1/2", "erased_silence": "1/2"},
                    },
                ),
                make_history_sensitive_observable(
                    "protocol_eraser_screen_history",
                    "mid",
                    {
                        "h_mid_0": {"screen_bright": 1, "screen_dark": 0},
                        "h_mid_1": {"screen_bright": 0, "screen_dark": 1},
                    },
                ),
            ],
        )
    if observable_family_id == "relative_cycle_anchor_positive_observable_family":
        _require_benchmark(context, "relative_cycle_carrier_base", observable_family_id)
        return build_relative_cycle_case(default_anchor_parameters(), context=context).observable_family
    if observable_family_id == "relative_cycle_anchor_completion_partner_observable_family":
        _require_benchmark(context, "relative_cycle_carrier_base", observable_family_id)
        return build_relative_cycle_completion_observable_family(default_anchor_parameters())
    if observable_family_id == "route_marked_suppression_observable_family":
        _require_benchmark(context, "route_marked_split_recombine", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "route_marker_mix",
                    "mid",
                    {
                        "C0": {"marker_left": 1, "marker_right": 0},
                        "C1": {"marker_left": 0, "marker_right": 1},
                    },
                ),
                make_branchwise_mixing_observable(
                    "screen_pattern_mix",
                    "mid",
                    {
                        "C0": {"screen_bright": "1/2", "screen_dark": "1/2"},
                        "C1": {"screen_bright": "1/2", "screen_dark": "1/2"},
                    },
                ),
            ],
        )
    if observable_family_id == "route_erasure_recovery_observable_family":
        _require_benchmark(context, "route_erased_split_recombine", observable_family_id)
        return build_observable_family(
            observable_family_id,
            "mid",
            [
                make_branchwise_mixing_observable(
                    "erased_route_mix",
                    "mid",
                    {
                        "C0": {"erased_signal": "1/2", "erased_silence": "1/2"},
                    },
                ),
                make_history_sensitive_observable(
                    "eraser_screen_history",
                    "mid",
                    {
                        "h_mid_0": {"screen_bright": 1, "screen_dark": 0},
                        "h_mid_1": {"screen_bright": 0, "screen_dark": 1},
                    },
                ),
            ],
        )
    raise ValueError(f"unknown observable_family_id {observable_family_id}")


def resolve_route_readability_scenario(
    scenario_id: str,
) -> dict[str, EventDistribution]:
    if scenario_id == "perfect_binary_route_recovery":
        return {
            "route_a": build_event_distribution({"blue": 0, "red": 1}),
            "route_b": build_event_distribution({"blue": 1, "red": 0}),
        }
    if scenario_id == "route_marker_readability":
        return {
            "route_left": build_event_distribution({"marker_left": 1, "marker_right": 0}),
            "route_right": build_event_distribution({"marker_left": 0, "marker_right": 1}),
        }
    if scenario_id == "relative_cycle_anchor_readability":
        erased_distribution = build_event_distribution(
            {"erased_signal": "1/2", "erased_silence": "1/2"}
        )
        return {
            "route_left": erased_distribution,
            "route_right": erased_distribution,
        }
    if scenario_id == "route_erasure_readability":
        erased_distribution = build_event_distribution(
            {"erased_signal": "1/2", "erased_silence": "1/2"}
        )
        return {
            "route_left": erased_distribution,
            "route_right": erased_distribution,
        }
    if scenario_id == "unreadable_binary_route_recovery":
        return {
            "route_a": build_event_distribution({"blue": "1/2", "red": "1/2"}),
            "route_b": build_event_distribution({"blue": "1/2", "red": "1/2"}),
        }
    raise ValueError(f"unknown route_readability_scenario_id {scenario_id}")


def resolve_visibility_scenario(
    scenario_id: str,
) -> tuple[EventDistribution, Mapping[str, EventDistribution]]:
    if scenario_id == "binary_visibility_recovery":
        return (
            build_event_distribution({"blue": "1/2", "red": "1/2"}),
            {
                "route_a": build_event_distribution({"blue": 0, "red": 1}),
                "route_b": build_event_distribution({"blue": 1, "red": 0}),
            },
        )
    if scenario_id == "route_marker_screen_visibility":
        screen_uniform = build_event_distribution(
            {"screen_bright": "1/2", "screen_dark": "1/2"}
        )
        return (
            screen_uniform,
            {
                "route_left": screen_uniform,
                "route_right": screen_uniform,
            },
        )
    if scenario_id == "relative_cycle_anchor_screen_visibility":
        return build_relative_cycle_visibility_scenario(default_anchor_parameters())
    if scenario_id == "route_eraser_screen_visibility":
        return (
            build_event_distribution({"screen_bright": "1/2", "screen_dark": "1/2"}),
            {
                "route_left": build_event_distribution({"screen_bright": 1, "screen_dark": 0}),
                "route_right": build_event_distribution({"screen_bright": 0, "screen_dark": 1}),
            },
        )
    raise ValueError(f"unknown visibility_scenario_id {scenario_id}")


def validate_search_space_id(search_space_id: str) -> None:
    if search_space_id not in SEARCH_SPACE_IDS:
        raise ValueError(f"unknown search_space_id {search_space_id}")


def _flat_family(context: InheritedBenchmarkContext) -> dict[str, BranchAssemblage]:
    return {
        "flat_left": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_0", 1, branch_label="left")],
        ),
        "flat_right": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_1", 1, branch_label="right")],
        ),
        "flat_split": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/3", branch_label="a"),
                make_branch_member("h_mid_1", "2/3", branch_label="b"),
            ],
        ),
    }


def _latent_family(context: InheritedBenchmarkContext) -> dict[str, BranchAssemblage]:
    return {
        "latent_left": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_0", 1, branch_label="left")],
        ),
        "latent_right": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_1", 1, branch_label="right")],
        ),
        "latent_balanced": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/2", branch_label="left"),
                make_branch_member("h_mid_1", "1/2", branch_label="right"),
            ],
        ),
        "latent_balanced_split": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/4", branch_label="left-a"),
                make_branch_member("h_mid_0", "1/4", branch_label="left-b"),
                make_branch_member("h_mid_1", "1/2", branch_label="right"),
            ],
        ),
    }


def _protocol_trap_family(context: InheritedBenchmarkContext) -> dict[str, BranchAssemblage]:
    return {
        "protocol_left": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_0", 1, branch_label="scheduler-left")],
        ),
        "protocol_right": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_1", 1, branch_label="scheduler-right")],
        ),
        "protocol_split": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/3", branch_label="scheduler-a"),
                make_branch_member("h_mid_1", "2/3", branch_label="scheduler-b"),
            ],
        ),
    }


def _protocol_erasure_recovery_family(
    context: InheritedBenchmarkContext,
) -> dict[str, BranchAssemblage]:
    return {
        "protocol_erased_left": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_0", 1, branch_label="protocol-left")],
        ),
        "protocol_erased_right": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_1", 1, branch_label="protocol-right")],
        ),
        "protocol_erased_balanced": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/2", branch_label="protocol-left"),
                make_branch_member("h_mid_1", "1/2", branch_label="protocol-right"),
            ],
        ),
        "protocol_erased_balanced_split": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/4", branch_label="protocol-left-a"),
                make_branch_member("h_mid_0", "1/4", branch_label="protocol-left-b"),
                make_branch_member("h_mid_1", "1/2", branch_label="protocol-right"),
            ],
        ),
    }


def _relative_cycle_anchor_family(
    context: InheritedBenchmarkContext,
) -> dict[str, BranchAssemblage]:
    return build_relative_cycle_case(default_anchor_parameters(), context=context).assemblages


def _route_marked_family(context: InheritedBenchmarkContext) -> dict[str, BranchAssemblage]:
    return {
        "marked_left": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_0", 1, branch_label="route-left")],
        ),
        "marked_right": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_1", 1, branch_label="route-right")],
        ),
        "marked_balanced": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/2", branch_label="route-left"),
                make_branch_member("h_mid_1", "1/2", branch_label="route-right"),
            ],
        ),
        "marked_balanced_split": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/4", branch_label="route-left-a"),
                make_branch_member("h_mid_0", "1/4", branch_label="route-left-b"),
                make_branch_member("h_mid_1", "1/2", branch_label="route-right"),
            ],
        ),
    }


def _route_erasure_family(context: InheritedBenchmarkContext) -> dict[str, BranchAssemblage]:
    return {
        "erased_left": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_0", 1, branch_label="route-left")],
        ),
        "erased_right": build_branch_assemblage(
            context,
            "mid",
            [make_branch_member("h_mid_1", 1, branch_label="route-right")],
        ),
        "erased_balanced": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/2", branch_label="route-left"),
                make_branch_member("h_mid_1", "1/2", branch_label="route-right"),
            ],
        ),
        "erased_balanced_split": build_branch_assemblage(
            context,
            "mid",
            [
                make_branch_member("h_mid_0", "1/4", branch_label="route-left-a"),
                make_branch_member("h_mid_0", "1/4", branch_label="route-left-b"),
                make_branch_member("h_mid_1", "1/2", branch_label="route-right"),
            ],
        ),
    }


def _require_benchmark(
    context: InheritedBenchmarkContext,
    expected_benchmark_id: str,
    object_id: str,
) -> None:
    if context.benchmark_id != expected_benchmark_id:
        raise ValueError(
            f"{object_id} requires benchmark {expected_benchmark_id}, got {context.benchmark_id}"
        )


__all__ = [
    "ASSEMBLAGE_FAMILY_IDS",
    "OBSERVABLE_FAMILY_IDS",
    "ROUTE_READABILITY_SCENARIO_IDS",
    "SEARCH_SPACE_IDS",
    "VISIBILITY_SCENARIO_IDS",
    "resolve_assemblage_family",
    "resolve_observable_family",
    "resolve_route_readability_scenario",
    "resolve_visibility_scenario",
    "validate_search_space_id",
]
