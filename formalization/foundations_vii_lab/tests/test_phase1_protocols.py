from __future__ import annotations

import unittest

from fvii_lab.fixtures import load_countermodels, load_scenarios
from fvii_lab.protocols import (
    append_only_extends,
    negative_licenses,
    phase1_detector_contract,
    science_asset_grade_faithful,
    transport_licensed,
)


class Phase1ProtocolTests(unittest.TestCase):
    def _bridge(self, disposition: str = "ACCEPTED") -> dict[str, object]:
        return {
            "source_declaration": "Prior.source",
            "target_declaration": "FoundationsVII.target",
            "source_type": "Prior.Source",
            "target_type": "FoundationsVII.Target",
            "source_map": "sourceAdapter",
            "target_map": "targetAdapter",
            "preserved_hypotheses": ["typed source"],
            "added_hypotheses": ["accepted VII bridge"],
            "lost_hypotheses": ["none silently"],
            "trust_dependencies": ["source theorem trust ledger"],
            "nonclaims": ["does not strengthen the source theorem"],
            "disposition": disposition,
            "audit": [{"disposition": disposition}],
        }

    def test_c020_citation_is_never_transport_authorization(self) -> None:
        self.assertFalse(transport_licensed("CITATION_ONLY", None))
        self.assertTrue(transport_licensed("CERTIFIED_BRIDGE", self._bridge()))
        self.assertFalse(transport_licensed("CERTIFIED_BRIDGE", self._bridge("FAILED")))
        self.assertFalse(transport_licensed("CERTIFIED_BRIDGE", self._bridge("WITHDRAWN")))
        explicit_none = self._bridge()
        explicit_none["added_hypotheses"] = []
        explicit_none["lost_hypotheses"] = []
        explicit_none["trust_dependencies"] = []
        self.assertTrue(transport_licensed("CERTIFIED_BRIDGE", explicit_none))
        malformed = self._bridge()
        malformed["source_map"] = ""
        self.assertFalse(transport_licensed("CERTIFIED_BRIDGE", malformed))

    def test_c020_failed_and_withdrawn_records_are_append_only(self) -> None:
        old = [{"id": "B1", "disposition": "FAILED"}, {"id": "B2", "disposition": "WITHDRAWN"}]
        new = old + [{"id": "B3", "disposition": "ACCEPTED"}]
        self.assertTrue(append_only_extends(old, new))
        self.assertFalse(append_only_extends(old, [new[1], new[0], new[2]]))
        self.assertFalse(append_only_extends(old, [old[0]]))

    def test_c023_negative_scope_lattice(self) -> None:
        self.assertTrue(negative_licenses("POINT_NULL", "ONE_INSTANCE", "ONE_INSTANCE", family_closed=False))
        self.assertFalse(negative_licenses("POINT_NULL", "ONE_INSTANCE", "BOUNDED_FAMILY", family_closed=False))
        self.assertFalse(negative_licenses("BOUNDED_SEARCH", "BOUNDED_FAMILY", "UNRESTRICTED_UNDER_HYPOTHESES", family_closed=False))
        self.assertTrue(negative_licenses("EXHAUSTIVE_CLOSED_FINITE", "CLOSED_FINITE_FAMILY", "CLOSED_FINITE_FAMILY", family_closed=True))
        self.assertFalse(negative_licenses("EXHAUSTIVE_CLOSED_FINITE", "CLOSED_FINITE_FAMILY", "CLOSED_FINITE_FAMILY", family_closed=False))
        self.assertTrue(negative_licenses("THEOREM_IMPOSSIBILITY", "UNRESTRICTED_UNDER_HYPOTHESES", "UNRESTRICTED_UNDER_HYPOTHESES", family_closed=False))

    def test_c024_theorem_and_finite_evidence_do_not_collapse(self) -> None:
        finite_only = {
            "claim_grade": "THEOREM",
            "evidence_grade": "EXHAUSTIVE_FINITE_EXTERNAL",
            "formal_declaration": None,
            "specification_kind": "NOT_APPLICABLE",
            "normative_specification": None,
            "nonclaims": ["finite only"],
            "audit": [{"disposition": "ACCEPTED"}],
        }
        self.assertFalse(science_asset_grade_faithful(finite_only))
        theorem = dict(finite_only)
        theorem.update(evidence_grade="THEOREM_BACKED", formal_declaration="FoundationsVII.someTheorem")
        self.assertTrue(science_asset_grade_faithful(theorem))

    def test_c024_normative_requires_explicit_specification(self) -> None:
        base = {
            "claim_grade": "SCHEMA",
            "evidence_grade": "NONE",
            "formal_declaration": None,
            "specification_kind": "NORMATIVE",
            "normative_specification": None,
            "nonclaims": ["normative, not a theorem"],
            "audit": [{"disposition": "ACCEPTED"}],
        }
        self.assertFalse(science_asset_grade_faithful(base))
        base["normative_specification"] = {"gate": "all fixtures frozen"}
        self.assertTrue(science_asset_grade_faithful(base))

    def test_c025_detector_contract_freezes_all_cases(self) -> None:
        scenarios = load_scenarios()
        countermodels = load_countermodels()
        contract = phase1_detector_contract(
            [x.fixture_id for x in scenarios],
            [x.fixture_id for x in countermodels],
        )
        self.assertTrue(contract.well_formed())
        self.assertEqual(len(contract.frozen_scenario_ids), 24)
        self.assertEqual(len(contract.frozen_countermodel_ids), 27)
        self.assertGreater(contract.false_positive_cost, contract.false_negative_cost)
        frozen = set(contract.frozen_scenario_ids) | set(contract.frozen_countermodel_ids)
        self.assertTrue(set(contract.same_source_controls) <= frozen)
        fields = {field: getattr(contract, field) for field in contract.__dataclass_fields__}
        fields["relabeling_controls"] = ("UNKNOWN-CONTROL",)
        malformed = contract.__class__(**fields)
        self.assertFalse(malformed.well_formed())
        self.assertTrue(set(contract.same_source_controls) <= set(contract.frozen_scenario_ids) | set(contract.frozen_countermodel_ids))
        malformed = contract.__class__(
            **{**{field: getattr(contract, field) for field in contract.__dataclass_fields__},
               "relabeling_controls": ("UNKNOWN-CONTROL",)}
        )
        self.assertFalse(malformed.well_formed())


if __name__ == "__main__":
    unittest.main()
