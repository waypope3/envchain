"""Trimmer: strip, normalize, and clean env variable keys and values."""

from __future__ import annotations


class TrimError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def trim_value(value: str, chars: str | None = None) -> str:
    """Strip leading/trailing whitespace (or custom chars) from a value."""
    if not isinstance(value, str):
        raise TrimError(f"Expected str, got {type(value).__name__}")
    return value.strip(chars)


def trim_key(key: str) -> str:
    """Strip whitespace from a key and normalize to uppercase."""
    if not isinstance(key, str):
        raise TrimError(f"Expected str key, got {type(key).__name__}")
    stripped = key.strip()
    if not stripped:
        raise TrimError("Key must not be empty or whitespace-only")
    return stripped.upper()


def trim_env(
    env: dict[str, str],
    *,
    normalize_keys: bool = False,
    strip_chars: str | None = None,
) -> dict[str, str]:
    """Return a new dict with all keys and values trimmed.

    Args:
        env: Source environment dictionary.
        normalize_keys: If True, keys are also uppercased after stripping.
        strip_chars: Custom characters to strip from values (default: whitespace).

    Returns:
        A new dict with cleaned keys and values.

    Raises:
        TrimError: If any key is empty after stripping.
    """
    result: dict[str, str] = {}
    for key, value in env.items():
        clean_key = key.strip()
        if not clean_key:
            raise TrimError("Encountered empty key after stripping whitespace")
        if normalize_keys:
            clean_key = clean_key.upper()
        clean_value = trim_value(value, strip_chars)
        result[clean_key] = clean_value
    return result


def collapse_whitespace(value: str) -> str:
    """Replace runs of internal whitespace with a single space and strip ends."""
    if not isinstance(value, str):
        raise TrimError(f"Expected str, got {type(value).__name__}")
    import re
    return re.sub(r"\s+", " ", value).strip()


def trim_env_values_collapsed(env: dict[str, str]) -> dict[str, str]:
    """Return a new dict where every value has internal whitespace collapsed."""
    return {k: collapse_whitespace(v) for k, v in env.items()}
