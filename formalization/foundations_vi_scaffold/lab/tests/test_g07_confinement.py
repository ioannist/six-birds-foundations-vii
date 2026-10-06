"""Tests for the G7 finite-board angel/devil lab."""

from foundations_vi_lab.g07_confinement.finite_game import (
    Board,
    legal_angel_moves,
    run_wall_rank_testbed,
    solve_bounded_horizon,
    torus_axis_distance,
    torus_chebyshev_distance,
)


def test_torus_axis_distance_wraparound() -> None:
    """Wrapped coordinate distance uses the shorter torus path."""

    assert torus_axis_distance(5, 0, 4) == 1
    assert torus_axis_distance(5, 1, 4) == 2
    assert torus_axis_distance(6, 0, 3) == 3


def test_torus_chebyshev_distance_wraparound() -> None:
    """Chebyshev distance composes wrapped axis distances."""

    board = Board(5)
    assert torus_chebyshev_distance(board, board.index(0, 0), board.index(4, 4)) == 1
    assert torus_chebyshev_distance(board, board.index(0, 0), board.index(2, 4)) == 2


def test_tiny_board_exact_values() -> None:
    """Hand-checkable tiny torus values are exact minimax outputs."""

    board = Board(2)
    assert set(legal_angel_moves(board, 0, 0, 1)) == {1, 2, 3}
    p1 = solve_bounded_horizon(board, power=1, budget=1, horizon=3)
    p2 = solve_bounded_horizon(board, power=2, budget=2, horizon=3)
    assert p1.guaranteed_turns == 3
    assert p1.survived_to_horizon
    assert p2.guaranteed_turns == 2
    assert p2.trapped_within == 3


def test_wall_rank_strict_decrease() -> None:
    """The finite-board wall-rank testbed strictly decreases rank each step."""

    result = run_wall_rank_testbed(Board(4), start=0)
    assert result.steps
    assert result.trapped
    for step in result.steps:
        assert step.rank_after < step.rank_before
