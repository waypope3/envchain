"""Key selector and filter utilities for envchain."""

import re
from typing import Dict, List, Optional, Pattern, Union


class SelectorError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def select_keys(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return a dict containing only the specified keys."""
    missing = [k for k in keys if k not in env]
    if missing:
        raise SelectorError(f"Keys not found in env: {missing}")
    return {k: env[k] for k in keys}


def exclude_keys(env: Dict[str, str], keys: List[str]) -> Dict[str, str]:
    """Return a dict with the specified keys removed."""
    return {k: v for k, v in env.items() if k not in keys}


def select_by_pattern(
    env: Dict[str, str],
    pattern: Union[str, Pattern],
    strip_match: bool = False,
) -> Dict[str, str]:
    """Return keys matching a regex pattern.

    If strip_match is True, removes the matched prefix from each key.
    """
    compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
    result = {}
    for key, value in env.items():
        m = compiled.match(key)
        if m:
            new_key = key[m.end():] if strip_match else key
            if new_key == "":
                continue
            result[new_key] = value
    return result


def select_by_prefix(
    env: Dict[str, str],
    prefix: str,
    strip_prefix: bool = True,
) -> Dict[str, str]:
    """Return keys that start with the given prefix.

    If strip_prefix is True (default), the prefix is removed from keys.
    """
    if not prefix:
        raise SelectorError("Prefix must be a non-empty string.")
    result = {}
    for key, value in env.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):] if strip_prefix else key
            if new_key == "":
                continue
            result[new_key] = value
    return result


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    strict: bool = False,
) -> Dict[str, str]:
    """Rename keys according to a mapping dict {old_name: new_name}.

    If strict is True, raises SelectorError for missing keys.
    """
    if strict:
        missing = [k for k in mapping if k not in env]
        if missing:
            raise SelectorError(f"Keys to rename not found: {missing}")
    result = dict(env)
    for old, new in mapping.items():
        if old in result:
            result[new] = result.pop(old)
    return result
