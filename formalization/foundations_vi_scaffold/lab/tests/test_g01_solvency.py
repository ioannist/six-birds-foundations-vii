"""Tests for the G1 Collatz affine-ledger lab."""

from foundations_vi_lab.g01_solvency.collatz_ledger import (
    accelerated_step,
    audit_orbit,
    nu_2,
    verify_checkpoint,
)
from foundations_vi_lab.g01_solvency.bad_tail import (
    first_descent_step,
    sweep_first_descent,
    verify_ghost_family_member,
)
from foundations_vi_lab.g01_solvency.ghost_toy import (
    classify_all_residues,
    classify_residue,
    finite_transition,
    ghost_residue,
)
from foundations_vi_lab.g01_solvency.aliquot import (
    SigmaComputer,
    brute_sigma,
    track_aliquot_orbit,
    verify_sigma_spot_checks,
)


def test_nu_2_hand_values() -> None:
    """The 2-adic valuation is computed exactly by trailing powers of two."""

    assert nu_2(1) == 0
    assert nu_2(2) == 1
    assert nu_2(12) == 2
    assert nu_2(40) == 3
    assert nu_2(1024) == 10


def test_accelerated_step_hand_values() -> None:
    """Small accelerated Collatz steps match direct hand computation."""

    assert accelerated_step(1) == (1, 2)
    assert accelerated_step(3) == (5, 1)
    assert accelerated_step(5) == (1, 4)
    assert accelerated_step(7) == (11, 1)


def test_hand_traced_orbit_n3() -> None:
    """For `n=3`, the ledger descends at `k=2` with `A_2=5`, `B_2=5`."""

    audit = audit_orbit(3, keep_checkpoints=True)
    checkpoints = audit.checkpoints
    assert audit.descent_step == 2
    assert [checkpoint.n_k for checkpoint in checkpoints] == [3, 5, 1]
    assert [checkpoint.A_k for checkpoint in checkpoints] == [0, 1, 5]
    assert [checkpoint.B_k for checkpoint in checkpoints] == [0, 1, 5]
    assert checkpoints[2].ledger_numerator == 3**2 * 3 + 5
    assert checkpoints[2].ledger_denominator == 2**5
    assert checkpoints[2].descends is True
    assert checkpoints[2].certificate_descends is True


def test_hand_traced_orbit_n5() -> None:
    """For `n=5`, one accelerated step descends to `1`."""

    audit = audit_orbit(5, keep_checkpoints=True)
    checkpoints = audit.checkpoints
    assert audit.descent_step == 1
    assert [checkpoint.n_k for checkpoint in checkpoints] == [5, 1]
    assert checkpoints[1].A_k == 4
    assert checkpoints[1].B_k == 1
    assert checkpoints[1].ledger_numerator == 16
    assert checkpoints[1].ledger_denominator == 16
    assert checkpoints[1].descends == checkpoints[1].certificate_descends


def test_hand_traced_orbit_n7_b_recurrence_indexing() -> None:
    """The `B_{j+1}=3B_j+2^A_j` recurrence uses pre-step `A_j`."""

    audit = audit_orbit(7, keep_checkpoints=True)
    checkpoints = audit.checkpoints
    assert audit.descent_step == 4
    assert [checkpoint.n_k for checkpoint in checkpoints] == [7, 11, 17, 13, 5]
    assert [checkpoint.A_k for checkpoint in checkpoints] == [0, 1, 2, 4, 7]
    assert [checkpoint.B_k for checkpoint in checkpoints] == [0, 1, 5, 19, 73]
    assert checkpoints[4].ledger_numerator == 3**4 * 7 + 73
    assert checkpoints[4].ledger_denominator == 2**7
    assert checkpoints[4].descends is True


def test_certificate_equivalence_direct_checkpoint() -> None:
    """The multiplied-through descent certificate agrees with direct descent."""

    checkpoint = verify_checkpoint(
        start=3,
        k=2,
        n_k=1,
        A_k=5,
        B_k=5,
        pow3_k=9,
        a_previous=4,
    )
    assert checkpoint.descends is True
    assert checkpoint.certificate_descends is True
    assert checkpoint.ledger_numerator == 32
    assert checkpoint.ledger_denominator == 32


def test_first_descent_small_membrane_sizes() -> None:
    """Odd starts below 10 give a hand-checkable `k*` histogram."""

    summary = sweep_first_descent(10, max_steps=20)
    assert summary.tested_odd_count == 5
    assert summary.terminal_fixed_count == 1
    assert summary.nonterminal_count == 4
    assert summary.histogram == {1: 2, 2: 1, 4: 1}
    assert summary.membrane_sizes[0] == 4
    assert summary.membrane_sizes[1] == 2
    assert summary.membrane_sizes[2] == 1
    assert summary.membrane_sizes[3] == 1
    assert summary.membrane_sizes[4] == 0


def test_first_descent_step_terminal_and_small_values() -> None:
    """The lightweight first-descent helper matches hand-traced values."""

    assert first_descent_step(1).terminal_fixed is True
    assert first_descent_step(1).first_descent_step is None
    assert first_descent_step(3).first_descent_step == 2
    assert first_descent_step(5).first_descent_step == 1
    assert first_descent_step(7).first_descent_step == 4


def test_ghost_family_l3_shadowing_prefix() -> None:
    """For `L=3`, `2^L-1=7` shadows for `L-1` steps exactly."""

    record = verify_ghost_family_member(3, max_steps=20)
    assert record.start == 7
    assert record.shadow_steps == 2
    assert record.valuations == (1, 1)
    assert record.shadow_valuations_all_one is True
    assert record.closed_form_agrees is True
    assert record.predicted_k_star == 2
    assert record.first_descent_step == 4
    assert record.predicted_k_star_matches is False


def test_finite_ghost_residue_for_tiny_ring() -> None:
    """For `m=6`, the declared ghost residue is `(2^6-1)/3 = 21`."""

    assert ghost_residue(6) == 21
    transition = finite_transition(21, m=6)
    assert transition.reaches_declared_ghost is True
    assert transition.next_residue is None


def test_finite_ghost_toy_hand_descent() -> None:
    """Residue `5 mod 64` descends normally to `1` in one step."""

    classification = classify_residue(5, m=6)
    assert classification.kind == "descends"
    assert classification.steps == 1
    assert classification.descent_value == 1


def test_finite_ghost_toy_hand_ghost_bound() -> None:
    """The declared ghost residue reaches the absorbing ghost before descent."""

    classification = classify_residue(21, m=6)
    assert classification.kind == "declared_ghost"
    assert classification.steps == 1
    assert classification.trajectory == (21,)
    assert classification.descent_value is None


def test_finite_ghost_toy_exhaustive_m6() -> None:
    """The tiny `m=6` toy classifies every odd residue with no timeout."""

    summary = classify_all_residues(6)
    assert summary.odd_residue_count == 32
    assert summary.ghost_residue == 21
    assert summary.terminal_residue == 1
    assert summary.unclassified_count == 0
    assert summary.descended_count + summary.ghost_bound_count + summary.bad_cycle_start_count == 32
    assert 1 not in summary.gamma_nonterminal_residues
    assert summary.genuine_bad_cycle_count == 0
    assert summary.native_separation_verified is True
    assert summary.ghost_convergence_verified is True


def test_aliquot_sigma_exact_values() -> None:
    """Factorized `sigma` agrees with hand-known divisor sums."""

    computer = SigmaComputer(10**6)
    assert computer.sigma(1) == 1
    assert computer.sigma(2) == 3
    assert computer.sigma(6) == 12
    assert computer.sigma(12) == 28
    assert computer.sigma(28) == 56
    assert computer.sigma(220) == 504
    assert computer.sigma(284) == 504
    assert computer.aliquot(220) == 284
    assert computer.aliquot(284) == 220


def test_aliquot_sigma_bruteforce_spot_checks() -> None:
    """The factorized sigma path matches brute force on a small range."""

    computer = SigmaComputer(10**6)
    assert verify_sigma_spot_checks(computer, limit=200)
    for n in (1, 13, 36, 97, 220):
        assert computer.sigma(n) == brute_sigma(n)


def test_aliquot_amicable_pair_cycle_and_ledger_projection() -> None:
    """Starting from `220` detects the exact `220 <-> 284` amicable pair."""

    computer = SigmaComputer(10**6)
    result = track_aliquot_orbit(220, computer, max_steps=10, keep_ledger=True)
    assert result.status == "cycle"
    assert result.cycle == (220, 284)
    assert [step.value for step in result.ledger[:2]] == [220, 284]
    assert [step.aliquot for step in result.ledger[:2]] == [284, 220]
    assert [step.nu2_sigma for step in result.ledger[:2]] == [3, 3]


def test_aliquot_prime_terminates_and_perfect_number_fixes() -> None:
    """A prime reaches `0`; a perfect number is a fixed-point cycle."""

    computer = SigmaComputer(10**6)
    prime_result = track_aliquot_orbit(13, computer, max_steps=10)
    assert prime_result.status == "terminated_zero"
    assert prime_result.steps == 2

    perfect_result = track_aliquot_orbit(6, computer, max_steps=10)
    assert perfect_result.status == "cycle"
    assert perfect_result.cycle == (6,)
