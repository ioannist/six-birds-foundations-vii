from __future__ import annotations

from typing import Any

import numpy as np


def normalize_columns(D: np.ndarray, eps: float = 1e-18) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Normalize columns of D with stable zero-column handling.

    Columns with norm <= eps are treated as zero columns and left as all zeros.
    """

    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    if eps < 0.0:
        raise ValueError("eps must be non-negative.")

    norms = np.linalg.norm(mat, axis=0)
    zero_mask = norms <= float(eps)
    out = mat.astype(np.complex128 if np.iscomplexobj(mat) else float, copy=True)
    nonzero = ~zero_mask
    if np.any(nonzero):
        out[:, nonzero] = out[:, nonzero] / norms[nonzero]
    if np.any(zero_mask):
        out[:, zero_mask] = 0
    return out, norms, zero_mask


def column_space_basis_svd(
    X: np.ndarray,
    rtol: float = 1e-10,
    atol: float = 0.0,
) -> tuple[np.ndarray, int, np.ndarray]:
    """Return an orthonormal basis for col(X) using SVD rank truncation.

    Rank threshold:
      thr = max(atol, rtol * s[0]) where s are singular values.
    """

    mat = np.asarray(X)
    if mat.ndim != 2:
        raise ValueError("X must be a 2D array.")
    if mat.shape[0] < 1 or mat.shape[1] < 1:
        raise ValueError("X must have positive shape in both dimensions.")
    if float(rtol) < 0.0 or float(atol) < 0.0:
        raise ValueError("rtol and atol must be non-negative.")

    U, s, _ = np.linalg.svd(mat, full_matrices=False)
    if s.size == 0:
        raise ValueError("SVD returned no singular values.")

    s0 = float(s[0])
    thr = max(float(atol), float(rtol) * s0)
    r = int(np.sum(s > thr))
    if r < 1:
        raise ValueError("Estimated rank is zero under given tolerances.")

    Q = U[:, :r]
    G = Q.conj().T @ Q
    if not np.allclose(G, np.eye(r, dtype=G.dtype), atol=1e-8, rtol=0.0):
        raise ValueError("Computed basis is not orthonormal within tolerance.")
    return Q, r, s


def mutual_coherence(D: np.ndarray) -> float:
    """Return max off-diagonal absolute inner product of normalized columns."""

    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    M = mat.shape[1]
    if M < 2:
        return 0.0

    d_norm, _, _ = normalize_columns(mat)
    G = np.abs(d_norm.conj().T @ d_norm)
    np.fill_diagonal(G, 0.0)
    return float(np.max(G))


def near_duplicate_pairs(
    D: np.ndarray,
    thresh: float = 0.99,
    max_pairs: int | None = None,
) -> list[tuple[int, int, float]]:
    """Return near-duplicate column pairs (i, j, abs_dot) with i < j and abs_dot >= thresh."""

    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    if thresh < 0.0 or thresh > 1.0:
        raise ValueError("thresh must be in [0, 1].")
    if max_pairs is not None and max_pairs < 0:
        raise ValueError("max_pairs must be non-negative when provided.")

    d_norm, _, zero_mask = normalize_columns(mat)
    M = d_norm.shape[1]
    pairs: list[tuple[int, int, float]] = []
    if M < 2:
        return pairs

    G = np.abs(d_norm.conj().T @ d_norm)
    np.fill_diagonal(G, 0.0)
    for i in range(M):
        if bool(zero_mask[i]):
            continue
        for j in range(i + 1, M):
            if bool(zero_mask[j]):
                continue
            val = float(G[i, j])
            if val >= thresh:
                pairs.append((i, j, val))

    pairs.sort(key=lambda t: (-t[2], t[0], t[1]))
    if max_pairs is not None:
        return pairs[:max_pairs]
    return pairs


def cluster_stats_from_pairs(M: int, pairs: list[tuple[int, int, float]]) -> dict[str, Any]:
    """Compute union-find cluster statistics induced by near-duplicate pairs."""

    if not isinstance(M, int) or M < 0:
        raise ValueError("M must be a non-negative integer.")

    parent = list(range(M))
    used: set[int] = set()

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return
        if ra < rb:
            parent[rb] = ra
        else:
            parent[ra] = rb

    for item in pairs:
        if len(item) != 3:
            raise ValueError("pairs must contain tuples of (i, j, abs_dot).")
        i, j, _ = item
        if not (0 <= int(i) < M and 0 <= int(j) < M):
            raise ValueError("pair index out of range.")
        i = int(i)
        j = int(j)
        if i == j:
            raise ValueError("pair indices must be distinct.")
        a, b = (i, j) if i < j else (j, i)
        used.add(a)
        used.add(b)
        union(a, b)

    comp_sizes: dict[int, int] = {}
    for v in sorted(used):
        r = find(v)
        comp_sizes[r] = comp_sizes.get(r, 0) + 1
    sizes = list(comp_sizes.values())

    hist: dict[int, int] = {}
    for s in sizes:
        hist[s] = hist.get(s, 0) + 1

    return {
        "num_clusters": int(len(sizes)),
        "max_cluster_size": int(max(sizes) if sizes else 0),
        "cluster_size_hist": hist,
        "num_nodes_in_pairs": int(len(used)),
        "num_pairs": int(len(pairs)),
    }


def principal_angles(Psi1: np.ndarray, Psi2: np.ndarray) -> np.ndarray:
    """Return singular values of Psi1^* Psi2 (principal-angle cosines for orthonormal bases)."""

    a = np.asarray(Psi1)
    b = np.asarray(Psi2)
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("Psi1 and Psi2 must be 2D arrays.")
    if a.shape[0] != b.shape[0]:
        raise ValueError("Psi1 and Psi2 must have matching row dimension N.")
    if a.shape[1] < 1 or b.shape[1] < 1:
        raise ValueError("Psi1 and Psi2 must each have at least one column.")

    C = a.conj().T @ b
    s = np.linalg.svd(C, compute_uv=False)
    return np.asarray(s, dtype=float)


def two_column_min_singular(u: np.ndarray, v: np.ndarray) -> float:
    """Return smallest singular value of [u v] after normalizing u and v."""

    uu = np.asarray(u).reshape(-1)
    vv = np.asarray(v).reshape(-1)
    if uu.ndim != 1 or vv.ndim != 1:
        raise ValueError("u and v must be 1D arrays.")
    if uu.shape[0] != vv.shape[0]:
        raise ValueError("u and v must have the same length.")

    nu = float(np.linalg.norm(uu))
    nv = float(np.linalg.norm(vv))
    if nu <= 0.0 or nv <= 0.0:
        raise ValueError("u and v must be non-zero vectors.")

    M = np.stack([uu / nu, vv / nv], axis=1)
    s = np.linalg.svd(M, compute_uv=False, full_matrices=False)
    return float(np.min(s))


def eig_gap_stats(eigvals: np.ndarray, k: int | None = None) -> dict[str, float | int]:
    """Return sorted-eigenvalue gap diagnostics, optionally focused at top-k cutoff."""

    vals = np.asarray(eigvals)
    if vals.ndim != 1:
        raise ValueError("eigvals must be a 1D array.")
    if vals.size < 1:
        raise ValueError("eigvals must be non-empty.")

    vals = np.asarray(vals, dtype=float)
    vals = np.sort(vals)[::-1]
    n = int(vals.size)
    if n >= 2:
        gaps = vals[:-1] - vals[1:]
        gap_min = float(np.min(gaps))
        gap_median = float(np.median(gaps))
        gap_max = float(np.max(gaps))
    else:
        gaps = np.array([], dtype=float)
        gap_min = 0.0
        gap_median = 0.0
        gap_max = 0.0

    out: dict[str, float | int] = {
        "n": int(n),
        "gap_min": float(gap_min),
        "gap_median": float(gap_median),
        "gap_max": float(gap_max),
    }

    if k is not None and 1 <= int(k) < n:
        kk = int(k)
        cutoff_idx = kk - 1
        gap_at = float(vals[cutoff_idx] - vals[cutoff_idx + 1])

        # Window over gap indices centered on cutoff gap index.
        lo = max(0, cutoff_idx - 3)
        hi = min(n - 2, cutoff_idx + 3)
        if hi >= lo:
            near = gaps[lo : hi + 1]
            min_near = float(np.min(near))
        else:
            min_near = float(gap_at)

        out.update(
            {
                "k": int(kk),
                "gap_at_cutoff": float(gap_at),
                "min_gap_near_cutoff": float(min_near),
                "gap_ratio_cutoff_to_median": float(gap_at / (gap_median + 1e-18)),
            }
        )

    return out
