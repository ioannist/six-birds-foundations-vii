from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from ._support.run_dictionary_feasibility import (
    _build_localized_dictionary,
    _build_paired_dictionary,
    _build_random_dictionary,
)
from ._support.route_mismatch import basis_from_sequential, route_mismatch_fro
from ._support.subspaces import (
    circulant_top_fourier_subspace,
    delta_localized_subspace,
    fourier_lowfreq_subspace,
    haar_random_subspace,
)
from .audits import audit_dictionary, audit_routes, audit_subspace
from .closure import evaluate_all_closures
from .meta_moves import (
    canonicalize_dictionary,
    gate_coherent_pairs,
    merge_routes_into_artifact,
    symmetrize_subspace_via_projector,
)


def _load_yaml(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if not isinstance(cfg, dict):
        raise ValueError(f"Expected YAML dict at {p}")
    return cfg


def _init_artifact(run_cfg: dict[str, Any]) -> dict[str, Any]:
    artifact_type = str(run_cfg["artifact_type"])
    constructor = str(run_cfg["constructor"])
    params = dict(run_cfg.get("params", {}))

    if artifact_type == "subspace":
        N = int(params["N"])
        m = int(params["m"])
        if constructor == "fourier":
            Psi = fourier_lowfreq_subspace(N, m)
        elif constructor == "circulant_top_fourier":
            Psi = circulant_top_fourier_subspace(N, m, sigma=float(params.get("sigma", 4.0)))
        elif constructor == "random":
            Psi = haar_random_subspace(N, m, seed=int(params.get("seed", 0)))
        elif constructor == "delta":
            Psi = delta_localized_subspace(N, m, pattern=str(params.get("pattern", "first")))
        else:
            raise ValueError(f"Unknown constructor: {constructor}")
        return {
            "kind": "subspace",
            "constructor": constructor,
            "N": N,
            "m": m,
            "Psi": Psi,
        }

    if artifact_type == "dictionary":
        N = int(params["N"])
        M = int(params["M"])
        if constructor == "paired":
            D = _build_paired_dictionary(
                N=N,
                M=M,
                sigma_pair=float(params["sigma_pair"]),
                alpha=float(params["alpha"]),
                seed=int(params["seed"]),
            )
        elif constructor == "random":
            D = _build_random_dictionary(N=N, M=M, seed=int(params.get("seed", 0)))
        elif constructor == "localized":
            D = _build_localized_dictionary(
                N=N,
                M=M,
                sigma1=float(params["sigma1"]),
                sigma2=float(params["sigma2"]),
            )
        else:
            raise ValueError(f"Unknown constructor: {constructor}")
        return {
            "kind": "dictionary",
            "constructor": constructor,
            "N": N,
            "M": M,
            "D": D,
            "constraint_specs": list(run_cfg.get("constraint_specs", [])),
        }

    if artifact_type == "routes":
        if constructor != "two_route":
            raise ValueError(f"Unknown constructor: {constructor}")
        N = int(params["N"])
        m2 = int(params["m2"])
        m1 = int(params["m1"])
        seed = int(params["seed"])
        Q_big = haar_random_subspace(N, m2, seed=seed)
        Q_small = haar_random_subspace(N, m1, seed=seed + 1000)
        Q_direct = haar_random_subspace(N, m1, seed=seed + 2000)
        Psi_seq = basis_from_sequential(Q_small, Q_big)
        mismatch = route_mismatch_fro(Q_small, Q_big, Q_direct)
        return {
            "kind": "routes",
            "constructor": constructor,
            "N": N,
            "Psi_seq": Psi_seq,
            "Psi_direct": Q_direct,
            "route_mismatch": float(mismatch),
            "merged_once": False,
        }

    raise ValueError(f"Unsupported artifact_type: {artifact_type}")


def _run_audit(artifact: dict[str, Any], common_cfg: dict[str, Any]) -> dict[str, Any]:
    kind = artifact["kind"]
    if kind == "subspace":
        sub = common_cfg["subspace"]
        return audit_subspace(
            artifact["Psi"],
            N=int(artifact["N"]),
            j_list=[int(x) for x in sub["j_list"]],
            shift_list=[int(x) for x in sub["shift_list"]],
            orbit_tau_list=tuple(float(x) for x in sub.get("orbit_tau_list", [1e-2])),
            orbit_k_cap=int(sub.get("orbit_k_cap", 128)),
        )
    if kind == "dictionary":
        dcfg = common_cfg["dictionary"]
        return audit_dictionary(
            artifact["D"],
            N=int(artifact["N"]),
            j_list=[int(x) for x in dcfg["j_list"]],
            constraint_specs=list(artifact.get("constraint_specs", [])),
        )
    if kind == "routes":
        rcfg = common_cfg["routes"]
        return audit_routes(
            artifact["Psi_seq"],
            artifact["Psi_direct"],
            mismatch_scalar=float(artifact["route_mismatch"]),
            N=int(artifact["N"]),
            j_list=[int(x) for x in rcfg["j_list"]],
        )
    raise ValueError(f"Unsupported artifact kind: {kind}")


def _relevant_closures(kind: str) -> list[str]:
    if kind == "subspace":
        return ["symmetry", "anti_localization"]
    if kind == "dictionary":
        return ["feasibility"]
    if kind == "routes":
        return ["routes", "feasibility"]
    return []


def _suggested_union(closure_report: dict[str, Any], relevant: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for name in relevant:
        entry = closure_report[name]
        if bool(entry["pass"]):
            continue
        for prim in entry["suggest"]:
            p = str(prim)
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def _move_to_primitives(move_name: str) -> set[str]:
    mapping = {
        "symmetrize_subspace_via_projector": {"P4", "P1"},
        "gate_coherent_pairs": {"P2"},
        "merge_routes_into_artifact": {"P3"},
        "canonicalize_dictionary": {"P5"},
    }
    return mapping.get(move_name, set())


def _is_move_applicable(move_name: str, artifact: dict[str, Any], p5_applied: bool) -> bool:
    kind = artifact["kind"]
    if move_name == "symmetrize_subspace_via_projector":
        return kind == "subspace"
    if move_name == "gate_coherent_pairs":
        return kind == "dictionary"
    if move_name == "canonicalize_dictionary":
        return kind == "dictionary" and not p5_applied
    if move_name == "merge_routes_into_artifact":
        return kind == "routes" and not bool(artifact.get("merged_once", False))
    return False


def _apply_move(
    artifact: dict[str, Any],
    move_name: str,
    move_params: dict[str, Any],
) -> dict[str, Any]:
    new_artifact = dict(artifact)
    if move_name == "symmetrize_subspace_via_projector":
        Psi_sym, summary = symmetrize_subspace_via_projector(
            artifact["Psi"],
            m=int(artifact["m"]),
            group=str(move_params.get("group", "shifts")),
            shifts=move_params.get("shifts"),
            method=str(move_params.get("method", "auto")),
        )
        new_artifact["Psi"] = Psi_sym
        new_artifact["last_move_summary"] = summary
        return new_artifact

    if move_name == "canonicalize_dictionary":
        D_canon, summary = canonicalize_dictionary(
            artifact["D"],
            near_dup_threshold=float(move_params.get("near_dup_threshold", 0.99)),
        )
        new_artifact["D"] = D_canon
        new_artifact["last_move_summary"] = summary
        return new_artifact

    if move_name == "gate_coherent_pairs":
        D_gated, summary = gate_coherent_pairs(
            artifact["D"],
            mu_target=float(move_params["mu_target"]),
        )
        new_artifact["D"] = D_gated
        new_artifact["M"] = int(D_gated.shape[1])
        new_artifact["last_move_summary"] = summary
        return new_artifact

    if move_name == "merge_routes_into_artifact":
        merged = merge_routes_into_artifact(
            artifact["Psi_seq"],
            artifact["Psi_direct"],
            mismatch_scalar=artifact.get("route_mismatch"),
        )
        new_artifact["merged_payload"] = merged
        new_artifact["merged_once"] = True
        new_artifact["last_move_summary"] = merged["summary"]
        return new_artifact

    raise ValueError(f"Unsupported move: {move_name}")


def _headline_metrics(
    audit_row: dict[str, Any],
    kind: str,
    common_cfg: dict[str, Any],
) -> dict[str, float]:
    out = {
        "metric_eta": float("nan"),
        "metric_inv_score": float("nan"),
        "metric_gain_rel": float("nan"),
        "metric_mu": float("nan"),
        "metric_mismatch": float("nan"),
    }
    if kind == "subspace":
        j_max = max(int(x) for x in common_cfg["subspace"]["j_list"])
        shift1 = int(common_cfg["subspace"]["shift_list"][0])
        out["metric_eta"] = float(audit_row.get(f"loc_eta_j{j_max}", float("nan")))
        out["metric_inv_score"] = float(audit_row.get(f"sym_inv_score_s{shift1}", float("nan")))
        return out

    if kind == "dictionary":
        j_max = max(int(x) for x in common_cfg["dictionary"]["j_list"])
        atom_key = f"loc_max_atom_loc_j{j_max}"
        paired_key = f"cancel_eta_hat_paired_diff_j{j_max}"
        if atom_key in audit_row and paired_key in audit_row:
            atom = float(audit_row[atom_key])
            out["metric_gain_rel"] = float(audit_row[paired_key]) / (atom + 1e-18)
        out["metric_mu"] = float(audit_row.get("dict_mu", float("nan")))
        return out

    if kind == "routes":
        j_max = max(int(x) for x in common_cfg["routes"]["j_list"])
        out["metric_gain_rel"] = float(audit_row.get(f"cancel_gain_rel_best_diff_j{j_max}", float("nan")))
        out["metric_mismatch"] = float(audit_row.get("route_mismatch", float("nan")))
        return out

    return out


def _plot_metric(df: pd.DataFrame, metric_col: str, out_path: Path, title: str, ylabel: str, log_y: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    subset = df[df[metric_col].notna()].copy()
    if subset.empty:
        ax.text(0.5, 0.5, f"No data for {metric_col}", ha="center", va="center")
        ax.set_axis_off()
    else:
        for run_id, grp in subset.groupby("run_id", sort=False):
            grp = grp.sort_values("step")
            ax.plot(grp["step"], grp[metric_col], marker="o", label=str(run_id))
        ax.set_xlabel("step")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        if log_y:
            ax.set_yscale("log")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def _make_plots(df: pd.DataFrame, plots_dir: str | Path) -> None:
    pdir = Path(plots_dir)
    pdir.mkdir(parents=True, exist_ok=True)
    _plot_metric(
        df,
        "metric_eta",
        pdir / "reflexive_loop_eta_over_steps.png",
        title="Reflexive Loop: eta over steps",
        ylabel="metric_eta",
    )
    _plot_metric(
        df,
        "metric_inv_score",
        pdir / "reflexive_loop_invscore_over_steps.png",
        title="Reflexive Loop: inv score over steps",
        ylabel="metric_inv_score",
        log_y=True,
    )
    _plot_metric(
        df,
        "metric_gain_rel",
        pdir / "reflexive_loop_gain_over_steps.png",
        title="Reflexive Loop: gain ratio over steps",
        ylabel="metric_gain_rel",
    )


def run_loop_from_config_dict(cfg: dict[str, Any], make_plots: bool = True) -> pd.DataFrame:
    thresholds = _load_yaml(cfg["thresholds_path"])
    common_cfg = dict(cfg["common"])
    runs = list(cfg["runs"])
    output_csv = Path(cfg["output_csv"])
    plots_dir = Path(cfg["plots_dir"])

    rows: list[dict[str, Any]] = []
    for run_cfg in runs:
        run_id = str(run_cfg["run_id"])
        max_steps = int(run_cfg["max_steps"])
        allowed_moves = [str(x) for x in run_cfg.get("allowed_moves", [])]
        move_params_all = dict(run_cfg.get("move_params", {}))
        artifact = _init_artifact(run_cfg)
        kind = artifact["kind"]

        for step in range(max_steps + 1):
            p5_applied = False
            p4_applied = False
            move_applied = ""

            # P5 canonicalization phase
            if kind == "dictionary" and "canonicalize_dictionary" in allowed_moves:
                params = dict(move_params_all.get("canonicalize_dictionary", {}))
                artifact = _apply_move(artifact, "canonicalize_dictionary", params)
                p5_applied = True
            elif kind == "routes" and "merge_routes_into_artifact" in allowed_moves and not artifact.get("merged_once", False):
                artifact = _apply_move(artifact, "merge_routes_into_artifact", {})
                p5_applied = True

            audit_row = _run_audit(artifact, common_cfg)
            closure_report = evaluate_all_closures(audit_row, thresholds)

            relevant = _relevant_closures(kind)
            suggested_primitives = _suggested_union(closure_report, relevant)
            all_relevant_pass = all(bool(closure_report[name]["pass"]) for name in relevant)

            stuck = False
            stop_reason = "continue"

            if all_relevant_pass:
                stop_reason = "all_pass"
            elif step >= max_steps:
                stop_reason = "max_steps"
            else:
                selected_move = ""
                for mv in allowed_moves:
                    prims = _move_to_primitives(mv)
                    if not prims.intersection(suggested_primitives):
                        continue
                    if not _is_move_applicable(mv, artifact, p5_applied=p5_applied):
                        continue
                    selected_move = mv
                    break

                if selected_move:
                    params = dict(move_params_all.get(selected_move, {}))
                    artifact = _apply_move(artifact, selected_move, params)
                    move_applied = selected_move
                    p4_applied = selected_move == "symmetrize_subspace_via_projector"
                    stop_reason = "continue"
                else:
                    stuck = True
                    stop_reason = "stuck"

            headline = _headline_metrics(audit_row, kind, common_cfg)
            row: dict[str, Any] = {
                "run_id": run_id,
                "step": int(step),
                "artifact_type": str(run_cfg["artifact_type"]),
                "constructor": str(run_cfg["constructor"]),
                "p5_applied": bool(p5_applied),
                "p4_applied": bool(p4_applied),
                "move_applied": move_applied,
                "suggested_primitives": ",".join(suggested_primitives),
                "stuck": bool(stuck),
                "stop_reason": stop_reason,
                "closure_symmetry_pass": bool(closure_report["symmetry"]["pass"]),
                "closure_feasibility_pass": bool(closure_report["feasibility"]["pass"]),
                "closure_routes_pass": bool(closure_report["routes"]["pass"]),
                "closure_anti_localization_pass": bool(closure_report["anti_localization"]["pass"]),
            }
            row.update(headline)
            row.update(audit_row)
            rows.append(row)

            if stop_reason in {"all_pass", "stuck", "max_steps"}:
                break

    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    if make_plots:
        _make_plots(df, plots_dir)
    return df


def run_loop_from_config_path(path: str) -> pd.DataFrame:
    cfg = _load_yaml(path)
    return run_loop_from_config_dict(cfg, make_plots=True)
