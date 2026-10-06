from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from scipy.linalg import eigh


def apply_shift_roll(X: np.ndarray, shift: int = 1) -> np.ndarray:
    """Apply cyclic row-shift to a basis matrix X."""

    mat = np.asarray(X)
    if mat.ndim != 2:
        raise ValueError("X must be a 2D array.")
    return np.roll(mat, int(shift), axis=0)


def projector_mismatch_fro(Ua: np.ndarray, Ub: np.ndarray) -> float:
    """Return Frobenius projector mismatch via overlap identity."""

    A = np.asarray(Ua)
    B = np.asarray(Ub)
    if A.ndim != 2 or B.ndim != 2:
        raise ValueError("Ua and Ub must be 2D arrays.")
    if A.shape != B.shape:
        raise ValueError("Ua and Ub must have identical shapes (N, m).")
    m = int(A.shape[1])
    C = A.conj().T @ B
    overlap_fro2 = float(np.sum(np.abs(C) ** 2))
    return float(np.sqrt(max(0.0, 2.0 * m - 2.0 * overlap_fro2)))


def _validate_hermitian(A: np.ndarray) -> np.ndarray:
    mat = np.asarray(A)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError("A must be a square 2D array.")
    if not np.allclose(mat, mat.conj().T, atol=1e-10, rtol=0.0):
        raise ValueError("A must be Hermitian/symmetric.")
    return mat


def _descending_order(vals: np.ndarray) -> np.ndarray:
    # Stable descending sort; preserves LAPACK order inside ties.
    return np.argsort(-vals, kind="mergesort")


def pkg_naive(A: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray]:
    """Naive top-m eigenspace packaging based on Hermitian eigendecomposition."""

    mat = _validate_hermitian(A)
    N = int(mat.shape[0])
    if not (1 <= int(m) <= N):
        raise ValueError("m must satisfy 1 <= m <= N.")

    eigvals, eigvecs = eigh(mat, check_finite=False)
    order = _descending_order(eigvals)
    eigvals_desc = eigvals[order]
    eigvecs_desc = eigvecs[:, order]
    U = eigvecs_desc[:, : int(m)]
    return U, eigvals_desc


def _group_blocks_desc(eigvals_desc: np.ndarray, tol: float) -> list[tuple[int, int]]:
    blocks: list[tuple[int, int]] = []
    n = int(eigvals_desc.size)
    if n == 0:
        return blocks

    start = 0
    for idx in range(1, n):
        if abs(float(eigvals_desc[idx - 1] - eigvals_desc[idx])) > tol:
            blocks.append((start, idx))
            start = idx
    blocks.append((start, n))
    return blocks


def _sort_by_shift_eigs(shift_eigvals: np.ndarray) -> np.ndarray:
    ang = np.angle(shift_eigvals)
    re = np.real(shift_eigvals)
    im = np.imag(shift_eigvals)
    idx = np.arange(shift_eigvals.size, dtype=int)
    # Primary: angle; deterministic ties by real, imag, then index.
    return np.lexsort((idx, im, re, ang))


def pkg_canonical(
    A: np.ndarray,
    m: int,
    *,
    shift_apply: Callable[[np.ndarray], np.ndarray] | None = None,
    shift_matrix: np.ndarray | None = None,
    tol: float = 1e-12,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Canonical top-m packaging with deterministic tie-break in degenerate cutoff blocks."""

    if shift_apply is not None and shift_matrix is not None:
        raise ValueError("Provide at most one of shift_apply or shift_matrix.")
    if tol < 0.0:
        raise ValueError("tol must be non-negative.")

    mat = _validate_hermitian(A)
    N = int(mat.shape[0])
    if not (1 <= int(m) <= N):
        raise ValueError("m must satisfy 1 <= m <= N.")

    eigvals, eigvecs = eigh(mat, check_finite=False)
    order = _descending_order(eigvals)
    eigvals_desc = eigvals[order]
    eigvecs_desc = eigvecs[:, order]
    blocks = _group_blocks_desc(eigvals_desc, float(tol))

    selected_parts: list[np.ndarray] = []
    chosen = 0
    cutoff_block_size = 0
    cutoff_partial = False
    r_from_cutoff = 0
    used_shift_proxy = False

    for bstart, bend in blocks:
        block_size = int(bend - bstart)
        Ublock = eigvecs_desc[:, bstart:bend]
        if chosen + block_size < int(m):
            selected_parts.append(Ublock)
            chosen += block_size
            continue
        if chosen + block_size == int(m):
            selected_parts.append(Ublock)
            chosen += block_size
            cutoff_block_size = block_size
            cutoff_partial = False
            r_from_cutoff = block_size
            break

        # Partial selection from cutoff block.
        cutoff_block_size = block_size
        cutoff_partial = True
        r = int(m) - chosen
        r_from_cutoff = r
        if r <= 0:
            break

        if shift_apply is not None or shift_matrix is not None:
            if shift_apply is not None:
                SU = np.asarray(shift_apply(Ublock))
                if SU.shape != Ublock.shape:
                    raise ValueError("shift_apply(Ublock) must preserve shape.")
                M = Ublock.conj().T @ SU
            else:
                S = np.asarray(shift_matrix)
                if S.ndim != 2 or S.shape != (N, N):
                    # Allow reduced-space shift matrix when packaging reduced operator.
                    if S.ndim != 2 or S.shape != (block_size, block_size):
                        raise ValueError("shift_matrix has incompatible shape.")
                    M = Ublock.conj().T @ (Ublock @ S)
                else:
                    M = Ublock.conj().T @ (S @ Ublock)

            shift_vals, W = np.linalg.eig(M)
            sorder = _sort_by_shift_eigs(shift_vals)
            Wr = W[:, sorder[:r]]
            Usel = Ublock @ Wr
            used_shift_proxy = True
        else:
            Usel = Ublock[:, :r]
            used_shift_proxy = False

        Qr, _ = np.linalg.qr(Usel)
        selected_parts.append(Qr[:, :r])
        chosen += r
        break

    if chosen != int(m):
        # Should be unreachable for valid m; keep explicit guard.
        raise RuntimeError(f"Canonical packaging selected {chosen} vectors, expected {m}.")

    U = np.concatenate(selected_parts, axis=1) if selected_parts else np.zeros((N, 0), dtype=mat.dtype)
    Q, _ = np.linalg.qr(U)
    U = Q[:, : int(m)]

    summary: dict[str, Any] = {
        "m": int(m),
        "tol": float(tol),
        "num_blocks": int(len(blocks)),
        "block_sizes": [int(bend - bstart) for bstart, bend in blocks],
        "cutoff_block_size": int(cutoff_block_size),
        "cutoff_block_partial": bool(cutoff_partial),
        "r_selected_from_cutoff": int(r_from_cutoff),
        "used_shift_proxy": bool(used_shift_proxy),
    }
    return U, summary
