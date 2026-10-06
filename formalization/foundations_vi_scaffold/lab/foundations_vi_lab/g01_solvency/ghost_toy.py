"""Finite residue-ring ghost toy for G1-L3."""

from __future__ import annotations

import time
from dataclasses import dataclass

from foundations_vi_lab.g01_solvency.collatz_ledger import nu_2


@dataclass(frozen=True)
class ToyTransition:
    """Transition result in the finite residue-ring toy."""

    next_residue: int | None
    valuation: int | None
    reaches_declared_ghost: bool


@dataclass(frozen=True)
class ResidueClassification:
    """Classification of one odd residue in the finite toy."""

    start: int
    kind: str
    steps: int
    trajectory: tuple[int, ...]
    descent_value: int | None
    cycle: tuple[int, ...]


@dataclass(frozen=True)
class GhostToySummary:
    """Exhaustive G1-L3 finite-toy classification summary."""

    m: int
    modulus: int
    odd_residue_count: int
    ghost_residue: int
    ghost_residue_formula: str
    terminal_residue: int
    descended_count: int
    ghost_bound_count: int
    bad_cycle_start_count: int
    bad_cycle_count: int
    nonterminal_residue_count: int
    gamma_nonterminal_residues: tuple[int, ...]
    genuine_bad_cycle_start_count: int
    genuine_bad_cycle_count: int
    genuine_bad_cycles: tuple[tuple[int, ...], ...]
    unclassified_count: int
    max_descent_step: int
    max_descent_start: int
    gamma_residues: tuple[int, ...]
    ghost_bound_residues: tuple[int, ...]
    bad_cycles: tuple[tuple[int, ...], ...]
    native_separation_verified: bool
    ghost_convergence_verified: bool
    elapsed_seconds: float


def ghost_residue(m: int) -> int:
    """Return the unique odd residue with `3*r + 1 == 0 mod 2^m`."""

    if m < 2:
        raise ValueError("m must be at least 2")
    modulus = 1 << m
    return (-pow(3, -1, modulus)) % modulus


def ghost_residue_formula(m: int) -> str:
    """Return a closed-form description for the unique ghost residue."""

    if m % 2 == 0:
        return f"(2^{m} - 1) / 3"
    return f"(2^{m + 1} - 1) / 3 mod 2^{m}"


def finite_transition(residue: int, *, m: int) -> ToyTransition:
    """Apply the declared finite-ring lift rule to one odd residue."""

    modulus = 1 << m
    if residue <= 0 or residue >= modulus or residue % 2 == 0:
        raise ValueError("residue must be an odd canonical representative")
    s = (3 * residue + 1) % modulus
    if s == 0:
        return ToyTransition(next_residue=None, valuation=None, reaches_declared_ghost=True)
    valuation = nu_2(s)
    next_residue = s >> valuation
    if next_residue % 2 != 1:
        raise AssertionError("finite transition did not return an odd residue")
    return ToyTransition(
        next_residue=next_residue,
        valuation=valuation,
        reaches_declared_ghost=False,
    )


def classify_residue(start: int, *, m: int) -> ResidueClassification:
    """Classify one odd residue as descending, ghost-bound, or bad-cycle."""

    modulus = 1 << m
    if start <= 0 or start >= modulus or start % 2 == 0:
        raise ValueError("start must be an odd canonical representative")

    seen: dict[int, int] = {}
    trajectory: list[int] = []
    current = start
    bound = modulus // 2 + 1

    for step in range(bound + 1):
        if step > 0 and current < start:
            return ResidueClassification(
                start=start,
                kind="descends",
                steps=step,
                trajectory=tuple(trajectory),
                descent_value=current,
                cycle=(),
            )

        if current in seen:
            cycle_start = seen[current]
            cycle = tuple(trajectory[cycle_start:])
            if any(value < start for value in cycle):
                raise AssertionError("cycle classification encountered a descending value")
            return ResidueClassification(
                start=start,
                kind="bad_cycle",
                steps=step,
                trajectory=tuple(trajectory),
                descent_value=None,
                cycle=cycle,
            )

        seen[current] = step
        trajectory.append(current)
        transition = finite_transition(current, m=m)
        if transition.reaches_declared_ghost:
            return ResidueClassification(
                start=start,
                kind="declared_ghost",
                steps=step + 1,
                trajectory=tuple(trajectory),
                descent_value=None,
                cycle=(),
            )
        if transition.next_residue is None:
            raise AssertionError("non-ghost transition lacked a next residue")
        current = transition.next_residue

    return ResidueClassification(
        start=start,
        kind="unclassified",
        steps=bound,
        trajectory=tuple(trajectory),
        descent_value=None,
        cycle=(),
    )


def classify_all_residues(m: int) -> GhostToySummary:
    """Exhaustively classify every odd residue in `Z/2^m`."""

    started = time.perf_counter()
    modulus = 1 << m
    ghost = ghost_residue(m)
    terminal = 1

    descended_count = 0
    ghost_bound: list[int] = []
    bad_cycle_starts: list[int] = []
    unclassified: list[int] = []
    cycles_seen: dict[tuple[int, ...], tuple[int, ...]] = {}
    max_descent_step = 0
    max_descent_start = 0

    for start in range(1, modulus, 2):
        classification = classify_residue(start, m=m)
        if classification.kind == "descends":
            descended_count += 1
            if classification.steps > max_descent_step:
                max_descent_step = classification.steps
                max_descent_start = start
        elif classification.kind == "declared_ghost":
            ghost_bound.append(start)
        elif classification.kind == "bad_cycle":
            bad_cycle_starts.append(start)
            canonical = _canonical_cycle(classification.cycle)
            cycles_seen[canonical] = canonical
        else:
            unclassified.append(start)

    gamma = tuple(sorted(set(ghost_bound).union(bad_cycle_starts)))
    bad_cycles = tuple(sorted(cycles_seen.values()))
    gamma_nonterminal = tuple(value for value in gamma if value != terminal)
    genuine_bad_cycles = tuple(cycle for cycle in bad_cycles if cycle != (terminal,))
    genuine_bad_cycle_starts = tuple(value for value in bad_cycle_starts if value != terminal)
    native_separation_verified = (
        len(unclassified) == 0
        and descended_count + len(gamma_nonterminal) + 1 == modulus // 2
    )
    ghost_convergence_verified = len(unclassified) == 0 and all(
        _gamma_residue_never_descends(start, m=m) for start in gamma_nonterminal
    )

    elapsed = time.perf_counter() - started
    return GhostToySummary(
        m=m,
        modulus=modulus,
        odd_residue_count=modulus // 2,
        ghost_residue=ghost,
        ghost_residue_formula=ghost_residue_formula(m),
        terminal_residue=terminal,
        descended_count=descended_count,
        ghost_bound_count=len(ghost_bound),
        bad_cycle_start_count=len(bad_cycle_starts),
        bad_cycle_count=len(bad_cycles),
        nonterminal_residue_count=modulus // 2 - 1,
        gamma_nonterminal_residues=gamma_nonterminal,
        genuine_bad_cycle_start_count=len(genuine_bad_cycle_starts),
        genuine_bad_cycle_count=len(genuine_bad_cycles),
        genuine_bad_cycles=genuine_bad_cycles,
        unclassified_count=len(unclassified),
        max_descent_step=max_descent_step,
        max_descent_start=max_descent_start,
        gamma_residues=gamma,
        ghost_bound_residues=tuple(ghost_bound),
        bad_cycles=bad_cycles,
        native_separation_verified=native_separation_verified,
        ghost_convergence_verified=ghost_convergence_verified,
        elapsed_seconds=elapsed,
    )


def _canonical_cycle(cycle: tuple[int, ...]) -> tuple[int, ...]:
    """Rotate a cycle to a deterministic least lexicographic representative."""

    if not cycle:
        return cycle
    rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
    return min(rotations)


def _gamma_residue_never_descends(start: int, *, m: int) -> bool:
    """Recheck that a gamma start reaches ghost/cycle before any descent."""

    classification = classify_residue(start, m=m)
    return classification.kind in {"declared_ghost", "bad_cycle"}
