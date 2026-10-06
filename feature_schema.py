"""Validate that tabular records contain the features a model expects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Iterable, Any


@dataclass(frozen=True)
class SchemaIssue:
    """A missing, unexpected, or null feature discovered during validation."""

    field: str
    reason: str


def validate_record(
    record: Mapping[str, Any],
    required_fields: Iterable[str],
    *,
    allow_extra: bool = True,
) -> list[SchemaIssue]:
    """Return deterministic issues without mutating the incoming record."""
    required = tuple(dict.fromkeys(required_fields))
    issues = [SchemaIssue(field, "missing") for field in required if field not in record]
    issues.extend(SchemaIssue(field, "null") for field in required if field in record and record[field] is None)
    if not allow_extra:
        expected = set(required)
        issues.extend(SchemaIssue(field, "unexpected") for field in sorted(set(record) - expected))
    return sorted(issues, key=lambda issue: (issue.field, issue.reason))


def is_valid_record(record: Mapping[str, Any], required_fields: Iterable[str]) -> bool:
    """Return whether all required fields are present and non-null."""
    return not validate_record(record, required_fields)
