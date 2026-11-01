"""Focused tests for the standalone XML structural diff utility."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
from xml_tree_diff import diff_xml, format_diff  # noqa: E402


class XmlTreeDiffTests(unittest.TestCase):
    def test_added_removed_changed_elements_attributes_and_text(self):
        result = diff_xml(
            '<root><item id="a" enabled="no">old</item><gone/></root>',
            '<root><item id="a" enabled="yes">new</item><fresh/></root>',
        )
        self.assertEqual([entry["path"] for entry in result["added"]], ["/root[1]/fresh[1]"])
        self.assertEqual([entry["path"] for entry in result["removed"]], ["/root[1]/gone[1]"])
        self.assertEqual(len(result["changed"]), 1)
        self.assertEqual(result["changed"][0]["before"]["text"], "old")
        self.assertEqual(result["changed"][0]["after"]["attributes"]["enabled"], "yes")

    def test_unique_key_identifies_moved_element(self):
        result = diff_xml(
            '<root><left><item id="x">same</item></left><right/></root>',
            '<root><left/><right><item id="x">same</item></right></root>',
        )
        self.assertEqual(result["moved"], [{"from": "/root[1]/left[1]/item[1]", "to": "/root[1]/right[1]/item[1]"}])
        self.assertEqual(result["added"], [])
        self.assertEqual(result["removed"], [])
        self.assertEqual(result["changed"], [])

    def test_sibling_order_change_is_move(self):
        result = diff_xml('<root><item id="a"/><item id="b"/></root>', '<root><item id="b"/><item id="a"/></root>')
        self.assertEqual(len(result["moved"]), 2)
        self.assertEqual(
            {(move["from"], move["to"]) for move in result["moved"]},
            {
                ("/root[1]/item[1]", "/root[1]/item[2]"),
                ("/root[1]/item[2]", "/root[1]/item[1]"),
            },
        )

    def test_namespace_aware_paths_and_attributes(self):
        result = diff_xml('<r xmlns="urn:old"><x id="1"/></r>', '<r xmlns="urn:new"><x id="1"/></r>')
        self.assertEqual(result["removed"][0]["path"], "/{urn:old}r[1]")
        self.assertEqual(result["added"][0]["path"], "/{urn:new}r[1]")

    def test_empty_documents_have_empty_diff(self):
        self.assertEqual(diff_xml("<root/>", "<root></root>"), {"added": [], "removed": [], "changed": [], "moved": []})

    def test_malformed_and_empty_input_rejected(self):
        for value in ("<root>", "", "not xml"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                diff_xml(value, "<root/>")

    def test_ambiguous_ids_fall_back_to_paths(self):
        result = diff_xml('<root><item id="x"/><item id="x"/></root>', '<root><item id="x"/><item id="x"/></root>')
        self.assertEqual(result, {"added": [], "removed": [], "changed": [], "moved": []})

    def test_output_is_deterministic_and_valid_json(self):
        before, after = '<r><x id="2"/><x id="1"/></r>', '<r><x id="1"/><x id="2"/></r>'
        self.assertEqual(format_diff(before, after), format_diff(before, after))
        self.assertIn('"moved"', format_diff(before, after))


if __name__ == "__main__":
    unittest.main()
