from __future__ import annotations

import numpy as np

from .subspaces import haar_random_subspace


def random_orthoprojector(N: int, m: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    if not isinstance(N, int):
        raise ValueError("N must be an integer.")
    if not isinstance(m, int):
        raise ValueError("m must be an integer.")
    if N < 1:
        raise ValueError("N must be >= 1.")
    if m < 1 or m > N:
        raise ValueError("m must satisfy 1 <= m <= N.")

    Q = haar_random_subspace(N, m, seed)
    P = Q @ Q.T
    return Q, P


def basis_from_sequential(
    Q_small: np.ndarray,
    Q_big: np.ndarray,
    tol: float = 1e-10,
) -> np.ndarray:
    q_small = np.asarray(Q_small)
    q_big = np.asarray(Q_big)
    if q_small.ndim != 2 or q_big.ndim != 2:
        raise ValueError("Q_small and Q_big must be 2D arrays.")
    if q_small.shape[0] != q_big.shape[0]:
        raise ValueError("Q_small and Q_big must have matching row dimension N.")
    if tol < 0:
        raise ValueError("tol must be non-negative.")

    M = q_small.T @ q_big
    U, s, _ = np.linalg.svd(M, full_matrices=False)
    r = int(np.sum(s > tol))
    return q_small @ U[:, :r]


def route_mismatch_fro(Q_small: np.ndarray, Q_big: np.ndarray, Q_direct: np.ndarray) -> float:
    q_small = np.asarray(Q_small)
    q_big = np.asarray(Q_big)
    q_direct = np.asarray(Q_direct)

    if q_small.ndim != 2 or q_big.ndim != 2 or q_direct.ndim != 2:
        raise ValueError("All Q inputs must be 2D arrays.")
    N = q_small.shape[0]
    if q_big.shape[0] != N or q_direct.shape[0] != N:
        raise ValueError("All Q inputs must have same row dimension N.")

    m1 = q_small.shape[1]
    if q_direct.shape[1] != m1:
        raise ValueError("Q_small and Q_direct must have the same column count m1.")

    M = q_small.T @ q_big  # (m1, m2)
    norm_s_sq = float(np.sum(np.abs(M) ** 2))

    A = q_small.T @ q_direct  # (m1, m1)
    B = q_direct.T @ q_big  # (m1, m2)
    C = q_big.T @ q_small  # (m2, m1)
    tr_term = float(np.trace(A @ (B @ C)).real)

    fro2 = norm_s_sq + float(m1) - 2.0 * tr_term
    return float(np.sqrt(max(fro2, 0.0)))
