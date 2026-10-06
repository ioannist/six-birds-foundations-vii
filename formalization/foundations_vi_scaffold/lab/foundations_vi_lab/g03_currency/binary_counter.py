"""Binary-counter amortized-cost calibration for G3."""

from __future__ import annotations

import random
from dataclasses import dataclass

from foundations_vi_lab.g03_currency.ledger import LedgerStep, ledger_preview, telescoping_holds


def potential(value: int) -> int:
    """Potential `Phi`: the number of `1` bits."""

    if value < 0:
        raise ValueError("binary counter value must be nonnegative")
    return value.bit_count()


def trailing_ones(value: int) -> int:
    """Count the trailing one bits in a nonnegative integer."""

    if value < 0:
        raise ValueError("binary counter value must be nonnegative")
    count = 0
    while (value >> count) & 1:
        count += 1
    return count


def bits(value: int, width: int = 0) -> str:
    """Format a nonnegative integer as a zero-padded binary string."""

    if value < 0:
        raise ValueError("binary counter value must be nonnegative")
    actual_width = max(width, 1, value.bit_length())
    return format(value, f"0{actual_width}b")


def increment_step(value: int, index: int = 1, width: int = 0) -> LedgerStep:
    """Increment the binary counter once and return the audited ledger step."""

    r = trailing_ones(value)
    new_value = value + 1
    display_width = max(width, value.bit_length(), new_value.bit_length(), 1)
    return LedgerStep(
        index=index,
        operation=f"increment(r={r})",
        before=bits(value, display_width),
        after=bits(new_value, display_width),
        actual_cost=r + 1,
        phi_before=potential(value),
        phi_after=potential(new_value),
    )


@dataclass(frozen=True)
class BinaryRunSummary:
    """Summary of the seeded binary-counter G3 calibration run."""

    seed: int
    length: int
    start_value: int
    final_value: int
    total_actual: int
    total_amortized: int
    max_trailing_ones: int
    telescoping: bool
    all_amortized_exact_two: bool
    preview: list[dict[str, object]]


def worked_examples() -> dict[str, dict[str, object]]:
    """Return the two binary-counter worked examples from `THEOREMS.md`."""

    carry = increment_step(0b0111, width=4)
    noncarry = increment_step(0b0100, width=4)
    return {
        "carry_0111_to_1000": {
            "before": carry.before,
            "after": carry.after,
            "actual_cost": carry.actual_cost,
            "phi_before": carry.phi_before,
            "phi_after": carry.phi_after,
            "amortized_cost": carry.amortized_cost,
        },
        "noncarry_0100_to_0101": {
            "before": noncarry.before,
            "after": noncarry.after,
            "actual_cost": noncarry.actual_cost,
            "phi_before": noncarry.phi_before,
            "phi_after": noncarry.phi_after,
            "amortized_cost": noncarry.amortized_cost,
        },
    }


def run_binary_counter(seed: int, length: int) -> BinaryRunSummary:
    """Run a seeded binary-counter increment sequence."""

    rng = random.Random(seed)
    value = rng.randrange(0, 1 << 16)
    start_value = value
    steps: list[LedgerStep] = []
    max_r = 0
    for index in range(1, length + 1):
        step = increment_step(value, index=index)
        steps.append(step)
        max_r = max(max_r, trailing_ones(value))
        value += 1

    all_exact = all(step.amortized_cost == 2 for step in steps)
    if not all_exact:
        raise AssertionError("binary counter amortized cost was not exactly 2")
    if not telescoping_holds(steps):
        raise AssertionError("binary counter telescoping identity failed")

    return BinaryRunSummary(
        seed=seed,
        length=length,
        start_value=start_value,
        final_value=value,
        total_actual=sum(step.actual_cost for step in steps),
        total_amortized=sum(step.amortized_cost for step in steps),
        max_trailing_ones=max_r,
        telescoping=True,
        all_amortized_exact_two=True,
        preview=ledger_preview(steps),
    )
