import tempfile
import unittest
from pathlib import Path

from json_db import JsonDB


class JsonDbIdAllocationTests(unittest.TestCase):
    def test_insert_does_not_reuse_id_after_deleting_a_lower_id(self):
        with tempfile.TemporaryDirectory() as temp:
            collection = JsonDB(str(Path(temp) / "db.json")).collection("items")
            original_ids = [collection.insert({"value": value}) for value in range(3)]
            collection.delete({"_id": original_ids[0]})

            new_id = collection.insert({"value": "new"})
            existing_ids = [doc["_id"] for doc in collection.find()]

            self.assertEqual(new_id, 4)
            self.assertEqual(len(existing_ids), len(set(existing_ids)))
            self.assertNotIn(new_id, original_ids[1:])


if __name__ == "__main__":
    unittest.main()
