"""Exact finite-torus angel/devil bounded-horizon game search."""

from __future__ import annotations

import itertools
import time
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Board:
    """An `n x n` torus board."""

    n: int

    def __post_init__(self) -> None:
        if self.n < 2:
            raise ValueError("board size must be at least 2")

    @property
    def cell_count(self) -> int:
        """Number of cells."""

        return self.n * self.n

    def index(self, row: int, col: int) -> int:
        """Convert a possibly wrapped coordinate to a cell index."""

        return (row % self.n) * self.n + (col % self.n)

    def coord(self, cell: int) -> tuple[int, int]:
        """Convert a cell index to `(row, col)`."""

        if cell < 0 or cell >= self.cell_count:
            raise ValueError(f"cell out of range: {cell}")
        return divmod(cell, self.n)

    def bit(self, cell: int) -> int:
        """Bitmask with exactly `cell` set."""

        return 1 << cell


def torus_axis_distance(n: int, a: int, b: int) -> int:
    """Shortest wrapped distance between coordinates `a` and `b`."""

    diff = abs(a - b) % n
    return min(diff, n - diff)


def torus_chebyshev_distance(board: Board, a: int, b: int) -> int:
    """Chebyshev distance on an `n x n` torus."""

    ar, ac = board.coord(a)
    br, bc = board.coord(b)
    return max(
        torus_axis_distance(board.n, ar, br),
        torus_axis_distance(board.n, ac, bc),
    )


def is_deleted(mask: int, cell: int) -> bool:
    """Return whether `cell` is deleted in `mask`."""

    return bool(mask & (1 << cell))


def legal_angel_moves(board: Board, pos: int, deleted: int, power: int) -> tuple[int, ...]:
    """All undeleted, different cells within torus Chebyshev distance `power`."""

    if power < 1:
        raise ValueError("angel power must be at least 1")
    moves: list[int] = []
    for cell in range(board.cell_count):
        if cell == pos or is_deleted(deleted, cell):
            continue
        if torus_chebyshev_distance(board, pos, cell) <= power:
            moves.append(cell)
    return tuple(moves)


def devil_response_masks(board: Board, deleted: int, new_pos: int, budget: int) -> tuple[int, ...]:
    """All exact legal devil response masks deleting at most `budget` cells."""

    if budget < 0:
        raise ValueError("budget must be nonnegative")
    candidates = [
        cell
        for cell in range(board.cell_count)
        if cell != new_pos and not is_deleted(deleted, cell)
    ]
    responses = [0]
    max_delete = min(budget, len(candidates))
    for size in range(1, max_delete + 1):
        for combo in itertools.combinations(candidates, size):
            mask = 0
            for cell in combo:
                mask |= board.bit(cell)
            responses.append(mask)
    return tuple(responses)


@dataclass(frozen=True)
class SearchResult:
    """Exact bounded-horizon minimax result for one parameter setting."""

    n: int
    power: int
    budget: int
    horizon: int
    guaranteed_turns: int
    survived_to_horizon: bool
    trapped_within: int | None
    states_evaluated: int
    cache_hits: int
    elapsed_seconds: float


def solve_bounded_horizon(
    board: Board,
    power: int,
    budget: int,
    horizon: int,
    start: int = 0,
) -> SearchResult:
    """Compute the exact maximum guaranteed survival up to `horizon` turns."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    start_time = time.perf_counter()

    @lru_cache(maxsize=None)
    def survives(pos: int, deleted: int, turns_remaining: int) -> bool:
        if turns_remaining == 0:
            return True
        moves = legal_angel_moves(board, pos, deleted, power)
        if not moves:
            return False
        for new_pos in moves:
            angel_can_force = True
            for response in devil_response_masks(board, deleted, new_pos, budget):
                if not survives(new_pos, deleted | response, turns_remaining - 1):
                    angel_can_force = False
                    break
            if angel_can_force:
                return True
        return False

    guaranteed = 0
    for turns in range(1, horizon + 1):
        if survives(start, 0, turns):
            guaranteed = turns
        else:
            break

    elapsed = time.perf_counter() - start_time
    info = survives.cache_info()
    survived = guaranteed == horizon
    return SearchResult(
        n=board.n,
        power=power,
        budget=budget,
        horizon=horizon,
        guaranteed_turns=guaranteed,
        survived_to_horizon=survived,
        trapped_within=None if survived else guaranteed + 1,
        states_evaluated=info.currsize,
        cache_hits=info.hits,
        elapsed_seconds=elapsed,
    )


@dataclass(frozen=True)
class WallRankStep:
    """One step in the finite-board confinement-rank testbed."""

    turn: int
    angel_before: int
    angel_after: int
    deleted_cell: int
    rank_before: int
    rank_after: int


@dataclass(frozen=True)
class WallRankResult:
    """Result of a deterministic finite-board rank-decrease testbed run."""

    n: int
    start: int
    trapped: bool
    turns: int
    steps: list[WallRankStep]


def finite_exhaustion_rank(board: Board, deleted: int, angel_pos: int) -> int:
    """Rank for the finite-board confinement testbed: deletable free cells."""

    return sum(
        1
        for cell in range(board.cell_count)
        if cell != angel_pos and not is_deleted(deleted, cell)
    )


def first_legal_angel_move(board: Board, pos: int, deleted: int, power: int = 1) -> int | None:
    """Deterministic legal angel move used by the rank testbed."""

    moves = legal_angel_moves(board, pos, deleted, power)
    return moves[0] if moves else None


def exhaustion_wall_response(board: Board, deleted: int, angel_pos: int) -> int | None:
    """Delete the first available non-angel cell, building a finite-board wall by exhaustion."""

    for cell in range(board.cell_count):
        if cell != angel_pos and not is_deleted(deleted, cell):
            return cell
    return None


def run_wall_rank_testbed(board: Board, start: int, max_turns: int | None = None) -> WallRankResult:
    """Check strict rank decrease for a concrete `p=1,b=1` confinement testbed."""

    deleted = 0
    pos = start
    limit = max_turns if max_turns is not None else board.cell_count
    steps: list[WallRankStep] = []
    for turn in range(limit):
        move = first_legal_angel_move(board, pos, deleted, power=1)
        if move is None:
            return WallRankResult(board.n, start, True, turn, steps)
        before_rank = finite_exhaustion_rank(board, deleted, pos)
        deleted_cell = exhaustion_wall_response(board, deleted, move)
        if deleted_cell is None:
            return WallRankResult(board.n, start, True, turn, steps)
        new_deleted = deleted | board.bit(deleted_cell)
        after_rank = finite_exhaustion_rank(board, new_deleted, move)
        if not after_rank < before_rank:
            raise AssertionError(
                f"rank did not decrease at turn {turn}: {before_rank} -> {after_rank}"
            )
        steps.append(
            WallRankStep(
                turn=turn,
                angel_before=pos,
                angel_after=move,
                deleted_cell=deleted_cell,
                rank_before=before_rank,
                rank_after=after_rank,
            )
        )
        pos = move
        deleted = new_deleted
    return WallRankResult(board.n, start, False, limit, steps)
