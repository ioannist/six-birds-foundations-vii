from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from types import MappingProxyType
from typing import Iterable, Mapping

from .assemblages import BranchAssemblage
from .predictive import InheritedInterfaceAnalysis, analyze_inherited_interface
from .substrate import InheritedBenchmarkContext


@dataclass(frozen=True)
class BranchwiseSummaryEntry:
    predictive_class_id: str
    total_weight: Fraction


@dataclass(frozen=True)
class BranchwiseSummary:
    benchmark_id: str
    interface_id: str
    entries: tuple[BranchwiseSummaryEntry, ...]


@dataclass(frozen=True)
class BranchwiseQuotientClass:
    class_id: str
    assemblage_ids: tuple[str, ...]
    summary: BranchwiseSummary


@dataclass(frozen=True)
class BranchwiseQuotientResult:
    benchmark_id: str
    interface_id: str
    predictive_class_ids: tuple[str, ...]
    summaries_by_assemblage_id: Mapping[str, BranchwiseSummary]
    assemblage_to_class_id: Mapping[str, str]
    classes: tuple[BranchwiseQuotientClass, ...]

    @property
    def class_count(self) -> int:
        return len(self.classes)


def compute_branchwise_summary(
    context: InheritedBenchmarkContext,
    assemblage: BranchAssemblage,
    *,
    analysis: InheritedInterfaceAnalysis | None = None,
) -> BranchwiseSummary:
    _validate_context_alignment(context, assemblage)
    resolved_analysis = analysis or analyze_inherited_interface(
        context,
        assemblage.interface_id,
    )
    if resolved_analysis.interface_id != assemblage.interface_id:
        raise ValueError(
            "predictive analysis interface does not match assemblage interface"
        )

    weights_by_class_id = {
        equivalence_class.class_id: Fraction(0, 1)
        for equivalence_class in resolved_analysis.predictive_partition.classes
    }
    for member in assemblage.members:
        predictive_class_id = resolved_analysis.predictive_partition.history_to_class_id[
            member.history_id
        ]
        weights_by_class_id[predictive_class_id] += member.weight

    entries = tuple(
        BranchwiseSummaryEntry(
            predictive_class_id=equivalence_class.class_id,
            total_weight=weights_by_class_id[equivalence_class.class_id],
        )
        for equivalence_class in resolved_analysis.predictive_partition.classes
    )
    return BranchwiseSummary(
        benchmark_id=assemblage.benchmark_id,
        interface_id=assemblage.interface_id,
        entries=entries,
    )


def compute_branchwise_quotient(
    context: InheritedBenchmarkContext,
    interface_id: str,
    assemblages: Mapping[str, BranchAssemblage] | Iterable[tuple[str, BranchAssemblage]],
) -> BranchwiseQuotientResult:
    resolved_analysis = analyze_inherited_interface(context, interface_id)
    ordered_items = _ordered_assemblage_items(assemblages)
    if not ordered_items:
        raise ValueError("branchwise quotient requires at least one assemblage")

    summaries_by_assemblage_id: dict[str, BranchwiseSummary] = {}
    class_members_by_key: dict[
        tuple[tuple[str, Fraction], ...],
        list[str],
    ] = {}
    ordered_keys: list[tuple[tuple[str, Fraction], ...]] = []

    for assemblage_id, assemblage in ordered_items:
        if assemblage_id in summaries_by_assemblage_id:
            raise ValueError(f"duplicate assemblage id {assemblage_id}")
        if assemblage.interface_id != interface_id:
            raise ValueError(
                f"assemblage {assemblage_id} targets interface {assemblage.interface_id}, "
                f"expected {interface_id}"
            )
        summary = compute_branchwise_summary(
            context,
            assemblage,
            analysis=resolved_analysis,
        )
        summaries_by_assemblage_id[assemblage_id] = summary
        summary_key = tuple(
            (entry.predictive_class_id, entry.total_weight) for entry in summary.entries
        )
        if summary_key not in class_members_by_key:
            class_members_by_key[summary_key] = []
            ordered_keys.append(summary_key)
        class_members_by_key[summary_key].append(assemblage_id)

    assemblage_to_class_id: dict[str, str] = {}
    classes: list[BranchwiseQuotientClass] = []
    for index, summary_key in enumerate(ordered_keys):
        class_id = f"K{index}"
        assemblage_ids = tuple(class_members_by_key[summary_key])
        for assemblage_id in assemblage_ids:
            assemblage_to_class_id[assemblage_id] = class_id
        classes.append(
            BranchwiseQuotientClass(
                class_id=class_id,
                assemblage_ids=assemblage_ids,
                summary=summaries_by_assemblage_id[assemblage_ids[0]],
            )
        )

    return BranchwiseQuotientResult(
        benchmark_id=context.benchmark_id,
        interface_id=interface_id,
        predictive_class_ids=tuple(
            equivalence_class.class_id
            for equivalence_class in resolved_analysis.predictive_partition.classes
        ),
        summaries_by_assemblage_id=MappingProxyType(summaries_by_assemblage_id),
        assemblage_to_class_id=MappingProxyType(assemblage_to_class_id),
        classes=tuple(classes),
    )


def branchwise_summary_payload(summary: BranchwiseSummary) -> dict[str, object]:
    return {
        "benchmark_id": summary.benchmark_id,
        "interface_id": summary.interface_id,
        "entries": [
            {
                "predictive_class_id": entry.predictive_class_id,
                "total_weight": str(entry.total_weight),
            }
            for entry in summary.entries
        ],
    }


def branchwise_quotient_payload(result: BranchwiseQuotientResult) -> dict[str, object]:
    return {
        "benchmark_id": result.benchmark_id,
        "interface_id": result.interface_id,
        "predictive_class_ids": list(result.predictive_class_ids),
        "assemblage_to_class_id": dict(result.assemblage_to_class_id),
        "class_count": result.class_count,
        "class_summaries": {
            equivalence_class.class_id: branchwise_summary_payload(
                equivalence_class.summary
            )["entries"]
            for equivalence_class in result.classes
        },
    }


def _ordered_assemblage_items(
    assemblages: Mapping[str, BranchAssemblage] | Iterable[tuple[str, BranchAssemblage]],
) -> tuple[tuple[str, BranchAssemblage], ...]:
    if isinstance(assemblages, Mapping):
        return tuple(assemblages.items())
    return tuple(assemblages)


def _validate_context_alignment(
    context: InheritedBenchmarkContext,
    assemblage: BranchAssemblage,
) -> None:
    if assemblage.benchmark_id != context.benchmark_id:
        raise ValueError(
            f"assemblage benchmark {assemblage.benchmark_id} does not match context "
            f"{context.benchmark_id}"
        )


__all__ = [
    "BranchwiseQuotientClass",
    "BranchwiseQuotientResult",
    "BranchwiseSummary",
    "BranchwiseSummaryEntry",
    "branchwise_quotient_payload",
    "branchwise_summary_payload",
    "compute_branchwise_quotient",
    "compute_branchwise_summary",
]
