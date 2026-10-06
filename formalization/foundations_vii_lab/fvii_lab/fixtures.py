from __future__ import annotations

from pathlib import Path

from .canonical import load_json
from .model import Countermodel, Scenario
from .schema import validate_countermodel_dict, validate_scenario_dict

LAB_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = LAB_ROOT / "fixtures"


def load_scenarios(root: Path | None = None) -> list[Scenario]:
    base = (root or FIXTURE_ROOT) / "scenarios"
    out: list[Scenario] = []
    for path in sorted(base.glob("*.json")):
        raw = load_json(path)
        validate_scenario_dict(raw)
        out.append(
            Scenario(
                fixture_id=raw["fixture_id"],
                name=raw["name"],
                expected_status=raw["expected_status"],
                flags=raw["flags"],
                assertions=raw["assertions"],
                candidate_ids=tuple(raw["candidate_ids"]),
                falsifier=raw["falsifier"],
                structural_record=raw["structural_record"],
                source_path=path,
            )
        )
    return out


def load_countermodels(root: Path | None = None) -> list[Countermodel]:
    base = (root or FIXTURE_ROOT) / "countermodels"
    out: list[Countermodel] = []
    for path in sorted(base.glob("*.json")):
        raw = load_json(path)
        validate_countermodel_dict(raw)
        out.append(
            Countermodel(
                fixture_id=raw["fixture_id"],
                name=raw["name"],
                scenario_id=raw["scenario_id"],
                expected_status=raw["expected_status"],
                shows=raw["shows"],
                candidate_ids=tuple(raw["candidate_ids"]),
                escape_route=raw["escape_route"],
                scenario_sha256=raw["scenario_sha256"],
                source_path=path,
            )
        )
    return out
