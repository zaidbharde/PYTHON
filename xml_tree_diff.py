"""Deterministic structural comparison for XML documents.

Elements are addressed by expanded-name paths with same-name sibling indexes.
Unique ``id``, ``name``, or ``key`` attributes identify elements across paths,
allowing moves to be reported. Ambiguous keys deliberately fall back to paths.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from typing import Any

_KEY_ATTRIBUTES = ("id", "name", "key")


def _tag(tag: str) -> str:
    """Return a readable, namespace-preserving element name."""
    if tag.startswith("{"):
        uri, local = tag[1:].split("}", 1)
        return f"{{{uri}}}{local}"
    return tag


def _paths(root: ET.Element) -> dict[str, ET.Element]:
    result: dict[str, ET.Element] = {}

    def visit(element: ET.Element, path: str) -> None:
        result[path] = element
        counts: Counter[str] = Counter()
        for child in element:
            name = _tag(child.tag)
            counts[name] += 1
            visit(child, f"{path}/{name}[{counts[name]}]")

    visit(root, f"/{_tag(root.tag)}[1]")
    return result


def _identities(paths: dict[str, ET.Element]) -> dict[str, str]:
    candidates: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for path, element in paths.items():
        for attribute in _KEY_ATTRIBUTES:
            value = element.get(attribute)
            if value is not None:
                candidates[(_tag(element.tag), attribute, value)].append(path)
                break
    return {
        path: f"{tag}\0{attribute}\0{value}"
        for (tag, attribute, value), matches in candidates.items()
        if len(matches) == 1
        for path in matches
    }


def _values(element: ET.Element) -> dict[str, Any]:
    return {"attributes": dict(sorted(element.attrib.items())), "text": (element.text or "").strip()}


def diff_xml(before: str, after: str) -> dict[str, list[dict[str, Any]]]:
    """Compare XML strings; malformed documents raise ``ValueError``.

    Output keys are ``added``, ``removed``, ``changed``, and ``moved``. Text
    means trimmed direct element text; comments and formatting-only whitespace
    are ignored. Each list and each record has deterministic ordering.
    """
    try:
        old_root, new_root = ET.fromstring(before), ET.fromstring(after)
    except (ET.ParseError, TypeError) as exc:
        raise ValueError(f"invalid XML: {exc}") from exc

    old, new = _paths(old_root), _paths(new_root)
    old_ids, new_ids = _identities(old), _identities(new)
    old_by_id = {identity: path for path, identity in old_ids.items()}
    new_by_id = {identity: path for path, identity in new_ids.items()}
    pairs: list[tuple[str, str]] = []
    used_old: set[str] = set()
    used_new: set[str] = set()

    for identity in sorted(old_by_id.keys() & new_by_id.keys()):
        old_path, new_path = old_by_id[identity], new_by_id[identity]
        pairs.append((old_path, new_path))
        used_old.add(old_path)
        used_new.add(new_path)
    for path in sorted(old.keys() & new.keys()):
        if path not in used_old and path not in used_new:
            pairs.append((path, path))
            used_old.add(path)
            used_new.add(path)

    added = [{"path": path, **_values(new[path])} for path in sorted(new.keys() - used_new)]
    removed = [{"path": path, **_values(old[path])} for path in sorted(old.keys() - used_old)]
    changed = []
    moved = []
    for old_path, new_path in sorted(pairs, key=lambda pair: (pair[1], pair[0])):
        old_value, new_value = _values(old[old_path]), _values(new[new_path])
        if old_path != new_path:
            moved.append({"from": old_path, "to": new_path})
        if old_value != new_value:
            changed.append({"path": new_path, "before": old_value, "after": new_value})

    return {"added": added, "removed": removed, "changed": changed, "moved": moved}


def format_diff(before: str, after: str) -> str:
    """Serialize :func:`diff_xml` as canonical compact JSON."""
    return json.dumps(diff_xml(before, after), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    print(format_diff(args.before.read_text(encoding="utf-8"), args.after.read_text(encoding="utf-8")))
