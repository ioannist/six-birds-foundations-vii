"""Currency and minimum-spend checkers ported from ``Xi/Currency.lean``."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from .matrix import (
    ExtendedRat,
    Mat,
    ScalarInput,
    Vec,
    InRange,
    diagonalPseudoInverse,
    matMul,
    matVec,
    quad,
    transpose,
    vec,
)


def xiCurrency(C: Mat, F: Mat) -> Mat:
    return matMul(matMul(F, diagonalPseudoInverse(C)), transpose(F))


def xiMinimumSpendCost(
    C: Mat,
    F: Mat,
    z: Sequence[ScalarInput],
    value: ExtendedRat,
    *,
    witness: Sequence[ScalarInput] | None = None,
    lower_bound_witnesses: Iterable[Sequence[ScalarInput]] = (),
) -> bool:
    """Verification-shaped checker for Lean's ``xiMinimumSpendCost`` Prop.

    For finite values, this verifies a concrete attaining witness and any
    caller-supplied feasible comparison witnesses.  It does not solve the
    universal lower-bound problem.  For positive infinity, it uses exact
    Gaussian elimination via ``InRange`` to check that ``z`` is outside the
    range of ``F``.
    """

    if value.is_pos_infinity:
        return not InRange(F, z)

    if witness is None:
        raise ValueError("finite xiMinimumSpendCost checks require an attaining witness")

    m = value.value()
    target = vec(z)
    if matVec(F, witness) != target:
        return False
    if quad(C, witness) != m:
        return False
    for candidate in lower_bound_witnesses:
        if matVec(F, candidate) == target and m > quad(C, candidate):
            return False
    return True


__all__ = ["xiCurrency", "xiMinimumSpendCost"]
