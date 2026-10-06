from __future__ import annotations

import numpy as np
import pytest

from sixbirds_foundations_v.carrier import (
    FiniteKernel,
    build_channel_matrix,
    enumerate_action_seqs,
    viability_kernel,
    viability_kernel_history,
)


def _make_kernel() -> FiniteKernel:
    transitions = np.array(
        [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.0, 1.0], [1.0, 0.0]],
        ]
    )
    return FiniteKernel(transitions)


def test_kernel_validate_and_rollout() -> None:
    kernel = _make_kernel()
    kernel.validate()

    dist = np.array([0.25, 0.75])
    rolled = kernel.rollout_dist(dist, [1, 0, 1])
    stepped = kernel.step_dist(kernel.step_dist(kernel.step_dist(dist, 1), 0), 1)
    assert np.allclose(rolled, stepped, atol=0.0, rtol=0.0)


def test_kernel_validation_rejects_bad_rows() -> None:
    kernel = FiniteKernel(np.array([[[0.9, 0.0], [0.0, 1.0]]]))
    with pytest.raises(ValueError):
        kernel.validate()


def test_viability_kernel_exact() -> None:
    states = [0, 1, 2, 3]
    actions = [0, 1]
    transitions = {
        (0, 0): {0},
        (0, 1): {1},
        (1, 0): {1},
        (1, 1): {2},
        (2, 0): {2, 3},
        (2, 1): {3},
        (3, 0): {3},
        (3, 1): {3},
    }

    kernel_set = viability_kernel(
        states,
        actions,
        lambda _s: actions,
        lambda s, a: transitions[(s, a)],
        lambda s: s != 3,
    )
    history = viability_kernel_history(
        states,
        actions,
        lambda _s: actions,
        lambda s, a: transitions[(s, a)],
        lambda s: s != 3,
    )

    assert kernel_set == {0, 1}
    assert history[-1] == {0, 1}


def test_channel_matrix_deterministic() -> None:
    seqs = enumerate_action_seqs([0, 1], 2)
    matrix = build_channel_matrix(_make_kernel(), s0=0, action_seqs=seqs, proj=lambda s: s)

    expected = np.array(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [0.0, 1.0],
            [1.0, 0.0],
        ]
    )
    assert seqs == [(0, 0), (0, 1), (1, 0), (1, 1)]
    assert np.allclose(matrix, expected, atol=0.0, rtol=0.0)

