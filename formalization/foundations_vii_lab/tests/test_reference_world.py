from __future__ import annotations

import json
import unittest
from pathlib import Path

from fvii_lab.canonical import canonical_bytes, load_json, sha256_value
from fvii_lab.compare import evaluate_all
from fvii_lab.evaluator import evaluate
from fvii_lab.fixtures import FIXTURE_ROOT, load_countermodels, load_scenarios
from fvii_lab.model import FixtureError
from fvii_lab.schema import (
    REQUIRED_STRUCTURAL_SECTIONS,
    validate_countermodel_dict,
    validate_scenario_dict,
)


class ReferenceWorldTests(unittest.TestCase):
    def test_complete_fixture_census(self) -> None:
        self.assertEqual(len(load_scenarios()), 24)
        self.assertEqual(len(load_countermodels()), 27)

    def test_all_scenarios_and_countermodels_pass(self) -> None:
        scenarios, countermodels = evaluate_all()
        self.assertTrue(all(row["all_pass"] for row in scenarios))
        self.assertTrue(all(row["all_pass"] for row in countermodels))

    def test_all_24_statuses_are_distinct_and_reached(self) -> None:
        scenarios = load_scenarios()
        observed = {evaluate(s.flags)[0] for s in scenarios}
        self.assertEqual(len(observed), 24)
        self.assertEqual(observed, {s.expected_status for s in scenarios})

    def test_canonical_round_trip(self) -> None:
        for path in sorted(FIXTURE_ROOT.rglob("*.json")):
            value = load_json(path)
            self.assertEqual(path.read_bytes(), canonical_bytes(value), path)

    def test_manifest_hashes(self) -> None:
        manifest = load_json(FIXTURE_ROOT / "manifest.json")
        for row in manifest["fixtures"]:
            path = FIXTURE_ROOT.parent / row["path"]
            self.assertEqual(sha256_value(load_json(path)), row["sha256"], path)

    def test_countermodel_scenario_hashes(self) -> None:
        scenario_hashes = {
            path.stem: sha256_value(load_json(path))
            for path in (FIXTURE_ROOT / "scenarios").glob("*.json")
        }
        for countermodel in load_countermodels():
            self.assertEqual(countermodel.scenario_sha256, scenario_hashes[countermodel.scenario_id])

    def test_structural_field_removal_is_rejected(self) -> None:
        base = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S08.json")
        for field in REQUIRED_STRUCTURAL_SECTIONS:
            mutated = json.loads(json.dumps(base))
            del mutated["structural_record"][field]
            with self.subTest(field=field), self.assertRaises(FixtureError):
                validate_scenario_dict(mutated)


    def test_extra_root_and_structural_keys_are_rejected(self) -> None:
        base = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S08.json")
        root_extra = json.loads(json.dumps(base))
        root_extra["undeclared_root_field"] = True
        with self.assertRaises(FixtureError):
            validate_scenario_dict(root_extra)
        structural_extra = json.loads(json.dumps(base))
        structural_extra["structural_record"]["undeclared_section"] = {}
        with self.assertRaises(FixtureError):
            validate_scenario_dict(structural_extra)

    def test_flag_and_nested_record_extras_are_rejected(self) -> None:
        base = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S08.json")
        flag_extra = json.loads(json.dumps(base))
        flag_extra["flags"]["undeclared_flag"] = False
        with self.assertRaises(FixtureError):
            validate_scenario_dict(flag_extra)
        nested_extra = json.loads(json.dumps(base))
        nested_extra["structural_record"]["domain_state"]["undeclared_state"] = False
        with self.assertRaises(FixtureError):
            validate_scenario_dict(nested_extra)

    def test_accepted_infeasible_budget_entry_is_rejected(self) -> None:
        base = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S08.json")
        mutated = json.loads(json.dumps(base))
        entry = mutated["structural_record"]["budget_ledger"]["entries"][0]
        entry.update({"allocated": 0, "spent": 1, "occupied": 0, "refunded": 0, "disposition": "ACCEPTED"})
        with self.assertRaises(FixtureError):
            validate_scenario_dict(mutated)

    def test_failed_infeasible_attempt_remains_auditable(self) -> None:
        # TTW-S22 records an unpriced occupancy attempt as FAILED rather than
        # deleting it or pretending that it was a feasible accepted spend.
        fixture = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S22.json")
        entry = fixture["structural_record"]["budget_ledger"]["entries"][0]
        self.assertEqual(entry["disposition"], "FAILED")
        self.assertGreater(entry["occupied"], entry["allocated"])
        validate_scenario_dict(fixture)

    def test_countermodel_extra_fields_are_rejected(self) -> None:
        base = load_json(FIXTURE_ROOT / "countermodels" / "CM-01.json")
        mutated = json.loads(json.dumps(base))
        mutated["undeclared_field"] = "not licensed"
        with self.assertRaises(FixtureError):
            validate_countermodel_dict(mutated)

    def test_source_self_parenting_is_rejected(self) -> None:
        base = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S08.json")
        mutated = json.loads(json.dumps(base))
        entry = mutated["structural_record"]["source_ledger"]["entries"][0]
        entry["parent_sources"] = [entry["source_id"]]
        with self.assertRaises(FixtureError):
            validate_scenario_dict(mutated)

    def test_status_relevant_field_mutations_are_detected(self) -> None:
        mutations = {
            "source_independent": "SOURCE_OBSTRUCTION",
            "budget_ok": "BUDGET_OBSTRUCTION",
            "retention": "RETENTION_OBSTRUCTION",
            "contact": "NO_EVIDENCED_CONTACT",
        }
        base = load_json(FIXTURE_ROOT / "scenarios" / "TTW-S08.json")
        for field, expected_mutated_status in mutations.items():
            flags = dict(base["flags"])
            flags[field] = False
            if field == "contact":
                flags["compatible"] = True
            status, _ = evaluate(flags)
            with self.subTest(field=field):
                self.assertEqual(status, expected_mutated_status)
                self.assertNotEqual(status, base["expected_status"])


if __name__ == "__main__":
    unittest.main()
