from __future__ import annotations

import numpy as np

from .localization import eta_j_from_basis


def loc_j(v: np.ndarray, cells: list[np.ndarray]) -> float:
    vec = np.asarray(v)
    if vec.ndim != 1:
        raise ValueError("v must be a 1D array.")
    if len(cells) == 0:
        raise ValueError("cells must be a non-empty list.")

    denom = float(np.sum(np.abs(vec) ** 2))
    if denom <= 0.0:
        raise ValueError("v must have non-zero norm.")

    best = 0.0
    for idx, cell in enumerate(cells):
        arr = np.asarray(cell)
        if arr.ndim != 1:
            raise ValueError(f"Cell {idx} must be 1D.")
        if arr.size == 0:
            raise ValueError(f"Cell {idx} must be non-empty.")
        val = float(np.sum(np.abs(vec[arr]) ** 2) / denom)
        if val > best:
            best = val
    return best


def eta_l2_exact_via_qr(
    D: np.ndarray,
    cells: list[np.ndarray],
    rank_tol: float = 1e-10,
) -> dict[str, float]:
    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    if rank_tol < 0.0:
        raise ValueError("rank_tol must be non-negative.")

    Q, R = np.linalg.qr(mat, mode="reduced")
    diag = np.abs(np.diag(R))
    r = int(np.sum(diag > rank_tol))

    if r == 0:
        eta_exact = 0.0
    else:
        Q_r = Q[:, :r]
        eta_exact = float(eta_j_from_basis(Q_r, cells, check_orthonormal=False))

    return {
        "eta_exact": float(eta_exact),
        "rank": float(r),
        "rank_tol": float(rank_tol),
    }
