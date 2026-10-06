"""Hereditary-base Goodstein operations for G2-L1."""

from __future__ import annotations

from dataclasses import dataclass

from foundations_vi_lab.g02_escrow.ordinals import Ordinal, ZERO, finite


@dataclass(frozen=True)
class HereditaryTerm:
    """One term `coefficient * base^exponent` in hereditary base notation."""

    exponent: "HereditaryExpression"
    coefficient: int


HereditaryExpression = tuple[HereditaryTerm, ...]


def hereditary(n: int, base: int) -> HereditaryExpression:
    """Return the hereditary base-`base` expression for `n`."""

    if base < 2:
        raise ValueError("base must be at least 2")
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return ()
    if n < base:
        return (HereditaryTerm((), n),)

    digits: list[tuple[int, int]] = []
    exponent = 0
    remaining = n
    while remaining:
        digit = remaining % base
        if digit:
            digits.append((exponent, digit))
        remaining //= base
        exponent += 1

    return tuple(
        HereditaryTerm(hereditary(power, base), digit)
        for power, digit in reversed(digits)
    )


def evaluate(expr: HereditaryExpression, base: int) -> int:
    """Evaluate a hereditary expression at a concrete integer base."""

    total = 0
    for term in expr:
        total += term.coefficient * (base ** evaluate(term.exponent, base))
    return total


def ordinal_of_expr(expr: HereditaryExpression) -> Ordinal:
    """Replace the hereditary base symbol by omega, producing a CNF ordinal."""

    terms: list[tuple[Ordinal, int]] = []
    for term in expr:
        exponent = ordinal_of_expr(term.exponent)
        terms.append((exponent, term.coefficient))
    return Ordinal(tuple(terms))


def ordinal_assignment(n: int, base: int) -> Ordinal:
    """Compute `O_base(n)`."""

    return ordinal_of_expr(hereditary(n, base))


def rebase(n: int, base: int) -> int:
    """Substitute `base + 1` for `base` in `n`'s hereditary representation."""

    return evaluate(hereditary(n, base), base + 1)


def goodstein_step(n: int, base: int) -> int:
    """Return the Goodstein step `G_base(n)`."""

    if n == 0:
        return 0
    return rebase(n, base) - 1


def expr_to_string(expr: HereditaryExpression, base_symbol: str) -> str:
    """Render a hereditary expression for diagnostics and tests."""

    if not expr:
        return "0"
    parts: list[str] = []
    for term in expr:
        if term.exponent == ():
            part = str(term.coefficient)
        else:
            exp_text = expr_to_string(term.exponent, base_symbol)
            if "^" in exp_text or " + " in exp_text or "*" in exp_text:
                exp_text = f"({exp_text})"
            power = f"{base_symbol}^{exp_text}"
            if term.coefficient == 1:
                part = power
            else:
                part = f"{term.coefficient}*{power}"
        parts.append(part)
    return " + ".join(parts)


@dataclass(frozen=True)
class GoodsteinCheck:
    """One verified Goodstein escrow step."""

    start_n: int
    step: int
    base: int
    n: int
    rebased: int
    next_n: int
    before: str
    rebased_ordinal: str
    after: str


@dataclass(frozen=True)
class GoodsteinSweep:
    """Aggregate deterministic G2-L1 sweep result."""

    max_start: int
    step_budget: int
    checked_steps: int
    terminated_starts: tuple[int, ...]
    max_reached_base: int
    max_integer_bits: int


def verify_step(start_n: int, step: int, base: int, n: int) -> GoodsteinCheck:
    """Verify rebase invariance and strict ordinal descent for one step."""

    before = ordinal_assignment(n, base)
    rebased = rebase(n, base)
    rebased_ordinal = ordinal_assignment(rebased, base + 1)
    if rebased_ordinal != before:
        raise AssertionError(
            f"rebase invariance failed for start={start_n}, step={step}, base={base}"
        )
    next_n = rebased - 1
    after = ordinal_assignment(next_n, base + 1)
    if n != 0 and not (after < before):
        raise AssertionError(
            f"strict descent failed for start={start_n}, step={step}, base={base}"
        )
    return GoodsteinCheck(
        start_n=start_n,
        step=step,
        base=base,
        n=n,
        rebased=rebased,
        next_n=next_n,
        before=str(before),
        rebased_ordinal=str(rebased_ordinal),
        after=str(after),
    )


def run_sweep(max_start: int, step_budget: int) -> GoodsteinSweep:
    """Run the deterministic G2-L1 bounded Goodstein sweep."""

    if max_start < 1:
        raise ValueError("max_start must be positive")
    if step_budget < 1:
        raise ValueError("step_budget must be positive")

    checked_steps = 0
    terminated: list[int] = []
    max_reached_base = 2
    max_integer_bits = 1
    for start in range(1, max_start + 1):
        n = start
        base = 2
        for step in range(step_budget):
            if n == 0:
                terminated.append(start)
                break
            check = verify_step(start, step, base, n)
            checked_steps += 1
            max_reached_base = max(max_reached_base, base + 1)
            max_integer_bits = max(
                max_integer_bits,
                n.bit_length(),
                check.rebased.bit_length(),
                check.next_n.bit_length(),
            )
            n = check.next_n
            base += 1
        else:
            if n == 0:
                terminated.append(start)

    return GoodsteinSweep(
        max_start=max_start,
        step_budget=step_budget,
        checked_steps=checked_steps,
        terminated_starts=tuple(terminated),
        max_reached_base=max_reached_base,
        max_integer_bits=max_integer_bits,
    )


def worked_example() -> dict[str, object]:
    """Return the exact base-2, n=4 example from `THEOREMS.md`."""

    expr_4_base_2 = hereditary(4, 2)
    rebase_4 = rebase(4, 2)
    step_4 = goodstein_step(4, 2)
    return {
        "hereditary_2_4": expr_to_string(expr_4_base_2, "2"),
        "O_2_4": str(ordinal_assignment(4, 2)),
        "rebase_2_to_3_4": rebase_4,
        "O_3_27": str(ordinal_assignment(rebase_4, 3)),
        "G_2_4": step_4,
        "hereditary_3_26": expr_to_string(hereditary(step_4, 3), "3"),
        "O_3_26": str(ordinal_assignment(step_4, 3)),
        "descent": ordinal_assignment(step_4, 3) < ordinal_assignment(4, 2),
        "zero": ZERO.is_zero(),
    }
