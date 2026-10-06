from __future__ import annotations

import json
import unittest
from pathlib import Path

from fvii_lab.phase2 import all_envelopes, canonical_witnesses, no_go_controls


class Phase2AdmissionTests(unittest.TestCase):
    def test_nine_closed_bounded_envelopes(self) -> None:
        rows = all_envelopes()
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(result.raw_cardinality >= result.canonical_cardinality for result, _, _ in rows))
        self.assertTrue(all(result.accepted_cardinality + result.rejected_cardinality == result.canonical_cardinality for result, _, _ in rows))

    def test_bootstrap_has_exact_closed_and_open_failure_assignments(self) -> None:
        result, accepted, rejected = all_envelopes()[2]
        self.assertEqual(result.canonical_cardinality, 32)
        self.assertEqual(result.accepted_cardinality, 29)
        self.assertEqual(len(rejected), 3)
        self.assertEqual(rejected, [
            {
                "closed_family": False,
                "seed": False,
                "generator_reachable": False,
                "external_provision": False,
                "first_extension": True,
            },
            {
                "closed_family": True,
                "seed": False,
                "generator_reachable": False,
                "external_provision": False,
                "first_extension": True,
            },
            {
                "closed_family": True,
                "seed": False,
                "generator_reachable": False,
                "external_provision": True,
                "first_extension": True,
            },
        ])

    def test_totality_requires_total_source_self_owned_target_and_adapter_when_partial(self) -> None:
        result, accepted, rejected = all_envelopes()[5]
        self.assertEqual(result.canonical_cardinality, 32)
        self.assertEqual(result.accepted_cardinality, 19)
        self.assertEqual(result.rejected_cardinality, 13)
        unlawful = {
            "source_total": True,
            "target_partial": True,
            "target_self_owned": True,
            "adapter_certified": False,
            "transfer_licensed": True,
        }
        self.assertIn(unlawful, rejected)

    def test_access_noncollapse_witnesses_are_coherent(self) -> None:
        witnesses = {row["witness_id"]: row for row in canonical_witnesses()}
        for witness_id in ["P2-W01", "P2-W02", "P2-W03", "P2-W04", "P2-W05", "P2-W06"]:
            assignment = witnesses[witness_id]["assignment"]
            self.assertIn(assignment, all_envelopes()[0][1])

    def test_reachability_and_soundness_witnesses_are_coherent(self) -> None:
        witnesses = {row["witness_id"]: row for row in canonical_witnesses()}
        self.assertIn(witnesses["P2-W07"]["assignment"], all_envelopes()[1][1])
        self.assertIn(witnesses["P2-W08"]["assignment"], all_envelopes()[1][1])

    def test_neutral_commitment_requires_symmetry_and_matched_controls(self) -> None:
        result, accepted, rejected = all_envelopes()[3]
        self.assertEqual(result.canonical_cardinality, 256)
        self.assertEqual(result.accepted_cardinality, 129)
        self.assertEqual(result.rejected_cardinality, 127)
        isolated_retrospective = {
            "preregistered": True,
            "precedes_evidence": True,
            "retrospective": True,
            "task_blind": True,
            "outcome_independent": True,
            "symmetry_certified": True,
            "control_matched": True,
            "prospective_credit": True,
        }
        self.assertIn(isolated_retrospective, rejected)

    def test_provenance_normalization_reduces_labeled_source_pairs(self) -> None:
        result, accepted, rejected = all_envelopes()[4]
        self.assertEqual(result.raw_cardinality, 512)
        self.assertEqual(result.canonical_cardinality, 256)
        self.assertEqual(result.accepted_cardinality, 128)
        self.assertEqual(result.rejected_cardinality, 128)

    def test_no_go_front_has_failure_and_escape_controls(self) -> None:
        rows = no_go_controls()
        self.assertEqual({row["no_go_id"] for row in rows}, {"NGVII-01", "NGVII-03", "NGVII-04", "NGVII-05", "NGVII-11"})
        self.assertTrue(all(row["failure_scenario"].startswith("TTW-S") for row in rows))
        self.assertTrue(all(row["escape_scenarios"] for row in rows))

    def test_witnesses_are_unique_and_source_typed(self) -> None:
        rows = canonical_witnesses()
        self.assertEqual(len(rows), 15)
        self.assertEqual(len({row["witness_id"] for row in rows}), 15)
        self.assertTrue(all(row["candidate_id"].startswith("VII-C") for row in rows))
        self.assertTrue(all(len(row["assignment_sha256"]) == 64 for row in rows))


if __name__ == "__main__":
    unittest.main()
