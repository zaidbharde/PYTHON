import unittest

from json_patch_paths import diff_paths


class EmptyContainerDiffTests(unittest.TestCase):
    def test_added_empty_object_is_reported(self):
        self.assertEqual(diff_paths({}, {"settings": {}}), {"/settings": (None, {})})

    def test_added_empty_array_is_reported(self):
        self.assertEqual(diff_paths({}, {"items": []}), {"/items": (None, [])})

    def test_empty_array_replaced_by_values_reports_change(self):
        changes = diff_paths({"items": []}, {"items": [1]})
        self.assertIn("/items", changes)
        self.assertIn("/items/0", changes)


if __name__ == "__main__":
    unittest.main()
