"""Flatten and unflatten nested env-like dicts using delimiter-separated keys."""

from typing import Any


class FlattenError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def flatten_dict(nested: dict, delimiter: str = "__", prefix: str = "") -> dict:
    """Recursively flatten a nested dict into a single-level dict.

    Keys are joined using the given delimiter.
    Only string leaf values are preserved; non-string leaves are converted via str().

    Example:
        {"DB": {"HOST": "localhost", "PORT": "5432"}} ->
        {"DB__HOST": "localhost", "DB__PORT": "5432"}
    """
    if not isinstance(nested, dict):
        raise FlattenError(f"Expected a dict, got {type(nested).__name__}")
    if not delimiter:
        raise FlattenError("Delimiter must be a non-empty string")

    result = {}
    for key, value in nested.items():
        if not isinstance(key, str):
            raise FlattenError(f"All keys must be strings, got {type(key).__name__}: {key!r}")
        full_key = f"{prefix}{delimiter}{key}" if prefix else key
        if isinstance(value, dict):
            nested_flat = flatten_dict(value, delimiter=delimiter, prefix=full_key)
            result.update(nested_flat)
        else:
            result[full_key] = str(value) if not isinstance(value, str) else value
    return result


def unflatten_dict(flat: dict, delimiter: str = "__") -> dict:
    """Reconstruct a nested dict from a flat delimiter-separated dict.

    Example:
        {"DB__HOST": "localhost", "DB__PORT": "5432"} ->
        {"DB": {"HOST": "localhost", "PORT": "5432"}}
    """
    if not isinstance(flat, dict):
        raise FlattenError(f"Expected a dict, got {type(flat).__name__}")
    if not delimiter:
        raise FlattenError("Delimiter must be a non-empty string")

    result: dict[str, Any] = {}
    for key, value in flat.items():
        if not isinstance(key, str):
            raise FlattenError(f"All keys must be strings, got {type(key).__name__}: {key!r}")
        parts = key.split(delimiter)
        node = result
        for part in parts[:-1]:
            if part not in node:
                node[part] = {}
            elif not isinstance(node[part], dict):
                raise FlattenError(
                    f"Key conflict: '{part}' is both a leaf and a branch in key '{key}'"
                )
            node = node[part]
        leaf = parts[-1]
        if leaf in node and isinstance(node[leaf], dict):
            raise FlattenError(
                f"Key conflict: '{leaf}' is both a branch and a leaf in key '{key}'"
            )
        node[leaf] = value
    return result
