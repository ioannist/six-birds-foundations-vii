"""Adequacy residual formulas ported from ``Xi/AdequacyResidual.lean``."""

from __future__ import annotations

from .matrix import Mat, ScalarInput, diagonalPseudoInverse, matMul, matSub, transpose


def blockCurrencyLL(C: Mat, L: Mat) -> Mat:
    return matMul(matMul(L, diagonalPseudoInverse(C)), transpose(L))


def blockCurrencyDL(C: Mat, L: Mat, D: Mat) -> Mat:
    return matMul(matMul(D, diagonalPseudoInverse(C)), transpose(L))


def blockCurrencyLD(C: Mat, L: Mat, D: Mat) -> Mat:
    return matMul(matMul(L, diagonalPseudoInverse(C)), transpose(D))


def blockCurrencyDD(C: Mat, D: Mat) -> Mat:
    return matMul(matMul(D, diagonalPseudoInverse(C)), transpose(D))


def adequacyResidual(C: Mat, L: Mat, D: Mat, KLLdagger: Mat) -> Mat:
    """Return ``K_DD - K_DL K_LL^dagger K_LD``.

    The Moore-Penrose-like matrix ``KLLdagger`` is an explicit caller-supplied
    parameter, exactly as in Lean.  This function intentionally does not
    compute a general pseudoinverse.
    """

    return matSub(
        blockCurrencyDD(C, D),
        matMul(matMul(blockCurrencyDL(C, L, D), KLLdagger), blockCurrencyLD(C, L, D)),
    )


__all__ = [
    "adequacyResidual",
    "blockCurrencyDD",
    "blockCurrencyDL",
    "blockCurrencyLD",
    "blockCurrencyLL",
]
