from foundations_vi_lab.g08_odometer.case_b import run_random_order
from foundations_vi_lab.g08_odometer.sandpile import (
    choose_max,
    choose_min,
    stabilize,
)


def test_small_sandpile_odometer_invariance_min_max() -> None:
    size = 3
    initial = (
        0, 0, 0,
        0, 12, 0,
        0, 0, 0,
    )

    min_result = stabilize(size, initial, seed=1, chooser=choose_min)
    max_result = stabilize(size, initial, seed=2, chooser=choose_max)

    assert min_result.final == max_result.final
    assert min_result.odometer == max_result.odometer
    assert min_result.final == (
        0, 3, 0,
        3, 0, 3,
        0, 3, 0,
    )
    assert min_result.odometer == (
        0, 0, 0,
        0, 3, 0,
        0, 0, 0,
    )


def test_case_b_rewrite_routes_reach_n_with_different_counters() -> None:
    seen = [run_random_order(seed) for seed in range(20)]

    assert {run.final for run in seen} == {"N"}
    counters = {run.counters for run in seen}
    assert len(counters) >= 2
    assert run_random_order(0).route == ("s", "q")
    assert run_random_order(1).route == ("r", "p")
    assert run_random_order(4).route == ("r", "t")
    assert run_random_order(0).counters != run_random_order(1).counters
