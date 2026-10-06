"""Exact Recaman-sequence census tools for G6-L1."""

from __future__ import annotations

from dataclasses import dataclass


OEIS_A005132_PREFIX_20: tuple[int, ...] = (
    0,
    1,
    3,
    6,
    2,
    7,
    13,
    20,
    12,
    21,
    11,
    22,
    10,
    23,
    9,
    24,
    8,
    25,
    43,
    62,
)


class HybridVisited:
    """Exact visited-set membership with a low bytearray and high-value set."""

    def __init__(self, low_limit: int) -> None:
        if low_limit < 1:
            raise ValueError("low_limit must be positive")
        self.low_limit = low_limit
        self.low = bytearray(low_limit + 1)
        self.high: set[int] = set()

    def contains(self, value: int) -> bool:
        """Return whether `value` has been visited."""

        if 0 <= value <= self.low_limit:
            return self.low[value] != 0
        return value in self.high

    def add(self, value: int) -> bool:
        """Mark `value` visited; return whether it was newly inserted."""

        if value < 0:
            raise ValueError("visited values must be nonnegative")
        if value <= self.low_limit:
            was_new = self.low[value] == 0
            self.low[value] = 1
            return was_new
        was_new = value not in self.high
        self.high.add(value)
        return was_new


@dataclass(frozen=True)
class RecamanCheckpoint:
    """Checkpoint summary for the G6-L1 census."""

    step: int
    current_value: int
    max_value: int
    smallest_missing: int
    backward_legal_steps: int
    return_pressure_numerator: int
    return_pressure_denominator: int
    interval_backward_legal: int
    coverage: dict[str, dict[str, int]]
    interval_new_visits: dict[str, int]


@dataclass(frozen=True)
class RecamanSummary:
    """Full G6-L1 run summary."""

    steps: int
    low_limit: int
    checkpoint_interval: int
    windows: tuple[int, ...]
    prefix_checked: tuple[int, ...]
    final_value: int
    max_value: int
    high_value_count: int
    backward_legal_steps: int
    return_pressure_numerator: int
    return_pressure_denominator: int
    final_smallest_missing: int
    final_coverage: dict[str, dict[str, int]]
    missing_intervals_window: int
    missing_intervals: tuple[tuple[int, int], ...]
    checkpoints: tuple[RecamanCheckpoint, ...]


def recaman_prefix(length: int) -> tuple[int, ...]:
    """Return the first `length` Recaman values, including `a_0`."""

    if length <= 0:
        return ()
    visited = HybridVisited(low_limit=max(100, length * length + 10))
    current = 0
    visited.add(current)
    values = [current]
    for n in range(1, length):
        candidate = current - n
        if candidate > 0 and not visited.contains(candidate):
            current = candidate
        else:
            current = current + n
        visited.add(current)
        values.append(current)
    return tuple(values)


def _coverage_dict(windows: tuple[int, ...], counts: dict[int, int]) -> dict[str, dict[str, int]]:
    return {
        str(window): {"visited": counts[window], "total": window}
        for window in windows
    }


def _missing_intervals(
    visited: HybridVisited, *, window: int, limit: int
) -> tuple[tuple[int, int], ...]:
    """Return the first missing-value intervals in `[1, window]`."""

    intervals: list[tuple[int, int]] = []
    value = 1
    while value <= window and len(intervals) < limit:
        while value <= window and visited.contains(value):
            value += 1
        if value > window:
            break
        start = value
        while value <= window and not visited.contains(value):
            value += 1
        intervals.append((start, value - 1))
    return tuple(intervals)


def run_recaman_census(
    *,
    steps: int = 10_000_000,
    low_limit: int = 100_000_000,
    checkpoint_interval: int = 1_000_000,
    windows: tuple[int, ...] = (100_000, 1_000_000, 10_000_000),
    missing_interval_window: int = 1_000_000,
    missing_interval_limit: int = 20,
) -> RecamanSummary:
    """Run the exact bounded Recaman census."""

    if steps < 1:
        raise ValueError("steps must be positive")
    if checkpoint_interval < 1:
        raise ValueError("checkpoint_interval must be positive")
    if max(windows) > low_limit:
        raise ValueError("low_limit must cover all requested fixed windows")

    prefix = recaman_prefix(len(OEIS_A005132_PREFIX_20))
    if prefix != OEIS_A005132_PREFIX_20:
        raise AssertionError("Recaman prefix mismatch against OEIS A005132")

    visited = HybridVisited(low_limit=low_limit)
    current = 0
    max_value = 0
    visited.add(current)
    visited_counts = {window: 0 for window in windows}
    interval_new = {window: 0 for window in windows}
    smallest_missing = 1
    backward_legal = 0
    interval_backward_legal = 0
    checkpoints: list[RecamanCheckpoint] = []

    for n in range(1, steps + 1):
        candidate = current - n
        legal_backward = candidate > 0 and not visited.contains(candidate)
        if legal_backward:
            current = candidate
            backward_legal += 1
            interval_backward_legal += 1
        else:
            current = current + n

        if current > max_value:
            max_value = current
        was_new = visited.add(current)
        if was_new and current > 0:
            for window in windows:
                if current <= window:
                    visited_counts[window] += 1
                    interval_new[window] += 1
        while smallest_missing <= low_limit and visited.contains(smallest_missing):
            smallest_missing += 1

        if n % checkpoint_interval == 0 or n == steps:
            checkpoints.append(
                RecamanCheckpoint(
                    step=n,
                    current_value=current,
                    max_value=max_value,
                    smallest_missing=smallest_missing,
                    backward_legal_steps=backward_legal,
                    return_pressure_numerator=backward_legal,
                    return_pressure_denominator=n,
                    interval_backward_legal=interval_backward_legal,
                    coverage=_coverage_dict(windows, visited_counts),
                    interval_new_visits={str(k): v for k, v in interval_new.items()},
                )
            )
            interval_backward_legal = 0
            interval_new = {window: 0 for window in windows}

    return RecamanSummary(
        steps=steps,
        low_limit=low_limit,
        checkpoint_interval=checkpoint_interval,
        windows=windows,
        prefix_checked=prefix,
        final_value=current,
        max_value=max_value,
        high_value_count=len(visited.high),
        backward_legal_steps=backward_legal,
        return_pressure_numerator=backward_legal,
        return_pressure_denominator=steps,
        final_smallest_missing=smallest_missing,
        final_coverage=_coverage_dict(windows, visited_counts),
        missing_intervals_window=missing_interval_window,
        missing_intervals=_missing_intervals(
            visited, window=missing_interval_window, limit=missing_interval_limit
        ),
        checkpoints=tuple(checkpoints),
    )
