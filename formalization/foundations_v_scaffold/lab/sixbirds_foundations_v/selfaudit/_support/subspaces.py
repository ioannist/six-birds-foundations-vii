from __future__ import annotations

import numpy as np


def haar_random_subspace(N: int, m: int, seed: int) -> np.ndarray:
    _validate_N_m(N, m)
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((N, m))
    Q, R = np.linalg.qr(A, mode="reduced")
    signs = np.sign(np.diag(R))
    signs[signs == 0] = 1.0
    return Q * signs


def fourier_lowfreq_subspace(N: int, m: int) -> np.ndarray:
    _validate_N_m(N, m)
    ks = _lowfreq_indices(N, m)
    n = np.arange(N, dtype=float)[:, None]
    k = np.array(ks, dtype=float)[None, :]
    return np.exp(2j * np.pi * n * k / float(N)) / np.sqrt(float(N))


def circulant_top_fourier_subspace(N: int, m: int, sigma: float = 4.0) -> np.ndarray:
    """Return top-m Fourier modes by eigenvalue of a Gaussian-ish circulant kernel."""
    _validate_N_m(N, m)
    if sigma <= 0:
        raise ValueError("sigma must be > 0.")

    idx = np.arange(N, dtype=float)
    dist = np.minimum(idx, N - idx)
    kernel = np.exp(-(dist**2) / (2.0 * float(sigma) ** 2))
    kernel /= np.sum(kernel)

    lam = np.fft.fft(kernel).real
    order = np.lexsort((np.arange(N), -lam))
    ks = order[:m]

    n = np.arange(N, dtype=float)[:, None]
    k = np.array(ks, dtype=float)[None, :]
    return np.exp(2j * np.pi * n * k / float(N)) / np.sqrt(float(N))


def delta_localized_subspace(
    N: int,
    m: int,
    pattern: str = "first",
    seed: int | None = None,
) -> np.ndarray:
    _validate_N_m(N, m)
    if pattern not in {"first", "random"}:
        raise ValueError("pattern must be either 'first' or 'random'.")

    if pattern == "first":
        idx = np.arange(m, dtype=np.int64)
    else:
        rng = np.random.default_rng(seed)
        idx = rng.choice(N, size=m, replace=False)
        idx = np.asarray(idx, dtype=np.int64)

    return np.eye(N, dtype=float)[:, idx]


def _lowfreq_indices(N: int, m: int) -> list[int]:
    out: list[int] = []
    seen: set[int] = set()
    k = 0
    while len(out) < m:
        candidates = [0] if k == 0 else [k, (-k) % N]
        for c in candidates:
            if c not in seen:
                seen.add(c)
                out.append(c)
                if len(out) == m:
                    break
        k += 1
        if k > N:
            raise ValueError("Unable to generate enough unique Fourier frequencies.")
    return out


def _validate_N_m(N: int, m: int) -> None:
    if not isinstance(N, int):
        raise ValueError("N must be an integer.")
    if not isinstance(m, int):
        raise ValueError("m must be an integer.")
    if N < 1:
        raise ValueError("N must be >= 1.")
    if m < 1:
        raise ValueError("m must be >= 1.")
    if m > N:
        raise ValueError("m must satisfy 1 <= m <= N.")
