"""Exact integer sandpile stabilization utilities for G8-L1."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Iterable

GridIndex = int
Configuration = tuple[int, ...]
Chooser = Callable[[tuple[GridIndex, ...], Random], GridIndex]


@dataclass(frozen=True)
class StabilizationResult:
    """Result of one legal stabilization run."""

    final: Configuration
    odometer: tuple[int, ...]
    steps: int
    seed: int


def site_count(size: int) -> int:
    """Return the number of non-sink grid sites."""

    if size <= 0:
        raise ValueError("grid size must be positive")
    return size * size


def neighbors(size: int, site: GridIndex) -> tuple[GridIndex, ...]:
    """Return non-sink neighbors of a grid site in the 4-neighbor graph."""

    row, col = divmod(site, size)
    out: list[GridIndex] = []
    if row > 0:
        out.append(site - size)
    if row + 1 < size:
        out.append(site + size)
    if col > 0:
        out.append(site - 1)
    if col + 1 < size:
        out.append(site + 1)
    return tuple(out)


def _validate_configuration(size: int, chips: Configuration) -> None:
    if len(chips) != site_count(size):
        raise ValueError("configuration length does not match grid size")
    if any(chip < 0 for chip in chips):
        raise ValueError("chip counts must be nonnegative integers")


def legal_sites(size: int, chips: Configuration | list[int]) -> tuple[GridIndex, ...]:
    """Return sites with at least four chips, using the boundary sink convention."""

    _ = size
    return tuple(i for i, chip in enumerate(chips) if chip >= 4)


def choose_random(legal: tuple[GridIndex, ...], rng: Random) -> GridIndex:
    """Choose one legal site uniformly from the current legal set."""

    return legal[rng.randrange(len(legal))]


def choose_min(legal: tuple[GridIndex, ...], _rng: Random) -> GridIndex:
    """Choose the smallest legal site, for deterministic test runs."""

    return legal[0]


def choose_max(legal: tuple[GridIndex, ...], _rng: Random) -> GridIndex:
    """Choose the largest legal site, for deterministic test runs."""

    return legal[-1]


def stabilize(
    size: int,
    initial: Configuration,
    *,
    seed: int,
    chooser: Chooser = choose_random,
) -> StabilizationResult:
    """Stabilize a grid sandpile by legal firings chosen by `chooser`."""

    _validate_configuration(size, initial)
    rng = Random(seed)
    chips = list(initial)
    odometer = [0 for _ in chips]
    degree = 4
    steps = 0
    legal = {i for i, chip in enumerate(chips) if chip >= degree}

    while legal:
        legal_tuple = tuple(sorted(legal))
        fired = chooser(legal_tuple, rng)
        if fired not in legal:
            raise RuntimeError("chooser selected a site outside the legal set")
        if chips[fired] < degree:
            raise RuntimeError("chooser selected an illegal site")
        touched = {fired, *neighbors(size, fired)}
        chips[fired] -= degree
        for nb in neighbors(size, fired):
            chips[nb] += 1
        odometer[fired] += 1
        steps += 1

        for site in touched:
            if chips[site] >= degree:
                legal.add(site)
            else:
                legal.discard(site)

    return StabilizationResult(tuple(chips), tuple(odometer), steps, seed)


def stabilize_by_scanning(
    size: int,
    initial: Configuration,
    *,
    seed: int,
    chooser: Chooser = choose_random,
) -> StabilizationResult:
    """Reference stabilizer that recomputes the legal set after every firing."""

    _validate_configuration(size, initial)
    rng = Random(seed)
    chips = list(initial)
    odometer = [0 for _ in chips]
    degree = 4
    steps = 0

    while True:
        legal_tuple = legal_sites(size, chips)
        if not legal_tuple:
            return StabilizationResult(tuple(chips), tuple(odometer), steps, seed)
        fired = chooser(legal_tuple, rng)
        if chips[fired] < degree:
            raise RuntimeError("chooser selected an illegal site")
        chips[fired] -= degree
        for nb in neighbors(size, fired):
            chips[nb] += 1
        odometer[fired] += 1
        steps += 1


def random_initial(size: int, rng: Random) -> Configuration:
    """Generate a reproducible nonnegative integer chip configuration."""

    chips = [rng.randrange(0, 4) for _ in range(site_count(size))]
    center = (size // 2) * size + (size // 2)
    chips[center] += size
    return tuple(chips)


@dataclass(frozen=True)
class SandpileTrial:
    """Summary for one initial configuration tested against many legal orders."""

    size: int
    config_index: int
    initial_seed: int
    order_seeds: tuple[int, ...]
    baseline_steps: int
    min_steps: int
    max_steps: int
    final_checksum: int
    odometer_checksum: int


@dataclass(frozen=True)
class SandpileExperiment:
    """Aggregate exact-invariance outcome for G8-L1."""

    seed: int
    sizes: tuple[int, ...]
    configurations_per_size: int
    orders_per_configuration: int
    trials: tuple[SandpileTrial, ...]

    @property
    def total_stabilizations(self) -> int:
        """Count seeded random stabilizations, excluding deterministic test orders."""

        return len(self.trials) * self.orders_per_configuration


def run_sandpile_experiment(
    *,
    seed: int,
    sizes: Iterable[int],
    configurations_per_size: int,
    orders_per_configuration: int,
) -> SandpileExperiment:
    """Run G8-L1 and raise `AssertionError` on the first invariance failure."""

    if configurations_per_size <= 0:
        raise ValueError("configurations_per_size must be positive")
    if orders_per_configuration <= 0:
        raise ValueError("orders_per_configuration must be positive")

    root_rng = Random(seed)
    size_tuple = tuple(sizes)
    trials: list[SandpileTrial] = []
    for size in size_tuple:
        for config_index in range(configurations_per_size):
            initial_seed = root_rng.randrange(0, 2**63)
            initial = random_initial(size, Random(initial_seed))
            min_result = stabilize(size, initial, seed=initial_seed, chooser=choose_min)
            max_result = stabilize(size, initial, seed=initial_seed, chooser=choose_max)
            if min_result.final != max_result.final:
                raise AssertionError(f"deterministic final mismatch for size {size}")
            if min_result.odometer != max_result.odometer:
                raise AssertionError(f"deterministic odometer mismatch for size {size}")

            order_seeds: list[int] = []
            baseline: StabilizationResult | None = None
            for _ in range(orders_per_configuration):
                order_seed = root_rng.randrange(0, 2**63)
                order_seeds.append(order_seed)
                result = stabilize(size, initial, seed=order_seed)
                if baseline is None:
                    baseline = result
                elif result.final != baseline.final:
                    raise AssertionError(f"random final mismatch for size {size}")
                elif result.odometer != baseline.odometer:
                    raise AssertionError(f"random odometer mismatch for size {size}")

            assert baseline is not None
            if baseline.final != min_result.final:
                raise AssertionError(f"baseline final mismatch for size {size}")
            if baseline.odometer != min_result.odometer:
                raise AssertionError(f"baseline odometer mismatch for size {size}")

            trials.append(
                SandpileTrial(
                    size=size,
                    config_index=config_index,
                    initial_seed=initial_seed,
                    order_seeds=tuple(order_seeds),
                    baseline_steps=baseline.steps,
                    min_steps=min_result.steps,
                    max_steps=max_result.steps,
                    final_checksum=sum((i + 1) * chip for i, chip in enumerate(baseline.final)),
                    odometer_checksum=sum(
                        (i + 1) * count for i, count in enumerate(baseline.odometer)
                    ),
                )
            )

    return SandpileExperiment(
        seed=seed,
        sizes=size_tuple,
        configurations_per_size=configurations_per_size,
        orders_per_configuration=orders_per_configuration,
        trials=tuple(trials),
    )
