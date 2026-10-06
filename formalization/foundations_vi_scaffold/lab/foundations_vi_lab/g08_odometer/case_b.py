"""Lean-matching non-abelian case (b) witness for G8-L2."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

STATES = ("S", "A", "B", "N")
MOVES = ("r", "s", "p", "q", "t")

TRANSITIONS = {
    ("S", "r"): "A",
    ("S", "s"): "B",
    ("A", "p"): "N",
    ("A", "t"): "N",
    ("B", "q"): "N",
}

LEGAL_MOVES = {
    "S": ("r", "s"),
    "A": ("p", "t"),
    "B": ("q",),
    "N": (),
}


@dataclass(frozen=True)
class RewriteRun:
    """One sampled legal route through the G8 case (b) witness."""

    seed: int
    route: tuple[str, ...]
    final: str
    counters: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class RewriteExperiment:
    """Aggregate outcome for G8-L2."""

    seed: int
    orders: int
    runs: tuple[RewriteRun, ...]

    @property
    def distinct_counters(self) -> int:
        """Number of distinct counter vectors sampled."""

        return len({run.counters for run in self.runs})


def legal_moves(state: str) -> tuple[str, ...]:
    """Return legal moves at `state`."""

    return LEGAL_MOVES[state]


def apply_move(state: str, move: str) -> str:
    """Apply a legal move in the case (b) system."""

    if move not in legal_moves(state):
        raise ValueError(f"illegal move {move!r} at state {state!r}")
    return TRANSITIONS[(state, move)]


def run_random_order(seed: int) -> RewriteRun:
    """Run one random legal order from `S` to a stable state."""

    rng = Random(seed)
    state = "S"
    route: list[str] = []
    counters = {move: 0 for move in MOVES}
    while legal_moves(state):
        options = legal_moves(state)
        move = options[rng.randrange(len(options))]
        state = apply_move(state, move)
        route.append(move)
        counters[move] += 1
    return RewriteRun(
        seed=seed,
        route=tuple(route),
        final=state,
        counters=tuple((move, counters[move]) for move in MOVES),
    )


def run_rewrite_experiment(*, seed: int, orders: int) -> RewriteExperiment:
    """Run G8-L2 and raise `AssertionError` if the witness check fails."""

    if orders <= 0:
        raise ValueError("orders must be positive")
    rng = Random(seed)
    runs = tuple(run_random_order(rng.randrange(0, 2**63)) for _ in range(orders))
    bad = [run for run in runs if run.final != "N"]
    if bad:
        raise AssertionError(f"non-N final state reached: {bad[0]}")
    experiment = RewriteExperiment(seed=seed, orders=orders, runs=runs)
    if experiment.distinct_counters < 2:
        raise AssertionError("sampled routes did not exhibit counter variation")
    return experiment

