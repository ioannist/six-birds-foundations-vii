from __future__ import annotations

import math
from typing import Any


def _available_js(audit_row: dict[str, Any], prefix: str) -> list[int]:
    js: set[int] = set()
    for key in audit_row:
        if not key.startswith(prefix):
            continue
        suffix = key[len(prefix) :]
        if suffix.isdigit():
            js.add(int(suffix))
    return sorted(js)


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


def _log_violation(x: float, ref: float) -> float:
    return float(math.log10(1.0 + max(x, 0.0) / max(ref, 1e-18)))


def compute_sym_score(audit_row: dict, thresholds: dict, shift: int = 1) -> dict:
    """Returns flat SymScore terms (experimental RS7 aggregate)."""
    inv_key = f"sym_inv_score_s{int(shift)}"
    inv = _safe_float(audit_row.get(inv_key, 0.0), default=0.0)
    diag = _safe_float(audit_row.get("sym_diag_std", 0.0), default=0.0)

    js_err = _available_js(audit_row, "sym_trace_ratio_err_j")
    js_ratio = _available_js(audit_row, "sym_trace_ratio_j")
    trace_err = 0.0
    j_used = -1
    if js_err:
        j_used = max(js_err)
        trace_err = _safe_float(audit_row.get(f"sym_trace_ratio_err_j{j_used}", 0.0), default=0.0)
    elif js_ratio:
        j_used = max(js_ratio)
        ratio = _safe_float(audit_row.get(f"sym_trace_ratio_j{j_used}", 1.0), default=1.0)
        trace_err = abs(ratio - 1.0)

    sym_th = thresholds["symmetry"]
    inv_ref = _safe_float(sym_th.get("inv_score_max", 1e-6), default=1e-6)
    diag_ref = _safe_float(sym_th.get("diag_std_max", 1e-6), default=1e-6)
    trace_ref = _safe_float(sym_th.get("trace_ratio_err_max", 1e-6), default=1e-6)

    t_inv = _log_violation(inv, inv_ref)
    t_diag = _log_violation(diag, diag_ref)
    t_trace = _log_violation(trace_err, trace_ref)
    sym_score = t_inv + t_diag + t_trace

    return {
        "sym_inv": float(inv),
        "sym_diag_std": float(diag),
        "sym_trace_ratio_err": float(trace_err),
        "sym_j_used": int(j_used),
        "sym_t_inv": float(t_inv),
        "sym_t_diag": float(t_diag),
        "sym_t_trace": float(t_trace),
        "SymScore": float(sym_score),
    }


def compute_cancel_score(audit_row: dict, thresholds: dict) -> dict:
    """Returns flat CancelScore terms (experimental RS7 aggregate)."""
    feas_th = thresholds["feasibility"]
    eps = _safe_float(feas_th.get("eps", 1e-18), default=1e-18)
    gain_ref = _safe_float(feas_th.get("gain_rel_max", 1.25), default=1.25) - 1.0
    gain_ref = max(gain_ref, 1e-18)

    gain_rel = float("nan")
    j_used = -1

    metric_gain = _safe_float(audit_row.get("metric_gain_rel", float("nan")), default=float("nan"))
    if not math.isnan(metric_gain):
        gain_rel = float(metric_gain)
    else:
        js_route = _available_js(audit_row, "cancel_gain_rel_best_diff_j")
        if js_route:
            j_used = max(js_route)
            gain_rel = _safe_float(audit_row.get(f"cancel_gain_rel_best_diff_j{j_used}", 1.0), default=1.0)
        else:
            js_dict = _available_js(audit_row, "cancel_eta_hat_paired_diff_j")
            if js_dict:
                j_used = max(js_dict)
                eta_hat = _safe_float(audit_row.get(f"cancel_eta_hat_paired_diff_j{j_used}", 1.0), default=1.0)
                atom = _safe_float(audit_row.get(f"loc_max_atom_loc_j{j_used}", 1.0), default=1.0)
                gain_rel = float(eta_hat / (atom + eps))
            else:
                gain_rel = 1.0

    gain_excess = max(gain_rel - 1.0, 0.0)
    t_gain = float(math.log10(1.0 + gain_excess / (gain_ref + 1e-18)))

    p95 = _safe_float(audit_row.get("cancel_gain_rel_p95", float("nan")), default=float("nan"))
    if math.isnan(p95):
        t_p95 = 0.0
    else:
        p95_excess = max(p95 - 1.0, 0.0)
        t_p95 = float(math.log10(1.0 + p95_excess / (gain_ref + 1e-18)))

    frac = _safe_float(audit_row.get("cancel_frac_gain_rel_gt_1p25", float("nan")), default=float("nan"))
    frac_ref = 0.01
    if math.isnan(frac):
        t_frac = 0.0
    else:
        t_frac = float(math.log10(1.0 + max(frac, 0.0) / frac_ref))

    mu = _safe_float(audit_row.get("dict_mu", 0.0), default=0.0)
    mu_ref = 0.5
    t_mu = float(math.log10(1.0 + max(mu, 0.0) / mu_ref))
    w_mu = 0.2

    cancel_score = w_mu * t_mu + t_gain + 0.5 * t_p95 + 0.5 * t_frac
    return {
        "cancel_gain_rel_used": float(gain_rel),
        "cancel_j_used": int(j_used),
        "cancel_gain_rel_p95": float(p95) if not math.isnan(p95) else float("nan"),
        "cancel_frac_gain_rel_gt_1p25": float(frac) if not math.isnan(frac) else float("nan"),
        "cancel_mu": float(mu),
        "cancel_t_gain": float(t_gain),
        "cancel_t_p95": float(t_p95),
        "cancel_t_frac": float(t_frac),
        "cancel_t_mu": float(t_mu),
        "CancelScore": float(cancel_score),
    }


def compute_addressability_scores(audit_row: dict, thresholds: dict) -> dict:
    """Returns flat Addressability scores (SymScore, CancelScore, AddrScore)."""
    sym = compute_sym_score(audit_row, thresholds)
    cancel = compute_cancel_score(audit_row, thresholds)
    addr = float(sym["SymScore"]) + float(cancel["CancelScore"])
    out = {}
    out.update(sym)
    out.update(cancel)
    out["AddrScore"] = float(addr)
    return out
