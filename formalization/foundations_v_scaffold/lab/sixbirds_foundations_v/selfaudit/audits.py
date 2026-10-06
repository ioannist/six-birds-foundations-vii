from __future__ import annotations

import numpy as np

from ._support.dict_l2_opt import loc_j
from ._support.dict_metrics import dictionary_metrics
from ._support.invariance import diag_stats, projector_diag_from_basis, subspace_shift_residual_score
from ._support.localization import b_j_per_channel, eta_j_from_basis, make_cells_1d, trace_bound_eta


def _tau_to_key(tau: float) -> str:
    s = f"{tau:.0e}"
    s = s.replace("e-0", "e-").replace("e+0", "e+").replace("e+", "e")
    return s


def _eta_maximizer_vector(Psi: np.ndarray, cells: list[np.ndarray]) -> tuple[np.ndarray, float]:
    psi = np.asarray(Psi)
    best_eta = -np.inf
    best_a = None
    for cell in cells:
        psi_B = psi[cell, :]
        _, svals, Vh = np.linalg.svd(psi_B, full_matrices=False)
        eta_B = float(svals[0] ** 2) if svals.size else 0.0
        if eta_B > best_eta:
            best_eta = eta_B
            best_a = Vh[0].conj() if Vh.size else np.zeros(psi.shape[1], dtype=psi.dtype)
    if best_a is None:
        raise ValueError("Could not compute eta maximizer vector.")
    v_star = psi @ best_a
    return v_star, float(best_eta)


def audit_subspace(
    Psi: np.ndarray,
    N: int,
    j_list: list[int],
    shift_list: list[int],
    orbit_tau_list: tuple[float, ...] = (1e-2, 1e-3),
    orbit_k_cap: int = 128,
) -> dict[str, float | int | str | bool]:
    psi = np.asarray(Psi)
    if psi.ndim != 2:
        raise ValueError("Psi must be a 2D array with shape (N, m).")
    if psi.shape[0] != N:
        raise ValueError("Provided N does not match Psi.shape[0].")
    if len(j_list) == 0:
        raise ValueError("j_list must be non-empty.")
    if len(shift_list) == 0:
        raise ValueError("shift_list must be non-empty.")

    m = int(psi.shape[1])
    out: dict[str, float | int | str | bool] = {
        "artifact_type": "subspace",
        "N": int(N),
        "m": int(m),
    }

    diagP = projector_diag_from_basis(psi)
    dstats = diag_stats(diagP)
    out["sym_diag_mean"] = float(dstats["diag_mean"])
    out["sym_diag_std"] = float(dstats["diag_std"])
    out["sym_diag_min"] = float(dstats["diag_min"])
    out["sym_diag_max"] = float(dstats["diag_max"])
    out["sym_diag_cv"] = float(dstats.get("diag_cv", np.nan))

    for shift in shift_list:
        out[f"sym_inv_score_s{int(shift)}"] = float(subspace_shift_residual_score(psi, int(shift)))

    for j in j_list:
        jj = int(j)
        cells = make_cells_1d(N, jj)
        eta = float(eta_j_from_basis(psi, cells, check_orthonormal=False))
        trace = float(trace_bound_eta(psi, cells, check_orthonormal=False))
        b = b_j_per_channel(psi, cells, check_orthonormal=False)
        ratio = float(eta / trace) if trace != 0.0 else float("nan")
        theory = float(m / (2**jj))
        trace_ratio = float(trace / theory) if theory != 0.0 else float("nan")
        trace_ratio_err = float(abs(trace_ratio - 1.0)) if np.isfinite(trace_ratio) else float("nan")

        out[f"loc_eta_j{jj}"] = eta
        out[f"loc_trace_bound_j{jj}"] = trace
        out[f"loc_eta_over_trace_j{jj}"] = ratio
        out[f"loc_b_mean_j{jj}"] = float(np.mean(b))
        out[f"loc_b_max_j{jj}"] = float(np.max(b))

        out[f"sym_trace_theory_j{jj}"] = theory
        out[f"sym_trace_ratio_j{jj}"] = trace_ratio
        out[f"sym_trace_ratio_err_j{jj}"] = trace_ratio_err

        v_star, _ = _eta_maximizer_vector(psi, cells)
        L = 2**jj
        step = int(N // L)
        k = int(min(L, orbit_k_cap))
        V = np.column_stack([np.roll(v_star, shift=t * step) for t in range(k)])
        G = V.conj().T @ V
        evals = np.linalg.eigvalsh(G)
        eig_max = float(np.real(evals[-1])) if evals.size > 0 else 0.0

        out[f"orbit_step_j{jj}"] = step
        out[f"orbit_k_j{jj}"] = k
        for tau_rel in orbit_tau_list:
            tau_key = _tau_to_key(float(tau_rel))
            threshold = float(tau_rel) * eig_max
            eff_rank = int(np.sum(evals > threshold))
            out[f"orbit_eff_rank_rel_{tau_key}_j{jj}"] = eff_rank

    return out


def audit_dictionary(
    D: np.ndarray,
    N: int,
    j_list: list[int],
    constraint_specs: list[dict[str, object]],
) -> dict[str, float | int | str | bool]:
    mat = np.asarray(D)
    if mat.ndim != 2:
        raise ValueError("D must be a 2D array with shape (N, M).")
    if mat.shape[0] != N:
        raise ValueError("Provided N does not match D.shape[0].")
    if len(j_list) == 0:
        raise ValueError("j_list must be non-empty.")

    M = int(mat.shape[1])
    out: dict[str, float | int | str | bool] = {
        "artifact_type": "dictionary",
        "N": int(N),
        "M": int(M),
    }

    dmetrics = dictionary_metrics(mat)
    out["dict_mu"] = float(dmetrics["mu"])
    out["dict_mean_abs_offdiag"] = float(dmetrics["mean_abs_offdiag"])
    out["dict_gram_top_eig"] = float(dmetrics["gram_top_eig"])
    out["dict_cond_proxy"] = float(dmetrics["cond_proxy"])
    out["dict_stable_rank"] = float(dmetrics["stable_rank"])

    cells_cache = {int(j): make_cells_1d(N, int(j)) for j in j_list}
    for j in j_list:
        jj = int(j)
        locs = np.array([loc_j(mat[:, i], cells_cache[jj]) for i in range(M)], dtype=float)
        out[f"loc_max_atom_loc_j{jj}"] = float(np.max(locs))
        out[f"loc_mean_atom_loc_j{jj}"] = float(np.mean(locs))

    for spec in constraint_specs:
        kind = spec.get("kind")
        if kind == "paired_diff":
            pair_offset_obj = spec.get("pair_offset", "half")
            if pair_offset_obj == "half":
                pair_offset = M // 2
            else:
                pair_offset = int(pair_offset_obj)
            if pair_offset <= 0 or 2 * pair_offset > M:
                raise ValueError("paired_diff requires pair_offset > 0 and 2*pair_offset <= M.")

            for j in j_list:
                jj = int(j)
                best = -np.inf
                for i in range(pair_offset):
                    d_i = mat[:, i]
                    d_j = mat[:, i + pair_offset]
                    dot = np.vdot(d_i, d_j)
                    dot_abs = float(np.abs(dot))
                    phase = dot / dot_abs if dot_abs > 0.0 else (1.0 + 0.0j)
                    v_raw = d_i - phase * d_j
                    v_norm = float(np.linalg.norm(v_raw))
                    if v_norm < 1e-12:
                        continue
                    val = float(loc_j(v_raw / v_norm, cells_cache[jj]))
                    if val > best:
                        best = val
                eta_hat = float(best) if np.isfinite(best) else float("nan")
                out[f"cancel_eta_hat_paired_diff_j{jj}"] = eta_hat
                out[f"cancel_gain_paired_diff_j{jj}"] = float(
                    eta_hat - float(out[f"loc_max_atom_loc_j{jj}"])
                )
        elif kind == "sparse_random":
            s = int(spec["s"])
            num_samples = int(spec["num_samples"])
            seed = int(spec["seed"])
            if s < 1 or s > M:
                raise ValueError("sparse_random requires 1 <= s <= M.")
            if num_samples < 1:
                raise ValueError("sparse_random requires num_samples >= 1.")

            rng = np.random.default_rng(seed)
            max_vals = {int(j): -np.inf for j in j_list}
            for _ in range(num_samples):
                idx = rng.choice(M, size=s, replace=False)
                signs = rng.choice(np.array([-1.0, 1.0]), size=s) / np.sqrt(float(s))
                v = mat[:, idx] @ signs
                for j in j_list:
                    jj = int(j)
                    val = float(loc_j(v, cells_cache[jj]))
                    if val > max_vals[jj]:
                        max_vals[jj] = val
            for j in j_list:
                jj = int(j)
                out[f"cancel_eta_hat_sparse_random_s{s}_j{jj}"] = float(max_vals[jj])
        else:
            raise ValueError(f"Unknown constraint spec kind: {kind}")

    return out


def audit_routes(
    Psi_seq: np.ndarray,
    Psi_direct: np.ndarray,
    mismatch_scalar: float,
    N: int,
    j_list: list[int],
) -> dict[str, float | int | str | bool]:
    seq = np.asarray(Psi_seq)
    direct = np.asarray(Psi_direct)
    if seq.ndim != 2 or direct.ndim != 2:
        raise ValueError("Psi_seq and Psi_direct must be 2D arrays.")
    if seq.shape[0] != N or direct.shape[0] != N:
        raise ValueError("Provided N must match row count of both inputs.")
    if len(j_list) == 0:
        raise ValueError("j_list must be non-empty.")

    rank_seq = int(seq.shape[1])
    m_direct = int(direct.shape[1])
    out: dict[str, float | int | str | bool] = {
        "artifact_type": "routes",
        "N": int(N),
        "rank_seq": rank_seq,
        "m_direct": m_direct,
        "route_mismatch": float(mismatch_scalar),
    }

    if rank_seq < 1 or m_direct < 1:
        out["cancel_max_cross_coherence"] = float("nan")
        out["cancel_best_i"] = -1
        out["cancel_best_j"] = -1
        out["cancel_best_dot_abs"] = float("nan")
        out["cancel_diff_norm"] = float("nan")
        for j in j_list:
            jj = int(j)
            out[f"loc_seq_best_j{jj}"] = float("nan")
            out[f"loc_direct_best_j{jj}"] = float("nan")
            out[f"cancel_loc_best_diff_j{jj}"] = float("nan")
            out[f"cancel_gain_best_diff_j{jj}"] = float("nan")
            out[f"cancel_gain_rel_best_diff_j{jj}"] = float("nan")
        return out

    C = seq.conj().T @ direct
    abs_C = np.abs(C)
    flat_idx = int(np.argmax(abs_C))
    i_star, j_star = np.unravel_index(flat_idx, abs_C.shape)
    dot = complex(C[i_star, j_star])
    dot_abs = float(np.abs(dot))
    phase = dot / dot_abs if dot_abs > 0.0 else (1.0 + 0.0j)

    u_seq = seq[:, i_star]
    u_direct = direct[:, j_star]
    v_raw = u_seq - phase * u_direct
    diff_norm = float(np.linalg.norm(v_raw))
    v = None if diff_norm < 1e-12 else (v_raw / diff_norm)

    out["cancel_max_cross_coherence"] = dot_abs
    out["cancel_best_i"] = int(i_star)
    out["cancel_best_j"] = int(j_star)
    out["cancel_best_dot_abs"] = dot_abs
    out["cancel_diff_norm"] = diff_norm

    for j in j_list:
        jj = int(j)
        cells = make_cells_1d(N, jj)
        loc_seq_val = float(loc_j(u_seq, cells))
        loc_direct_val = float(loc_j(u_direct, cells))
        if v is None:
            loc_diff = float("nan")
            gain = float("nan")
            gain_rel = float("nan")
        else:
            loc_diff = float(loc_j(v, cells))
            base = max(loc_seq_val, loc_direct_val)
            gain = float(loc_diff - base)
            gain_rel = float(loc_diff / (base + 1e-18))

        out[f"loc_seq_best_j{jj}"] = loc_seq_val
        out[f"loc_direct_best_j{jj}"] = loc_direct_val
        out[f"cancel_loc_best_diff_j{jj}"] = loc_diff
        out[f"cancel_gain_best_diff_j{jj}"] = gain
        out[f"cancel_gain_rel_best_diff_j{jj}"] = gain_rel

    return out
