"""envchain.splitter — Split a flat env dict into multiple named partitions."""

from __future__ import annotations

from typing import Callable, Dict, List, Optional


class SplitError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def split_by_prefix(
    env: Dict[str, str],
    prefixes: List[str],
    separator: str = "_",
    strip_prefix: bool = True,
) -> Dict[str, Dict[str, str]]:
    """Partition *env* into buckets keyed by prefix.

    Keys that match no prefix land in the ``"__other__"`` bucket.
    """
    if not isinstance(separator, str) or len(separator) == 0:
        raise SplitError("separator must be a non-empty string")

    result: Dict[str, Dict[str, str]] = {p: {} for p in prefixes}
    result["__other__"] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            full_prefix = prefix + separator
            if key.startswith(full_prefix):
                bucket_key = key[len(full_prefix):] if strip_prefix else key
                result[prefix][bucket_key] = value
                matched = True
                break
        if not matched:
            result["__other__"][key] = value

    return result


def split_by_predicate(
    env: Dict[str, str],
    predicates: Dict[str, Callable[[str, str], bool]],
) -> Dict[str, Dict[str, str]]:
    """Partition *env* using named predicate callables.

    Each key/value pair is placed in the first bucket whose predicate returns
    ``True``.  Unmatched pairs go to ``"__other__"``.
    """
    result: Dict[str, Dict[str, str]] = {name: {} for name in predicates}
    result["__other__"] = {}

    for key, value in env.items():
        matched = False
        for name, predicate in predicates.items():
            if predicate(key, value):
                result[name][key] = value
                matched = True
                break
        if not matched:
            result["__other__"][key] = value

    return result


def split_by_keys(
    env: Dict[str, str],
    key_groups: Dict[str, List[str]],
    strict: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Partition *env* by explicit key lists.

    If *strict* is ``True``, a :class:`SplitError` is raised for any requested
    key that is absent from *env*.
    """
    result: Dict[str, Dict[str, str]] = {}
    assigned: set = set()

    for group, keys in key_groups.items():
        bucket: Dict[str, str] = {}
        for k in keys:
            if k in env:
                bucket[k] = env[k]
                assigned.add(k)
            elif strict:
                raise SplitError(f"key '{k}' not found in env")
        result[group] = bucket

    result["__other__"] = {k: v for k, v in env.items() if k not in assigned}
    return result
