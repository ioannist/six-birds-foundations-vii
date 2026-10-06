from __future__ import annotations

import numpy as np

from ._support.dict_l2_opt import loc_j
from ._support.localization import make_cells_1d


def _normalize_columns(D: np.ndarray, eps: float = 1e-18) -> np.ndarray:
    norms = np.linalg.norm(D, axis=0)
    out = D.copy()
    nz = norms > eps
    out[:, nz] = out[:, nz] / norms[nz]
    out[:, ~nz] = 0.0
    return out


def _max_cell_op_norm_sq(U: np.ndarray, cells: list[np.ndarray]) -> float:
    best = 0.0
    for B in cells:
        UB = U[B, :]
        svals = np.linalg.svd(UB, compute_uv=False, full_matrices=False)
        val = float(svals[0] ** 2) if svals.size > 0 else 0.0
        if val > best:
            best = val
    return best


def run_checks() -> tuple[int, float, float]:
    seed = 0
    num_dicts = 5
    N = 64
    M = 128
    j = 4
    s_list = [2, 4]
    num_supports_per_s = 50
    num_a_samples = 30
    tol = 1e-10

    rng = np.random.default_rng(seed)
    cells = make_cells_1d(N, j)

    total_cases = 0
    max_loc = 0.0
    min_slack = float("inf")

    for _ in range(num_dicts):
        D = rng.standard_normal((N, M))
        D = _normalize_columns(D)

        for s in s_list:
            for _ in range(num_supports_per_s):
                S = rng.choice(M, size=s, replace=False)
                U = D[:, S]

                svals_full = np.linalg.svd(U, compute_uv=False, full_matrices=False)
                sigma_min = float(svals_full[-1])
                sigma_min_sq = sigma_min * sigma_min
                if sigma_min_sq <= 0.0:
                    pred = float("inf")
                else:
                    pred = _max_cell_op_norm_sq(U, cells) / sigma_min_sq

                for _ in range(num_a_samples):
                    a = rng.standard_normal(s)
                    a_norm = float(np.linalg.norm(a))
                    if a_norm <= 0.0:
                        continue
                    a = a / a_norm
                    v = U @ a
                    loc = float(loc_j(v, cells))
                    slack = float(pred - loc)

                    total_cases += 1
                    if loc > max_loc:
                        max_loc = loc
                    if slack < min_slack:
                        min_slack = slack

                    if slack < -tol:
                        raise AssertionError(
                            f"Inequality violation: loc={loc:.12g} pred={pred:.12g} slack={slack:.12g}"
                        )

    return total_cases, max_loc, min_slack


def main() -> None:
    total_cases, max_loc, min_slack = run_checks()
    print(f"total_cases_tested={total_cases}")
    print(f"max_observed_loc={max_loc:.12g}")
    print(f"min_slack_pred_minus_loc={min_slack:.12g}")
    print("OK")


if __name__ == "__main__":
    main()
