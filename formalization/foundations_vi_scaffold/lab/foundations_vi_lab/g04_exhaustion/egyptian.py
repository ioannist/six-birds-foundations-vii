"""Exact Fibonacci-Sylvester greedy Egyptian-fraction expansion."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd


@dataclass(frozen=True)
class GreedyStep:
    """One exact greedy subtraction step."""

    numerator_before: int
    denominator_before: int
    unit_denominator: int
    numerator_after: int
    denominator_after: int


@dataclass(frozen=True)
class GreedyExpansion:
    """Full exact greedy expansion for one proper fraction."""

    original_p: int
    original_q: int
    reduced_p: int
    reduced_q: int
    denominators: tuple[int, ...]
    numerators: tuple[int, ...]
    steps: tuple[GreedyStep, ...]

    @property
    def target(self) -> Fraction:
        """The reduced target fraction."""

        return Fraction(self.reduced_p, self.reduced_q)

    @property
    def length(self) -> int:
        """Number of unit fractions in the certificate."""

        return len(self.denominators)


@dataclass(frozen=True)
class SweepSummary:
    """Summary for the full G4-L1 sweep."""

    max_q: int
    step_cap: int
    raw_fraction_count: int
    distinct_reduced_count: int
    failures: tuple[str, ...]
    max_length: int
    max_length_examples: tuple[str, ...]
    length_histogram: dict[int, int]
    max_length_by_q: dict[int, int]


def ceil_div(numerator: int, denominator: int) -> int:
    """Exact positive integer ceiling division."""

    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return (numerator + denominator - 1) // denominator


def reduce_pair(p: int, q: int) -> tuple[int, int]:
    """Reduce a positive rational pair to lowest terms."""

    if p <= 0 or q <= 0:
        raise ValueError("p and q must be positive")
    g = gcd(p, q)
    return p // g, q // g


def greedy_step(frac: Fraction) -> tuple[int, Fraction]:
    """Compute one exact Fibonacci-Sylvester greedy step."""

    if not (0 < frac.numerator < frac.denominator):
        raise ValueError("greedy_step expects a proper positive fraction")
    m = ceil_div(frac.denominator, frac.numerator)
    unit = Fraction(1, m)
    if unit > frac:
        raise AssertionError("greedy unit fraction exceeds target")
    remainder = frac - unit
    if remainder < 0:
        raise AssertionError("negative remainder")
    if remainder.numerator >= frac.numerator:
        raise AssertionError("numerator did not strictly decrease")
    return m, remainder


def expand_fraction(p: int, q: int, *, step_cap: int = 1000) -> GreedyExpansion:
    """Expand `p/q` exactly by the greedy Egyptian-fraction algorithm."""

    if not (0 < p < q):
        raise ValueError("expected a proper fraction 0 < p < q")
    reduced_p, reduced_q = reduce_pair(p, q)
    current = Fraction(reduced_p, reduced_q)
    denominators: list[int] = []
    numerators: list[int] = [current.numerator]
    steps: list[GreedyStep] = []

    for _ in range(step_cap):
        if current == 0:
            break
        before_num = current.numerator
        before_den = current.denominator
        m, remainder = greedy_step(current)
        denominators.append(m)
        numerators.append(remainder.numerator)
        steps.append(
            GreedyStep(
                numerator_before=before_num,
                denominator_before=before_den,
                unit_denominator=m,
                numerator_after=remainder.numerator,
                denominator_after=remainder.denominator,
            )
        )
        current = remainder
    else:
        raise RuntimeError(f"step cap {step_cap} exceeded for {p}/{q}")

    expansion = GreedyExpansion(
        original_p=p,
        original_q=q,
        reduced_p=reduced_p,
        reduced_q=reduced_q,
        denominators=tuple(denominators),
        numerators=tuple(numerators),
        steps=tuple(steps),
    )
    validate_expansion(expansion)
    return expansion


def unit_fraction_sum(denominators: tuple[int, ...]) -> Fraction:
    """Exact sum of the listed unit fractions."""

    total = Fraction(0, 1)
    for d in denominators:
        total += Fraction(1, d)
    return total


def validate_expansion(expansion: GreedyExpansion) -> None:
    """Validate exact sum, distinct denominators, and numerator descent."""

    if len(set(expansion.denominators)) != len(expansion.denominators):
        raise AssertionError(
            f"repeated denominator in {expansion.original_p}/{expansion.original_q}"
        )
    if unit_fraction_sum(expansion.denominators) != expansion.target:
        raise AssertionError(
            f"unit-fraction sum mismatch for {expansion.original_p}/{expansion.original_q}"
        )
    for before, after in zip(expansion.numerators, expansion.numerators[1:]):
        if not after < before:
            raise AssertionError(
                f"non-strict numerator step for {expansion.original_p}/{expansion.original_q}"
            )


def sweep_proper_fractions(max_q: int = 500, *, step_cap: int = 1000) -> SweepSummary:
    """Run the exact G4-L1 sweep over all raw proper fractions `p/q`."""

    raw_count = 0
    reduced_seen: set[tuple[int, int]] = set()
    failures: list[str] = []
    length_histogram: dict[int, int] = {}
    max_length_by_q: dict[int, int] = {}
    max_length = 0
    max_examples: list[str] = []

    for q in range(2, max_q + 1):
        max_for_q = 0
        for p in range(1, q):
            raw_count += 1
            reduced_seen.add(reduce_pair(p, q))
            try:
                expansion = expand_fraction(p, q, step_cap=step_cap)
            except Exception as exc:  # pragma: no cover - failure path is reported.
                failures.append(f"{p}/{q}: {exc}")
                continue
            length_histogram[expansion.length] = (
                length_histogram.get(expansion.length, 0) + 1
            )
            max_for_q = max(max_for_q, expansion.length)
            if expansion.length > max_length:
                max_length = expansion.length
                max_examples = [f"{p}/{q}"]
            elif expansion.length == max_length:
                max_examples.append(f"{p}/{q}")
        max_length_by_q[q] = max_for_q

    return SweepSummary(
        max_q=max_q,
        step_cap=step_cap,
        raw_fraction_count=raw_count,
        distinct_reduced_count=len(reduced_seen),
        failures=tuple(failures),
        max_length=max_length,
        max_length_examples=tuple(max_examples),
        length_histogram=dict(sorted(length_histogram.items())),
        max_length_by_q=max_length_by_q,
    )
