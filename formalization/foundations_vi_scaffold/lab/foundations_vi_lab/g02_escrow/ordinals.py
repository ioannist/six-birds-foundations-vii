"""Exact Cantor-normal-form ordinals below epsilon_0 for G2-L1."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering


@total_ordering
@dataclass(frozen=True)
class Ordinal:
    """Ordinal below epsilon_0 as Cantor normal form terms.

    `terms` is a tuple of `(exponent, coefficient)` pairs, with strictly
    descending exponents and positive integer coefficients. The empty tuple is
    zero. Exponents are themselves `Ordinal` values, giving the usual recursive
    CNF representation below epsilon_0.
    """

    terms: tuple[tuple["Ordinal", int], ...] = ()

    def __post_init__(self) -> None:
        previous: Ordinal | None = None
        for exponent, coefficient in self.terms:
            if coefficient <= 0:
                raise ValueError("ordinal coefficients must be positive")
            if previous is not None and not (exponent < previous):
                raise ValueError("ordinal exponents must be strictly decreasing")
            previous = exponent

    def is_zero(self) -> bool:
        """Return whether this ordinal is zero."""

        return not self.terms

    def is_finite(self) -> bool:
        """Return whether this ordinal is a finite natural ordinal."""

        return self.is_zero() or (
            len(self.terms) == 1 and self.terms[0][0].is_zero()
        )

    def finite_value(self) -> int:
        """Return the natural value of a finite ordinal."""

        if self.is_zero():
            return 0
        if not self.is_finite():
            raise ValueError("ordinal is not finite")
        return self.terms[0][1]

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Ordinal):
            return NotImplemented
        return _compare(self, other) < 0

    def __str__(self) -> str:
        if self.is_zero():
            return "0"
        return " + ".join(_format_term(exponent, coefficient) for exponent, coefficient in self.terms)


ZERO = Ordinal(())
ONE = Ordinal(((ZERO, 1),))


def finite(n: int) -> Ordinal:
    """Return the finite ordinal `n`."""

    if n < 0:
        raise ValueError("finite ordinal cannot be negative")
    if n == 0:
        return ZERO
    return Ordinal(((ZERO, n),))


def omega_power(exponent: Ordinal, coefficient: int = 1) -> Ordinal:
    """Return `omega^exponent * coefficient` as one CNF term."""

    return Ordinal(((exponent, coefficient),))


def _compare(a: Ordinal, b: Ordinal) -> int:
    if not a.terms and not b.terms:
        return 0
    if not a.terms:
        return -1
    if not b.terms:
        return 1

    (a_exp, a_coeff), *a_tail = a.terms
    (b_exp, b_coeff), *b_tail = b.terms
    exp_cmp = _compare(a_exp, b_exp)
    if exp_cmp != 0:
        return exp_cmp
    if a_coeff != b_coeff:
        return -1 if a_coeff < b_coeff else 1
    return _compare(Ordinal(tuple(a_tail)), Ordinal(tuple(b_tail)))


def _format_term(exponent: Ordinal, coefficient: int) -> str:
    if exponent.is_zero():
        return str(coefficient)

    if exponent == ONE:
        base = "omega"
    else:
        exp_text = str(exponent)
        if " + " in exp_text or "*" in exp_text:
            exp_text = f"({exp_text})"
        base = f"omega^{exp_text}"

    if coefficient == 1:
        return base
    return f"{base}*{coefficient}"

