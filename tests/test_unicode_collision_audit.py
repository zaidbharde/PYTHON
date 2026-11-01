"""Tests for Unicode identifier collision auditing."""
import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "unicode_collision_audit.py"
SPEC = importlib.util.spec_from_file_location("unicode_collision_audit", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
collision_groups = MODULE.collision_groups


class CollisionGroupsTests(unittest.TestCase):
    def test_canonical_nfc_collision_preserves_spellings(self):
        self.assertEqual(collision_groups(["é", "e\u0301", "x"]), [["é", "e\u0301"]])

    def test_case_folding_is_optional_and_unicode_aware(self):
        names = ["Admin", "admin", "Straße", "STRASSE"]
        self.assertEqual(collision_groups(names), [])
        self.assertEqual(
            collision_groups(names, case_fold=True),
            [["Admin", "admin"], ["Straße", "STRASSE"]],
        )

    def test_compatibility_normalization_can_be_selected(self):
        names = ["Ａ", "A"]
        self.assertEqual(collision_groups(names), [])
        self.assertEqual(collision_groups(names, normalization="NFKC"), [names])

    def test_groups_and_members_are_stable_and_distinct_names_remain_out(self):
        names = ["B", "b", "A", "a", "unique"]
        self.assertEqual(
            collision_groups(names, case_fold=True), [["B", "b"], ["A", "a"]]
        )
        self.assertEqual(collision_groups(["one", "two", "three"]), [])

    def test_empty_input(self):
        self.assertEqual(collision_groups([]), [])

    def test_repeated_identical_spelling_is_a_collision(self):
        self.assertEqual(collision_groups(["same", "same"]), [["same", "same"]])

    def test_invalid_normalization_and_non_string_names_are_rejected(self):
        with self.assertRaises(ValueError):
            collision_groups(["name"], normalization="BAD")
        with self.assertRaises(TypeError):
            collision_groups(["name", 3])


if __name__ == "__main__":
    unittest.main()
