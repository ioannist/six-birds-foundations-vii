from __future__ import annotations

import unittest

from fvii_lab.phase3 import all_envelopes, canonical_witnesses, join_status, no_go_controls, status_partitions


class Phase3JoinTests(unittest.TestCase):
    def test_eleven_closed_bounded_envelopes(self) -> None:
        rows = all_envelopes()
        self.assertEqual(len(rows), 11)
        self.assertTrue(all(result.raw_cardinality >= result.canonical_cardinality for result, _, _ in rows))
        self.assertTrue(all(result.accepted_cardinality + result.rejected_cardinality == result.canonical_cardinality for result, _, _ in rows))

    def test_contact_and_composite_are_separate(self) -> None:
        accepted = all_envelopes()[0][1]
        self.assertIn({
            "compatible": False, "contact": True, "payload_certified": False,
            "destination_owned": False, "provenance_preserved": False,
            "transport_credit": False, "composite": False, "strict_join": False,
        }, accepted)

    def test_status_partition_covers_each_accepted_join_profile_once(self) -> None:
        accepted = all_envelopes()[1][1]
        partitions = status_partitions()
        self.assertEqual(sum(len(rows) for rows in partitions.values()), len(accepted))
        self.assertEqual(set(partitions), {
            "NO_EVIDENCED_CONTACT", "EVIDENCED_CONTACT", "COMMON_REFINEMENT",
            "LAWFUL_COMPOSITE", "STRICT_JOIN", "OBSTRUCTED",
            "CERTIFIED_NONINTERACTION",
        })
        self.assertTrue(all(join_status(row) == status for status, rows in partitions.items() for row in rows))

    def test_strict_credit_requires_every_non_direction_gate(self) -> None:
        accepted = all_envelopes()[2][1]
        strict = [row for row in accepted if row["strict_credit"]]
        self.assertTrue(strict)
        for row in strict:
            self.assertTrue(all(row[key] for key in (
                "contact", "composite", "objecthood", "left_retention",
                "right_retention", "nonfactor_left", "nonfactor_right",
                "nonfactor_product", "source_independent", "budget_paid",
            )))
            self.assertFalse(row["relabel_only"])
            self.assertFalse(row["scheduling_only"])
            self.assertFalse(row["coarsening_only"])
            self.assertFalse(row["common_refinement_only"])
        self.assertTrue(any(not row["direction_certified"] for row in strict))

    def test_same_lineage_credit_is_rejected(self) -> None:
        rejected = all_envelopes()[3][2]
        self.assertTrue(any(row["same_lineage"] and row["independence_credit"] for row in rejected))

    def test_positive_unpaid_credit_is_rejected_and_zero_cost_escape_exists(self) -> None:
        accepted, rejected = all_envelopes()[4][1:]
        self.assertTrue(any(row["amount"] == 0 and row["zero_cost_certified"] and row["credit"] for row in accepted))
        self.assertTrue(any(row["amount"] > 0 and row["paid"] == 0 and row["refunded"] == 0 and row["credit"] for row in rejected))

    def test_capacity_profiles_respect_positive_unit_cost(self) -> None:
        accepted = [row for row in all_envelopes()[5][1] if row["feasible"]]
        self.assertTrue(all(row["minimum_positive_cost"] > 0 for row in accepted))
        self.assertTrue(all(row["live_join_count"] <= row["capacity"] for row in accepted))

    def test_refinement_has_preserve_strengthen_weaken_destroy_controls(self) -> None:
        accepted = all_envelopes()[6][1]
        self.assertTrue(any(r["join_before"] and not r["join_after"] for r in accepted))
        self.assertTrue(any(not r["join_before"] and r["join_after"] for r in accepted))
        self.assertTrue(any(r["join_before"] and r["join_after"] and r["novelty_before"] and not r["novelty_after"] for r in accepted))
        self.assertTrue(any(r["join_before"] and r["join_after"] and r["novelty_before"] and r["novelty_after"] for r in accepted))

    def test_created_cross_term_requires_active_nonrelabeling_needle(self) -> None:
        accepted = [row for row in all_envelopes()[7][1] if row["origin"] == "CREATED_CROSS_TERM"]
        self.assertTrue(accepted)
        self.assertTrue(all(row["active"] and row["cross_term"] and not row["relabel_only"] for row in accepted))

    def test_noninteraction_credit_requires_all_coverage_gates(self) -> None:
        accepted = [row for row in all_envelopes()[8][1] if row["certificate_credit"]]
        self.assertEqual(len(accepted), 1)
        self.assertFalse(accepted[0]["contact"])

    def test_strict_join_does_not_force_categorical_reduction(self) -> None:
        accepted = all_envelopes()[9][1]
        self.assertTrue(any(row["strict_join"] and not row["product_universal"] and not row["pullback_universal"] and not row["pushout_universal"] for row in accepted))

    def test_each_listed_contact_measure_has_a_lawful_nonconservation_control(self) -> None:
        accepted = all_envelopes()[10][1]
        kinds = {"CONTACTS", "LIVE_JOINS", "PAID_COST", "ACTIVE_RESIDUALS", "RETAINED_PARENTS"}
        witnessed = {row["measure_kind"] for row in accepted if row["lawful"] and row["before"] != row["after"] and not row["conservation_credit"]}
        self.assertEqual(witnessed, kinds)

    def test_witness_census_and_uniqueness(self) -> None:
        rows = canonical_witnesses()
        self.assertEqual(len(rows), 27)
        self.assertEqual(len({row["witness_id"] for row in rows}), 27)
        self.assertTrue(all(len(row["assignment_sha256"]) == 64 for row in rows))

    def test_no_go_front_has_failure_and_escape_controls(self) -> None:
        rows = no_go_controls()
        self.assertEqual({row["no_go_id"] for row in rows}, {"NGVII-02", "NGVII-06", "NGVII-07", "NGVII-08", "NGVII-09"})
        self.assertTrue(all(row["failure_scenarios"] and row["escape_scenarios"] for row in rows))


if __name__ == "__main__":
    unittest.main()
