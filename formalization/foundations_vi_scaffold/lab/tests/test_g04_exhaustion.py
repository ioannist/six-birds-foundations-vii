"""Tests for the G4 greedy Egyptian-fraction lab."""

from fractions import Fraction

from foundations_vi_lab.g04_exhaustion.egyptian import (
    expand_fraction,
    greedy_step,
    unit_fraction_sum,
)


def test_greedy_step_for_three_sevenths() -> None:
    """The first `3/7` step is `1/3` with remainder `2/21`."""

    m, remainder = greedy_step(Fraction(3, 7))
    assert m == 3
    assert remainder == Fraction(2, 21)


def test_three_sevenths_worked_expansion() -> None:
    """`3/7 = 1/3 + 1/11 + 1/231` exactly."""

    expansion = expand_fraction(3, 7)
    assert expansion.denominators == (3, 11, 231)
    assert expansion.numerators == (3, 2, 1, 0)
    assert unit_fraction_sum(expansion.denominators) == Fraction(3, 7)


def test_two_thirds_worked_expansion() -> None:
    """`2/3 = 1/2 + 1/6` exactly."""

    expansion = expand_fraction(2, 3)
    assert expansion.denominators == (2, 6)
    assert expansion.numerators == (2, 1, 0)
    assert unit_fraction_sum(expansion.denominators) == Fraction(2, 3)


def test_non_lowest_terms_reduce_first() -> None:
    """`4/6` reduces to `2/3` before expansion."""

    expansion = expand_fraction(4, 6)
    assert (expansion.reduced_p, expansion.reduced_q) == (2, 3)
    assert expansion.denominators == (2, 6)
