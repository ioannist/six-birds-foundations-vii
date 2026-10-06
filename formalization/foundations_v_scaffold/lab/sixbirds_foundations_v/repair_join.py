"""D1 repair-join checks for finite Repair-World carriers.

The Lean definition represents quotients by maps out of a common carrier and
uses the raw product map for ``Q vee R``.  Python cannot prove the universal
properties for arbitrary types, so the relation checkers take an explicit
finite domain and exhaustively test every pair of carrier states.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar


X = TypeVar("X")
A = TypeVar("A")
B = TypeVar("B")


def Refines(q: Callable[[X], A], r: Callable[[X], B], domain: Sequence[X]) -> bool:
    """Return whether ``q`` refines ``r`` on the given finite carrier.

    This mirrors Lean's ``Refines q r := forall x x', q x = q x' -> r x = r x'``.
    Under the project's order convention, ``q`` is at least as fine as ``r``.
    """

    for x in domain:
        for x_prime in domain:
            if q(x) == q(x_prime) and r(x) != r(x_prime):
                return False
    return True


def fiber_equiv(q: Callable[[X], A], r: Callable[[X], B], domain: Sequence[X]) -> bool:
    """Return whether two quotient maps induce the same fiber relation."""

    for x in domain:
        for x_prime in domain:
            if (q(x) == q(x_prime)) != (r(x) == r(x_prime)):
                return False
    return True


def FiberEquiv(q: Callable[[X], A], r: Callable[[X], B], domain: Sequence[X]) -> bool:
    """Lean-name alias for ``fiber_equiv``."""

    return fiber_equiv(q, r, domain)


def repair_join(q: Callable[[X], A], r: Callable[[X], B]) -> Callable[[X], tuple[A, B]]:
    """Return D1's raw product-map representation of ``Q vee R``."""

    return lambda x: (q(x), r(x))


__all__ = [
    "FiberEquiv",
    "Refines",
    "fiber_equiv",
    "repair_join",
]
