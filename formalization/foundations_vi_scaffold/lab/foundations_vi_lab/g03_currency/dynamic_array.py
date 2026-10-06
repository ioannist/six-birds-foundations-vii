"""Dynamic-array amortized-cost calibration for G3."""

from __future__ import annotations

import random
from dataclasses import dataclass

from foundations_vi_lab.g03_currency.ledger import LedgerStep, ledger_preview, telescoping_holds


@dataclass(frozen=True)
class ArrayState:
    """Dynamic-array state tracked by logical size and allocated capacity."""

    size: int
    capacity: int

    def __post_init__(self) -> None:
        if self.size < 0:
            raise ValueError("size must be nonnegative")
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")
        if self.size > self.capacity:
            raise ValueError("size cannot exceed capacity")

    def label(self) -> str:
        """Return a compact state label."""

        return f"size={self.size},capacity={self.capacity}"


def potential(state: ArrayState) -> int:
    """Potential `Phi = max(0, 2*size - capacity)`."""

    return max(0, 2 * state.size - state.capacity)


def insert_step(state: ArrayState, index: int = 1) -> tuple[ArrayState, LedgerStep, bool]:
    """Insert one element under the standard doubling policy."""

    phi_before = potential(state)
    resized = state.size == state.capacity
    if resized:
        new_state = ArrayState(size=state.size + 1, capacity=state.capacity * 2)
        actual_cost = state.size + 1
        operation = "insert_resize"
    else:
        new_state = ArrayState(size=state.size + 1, capacity=state.capacity)
        actual_cost = 1
        operation = "insert"
    step = LedgerStep(
        index=index,
        operation=operation,
        before=state.label(),
        after=new_state.label(),
        actual_cost=actual_cost,
        phi_before=phi_before,
        phi_after=potential(new_state),
    )
    return new_state, step, resized


@dataclass(frozen=True)
class DynamicArrayRunSummary:
    """Summary of the seeded dynamic-array G3 calibration run."""

    seed: int
    length: int
    warmup_inserts: int
    start_state: dict[str, int]
    final_state: dict[str, int]
    total_actual: int
    total_amortized: int
    resize_count: int
    telescoping: bool
    all_amortized_at_most_three: bool
    resize_steps_exact_three: bool
    preview: list[dict[str, object]]


def worked_resize_example() -> dict[str, object]:
    """Return the dynamic-array resize worked example from `THEOREMS.md`."""

    state = ArrayState(size=4, capacity=4)
    new_state, step, resized = insert_step(state)
    return {
        "before": step.before,
        "after": step.after,
        "resized": resized,
        "actual_cost": step.actual_cost,
        "phi_before": step.phi_before,
        "phi_after": step.phi_after,
        "amortized_cost": step.amortized_cost,
        "final_size": new_state.size,
        "final_capacity": new_state.capacity,
    }


def _warm_state(count: int) -> ArrayState:
    """Build a valid dynamic-array state by applying unrecorded warmup inserts."""

    state = ArrayState(size=0, capacity=1)
    for _ in range(count):
        state, _step, _resized = insert_step(state)
    return state


def run_dynamic_array(seed: int, length: int) -> DynamicArrayRunSummary:
    """Run a seeded dynamic-array insertion sequence."""

    rng = random.Random(seed)
    warmup = rng.randrange(0, 32)
    state = _warm_state(warmup)
    start_state = state
    steps: list[LedgerStep] = []
    resize_count = 0
    resize_exact = True
    for index in range(1, length + 1):
        state, step, resized = insert_step(state, index=index)
        steps.append(step)
        if resized:
            resize_count += 1
            resize_exact = resize_exact and step.amortized_cost == 3

    all_bounded = all(step.amortized_cost <= 3 for step in steps)
    if not all_bounded:
        raise AssertionError("dynamic-array amortized cost exceeded 3")
    if not resize_exact:
        raise AssertionError("dynamic-array resize step did not have amortized cost 3")
    if not telescoping_holds(steps):
        raise AssertionError("dynamic-array telescoping identity failed")

    return DynamicArrayRunSummary(
        seed=seed,
        length=length,
        warmup_inserts=warmup,
        start_state={"size": start_state.size, "capacity": start_state.capacity},
        final_state={"size": state.size, "capacity": state.capacity},
        total_actual=sum(step.actual_cost for step in steps),
        total_amortized=sum(step.amortized_cost for step in steps),
        resize_count=resize_count,
        telescoping=True,
        all_amortized_at_most_three=True,
        resize_steps_exact_three=True,
        preview=ledger_preview(steps),
    )
