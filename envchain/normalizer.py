"""Key and value normalization utilities for envchain."""

from typing import Dict, Optional


class NormalizeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def normalize_key(key: str, case: str = "upper") -> str:
    """Normalize a single key by case and stripping whitespace.

    Args:
        key: The environment variable key to normalize.
        case: 'upper', 'lower', or 'preserve'.

    Returns:
        Normalized key string.

    Raises:
        NormalizeError: If an unsupported case option is provided.
    """
    if not isinstance(key, str):
        raise NormalizeError(f"Key must be a string, got {type(key).__name__}")
    key = key.strip()
    if case == "upper":
        return key.upper()
    elif case == "lower":
        return key.lower()
    elif case == "preserve":
        return key
    else:
        raise NormalizeError(f"Unsupported case option: {case!r}. Use 'upper', 'lower', or 'preserve'.")


def normalize_value(value: str, strip: bool = True, collapse_whitespace: bool = False) -> str:
    """Normalize a single environment variable value.

    Args:
        value: The value to normalize.
        strip: Whether to strip leading/trailing whitespace.
        collapse_whitespace: Whether to collapse internal whitespace to single spaces.

    Returns:
        Normalized value string.
    """
    if not isinstance(value, str):
        raise NormalizeError(f"Value must be a string, got {type(value).__name__}")
    if strip:
        value = value.strip()
    if collapse_whitespace:
        import re
        value = re.sub(r"\s+", " ", value)
    return value


def normalize_env(
    env: Dict[str, str],
    case: str = "upper",
    strip_values: bool = True,
    collapse_whitespace: bool = False,
) -> Dict[str, str]:
    """Normalize all keys and values in an env dict.

    Args:
        env: Input environment dictionary.
        case: Key case normalization ('upper', 'lower', 'preserve').
        strip_values: Strip whitespace from values.
        collapse_whitespace: Collapse internal whitespace in values.

    Returns:
        New normalized dictionary.

    Raises:
        NormalizeError: On duplicate keys after normalization.
    """
    result: Dict[str, str] = {}
    for k, v in env.items():
        norm_key = normalize_key(k, case=case)
        norm_val = normalize_value(v, strip=strip_values, collapse_whitespace=collapse_whitespace)
        if norm_key in result:
            raise NormalizeError(
                f"Duplicate key after normalization: {norm_key!r} (from {k!r})"
            )
        result[norm_key] = norm_val
    return result
