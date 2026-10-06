from __future__ import annotations

import numpy as np

from sixbirds_foundations_v.selfaudit import audit_subspace, canonicalize_dictionary
from sixbirds_foundations_v.selfaudit._support.subspaces import (
    delta_localized_subspace,
    fourier_lowfreq_subspace,
)


def test_audit_subspace_fourier_smoke() -> None:
    psi = fourier_lowfreq_subspace(N=32, m=8)
    audit = audit_subspace(psi, N=32, j_list=[2, 3], shift_list=[1, 4])

    assert "sym_diag_std" in audit
    assert "loc_eta_j2" in audit
    assert float(audit["sym_diag_std"]) < 1e-10


def test_audit_subspace_delta_smoke() -> None:
    psi = delta_localized_subspace(N=32, m=8, pattern="first")
    audit = audit_subspace(psi, N=32, j_list=[2, 3], shift_list=[1, 4])

    assert float(audit["sym_diag_std"]) > 1e-3
    assert float(audit["loc_eta_j3"]) == 1.0


def test_canonicalize_dictionary_smoke() -> None:
    matrix = np.array(
        [
            [3.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 2.0, 1.0],
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ]
    )
    canonical, summary = canonicalize_dictionary(matrix)

    norms = np.linalg.norm(canonical, axis=0)
    assert np.allclose(norms[norms > 0.0], 1.0, atol=1e-12, rtol=0.0)
    assert int(summary["num_zero_cols"]) == 1

