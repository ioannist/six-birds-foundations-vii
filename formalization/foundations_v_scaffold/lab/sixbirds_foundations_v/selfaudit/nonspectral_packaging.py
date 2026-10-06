from __future__ import annotations

from typing import Any

import numpy as np

from .spectral_packaging import projector_mismatch_fro


def _validate_square(A: np.ndarray) -> np.ndarray:
    mat = np.asarray(A)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError("A must be a square matrix.")
    return mat


def _krylov_matrix(A: np.ndarray, v: np.ndarray, k: int) -> np.ndarray:
    N = A.shape[0]
    K = np.zeros((N, int(k)), dtype=np.result_type(A, v, np.float64))
    cur = np.asarray(v).astype(K.dtype, copy=True)
    for t in range(int(k)):
        K[:, t] = cur
        cur = A @ cur
    return K


def _resolve_start_vector(
    A: np.ndarray,
    *,
    v: np.ndarray | None,
    v_seed: int | None,
) -> tuple[np.ndarray, dict[str, Any]]:
    N = A.shape[0]
    if v is not None and v_seed is not None:
        raise ValueError("Provide either v or v_seed, not both.")
    if v is None and v_seed is None:
        raise ValueError("Provide one of v or v_seed.")

    if v is not None:
        vec = np.asarray(v).reshape(-1)
        if vec.size != N:
            raise ValueError("v must have length N.")
        vec = vec.astype(np.result_type(A, vec, np.float64), copy=True)
        source = "explicit_v"
        seed_used = None
    else:
        rng = np.random.default_rng(int(v_seed))
        vec = rng.standard_normal(N).astype(np.result_type(A, np.float64), copy=False)
        source = "seed"
        seed_used = int(v_seed)

    nrm = float(np.linalg.norm(vec))
    if nrm <= 0.0:
        raise ValueError("Start vector must be non-zero.")
    vec = vec / nrm
    return vec, {"start_source": source, "start_seed": seed_used, "start_norm_before": nrm}


def _canonicalize_in_span_shift(
    Q: np.ndarray,
    m: int,
    *,
    shift_apply: Any | None = None,
    shift_matrix: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    r = int(Q.shape[1])
    if r < int(m):
        raise ValueError("Krylov rank must satisfy rank >= m for shift canonicalization.")
    if shift_apply is None and shift_matrix is None:
        raise ValueError("shift proxy is required for method='krylov_shift_canonical'.")
    if shift_apply is not None and shift_matrix is not None:
        raise ValueError("Provide at most one of shift_apply or shift_matrix.")

    if shift_apply is not None:
        SQ = np.asarray(shift_apply(Q))
        if SQ.shape != Q.shape:
            raise ValueError("shift_apply(Q) must preserve Q shape.")
        M = Q.conj().T @ SQ
    else:
        S = np.asarray(shift_matrix)
        if S.ndim != 2 or S.shape != (Q.shape[0], Q.shape[0]):
            raise ValueError("shift_matrix must have shape (ambient_dim, ambient_dim).")
        M = Q.conj().T @ (S @ Q)

    MtM = M.conj().T @ M
    evals, V = np.linalg.eigh(MtM)
    order = np.argsort(-evals, kind="mergesort")
    keep = order[: int(m)]
    U = Q @ V[:, keep]
    U, _ = np.linalg.qr(U)
    top = np.real(evals[keep])
    summary = {
        "shift_compat_top_eigs": [float(x) for x in top.tolist()],
        "shift_compat_mean_top": float(np.mean(top)),
        "shift_compat_min_top": float(np.min(top)),
        "shift_compat_max_top": float(np.max(top)),
    }
    return U[:, : int(m)], summary


def krylov_basis(A: np.ndarray, v: np.ndarray, k: int, tol: float = 1e-12) -> np.ndarray:
    """Return an orthonormal Krylov basis for span{v, Av, ..., A^{k-1}v}."""

    mat = _validate_square(A)
    vec = np.asarray(v).reshape(-1)
    N = mat.shape[0]
    if vec.size != N:
        raise ValueError("v must have length N.")
    if int(k) < 1:
        raise ValueError("k must be >= 1.")
    if float(tol) < 0.0:
        raise ValueError("tol must be non-negative.")
    if np.linalg.norm(vec) <= 0.0:
        raise ValueError("v must be non-zero.")

    K = _krylov_matrix(mat, vec, int(k))
    Q_cols: list[np.ndarray] = []
    for t in range(K.shape[1]):
        w = K[:, t].astype(np.result_type(K, np.float64), copy=True)
        for q in Q_cols:
            w = w - q * np.vdot(q, w)
        nrm = float(np.linalg.norm(w))
        if nrm > float(tol):
            Q_cols.append(w / nrm)

    if len(Q_cols) == 0:
        raise ValueError("Krylov basis rank is zero under given tolerance.")
    return np.column_stack(Q_cols)


def pkg_krylov(
    A: np.ndarray,
    m: int,
    k: int,
    *,
    v: np.ndarray | None = None,
    v_seed: int | None = None,
    method: str = "krylov_naive",
    shift_apply: Any | None = None,
    shift_matrix: np.ndarray | None = None,
    tol: float = 1e-12,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Krylov packaging: build k-step Krylov matrix and compress to m via SVD."""

    mat = _validate_square(A)
    N = mat.shape[0]
    if int(m) < 1 or int(m) > N:
        raise ValueError("m must satisfy 1 <= m <= N.")
    if int(k) < int(m):
        raise ValueError("k must be >= m.")

    v0, start_meta = _resolve_start_vector(mat, v=v, v_seed=v_seed)

    if method not in {"krylov_naive", "krylov_shift_canonical"}:
        raise ValueError("method must be one of {'krylov_naive', 'krylov_shift_canonical'}.")

    K = _krylov_matrix(mat, v0, int(k))
    Q = krylov_basis(mat, v0, int(k), tol=tol)  # stable orthonormal basis for Krylov span
    rank = int(Q.shape[1])
    m_eff = int(min(int(m), rank))

    shift_summary: dict[str, Any] = {}
    if method == "krylov_naive":
        B = Q.conj().T @ K  # reduced coordinates; left singular vectors lift via Q
        W, svals, _ = np.linalg.svd(B, full_matrices=False)
        U_core = Q @ W[:, :m_eff]
        if m_eff < int(m):
            completed = True
            completion_dim = int(m) - m_eff
            I = np.eye(N, dtype=U_core.dtype)
            cand = np.concatenate([U_core, I], axis=1)
            U_full, _ = np.linalg.qr(cand)
            U_m = U_full[:, : int(m)]
        else:
            completed = False
            completion_dim = 0
            U_m = U_core
        energy = float(np.sum(svals[:m_eff] ** 2) / (np.sum(svals**2) + 1e-18))
    else:
        U_core, shift_summary = _canonicalize_in_span_shift(
            Q,
            int(m_eff),
            shift_apply=shift_apply,
            shift_matrix=shift_matrix,
        )
        if m_eff < int(m):
            completed = True
            completion_dim = int(m) - m_eff
            I = np.eye(N, dtype=U_core.dtype)
            cand = np.concatenate([U_core, I], axis=1)
            U_full, _ = np.linalg.qr(cand)
            U_m = U_full[:, : int(m)]
        else:
            completed = False
            completion_dim = 0
            U_m = U_core
        energy = float(np.sum(np.asarray(shift_summary["shift_compat_top_eigs"], dtype=float)) / max(1, m_eff))

    # Numerical cleanup for MGS drift / near-rank-deficient cases.
    U_qr, _ = np.linalg.qr(U_m)
    U_m = U_qr[:, : int(m)]
    G = U_m.conj().T @ U_m
    if not np.allclose(G, np.eye(int(m), dtype=G.dtype), atol=1e-8, rtol=0.0):
        raise ValueError("pkg_krylov produced non-orthonormal columns.")

    summary = {
        "k": int(k),
        "m": int(m),
        "method": method,
        "rank_krylov": int(rank),
        "explained_energy": float(energy),
        "completed": bool(completed),
        "completion_dim": int(completion_dim),
        "start_vector": v0.copy(),
    }
    summary.update(start_meta)
    summary.update(shift_summary)
    return U_m, summary


def pkg_krylov_sequential(
    A: np.ndarray,
    m2: int,
    k2: int,
    m1: int,
    k1: int,
    *,
    v: np.ndarray | None = None,
    v_seed: int | None = None,
    init_mode: str = "projected_v",
    method: str = "krylov_naive",
    tol: float = 1e-12,
) -> tuple[np.ndarray, np.ndarray, float, dict[str, Any]]:
    """Direct vs sequential Krylov packaging and projector mismatch."""

    mat = _validate_square(A)
    if int(m2) < int(m1):
        raise ValueError("m2 must be >= m1.")
    if init_mode not in {"projected_v", "independent_seed"}:
        raise ValueError("init_mode must be one of {'projected_v', 'independent_seed'}.")
    if method not in {"krylov_naive", "krylov_shift_canonical"}:
        raise ValueError("method must be one of {'krylov_naive', 'krylov_shift_canonical'}.")

    vN, start_meta = _resolve_start_vector(mat, v=v, v_seed=v_seed)
    shift_apply = lambda X: np.roll(X, 1, axis=0)

    U2, s2 = pkg_krylov(
        mat,
        m=int(m2),
        k=int(k2),
        v=vN,
        method=method,
        shift_apply=shift_apply if method == "krylov_shift_canonical" else None,
        tol=tol,
    )
    B = U2.conj().T @ mat @ U2

    U_direct, s_direct = pkg_krylov(
        mat,
        m=int(m1),
        k=int(k1),
        v=vN,
        method=method,
        shift_apply=shift_apply if method == "krylov_shift_canonical" else None,
        tol=tol,
    )

    projected_v_was_zero = False
    if init_mode == "projected_v":
        v_red = U2.conj().T @ vN
        red_norm = float(np.linalg.norm(v_red))
        if red_norm <= float(tol):
            projected_v_was_zero = True
            v_red = np.zeros(U2.shape[1], dtype=np.result_type(B, np.float64))
            v_red[0] = 1.0
        else:
            v_red = v_red / red_norm
        S2 = U2.conj().T @ shift_apply(U2)
        V_seq, s_seq = pkg_krylov(
            B,
            m=int(m1),
            k=int(k1),
            v=v_red,
            method=method,
            shift_matrix=S2 if method == "krylov_shift_canonical" else None,
            tol=tol,
        )
        reduced_start_source = "projected_v"
        reduced_start_seed = None
    else:
        if v_seed is None:
            raise ValueError("v_seed is required for init_mode='independent_seed'.")
        reduced_seed = int(v_seed) + 100_003
        S2 = U2.conj().T @ shift_apply(U2)
        V_seq, s_seq = pkg_krylov(
            B,
            m=int(m1),
            k=int(k1),
            v_seed=reduced_seed,
            method=method,
            shift_matrix=S2 if method == "krylov_shift_canonical" else None,
            tol=tol,
        )
        reduced_start_source = "independent_seed"
        reduced_start_seed = reduced_seed

    U_seq = U2 @ V_seq

    mismatch = float(projector_mismatch_fro(U_seq, U_direct))
    summaries: dict[str, Any] = {
        "stage_m2": s2,
        "direct": s_direct,
        "seq_reduced": s_seq,
        "method": method,
        "init_mode": init_mode,
        "start_vector": vN.copy(),
        "start_source": start_meta["start_source"],
        "start_seed": start_meta["start_seed"],
        "reduced_start_source": reduced_start_source,
        "reduced_start_seed": reduced_start_seed,
        "projected_v_was_zero": bool(projected_v_was_zero),
    }
    return U_seq, U_direct, mismatch, summaries
