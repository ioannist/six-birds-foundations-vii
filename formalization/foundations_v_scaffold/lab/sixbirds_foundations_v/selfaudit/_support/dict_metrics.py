from __future__ import annotations

import numpy as np


def gram_matrix(D: np.ndarray) -> np.ndarray:
    d = np.asarray(D)
    if d.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    return d.conj().T @ d


def mutual_coherence(D: np.ndarray) -> float:
    G = gram_matrix(D)
    A = np.abs(G).astype(float, copy=False)
    np.fill_diagonal(A, 0.0)
    return float(np.max(A))


def mean_abs_offdiag(D: np.ndarray) -> float:
    G = gram_matrix(D)
    A = np.abs(G).astype(float, copy=False)
    M = A.shape[0]
    if M <= 1:
        return 0.0
    np.fill_diagonal(A, 0.0)
    return float(np.sum(A) / float(M * (M - 1)))


def gram_spectrum_summaries(D: np.ndarray) -> dict[str, float]:
    d = np.asarray(D)
    if d.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    svals = np.linalg.svd(d, full_matrices=False, compute_uv=False)
    sigma_max = float(svals[0])
    sigma_min = float(svals[-1])
    gram_top_eig = sigma_max**2
    cond_proxy = float(np.inf) if sigma_min <= 1e-12 else float(sigma_max / sigma_min)
    fro2 = float(np.linalg.norm(d, ord="fro") ** 2)
    stable_rank = float(fro2 / (gram_top_eig + 1e-18))
    return {
        "gram_top_eig": float(gram_top_eig),
        "cond_proxy": cond_proxy,
        "stable_rank": stable_rank,
    }


def dictionary_metrics(D: np.ndarray) -> dict[str, float]:
    out = {
        "mu": mutual_coherence(D),
        "mean_abs_offdiag": mean_abs_offdiag(D),
    }
    out.update(gram_spectrum_summaries(D))
    return out
