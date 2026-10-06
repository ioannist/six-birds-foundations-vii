"""Exact Apollonian Descartes-reflection orbit generation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import isqrt
from time import perf_counter
from typing import Iterable


Quadruple = tuple[int, int, int, int]

ADMISSIBLE_MOD24 = frozenset({2, 3, 6, 11, 14, 15, 18, 23})
BASELINE_ROOT: Quadruple = (-1, 2, 2, 3)
RECIPROCITY_ROOT: Quadruple = (-6, 11, 14, 15)


@dataclass(frozen=True)
class CoveragePoint:
    """Coverage summary at one curvature cutoff."""

    bound: int
    admissible_count: int
    hit_count: int
    missing_count: int
    coverage_numerator: int
    coverage_denominator: int


@dataclass(frozen=True)
class ObstructionCheck:
    """Membership check for one reciprocity-obstructed quadratic family."""

    coefficient: int
    checked_values: int
    hit_values: tuple[int, ...]
    first_values: tuple[int, ...]


@dataclass(frozen=True)
class PackingSummary:
    """Bounded exact orbit summary for one root quadruple."""

    label: str
    root: Quadruple
    bound: int
    states_explored: int
    curvatures_hit: int
    admissible_count: int
    missing_count: int
    missing_first: tuple[int, ...]
    missing_last: tuple[int, ...]
    stored_missing: tuple[int, ...]
    residues_hit: tuple[int, ...]
    residue_violations: tuple[int, ...]
    max_curvature_hit: int
    coverage_points: tuple[CoveragePoint, ...]
    obstruction_checks: tuple[ObstructionCheck, ...]
    elapsed_seconds: float


def descartes_holds(q: Quadruple) -> bool:
    """Return whether `q` satisfies the Descartes quadratic identity exactly."""

    total = sum(q)
    return 2 * sum(value * value for value in q) == total * total


def reflect(q: Quadruple, index: int) -> Quadruple:
    """Reflect one Descartes coordinate, replacing it by the other root."""

    if index < 0 or index >= 4:
        raise IndexError(index)
    other_sum = sum(q) - q[index]
    reflected = list(q)
    reflected[index] = 2 * other_sum - q[index]
    return tuple(reflected)  # type: ignore[return-value]


def reflections(q: Quadruple) -> tuple[Quadruple, Quadruple, Quadruple, Quadruple]:
    """Return the four Descartes reflections of `q`."""

    return tuple(reflect(q, index) for index in range(4))  # type: ignore[return-value]


def positive_curvatures(q: Quadruple) -> tuple[int, ...]:
    """Return the positive coordinates of a Descartes quadruple."""

    return tuple(value for value in q if value > 0)


def _within_bound(q: Quadruple, bound: int) -> bool:
    positives = positive_curvatures(q)
    return bool(positives) and max(positives) <= bound


def generate_orbit(root: Quadruple, bound: int) -> tuple[set[Quadruple], set[int]]:
    """Generate the bounded Descartes-reflection orbit and hit curvatures.

    The traversal keeps states whose positive coordinates are all at most
    `bound`. In the usual Apollonian descent tree, every state contributing a
    positive curvature at most `bound` has a path through such bounded states
    back to the root.
    """

    if bound <= 0:
        raise ValueError("bound must be positive")
    if not descartes_holds(root):
        raise ValueError(f"root is not a Descartes quadruple: {root}")

    visited: set[Quadruple] = {root}
    queue: deque[Quadruple] = deque([root])
    curvatures: set[int] = set()

    while queue:
        q = queue.popleft()
        if not descartes_holds(q):
            raise AssertionError(f"Descartes identity failed for {q}")
        curvatures.update(value for value in q if 0 < value <= bound)
        for neighbor in reflections(q):
            if not descartes_holds(neighbor):
                raise AssertionError(f"Descartes identity failed for {neighbor}")
            if neighbor not in visited and _within_bound(neighbor, bound):
                visited.add(neighbor)
                queue.append(neighbor)
    return visited, curvatures


def admissible_values(bound: int) -> tuple[int, ...]:
    """Return positive integers up to `bound` in the expected mod-24 classes."""

    return tuple(value for value in range(1, bound + 1) if value % 24 in ADMISSIBLE_MOD24)


def missing_admissible(curvatures: set[int], bound: int) -> tuple[int, ...]:
    """Return admissible curvatures up to `bound` not present in `curvatures`."""

    return tuple(value for value in admissible_values(bound) if value not in curvatures)


def residue_violations(curvatures: Iterable[int]) -> tuple[int, ...]:
    """Return generated positive curvatures outside the expected mod-24 classes."""

    return tuple(sorted(value for value in curvatures if value % 24 not in ADMISSIBLE_MOD24))


def obstruction_values(coefficient: int, bound: int) -> tuple[int, ...]:
    """Return values `coefficient * n^2 <= bound`, with `n >= 1`."""

    max_n = isqrt(bound // coefficient)
    return tuple(coefficient * n * n for n in range(1, max_n + 1))


def check_obstruction_family(
    curvatures: set[int],
    coefficient: int,
    bound: int,
    sample_size: int = 12,
) -> ObstructionCheck:
    """Check one `coefficient * n^2` family against generated curvatures."""

    values = obstruction_values(coefficient, bound)
    hits = tuple(value for value in values if value in curvatures)
    return ObstructionCheck(
        coefficient=coefficient,
        checked_values=len(values),
        hit_values=hits,
        first_values=values[:sample_size],
    )


def coverage_points(
    curvatures: set[int],
    checkpoints: Iterable[int],
) -> tuple[CoveragePoint, ...]:
    """Compute exact hit/admissible coverage points at selected bounds."""

    points: list[CoveragePoint] = []
    for bound in checkpoints:
        admissible = admissible_values(bound)
        hit_count = sum(1 for value in admissible if value in curvatures)
        admissible_count = len(admissible)
        points.append(
            CoveragePoint(
                bound=bound,
                admissible_count=admissible_count,
                hit_count=hit_count,
                missing_count=admissible_count - hit_count,
                coverage_numerator=hit_count,
                coverage_denominator=admissible_count,
            )
        )
    return tuple(points)


def summarize_packing(
    label: str,
    root: Quadruple,
    bound: int,
    checkpoints: Iterable[int],
    check_reciprocity: bool = False,
    store_missing_limit: int = 20_000,
) -> PackingSummary:
    """Generate one bounded orbit and return a compact exact summary."""

    start = perf_counter()
    states, curvatures = generate_orbit(root, bound)
    elapsed = perf_counter() - start

    missing = missing_admissible(curvatures, bound)
    violations = residue_violations(curvatures)
    stored_missing = missing if len(missing) <= store_missing_limit else ()
    obstruction_checks = (
        tuple(check_obstruction_family(curvatures, coefficient, bound) for coefficient in (2, 3, 6))
        if check_reciprocity
        else ()
    )
    residues = tuple(sorted({value % 24 for value in curvatures}))
    return PackingSummary(
        label=label,
        root=root,
        bound=bound,
        states_explored=len(states),
        curvatures_hit=len(curvatures),
        admissible_count=len(admissible_values(bound)),
        missing_count=len(missing),
        missing_first=missing[:25],
        missing_last=missing[-25:],
        stored_missing=stored_missing,
        residues_hit=residues,
        residue_violations=violations[:50],
        max_curvature_hit=max(curvatures) if curvatures else 0,
        coverage_points=coverage_points(curvatures, checkpoints),
        obstruction_checks=obstruction_checks,
        elapsed_seconds=elapsed,
    )
