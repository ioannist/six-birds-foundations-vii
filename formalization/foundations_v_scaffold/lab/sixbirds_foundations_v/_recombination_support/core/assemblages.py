from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

from .substrate import InheritedBenchmarkContext

WeightInput = Fraction | int | str


@dataclass(frozen=True)
class BranchMember:
    history_id: str
    weight: Fraction
    branch_label: str | None = None


@dataclass(frozen=True)
class BranchAssemblage:
    benchmark_id: str
    interface_id: str
    members: tuple[BranchMember, ...]

    @property
    def total_weight(self) -> Fraction:
        return sum((member.weight for member in self.members), start=Fraction(0, 1))


def coerce_branch_weight(weight: WeightInput) -> Fraction:
    if isinstance(weight, Fraction):
        normalized = weight
    elif isinstance(weight, bool):
        raise TypeError("boolean branch weights are not supported")
    elif isinstance(weight, int):
        normalized = Fraction(weight, 1)
    elif isinstance(weight, str):
        try:
            normalized = Fraction(weight.strip())
        except ValueError as exc:
            raise ValueError(f"invalid branch weight string: {weight!r}") from exc
    elif isinstance(weight, float):
        raise TypeError("binary float branch weights are not supported")
    else:
        raise TypeError(f"unsupported branch weight type: {type(weight).__name__}")

    if normalized < 0:
        raise ValueError("branch weights must be nonnegative")
    if normalized == 0:
        raise ValueError("zero-weight branch members are rejected")
    return normalized


def make_branch_member(
    history_id: str,
    weight: WeightInput,
    *,
    branch_label: str | None = None,
) -> BranchMember:
    return BranchMember(
        history_id=history_id,
        weight=coerce_branch_weight(weight),
        branch_label=branch_label,
    )


def build_branch_assemblage(
    context: InheritedBenchmarkContext,
    interface_id: str,
    members: Iterable[BranchMember],
) -> BranchAssemblage:
    canonical_members = _canonical_members(context, interface_id, tuple(members))
    if not canonical_members:
        raise ValueError("branch assemblages must contain at least one member")
    return BranchAssemblage(
        benchmark_id=context.benchmark_id,
        interface_id=interface_id,
        members=canonical_members,
    )


def canonicalize_branch_assemblage(assemblage: BranchAssemblage) -> BranchAssemblage:
    canonical_members = tuple(
        sorted(
            (
                BranchMember(
                    history_id=member.history_id,
                    weight=coerce_branch_weight(member.weight),
                    branch_label=None,
                )
                for member in assemblage.members
            ),
            key=_member_sort_key,
        )
    )
    return BranchAssemblage(
        benchmark_id=assemblage.benchmark_id,
        interface_id=assemblage.interface_id,
        members=canonical_members,
    )


def _canonical_members(
    context: InheritedBenchmarkContext,
    interface_id: str,
    members: tuple[BranchMember, ...],
) -> tuple[BranchMember, ...]:
    if not context.runtime_package.support.same_support_required:
        raise ValueError(
            f"benchmark {context.benchmark_id} does not certify same-support assemblages"
        )

    allowed_history_ids = {
        history.history_id
        for history in context.runtime_package.histories
        if history.target_interface_id == interface_id
    }
    if not allowed_history_ids:
        raise ValueError(
            f"interface {interface_id} has no inherited histories in benchmark {context.benchmark_id}"
        )

    canonical_members: list[BranchMember] = []
    for member in members:
        if member.history_id not in allowed_history_ids:
            raise ValueError(
                "branch member history "
                f"{member.history_id} is not declared for interface {interface_id}"
            )
        canonical_members.append(
            BranchMember(
                history_id=member.history_id,
                weight=coerce_branch_weight(member.weight),
                branch_label=None,
            )
        )
    return tuple(sorted(canonical_members, key=_member_sort_key))


def _member_sort_key(member: BranchMember) -> tuple[str, int, int]:
    return (member.history_id, member.weight.numerator, member.weight.denominator)


__all__ = [
    "BranchAssemblage",
    "BranchMember",
    "WeightInput",
    "build_branch_assemblage",
    "canonicalize_branch_assemblage",
    "coerce_branch_weight",
    "make_branch_member",
]
