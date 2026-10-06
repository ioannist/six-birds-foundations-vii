from foundations_vi_lab.g10_persistence.ducci import (
    check_power_two_nilpotency,
    ducci_linear_operator,
    ducci_step,
    gf2_matrix_pow,
    gf2_zero,
    run_ducci_until_cycle,
)


def test_ducci_step_hardcoded() -> None:
    assert ducci_step((1, 5, 3, 7)) == (4, 2, 4, 6)


def test_k4_ducci_collapse_example() -> None:
    result = run_ducci_until_cycle((1, 5, 3, 7), seed=0, max_steps=32)

    assert result.status == "zero"
    assert result.final == (0, 0, 0, 0)
    assert result.steps <= 32
    assert result.bounded_after_first is True
    assert result.max_after_first <= result.initial_range


def test_gf2_k4_matrix_nilpotency() -> None:
    operator = ducci_linear_operator(4)

    assert gf2_matrix_pow(operator, 4) == gf2_zero(4)
    assert check_power_two_nilpotency(4).is_zero is True
