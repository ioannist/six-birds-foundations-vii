from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Mapping

from .observables import EventDistribution
from .recombination import RecombinationQuotientResult


@dataclass(frozen=True)
class RecombinationGapDiagnostic:
    metric_name: str
    metric_value: Fraction
    witness_k_class_id: str | None
    witness_assemblage_id_left: str | None
    witness_assemblage_id_right: str | None
    witness_observable_id: str | None
    witness_event_id: str | None
    evaluated_pair_count: int


@dataclass(frozen=True)
class EtaFiberDiagnostic:
    eta_max_fiber_size: int
    fiber_sizes_by_k_class: Mapping[str, int]
    r_class_to_k_class: Mapping[str, str]
    eta_is_surjective: bool
    k_class_count: int
    r_class_count: int


@dataclass(frozen=True)
class RouteReadabilityDiagnostic:
    score_name: str
    score_value: Fraction
    raw_success_probability: Fraction
    route_count: int
    event_ids: tuple[str, ...]
    route_ids: tuple[str, ...]


@dataclass(frozen=True)
class ConditionalVisibilityDiagnostic:
    metric_name: str
    unconditional_visibility: Fraction
    conditional_visibility_by_condition: Mapping[str, Fraction]
    max_conditional_visibility: Fraction
    visibility_recovery_gap: Fraction
    condition_ids: tuple[str, ...]
    event_ids: tuple[str, ...]


def compute_recombination_gap(
    quotient: RecombinationQuotientResult,
) -> RecombinationGapDiagnostic:
    max_gap = Fraction(0, 1)
    witness_k_class_id: str | None = None
    witness_left: str | None = None
    witness_right: str | None = None
    witness_observable_id: str | None = None
    witness_event_id: str | None = None
    evaluated_pair_count = 0

    for branchwise_class in quotient.branchwise_quotient.classes:
        for left_id, right_id in combinations(branchwise_class.assemblage_ids, 2):
            evaluated_pair_count += 1
            left_signature = quotient.signatures_by_assemblage_id[left_id]
            right_signature = quotient.signatures_by_assemblage_id[right_id]
            for observable_id, left_distribution, right_distribution in zip(
                left_signature.observable_ids,
                left_signature.distributions,
                right_signature.distributions,
                strict=True,
            ):
                for event_id, left_probability, right_probability in zip(
                    left_distribution.event_ids,
                    left_distribution.probabilities,
                    right_distribution.probabilities,
                    strict=True,
                ):
                    gap = abs(left_probability - right_probability)
                    if gap > max_gap:
                        max_gap = gap
                        witness_k_class_id = branchwise_class.class_id
                        witness_left = left_id
                        witness_right = right_id
                        witness_observable_id = observable_id
                        witness_event_id = event_id

    return RecombinationGapDiagnostic(
        metric_name="exact_recombination_gap",
        metric_value=max_gap,
        witness_k_class_id=witness_k_class_id,
        witness_assemblage_id_left=witness_left,
        witness_assemblage_id_right=witness_right,
        witness_observable_id=witness_observable_id,
        witness_event_id=witness_event_id,
        evaluated_pair_count=evaluated_pair_count,
    )


def extract_eta_fiber_diagnostics(
    quotient: RecombinationQuotientResult,
) -> EtaFiberDiagnostic:
    return EtaFiberDiagnostic(
        eta_max_fiber_size=quotient.eta.eta_max_fiber_size,
        fiber_sizes_by_k_class=quotient.eta.fiber_sizes_by_k_class,
        r_class_to_k_class=quotient.eta.r_class_to_k_class,
        eta_is_surjective=quotient.eta.eta_is_surjective,
        k_class_count=quotient.branchwise_quotient.class_count,
        r_class_count=quotient.class_count,
    )


def compute_route_readability(
    route_conditioned_distributions: Mapping[str, EventDistribution],
) -> RouteReadabilityDiagnostic:
    if not route_conditioned_distributions:
        raise ValueError("route readability requires at least one route distribution")
    route_ids = tuple(sorted(route_conditioned_distributions))
    distributions = {
        route_id: route_conditioned_distributions[route_id]
        for route_id in route_ids
    }
    event_ids = _require_shared_event_ids(distributions, identity_label="route")
    route_count = len(route_ids)
    raw_success_probability = sum(
        (
            max(distributions[route_id].as_mapping()[event_id] for route_id in route_ids)
            for event_id in event_ids
        ),
        start=Fraction(0, 1),
    ) / Fraction(route_count, 1)
    if route_count == 1:
        score_value = Fraction(1, 1)
    else:
        baseline = Fraction(1, route_count)
        score_value = (raw_success_probability - baseline) / (Fraction(1, 1) - baseline)
    return RouteReadabilityDiagnostic(
        score_name="bayes_optimal_route_recovery",
        score_value=score_value,
        raw_success_probability=raw_success_probability,
        route_count=route_count,
        event_ids=event_ids,
        route_ids=route_ids,
    )


def compute_conditional_visibility(
    unconditional_distribution: EventDistribution,
    conditional_distributions: Mapping[str, EventDistribution],
) -> ConditionalVisibilityDiagnostic:
    if not conditional_distributions:
        raise ValueError("conditional visibility requires at least one condition")
    event_ids = unconditional_distribution.event_ids
    conditional_by_condition: dict[str, Fraction] = {}
    for condition_id in sorted(conditional_distributions):
        distribution = conditional_distributions[condition_id]
        if distribution.event_ids != event_ids:
            raise ValueError(
                f"condition {condition_id} uses event ids {distribution.event_ids}, "
                f"expected {event_ids}"
            )
        conditional_by_condition[condition_id] = _total_variation_from_uniform(distribution)
    unconditional_visibility = _total_variation_from_uniform(unconditional_distribution)
    max_conditional_visibility = max(
        conditional_by_condition.values(),
        default=Fraction(0, 1),
    )
    return ConditionalVisibilityDiagnostic(
        metric_name="total_variation_from_uniform",
        unconditional_visibility=unconditional_visibility,
        conditional_visibility_by_condition=conditional_by_condition,
        max_conditional_visibility=max_conditional_visibility,
        visibility_recovery_gap=max_conditional_visibility - unconditional_visibility,
        condition_ids=tuple(sorted(conditional_distributions)),
        event_ids=event_ids,
    )


def recombination_gap_payload(
    diagnostic: RecombinationGapDiagnostic,
) -> dict[str, object]:
    return {
        "metric_name": diagnostic.metric_name,
        "metric_value": str(diagnostic.metric_value),
        "witness_k_class_id": diagnostic.witness_k_class_id,
        "witness_assemblage_id_left": diagnostic.witness_assemblage_id_left,
        "witness_assemblage_id_right": diagnostic.witness_assemblage_id_right,
        "witness_observable_id": diagnostic.witness_observable_id,
        "witness_event_id": diagnostic.witness_event_id,
        "evaluated_pair_count": diagnostic.evaluated_pair_count,
    }


def eta_fiber_payload(diagnostic: EtaFiberDiagnostic) -> dict[str, object]:
    return {
        "eta_max_fiber_size": diagnostic.eta_max_fiber_size,
        "fiber_sizes_by_k_class": dict(diagnostic.fiber_sizes_by_k_class),
        "r_class_to_k_class": dict(diagnostic.r_class_to_k_class),
        "eta_is_surjective": diagnostic.eta_is_surjective,
        "k_class_count": diagnostic.k_class_count,
        "r_class_count": diagnostic.r_class_count,
    }


def route_readability_payload(
    diagnostic: RouteReadabilityDiagnostic,
) -> dict[str, object]:
    return {
        "score_name": diagnostic.score_name,
        "score_value": str(diagnostic.score_value),
        "raw_success_probability": str(diagnostic.raw_success_probability),
        "route_count": diagnostic.route_count,
        "event_ids": list(diagnostic.event_ids),
        "route_ids": list(diagnostic.route_ids),
    }


def conditional_visibility_payload(
    diagnostic: ConditionalVisibilityDiagnostic,
) -> dict[str, object]:
    return {
        "metric_name": diagnostic.metric_name,
        "unconditional_visibility": str(diagnostic.unconditional_visibility),
        "conditional_visibility_by_condition": {
            condition_id: str(value)
            for condition_id, value in diagnostic.conditional_visibility_by_condition.items()
        },
        "max_conditional_visibility": str(diagnostic.max_conditional_visibility),
        "visibility_recovery_gap": str(diagnostic.visibility_recovery_gap),
        "condition_ids": list(diagnostic.condition_ids),
        "event_ids": list(diagnostic.event_ids),
    }


def _require_shared_event_ids(
    distributions: Mapping[str, EventDistribution],
    *,
    identity_label: str,
) -> tuple[str, ...]:
    event_ids = next(iter(distributions.values())).event_ids
    for identity, distribution in distributions.items():
        if distribution.event_ids != event_ids:
            raise ValueError(
                f"{identity_label} {identity} uses event ids {distribution.event_ids}, "
                f"expected {event_ids}"
            )
    return event_ids


def _total_variation_from_uniform(distribution: EventDistribution) -> Fraction:
    uniform_probability = Fraction(1, len(distribution.event_ids))
    return sum(
        (abs(probability - uniform_probability) for probability in distribution.probabilities),
        start=Fraction(0, 1),
    ) / Fraction(2, 1)


__all__ = [
    "ConditionalVisibilityDiagnostic",
    "EtaFiberDiagnostic",
    "RecombinationGapDiagnostic",
    "RouteReadabilityDiagnostic",
    "compute_conditional_visibility",
    "compute_recombination_gap",
    "compute_route_readability",
    "conditional_visibility_payload",
    "eta_fiber_payload",
    "extract_eta_fiber_diagnostics",
    "recombination_gap_payload",
    "route_readability_payload",
]
