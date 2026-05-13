"""envchain.renamer — Rename keys in an env dict via a mapping or callable."""
from __future__ import annotations

from typing import Callable, Dict, Union


class RenameError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    *,
    strict: bool = False,
) -> Dict[str, str]:
    """Return a copy of *env* with keys renamed according to *mapping*.

    Keys not present in *mapping* are kept as-is.  If *strict* is True,
    every key in *mapping* must exist in *env*; otherwise a RenameError
    is raised.
    """
    if not isinstance(mapping, dict):
        raise RenameError("mapping must be a dict")
    if strict:
        missing = [k for k in mapping if k not in env]
        if missing:
            raise RenameError(
                f"strict=True but keys not found in env: {missing}"
            )
    result: Dict[str, str] = {}
    for key, value in env.items():
        new_key = mapping.get(key, key)
        if new_key in result:
            raise RenameError(
                f"Rename collision: multiple keys would become '{new_key}'"
            )
        result[new_key] = value
    return result


def rename_by(
    env: Dict[str, str],
    func: Callable[[str], str],
) -> Dict[str, str]:
    """Return a copy of *env* with every key transformed by *func*.

    Raises RenameError if *func* produces duplicate keys.
    """
    if not callable(func):
        raise RenameError("func must be callable")
    result: Dict[str, str] = {}
    for key, value in env.items():
        new_key = func(key)
        if new_key in result:
            raise RenameError(
                f"Rename collision: multiple keys would become '{new_key}'"
            )
        result[new_key] = value
    return result


def build_rename_mapping(
    env: Dict[str, str],
    func: Callable[[str], str],
) -> Dict[str, str]:
    """Return a mapping of old_key -> new_key for all keys in *env*."""
    return {key: func(key) for key in env}
