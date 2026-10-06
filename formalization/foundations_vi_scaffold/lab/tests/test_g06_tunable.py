"""Tests for the G6-L2 tunable Recaman variants."""

from foundations_vi_lab.g06_needle.tunable import (
    even_jump_terms,
    unit_jump_terms,
    verify_even_jump_variant,
    verify_unit_jump_variant,
)


def test_even_jump_terms_are_even() -> None:
    """Variant A starts 0,2,6,12,4 and stays even on the checked prefix."""

    terms = even_jump_terms(10)
    assert terms[:5] == (0, 2, 6, 12, 4)
    assert all(value % 2 == 0 for value in terms)


def test_unit_jump_terms_count_up() -> None:
    """Variant B is exactly 0,1,2,3,... on the checked prefix."""

    assert unit_jump_terms(20) == tuple(range(21))


def test_even_jump_verification_summary() -> None:
    """Variant A verification records no odd violations."""

    summary = verify_even_jump_variant(1000)
    assert summary.all_even
    assert summary.odd_violations == ()


def test_unit_jump_verification_summary() -> None:
    """Variant B verification records exact identity and visited-set equality."""

    summary = verify_unit_jump_variant(1000)
    assert summary.identity_holds
    assert summary.visited_set_exact
    assert summary.unique_visited == 1001
