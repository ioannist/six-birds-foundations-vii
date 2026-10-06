"""Exact accelerated-Collatz affine ledger checks for G1-L1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LedgerCheckpoint:
    """One checked horizon in the accelerated Collatz affine ledger."""

    k: int
    n_k: int
    a_previous: int | None
    A_k: int
    B_k: int
    pow3_k: int
    ledger_numerator: int
    ledger_denominator: int
    descends: bool
    certificate_descends: bool


@dataclass(frozen=True)
class OrbitAudit:
    """Audit result for one starting odd integer."""

    start: int
    checkpoints: tuple[LedgerCheckpoint, ...]
    descent_step: int | None
    terminal_reached: bool
    capped: bool


@dataclass(frozen=True)
class SweepSummary:
    """Aggregate output for the G1-L1 sweep."""

    limit: int
    max_steps: int
    tested_odd_count: int
    nonterminal_count: int
    terminal_fixed_count: int
    descended_count: int
    capped_count: int
    total_checkpoints: int
    max_descent_step: int
    max_descent_start: int
    max_A_k: int
    max_B_bits: int
    max_n_k_bits: int
    elapsed_seconds: float


def nu_2(value: int) -> int:
    """Return the exact exponent of 2 dividing a nonzero integer."""

    if value == 0:
        raise ValueError("nu_2 is undefined for 0")
    value = abs(value)
    return (value & -value).bit_length() - 1


def accelerated_step(n: int) -> tuple[int, int]:
    """Return `(T(n), a(n))` for odd positive `n`."""

    if n <= 0 or n % 2 == 0:
        raise ValueError("accelerated_step expects a positive odd integer")
    m = 3 * n + 1
    a = nu_2(m)
    next_n = m >> a
    if next_n % 2 != 1:
        raise AssertionError("accelerated Collatz step did not return an odd integer")
    return next_n, a


def verify_checkpoint(
    *,
    start: int,
    k: int,
    n_k: int,
    A_k: int,
    B_k: int,
    pow3_k: int,
    a_previous: int | None,
) -> LedgerCheckpoint:
    """Verify one exact affine-ledger checkpoint and return its record."""

    denominator = 1 << A_k
    numerator = pow3_k * start + B_k
    remainder = numerator % denominator
    if remainder != 0:
        raise AssertionError(
            f"ledger division was not exact for n={start}, k={k}: remainder={remainder}"
        )
    ledger_value = numerator // denominator
    if ledger_value != n_k:
        raise AssertionError(
            f"ledger mismatch for n={start}, k={k}: ledger={ledger_value}, direct={n_k}"
        )

    descends = n_k < start
    certificate_descends = denominator * start > numerator
    if descends != certificate_descends:
        raise AssertionError(
            "descent certificate mismatch for "
            f"n={start}, k={k}: direct={descends}, certificate={certificate_descends}"
        )

    return LedgerCheckpoint(
        k=k,
        n_k=n_k,
        a_previous=a_previous,
        A_k=A_k,
        B_k=B_k,
        pow3_k=pow3_k,
        ledger_numerator=numerator,
        ledger_denominator=denominator,
        descends=descends,
        certificate_descends=certificate_descends,
    )


def audit_orbit(start: int, *, max_steps: int = 1000, keep_checkpoints: bool = False) -> OrbitAudit:
    """Verify the affine ledger for one odd start through first descent.

    The terminal fixed point `1` is checked through one accelerated step and
    reported as terminal rather than descended.
    """

    if start <= 0 or start % 2 == 0:
        raise ValueError("audit_orbit expects a positive odd start")

    checkpoints: list[LedgerCheckpoint] = []
    n_k = start
    A_k = 0
    B_k = 0
    pow3_k = 1
    a_previous: int | None = None

    for k in range(max_steps + 1):
        checkpoint = verify_checkpoint(
            start=start,
            k=k,
            n_k=n_k,
            A_k=A_k,
            B_k=B_k,
            pow3_k=pow3_k,
            a_previous=a_previous,
        )
        if keep_checkpoints:
            checkpoints.append(checkpoint)

        if k > 0 and n_k < start:
            return OrbitAudit(
                start=start,
                checkpoints=tuple(checkpoints),
                descent_step=k,
                terminal_reached=(n_k == 1),
                capped=False,
            )

        if start == 1 and k == 1 and n_k == 1:
            return OrbitAudit(
                start=start,
                checkpoints=tuple(checkpoints),
                descent_step=None,
                terminal_reached=True,
                capped=False,
            )

        if k == max_steps:
            return OrbitAudit(
                start=start,
                checkpoints=tuple(checkpoints),
                descent_step=None,
                terminal_reached=(n_k == 1),
                capped=True,
            )

        A_before = A_k
        next_n, a_j = accelerated_step(n_k)
        B_k = 3 * B_k + (1 << A_before)
        A_k = A_before + a_j
        pow3_k *= 3
        n_k = next_n
        a_previous = a_j

    raise AssertionError("unreachable audit loop exit")


def sweep_odd_starts(limit: int, *, max_steps: int = 1000) -> SweepSummary:
    """Run G1-L1 over every positive odd `n < limit`."""

    if limit <= 1:
        raise ValueError("limit must be greater than 1")

    import time

    started = time.perf_counter()
    tested = 0
    nonterminal = 0
    terminal_fixed = 0
    descended = 0
    capped = 0
    total_checkpoints = 0
    max_descent_step = 0
    max_descent_start = 0
    max_A_k = 0
    max_B_bits = 0
    max_n_k_bits = 0

    for start in range(1, limit, 2):
        tested += 1
        audit = audit_orbit(start, max_steps=max_steps, keep_checkpoints=True)
        total_checkpoints += len(audit.checkpoints)
        if start == 1:
            terminal_fixed += 1
        else:
            nonterminal += 1

        if audit.capped:
            capped += 1
        if audit.descent_step is not None:
            descended += 1
            if audit.descent_step > max_descent_step:
                max_descent_step = audit.descent_step
                max_descent_start = start

        for checkpoint in audit.checkpoints:
            max_A_k = max(max_A_k, checkpoint.A_k)
            max_B_bits = max(max_B_bits, checkpoint.B_k.bit_length())
            max_n_k_bits = max(max_n_k_bits, checkpoint.n_k.bit_length())

    elapsed = time.perf_counter() - started
    return SweepSummary(
        limit=limit,
        max_steps=max_steps,
        tested_odd_count=tested,
        nonterminal_count=nonterminal,
        terminal_fixed_count=terminal_fixed,
        descended_count=descended,
        capped_count=capped,
        total_checkpoints=total_checkpoints,
        max_descent_step=max_descent_step,
        max_descent_start=max_descent_start,
        max_A_k=max_A_k,
        max_B_bits=max_B_bits,
        max_n_k_bits=max_n_k_bits,
        elapsed_seconds=elapsed,
    )

