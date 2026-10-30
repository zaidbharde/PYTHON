import tempfile
import unittest

from database_engine import Column, Database


class NestedDistinctRegressionTests(unittest.TestCase):
    def test_distinct_handles_unhashable_nested_values(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Database("test", data_dir=temp)
            table = db.create_table("items", [Column("payload")])
            table.insert_many([
                {"payload": {"tags": ["x"]}},
                {"payload": {"tags": ["x"]}},
                {"payload": {"tags": ["y"]}},
            ])
            result = db.query("items").select("payload").distinct().execute()
            self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
