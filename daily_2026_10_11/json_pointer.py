"""Resolve and update values using RFC 6901-style JSON pointer paths."""
from collections.abc import MutableMapping, MutableSequence


def _tokens(pointer: str) -> list[str]:
    if pointer == "":
        return []
    if not pointer.startswith("/"):
        raise ValueError("pointer must be empty or begin with '/'")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def resolve(document: object, pointer: str) -> object:
    """Return the value selected by pointer, raising KeyError on a miss."""
    current = document
    for token in _tokens(pointer):
        if isinstance(current, MutableMapping):
            current = current[token]
        elif isinstance(current, MutableSequence):
            current = current[int(token)]
        else:
            raise KeyError(token)
    return current


def assign(document: object, pointer: str, value: object) -> None:
    """Replace a selected mapping value or list element in place."""
    tokens = _tokens(pointer)
    if not tokens:
        raise ValueError("root replacement requires returning a new document")
    parent = resolve(document, "/" + "/".join(token.replace("~", "~0").replace("/", "~1")
                                          for token in tokens[:-1]))
    token = tokens[-1]
    if isinstance(parent, MutableMapping):
        if token not in parent:
            raise KeyError(token)
        parent[token] = value
    elif isinstance(parent, MutableSequence):
        parent[int(token)] = value
    else:
        raise KeyError(token)


if __name__ == "__main__":
    record = {"profile": {"name": "Ada", "roles": ["builder"]}}
    assign(record, "/profile/name", "Grace")
    print(resolve(record, "/profile/name"))
