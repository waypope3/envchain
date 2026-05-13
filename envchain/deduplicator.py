"""envchain.deduplicator — Remove duplicate values from env dicts."""
from __future__ import annotations

from typing import Dict, Any, List, Optional


class DeduplicateError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def deduplicate_values(
    env: Dict[str, Any],
    *,
    keep: str = "first",
) -> Dict[str, Any]:
    """Return a new dict with only the first (or last) key for each unique value.

    Args:
        env:  Input environment dict.
        keep: ``'first'`` keeps the first key encountered for each value;
              ``'last'`` keeps the last.

    Returns:
        New dict with duplicate values removed.

    Raises:
        DeduplicateError: If *keep* is not ``'first'`` or ``'last'``.
    """
    if keep not in ("first", "last"):
        raise DeduplicateError(
            f"Invalid keep strategy '{keep}': must be 'first' or 'last'."
        )

    seen: Dict[Any, str] = {}
    items = list(env.items())
    if keep == "last":
        items = list(reversed(items))

    for key, value in items:
        if value not in seen:
            seen[value] = key

    chosen_keys = set(seen.values())
    return {k: v for k, v in env.items() if k in chosen_keys}


def find_duplicate_keys(
    env: Dict[str, Any],
) -> Dict[Any, List[str]]:
    """Return a mapping from value -> list of keys that share that value.

    Only values that appear more than once are included.

    Args:
        env: Input environment dict.

    Returns:
        Dict mapping duplicated values to the list of keys holding them.
    """
    from collections import defaultdict

    value_to_keys: Dict[Any, List[str]] = defaultdict(list)
    for key, value in env.items():
        value_to_keys[value].append(key)

    return {v: keys for v, keys in value_to_keys.items() if len(keys) > 1}


def has_duplicate_values(env: Dict[str, Any]) -> bool:
    """Return True if any two keys in *env* share the same value."""
    values = list(env.values())
    return len(values) != len(set(values))
