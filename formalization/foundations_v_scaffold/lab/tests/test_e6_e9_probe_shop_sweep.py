from __future__ import annotations

from fractions import Fraction

from sixbirds_foundations_v.sweeps.e6_e9_probe_shop import (
    F,
    run_probe_shop_sweep,
)


def test_e6_e9_probe_shop_confirms_all_registered_predictions() -> None:
    results = run_probe_shop_sweep()

    failures = [comparison for comparison in results.comparisons if not comparison.passed]
    assert failures == []


def test_e6_e9_allocation_registered_values_are_exact() -> None:
    results = run_probe_shop_sweep()

    assert results.allocation_optima[F(1)].weight == (F(4, 5), F(1, 5))
    assert results.allocation_optima[F(1)].discharge == F(14, 3)
    assert results.allocation_optima[F(1)].residual_trace == F(103, 12)
    assert results.allocation_optima[F(1)].marginal_ratios == (F(25, 9), F(25, 9))

    assert results.allocation_optima[F(2)].weight == (F(7, 5), F(3, 5))
    assert results.allocation_optima[F(2)].discharge == F(27, 4)
    assert results.allocation_optima[F(2)].residual_trace == F(13, 2)
    assert results.allocation_optima[F(2)].marginal_ratios == (F(25, 16), F(25, 16))

    assert results.allocation_optima[F(3)].weight == (F(2), F(1))
    assert results.allocation_optima[F(3)].discharge == F(8)
    assert results.allocation_optima[F(3)].residual_trace == F(21, 4)
    assert results.allocation_optima[F(3)].marginal_ratios == (F(1), F(1))

    assert results.slack_allocation.weight == (F(2), F(1))
    assert results.slack_allocation.discharge == F(8)


def test_e6_e9_acquisition_and_arbitration_registered_values_are_exact() -> None:
    results = run_probe_shop_sweep()

    assert all(candidate.saturated for candidate in results.saturated_candidates)
    assert all(not candidate.acquisition_strict for candidate in results.saturated_candidates)
    assert all(candidate.discharge == 0 for candidate in results.saturated_candidates)

    strict_frontier = tuple(
        (candidate.name, candidate.discharge, candidate.ratio)
        for candidate in results.strict_candidates
    )
    assert strict_frontier == (
        ("C", Fraction(1, 4), Fraction(1, 4)),
        ("AC", Fraction(1, 4), Fraction(1, 8)),
        ("BC", Fraction(1, 4), Fraction(1, 16)),
    )
    assert results.allocation_increment_floor == Fraction(15, 14)

    assert results.joint_budget[F(4)].allocation == (F(2), F(1))
    assert results.joint_budget[F(4)].acquisitions == ("C",)
    assert results.joint_budget[F(3)].allocation == (F(2), F(1))
    assert results.joint_budget[F(3)].acquisitions == ()
    assert results.joint_budget[F(2)].allocation_degraded
    assert results.joint_budget[F(1)].allocation_degraded


def test_e6_e9_proxy_and_salience_registered_values_are_exact() -> None:
    results = run_probe_shop_sweep()

    assert results.proxy_discharge_by_budget == {
        F(1): F(2),
        F(2): F(2),
        F(3): F(2),
        F(4): F(2),
    }
    assert results.proxy_residual_trace == F(45, 4)
    assert results.salience_base.top_direction == "A"
    assert results.salience_base.top_magnitude == F(3)
    assert results.salience_shift_b.top_direction == "B"
    assert results.salience_shift_b.top_magnitude == F(8)
    assert len(results.salience_config_hash) == 64
    assert len(results.salience_output_hash) == 64

