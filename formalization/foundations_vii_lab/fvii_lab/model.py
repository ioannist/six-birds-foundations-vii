from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Scenario:
    fixture_id: str
    name: str
    expected_status: str
    flags: Mapping[str, bool]
    assertions: Mapping[str, bool]
    candidate_ids: tuple[str, ...]
    falsifier: str
    structural_record: Mapping[str, Any]
    source_path: Path


@dataclass(frozen=True, slots=True)
class Countermodel:
    fixture_id: str
    name: str
    scenario_id: str
    expected_status: str
    shows: str
    candidate_ids: tuple[str, ...]
    escape_route: str
    scenario_sha256: str
    source_path: Path


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    fixture_id: str
    expected_status: str
    observed_status: str
    status_pass: bool
    assertion_results: Mapping[str, bool]
    all_pass: bool
    derived: Mapping[str, bool]
    canonical_input_sha256: str
    canonical_result_sha256: str


class FixtureError(ValueError):
    """Raised when a fixture violates the Phase-1 canonical contract."""
