"""envchain.limiter — Limit env dicts to a maximum number of keys or value length."""

from __future__ import annotations

from typing import Dict, Optional


class LimitError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def limit_keys(
    env: Dict[str, str],
    max_keys: int,
    *,
    strategy: str = "first",
) -> Dict[str, str]:
    """Return a copy of *env* containing at most *max_keys* entries.

    strategy:
      - ``"first"``  — keep the first N keys in insertion order (default)
      - ``"last"``   — keep the last N keys in insertion order
      - ``"alpha"``  — keep the first N keys in alphabetical order
    """
    if max_keys < 0:
        raise LimitError(f"max_keys must be >= 0, got {max_keys}")
    if strategy not in ("first", "last", "alpha"):
        raise LimitError(f"Unknown strategy {strategy!r}; choose 'first', 'last', or 'alpha'")

    keys = list(env.keys())
    if strategy == "alpha":
        keys = sorted(keys)
    elif strategy == "last":
        keys = keys[-max_keys:] if max_keys else []

    selected = keys[:max_keys]
    return {k: env[k] for k in selected}


def limit_value_length(
    env: Dict[str, str],
    max_length: int,
    *,
    truncate: bool = False,
    placeholder: str = "...",
) -> Dict[str, str]:
    """Enforce a maximum character length on every value in *env*.

    If *truncate* is ``True``, values exceeding *max_length* are shortened and
    *placeholder* is appended (the total length is capped at *max_length*).
    If *truncate* is ``False`` (default), a :class:`LimitError` is raised.
    """
    if max_length < 0:
        raise LimitError(f"max_length must be >= 0, got {max_length}")

    result: Dict[str, str] = {}
    for key, value in env.items():
        if len(value) <= max_length:
            result[key] = value
        elif truncate:
            cut = max(0, max_length - len(placeholder))
            result[key] = value[:cut] + placeholder
        else:
            raise LimitError(
                f"Value for key {key!r} exceeds max_length {max_length} "
                f"(got {len(value)} chars)"
            )
    return result


def limit_env(
    env: Dict[str, str],
    *,
    max_keys: Optional[int] = None,
    max_value_length: Optional[int] = None,
    key_strategy: str = "first",
    truncate_values: bool = False,
    truncate_placeholder: str = "...",
) -> Dict[str, str]:
    """Convenience wrapper that applies both key and value limits in one call."""
    result = dict(env)
    if max_keys is not None:
        result = limit_keys(result, max_keys, strategy=key_strategy)
    if max_value_length is not None:
        result = limit_value_length(
            result,
            max_value_length,
            truncate=truncate_values,
            placeholder=truncate_placeholder,
        )
    return result
