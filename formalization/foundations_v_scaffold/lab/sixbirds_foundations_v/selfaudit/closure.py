from __future__ import annotations

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


def _pick_j(js: list[int], mode: str) -> int:
    if not js:
        raise ValueError("No scale indices available for requested prefix.")
    if mode == "max":
        return max(js)
    if mode == "min":
        return min(js)
    raise ValueError(f"Unsupported j selection mode: {mode}")


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def closure_symmetry(audit_row: dict[str, Any], thresholds: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    if audit_row.get("artifact_type") != "subspace":
        return True, ["n/a (artifact_type != subspace)"], []

    th = thresholds["symmetry"]
    shift = int(th["inv_shift"])
    inv_max = float(th["inv_score_max"])
    diag_std_max = float(th["diag_std_max"])
    trace_err_max = float(th["trace_ratio_err_max"])
    trace_j_mode = str(th["trace_j_mode"])

    reasons: list[str] = []
    passed = True

    inv_key = f"sym_inv_score_s{shift}"
    if inv_key not in audit_row:
        passed = False
        reasons.append(f"missing key: {inv_key}")
    else:
        inv_val = float(audit_row[inv_key])
        if inv_val > inv_max:
            passed = False
            reasons.append(f"{inv_key}={inv_val:.6g} > {inv_max:.6g}")

    diag_key = "sym_diag_std"
    if diag_key not in audit_row:
        passed = False
        reasons.append("missing key: sym_diag_std")
    else:
        diag_val = float(audit_row[diag_key])
        if diag_val > diag_std_max:
            passed = False
            reasons.append(f"sym_diag_std={diag_val:.6g} > {diag_std_max:.6g}")

    trace_js = _available_js(audit_row, "sym_trace_ratio_err_j")
    if not trace_js:
        passed = False
        reasons.append("missing keys: sym_trace_ratio_err_j*")
    else:
        j = _pick_j(trace_js, trace_j_mode)
        key = f"sym_trace_ratio_err_j{j}"
        val = float(audit_row[key])
        if val > trace_err_max:
            passed = False
            reasons.append(f"{key}={val:.6g} > {trace_err_max:.6g}")

    if passed:
        return True, ["symmetry closure passed"], []
    return False, reasons, ["P4", "P1", "P5"]


def closure_AL(audit_row: dict[str, Any], thresholds: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    if audit_row.get("artifact_type") != "subspace":
        return True, ["n/a (artifact_type != subspace)"], []

    th = thresholds["anti_localization"]
    ratio_max = float(th["eta_over_theory_max"])
    j_mode = str(th["j_mode"])
    abs_eps = float(th["abs_eps"])

    js = _available_js(audit_row, "loc_eta_j")
    if not js:
        return False, ["missing keys: loc_eta_j*"], ["P6"]
    j = _pick_j(js, j_mode)

    eta_key = f"loc_eta_j{j}"
    theory_key = f"sym_trace_theory_j{j}"
    if eta_key not in audit_row or theory_key not in audit_row:
        missing = []
        if eta_key not in audit_row:
            missing.append(eta_key)
        if theory_key not in audit_row:
            missing.append(theory_key)
        return False, [f"missing key(s): {', '.join(missing)}"], ["P6"]

    eta = float(audit_row[eta_key])
    theory = float(audit_row[theory_key])
    ratio = eta / (theory + abs_eps)
    if ratio <= ratio_max:
        return True, [f"eta/theory at j={j} is {ratio:.6g} <= {ratio_max:.6g}"], []
    return False, [f"eta/theory at j={j} is {ratio:.6g} > {ratio_max:.6g}"], ["P2", "P1", "P6"]


def closure_feasibility(audit_row: dict[str, Any], thresholds: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    artifact = audit_row.get("artifact_type")
    if artifact == "subspace":
        return True, ["n/a (artifact_type == subspace)"], []
    if artifact not in {"dictionary", "routes"}:
        return True, [f"n/a (artifact_type={artifact!r})"], []

    th = thresholds["feasibility"]
    gain_rel_max = float(th["gain_rel_max"])
    gain_abs_max = float(th["gain_abs_max"])
    j_mode = str(th["j_mode"])
    eps = float(th["eps"])

    if artifact == "dictionary":
        js = _available_js(audit_row, "loc_max_atom_loc_j")
        if not js:
            return False, ["missing keys: loc_max_atom_loc_j*"], ["P6"]
        j = _pick_j(js, j_mode)

        paired_key = f"cancel_eta_hat_paired_diff_j{j}"
        if paired_key not in audit_row:
            return True, ["no cancellation probe present"], []

        atom_key = f"loc_max_atom_loc_j{j}"
        gain_key = f"cancel_gain_paired_diff_j{j}"
        eta_hat = float(audit_row[paired_key])
        atom = float(audit_row[atom_key])
        gain_abs = float(audit_row[gain_key]) if gain_key in audit_row else float(eta_hat - atom)
        gain_rel = float(eta_hat / (atom + eps))

        reasons: list[str] = []
        passed = True
        if gain_rel > gain_rel_max:
            passed = False
            reasons.append(f"gain_rel(j={j})={gain_rel:.6g} > {gain_rel_max:.6g}")
        if gain_abs > gain_abs_max + 1e-12:
            passed = False
            reasons.append(f"gain_abs(j={j})={gain_abs:.6g} > {gain_abs_max:.6g}")
        if passed:
            return True, [f"cancellation probe within thresholds at j={j}"], []
        return False, reasons, ["P2", "P5", "P6"]

    # routes
    js = _available_js(audit_row, "cancel_gain_rel_best_diff_j")
    if not js:
        return True, ["no cancellation probe present"], []
    j = _pick_j(js, j_mode)
    gain_rel_key = f"cancel_gain_rel_best_diff_j{j}"
    gain_abs_key = f"cancel_gain_best_diff_j{j}"
    gain_rel = float(audit_row[gain_rel_key])
    gain_abs = float(audit_row[gain_abs_key]) if gain_abs_key in audit_row else float("nan")

    reasons = []
    passed = True
    if gain_rel > gain_rel_max:
        passed = False
        reasons.append(f"route gain_rel(j={j})={gain_rel:.6g} > {gain_rel_max:.6g}")
    if gain_abs > gain_abs_max + 1e-12:
        passed = False
        reasons.append(f"route gain_abs(j={j})={gain_abs:.6g} > {gain_abs_max:.6g}")
    if passed:
        return True, [f"route cancellation probe within thresholds at j={j}"], []
    return False, reasons, ["P2", "P5", "P6"]


def closure_routes(audit_row: dict[str, Any], thresholds: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    if audit_row.get("artifact_type") != "routes":
        return True, ["n/a (artifact_type != routes)"], []

    th = thresholds["routes"]
    mismatch_max = float(th["mismatch_max"])
    gain_rel_max = float(th["gain_rel_max"])
    gain_abs_max = float(th["gain_abs_max"])
    j_mode = str(th["j_mode"])
    eps = float(th["eps"])

    reasons: list[str] = []
    suggestions: list[str] = []
    passed = True

    mismatch = float(audit_row.get("route_mismatch", float("nan")))
    if mismatch > mismatch_max:
        passed = False
        reasons.append(f"route_mismatch={mismatch:.6g} > {mismatch_max:.6g}")
        suggestions.extend(["P3", "P5", "P1"])

    js = _available_js(audit_row, "cancel_gain_rel_best_diff_j")
    if js:
        j = _pick_j(js, j_mode)
        gain_rel_key = f"cancel_gain_rel_best_diff_j{j}"
        gain_abs_key = f"cancel_gain_best_diff_j{j}"
        gain_rel = float(audit_row[gain_rel_key])
        gain_abs = float(audit_row[gain_abs_key]) if gain_abs_key in audit_row else float("nan")
        if gain_rel > gain_rel_max:
            passed = False
            reasons.append(f"cancel_gain_rel_best_diff_j{j}={gain_rel:.6g} > {gain_rel_max:.6g}")
            suggestions.append("P2")
        if gain_abs > gain_abs_max + 1e-12 + eps:
            passed = False
            reasons.append(f"cancel_gain_best_diff_j{j}={gain_abs:.6g} > {gain_abs_max:.6g}")
            suggestions.append("P2")
    else:
        reasons.append("no route cancellation probe present")

    if passed:
        return True, ["route closure passed"], []
    return False, reasons, _dedupe_keep_order(suggestions)


def evaluate_all_closures(audit_row: dict[str, Any], thresholds: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sym_pass, sym_reasons, sym_suggest = closure_symmetry(audit_row, thresholds)
    feas_pass, feas_reasons, feas_suggest = closure_feasibility(audit_row, thresholds)
    route_pass, route_reasons, route_suggest = closure_routes(audit_row, thresholds)
    al_pass, al_reasons, al_suggest = closure_AL(audit_row, thresholds)
    return {
        "symmetry": {"pass": sym_pass, "reasons": sym_reasons, "suggest": sym_suggest},
        "feasibility": {"pass": feas_pass, "reasons": feas_reasons, "suggest": feas_suggest},
        "routes": {"pass": route_pass, "reasons": route_reasons, "suggest": route_suggest},
        "anti_localization": {"pass": al_pass, "reasons": al_reasons, "suggest": al_suggest},
    }
