"""Tests for the G5 base-2 reverse-and-add confinement lab."""

from foundations_vi_lab.g05_confinement.reverse_add import (
    PRE_ENTRY_STRINGS,
    PhaseMatch,
    binary,
    classify_phase,
    is_palindrome,
    phase_string,
    pre_entry_orbit,
    reverse_and_add,
    verify_g5_l1,
    worked_first_cycle,
)


def test_worked_first_cycle_exact() -> None:
    """The four first-cycle identities match `THEOREMS.md` exactly."""

    expected = [
        ("10110100", "11100001"),
        ("11100001", "101101000"),
        ("101101000", "110010101"),
        ("110010101", "1011101000"),
    ]
    assert worked_first_cycle() == expected
    for before, after in expected:
        assert binary(reverse_and_add(int(before, 2), 2)) == after


def test_pre_entry_segment_exact() -> None:
    """The seed `22` reaches `P0(2)` through the documented pre-entry segment."""

    assert pre_entry_orbit(22) == PRE_ENTRY_STRINGS
    assert all(not is_palindrome(text) for text in PRE_ENTRY_STRINGS)


def test_phase_matchers_positive_and_negative() -> None:
    """Each phase matcher accepts its exact string and rejects nearby wrong strings."""

    positives = {
        "P0": "10110100",
        "P1": "11100001",
        "P2": "101101000",
        "P3": "110010101",
    }
    for phase, text in positives.items():
        assert phase_string(phase, 2) == text
        assert classify_phase(text) == PhaseMatch(phase=phase, r=2)

    assert classify_phase("10110") is None
    assert classify_phase("11100000") is None
    assert classify_phase("10110101") is None
    assert classify_phase("110010100") is None


def test_short_confinement_sweep() -> None:
    """A short sweep checks the same logic used by the full CLI run."""

    summary = verify_g5_l1(seed=22, cycles=3)
    assert summary.phase_transitions == 12
    assert summary.final_binary == "10111110100000"
    assert summary.final_r == 5
    assert all(not record.palindrome for record in summary.records)
