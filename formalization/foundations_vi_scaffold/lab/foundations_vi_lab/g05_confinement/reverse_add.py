"""Exact base-2 reverse-and-add confinement checks for G5-L1."""

from __future__ import annotations

from dataclasses import dataclass


PHASES = ("P0", "P1", "P2", "P3")
PRE_ENTRY_STRINGS = ["10110", "100011", "1010100", "1101001", "10110100"]


@dataclass(frozen=True)
class PhaseMatch:
    """A successful match against one phase language."""

    phase: str
    r: int


@dataclass(frozen=True)
class PhaseRecord:
    """One audited phase-family iterate."""

    index: int
    binary: str
    value: int
    phase: str
    r: int
    palindrome: bool


@dataclass(frozen=True)
class G5RunSummary:
    """Summary of the G5-L1 confinement sweep."""

    seed: int
    cycles: int
    pre_entry_steps: int
    phase_transitions: int
    total_reverse_add_steps: int
    entry_binary: str
    final_binary: str
    final_r: int
    max_bit_length: int
    records: list[PhaseRecord]
    pre_entry_strings: list[str]


def to_base_digits(n: int, base: int) -> str:
    """Return the canonical digit string for nonnegative `n` in `base`."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    if base < 2:
        raise ValueError("base must be at least 2")
    if n == 0:
        return "0"
    digits: list[str] = []
    value = n
    while value:
        digit = value % base
        if digit >= 10:
            raise ValueError("bases above 10 are not used by this lab")
        digits.append(str(digit))
        value //= base
    return "".join(reversed(digits))


def from_base_digits(digits: str, base: int) -> int:
    """Evaluate a canonical digit string in `base`."""

    if base < 2:
        raise ValueError("base must be at least 2")
    if not digits:
        raise ValueError("digit string must be nonempty")
    value = 0
    for char in digits:
        digit = ord(char) - ord("0")
        if digit < 0 or digit >= base:
            raise ValueError(f"digit {char!r} is invalid for base {base}")
        value = value * base + digit
    return value


def rev_b(n: int, base: int = 2) -> int:
    """Reverse the canonical base-`base` digit string of `n` and evaluate it."""

    return from_base_digits(to_base_digits(n, base)[::-1], base)


def reverse_and_add(n: int, base: int = 2) -> int:
    """Compute `R_b(n) = n + rev_b(n)` exactly."""

    return n + rev_b(n, base)


def binary(n: int) -> str:
    """Return the canonical binary representation of `n`."""

    return to_base_digits(n, 2)


def is_palindrome(text: str) -> bool:
    """Check exact string palindromicity."""

    return text == text[::-1]


def phase_string(phase: str, r: int) -> str:
    """Construct the exact G5 base-2 phase-language string for `phase` and `r`."""

    if r < 2:
        raise ValueError("the G5 phase family is declared for r >= 2")
    if phase == "P0":
        return "10" + ("1" * r) + "01" + ("0" * r)
    if phase == "P1":
        return "11" + ("0" * (r - 2)) + "1" + "000" + ("1" * (r - 2)) + "01"
    if phase == "P2":
        return "10" + ("1" * r) + "01" + ("0" * (r + 1))
    if phase == "P3":
        return "11" + ("0" * r) + "10" + ("1" * (r - 1)) + "01"
    raise ValueError(f"unknown phase {phase!r}")


def classify_phase(text: str) -> PhaseMatch | None:
    """Return the unique phase/rank match for `text`, if one exists."""

    matches: list[PhaseMatch] = []
    for r in range(2, len(text) + 1):
        for phase in PHASES:
            if text == phase_string(phase, r):
                matches.append(PhaseMatch(phase=phase, r=r))
    if len(matches) > 1:
        raise AssertionError(f"ambiguous phase match for {text}: {matches}")
    return matches[0] if matches else None


def expected_phase(index: int) -> PhaseMatch:
    """Expected phase/rank at phase-family index `index`, starting at `P0(2)`."""

    if index < 0:
        raise ValueError("index must be nonnegative")
    return PhaseMatch(phase=PHASES[index % 4], r=2 + index // 4)


def worked_first_cycle() -> list[tuple[str, str]]:
    """Return the four exact first-cycle transitions from `THEOREMS.md`."""

    states = [
        "10110100",
        "11100001",
        "101101000",
        "110010101",
        "1011101000",
    ]
    return list(zip(states, states[1:]))


def assert_worked_first_cycle() -> None:
    """Assert the exact first-cycle reverse-and-add identities."""

    expected_after = {
        "10110100": "11100001",
        "11100001": "101101000",
        "101101000": "110010101",
        "110010101": "1011101000",
    }
    for before, after in expected_after.items():
        value = from_base_digits(before, 2)
        actual = binary(reverse_and_add(value, 2))
        if actual != after:
            raise AssertionError(f"R({before}) = {actual}, expected {after}")


def pre_entry_orbit(seed: int = 22) -> list[str]:
    """Return the seed-to-entry binary orbit segment."""

    value = seed
    states = [binary(value)]
    for _ in range(4):
        value = reverse_and_add(value, 2)
        states.append(binary(value))
    return states


def verify_g5_l1(seed: int = 22, cycles: int = 20) -> G5RunSummary:
    """Verify the G5-L1 base-2 confinement certificate for `cycles` full cycles."""

    if cycles < 1:
        raise ValueError("cycles must be positive")

    assert_worked_first_cycle()
    pre_entry = pre_entry_orbit(seed)
    if pre_entry != PRE_ENTRY_STRINGS:
        raise AssertionError(f"pre-entry orbit {pre_entry} did not match expected {PRE_ENTRY_STRINGS}")
    for text in pre_entry:
        if is_palindrome(text):
            raise AssertionError(f"pre-entry string {text} is unexpectedly palindromic")

    value = from_base_digits(PRE_ENTRY_STRINGS[-1], 2)
    phase_transitions = cycles * 4
    records: list[PhaseRecord] = []

    for index in range(phase_transitions + 1):
        text = binary(value)
        expected = expected_phase(index)
        actual = classify_phase(text)
        if actual != expected:
            raise AssertionError(f"at index {index}, got {actual} for {text}, expected {expected}")
        pal = is_palindrome(text)
        if pal:
            raise AssertionError(f"phase-family string {text} at index {index} is palindromic")
        records.append(
            PhaseRecord(
                index=index,
                binary=text,
                value=value,
                phase=actual.phase,
                r=actual.r,
                palindrome=pal,
            )
        )
        if index != phase_transitions:
            value = reverse_and_add(value, 2)

    return G5RunSummary(
        seed=seed,
        cycles=cycles,
        pre_entry_steps=len(PRE_ENTRY_STRINGS) - 1,
        phase_transitions=phase_transitions,
        total_reverse_add_steps=(len(PRE_ENTRY_STRINGS) - 1) + phase_transitions,
        entry_binary=PRE_ENTRY_STRINGS[-1],
        final_binary=records[-1].binary,
        final_r=records[-1].r,
        max_bit_length=max(len(record.binary) for record in records),
        records=records,
        pre_entry_strings=pre_entry,
    )
