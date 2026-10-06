from __future__ import annotations

import unittest

from fvii_lab.phase5 import (
    all_envelopes,
    canonical_witnesses,
    cross_family_controls,
)


class Phase5ClosureTests(unittest.TestCase):
    def test_eleven_envelopes_partition_exactly(self) -> None:
        envelopes = all_envelopes()
        self.assertEqual(len(envelopes), 11)
        for result, accepted, rejected, symmetry_rule in envelopes:
            self.assertEqual(result.canonical_cardinality, len(accepted) + len(rejected))
            self.assertEqual(result.accepted_cardinality, len(accepted))
            self.assertEqual(result.rejected_cardinality, len(rejected))
            self.assertGreaterEqual(result.raw_cardinality, result.canonical_cardinality)
            self.assertTrue(result.nonclaim)
            self.assertTrue(symmetry_rule)

    def test_witnesses_cover_each_family_three_times(self) -> None:
        witnesses = canonical_witnesses()
        self.assertEqual(len(witnesses), 33)
        family_counts: dict[str, int] = {}
        roles_by_family: dict[str, set[str]] = {}
        for row in witnesses:
            family_counts[row["family_id"]] = family_counts.get(row["family_id"], 0) + 1
            roles_by_family.setdefault(row["family_id"], set()).add(row["role"])
            self.assertTrue(row["corollary_ids"])
            self.assertTrue(row["candidate_ids"])
        self.assertEqual(set(family_counts.values()), {3})
        self.assertTrue(all(len(roles) == 3 for roles in roles_by_family.values()))

    def test_cross_family_control_contract(self) -> None:
        controls = cross_family_controls()
        self.assertEqual(len(controls), 12)
        self.assertEqual(len({row["control_id"] for row in controls}), 12)
        self.assertTrue(all(row["asset_ids"] for row in controls))
        self.assertTrue(all(row["positive_control"] and row["failure_control"] for row in controls))

    def test_no_free_join_accepts_no_free_credit(self) -> None:
        _, accepted, _, _ = dict(
            (r.family_id, (r, a, b, s)) for r, a, b, s in all_envelopes()
        )["P5-E06"]
        self.assertTrue(all(not row["free_join_credit"] for row in accepted))

    def test_holonomy_without_drive_never_gets_arrow_credit(self) -> None:
        _, accepted, _, _ = dict(
            (r.family_id, (r, a, b, s)) for r, a, b, s in all_envelopes()
        )["P5-E07"]
        self.assertTrue(
            all(
                not row["arrow_credit"]
                for row in accepted
                if row["holonomy"] and not row["drive"]
            )
        )

    def test_reachability_alone_never_forces_occurrence(self) -> None:
        _, accepted, _, _ = dict(
            (r.family_id, (r, a, b, s)) for r, a, b, s in all_envelopes()
        )["P5-E08"]
        self.assertTrue(
            any(row["reachable"] and not row["occurrent"] for row in accepted)
        )

    def test_unpriced_observer_never_gets_native_or_joint_credit(self) -> None:
        _, accepted, _, _ = dict(
            (r.family_id, (r, a, b, s)) for r, a, b, s in all_envelopes()
        )["P5-E09"]
        self.assertTrue(
            all(
                not row["native_credit"] and not row["joint_credit"]
                for row in accepted
                if row["charged"] < row["occupied"]
            )
        )

    def test_three_domain_symmetry_reduces_carrier(self) -> None:
        result, _, _, symmetry_rule = dict(
            (r.family_id, (r, a, b, s)) for r, a, b, s in all_envelopes()
        )["P5-E10"]
        self.assertLess(result.canonical_cardinality, result.raw_cardinality)
        self.assertEqual(symmetry_rule, "QUOTIENT_BY_AB_BC_PAIR_LABEL_SWAP")


if __name__ == "__main__":
    unittest.main()
