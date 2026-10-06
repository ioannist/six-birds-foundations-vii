"""Provable tunable Recaman-style variants for G6-L2."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvenJumpSummary:
    """Verification summary for Variant A."""

    steps: int
    final_value: int
    max_value: int
    unique_visited: int
    all_even: bool
    odd_violations: tuple[int, ...]


@dataclass(frozen=True)
class UnitJumpSummary:
    """Verification summary for Variant B."""

    steps: int
    final_value: int
    max_value: int
    unique_visited: int
    identity_holds: bool
    visited_set_exact: bool
    first_identity_failure: int | None
    first_missing_or_extra: int | None


@dataclass(frozen=True)
class TunableSummary:
    """Combined G6-L2 verification summary."""

    even_jump: EvenJumpSummary
    unit_jump: UnitJumpSummary


def even_jump_terms(steps: int) -> tuple[int, ...]:
    """Return Variant A terms through step `steps`."""

    if steps < 0:
        raise ValueError("steps must be nonnegative")
    current = 0
    visited = {current}
    values = [current]
    for n in range(1, steps + 1):
        jump = 2 * n
        candidate = current - jump
        if candidate > 0 and candidate not in visited:
            current = candidate
        else:
            current = current + jump
        visited.add(current)
        values.append(current)
    return tuple(values)


def unit_jump_terms(steps: int) -> tuple[int, ...]:
    """Return Variant B terms through step `steps`."""

    if steps < 0:
        raise ValueError("steps must be nonnegative")
    current = 0
    visited = {current}
    values = [current]
    for _n in range(1, steps + 1):
        candidate = current - 1
        if candidate > 0 and candidate not in visited:
            current = candidate
        else:
            current = current + 1
        visited.add(current)
        values.append(current)
    return tuple(values)


def verify_even_jump_variant(steps: int = 1_000_000) -> EvenJumpSummary:
    """Verify every Variant A term is even through `steps`."""

    current = 0
    visited = {current}
    max_value = current
    odd_violations: list[int] = []
    for n in range(1, steps + 1):
        jump = 2 * n
        candidate = current - jump
        if candidate > 0 and candidate not in visited:
            current = candidate
        else:
            current = current + jump
        if current % 2 != 0:
            odd_violations.append(current)
        visited.add(current)
        if current > max_value:
            max_value = current
    return EvenJumpSummary(
        steps=steps,
        final_value=current,
        max_value=max_value,
        unique_visited=len(visited),
        all_even=not odd_violations,
        odd_violations=tuple(odd_violations[:20]),
    )


def verify_unit_jump_variant(steps: int = 1_000_000) -> UnitJumpSummary:
    """Verify Variant B satisfies `a_n = n` and visits `{0,...,n}`."""

    current = 0
    visited = {current}
    first_identity_failure: int | None = None
    max_value = current
    for n in range(1, steps + 1):
        candidate = current - 1
        if candidate > 0 and candidate not in visited:
            current = candidate
        else:
            current = current + 1
        visited.add(current)
        if current > max_value:
            max_value = current
        if first_identity_failure is None and current != n:
            first_identity_failure = n

    expected = set(range(steps + 1))
    visited_set_exact = visited == expected
    first_missing_or_extra: int | None = None
    if not visited_set_exact:
        symmetric_difference = visited.symmetric_difference(expected)
        first_missing_or_extra = min(symmetric_difference)

    return UnitJumpSummary(
        steps=steps,
        final_value=current,
        max_value=max_value,
        unique_visited=len(visited),
        identity_holds=first_identity_failure is None,
        visited_set_exact=visited_set_exact,
        first_identity_failure=first_identity_failure,
        first_missing_or_extra=first_missing_or_extra,
    )


def verify_tunable_variants(
    *, even_steps: int = 1_000_000, unit_steps: int = 1_000_000
) -> TunableSummary:
    """Run both G6-L2 variant verifications."""

    return TunableSummary(
        even_jump=verify_even_jump_variant(even_steps),
        unit_jump=verify_unit_jump_variant(unit_steps),
    )
