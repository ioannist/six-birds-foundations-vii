from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .dict_metrics import dictionary_metrics
from .localization import eta_j_from_basis, make_cells_1d
from .subspaces import haar_random_subspace


def _parse_int_list(raw: str) -> list[int]:
    vals = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not vals:
        raise ValueError("Expected non-empty integer list.")
    return vals


def _normalize_columns(D: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(D, axis=0)
    norms[norms == 0.0] = 1.0
    return D / norms


def _bump(N: int, sigma: float) -> np.ndarray:
    idx = np.arange(N, dtype=float)
    d = np.minimum(idx, N - idx)
    return np.exp(-(d**2) / (2.0 * sigma**2))


def _build_random_dictionary(N: int, M: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    D = rng.standard_normal((N, M))
    return _normalize_columns(D)


def _build_localized_dictionary(N: int, M: int, sigma1: float, sigma2: float) -> np.ndarray:
    if M != 2 * N:
        raise ValueError("localized dictionary requires M = 2*N.")
    b1 = _bump(N, sigma1)
    b2 = _bump(N, sigma2)
    cols1 = np.column_stack([np.roll(b1, i) for i in range(N)])
    cols2 = np.column_stack([np.roll(b2, i) for i in range(N)])
    return _normalize_columns(np.column_stack([cols1, cols2]))


def _build_paired_dictionary(N: int, M: int, sigma_pair: float, alpha: float, seed: int) -> np.ndarray:
    if M != 2 * N:
        raise ValueError("paired dictionary requires M = 2*N.")
    rng = np.random.default_rng(seed)
    U = rng.standard_normal((N, N))
    U = _normalize_columns(U)
    b = _bump(N, sigma_pair)
    bumps = np.column_stack([np.roll(b, i) for i in range(N)])
    Dp = _normalize_columns(U + alpha * bumps)
    return _normalize_columns(np.column_stack([U, Dp]))


def _loc_from_vectors(V: np.ndarray, cell_size: int, num_cells: int) -> np.ndarray:
    energies = np.abs(V) ** 2
    T = energies.shape[1]
    per_cell = energies.reshape(num_cells, cell_size, T).sum(axis=1)
    numer = per_cell.max(axis=0)
    denom = energies.sum(axis=0)
    denom[denom == 0.0] = 1.0
    return numer / denom


def _atom_loc_stats(D: np.ndarray, cell_size: int, num_cells: int) -> tuple[float, float]:
    locs = _loc_from_vectors(D, cell_size, num_cells)
    return float(np.max(locs)), float(np.mean(locs))


def _estimate_atom_eta(D: np.ndarray, num_samples: int, rng: np.random.Generator, cell_size: int, num_cells: int) -> float:
    idx = rng.integers(0, D.shape[1], size=num_samples)
    V = D[:, idx]
    locs = _loc_from_vectors(V, cell_size, num_cells)
    return float(np.max(locs))


def _estimate_sparse_eta(
    D: np.ndarray,
    s: int,
    num_samples: int,
    rng: np.random.Generator,
    cell_size: int,
    num_cells: int,
) -> float:
    M = D.shape[1]
    idx = np.empty((num_samples, s), dtype=np.int64)
    for t in range(num_samples):
        idx[t] = rng.choice(M, size=s, replace=False)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(num_samples, s)) / np.sqrt(float(s))
    atoms = D[:, idx]  # (N, num_samples, s)
    V = np.einsum("nts,ts->nt", atoms, signs)
    locs = _loc_from_vectors(V, cell_size, num_cells)
    return float(np.max(locs))


def _estimate_l2_dense_eta(D: np.ndarray, num_samples: int, rng: np.random.Generator, cell_size: int, num_cells: int) -> float:
    M = D.shape[1]
    A = rng.standard_normal((M, num_samples))
    norms = np.linalg.norm(A, axis=0)
    norms[norms == 0.0] = 1.0
    A /= norms
    V = D @ A
    locs = _loc_from_vectors(V, cell_size, num_cells)
    return float(np.max(locs))


def _estimate_paired_diff_eta(D: np.ndarray, N: int, cell_size: int, num_cells: int) -> float:
    vals: list[float] = []
    for i in range(N):
        v = (D[:, i] - D[:, i + N]) / np.sqrt(2.0)
        vals.append(float(_loc_from_vectors(v.reshape(-1, 1), cell_size, num_cells)[0]))
    return float(np.max(vals))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dictionary feasibility localization experiment.")
    parser.add_argument("--N", type=int, default=256)
    parser.add_argument("--M", type=int, default=512)
    parser.add_argument("--j", type=int, default=6)
    parser.add_argument("--num-samples-dense", type=int, default=5000)
    parser.add_argument("--num-samples-sparse", type=int, default=5000)
    parser.add_argument("--s-list", type=str, default="1,2,4,8")
    parser.add_argument("--seed-dict", type=int, default=0)
    parser.add_argument("--seed-samples", type=int, default=1)
    parser.add_argument("--sigma1", type=float, default=1.0)
    parser.add_argument("--sigma2", type=float, default=2.0)
    parser.add_argument("--sigma-pair", type=float, default=2.0)
    parser.add_argument("--alpha", type=float, default=0.2)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    N = int(args.N)
    M = int(args.M)
    j = int(args.j)
    num_samples_dense = int(args.num_samples_dense)
    num_samples_sparse = int(args.num_samples_sparse)
    s_list = sorted(_parse_int_list(args.s_list))

    cells = make_cells_1d(N, j)
    num_cells = len(cells)
    cell_size = len(cells[0])
    if any(len(c) != cell_size for c in cells):
        raise ValueError("Expected equal-size cells from make_cells_1d.")

    Psi = haar_random_subspace(N, 32, seed=0)
    eta_subspace_baseline = float(eta_j_from_basis(Psi, cells))

    rng_samples = np.random.default_rng(int(args.seed_samples))

    D_random = _build_random_dictionary(N, M, seed=int(args.seed_dict))
    D_localized = _build_localized_dictionary(N, M, sigma1=float(args.sigma1), sigma2=float(args.sigma2))
    D_paired = _build_paired_dictionary(
        N,
        M,
        sigma_pair=float(args.sigma_pair),
        alpha=float(args.alpha),
        seed=int(args.seed_dict),
    )

    dicts = [("random", D_random), ("localized", D_localized), ("paired", D_paired)]
    rows: list[dict[str, object]] = []

    for dict_type, D in dicts:
        metrics = dictionary_metrics(D)
        max_atom_loc, mean_atom_loc = _atom_loc_stats(D, cell_size=cell_size, num_cells=num_cells)

        eta_atom = _estimate_atom_eta(
            D,
            num_samples=num_samples_sparse,
            rng=rng_samples,
            cell_size=cell_size,
            num_cells=num_cells,
        )
        rows.append(
            {
                "dict_type": dict_type,
                "constraint_type": "atom",
                "s": 1,
                "N": N,
                "M": M,
                "j": j,
                "num_samples": num_samples_sparse,
                "eta_hat": eta_atom,
                "max_atom_loc": max_atom_loc,
                "mean_atom_loc": mean_atom_loc,
                "sigma1": float(args.sigma1),
                "sigma2": float(args.sigma2),
                "sigma_pair": float(args.sigma_pair),
                "alpha": float(args.alpha),
                "eta_subspace_baseline": eta_subspace_baseline,
                "mu": float(metrics["mu"]),
                "mean_abs_offdiag": float(metrics["mean_abs_offdiag"]),
                "gram_top_eig": float(metrics["gram_top_eig"]),
                "cond_proxy": float(metrics["cond_proxy"]),
                "stable_rank": float(metrics["stable_rank"]),
            }
        )

        for s in [x for x in s_list if x >= 2]:
            eta_sparse = _estimate_sparse_eta(
                D,
                s=s,
                num_samples=num_samples_sparse,
                rng=rng_samples,
                cell_size=cell_size,
                num_cells=num_cells,
            )
            rows.append(
                {
                    "dict_type": dict_type,
                    "constraint_type": "sparse_random",
                    "s": s,
                    "N": N,
                    "M": M,
                    "j": j,
                    "num_samples": num_samples_sparse,
                    "eta_hat": eta_sparse,
                    "max_atom_loc": max_atom_loc,
                    "mean_atom_loc": mean_atom_loc,
                    "sigma1": float(args.sigma1),
                    "sigma2": float(args.sigma2),
                    "sigma_pair": float(args.sigma_pair),
                    "alpha": float(args.alpha),
                    "eta_subspace_baseline": eta_subspace_baseline,
                    "mu": float(metrics["mu"]),
                    "mean_abs_offdiag": float(metrics["mean_abs_offdiag"]),
                    "gram_top_eig": float(metrics["gram_top_eig"]),
                    "cond_proxy": float(metrics["cond_proxy"]),
                    "stable_rank": float(metrics["stable_rank"]),
                }
            )

        eta_l2 = _estimate_l2_dense_eta(
            D,
            num_samples=num_samples_dense,
            rng=rng_samples,
            cell_size=cell_size,
            num_cells=num_cells,
        )
        rows.append(
            {
                "dict_type": dict_type,
                "constraint_type": "l2_dense",
                "s": np.nan,
                "N": N,
                "M": M,
                "j": j,
                "num_samples": num_samples_dense,
                "eta_hat": eta_l2,
                "max_atom_loc": max_atom_loc,
                "mean_atom_loc": mean_atom_loc,
                "sigma1": float(args.sigma1),
                "sigma2": float(args.sigma2),
                "sigma_pair": float(args.sigma_pair),
                "alpha": float(args.alpha),
                "eta_subspace_baseline": eta_subspace_baseline,
                "mu": float(metrics["mu"]),
                "mean_abs_offdiag": float(metrics["mean_abs_offdiag"]),
                "gram_top_eig": float(metrics["gram_top_eig"]),
                "cond_proxy": float(metrics["cond_proxy"]),
                "stable_rank": float(metrics["stable_rank"]),
            }
        )

        if dict_type == "paired":
            eta_pair_diff = _estimate_paired_diff_eta(D, N=N, cell_size=cell_size, num_cells=num_cells)
            rows.append(
                {
                    "dict_type": dict_type,
                    "constraint_type": "paired_diff",
                    "s": 2,
                    "N": N,
                    "M": M,
                    "j": j,
                    "num_samples": N,
                    "eta_hat": eta_pair_diff,
                    "max_atom_loc": max_atom_loc,
                    "mean_atom_loc": mean_atom_loc,
                    "sigma1": float(args.sigma1),
                    "sigma2": float(args.sigma2),
                    "sigma_pair": float(args.sigma_pair),
                    "alpha": float(args.alpha),
                    "eta_subspace_baseline": eta_subspace_baseline,
                    "mu": float(metrics["mu"]),
                    "mean_abs_offdiag": float(metrics["mean_abs_offdiag"]),
                    "gram_top_eig": float(metrics["gram_top_eig"]),
                    "cond_proxy": float(metrics["cond_proxy"]),
                    "stable_rank": float(metrics["stable_rank"]),
                }
            )

    out_dir = Path("experiments/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "dictionary_feasibility.csv"
    out_path_metrics = out_dir / "dictionary_feasibility_with_metrics.csv"
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    df.to_csv(out_path_metrics, index=False)
    print(f"Wrote {out_path} with {len(df)} rows")
    print(f"Wrote {out_path_metrics} with {len(df)} rows")


if __name__ == "__main__":
    main()
