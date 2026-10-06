from __future__ import annotations

import numpy as np

from ._support.localization import eta_j_from_basis, make_cells_1d


def _orthonormal_from_seed(N: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((N, N))
    Q, R = np.linalg.qr(G)
    # Deterministic sign convention for QR columns.
    d = np.sign(np.diag(R))
    d[d == 0.0] = 1.0
    Q = Q * d[np.newaxis, :]
    return Q


def run_checks() -> tuple[int, float]:
    N = 64
    j = 4
    pairs = [(4, 4), (8, 4), (12, 8)]
    num_seeds = 50
    tol = 1e-10

    cells = make_cells_1d(N, j)

    cases = 0
    worst_violation = -np.inf

    for seed in range(num_seeds):
        Q = _orthonormal_from_seed(N, seed)
        for m, delta in pairs:
            m_big = m + delta
            Psi_small = Q[:, :m]
            Psi_big = Q[:, :m_big]

            eta_small = float(eta_j_from_basis(Psi_small, cells, check_orthonormal=False))
            eta_big = float(eta_j_from_basis(Psi_big, cells, check_orthonormal=False))

            violation = eta_small - eta_big
            if violation > worst_violation:
                worst_violation = violation
            if violation > tol:
                raise AssertionError(
                    f"Monotonicity violation: eta_small={eta_small:.12g} eta_big={eta_big:.12g} "
                    f"violation={violation:.12g} seed={seed} m={m} delta={delta}"
                )
            cases += 1

    return cases, float(worst_violation)


def main() -> None:
    cases, worst_violation = run_checks()
    print(f"cases tested: {cases}")
    print(f"worst violation eta_small-eta_big: {worst_violation:.12g}")
    print("OK")


if __name__ == "__main__":
    main()
