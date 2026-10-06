from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Iterable, Mapping

from .assemblages import BranchAssemblage
from .branchwise import BranchwiseQuotientResult, compute_branchwise_quotient
from .observables import (
    EventDistribution,
    RecombinationObservableFamily,
    event_distribution_payload,
)
from .substrate import InheritedBenchmarkContext


@dataclass(frozen=True)
class RecombinationSignature:
    family_id: str
    interface_id: str
    observable_ids: tuple[str, ...]
    distributions: tuple[EventDistribution, ...]


@dataclass(frozen=True)
class EtaMapSummary:
    r_class_to_k_class: Mapping[str, str]
    fiber_sizes_by_k_class: Mapping[str, int]
    eta_max_fiber_size: int
    eta_is_surjective: bool


@dataclass(frozen=True)
class RecombinationQuotientClass:
    class_id: str
    assemblage_ids: tuple[str, ...]
    signature: RecombinationSignature


@dataclass(frozen=True)
class RecombinationQuotientResult:
    benchmark_id: str
    interface_id: str
    observable_family: RecombinationObservableFamily
    includes_certified_branchwise_mixing: bool
    branchwise_quotient: BranchwiseQuotientResult
    signatures_by_assemblage_id: Mapping[str, RecombinationSignature]
    assemblage_to_r_class_id: Mapping[str, str]
    classes: tuple[RecombinationQuotientClass, ...]
    eta: EtaMapSummary

    @property
    def class_count(self) -> int:
        return len(self.classes)


def compute_recombination_signature(
    context: InheritedBenchmarkContext,
    assemblage: BranchAssemblage,
    observable_family: RecombinationObservableFamily,
) -> RecombinationSignature:
    if assemblage.interface_id != observable_family.interface_id:
        raise ValueError(
            f"assemblage interface {assemblage.interface_id} does not match observable family "
            f"interface {observable_family.interface_id}"
        )
    distributions = tuple(
        observable.evaluate(context, assemblage)
        for observable in observable_family.observables
    )
    return RecombinationSignature(
        family_id=observable_family.family_id,
        interface_id=observable_family.interface_id,
        observable_ids=tuple(
            observable.observable_id for observable in observable_family.observables
        ),
        distributions=distributions,
    )


def compute_recombination_quotient(
    context: InheritedBenchmarkContext,
    interface_id: str,
    assemblages: Mapping[str, BranchAssemblage] | Iterable[tuple[str, BranchAssemblage]],
    observable_family: RecombinationObservableFamily,
) -> RecombinationQuotientResult:
    if observable_family.interface_id != interface_id:
        raise ValueError(
            f"observable family interface {observable_family.interface_id} does not match "
            f"requested interface {interface_id}"
        )
    ordered_items = _ordered_assemblage_items(assemblages)
    if not ordered_items:
        raise ValueError("recombination quotient requires at least one assemblage")

    branchwise_quotient = compute_branchwise_quotient(context, interface_id, ordered_items)

    signatures_by_assemblage_id: dict[str, RecombinationSignature] = {}
    class_members_by_key: dict[
        tuple[tuple[str, tuple[tuple[str, Fraction], ...]], ...],
        list[str],
    ] = {}
    ordered_keys: list[tuple[tuple[str, tuple[tuple[str, Fraction], ...]], ...]] = []

    for assemblage_id, assemblage in ordered_items:
        signature = compute_recombination_signature(context, assemblage, observable_family)
        signatures_by_assemblage_id[assemblage_id] = signature
        signature_key = tuple(
            (
                observable_id,
                tuple(
                    zip(
                        distribution.event_ids,
                        distribution.probabilities,
                        strict=True,
                    )
                ),
            )
            for observable_id, distribution in zip(
                signature.observable_ids,
                signature.distributions,
                strict=True,
            )
        )
        if signature_key not in class_members_by_key:
            class_members_by_key[signature_key] = []
            ordered_keys.append(signature_key)
        class_members_by_key[signature_key].append(assemblage_id)

    assemblage_to_r_class_id: dict[str, str] = {}
    classes: list[RecombinationQuotientClass] = []
    r_class_to_k_class: dict[str, str] = {}
    fiber_sizes_by_k_class: dict[str, int] = {}

    for index, signature_key in enumerate(ordered_keys):
        class_id = f"R{index}"
        assemblage_ids = tuple(class_members_by_key[signature_key])
        for assemblage_id in assemblage_ids:
            assemblage_to_r_class_id[assemblage_id] = class_id
        classes.append(
            RecombinationQuotientClass(
                class_id=class_id,
                assemblage_ids=assemblage_ids,
                signature=signatures_by_assemblage_id[assemblage_ids[0]],
            )
        )
        k_class_ids = {
            branchwise_quotient.assemblage_to_class_id[assemblage_id]
            for assemblage_id in assemblage_ids
        }
        if len(k_class_ids) != 1:
            raise ValueError(
                "recombination quotient does not refine the branchwise quotient; eta is undefined"
            )
        k_class_id = next(iter(k_class_ids))
        r_class_to_k_class[class_id] = k_class_id
        fiber_sizes_by_k_class[k_class_id] = fiber_sizes_by_k_class.get(k_class_id, 0) + 1

    eta = EtaMapSummary(
        r_class_to_k_class=MappingProxyType(r_class_to_k_class),
        fiber_sizes_by_k_class=MappingProxyType(fiber_sizes_by_k_class),
        eta_max_fiber_size=max(fiber_sizes_by_k_class.values(), default=0),
        eta_is_surjective=set(fiber_sizes_by_k_class) == set(
            branchwise_quotient.assemblage_to_class_id.values()
        ),
    )

    return RecombinationQuotientResult(
        benchmark_id=context.benchmark_id,
        interface_id=interface_id,
        observable_family=observable_family,
        includes_certified_branchwise_mixing=(
            observable_family.includes_certified_branchwise_mixing
        ),
        branchwise_quotient=branchwise_quotient,
        signatures_by_assemblage_id=MappingProxyType(signatures_by_assemblage_id),
        assemblage_to_r_class_id=MappingProxyType(assemblage_to_r_class_id),
        classes=tuple(classes),
        eta=eta,
    )


def recombination_signature_payload(
    signature: RecombinationSignature,
) -> dict[str, object]:
    return {
        "family_id": signature.family_id,
        "interface_id": signature.interface_id,
        "observable_ids": list(signature.observable_ids),
        "distributions": [
            event_distribution_payload(distribution)
            for distribution in signature.distributions
        ],
    }


def eta_map_payload(eta: EtaMapSummary) -> dict[str, object]:
    return {
        "r_class_to_k_class": dict(eta.r_class_to_k_class),
        "fiber_sizes_by_k_class": dict(eta.fiber_sizes_by_k_class),
        "eta_max_fiber_size": eta.eta_max_fiber_size,
        "eta_is_surjective": eta.eta_is_surjective,
    }


def recombination_quotient_payload(
    quotient: RecombinationQuotientResult,
) -> dict[str, object]:
    return {
        "benchmark_id": quotient.benchmark_id,
        "interface_id": quotient.interface_id,
        "observable_family_id": quotient.observable_family.family_id,
        "includes_certified_branchwise_mixing": (
            quotient.includes_certified_branchwise_mixing
        ),
        "k_class_count": quotient.branchwise_quotient.class_count,
        "r_class_count": quotient.class_count,
        "assemblage_to_k_class_id": dict(quotient.branchwise_quotient.assemblage_to_class_id),
        "assemblage_to_r_class_id": dict(quotient.assemblage_to_r_class_id),
        "eta": eta_map_payload(quotient.eta),
        "class_signatures": {
            recombination_class.class_id: recombination_signature_payload(
                recombination_class.signature
            )
            for recombination_class in quotient.classes
        },
    }


def _ordered_assemblage_items(
    assemblages: Mapping[str, BranchAssemblage] | Iterable[tuple[str, BranchAssemblage]],
) -> tuple[tuple[str, BranchAssemblage], ...]:
    if isinstance(assemblages, Mapping):
        return tuple(assemblages.items())
    return tuple(assemblages)


__all__ = [
    "EtaMapSummary",
    "RecombinationQuotientClass",
    "RecombinationQuotientResult",
    "RecombinationSignature",
    "compute_recombination_quotient",
    "compute_recombination_signature",
    "eta_map_payload",
    "recombination_quotient_payload",
    "recombination_signature_payload",
]
