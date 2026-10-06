from foundations_vi_lab.g02_escrow.goodstein import (
    goodstein_step,
    ordinal_assignment,
    rebase,
    run_sweep,
    worked_example,
)
from foundations_vi_lab.g02_escrow.ordinals import finite, omega_power


def test_worked_example_from_theorems() -> None:
    example = worked_example()

    assert example["hereditary_2_4"] == "2^(2^1)"
    assert example["O_2_4"] == "omega^omega"
    assert example["rebase_2_to_3_4"] == 27
    assert example["O_3_27"] == "omega^omega"
    assert example["G_2_4"] == 26
    assert example["hereditary_3_26"] == "2*3^2 + 2*3^1 + 2"
    assert example["O_3_26"] == "omega^2*2 + omega*2 + 2"
    assert example["descent"] is True


def test_worked_example_expected_tree_shape() -> None:
    omega = omega_power(finite(1))
    omega_omega = omega_power(omega)
    omega2_times2_plus_omega_times2_plus2 = (
        omega_power(finite(2), 2).terms
        + omega_power(finite(1), 2).terms
        + finite(2).terms
    )

    assert ordinal_assignment(4, 2) == omega_omega
    assert ordinal_assignment(26, 3).terms == omega2_times2_plus_omega_times2_plus2
    assert ordinal_assignment(26, 3) < ordinal_assignment(4, 2)


def test_small_goodstein_descent_and_rebase_invariance() -> None:
    for n in range(1, 8):
        base = 2
        before = ordinal_assignment(n, base)
        rebased = rebase(n, base)
        assert ordinal_assignment(rebased, base + 1) == before
        after_n = goodstein_step(n, base)
        assert ordinal_assignment(after_n, base + 1) < before


def test_short_sweep_runs_exactly() -> None:
    sweep = run_sweep(max_start=5, step_budget=16)
    assert sweep.checked_steps > 0
    assert 1 in sweep.terminated_starts
