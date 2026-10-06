"""Conditional-currency formulas ported from ``Main/CriticalPair.lean``."""

from __future__ import annotations

from .adequacy_residual import blockCurrencyDL, blockCurrencyLD, blockCurrencyLL
from .matrix import Mat, matMul, matSub


def conditionalCurrencyDM_L(C: Mat, L: Mat, D: Mat, M: Mat, KLLdagger: Mat) -> Mat:
    return matSub(
        blockCurrencyDL(C, M, D),
        matMul(matMul(blockCurrencyDL(C, L, D), KLLdagger), blockCurrencyLD(C, L, M)),
    )


def conditionalCurrencyMM_L(C: Mat, L: Mat, M: Mat, KLLdagger: Mat) -> Mat:
    return matSub(
        blockCurrencyLL(C, M),
        matMul(matMul(blockCurrencyDL(C, L, M), KLLdagger), blockCurrencyLD(C, L, M)),
    )


def conditionalCurrencyMD_L(C: Mat, L: Mat, D: Mat, M: Mat, KLLdagger: Mat) -> Mat:
    return matSub(
        blockCurrencyLD(C, M, D),
        matMul(matMul(blockCurrencyDL(C, L, M), KLLdagger), blockCurrencyLD(C, L, D)),
    )


__all__ = [
    "conditionalCurrencyDM_L",
    "conditionalCurrencyMD_L",
    "conditionalCurrencyMM_L",
]
