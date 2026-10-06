"""Exact Ducci-sequence and GF(2) matrix checks for G10-L1."""

from __future__ import annotations

import random
from dataclasses import dataclass


TupleState = tuple[int, ...]
Matrix = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class DucciResult:
    """Outcome of one seeded Ducci run."""

    k: int
    seed: int
    initial: TupleState
    initial_range: int
    max_after_first: int
    bounded_after_first: bool
    status: str
    steps: int
    period: int | None
    repeated_at: int | None
    final: TupleState


@dataclass(frozen=True)
class MatrixCheck:
    """Exact GF(2) nilpotency check for one power-of-two length."""

    k: int
    exponent: int
    is_zero: bool


def ducci_step(state: TupleState) -> TupleState:
    """Apply the cyclic Ducci map `(|x_i - x_{i+1}|)_i`."""

    if not state:
        raise ValueError("Ducci state must be nonempty")
    return tuple(abs(value - state[(index + 1) % len(state)]) for index, value in enumerate(state))


def is_zero_state(state: TupleState) -> bool:
    """Return whether every coordinate is zero."""

    return all(value == 0 for value in state)


def run_ducci_until_cycle(
    initial: TupleState,
    *,
    seed: int,
    max_steps: int,
) -> DucciResult:
    """Iterate a Ducci tuple until zero, a repeated state, or `max_steps`."""

    initial_range = max(initial) - min(initial)
    max_after_first = 0
    seen: dict[TupleState, int] = {initial: 0}
    state = initial
    if is_zero_state(state):
        return DucciResult(
            k=len(initial),
            seed=seed,
            initial=initial,
            initial_range=initial_range,
            max_after_first=0,
            bounded_after_first=True,
            status="zero",
            steps=0,
            period=None,
            repeated_at=None,
            final=state,
        )
    for step in range(1, max_steps + 1):
        state = ducci_step(state)
        max_after_first = max(max_after_first, max(state))
        if is_zero_state(state):
            return DucciResult(
                k=len(initial),
                seed=seed,
                initial=initial,
                initial_range=initial_range,
                max_after_first=max_after_first,
                bounded_after_first=max_after_first <= initial_range,
                status="zero",
                steps=step,
                period=None,
                repeated_at=None,
                final=state,
            )
        if state in seen:
            first = seen[state]
            return DucciResult(
                k=len(initial),
                seed=seed,
                initial=initial,
                initial_range=initial_range,
                max_after_first=max_after_first,
                bounded_after_first=max_after_first <= initial_range,
                status="cycle",
                steps=step,
                period=step - first,
                repeated_at=first,
                final=state,
            )
        seen[state] = step
    return DucciResult(
        k=len(initial),
        seed=seed,
        initial=initial,
        initial_range=initial_range,
        max_after_first=max_after_first,
        bounded_after_first=max_after_first <= initial_range,
        status="budget_exhausted",
        steps=max_steps,
        period=None,
        repeated_at=None,
        final=state,
    )


def random_tuple(k: int, *, seed: int, max_entry: int) -> TupleState:
    """Generate one seeded random Ducci tuple with entries in `[0,max_entry]`."""

    rng = random.Random(seed)
    return tuple(rng.randint(0, max_entry) for _ in range(k))


def seeded_ducci_sweep(
    *,
    seed: int,
    min_k: int = 3,
    max_k: int = 16,
    max_entry: int = 1_000_000,
    max_steps: int = 100_000,
) -> list[DucciResult]:
    """Run the G10-L1 seeded Ducci sweep for all tuple lengths in range."""

    results = []
    for k in range(min_k, max_k + 1):
        k_seed = seed + k
        initial = random_tuple(k, seed=k_seed, max_entry=max_entry)
        results.append(run_ducci_until_cycle(initial, seed=k_seed, max_steps=max_steps))
    return results


def gf2_identity(k: int) -> Matrix:
    """Return the `k x k` identity matrix over GF(2)."""

    return tuple(tuple(1 if row == col else 0 for col in range(k)) for row in range(k))


def gf2_shift(k: int) -> Matrix:
    """Return the cyclic shift matrix `S` with `(Sx)_i = x_{i+1}` over GF(2)."""

    return tuple(tuple(1 if col == (row + 1) % k else 0 for col in range(k)) for row in range(k))


def gf2_matrix_add(left: Matrix, right: Matrix) -> Matrix:
    """Add two same-sized matrices over GF(2)."""

    return tuple(
        tuple((a + b) % 2 for a, b in zip(left_row, right_row))
        for left_row, right_row in zip(left, right)
    )


def gf2_matrix_mul(left: Matrix, right: Matrix) -> Matrix:
    """Multiply two same-sized matrices over GF(2)."""

    size = len(left)
    return tuple(
        tuple(
            sum(left[row][mid] * right[mid][col] for mid in range(size)) % 2
            for col in range(size)
        )
        for row in range(size)
    )


def gf2_matrix_pow(matrix: Matrix, exponent: int) -> Matrix:
    """Exponentiate a GF(2) matrix by repeated squaring."""

    if exponent < 0:
        raise ValueError("matrix exponent must be nonnegative")
    result = gf2_identity(len(matrix))
    base = matrix
    power = exponent
    while power:
        if power % 2 == 1:
            result = gf2_matrix_mul(result, base)
        base = gf2_matrix_mul(base, base)
        power //= 2
    return result


def gf2_zero(k: int) -> Matrix:
    """Return the `k x k` zero matrix over GF(2)."""

    return tuple(tuple(0 for _ in range(k)) for _ in range(k))


def ducci_linear_operator(k: int) -> Matrix:
    """Return `L = I + S` over GF(2) for the parity Ducci map."""

    return gf2_matrix_add(gf2_identity(k), gf2_shift(k))


def check_power_two_nilpotency(k: int) -> MatrixCheck:
    """Check `(I+S)^k=0` over GF(2), for a power-of-two tuple length `k`."""

    power = gf2_matrix_pow(ducci_linear_operator(k), k)
    return MatrixCheck(k=k, exponent=k, is_zero=power == gf2_zero(k))


def run_matrix_checks(lengths: tuple[int, ...] = (4, 8, 16)) -> list[MatrixCheck]:
    """Run all GF(2) nilpotency checks required by G10-L1."""

    return [check_power_two_nilpotency(k) for k in lengths]
