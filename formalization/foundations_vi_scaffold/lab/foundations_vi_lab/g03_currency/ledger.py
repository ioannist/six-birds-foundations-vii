"""Exact integer ledger helpers for G3 amortized-cost checks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LedgerStep:
    """One audited operation step in a finite amortized-cost run."""

    index: int
    operation: str
    before: str
    after: str
    actual_cost: int
    phi_before: int
    phi_after: int

    @property
    def amortized_cost(self) -> int:
        """Return `a_i + Phi(s_i) - Phi(s_{i-1})` exactly."""

        return self.actual_cost + self.phi_after - self.phi_before


def total_actual(steps: list[LedgerStep]) -> int:
    """Sum the actual costs in a ledger."""

    return sum(step.actual_cost for step in steps)


def total_amortized(steps: list[LedgerStep]) -> int:
    """Sum the amortized costs in a ledger."""

    return sum(step.amortized_cost for step in steps)


def telescoping_rhs(steps: list[LedgerStep]) -> int:
    """Compute `sum a_hat_i + Phi(s_0) - Phi(s_n)` for a nonempty ledger."""

    if not steps:
        return 0
    return total_amortized(steps) + steps[0].phi_before - steps[-1].phi_after


def telescoping_holds(steps: list[LedgerStep]) -> bool:
    """Check the G3 telescoping identity exactly."""

    return total_actual(steps) == telescoping_rhs(steps)


def ledger_preview(steps: list[LedgerStep], limit: int = 5) -> list[dict[str, object]]:
    """Return a compact JSON-friendly prefix of a ledger."""

    return [
        {
            "index": step.index,
            "operation": step.operation,
            "before": step.before,
            "after": step.after,
            "actual_cost": step.actual_cost,
            "phi_before": step.phi_before,
            "phi_after": step.phi_after,
            "amortized_cost": step.amortized_cost,
        }
        for step in steps[:limit]
    ]
