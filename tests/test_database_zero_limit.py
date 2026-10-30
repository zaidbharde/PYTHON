import tempfile
import unittest

from database_engine import Column, Database


class ZeroLimitRegressionTests(unittest.TestCase):
    def test_limit_zero_returns_no_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Database("test", data_dir=temp)
            table = db.create_table("items", [Column("value", "int")])
            table.insert_many([{"value": 1}, {"value": 2}])
            self.assertEqual(len(db.query("items").limit(0).execute()), 0)


if __name__ == "__main__":
    unittest.main()
