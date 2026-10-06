"""Tests for the G9 Rule 184 transport lab."""

from foundations_vi_lab.g09_transport.rule184 import (
    RULE184_TABLE,
    normalize_state,
    rule184_step_local,
    rule184_step_particles,
    rule184_step_wolfram,
    state_to_string,
    verify_rule184_formulations,
)


def test_wolfram_rule_184_table() -> None:
    """Rule number 184 is binary `10111000` on Wolfram neighborhood order."""

    neighborhoods = [
        (1, 1, 1),
        (1, 1, 0),
        (1, 0, 1),
        (1, 0, 0),
        (0, 1, 1),
        (0, 1, 0),
        (0, 0, 1),
        (0, 0, 0),
    ]
    outputs = [RULE184_TABLE[neighborhood] for neighborhood in neighborhoods]
    assert outputs == [1, 0, 1, 1, 1, 0, 0, 0]


def test_three_rule_184_formulations_agree() -> None:
    """Local formula, particle motion, and Wolfram table agree exactly."""

    states = [
        normalize_state("111000"),
        normalize_state("101010"),
        normalize_state("10010000"),
        normalize_state("01101100"),
        normalize_state("0001"),
    ]
    verify_rule184_formulations(states)
    for state in states:
        assert rule184_step_local(state) == rule184_step_particles(state)
        assert rule184_step_local(state) == rule184_step_wolfram(state)


def test_hand_checked_multistep_trace() -> None:
    """Two isolated cars on an 8-ring move one cell right per step."""

    state = normalize_state("10010000")
    expected = [
        "10010000",
        "01001000",
        "00100100",
        "00010010",
    ]
    observed = [state_to_string(state)]
    for _ in range(3):
        state = rule184_step_local(state)
        observed.append(state_to_string(state))
    assert observed == expected


def test_local_table_center_output() -> None:
    """Each explicit neighborhood gives the Wolfram-table center output."""

    for (left, center, right), output in RULE184_TABLE.items():
        state = normalize_state((0, left, center, right, 0))
        assert rule184_step_wolfram(state)[2] == output
        assert rule184_step_local(state)[2] == output
