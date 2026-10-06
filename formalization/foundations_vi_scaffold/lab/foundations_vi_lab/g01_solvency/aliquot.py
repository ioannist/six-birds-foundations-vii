"""Aliquot-sequence ledger illustration for G1-L4."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from foundations_vi_lab.g01_solvency.collatz_ledger import nu_2


@dataclass(frozen=True)
class AliquotLedgerStep:
    """One exact factorization-supply ledger projection along an aliquot orbit."""

    value: int
    sigma: int
    aliquot: int
    nu2_sigma: int


@dataclass(frozen=True)
class AliquotOrbitResult:
    """Classification of one aliquot sequence."""

    start: int
    status: str
    steps: int
    cycle: tuple[int, ...]
    escaped_value: int | None
    max_value_seen: int
    ledger: tuple[AliquotLedgerStep, ...]


@dataclass(frozen=True)
class AliquotSweepSummary:
    """Aggregate G1-L4 sweep result."""

    limit: int
    max_steps: int
    cap: int
    tested_count: int
    terminated_count: int
    cycled_count: int
    fixed_point_count: int
    escaped_cap_count: int
    step_cap_count: int
    unique_cycle_count: int
    unique_fixed_points: tuple[int, ...]
    unique_cycles: tuple[tuple[int, ...], ...]
    escaped_cap_starts_sample: tuple[int, ...]
    step_cap_starts_sample: tuple[int, ...]
    max_steps_observed: int
    max_steps_start: int
    max_value_seen: int
    sigma_spot_check_limit: int
    sigma_spot_checks_passed: bool
    elapsed_seconds: float


def primes_up_to(limit: int) -> list[int]:
    """Return all primes up to `limit` by an exact sieve."""

    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * (((limit - start) // p) + 1)
    return [n for n in range(2, limit + 1) if sieve[n]]


class SigmaComputer:
    """Exact cached divisor-sum computer for values up to the configured cap."""

    def __init__(self, cap: int) -> None:
        self.cap = cap
        self.primes = primes_up_to(math.isqrt(cap) + 1)
        self._cache: dict[int, int] = {0: 0, 1: 1}

    def sigma(self, n: int) -> int:
        """Return the exact sum of all positive divisors of `n`."""

        if n < 0:
            raise ValueError("sigma is defined here only for nonnegative integers")
        if n in self._cache:
            return self._cache[n]
        original = n
        remaining = n
        total = 1
        for p in self.primes:
            if p * p > remaining:
                break
            if remaining % p != 0:
                continue
            power = 1
            term_sum = 1
            while remaining % p == 0:
                remaining //= p
                power *= p
                term_sum += power
            total *= term_sum
        if remaining > 1:
            total *= 1 + remaining
        self._cache[original] = total
        return total

    def aliquot(self, n: int) -> int:
        """Return `s(n)=sigma(n)-n` exactly."""

        return self.sigma(n) - n


def brute_sigma(n: int) -> int:
    """Compute `sigma(n)` by direct divisor enumeration for tests/spot checks."""

    if n < 1:
        return 0
    total = 0
    root = math.isqrt(n)
    for d in range(1, root + 1):
        if n % d == 0:
            total += d
            other = n // d
            if other != d:
                total += other
    return total


def verify_sigma_spot_checks(computer: SigmaComputer, *, limit: int = 1000) -> bool:
    """Cross-check factorized sigma against brute force for `1..limit`."""

    for n in range(1, limit + 1):
        if computer.sigma(n) != brute_sigma(n):
            return False
    return True


def track_aliquot_orbit(
    start: int,
    computer: SigmaComputer,
    *,
    max_steps: int = 1000,
    cap: int = 10**12,
    keep_ledger: bool = True,
) -> AliquotOrbitResult:
    """Track one aliquot sequence until termination, cycle, cap, or step budget."""

    if start < 1:
        raise ValueError("start must be positive")

    seen: dict[int, int] = {}
    values: list[int] = []
    ledger: list[AliquotLedgerStep] = []
    current = start
    max_seen = start

    for step in range(max_steps + 1):
        if current == 0:
            return AliquotOrbitResult(
                start=start,
                status="terminated_zero",
                steps=step,
                cycle=(),
                escaped_value=None,
                max_value_seen=max_seen,
                ledger=tuple(ledger),
            )
        if current > cap:
            return AliquotOrbitResult(
                start=start,
                status="escaped_cap",
                steps=step,
                cycle=(),
                escaped_value=current,
                max_value_seen=max(max_seen, current),
                ledger=tuple(ledger),
            )
        if current in seen:
            cycle = tuple(values[seen[current] :])
            return AliquotOrbitResult(
                start=start,
                status="cycle",
                steps=step,
                cycle=_canonical_cycle(cycle),
                escaped_value=None,
                max_value_seen=max_seen,
                ledger=tuple(ledger),
            )
        if step == max_steps:
            return AliquotOrbitResult(
                start=start,
                status="step_cap",
                steps=step,
                cycle=(),
                escaped_value=None,
                max_value_seen=max_seen,
                ledger=tuple(ledger),
            )

        seen[current] = len(values)
        values.append(current)
        sigma_value = computer.sigma(current)
        next_value = sigma_value - current
        max_seen = max(max_seen, next_value)
        if keep_ledger:
            ledger.append(
                AliquotLedgerStep(
                    value=current,
                    sigma=sigma_value,
                    aliquot=next_value,
                    nu2_sigma=nu_2(sigma_value),
                )
            )
        current = next_value

    raise AssertionError("unreachable aliquot loop exit")


def sweep_aliquot(
    *,
    limit: int = 100_000,
    max_steps: int = 1000,
    cap: int = 10**12,
    sigma_spot_check_limit: int = 1000,
) -> AliquotSweepSummary:
    """Run G1-L4 for starts `1..limit`."""

    started = time.perf_counter()
    computer = SigmaComputer(cap)
    spot_ok = verify_sigma_spot_checks(computer, limit=sigma_spot_check_limit)

    terminated = 0
    cycled = 0
    fixed = 0
    escaped = 0
    step_cap = 0
    escaped_starts: list[int] = []
    step_cap_starts: list[int] = []
    cycles: dict[tuple[int, ...], tuple[int, ...]] = {}
    fixed_points: set[int] = set()
    max_steps_observed = 0
    max_steps_start = 1
    max_value_seen = 1

    for start in range(1, limit + 1):
        result = track_aliquot_orbit(
            start,
            computer,
            max_steps=max_steps,
            cap=cap,
            keep_ledger=False,
        )
        if result.status == "terminated_zero":
            terminated += 1
        elif result.status == "cycle":
            cycled += 1
            cycles[result.cycle] = result.cycle
            if len(result.cycle) == 1:
                fixed += 1
                fixed_points.add(result.cycle[0])
        elif result.status == "escaped_cap":
            escaped += 1
            if len(escaped_starts) < 50:
                escaped_starts.append(start)
            if result.escaped_value is not None:
                max_value_seen = max(max_value_seen, result.escaped_value)
        elif result.status == "step_cap":
            step_cap += 1
            if len(step_cap_starts) < 50:
                step_cap_starts.append(start)

        if result.steps > max_steps_observed:
            max_steps_observed = result.steps
            max_steps_start = start
        max_value_seen = max(max_value_seen, result.max_value_seen)

    elapsed = time.perf_counter() - started
    unique_cycles = tuple(sorted(cycles.values(), key=lambda cycle: (len(cycle), cycle)))
    return AliquotSweepSummary(
        limit=limit,
        max_steps=max_steps,
        cap=cap,
        tested_count=limit,
        terminated_count=terminated,
        cycled_count=cycled,
        fixed_point_count=fixed,
        escaped_cap_count=escaped,
        step_cap_count=step_cap,
        unique_cycle_count=len(unique_cycles),
        unique_fixed_points=tuple(sorted(fixed_points)),
        unique_cycles=unique_cycles,
        escaped_cap_starts_sample=tuple(escaped_starts),
        step_cap_starts_sample=tuple(step_cap_starts),
        max_steps_observed=max_steps_observed,
        max_steps_start=max_steps_start,
        max_value_seen=max_value_seen,
        sigma_spot_check_limit=sigma_spot_check_limit,
        sigma_spot_checks_passed=spot_ok,
        elapsed_seconds=elapsed,
    )


def _canonical_cycle(cycle: tuple[int, ...]) -> tuple[int, ...]:
    """Rotate a cycle to a deterministic least lexicographic representative."""

    if not cycle:
        return cycle
    rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
    return min(rotations)
