"""Tests for the G13 Apollonian curvature census."""

from foundations_vi_lab.g13_saturation.apollonian import (
    ADMISSIBLE_MOD24,
    BASELINE_ROOT,
    RECIPROCITY_ROOT,
    check_obstruction_family,
    descartes_holds,
    generate_orbit,
    reflect,
    summarize_packing,
)


def test_descartes_roots_and_reflection() -> None:
    """Both roots are Descartes quadruples and reflection is exact."""

    assert descartes_holds(BASELINE_ROOT)
    assert descartes_holds(RECIPROCITY_ROOT)
    assert reflect(BASELINE_ROOT, 0) == (15, 2, 2, 3)
    assert reflect(RECIPROCITY_ROOT, 0) == (86, 11, 14, 15)
    assert descartes_holds(reflect(BASELINE_ROOT, 0))
    assert descartes_holds(reflect(RECIPROCITY_ROOT, 0))


def test_small_orbit_residue_admissibility() -> None:
    """Generated positive curvatures stay in the expected mod-24 classes."""

    _, baseline_curvatures = generate_orbit(BASELINE_ROOT, 500)
    _, reciprocity_curvatures = generate_orbit(RECIPROCITY_ROOT, 500)
    assert {value % 24 for value in baseline_curvatures} <= ADMISSIBLE_MOD24
    assert {value % 24 for value in reciprocity_curvatures} <= ADMISSIBLE_MOD24


def test_reciprocity_obstruction_small_bound() -> None:
    """The corrected packing has no generated `2n^2`, `3n^2`, or `6n^2` hits."""

    _, curvatures = generate_orbit(RECIPROCITY_ROOT, 2_000)
    for coefficient in (2, 3, 6):
        check = check_obstruction_family(curvatures, coefficient, 2_000)
        assert check.checked_values > 0
        assert check.hit_values == ()


def test_summary_records_missing_and_coverage() -> None:
    """A compact summary records coverage checkpoints and no residue violations."""

    summary = summarize_packing(
        label="test",
        root=BASELINE_ROOT,
        bound=1_000,
        checkpoints=(100, 1_000),
    )
    assert summary.bound == 1_000
    assert summary.coverage_points[-1].bound == 1_000
    assert summary.residue_violations == ()
    assert summary.missing_count >= 0
