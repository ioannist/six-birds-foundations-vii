from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Callable, Iterable, Mapping

from .assemblages import BranchAssemblage, WeightInput
from .branchwise import compute_branchwise_summary
from .predictive import analyze_inherited_interface
from .substrate import InheritedBenchmarkContext


class ObservableKind(str, Enum):
    BRANCHWISE_MIXING = "branchwise_mixing"
    HISTORY_SENSITIVE = "history_sensitive"


@dataclass(frozen=True)
class EventDistribution:
    event_ids: tuple[str, ...]
    probabilities: tuple[Fraction, ...]

    def as_mapping(self) -> dict[str, Fraction]:
        return dict(zip(self.event_ids, self.probabilities, strict=True))


@dataclass(frozen=True)
class RecombinationObservable:
    observable_id: str
    interface_id: str
    event_ids: tuple[str, ...]
    kind: ObservableKind
    is_certified_branchwise_mixing: bool
    _evaluator: Callable[[InheritedBenchmarkContext, BranchAssemblage], EventDistribution]

    def evaluate(
        self,
        context: InheritedBenchmarkContext,
        assemblage: BranchAssemblage,
    ) -> EventDistribution:
        _validate_observable_context_alignment(context, assemblage, self.interface_id)
        distribution = self._evaluator(context, assemblage)
        if distribution.event_ids != self.event_ids:
            raise ValueError(
                f"observable {self.observable_id} produced unexpected event ordering"
            )
        return validate_event_distribution(distribution)


@dataclass(frozen=True)
class RecombinationObservableFamily:
    family_id: str
    interface_id: str
    observables: tuple[RecombinationObservable, ...]

    @property
    def includes_certified_branchwise_mixing(self) -> bool:
        return any(
            observable.is_certified_branchwise_mixing for observable in self.observables
        )


def build_event_distribution(
    probabilities_by_event_id: Mapping[str, WeightInput],
) -> EventDistribution:
    if not probabilities_by_event_id:
        raise ValueError("event distributions must contain at least one event")
    event_ids = tuple(sorted(probabilities_by_event_id))
    probabilities = tuple(
        _coerce_event_probability(probabilities_by_event_id[event_id]) for event_id in event_ids
    )
    distribution = EventDistribution(event_ids=event_ids, probabilities=probabilities)
    return validate_event_distribution(distribution)


def validate_event_distribution(distribution: EventDistribution) -> EventDistribution:
    if not distribution.event_ids:
        raise ValueError("event distributions must contain at least one event")
    if len(distribution.event_ids) != len(set(distribution.event_ids)):
        raise ValueError("event distributions must not repeat event ids")
    if len(distribution.event_ids) != len(distribution.probabilities):
        raise ValueError("event ids and probabilities must have the same length")
    if tuple(sorted(distribution.event_ids)) != distribution.event_ids:
        raise ValueError("event ids must be stored in deterministic sorted order")
    for probability in distribution.probabilities:
        if probability < 0:
            raise ValueError("event probabilities must be nonnegative")
    if sum(distribution.probabilities, start=Fraction(0, 1)) != Fraction(1, 1):
        raise ValueError("event probabilities must sum exactly to 1")
    return distribution


def make_branchwise_mixing_observable(
    observable_id: str,
    interface_id: str,
    emissions_by_predictive_class_id: Mapping[str, Mapping[str, WeightInput]],
) -> RecombinationObservable:
    canonical_emissions = _canonical_emission_distributions(
        emissions_by_predictive_class_id,
        identity_label="predictive class",
    )
    event_ids = next(iter(canonical_emissions.values())).event_ids

    def _evaluate(
        context: InheritedBenchmarkContext,
        assemblage: BranchAssemblage,
    ) -> EventDistribution:
        analysis = analyze_inherited_interface(context, interface_id)
        summary = compute_branchwise_summary(context, assemblage, analysis=analysis)
        probabilities_by_event_id = {event_id: Fraction(0, 1) for event_id in event_ids}
        total_weight = assemblage.total_weight
        for entry in summary.entries:
            emission = canonical_emissions.get(entry.predictive_class_id)
            if emission is None:
                raise ValueError(
                    "missing predictive-class emission distribution for "
                    f"{entry.predictive_class_id}"
                )
            class_weight = entry.total_weight / total_weight
            for event_id, probability in zip(
                emission.event_ids,
                emission.probabilities,
                strict=True,
            ):
                probabilities_by_event_id[event_id] += class_weight * probability
        return build_event_distribution(probabilities_by_event_id)

    return RecombinationObservable(
        observable_id=observable_id,
        interface_id=interface_id,
        event_ids=event_ids,
        kind=ObservableKind.BRANCHWISE_MIXING,
        is_certified_branchwise_mixing=True,
        _evaluator=_evaluate,
    )


def make_history_sensitive_observable(
    observable_id: str,
    interface_id: str,
    emissions_by_history_id: Mapping[str, Mapping[str, WeightInput]],
) -> RecombinationObservable:
    canonical_emissions = _canonical_emission_distributions(
        emissions_by_history_id,
        identity_label="history",
    )
    event_ids = next(iter(canonical_emissions.values())).event_ids

    def _evaluate(
        context: InheritedBenchmarkContext,
        assemblage: BranchAssemblage,
    ) -> EventDistribution:
        probabilities_by_event_id = {event_id: Fraction(0, 1) for event_id in event_ids}
        total_weight = assemblage.total_weight
        for member in assemblage.members:
            emission = canonical_emissions.get(member.history_id)
            if emission is None:
                raise ValueError(
                    f"missing history-sensitive emission distribution for {member.history_id}"
                )
            member_weight = member.weight / total_weight
            for event_id, probability in zip(
                emission.event_ids,
                emission.probabilities,
                strict=True,
            ):
                probabilities_by_event_id[event_id] += member_weight * probability
        return build_event_distribution(probabilities_by_event_id)

    return RecombinationObservable(
        observable_id=observable_id,
        interface_id=interface_id,
        event_ids=event_ids,
        kind=ObservableKind.HISTORY_SENSITIVE,
        is_certified_branchwise_mixing=False,
        _evaluator=_evaluate,
    )


def build_observable_family(
    family_id: str,
    interface_id: str,
    observables: Iterable[RecombinationObservable],
) -> RecombinationObservableFamily:
    ordered = tuple(observables)
    if not ordered:
        raise ValueError("observable families must contain at least one observable")
    seen_ids: set[str] = set()
    for observable in ordered:
        if observable.observable_id in seen_ids:
            raise ValueError(f"duplicate observable id {observable.observable_id}")
        seen_ids.add(observable.observable_id)
        if observable.interface_id != interface_id:
            raise ValueError(
                f"observable {observable.observable_id} targets interface "
                f"{observable.interface_id}, expected {interface_id}"
            )
    return RecombinationObservableFamily(
        family_id=family_id,
        interface_id=interface_id,
        observables=ordered,
    )


def event_distribution_payload(distribution: EventDistribution) -> dict[str, object]:
    return {
        "event_ids": list(distribution.event_ids),
        "probabilities": {
            event_id: str(probability)
            for event_id, probability in zip(
                distribution.event_ids,
                distribution.probabilities,
                strict=True,
            )
        },
    }


def observable_family_payload(
    family: RecombinationObservableFamily,
) -> dict[str, object]:
    return {
        "family_id": family.family_id,
        "interface_id": family.interface_id,
        "includes_certified_branchwise_mixing": family.includes_certified_branchwise_mixing,
        "observables": [
            {
                "observable_id": observable.observable_id,
                "kind": observable.kind.value,
                "event_ids": list(observable.event_ids),
                "is_certified_branchwise_mixing": observable.is_certified_branchwise_mixing,
            }
            for observable in family.observables
        ],
    }


def _coerce_event_probability(value: WeightInput) -> Fraction:
    if isinstance(value, Fraction):
        probability = value
    elif isinstance(value, bool):
        raise TypeError("boolean event probabilities are not supported")
    elif isinstance(value, int):
        probability = Fraction(value, 1)
    elif isinstance(value, str):
        try:
            probability = Fraction(value.strip())
        except ValueError as exc:
            raise ValueError(f"invalid event probability string: {value!r}") from exc
    elif isinstance(value, float):
        raise TypeError("binary float event probabilities are not supported")
    else:
        raise TypeError(f"unsupported event probability type: {type(value).__name__}")
    if probability < 0:
        raise ValueError("event probabilities must be nonnegative")
    return probability


def _canonical_emission_distributions(
    emissions: Mapping[str, Mapping[str, WeightInput]],
    *,
    identity_label: str,
) -> dict[str, EventDistribution]:
    if not emissions:
        raise ValueError(f"{identity_label} emissions must contain at least one entry")
    canonical = {
        key: build_event_distribution(distribution)
        for key, distribution in emissions.items()
    }
    expected_event_ids = next(iter(canonical.values())).event_ids
    for key, distribution in canonical.items():
        if distribution.event_ids != expected_event_ids:
            raise ValueError(
                f"{identity_label} {key} uses event ids {distribution.event_ids}, "
                f"expected {expected_event_ids}"
            )
    return canonical


def _validate_observable_context_alignment(
    context: InheritedBenchmarkContext,
    assemblage: BranchAssemblage,
    interface_id: str,
) -> None:
    if assemblage.benchmark_id != context.benchmark_id:
        raise ValueError(
            f"assemblage benchmark {assemblage.benchmark_id} does not match context "
            f"{context.benchmark_id}"
        )
    if assemblage.interface_id != interface_id:
        raise ValueError(
            f"assemblage interface {assemblage.interface_id} does not match observable "
            f"interface {interface_id}"
        )


__all__ = [
    "EventDistribution",
    "ObservableKind",
    "RecombinationObservable",
    "RecombinationObservableFamily",
    "build_event_distribution",
    "build_observable_family",
    "event_distribution_payload",
    "make_branchwise_mixing_observable",
    "make_history_sensitive_observable",
    "observable_family_payload",
    "validate_event_distribution",
]
