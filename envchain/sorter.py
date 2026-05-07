"""envchain.sorter — Utilities for sorting and ordering env variable dicts."""

from __future__ import annotations

from typing import Callable, Dict, Iterable, Optional


class SorterError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def sort_keys(
    env: Dict[str, str],
    *,
    reverse: bool = False,
) -> Dict[str, str]:
    """Return a new dict with keys sorted alphabetically."""
    return dict(sorted(env.items(), key=lambda item: item[0], reverse=reverse))


def sort_by_value(
    env: Dict[str, str],
    *,
    reverse: bool = False,
) -> Dict[str, str]:
    """Return a new dict with entries sorted by value alphabetically."""
    return dict(sorted(env.items(), key=lambda item: item[1], reverse=reverse))


def sort_by_custom(
    env: Dict[str, str],
    key_fn: Callable[[tuple], object],
    *,
    reverse: bool = False,
) -> Dict[str, str]:
    """Return a new dict sorted by a custom key function applied to (k, v) tuples."""
    if not callable(key_fn):
        raise SorterError("key_fn must be callable")
    return dict(sorted(env.items(), key=key_fn, reverse=reverse))


def prioritise_keys(
    env: Dict[str, str],
    priority: Iterable[str],
    *,
    reverse_rest: bool = False,
) -> Dict[str, str]:
    """Return a new dict with the given keys placed first (in order), remaining
    keys follow sorted alphabetically.  Keys in *priority* that are absent from
    *env* are silently ignored."""
    priority_list = list(priority)
    seen: set = set()
    result: Dict[str, str] = {}
    for k in priority_list:
        if k in env:
            result[k] = env[k]
            seen.add(k)
    rest = {k: v for k, v in env.items() if k not in seen}
    result.update(sort_keys(rest, reverse=reverse_rest))
    return result
