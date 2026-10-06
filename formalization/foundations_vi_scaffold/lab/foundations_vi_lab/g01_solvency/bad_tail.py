"""Bad-tail membrane census and ghost-shadowing checks for G1-L2."""

from __future__ import annotations

import time
from dataclasses import dataclass

from foundations_vi_lab.g01_solvency.collatz_ledger import accelerated_step, nu_2


@dataclass(frozen=True)
class FirstDescentResult:
    """First-solvency result for one odd start."""

    start: int
    first_descent_step: int | None
    terminal_fixed: bool
    capped: bool
    steps_checked: int


@dataclass(frozen=True)
class FirstDescentSweep:
    """Aggregate first-solvency census for odd starts below a limit."""

    limit: int
    max_steps: int
    tested_odd_count: int
    nonterminal_count: int
    terminal_fixed_count: int
    descended_count: int
    capped_count: int
    total_steps_checked: int
    histogram: dict[int, int]
    membrane_sizes: dict[int, int]
    mean_k_star: str
    percentile_50: int
    percentile_90: int
    percentile_99: int
    max_k_star: int
    max_k_star_start: int
    elapsed_seconds: float


@dataclass(frozen=True)
class GhostFamilyRecord:
    """Exact check for one `2^L - 1` ghost-shadowing member."""

    L: int
    start: int
    shadow_steps: int
    valuations: tuple[int, ...]
    shadow_valuations_all_one: bool
    closed_form_agrees: bool
    first_descent_step: int | None
    first_descent_value: int | None
    predicted_k_star: int
    predicted_k_star_matches: bool
    capped: bool


@dataclass(frozen=True)
class G1L2Summary:
    """Full G1-L2 run summary."""

    limit: int
    max_steps: int
    ghost_min_L: int
    ghost_max_L: int
    ghost_max_steps: int
    census: FirstDescentSweep
    ghost_family: tuple[GhostFamilyRecord, ...]
    ghost_prediction_failures: int
    elapsed_seconds: float


def first_descent_step(start: int, *, max_steps: int = 1000) -> FirstDescentResult:
    """Compute `k*(start)` by exact accelerated iteration only."""

    if start <= 0 or start % 2 == 0:
        raise ValueError("first_descent_step expects a positive odd start")

    n_k = start
    for k in range(1, max_steps + 1):
        m = 3 * n_k + 1
        a = (m & -m).bit_length() - 1
        n_k = m >> a
        if n_k % 2 != 1:
            raise AssertionError("accelerated Collatz step did not return an odd integer")
        if n_k < start:
            return FirstDescentResult(
                start=start,
                first_descent_step=k,
                terminal_fixed=(start == 1 and n_k == 1),
                capped=False,
                steps_checked=k,
            )
        if start == 1 and k == 1 and n_k == 1:
            return FirstDescentResult(
                start=start,
                first_descent_step=None,
                terminal_fixed=True,
                capped=False,
                steps_checked=k,
            )

    return FirstDescentResult(
        start=start,
        first_descent_step=None,
        terminal_fixed=(start == 1),
        capped=True,
        steps_checked=max_steps,
    )


def _percentile_from_histogram(histogram: dict[int, int], count: int, percent: int) -> int:
    """Return the nearest-rank percentile from a `k*` histogram."""

    if count <= 0:
        return 0
    rank = (percent * count + 99) // 100
    seen = 0
    for k in sorted(histogram):
        seen += histogram[k]
        if seen >= rank:
            return k
    return max(histogram) if histogram else 0


def _membrane_sizes(histogram: dict[int, int], nonterminal_count: int) -> dict[int, int]:
    """Compute `|N_k ∩ [1,N]| = count { n : k*(n) > k }` from a histogram."""

    if not histogram:
        return {0: 0}
    remaining = nonterminal_count
    sizes: dict[int, int] = {}
    for k in range(0, max(histogram) + 1):
        remaining -= histogram.get(k, 0)
        sizes[k] = remaining
    return sizes


def sweep_first_descent(limit: int, *, max_steps: int = 1000) -> FirstDescentSweep:
    """Compute `k*(n)` for every positive odd `n < limit`."""

    if limit <= 1:
        raise ValueError("limit must be greater than 1")

    started = time.perf_counter()
    tested = 0
    nonterminal = 0
    terminal_fixed = 0
    descended = 0
    capped = 0
    total_steps = 0
    histogram: dict[int, int] = {}
    sum_k = 0
    max_k = 0
    max_start = 0

    for start in range(1, limit, 2):
        tested += 1
        result = first_descent_step(start, max_steps=max_steps)
        total_steps += result.steps_checked
        if result.terminal_fixed:
            terminal_fixed += 1
            continue

        nonterminal += 1
        if result.capped or result.first_descent_step is None:
            capped += 1
            continue

        k_star = result.first_descent_step
        descended += 1
        histogram[k_star] = histogram.get(k_star, 0) + 1
        sum_k += k_star
        if k_star > max_k:
            max_k = k_star
            max_start = start

    elapsed = time.perf_counter() - started
    mean = "0" if descended == 0 else f"{sum_k / descended:.6f}"
    return FirstDescentSweep(
        limit=limit,
        max_steps=max_steps,
        tested_odd_count=tested,
        nonterminal_count=nonterminal,
        terminal_fixed_count=terminal_fixed,
        descended_count=descended,
        capped_count=capped,
        total_steps_checked=total_steps,
        histogram=histogram,
        membrane_sizes=_membrane_sizes(histogram, nonterminal),
        mean_k_star=mean,
        percentile_50=_percentile_from_histogram(histogram, descended, 50),
        percentile_90=_percentile_from_histogram(histogram, descended, 90),
        percentile_99=_percentile_from_histogram(histogram, descended, 99),
        max_k_star=max_k,
        max_k_star_start=max_start,
        elapsed_seconds=elapsed,
    )


def verify_ghost_family_member(L: int, *, max_steps: int = 5000) -> GhostFamilyRecord:
    """Verify the `2^L - 1` shadowing prefix and compute its actual `k*`."""

    if L < 2:
        raise ValueError("ghost family check expects L >= 2")

    start = (1 << L) - 1
    n_i = start
    valuations: list[int] = []
    closed_form_agrees = True

    for i in range(L):
        closed_form = (3**i) * (1 << (L - i)) - 1
        if n_i != closed_form:
            closed_form_agrees = False
        if i < L - 1:
            a_i = nu_2(3 * n_i + 1)
            valuations.append(a_i)
            n_i, _ = accelerated_step(n_i)

    descent = first_descent_step(start, max_steps=max_steps)
    descent_value: int | None = None
    if descent.first_descent_step is not None:
        descent_value = start
        for _ in range(descent.first_descent_step):
            descent_value, _ = accelerated_step(descent_value)

    predicted = L - 1
    actual = descent.first_descent_step
    return GhostFamilyRecord(
        L=L,
        start=start,
        shadow_steps=L - 1,
        valuations=tuple(valuations),
        shadow_valuations_all_one=all(a == 1 for a in valuations),
        closed_form_agrees=closed_form_agrees,
        first_descent_step=actual,
        first_descent_value=descent_value,
        predicted_k_star=predicted,
        predicted_k_star_matches=(actual == predicted),
        capped=descent.capped,
    )


def run_g1_l2(
    *,
    limit: int = 10_000_000,
    max_steps: int = 1000,
    ghost_min_L: int = 2,
    ghost_max_L: int = 80,
    ghost_max_steps: int = 5000,
) -> G1L2Summary:
    """Run the full G1-L2 census and ghost-family check."""

    started = time.perf_counter()
    census = sweep_first_descent(limit=limit, max_steps=max_steps)
    ghost_records = tuple(
        verify_ghost_family_member(L, max_steps=ghost_max_steps)
        for L in range(ghost_min_L, ghost_max_L + 1)
    )
    elapsed = time.perf_counter() - started
    return G1L2Summary(
        limit=limit,
        max_steps=max_steps,
        ghost_min_L=ghost_min_L,
        ghost_max_L=ghost_max_L,
        ghost_max_steps=ghost_max_steps,
        census=census,
        ghost_family=ghost_records,
        ghost_prediction_failures=sum(
            1 for record in ghost_records if not record.predicted_k_star_matches
        ),
        elapsed_seconds=elapsed,
    )

