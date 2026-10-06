from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Mapping, Sequence

from .assemblages import BranchAssemblage, build_branch_assemblage, make_branch_member
from .observables import (
    EventDistribution,
    RecombinationObservableFamily,
    build_event_distribution,
    build_observable_family,
    make_branchwise_mixing_observable,
    make_history_sensitive_observable,
)
from .substrate import InheritedBenchmarkContext, load_inherited_benchmark_context


DEFAULT_CARRIER_SIZES = (2, 3, 4, 5)
DEFAULT_ROUTE_SHIFT_DELTAS = (1, 2)
DEFAULT_WEIGHT_PAIRS = ((Fraction(1, 2), Fraction(1, 2)), (Fraction(1, 3), Fraction(2, 3)))
DEFAULT_DISSIPATIVE_NOISE_STRENGTHS = (
    Fraction(0, 1),
    Fraction(1, 6),
    Fraction(1, 3),
    Fraction(1, 2),
    Fraction(2, 3),
    Fraction(5, 6),
    Fraction(1, 1),
)
RELATIVE_CYCLE_BENCHMARK_ID = "relative_cycle_carrier_base"
RELATIVE_CYCLE_INTERFACE_ID = "mid"
RELATIVE_CYCLE_ANCHOR_CARRIER_SIZE = 5
RELATIVE_CYCLE_ANCHOR_ROUTE_SHIFT_DELTA = 1
RELATIVE_CYCLE_ANCHOR_WEIGHT_LEFT = Fraction(1, 3)
RELATIVE_CYCLE_ANCHOR_WEIGHT_RIGHT = Fraction(2, 3)


@dataclass(frozen=True)
class RelativeCycleParameters:
    carrier_size: int
    route_shift_left: int
    route_shift_right: int
    route_shift_delta: int
    weight_left: Fraction
    weight_right: Fraction

    @property
    def case_id(self) -> str:
        return (
            f"n{self.carrier_size}_d{self.route_shift_delta}_"
            f"w{_fraction_case_token(self.weight_left)}_{_fraction_case_token(self.weight_right)}"
        )


@dataclass(frozen=True)
class RelativeCycleCase:
    parameters: RelativeCycleParameters
    benchmark_id: str
    interface_id: str
    assemblages: Mapping[str, BranchAssemblage]
    observable_family: RecombinationObservableFamily
    route_readability_scenario: Mapping[str, EventDistribution]
    unconditional_visibility_distribution: EventDistribution
    conditional_visibility_distributions: Mapping[str, EventDistribution]


def normalize_relative_cycle_parameters(
    *,
    carrier_size: int,
    route_shift_delta: int,
    weight_left: Fraction | int | str,
    weight_right: Fraction | int | str,
) -> RelativeCycleParameters:
    if carrier_size < 2:
        raise ValueError("carrier_size must be at least 2")
    delta = int(route_shift_delta) % carrier_size
    if delta == 0:
        raise ValueError("route_shift_delta must be nonzero modulo carrier_size")
    if delta >= carrier_size:
        raise ValueError("normalized route_shift_delta must be less than carrier_size")
    left = _coerce_fraction(weight_left)
    right = _coerce_fraction(weight_right)
    if left <= 0 or right <= 0:
        raise ValueError("relative-cycle weights must be strictly positive")
    if left + right != Fraction(1, 1):
        raise ValueError("relative-cycle weight pairs must sum exactly to 1")
    return RelativeCycleParameters(
        carrier_size=carrier_size,
        route_shift_left=0,
        route_shift_right=delta,
        route_shift_delta=delta,
        weight_left=left,
        weight_right=right,
    )


def enumerate_relative_cycle_parameters(
    *,
    carrier_sizes: Sequence[int] | None = None,
    route_shift_deltas: Sequence[int] | None = None,
    weight_pairs: Sequence[tuple[Fraction | int | str, Fraction | int | str]] | None = None,
) -> tuple[RelativeCycleParameters, ...]:
    sizes = tuple(carrier_sizes or DEFAULT_CARRIER_SIZES)
    deltas = tuple(route_shift_deltas or DEFAULT_ROUTE_SHIFT_DELTAS)
    pairs = tuple(weight_pairs or DEFAULT_WEIGHT_PAIRS)
    params: list[RelativeCycleParameters] = []
    for carrier_size in sizes:
        if carrier_size < 2:
            raise ValueError(f"invalid carrier_size {carrier_size}")
        for delta in deltas:
            if delta <= 0 or delta >= carrier_size:
                continue
            for weight_left, weight_right in pairs:
                params.append(
                    normalize_relative_cycle_parameters(
                        carrier_size=carrier_size,
                        route_shift_delta=delta,
                        weight_left=weight_left,
                        weight_right=weight_right,
                    )
                )
    return tuple(params)


def build_relative_cycle_case(
    parameters: RelativeCycleParameters,
    *,
    context: InheritedBenchmarkContext | None = None,
) -> RelativeCycleCase:
    resolved_context = context or load_relative_cycle_context()
    left_distribution, right_distribution, balanced_distribution = _carrier_distributions(
        parameters
    )
    assemblages = {
        f"{parameters.case_id}_left": _build_weighted_assemblage(
            resolved_context,
            left_distribution,
            prefix="left",
        ),
        f"{parameters.case_id}_right": _build_weighted_assemblage(
            resolved_context,
            right_distribution,
            prefix="right",
        ),
        f"{parameters.case_id}_balanced": _build_weighted_assemblage(
            resolved_context,
            balanced_distribution,
            prefix="balanced",
        ),
        f"{parameters.case_id}_balanced_split": _build_weighted_split_assemblage(
            resolved_context,
            balanced_distribution,
            prefix="balanced-split",
        ),
    }

    observable_family = build_observable_family(
        family_id=f"relative_cycle_family_{parameters.case_id}",
        interface_id=RELATIVE_CYCLE_INTERFACE_ID,
        observables=[
            make_branchwise_mixing_observable(
                "relative_cycle_erased_mix",
                RELATIVE_CYCLE_INTERFACE_ID,
                {
                    "C0": {"erased_signal": "1/2", "erased_silence": "1/2"},
                },
            ),
            _build_screen_history_observable(
                observable_id="relative_cycle_screen_history",
                carrier_size=parameters.carrier_size,
                noise_strength=Fraction(0, 1),
            ),
        ],
    )

    event_ids = tuple(_screen_event_id(index) for index in range(parameters.carrier_size))
    erased_uniform = build_event_distribution(
        {"erased_signal": "1/2", "erased_silence": "1/2"}
    )
    route_readability = {
        "route_left": erased_uniform,
        "route_right": erased_uniform,
    }
    unconditional_visibility = build_event_distribution(
        {event_id: Fraction(1, parameters.carrier_size) for event_id in event_ids}
    )
    conditional_visibility = {
        "route_left": build_event_distribution(
            {
                _screen_event_id(index): left_distribution.get(index, Fraction(0, 1))
                for index in range(parameters.carrier_size)
            }
        ),
        "route_right": build_event_distribution(
            {
                _screen_event_id(index): right_distribution.get(index, Fraction(0, 1))
                for index in range(parameters.carrier_size)
            }
        ),
    }
    return RelativeCycleCase(
        parameters=parameters,
        benchmark_id=resolved_context.benchmark_id,
        interface_id=RELATIVE_CYCLE_INTERFACE_ID,
        assemblages=assemblages,
        observable_family=observable_family,
        route_readability_scenario=route_readability,
        unconditional_visibility_distribution=unconditional_visibility,
        conditional_visibility_distributions=conditional_visibility,
    )


def build_dissipative_relative_cycle_case(
    parameters: RelativeCycleParameters,
    *,
    noise_strength: Fraction | int | str,
    context: InheritedBenchmarkContext | None = None,
) -> RelativeCycleCase:
    resolved_context = context or load_relative_cycle_context()
    noise = _coerce_fraction(noise_strength)
    if noise < 0 or noise > 1:
        raise ValueError("noise_strength must lie in the exact interval [0, 1]")
    left_distribution, right_distribution, balanced_distribution = _carrier_distributions(
        parameters
    )
    assemblages = {
        f"{parameters.case_id}_noise_{_fraction_case_token(noise)}_left": _build_weighted_assemblage(
            resolved_context,
            left_distribution,
            prefix="left",
        ),
        f"{parameters.case_id}_noise_{_fraction_case_token(noise)}_right": _build_weighted_assemblage(
            resolved_context,
            right_distribution,
            prefix="right",
        ),
        f"{parameters.case_id}_noise_{_fraction_case_token(noise)}_balanced": _build_weighted_assemblage(
            resolved_context,
            balanced_distribution,
            prefix="balanced",
        ),
        f"{parameters.case_id}_noise_{_fraction_case_token(noise)}_balanced_split": _build_weighted_split_assemblage(
            resolved_context,
            balanced_distribution,
            prefix="balanced-split",
        ),
    }
    observable_family = build_observable_family(
        family_id=f"relative_cycle_dissipative_family_{parameters.case_id}_{_fraction_case_token(noise)}",
        interface_id=RELATIVE_CYCLE_INTERFACE_ID,
        observables=[
            make_branchwise_mixing_observable(
                "relative_cycle_erased_mix",
                RELATIVE_CYCLE_INTERFACE_ID,
                {
                    "C0": {"erased_signal": "1/2", "erased_silence": "1/2"},
                },
            ),
            _build_screen_history_observable(
                observable_id="relative_cycle_screen_history_dissipative",
                carrier_size=parameters.carrier_size,
                noise_strength=noise,
            ),
        ],
    )
    erased_uniform = build_event_distribution(
        {"erased_signal": "1/2", "erased_silence": "1/2"}
    )
    route_readability = {
        "route_left": erased_uniform,
        "route_right": erased_uniform,
    }
    unconditional_visibility = build_event_distribution(
        {
            _screen_event_id(index): Fraction(1, parameters.carrier_size)
            for index in range(parameters.carrier_size)
        }
    )
    conditional_visibility = {
        "route_left": _mix_distribution_toward_uniform(left_distribution, parameters.carrier_size, noise),
        "route_right": _mix_distribution_toward_uniform(right_distribution, parameters.carrier_size, noise),
    }
    return RelativeCycleCase(
        parameters=parameters,
        benchmark_id=resolved_context.benchmark_id,
        interface_id=RELATIVE_CYCLE_INTERFACE_ID,
        assemblages=assemblages,
        observable_family=observable_family,
        route_readability_scenario=route_readability,
        unconditional_visibility_distribution=unconditional_visibility,
        conditional_visibility_distributions=conditional_visibility,
    )


def build_relative_cycle_completion_observable_family(
    parameters: RelativeCycleParameters,
) -> RecombinationObservableFamily:
    case = build_relative_cycle_case(parameters)
    return build_observable_family(
        family_id=f"relative_cycle_completion_family_{parameters.case_id}",
        interface_id=RELATIVE_CYCLE_INTERFACE_ID,
        observables=[
            *case.observable_family.observables,
            make_branchwise_mixing_observable(
                "relative_cycle_completion_bins",
                RELATIVE_CYCLE_INTERFACE_ID,
                {
                    "C0": {
                        "completion_low": "2/5",
                        "completion_high": "3/5",
                    }
                },
            ),
        ],
    )


def build_relative_cycle_visibility_scenario(
    parameters: RelativeCycleParameters,
    *,
    noise_strength: Fraction | int | str = Fraction(0, 1),
) -> tuple[EventDistribution, Mapping[str, EventDistribution]]:
    noise = _coerce_fraction(noise_strength)
    left_distribution, right_distribution, _ = _carrier_distributions(parameters)
    unconditional_visibility = build_event_distribution(
        {
            _screen_event_id(index): Fraction(1, parameters.carrier_size)
            for index in range(parameters.carrier_size)
        }
    )
    conditional_visibility = {
        "route_left": _mix_distribution_toward_uniform(
            left_distribution,
            parameters.carrier_size,
            noise,
        ),
        "route_right": _mix_distribution_toward_uniform(
            right_distribution,
            parameters.carrier_size,
            noise,
        ),
    }
    return unconditional_visibility, conditional_visibility


def default_anchor_parameters() -> RelativeCycleParameters:
    return normalize_relative_cycle_parameters(
        carrier_size=RELATIVE_CYCLE_ANCHOR_CARRIER_SIZE,
        route_shift_delta=RELATIVE_CYCLE_ANCHOR_ROUTE_SHIFT_DELTA,
        weight_left=RELATIVE_CYCLE_ANCHOR_WEIGHT_LEFT,
        weight_right=RELATIVE_CYCLE_ANCHOR_WEIGHT_RIGHT,
    )


def noise_strength_strings(
    noise_strengths: Sequence[Fraction | int | str] | None,
) -> tuple[str, ...]:
    strengths = tuple(noise_strengths or DEFAULT_DISSIPATIVE_NOISE_STRENGTHS)
    return tuple(str(_coerce_fraction(strength)) for strength in strengths)


@lru_cache(maxsize=1)
def load_relative_cycle_context() -> InheritedBenchmarkContext:
    return load_inherited_benchmark_context(RELATIVE_CYCLE_BENCHMARK_ID)


def weight_pair_strings(
    weight_pairs: Sequence[tuple[Fraction | int | str, Fraction | int | str]] | None,
) -> tuple[tuple[str, str], ...]:
    pairs = tuple(weight_pairs or DEFAULT_WEIGHT_PAIRS)
    return tuple((str(_coerce_fraction(left)), str(_coerce_fraction(right))) for left, right in pairs)


def _carrier_distributions(
    parameters: RelativeCycleParameters,
) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
    left_distribution = _route_phase_distribution(
        parameters.carrier_size,
        parameters.route_shift_left,
        parameters.weight_left,
        parameters.weight_right,
    )
    right_distribution = _route_phase_distribution(
        parameters.carrier_size,
        parameters.route_shift_right,
        parameters.weight_left,
        parameters.weight_right,
    )
    balanced_distribution = {
        index: (left_distribution[index] + right_distribution[index]) / Fraction(2, 1)
        for index in range(parameters.carrier_size)
    }
    return left_distribution, right_distribution, balanced_distribution


def _build_screen_history_observable(
    *,
    observable_id: str,
    carrier_size: int,
    noise_strength: Fraction,
) -> object:
    event_ids = tuple(_screen_event_id(index) for index in range(carrier_size))
    uniform_probability = Fraction(1, carrier_size)
    return make_history_sensitive_observable(
        observable_id,
        RELATIVE_CYCLE_INTERFACE_ID,
        {
            _history_id(index): {
                event_id: (
                    (Fraction(1, 1) - noise_strength)
                    * (Fraction(1, 1) if event_id == _screen_event_id(index) else Fraction(0, 1))
                    + noise_strength * uniform_probability
                )
                for event_id in event_ids
            }
            for index in range(carrier_size)
        },
    )


def _mix_distribution_toward_uniform(
    distribution: Mapping[int, Fraction],
    carrier_size: int,
    noise_strength: Fraction,
) -> EventDistribution:
    uniform_probability = Fraction(1, carrier_size)
    return build_event_distribution(
        {
            _screen_event_id(index): (
                (Fraction(1, 1) - noise_strength) * distribution.get(index, Fraction(0, 1))
                + noise_strength * uniform_probability
            )
            for index in range(carrier_size)
        }
    )


def _build_weighted_assemblage(
    context: InheritedBenchmarkContext,
    distribution: Mapping[int, Fraction],
    *,
    prefix: str,
) -> BranchAssemblage:
    return build_branch_assemblage(
        context,
        RELATIVE_CYCLE_INTERFACE_ID,
        [
            make_branch_member(
                _history_id(index),
                weight,
                branch_label=f"{prefix}-{index}",
            )
            for index, weight in sorted(distribution.items())
            if weight > 0
        ],
    )


def _build_weighted_split_assemblage(
    context: InheritedBenchmarkContext,
    distribution: Mapping[int, Fraction],
    *,
    prefix: str,
) -> BranchAssemblage:
    members = []
    split_done = False
    for index, weight in sorted(distribution.items()):
        if weight == 0:
            continue
        if not split_done:
            half = weight / Fraction(2, 1)
            members.append(
                make_branch_member(_history_id(index), half, branch_label=f"{prefix}-{index}-a")
            )
            members.append(
                make_branch_member(_history_id(index), half, branch_label=f"{prefix}-{index}-b")
            )
            split_done = True
        else:
            members.append(
                make_branch_member(_history_id(index), weight, branch_label=f"{prefix}-{index}")
            )
    return build_branch_assemblage(context, RELATIVE_CYCLE_INTERFACE_ID, members)


def _route_phase_distribution(
    carrier_size: int,
    shift: int,
    weight_left: Fraction,
    weight_right: Fraction,
) -> dict[int, Fraction]:
    distribution = {index: Fraction(0, 1) for index in range(carrier_size)}
    distribution[shift % carrier_size] += weight_left
    distribution[(shift + 1) % carrier_size] += weight_right
    return distribution


def _coerce_fraction(value: Fraction | int | str) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    return Fraction(value)


def _fraction_case_token(value: Fraction) -> str:
    return f"{value.numerator}of{value.denominator}"


def _history_id(index: int) -> str:
    return f"h_mid_{index}"


def _screen_event_id(index: int) -> str:
    return f"screen_{index}"


__all__ = [
    "DEFAULT_CARRIER_SIZES",
    "DEFAULT_DISSIPATIVE_NOISE_STRENGTHS",
    "DEFAULT_ROUTE_SHIFT_DELTAS",
    "DEFAULT_WEIGHT_PAIRS",
    "RELATIVE_CYCLE_BENCHMARK_ID",
    "RELATIVE_CYCLE_ANCHOR_CARRIER_SIZE",
    "RELATIVE_CYCLE_ANCHOR_ROUTE_SHIFT_DELTA",
    "RELATIVE_CYCLE_ANCHOR_WEIGHT_LEFT",
    "RELATIVE_CYCLE_ANCHOR_WEIGHT_RIGHT",
    "RELATIVE_CYCLE_INTERFACE_ID",
    "RelativeCycleCase",
    "RelativeCycleParameters",
    "build_dissipative_relative_cycle_case",
    "build_relative_cycle_completion_observable_family",
    "build_relative_cycle_case",
    "build_relative_cycle_visibility_scenario",
    "default_anchor_parameters",
    "enumerate_relative_cycle_parameters",
    "load_relative_cycle_context",
    "noise_strength_strings",
    "normalize_relative_cycle_parameters",
    "weight_pair_strings",
]
