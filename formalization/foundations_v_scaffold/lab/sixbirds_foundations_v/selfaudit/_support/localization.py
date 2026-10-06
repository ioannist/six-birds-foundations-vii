from __future__ import annotations

import numpy as np


def make_cells_1d(N: int, j: int) -> list[np.ndarray]:
    if not isinstance(N, int):
        raise ValueError("N must be an integer.")
    if not isinstance(j, int):
        raise ValueError("j must be an integer.")
    if N < 1:
        raise ValueError("N must be >= 1.")
    if j < 0:
        raise ValueError("j must be >= 0.")

    num_cells = 2**j
    if N % num_cells != 0:
        raise ValueError("N must be divisible by 2**j.")

    cell_size = N // num_cells
    cells: list[np.ndarray] = []
    for k in range(num_cells):
        start = k * cell_size
        stop = start + cell_size
        cells.append(np.arange(start, stop, dtype=np.int64))
    return cells


def eta_j_from_basis(
    Psi: np.ndarray,
    cells: list[np.ndarray],
    *,
    check_orthonormal: bool = True,
    tol: float = 1e-8,
) -> float:
    psi, N, m = _validate_inputs(Psi, cells, check_orthonormal=check_orthonormal, tol=tol)
    checked_cells = _validate_cells(cells, N)

    eta = -np.inf
    for cell in checked_cells:
        psi_B = psi[cell, :]
        s = psi_B.shape[0]
        if s <= m:
            K_small = psi_B @ psi_B.conj().T
            lam_max = float(np.linalg.eigvalsh(K_small)[-1].real)
        else:
            K_big = psi_B.conj().T @ psi_B
            lam_max = float(np.linalg.eigvalsh(K_big)[-1].real)
        if lam_max > eta:
            eta = lam_max
    return float(eta)


def b_j_per_channel(
    Psi: np.ndarray,
    cells: list[np.ndarray],
    *,
    check_orthonormal: bool = True,
    tol: float = 1e-8,
) -> np.ndarray:
    psi, N, m = _validate_inputs(Psi, cells, check_orthonormal=check_orthonormal, tol=tol)
    checked_cells = _validate_cells(cells, N)

    out = np.zeros(m, dtype=float)
    for cell in checked_cells:
        energies = np.sum(np.abs(psi[cell, :]) ** 2, axis=0)
        out = np.maximum(out, energies)
    return out


def trace_bound_eta(
    Psi: np.ndarray,
    cells: list[np.ndarray],
    *,
    check_orthonormal: bool = True,
    tol: float = 1e-8,
) -> float:
    psi, N, _ = _validate_inputs(Psi, cells, check_orthonormal=check_orthonormal, tol=tol)
    checked_cells = _validate_cells(cells, N)

    trace_max = -np.inf
    for cell in checked_cells:
        trace_val = float(np.sum(np.abs(psi[cell, :]) ** 2))
        if trace_val > trace_max:
            trace_max = trace_val
    return float(trace_max)


def _validate_inputs(
    Psi: np.ndarray,
    cells: list[np.ndarray],
    *,
    check_orthonormal: bool,
    tol: float,
) -> tuple[np.ndarray, int, int]:
    psi = np.asarray(Psi)
    if psi.ndim != 2:
        raise ValueError("Psi must be a 2D array with shape (N, m).")

    N, m = psi.shape
    if N < 1:
        raise ValueError("Psi must have N >= 1 rows.")
    if m < 1:
        raise ValueError("Psi must have m >= 1 columns.")
    if m > N:
        raise ValueError("Psi must satisfy m <= N.")

    if not isinstance(cells, list) or len(cells) == 0:
        raise ValueError("cells must be a non-empty list of index arrays.")

    if check_orthonormal:
        G = psi.conj().T @ psi
        I = np.eye(m, dtype=G.dtype)
        if not np.allclose(G, I, atol=tol, rtol=0.0):
            raise ValueError("Psi columns are not orthonormal within tolerance.")

    return psi, N, m


def _validate_cells(cells: list[np.ndarray], N: int) -> list[np.ndarray]:
    checked: list[np.ndarray] = []
    for idx, cell in enumerate(cells):
        arr = np.asarray(cell)
        if arr.ndim != 1:
            raise ValueError(f"Cell {idx} must be a 1D array of indices.")
        if arr.size == 0:
            raise ValueError(f"Cell {idx} must be non-empty.")
        if not np.issubdtype(arr.dtype, np.integer):
            raise ValueError(f"Cell {idx} must contain integer indices.")
        if np.any(arr < 0) or np.any(arr >= N):
            raise ValueError(f"Cell {idx} contains indices outside [0, N-1].")
        checked.append(arr.astype(np.int64, copy=False))
    return checked
