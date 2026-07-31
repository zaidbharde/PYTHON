import json
import os
from datetime import datetime
from typing import Optional

class JsonDB:
    def __init__(self, path="db.json"):
        self.path = path
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                return json.load(f)
        return {"collections": {}}

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2, default=str)

    def collection(self, name):
        if name not in self.data["collections"]:
            self.data["collections"][name] = []
        return Collection(self, name)


class Collection:
    def __init__(self, db, name):
        self.db = db
        self.name = name

    @property
    def _docs(self):
        return self.db.data["collections"][self.name]

    def insert(self, doc):
        doc["_id"] = len(self._docs) + 1
        doc["_created"] = datetime.now().isoformat()
        self._docs.append(doc)
        self.db._save()
        return doc["_id"]

    def find(self, query=None):
        if not query:
            return self._docs[:]
        return [d for d in self._docs if all(d.get(k) == v for k, v in query.items())]

    def find_one(self, query):
        results = self.find(query)
        return results[0] if results else None

    def update(self, query, updates):
        count = 0
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(updates)
                doc["_updated"] = datetime.now().isoformat()
                count += 1
        self.db._save()
        return count

    def delete(self, query):
        before = len(self._docs)
        self.db.data["collections"][self.name] = [
            d for d in self._docs
            if not all(d.get(k) == v for k, v in query.items())
        ]
        self.db._save()
        return before - len(self._docs)

    def count(self, query=None):
        return len(self.find(query))


if __name__ == "__main__":
    db = JsonDB("test_db.json")
    users = db.collection("users")

    print("=" * 40)
    print("  JSON Document Database")
    print("=" * 40)

    users.insert({"name": "Alice", "age": 30, "role": "admin"})
    users.insert({"name": "Bob",   "age": 25, "role": "user"})
    users.insert({"name": "Charlie", "age": 35, "role": "user"})
    users.insert({"name": "Diana", "age": 28, "role": "admin"})

    print(f"\n  All users ({users.count()}):")
    for u in users.find():
        print(f"    #{u['_id']} {u['name']} age={u['age']} role={u['role']}")

    print(f"\n  Admins:")
    for u in users.find({"role": "admin"}):
        print(f"    {u['name']}")

    users.update({"name": "Bob"}, {"age": 26})
    bob = users.find_one({"name": "Bob"})
    print(f"\n  Bob after update: age={bob['age']}")

    deleted = users.delete({"name": "Charlie"})
    print(f"  Deleted {deleted} user(s)")
    print(f"  Remaining: {users.count()}")

    os.remove("test_db.json")
