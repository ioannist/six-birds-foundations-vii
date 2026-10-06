"""Exact rational matrix primitives ported from ``Main/LegalQuotient.lean``.

The module deliberately uses ``fractions.Fraction`` only.  Float inputs are
rejected so that callers cannot accidentally import binary floating-point
rounding into the Xi laboratory.

Matrices are tuple-backed.  That lightweight representation cannot distinguish
a 0-by-0 matrix from a 0-by-n matrix for n > 0, so constructors reject
0-row/nonzero-column matrices instead of silently collapsing their shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


ScalarInput = Fraction | int | str
Vec = tuple[Fraction, ...]
Mat = tuple[tuple[Fraction, ...], ...]


def _fraction(value: ScalarInput) -> Fraction:
    if isinstance(value, bool):
        raise TypeError("boolean values are not valid rational scalars")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"expected Fraction, int, or rational string, got {type(value).__name__}")


def vec(values: Sequence[ScalarInput]) -> Vec:
    return tuple(_fraction(value) for value in values)


def mat(rows: Sequence[Sequence[ScalarInput]]) -> Mat:
    """Normalize a concrete row list.

    An empty row list represents only the 0-by-0 matrix.  Use ``zeroMat`` for
    generated zero matrices; it rejects the unsupported 0-by-n shape when
    n is nonzero.
    """

    normalized = tuple(tuple(_fraction(value) for value in row) for row in rows)
    if not normalized:
        return ()
    width = len(normalized[0])
    for row in normalized:
        if len(row) != width:
            raise ValueError("matrix rows must all have the same length")
    return normalized


def shape(M: Mat) -> tuple[int, int]:
    if not M:
        return (0, 0)
    return (len(M), len(M[0]))


def _require_matrix(M: Sequence[Sequence[ScalarInput]]) -> Mat:
    return mat(M)


def _require_vector(v: Sequence[ScalarInput]) -> Vec:
    return vec(v)


def _require_square(M: Mat) -> None:
    m, n = shape(M)
    if m != n:
        raise ValueError("matrix must be square")


def matVec(M: Sequence[Sequence[ScalarInput]], v: Sequence[ScalarInput]) -> Vec:
    A = _require_matrix(M)
    x = _require_vector(v)
    m, n = shape(A)
    if len(x) != n:
        raise ValueError("matrix/vector dimensions do not align")
    return tuple(sum(A[i][j] * x[j] for j in range(n)) for i in range(m))


def traceMat(M: Sequence[Sequence[ScalarInput]]) -> Fraction:
    A = _require_matrix(M)
    _require_square(A)
    return sum(A[i][i] for i in range(len(A)))


def matMul(
    A: Sequence[Sequence[ScalarInput]],
    B: Sequence[Sequence[ScalarInput]],
) -> Mat:
    left = _require_matrix(A)
    right = _require_matrix(B)
    m, n = shape(left)
    n2, p = shape(right)
    if n != n2:
        raise ValueError("matrix dimensions do not align for multiplication")
    return tuple(
        tuple(sum(left[i][j] * right[j][k] for j in range(n)) for k in range(p))
        for i in range(m)
    )


def transpose(M: Sequence[Sequence[ScalarInput]]) -> Mat:
    A = _require_matrix(M)
    m, n = shape(A)
    return tuple(tuple(A[i][j] for i in range(m)) for j in range(n))


def matSub(
    A: Sequence[Sequence[ScalarInput]],
    B: Sequence[Sequence[ScalarInput]],
) -> Mat:
    left = _require_matrix(A)
    right = _require_matrix(B)
    if shape(left) != shape(right):
        raise ValueError("matrix dimensions do not align for subtraction")
    m, n = shape(left)
    return tuple(tuple(left[i][j] - right[i][j] for j in range(n)) for i in range(m))


def matAdd(
    A: Sequence[Sequence[ScalarInput]],
    B: Sequence[Sequence[ScalarInput]],
) -> Mat:
    left = _require_matrix(A)
    right = _require_matrix(B)
    if shape(left) != shape(right):
        raise ValueError("matrix dimensions do not align for addition")
    m, n = shape(left)
    return tuple(tuple(left[i][j] + right[i][j] for j in range(n)) for i in range(m))


def matScale(r: ScalarInput, M: Sequence[Sequence[ScalarInput]]) -> Mat:
    scalar = _fraction(r)
    A = _require_matrix(M)
    m, n = shape(A)
    return tuple(tuple(scalar * A[i][j] for j in range(n)) for i in range(m))


def zeroMat(m: int, n: int) -> Mat:
    if m < 0 or n < 0:
        raise ValueError("matrix dimensions must be nonnegative")
    if m == 0 and n != 0:
        raise ValueError(
            "tuple-backed Mat cannot represent a 0-row matrix with nonzero columns"
        )
    return tuple(tuple(Fraction(0) for _ in range(n)) for _ in range(m))


def identityMat(n: int) -> Mat:
    if n < 0:
        raise ValueError("matrix dimension must be nonnegative")
    return tuple(
        tuple(Fraction(1) if i == j else Fraction(0) for j in range(n))
        for i in range(n)
    )


def standardBasis(n: int, i: int) -> Vec:
    if n < 0:
        raise ValueError("vector length must be nonnegative")
    if i < 0 or i >= n:
        raise IndexError("basis index out of range")
    return tuple(Fraction(1) if j == i else Fraction(0) for j in range(n))


def dot(u: Sequence[ScalarInput], v: Sequence[ScalarInput]) -> Fraction:
    left = _require_vector(u)
    right = _require_vector(v)
    if len(left) != len(right):
        raise ValueError("vector dimensions do not align for dot product")
    return sum(left[i] * right[i] for i in range(len(left)))


def quad(M: Sequence[Sequence[ScalarInput]], v: Sequence[ScalarInput]) -> Fraction:
    x = _require_vector(v)
    return dot(x, matVec(M, x))


def Symmetric(M: Sequence[Sequence[ScalarInput]]) -> bool:
    A = _require_matrix(M)
    try:
        _require_square(A)
    except ValueError:
        return False
    n = len(A)
    return all(A[i][j] == A[j][i] for i in range(n) for j in range(n))


def PositiveSemidefinite(M: Sequence[Sequence[ScalarInput]]) -> bool:
    """Return a narrow runtime PSD screen, not a general PSD decision.

    Lean defines PSD as ``forall v, 0 <= quad(M, v)``.  This finite Python
    helper does not decide that universal statement for arbitrary rational
    matrices.  It checks nonnegative diagonal entries, which are necessary,
    and also requires symmetry as a practical sanity screen appropriate to the
    matrix shapes this module actually constructs.  Symmetry is not required
    by Lean's literal definition: skew-symmetric matrices can have zero
    quadratic form everywhere.  Callers needing claim-grade PSD must supply
    stronger construction-specific certificates.
    """

    A = _require_matrix(M)
    if not Symmetric(A):
        return False
    return all(A[i][i] >= 0 for i in range(len(A)))


def StrictPositiveDiagonal(M: Sequence[Sequence[ScalarInput]]) -> bool:
    A = _require_matrix(M)
    try:
        _require_square(A)
    except ValueError:
        return False
    n = len(A)
    return all(
        (A[i][j] > 0 if i == j else A[i][j] == 0)
        for i in range(n)
        for j in range(n)
    )


def diagonalPseudoInverse(M: Sequence[Sequence[ScalarInput]]) -> Mat:
    A = _require_matrix(M)
    _require_square(A)
    n = len(A)
    rows: list[tuple[Fraction, ...]] = []
    for i in range(n):
        row: list[Fraction] = []
        for j in range(n):
            if i != j:
                row.append(Fraction(0))
            elif A[i][i] == 0:
                row.append(Fraction(0))
            else:
                row.append(Fraction(1) / A[i][i])
        rows.append(tuple(row))
    return tuple(rows)


def _rank_augmented(rows: list[list[Fraction]], n_vars: int) -> bool:
    pivot_row = 0
    for col in range(n_vars):
        pivot = None
        for r in range(pivot_row, len(rows)):
            if rows[r][col] != 0:
                pivot = r
                break
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        pivot_value = rows[pivot_row][col]
        rows[pivot_row] = [value / pivot_value for value in rows[pivot_row]]
        for r in range(len(rows)):
            if r == pivot_row:
                continue
            factor = rows[r][col]
            if factor != 0:
                rows[r] = [
                    rows[r][c] - factor * rows[pivot_row][c]
                    for c in range(n_vars + 1)
                ]
        pivot_row += 1

    for row in rows:
        if all(row[c] == 0 for c in range(n_vars)) and row[n_vars] != 0:
            return False
    return True


def InRange(
    M: Sequence[Sequence[ScalarInput]],
    z: Sequence[ScalarInput],
    witness: Sequence[ScalarInput] | None = None,
) -> bool:
    """Check ``exists a, matVec(M, a) == z``.

    If ``witness`` is supplied, this verifies that concrete witness directly.
    Otherwise it runs exact rational Gaussian elimination to decide consistency
    of the linear system ``M a = z``.
    """

    A = _require_matrix(M)
    target = _require_vector(z)
    m, n = shape(A)
    if len(target) != m:
        raise ValueError("target vector length must match matrix row count")
    if witness is not None:
        return matVec(A, witness) == target
    augmented = [list(A[i]) + [target[i]] for i in range(m)]
    return _rank_augmented(augmented, n)


@dataclass(frozen=True)
class ExtendedRat:
    finite_value: Fraction | None = None
    is_pos_infinity: bool = False

    @classmethod
    def finite(cls, value: ScalarInput) -> "ExtendedRat":
        return cls(finite_value=_fraction(value), is_pos_infinity=False)

    @classmethod
    def pos_infinity(cls) -> "ExtendedRat":
        return cls(finite_value=None, is_pos_infinity=True)

    @property
    def is_finite(self) -> bool:
        return not self.is_pos_infinity

    def value(self) -> Fraction:
        if self.is_pos_infinity or self.finite_value is None:
            raise ValueError("positive infinity has no finite value")
        return self.finite_value


__all__ = [
    "ExtendedRat",
    "InRange",
    "Mat",
    "PositiveSemidefinite",
    "ScalarInput",
    "StrictPositiveDiagonal",
    "Symmetric",
    "Vec",
    "diagonalPseudoInverse",
    "dot",
    "identityMat",
    "mat",
    "matAdd",
    "matMul",
    "matScale",
    "matSub",
    "matVec",
    "quad",
    "shape",
    "standardBasis",
    "traceMat",
    "transpose",
    "vec",
    "zeroMat",
]
