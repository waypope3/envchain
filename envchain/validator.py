"""Validation utilities for EnvChain resolved environments."""

from typing import Any, Dict, List, Optional


class ValidationError(Exception):
    """Raised when environment validation fails."""

    def __init__(self, missing: List[str], invalid: Dict[str, str]):
        self.missing = missing
        self.invalid = invalid
        parts = []
        if missing:
            parts.append(f"Missing required keys: {', '.join(missing)}")
        if invalid:
            details = "; ".join(f"{k}: {v}" for k, v in invalid.items())
            parts.append(f"Invalid values: {details}")
        super().__init__(" | ".join(parts))


def validate(
    env: Dict[str, Any],
    required: Optional[List[str]] = None,
    types: Optional[Dict[str, type]] = None,
    non_empty: bool = False,
) -> None:
    """Validate a resolved environment dictionary.

    Args:
        env: The resolved environment dict to validate.
        required: List of keys that must be present.
        types: Dict mapping key names to expected Python types.
        non_empty: If True, all present string values must be non-empty.

    Raises:
        ValidationError: If any validation checks fail.
    """
    missing: List[str] = []
    invalid: Dict[str, str] = {}

    if required:
        for key in required:
            if key not in env:
                missing.append(key)

    if types:
        for key, expected_type in types.items():
            if key in env and not isinstance(env[key], expected_type):
                actual = type(env[key]).__name__
                invalid[key] = f"expected {expected_type.__name__}, got {actual}"

    if non_empty:
        for key, value in env.items():
            if isinstance(value, str) and value.strip() == "":
                invalid[key] = "value must not be empty or whitespace"

    if missing or invalid:
        raise ValidationError(missing=missing, invalid=invalid)


def assert_keys_present(env: Dict[str, Any], keys: List[str]) -> List[str]:
    """Return a list of keys from `keys` that are absent in `env`."""
    return [k for k in keys if k not in env]
