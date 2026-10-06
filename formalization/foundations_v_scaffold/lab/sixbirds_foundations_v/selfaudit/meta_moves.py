from __future__ import annotations

import numpy as np

from .diagnostics import mutual_coherence, near_duplicate_pairs, normalize_columns


def _normalize_columns_with_report(D: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array.")
    norms = np.linalg.norm(mat, axis=0)
    out = mat.astype(np.complex128, copy=True)
    nz = norms > 0.0
    out[:, nz] = out[:, nz] / norms[nz]
    return out, norms


def _fourier_basis(N: int, freqs: list[int]) -> np.ndarray:
    n = np.arange(N, dtype=float)
    basis = np.empty((N, len(freqs)), dtype=np.complex128)
    scale = 1.0 / np.sqrt(float(N))
    for col, k in enumerate(freqs):
        basis[:, col] = np.exp((2.0j * np.pi * float(k) * n) / float(N)) * scale
    return basis


def _orthonormal_completion(U: np.ndarray, m: int) -> np.ndarray:
    N = U.shape[0]
    if U.shape[1] >= m:
        return U[:, :m]
    freqs = list(range(N))
    F = _fourier_basis(N, freqs)
    cand = np.concatenate([U, F], axis=1)
    Q, _ = np.linalg.qr(cand)
    return Q[:, :m]


def symmetrize_subspace_via_projector(
    Psi: np.ndarray,
    m: int,
    group: str = "shifts",
    shifts: list[int] | None = None,
    method: str = "auto",
) -> tuple[np.ndarray, dict]:
    """Experimental P4/P1-like symmetry move via group-adapted subspace rewrite.

    This is an experimental operator (not a commitment): it rewrites a subspace into
    a symmetry-adapted basis for easier reflexive closure checks and re-auditing.
    """

    psi = np.asarray(Psi)
    if psi.ndim != 2:
        raise ValueError("Psi must be a 2D array with shape (N, m0).")
    N, m0 = psi.shape
    if N < 1:
        raise ValueError("Psi must have N >= 1.")
    if m0 < 1:
        raise ValueError("Psi must have at least one column.")
    if m < 1:
        raise ValueError("m must be >= 1.")
    if m > N:
        raise ValueError("m must satisfy m <= N.")
    if group != "shifts":
        raise ValueError("Only group='shifts' is supported.")

    use_method = method
    if method == "auto":
        use_method = "finite_shifts_svd" if (shifts is not None and len(shifts) > 0) else "fft_full_shifts"

    if use_method == "fft_full_shifts":
        F = np.fft.fft(psi, axis=0)
        weights = np.sum(np.abs(F) ** 2, axis=1) / float(N)
        order = np.lexsort((np.arange(N), -weights))
        selected = order[:m].tolist()
        Psi_sym = _fourier_basis(N, selected)
        summary = {
            "method": "fft_full_shifts",
            "selected_freqs": [int(k) for k in selected],
            "weights_selected_sum": float(np.sum(weights[selected])),
            "weights_total_sum": float(np.sum(weights)),
        }
    elif use_method == "finite_shifts_svd":
        if shifts is None or len(shifts) == 0:
            shifts = [0]
        unique_shifts = []
        seen = set()
        for s in shifts:
            ss = int(s)
            if ss not in seen:
                seen.add(ss)
                unique_shifts.append(ss)
        K = len(unique_shifts)
        B = np.concatenate([np.roll(psi, shift=s, axis=0) for s in unique_shifts], axis=1) / np.sqrt(float(K))
        U, _, _ = np.linalg.svd(B, full_matrices=False)
        Psi_sym = _orthonormal_completion(U, m)
        summary = {
            "method": "finite_shifts_svd",
            "selected_freqs": [],
            "weights_selected_sum": float("nan"),
            "weights_total_sum": float("nan"),
            "num_shifts": int(K),
        }
    else:
        raise ValueError(f"Unsupported method: {method}")

    overlap_fro2 = float(np.linalg.norm(psi.conj().T @ Psi_sym, ord="fro") ** 2 / float(m))
    summary["overlap_fro2"] = overlap_fro2
    return Psi_sym, summary


def canonicalize_dictionary(
    D: np.ndarray,
    near_dup_threshold: float = 0.99,
) -> tuple[np.ndarray, dict]:
    """Experimental P5-like dictionary canonicalization and structural reporting.

    This is an experimental operator (not a commitment): it normalizes and reports
    structural/coherence diagnostics without deleting columns.
    """

    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array.")
    if near_dup_threshold < 0.0 or near_dup_threshold > 1.0:
        raise ValueError("near_dup_threshold must be in [0, 1].")

    N, M = mat.shape
    D_canon, norms = _normalize_columns_with_report(mat)
    num_zero = int(np.sum(norms == 0.0))

    mu_before = float(mutual_coherence(mat))
    mu_after = float(mutual_coherence(D_canon))

    Gabs = np.abs(D_canon.conj().T @ D_canon)
    np.fill_diagonal(Gabs, 0.0)
    pair_mask = Gabs >= float(near_dup_threshold)
    num_pairs = int(np.sum(np.triu(pair_mask, k=1)))

    parent = list(range(M))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra = find(a)
        rb = find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    for i in range(M):
        for j in range(i + 1, M):
            if pair_mask[i, j]:
                union(i, j)

    comp_sizes: dict[int, int] = {}
    for i in range(M):
        r = find(i)
        comp_sizes[r] = comp_sizes.get(r, 0) + 1
    near_sizes = [s for s in comp_sizes.values() if s >= 2]

    summary = {
        "N": int(N),
        "M": int(M),
        "norm_min": float(np.min(norms) if norms.size else 0.0),
        "norm_max": float(np.max(norms) if norms.size else 0.0),
        "num_zero_cols": int(num_zero),
        "mu_before": mu_before,
        "mu_after": mu_after,
        "near_dup_threshold": float(near_dup_threshold),
        "near_dup_num_pairs": int(num_pairs),
        "near_dup_num_clusters": int(len(near_sizes)),
        "near_dup_max_cluster_size": int(max(near_sizes) if near_sizes else 0),
    }
    return D_canon, summary


def gate_coherent_pairs(
    D: np.ndarray,
    mu_target: float,
) -> tuple[np.ndarray, dict]:
    """Experimental P2-like coherence gate by greedy pair removal.

    This is an experimental operator (not a commitment): it greedily drops columns
    to force max coherence below a target and reports every dropped index.
    """

    if mu_target < 0.0:
        raise ValueError("mu_target must be >= 0.")

    D_canon, canon_summary = canonicalize_dictionary(D)
    _, M = D_canon.shape

    kept_indices = list(range(M))
    dropped_indices: list[int] = []
    current = D_canon

    mu_before = float(mutual_coherence(current)) if current.shape[1] >= 2 else 0.0
    mu_current = mu_before

    while current.shape[1] >= 2 and mu_current > mu_target:
        G = np.abs(current.conj().T @ current)
        np.fill_diagonal(G, 0.0)
        flat_idx = int(np.argmax(G))
        i, j = np.unravel_index(flat_idx, G.shape)
        if i == j:
            break
        drop_local = max(i, j)  # deterministic choice
        drop_global = kept_indices[drop_local]
        dropped_indices.append(int(drop_global))

        keep_mask = np.ones(current.shape[1], dtype=bool)
        keep_mask[drop_local] = False
        current = current[:, keep_mask]
        kept_indices = [idx for t, idx in enumerate(kept_indices) if keep_mask[t]]
        mu_current = float(mutual_coherence(current)) if current.shape[1] >= 2 else 0.0

    summary = {
        "mu_before": float(mu_before),
        "mu_after": float(mu_current),
        "mu_target": float(mu_target),
        "kept_indices": [int(i) for i in kept_indices],
        "dropped_indices": [int(i) for i in dropped_indices],
        "num_dropped": int(len(dropped_indices)),
        "canonical_summary": canon_summary,
    }
    return current, summary


def merge_routes_into_artifact(
    Psi_seq: np.ndarray,
    Psi_direct: np.ndarray,
    mismatch_scalar: float | None = None,
) -> dict:
    """Experimental P3-like route integration move into a single auditable artifact.

    This is an experimental operator (not a commitment): it packages both routes
    together (no information dropped) and reports cross-route alignment stats.
    """

    seq = np.asarray(Psi_seq)
    direct = np.asarray(Psi_direct)
    if seq.ndim != 2 or direct.ndim != 2:
        raise ValueError("Psi_seq and Psi_direct must be 2D arrays.")
    if seq.shape[0] != direct.shape[0]:
        raise ValueError("Psi_seq and Psi_direct must have the same N.")

    N = int(seq.shape[0])
    rank_seq = int(seq.shape[1])
    m_direct = int(direct.shape[1])

    if rank_seq == 0 or m_direct == 0:
        max_cross = float("nan")
        i_star = -1
        j_star = -1
        dot_abs = float("nan")
    else:
        C = seq.conj().T @ direct
        abs_C = np.abs(C)
        flat_idx = int(np.argmax(abs_C))
        i_star, j_star = np.unravel_index(flat_idx, abs_C.shape)
        dot_abs = float(abs_C[i_star, j_star])
        max_cross = dot_abs

    artifact = {
        "artifact_type": "routes_merged",
        "N": N,
        "Psi_seq": seq,
        "Psi_direct": direct,
        "D": np.concatenate([seq, direct], axis=1),
        "route_mismatch": mismatch_scalar,
        "rank_seq": rank_seq,
        "m_direct": m_direct,
        "summary": {
            "max_cross_coherence": float(max_cross),
            "best_i": int(i_star),
            "best_j": int(j_star),
            "best_dot_abs": float(dot_abs),
        },
    }
    return artifact


def split_near_duplicate_pairs(
    D: np.ndarray,
    thresh: float = 0.99,
    max_pairs: int = 50,
    mode: str = "replace",
    eps: float = 1e-12,
) -> tuple[np.ndarray, dict]:
    """Experimental P5-analogue replacement of near-duplicate channels by sum/diff modes.

    This is an experimental operator (not a commitment): it is designed to test
    whether hidden cancellation needles become explicit channels after repackaging.
    """

    if mode != "replace":
        raise ValueError("Only mode='replace' is supported.")
    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array.")
    if not (0.0 <= float(thresh) <= 1.0):
        raise ValueError("thresh must be in [0, 1].")
    if int(max_pairs) < 0:
        raise ValueError("max_pairs must be >= 0.")
    if float(eps) <= 0.0:
        raise ValueError("eps must be > 0.")

    N, M = mat.shape
    Dn, _, zero_mask = normalize_columns(mat, eps=float(eps))
    Gabs = np.abs(Dn.conj().T @ Dn)
    np.fill_diagonal(Gabs, 0.0)

    iu, ju = np.triu_indices(M, k=1)
    vals = Gabs[iu, ju]
    valid = (~zero_mask[iu]) & (~zero_mask[ju])
    candidates = np.where(valid & (vals >= float(thresh)))[0]
    cand_sorted = sorted(
        candidates.tolist(),
        key=lambda t: (-float(vals[t]), int(iu[t]), int(ju[t])),
    )

    selected: list[tuple[int, int, float]] = []
    used: set[int] = set()
    for t in cand_sorted:
        i = int(iu[t])
        j = int(ju[t])
        if i in used or j in used:
            continue
        selected.append((i, j, float(vals[t])))
        used.add(i)
        used.add(j)
        if len(selected) >= int(max_pairs):
            break

    dropped_indices = sorted(int(x) for x in used)
    kept_indices = [idx for idx in range(M) if idx not in used]
    new_cols: list[np.ndarray] = []
    pair_logs: list[dict[str, object]] = []

    for i, j, abs_dot in selected:
        u = Dn[:, i]
        v = Dn[:, j]
        dot = np.vdot(u, v)
        dot_abs = float(np.abs(dot))
        phase = dot / dot_abs if dot_abs > 0.0 else (1.0 + 0.0j)
        v_aligned = phase * v

        sum_vec = u + v_aligned
        diff_vec = u - v_aligned
        sum_norm = float(np.linalg.norm(sum_vec))
        diff_norm = float(np.linalg.norm(diff_vec))

        kept_sum = bool(sum_norm >= float(eps))
        kept_diff = bool(diff_norm >= float(eps))
        if kept_sum:
            new_cols.append(sum_vec / sum_norm)
        if kept_diff:
            new_cols.append(diff_vec / diff_norm)

        pair_logs.append(
            {
                "i": int(i),
                "j": int(j),
                "abs_dot": float(abs_dot),
                "dot": str(complex(dot)),
                "phase": str(complex(phase)),
                "kept_sum": kept_sum,
                "kept_diff": kept_diff,
                "sum_norm": float(sum_norm),
                "diff_norm": float(diff_norm),
            }
        )

    D_kept = Dn[:, kept_indices] if kept_indices else np.zeros((N, 0), dtype=Dn.dtype)
    D_new = np.concatenate([D_kept, np.column_stack(new_cols)], axis=1) if new_cols else D_kept

    summary: dict[str, object] = {
        "thresh": float(thresh),
        "max_pairs": int(max_pairs),
        "mode": str(mode),
        "eps": float(eps),
        "M_before": int(M),
        "M_after": int(D_new.shape[1]),
        "num_pairs_found": int(candidates.size),
        "num_pairs_used": int(len(selected)),
        "pairs_used": pair_logs,
        "dropped_indices": dropped_indices,
        "mu_before": float(mutual_coherence(Dn)),
        "mu_after": float(mutual_coherence(D_new)),
    }
    for tval, suffix in ((0.95, "095"), (0.98, "098"), (0.99, "099")):
        summary[f"num_pairs_ge_{suffix}_before"] = int(len(near_duplicate_pairs(Dn, thresh=tval)))
        summary[f"num_pairs_ge_{suffix}_after"] = int(len(near_duplicate_pairs(D_new, thresh=tval)))

    return D_new, summary
