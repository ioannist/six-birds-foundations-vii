from __future__ import annotations

import unittest

from fvii_lab.evaluator import evaluate


class ProtocolBoundaryTests(unittest.TestCase):
    def test_holonomy_does_not_imply_directionality(self) -> None:
        status, facts = evaluate({"contact": True, "holonomy": True, "drive": False})
        self.assertEqual(status, "HOLONOMY_ZERO_ARROW")
        self.assertTrue(facts.holonomy)
        self.assertFalse(facts.directionality)

    def test_soundness_does_not_imply_reachability(self) -> None:
        status, facts = evaluate({"sound": True, "reachable": False})
        self.assertEqual(status, "SOUND_UNREACHABLE")
        self.assertFalse(facts.reachable)

    def test_reachability_does_not_imply_occurrence(self) -> None:
        status, facts = evaluate({"sound": True, "reachable": True, "fired": False})
        self.assertEqual(status, "REACHABLE_NONOCCURRENT")
        self.assertFalse(facts.occurred)

    def test_contact_does_not_imply_join(self) -> None:
        status, facts = evaluate({"contact": True, "composite": False})
        self.assertEqual(status, "CONTACT_WITHOUT_JOIN")
        self.assertTrue(facts.contact)
        self.assertFalse(facts.strict_join)

    def test_finite_negative_does_not_change_scope(self) -> None:
        status, facts = evaluate({"sound": True, "reachable": False})
        self.assertEqual(status, "SOUND_UNREACHABLE")
        self.assertFalse(facts.occurred)
        # The evaluator deliberately has no "universal_impossibility" fact.
        self.assertNotIn("universal_impossibility", facts.as_mapping())


if __name__ == "__main__":
    unittest.main()
