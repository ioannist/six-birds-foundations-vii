from __future__ import annotations

import numpy as np


def _max_contiguous_sum(p: np.ndarray, b: int) -> float:
    N = p.size
    if not (1 <= b <= N):
        raise ValueError("b must satisfy 1 <= b <= N")
    # Non-wrap contiguous blocks: starts 0..N-b.
    csum = np.cumsum(np.concatenate(([0.0], p)))
    vals = csum[b:] - csum[:-b]
    return float(np.max(vals))


def run_checks() -> tuple[int, float, float]:
    seed = 0
    N = 64
    num_cases = 200
    tol = 1e-10

    rng = np.random.default_rng(seed)
    worst_slack_contig_topb = -np.inf
    worst_slack_topb_diagmax = -np.inf

    for _ in range(num_cases):
        p = rng.standard_normal(N)
        b = int(rng.integers(1, N + 1))

        max_contig_sum = _max_contiguous_sum(p, b)
        top_b_sum = float(np.sum(np.sort(p)[-b:]))
        diagmax_bound = float(b * np.max(p))

        slack1 = max_contig_sum - top_b_sum
        slack2 = top_b_sum - diagmax_bound

        worst_slack_contig_topb = max(worst_slack_contig_topb, slack1)
        worst_slack_topb_diagmax = max(worst_slack_topb_diagmax, slack2)

        if slack1 > tol:
            raise AssertionError(
                f"Violation max_contig<=top_b: contig={max_contig_sum:.12g}, "
                f"top_b={top_b_sum:.12g}, slack={slack1:.12g}, b={b}"
            )
        if slack2 > tol:
            raise AssertionError(
                f"Violation top_b<=diagmax: top_b={top_b_sum:.12g}, "
                f"diagmax={diagmax_bound:.12g}, slack={slack2:.12g}, b={b}"
            )

    return num_cases, float(worst_slack_contig_topb), float(worst_slack_topb_diagmax)


def main() -> None:
    num_cases, worst1, worst2 = run_checks()
    print(f"num_cases={num_cases}")
    print(f"worst_slack_max_contig_minus_top_b={worst1:.12g}")
    print(f"worst_slack_top_b_minus_diagmax={worst2:.12g}")
    print("OK")


if __name__ == "__main__":
    main()
