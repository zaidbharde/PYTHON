import json
import os
import re
import operator
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Callable
from datetime import datetime
from pathlib import Path
from copy import deepcopy

@dataclass
class Column:
    name:     str
    dtype:    str = "any"
    nullable: bool = True
    default:  Any = None
    unique:   bool = False

@dataclass
class Index:
    name:    str
    column:  str
    data:    Dict[Any, List[int]] = field(default_factory=dict)

    def build(self, rows: List[Dict]):
        self.data.clear()
        for i, row in enumerate(rows):
            val = row.get(self.column)
            self.data.setdefault(val, []).append(i)

    def lookup(self, value: Any) -> List[int]:
        return self.data.get(value, [])

class Table:
    def __init__(self, name: str, columns: List[Column]):
        self.name      = name
        self.columns   = {c.name: c for c in columns}
        self.rows:     List[Dict] = []
        self.indexes:  Dict[str, Index] = {}
        self.auto_id   = 0
        self.created_at = datetime.now().isoformat()

    def validate_row(self, row: Dict) -> Dict:
        validated = {}
        for col_name, col in self.columns.items():
            value = row.get(col_name, col.default)

            if col_name == "id" and value is None:
                self.auto_id += 1
                value = self.auto_id

            if value is None and not col.nullable:
                raise ValueError(f"Column '{col_name}' cannot be null")

            if value is not None and col.dtype != "any":
                type_map = {"int": int, "float": float, "str": str, "bool": bool}
                expected = type_map.get(col.dtype)
                if expected and not isinstance(value, expected):
                    try:
                        value = expected(value)
                    except:
                        raise TypeError(f"Column '{col_name}' expects {col.dtype}, got {type(value).__name__}")

            if col.unique and value is not None:
                for existing in self.rows:
                    if existing.get(col_name) == value:
                        raise ValueError(f"Duplicate value '{value}' for unique column '{col_name}'")

            validated[col_name] = value
        return validated

    def insert(self, row: Dict) -> Dict:
        validated = self.validate_row(row)
        self.rows.append(validated)
        for idx in self.indexes.values():
            val = validated.get(idx.column)
            idx.data.setdefault(val, []).append(len(self.rows) - 1)
        return validated

    def insert_many(self, rows: List[Dict]) -> int:
        count = 0
        for row in rows:
            self.insert(row)
            count += 1
        return count

    def create_index(self, column: str):
        idx = Index(name=f"idx_{self.name}_{column}", column=column)
        idx.build(self.rows)
        self.indexes[column] = idx

    def rebuild_indexes(self):
        for idx in self.indexes.values():
            idx.build(self.rows)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "columns": {n: {"dtype": c.dtype, "nullable": c.nullable, "unique": c.unique, "default": c.default}
                        for n, c in self.columns.items()},
            "rows": self.rows,
            "auto_id": self.auto_id,
            "created_at": self.created_at,
            "indexes": list(self.indexes.keys())
        }


class QueryResult:
    def __init__(self, rows: List[Dict], columns: List[str] = None):
        self.rows    = rows
        self.columns = columns or (list(rows[0].keys()) if rows else [])

    def __len__(self):   return len(self.rows)
    def __iter__(self):  return iter(self.rows)
    def __repr__(self):  return f"QueryResult({len(self.rows)} rows)"

    def to_table(self, max_rows: int = 50) -> str:
        if not self.rows:
            return "  (empty result set)"

        cols = self.columns
        widths = {c: len(str(c)) for c in cols}
        display_rows = self.rows[:max_rows]

        for row in display_rows:
            for c in cols:
                widths[c] = max(widths[c], len(str(row.get(c, "NULL"))))

        header = "  " + " | ".join(str(c).ljust(widths[c]) for c in cols)
        sep    = "  " + "-+-".join("-" * widths[c] for c in cols)
        lines  = [header, sep]

        for row in display_rows:
            line = "  " + " | ".join(str(row.get(c, "NULL")).ljust(widths[c]) for c in cols)
            lines.append(line)

        if len(self.rows) > max_rows:
            lines.append(f"  ... and {len(self.rows) - max_rows} more rows")

        lines.append(f"\n  ({len(self.rows)} rows)")
        return "\n".join(lines)


OPS = {
    "=":  operator.eq,  "!=": operator.ne,
    ">":  operator.gt,  ">=": operator.ge,
    "<":  operator.lt,  "<=": operator.le,
}

class Query:
    def __init__(self, table: Table):
        self.table       = table
        self._conditions = []
        self._or_conditions = []
        self._select     = None
        self._order_by   = None
        self._order_desc = False
        self._limit      = None
        self._offset     = 0
        self._group_by   = None
        self._aggregates = {}
        self._distinct   = False

    def select(self, *columns) -> 'Query':
        self._select = list(columns)
        return self

    def where(self, column: str, op: str, value: Any) -> 'Query':
        self._conditions.append((column, op, value))
        return self

    def or_where(self, column: str, op: str, value: Any) -> 'Query':
        self._or_conditions.append((column, op, value))
        return self

    def order_by(self, column: str, desc: bool = False) -> 'Query':
        self._order_by = column
        self._order_desc = desc
        return self

    def limit(self, n: int) -> 'Query':
        self._limit = n
        return self

    def offset(self, n: int) -> 'Query':
        self._offset = n
        return self

    def group_by(self, column: str) -> 'Query':
        self._group_by = column
        return self

    def count(self, alias: str = "count") -> 'Query':
        self._aggregates[alias] = ("count", None)
        return self

    def sum(self, column: str, alias: str = None) -> 'Query':
        self._aggregates[alias or f"sum_{column}"] = ("sum", column)
        return self

    def avg(self, column: str, alias: str = None) -> 'Query':
        self._aggregates[alias or f"avg_{column}"] = ("avg", column)
        return self

    def max_val(self, column: str, alias: str = None) -> 'Query':
        self._aggregates[alias or f"max_{column}"] = ("max", column)
        return self

    def min_val(self, column: str, alias: str = None) -> 'Query':
        self._aggregates[alias or f"min_{column}"] = ("min", column)
        return self

    def distinct(self) -> 'Query':
        self._distinct = True
        return self

    def _match_row(self, row: Dict) -> bool:
        and_match = all(
            OPS.get(op, operator.eq)(row.get(col), val)
            for col, op, val in self._conditions
        ) if self._conditions else True

        or_match = any(
            OPS.get(op, operator.eq)(row.get(col), val)
            for col, op, val in self._or_conditions
        ) if self._or_conditions else False

        if self._or_conditions:
            return and_match or or_match
        return and_match

    def execute(self) -> QueryResult:
        if self._conditions and len(self._conditions) == 1:
            col, op, val = self._conditions[0]
            if op == "=" and col in self.table.indexes:
                indices = self.table.indexes[col].lookup(val)
                rows = [self.table.rows[i] for i in indices]
            else:
                rows = [r for r in self.table.rows if self._match_row(r)]
        else:
            rows = [r for r in self.table.rows if self._match_row(r)]

        if self._group_by:
            return self._execute_grouped(rows)

        if self._order_by:
            rows.sort(key=lambda r: r.get(self._order_by, 0), reverse=self._order_desc)

        rows = rows[self._offset:]
        if self._limit:
            rows = rows[:self._limit]

        if self._select:
            rows = [{k: r.get(k) for k in self._select} for r in rows]

        if self._distinct:
            seen = set()
            unique = []
            for r in rows:
                key = tuple(sorted(r.items()))
                if key not in seen:
                    seen.add(key)
                    unique.append(r)
            rows = unique

        return QueryResult(rows)

    def _execute_grouped(self, rows: List[Dict]) -> QueryResult:
        groups = {}
        for row in rows:
            key = row.get(self._group_by)
            groups.setdefault(key, []).append(row)

        result = []
        for key, group_rows in groups.items():
            row = {self._group_by: key}
            for alias, (agg_type, col) in self._aggregates.items():
                if agg_type == "count":
                    row[alias] = len(group_rows)
                elif agg_type == "sum":
                    row[alias] = sum(r.get(col, 0) for r in group_rows)
                elif agg_type == "avg":
                    vals = [r.get(col, 0) for r in group_rows]
                    row[alias] = sum(vals) / len(vals) if vals else 0
                elif agg_type == "max":
                    row[alias] = max(r.get(col, 0) for r in group_rows)
                elif agg_type == "min":
                    row[alias] = min(r.get(col, 0) for r in group_rows)
            result.append(row)

        if self._order_by:
            result.sort(key=lambda r: r.get(self._order_by, 0), reverse=self._order_desc)

        return QueryResult(result)


class Database:
    def __init__(self, name: str = "default", data_dir: str = "./db_data"):
        self.name     = name
        self.tables:  Dict[str, Table] = {}
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_table(self, name: str, columns: List[Column]) -> Table:
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists")
        has_id = any(c.name == "id" for c in columns)
        if not has_id:
            columns.insert(0, Column("id", "int", nullable=False, unique=True))
        table = Table(name, columns)
        self.tables[name] = table
        return table

    def drop_table(self, name: str):
        if name not in self.tables:
            raise ValueError(f"Table '{name}' not found")
        del self.tables[name]

    def table(self, name: str) -> Table:
        if name not in self.tables:
            raise ValueError(f"Table '{name}' not found")
        return self.tables[name]

    def query(self, table_name: str) -> Query:
        return Query(self.table(table_name))

    def save(self):
        db_file = self.data_dir / f"{self.name}.json"
        data = {name: t.to_dict() for name, t in self.tables.items()}
        db_file.write_text(json.dumps(data, indent=2, default=str))

    def load(self):
        db_file = self.data_dir / f"{self.name}.json"
        if not db_file.exists():
            return
        data = json.loads(db_file.read_text())
        for name, tdata in data.items():
            columns = [Column(n, **props) for n, props in tdata["columns"].items()]
            table = Table(name, columns)
            table.rows = tdata["rows"]
            table.auto_id = tdata["auto_id"]
            table.created_at = tdata["created_at"]
            for idx_col in tdata.get("indexes", []):
                table.create_index(idx_col)
            self.tables[name] = table

    def table_info(self, name: str) -> str:
        t = self.table(name)
        lines = [f"\n  Table: {t.name} ({len(t.rows)} rows)"]
        lines.append("  " + "-" * 50)
        lines.append(f"  {'Column':<15} {'Type':<8} {'Null':<6} {'Unique':<8} {'Default'}")
        lines.append("  " + "-" * 50)
        for n, c in t.columns.items():
            lines.append(f"  {n:<15} {c.dtype:<8} {str(c.nullable):<6} {str(c.unique):<8} {c.default}")
        if t.indexes:
            lines.append(f"\n  Indexes: {', '.join(t.indexes.keys())}")
        return "\n".join(lines)


if __name__ == "__main__":
    db = Database("company")

    print("=" * 55)
    print("  Database Engine Demo")
    print("=" * 55)

    employees = db.create_table("employees", [
        Column("name",       "str",   nullable=False),
        Column("department", "str",   nullable=False),
        Column("salary",     "float", nullable=False),
        Column("age",        "int"),
        Column("active",     "bool",  default=True),
    ])

    employees.create_index("department")

    data = [
        {"name": "Alice",   "department": "Engineering", "salary": 95000, "age": 30},
        {"name": "Bob",     "department": "Engineering", "salary": 88000, "age": 28},
        {"name": "Charlie", "department": "Marketing",   "salary": 72000, "age": 35},
        {"name": "Diana",   "department": "Engineering", "salary": 105000,"age": 32},
        {"name": "Eve",     "department": "Marketing",   "salary": 68000, "age": 27},
        {"name": "Frank",   "department": "Sales",       "salary": 78000, "age": 40},
        {"name": "Grace",   "department": "Sales",       "salary": 82000, "age": 33},
        {"name": "Hank",    "department": "Engineering", "salary": 92000, "age": 29},
        {"name": "Ivy",     "department": "Marketing",   "salary": 75000, "age": 31},
        {"name": "Jack",    "department": "Sales",       "salary": 71000, "age": 26},
    ]
    employees.insert_many(data)

    print(db.table_info("employees"))

    print("\n  All employees:")
    result = db.query("employees").execute()
    print(result.to_table())

    print("\n  Engineering, salary > 90000, sorted by salary desc:")
    result = (db.query("employees")
        .select("name", "salary", "age")
        .where("department", "=", "Engineering")
        .where("salary", ">", 90000)
        .order_by("salary", desc=True)
        .execute())
    print(result.to_table())

    print("\n  Top 3 highest paid:")
    result = (db.query("employees")
        .select("name", "department", "salary")
        .order_by("salary", desc=True)
        .limit(3)
        .execute())
    print(result.to_table())

    print("\n  Salary stats by department:")
    result = (db.query("employees")
        .group_by("department")
        .count("headcount")
        .sum("salary", "total_salary")
        .avg("salary", "avg_salary")
        .max_val("salary", "max_salary")
        .min_val("salary", "min_salary")
        .order_by("avg_salary", desc=True)
        .execute())
    print(result.to_table())

    print("\n  Distinct departments:")
    result = (db.query("employees")
        .select("department")
        .distinct()
        .execute())
    print(result.to_table())

    print("\n  Employees aged 28-32 OR in Sales:")
    result = (db.query("employees")
        .select("name", "department", "age")
        .where("age", ">=", 28)
        .where("age", "<=", 32)
        .or_where("department", "=", "Sales")
        .execute())
    print(result.to_table())

    db.save()
    print(f"\n  Database saved to {db.data_dir / db.name}.json")

    import shutil
    shutil.rmtree(db.data_dir, ignore_errors=True)
