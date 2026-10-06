"""Strict-extension checkers ported from ``Xi/StrictExtension.lean``."""

from __future__ import annotations

from .critical_pair import conditionalCurrencyDM_L
from .matrix import Mat, PositiveSemidefinite, matMul, matSub, shape, zeroMat


def loewnerLE(K: Mat, Theta: Mat) -> bool:
    """Thin checker for Lean's ``loewnerLE K Theta`` definition.

    This inherits the documented limits of ``PositiveSemidefinite``: it checks
    only cheap necessary PSD conditions unless a caller supplies stronger
    construction-specific evidence outside this runtime helper.
    """

    return PositiveSemidefinite(matSub(Theta, K))


def is_same_family_saturated(
    C: Mat,
    L: Mat,
    D: Mat,
    M: Mat,
    KLLdagger: Mat,
    B: Mat,
) -> bool:
    """Check D6's Xi same-family-saturation hypotheses.

    This mirrors the Lean-side condition used by D6: ``M = B @ L`` and
    ``conditionalCurrencyDM_L(...) = zeroMat``.  It does not assert the
    Loewner theorem at runtime.
    """

    if matMul(B, L) != M:
        return False
    z, _ = shape(D)
    m, _ = shape(M)
    return conditionalCurrencyDM_L(C, L, D, M, KLLdagger) == zeroMat(z, m)


__all__ = ["is_same_family_saturated", "loewnerLE"]
