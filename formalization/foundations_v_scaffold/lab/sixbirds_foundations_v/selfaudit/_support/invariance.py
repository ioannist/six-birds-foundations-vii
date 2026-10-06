from __future__ import annotations

import numpy as np


def cyclic_shift_rows(X: np.ndarray, shift: int) -> np.ndarray:
    return np.roll(X, shift=shift, axis=0)


def projector_diag_from_basis(Psi: np.ndarray) -> np.ndarray:
    psi = np.asarray(Psi)
    if psi.ndim != 2:
        raise ValueError("Psi must be a 2D array with shape (N, m).")
    N, m = psi.shape
    if N < 1:
        raise ValueError("Psi must have N >= 1 rows.")
    if m < 1 or m > N:
        raise ValueError("Psi must satisfy 1 <= m <= N.")
    if not (
        np.issubdtype(psi.dtype, np.floating)
        or np.issubdtype(psi.dtype, np.complexfloating)
    ):
        raise ValueError("Psi dtype must be float or complex.")

    return np.sum(np.abs(psi) ** 2, axis=1).astype(float, copy=False)


def subspace_shift_residual_score(Psi: np.ndarray, shift: int) -> float:
    psi = np.asarray(Psi)
    if psi.ndim != 2:
        raise ValueError("Psi must be a 2D array with shape (N, m).")
    N, m = psi.shape
    if N < 1:
        raise ValueError("Psi must have N >= 1 rows.")
    if m < 1 or m > N:
        raise ValueError("Psi must satisfy 1 <= m <= N.")

    psi_shift = cyclic_shift_rows(psi, int(shift))
    C = psi.conj().T @ psi_shift
    proj = psi @ C
    residual = psi_shift - proj

    denom = float(np.linalg.norm(psi_shift, ord="fro"))
    if denom == 0.0:
        return 0.0
    numer = float(np.linalg.norm(residual, ord="fro"))
    return numer / denom


def diag_stats(diagP: np.ndarray) -> dict[str, float]:
    d = np.asarray(diagP, dtype=float)
    if d.ndim != 1 or d.size == 0:
        raise ValueError("diagP must be a non-empty 1D array.")

    mean = float(np.mean(d))
    std = float(np.std(d))
    return {
        "diag_mean": mean,
        "diag_std": std,
        "diag_min": float(np.min(d)),
        "diag_max": float(np.max(d)),
        "diag_cv": float(std / (mean + 1e-18)),
    }
