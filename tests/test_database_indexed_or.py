import tempfile
import unittest

from database_engine import Column, Database


class IndexedOrRegressionTests(unittest.TestCase):
    def test_or_alternative_is_not_dropped_by_index_fast_path(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Database("test", data_dir=temp)
            table = db.create_table("items", [Column("category", "str")])
            table.insert_many([
                {"category": "wanted"},
                {"category": "other"},
                {"category": "fallback"},
            ])
            table.create_index("category")

            result = db.query("items").where("category", "=", "wanted").or_where(
                "category", "=", "fallback"
            ).execute()
            self.assertEqual([row["category"] for row in result], ["wanted", "fallback"])


if __name__ == "__main__":
    unittest.main()
