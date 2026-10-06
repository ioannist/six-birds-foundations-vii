"""Tests for the G6 Recaman census lab."""

from foundations_vi_lab.g06_needle.recaman import (
    OEIS_A005132_PREFIX_20,
    recaman_prefix,
    run_recaman_census,
)


def test_recaman_oeis_a005132_prefix_20() -> None:
    """OEIS A005132 begins 0,1,3,6,2,7,13,20,12,21,11,22,10,23,9,24,8,25,43,62."""

    assert recaman_prefix(20) == OEIS_A005132_PREFIX_20


def test_small_census_records_exact_counts() -> None:
    """A short exact census exposes backward moves and a smallest missing value."""

    summary = run_recaman_census(
        steps=100,
        low_limit=10_000,
        checkpoint_interval=50,
        windows=(100, 1_000, 10_000),
        missing_interval_window=100,
    )
    assert summary.steps == 100
    assert summary.prefix_checked == OEIS_A005132_PREFIX_20
    assert summary.backward_legal_steps > 0
    assert summary.final_smallest_missing > 0
    assert len(summary.checkpoints) == 2
