from __future__ import annotations

from fractions import Fraction

import pytest

from sixbirds_foundations_v.xi import (
    ExtendedRat,
    InRange,
    PositiveSemidefinite,
    StrictPositiveDiagonal,
    Symmetric,
    adequacyResidual,
    blockCurrencyDD,
    blockCurrencyDL,
    blockCurrencyLD,
    blockCurrencyLL,
    conditionalCurrencyDM_L,
    conditionalCurrencyMD_L,
    conditionalCurrencyMM_L,
    diagonalPseudoInverse,
    dot,
    identityMat,
    is_same_family_saturated,
    mat,
    matAdd,
    matMul,
    matScale,
    matSub,
    matVec,
    quad,
    shape,
    standardBasis,
    traceMat,
    transpose,
    vec,
    xiCurrency,
    xiMinimumSpendCost,
    zeroMat,
)


def _example() -> tuple:
    C = mat([[1, 0], [0, 2]])
    L = mat([[1, 1]])
    D = mat([[1, 0]])
    KLLdagger = mat([["2/3"]])
    return C, L, D, KLLdagger


def test_matrix_core_exact_fraction_operations() -> None:
    M = mat([[2, 5], [7, 0]])

    assert diagonalPseudoInverse(M) == mat([["1/2", 0], [0, 0]])
    assert matVec(mat([[1, 2], [3, 4]]), vec([5, 6])) == vec([17, 39])
    assert traceMat(mat([[1, 2], [3, 4]])) == Fraction(5)
    assert matMul(mat([[1, 2]]), mat([[3], [4]])) == mat([[11]])
    assert transpose(mat([[1, 2, 3]])) == mat([[1], [2], [3]])
    assert matSub(mat([[3, 2]]), mat([[1, 5]])) == mat([[2, -3]])
    assert matAdd(mat([[3, 2]]), mat([[1, 5]])) == mat([[4, 7]])
    assert matScale(Fraction(2, 3), mat([[3, 6]])) == mat([[2, 4]])
    assert zeroMat(2, 3) == mat([[0, 0, 0], [0, 0, 0]])
    assert identityMat(3) == mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    assert standardBasis(3, 1) == vec([0, 1, 0])
    assert dot(vec([1, 2]), vec([3, 4])) == Fraction(11)
    assert quad(mat([[2, 0], [0, 3]]), vec([2, 1])) == Fraction(11)
    assert Symmetric(mat([[1, 2], [2, 3]]))
    assert not Symmetric(mat([[1, 2], [0, 3]]))
    assert StrictPositiveDiagonal(mat([[1, 0], [0, 2]]))
    assert not StrictPositiveDiagonal(mat([[1, 1], [0, 2]]))
    assert shape(zeroMat(0, 0)) == (0, 0)


def test_zero_row_nonzero_column_matrices_are_explicitly_unsupported() -> None:
    with pytest.raises(ValueError, match="0-row matrix with nonzero columns"):
        zeroMat(0, 2)


def test_psd_checker_documents_runtime_screen_scope() -> None:
    assert PositiveSemidefinite(mat([[1, 0], [0, 2]]))
    # This matrix is symmetric with nonnegative diagonal but is not PSD in the
    # universal Lean sense; the runtime helper is intentionally only a screen.
    assert PositiveSemidefinite(mat([[1, 2], [2, 1]]))

    skew = mat([[0, 1], [-1, 0]])
    assert quad(skew, vec([3, 5])) == 0
    # Lean's literal PSD predicate accepts this skew-symmetric matrix, but this
    # runtime helper deliberately rejects nonsymmetric matrices because the Xi
    # matrices built by this module are symmetric by construction.
    assert not PositiveSemidefinite(skew)


def test_adequacy_residual_hand_checked_example() -> None:
    C, L, D, KLLdagger = _example()

    assert blockCurrencyLL(C, L) == mat([["3/2"]])
    assert blockCurrencyDL(C, L, D) == mat([[1]])
    assert blockCurrencyLD(C, L, D) == mat([[1]])
    assert blockCurrencyDD(C, D) == mat([[1]])
    assert adequacyResidual(C, L, D, KLLdagger) == mat([["1/3"]])


def test_conditional_currencies_saturated_hand_checked_example() -> None:
    C, L, D, KLLdagger = _example()
    M = mat([[2, 2]])

    assert conditionalCurrencyDM_L(C, L, D, M, KLLdagger) == mat([[0]])
    assert conditionalCurrencyMM_L(C, L, M, KLLdagger) == mat([[0]])
    assert conditionalCurrencyMD_L(C, L, D, M, KLLdagger) == mat([[0]])
    assert is_same_family_saturated(C, L, D, M, KLLdagger, mat([[2]]))


def test_same_family_saturation_rejects_non_saturated_candidate() -> None:
    C, L, D, KLLdagger = _example()
    M = mat([[0, 1]])

    assert conditionalCurrencyDM_L(C, L, D, M, KLLdagger) == mat([["-1/3"]])
    assert not is_same_family_saturated(C, L, D, M, KLLdagger, mat([[1]]))


def test_currency_and_minimum_spend_checkers_are_verification_shaped() -> None:
    C = identityMat(2)
    F = identityMat(2)
    z = vec([2, 0])

    assert xiCurrency(C, F) == identityMat(2)
    assert InRange(F, z)
    assert InRange(F, z, witness=vec([2, 0]))
    assert xiMinimumSpendCost(
        C,
        F,
        z,
        ExtendedRat.finite(4),
        witness=vec([2, 0]),
        lower_bound_witnesses=[vec([2, 0])],
    )
    assert not xiMinimumSpendCost(
        C,
        F,
        z,
        ExtendedRat.finite(3),
        witness=vec([2, 0]),
    )

    zero_family = zeroMat(1, 2)
    assert not InRange(zero_family, vec([1]))
    assert xiMinimumSpendCost(C, zero_family, vec([1]), ExtendedRat.pos_infinity())


def test_float_inputs_are_rejected() -> None:
    with pytest.raises(TypeError):
        mat([[0.5]])
