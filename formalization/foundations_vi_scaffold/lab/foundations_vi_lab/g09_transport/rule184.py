"""Exact Rule 184 simulation and transport-certificate checks."""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import gcd


BitState = tuple[int, ...]

RULE184_TABLE: dict[tuple[int, int, int], int] = {
    (1, 1, 1): 1,
    (1, 1, 0): 0,
    (1, 0, 1): 1,
    (1, 0, 0): 1,
    (0, 1, 1): 1,
    (0, 1, 0): 0,
    (0, 0, 1): 0,
    (0, 0, 0): 0,
}


@dataclass(frozen=True)
class RecurrenceCertificate:
    """Exact recurrence-with-displacement certificate for a checked tail."""

    tau: int
    displacement: int
    checked_windows: int


@dataclass(frozen=True)
class Rule184DensityResult:
    """Result for one Rule 184 density setting."""

    length: int
    density_label: str
    cars: int
    realized_density: str
    regime: str
    seed: int
    max_steps: int
    evacuation_measure: str
    evacuation_step: int
    final_blocked_cars: int
    final_blocked_holes: int
    recurrence: RecurrenceCertificate
    transporter: str
    census_samples: list[dict[str, int]]


def normalize_state(state: list[int] | tuple[int, ...] | str) -> BitState:
    """Convert a bit list/tuple/string into a checked immutable state."""

    if isinstance(state, str):
        bits = tuple(1 if char == "1" else 0 if char == "0" else -1 for char in state)
    else:
        bits = tuple(state)
    if not bits:
        raise ValueError("state must be nonempty")
    if any(bit not in (0, 1) for bit in bits):
        raise ValueError(f"state contains non-bits: {state!r}")
    return bits


def state_to_string(state: BitState) -> str:
    """Render a bit state as a binary string."""

    return "".join(str(bit) for bit in state)


def rule184_step_local(state: BitState) -> BitState:
    """Rule 184 by the local formula from the G9 lab specification."""

    length = len(state)
    return tuple(
        1
        if (state[(i - 1) % length] == 1 and state[i] == 0)
        or (state[i] == 1 and state[(i + 1) % length] == 1)
        else 0
        for i in range(length)
    )


def rule184_step_particles(state: BitState) -> BitState:
    """Rule 184 by synchronous particle motion into empty right neighbors."""

    length = len(state)
    next_state = [0] * length
    for i, bit in enumerate(state):
        if bit == 0:
            continue
        right = (i + 1) % length
        if state[right] == 0:
            next_state[right] = 1
        else:
            next_state[i] = 1
    return tuple(next_state)


def rule184_step_wolfram(state: BitState) -> BitState:
    """Rule 184 by the Wolfram neighborhood table `10111000`."""

    length = len(state)
    return tuple(
        RULE184_TABLE[
            (state[(i - 1) % length], state[i], state[(i + 1) % length])
        ]
        for i in range(length)
    )


def rule184_step(state: BitState) -> BitState:
    """Canonical Rule 184 step, with formulations kept testable separately."""

    return rule184_step_local(state)


def shift_state(state: BitState, displacement: int) -> BitState:
    """Shift content by `displacement` cells to the right on the ring."""

    length = len(state)
    d = displacement % length
    return tuple(state[(i - d) % length] for i in range(length))


def count_adjacent_pair(state: BitState, left: int, right: int) -> int:
    """Count cyclic adjacent pairs equal to `(left, right)`."""

    length = len(state)
    return sum(
        1
        for i in range(length)
        if state[i] == left and state[(i + 1) % length] == right
    )


def blocked_cars(state: BitState) -> int:
    """Count adjacent `11` pairs, the subcritical blocked-car defect census."""

    return count_adjacent_pair(state, 1, 1)


def blocked_holes(state: BitState) -> int:
    """Count adjacent `00` pairs, the supercritical blocked-hole defect census."""

    return count_adjacent_pair(state, 0, 0)


def exact_density_label(numerator: int, denominator: int) -> str:
    """Format an exact rational density label."""

    common = gcd(numerator, denominator)
    return f"{numerator // common}/{denominator // common}"


def seeded_state(length: int, cars: int, seed: int) -> BitState:
    """Create a deterministic exact state with exactly `cars` particles."""

    if cars < 0 or cars > length:
        raise ValueError("car count must be between 0 and length")
    cells = [1] * cars + [0] * (length - cars)
    random.Random(seed).shuffle(cells)
    return tuple(cells)


def density_car_count(length: int, numerator: int, denominator: int) -> int:
    """Nearest-integer car count for an exact rational density."""

    return (length * numerator + denominator // 2) // denominator


def regime_for_count(length: int, cars: int) -> str:
    """Classify the density regime by exact particle count."""

    doubled = 2 * cars
    if doubled < length:
        return "subcritical"
    if doubled > length:
        return "supercritical"
    return "critical"


def defect_measure_for_regime(state: BitState, regime: str) -> int:
    """Return the defect census expected to evacuate for the regime."""

    if regime == "subcritical":
        return blocked_cars(state)
    if regime == "supercritical":
        return blocked_holes(state)
    if regime == "critical":
        return blocked_cars(state) + blocked_holes(state)
    raise ValueError(f"unknown regime: {regime}")


def measure_name_for_regime(regime: str) -> str:
    """Human-readable evacuated defect measure name."""

    if regime == "subcritical":
        return "adjacent_11_blocked_cars"
    if regime == "supercritical":
        return "adjacent_00_blocked_holes"
    if regime == "critical":
        return "adjacent_11_plus_adjacent_00_alternation_defects"
    raise ValueError(f"unknown regime: {regime}")


def signed_displacement(displacement: int, length: int) -> int:
    """Convert a modular displacement into the shortest signed representative."""

    d = displacement % length
    return d - length if d > length // 2 else d


def find_recurrence_certificate(
    history: list[BitState],
    start: int,
    max_tau: int,
    checked_windows: int,
) -> RecurrenceCertificate:
    """Find an exact `state[t+tau] = shift_d(state[t])` tail certificate."""

    length = len(history[0])
    if start + max_tau + checked_windows >= len(history):
        raise ValueError("history is too short for requested recurrence check")
    for tau in range(1, max_tau + 1):
        for displacement in range(length):
            if all(
                history[t + tau] == shift_state(history[t], displacement)
                for t in range(start, start + checked_windows)
            ):
                return RecurrenceCertificate(
                    tau=tau,
                    displacement=signed_displacement(displacement, length),
                    checked_windows=checked_windows,
                )
    raise AssertionError("no recurrence-with-displacement certificate found")


def census_samples(
    blocked_car_counts: list[int],
    blocked_hole_counts: list[int],
    evacuation_step: int,
) -> list[dict[str, int]]:
    """Small exact census curve excerpt around the start and evacuation time."""

    last = len(blocked_car_counts) - 1
    indices = {
        0,
        1,
        2,
        3,
        4,
        5,
        10,
        20,
        50,
        100,
        evacuation_step - 2,
        evacuation_step - 1,
        evacuation_step,
        evacuation_step + 1,
        evacuation_step + 2,
        last,
    }
    return [
        {
            "t": t,
            "blocked_cars_11": blocked_car_counts[t],
            "blocked_holes_00": blocked_hole_counts[t],
        }
        for t in sorted(i for i in indices if 0 <= i <= last)
    ]


def simulate_density(
    *,
    length: int,
    numerator: int,
    denominator: int,
    seed: int,
    max_steps: int,
    max_tau: int,
    recurrence_windows: int,
) -> Rule184DensityResult:
    """Run one exact density setting until evacuation and recurrence are certified."""

    cars = density_car_count(length, numerator, denominator)
    state = seeded_state(length, cars, seed)
    regime = regime_for_count(length, cars)
    history = [state]
    blocked_car_counts = [blocked_cars(state)]
    blocked_hole_counts = [blocked_holes(state)]
    evacuation_step: int | None = None

    for step in range(1, max_steps + 1):
        state = rule184_step(state)
        history.append(state)
        blocked_car_counts.append(blocked_cars(state))
        blocked_hole_counts.append(blocked_holes(state))
        if evacuation_step is None and defect_measure_for_regime(state, regime) == 0:
            evacuation_step = step
        if (
            evacuation_step is not None
            and step >= evacuation_step + max_tau + recurrence_windows
        ):
            break

    if evacuation_step is None:
        raise AssertionError(
            f"{regime} density {numerator}/{denominator} did not evacuate within {max_steps}"
        )

    if any(
        defect_measure_for_regime(history[t], regime) != 0
        for t in range(evacuation_step, len(history))
    ):
        raise AssertionError("evacuated defect measure did not stay at zero")

    recurrence = find_recurrence_certificate(
        history,
        start=evacuation_step,
        max_tau=max_tau,
        checked_windows=recurrence_windows,
    )
    transporter = "cars" if regime in ("subcritical", "critical") else "holes"
    return Rule184DensityResult(
        length=length,
        density_label=exact_density_label(numerator, denominator),
        cars=cars,
        realized_density=f"{cars}/{length}",
        regime=regime,
        seed=seed,
        max_steps=max_steps,
        evacuation_measure=measure_name_for_regime(regime),
        evacuation_step=evacuation_step,
        final_blocked_cars=blocked_car_counts[-1],
        final_blocked_holes=blocked_hole_counts[-1],
        recurrence=recurrence,
        transporter=transporter,
        census_samples=census_samples(
            blocked_car_counts,
            blocked_hole_counts,
            evacuation_step,
        ),
    )


def verify_rule184_formulations(states: list[BitState]) -> None:
    """Assert that all three Rule 184 formulations agree on given states."""

    for state in states:
        local = rule184_step_local(state)
        particles = rule184_step_particles(state)
        wolfram = rule184_step_wolfram(state)
        if not (local == particles == wolfram):
            raise AssertionError(
                f"Rule 184 formulations disagree for {state_to_string(state)}: "
                f"{local}, {particles}, {wolfram}"
            )
