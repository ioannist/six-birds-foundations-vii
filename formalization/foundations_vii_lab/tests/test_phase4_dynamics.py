from __future__ import annotations

import unittest

from fvii_lab.phase4 import (
    all_envelopes,
    canonical_witnesses,
    no_go_controls,
)


class Phase4DynamicsTests(unittest.TestCase):
    def test_twelve_closed_bounded_envelopes(self) -> None:
        rows = all_envelopes()
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(r.raw_cardinality >= r.canonical_cardinality for r, _, _ in rows))
        self.assertTrue(all(r.accepted_cardinality + r.rejected_cardinality == r.canonical_cardinality for r, _, _ in rows))

    def test_hidden_execution_blocks_attribution(self) -> None:
        rejected = all_envelopes()[0][2]
        self.assertTrue(any(r["hidden_executor"] and r["attribution_credit"] for r in rejected))

    def test_endogenous_credit_is_exact_on_declared_profile(self) -> None:
        accepted = all_envelopes()[1][1]
        positives = [r for r in accepted if r["endogenous_credit"]]
        self.assertTrue(positives)
        self.assertTrue(all(r["carried"] and r["reachable"] and r["executed"] and r["audited"] and r["budgeted"] and r["boundary_closed"] for r in positives))
        self.assertTrue(all(not r["theorist_hidden"] and not r["observer_hidden"] for r in positives))

    def test_participant_birth_requires_objecthood_and_survival(self) -> None:
        accepted = [r for r in all_envelopes()[2][1] if r["participant_credit"]]
        self.assertTrue(accepted)
        self.assertTrue(all(r["objecthood"] and r["survives_closure"] and r["outcome"] == "NEW_PARTICIPANT" for r in accepted))

    def test_downward_selection_does_not_create_absent_fact(self) -> None:
        accepted = [r for r in all_envelopes()[3][1] if r["direction"] == "DOWNWARD" and r["fidelity_credit"]]
        self.assertTrue(all(not r["lower_fact_after"] or r["lower_fact_before"] or r["external_insertion"] for r in accepted))

    def test_enablement_separations_have_positive_witnesses(self) -> None:
        accepted = all_envelopes()[4][1]
        self.assertTrue(any(r["enablement_without_descent_credit"] for r in accepted))
        self.assertTrue(any(r["necessary_insufficient_credit"] for r in accepted))

    def test_composed_enablement_does_not_force_causation(self) -> None:
        accepted = all_envelopes()[5][1]
        self.assertTrue(any(r["composed_credit"] and not r["transitive_causal_credit"] for r in accepted))

    def test_confluence_and_nonconfluence_controls_exist(self) -> None:
        accepted = all_envelopes()[6][1]
        self.assertTrue(any(r["both_legal"] and r["joinable"] and r["audit_equivalent"] and r["confluence_credit"] for r in accepted))
        self.assertTrue(any(r["both_legal"] and not r["joinable"] and not r["confluence_credit"] for r in accepted))

    def test_seed_dependence_is_not_presentation_only(self) -> None:
        accepted = all_envelopes()[7][1]
        self.assertTrue(any(r["seed_dependence_credit"] for r in accepted))
        self.assertTrue(all(not r["same_seed_partition"] and not r["terminal_equal"] for r in accepted if r["seed_dependence_credit"]))
        self.assertTrue(all(r["predictive_equivalent"] for r in accepted if r["presentation_only"]))

    def test_holonomy_zero_arrow_and_driven_arrow_both_exist(self) -> None:
        arrow_rows = all_envelopes()[9][1]
        self.assertTrue(any(r["holonomy"] and not r["arrow_credit"] for r in arrow_rows))
        self.assertTrue(any(r["holonomy"] and r["arrow_credit"] for r in arrow_rows))

    def test_cross_time_contact_requires_witness_not_assumed_simultaneity(self) -> None:
        accepted = [r for r in all_envelopes()[10][1] if r["contact_credit"]]
        self.assertTrue(accepted)
        self.assertTrue(all(not r["assumed_simultaneity"] for r in accepted))
        self.assertTrue(all(r["witness_kind"] != "NONE" for r in accepted))

    def test_full_algebra_and_fragment_are_separate(self) -> None:
        accepted = all_envelopes()[11][1]
        self.assertTrue(any(r["resource_fragment_credit"] and not r["full_algebra_credit"] for r in accepted))
        self.assertTrue(all(r["generators_declared"] and r["equivalence_declared"] and r["domains_declared"] and r["nonredundancy_proved"] and r["semantics_declared"] and r["laws_proved"] for r in accepted if r["full_algebra_credit"]))

    def test_witness_census_and_candidate_coverage(self) -> None:
        rows = canonical_witnesses()
        self.assertEqual(len(rows), 32)
        self.assertEqual(len({r["witness_id"] for r in rows}), 32)
        self.assertEqual({r["candidate_id"] for r in rows}, {
            "VII-C012", "VII-C013", "VII-C014", "VII-C015", "VII-C017",
            "VII-C018", "VII-C027", "VII-C028", "VII-C032", "VII-C034",
        })

    def test_no_go_has_failure_and_driven_escape(self) -> None:
        rows = no_go_controls()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["no_go_id"], "NGVII-10")
        self.assertEqual(rows[0]["failure_scenarios"], ["TTW-S17"])
        self.assertEqual(rows[0]["escape_scenarios"], ["TTW-S18"])


if __name__ == "__main__":
    unittest.main()
