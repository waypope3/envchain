"""Masking utilities for sensitive environment variable values."""

import re
from typing import Dict, Iterable, Optional


SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|pwd)", re.IGNORECASE),
    re.compile(r"(secret|token|api_key|apikey)", re.IGNORECASE),
    re.compile(r"(private_key|privatekey|auth)", re.IGNORECASE),
    re.compile(r"(credential|cred)", re.IGNORECASE),
]

DEFAULT_MASK = "***"


def is_sensitive_key(key: str, extra_patterns: Optional[Iterable[str]] = None) -> bool:
    """Return True if the key name looks like it holds sensitive data."""
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(key):
            return True
    if extra_patterns:
        for raw in extra_patterns:
            if re.search(raw, key, re.IGNORECASE):
                return True
    return False


def mask_value(value: str, mask: str = DEFAULT_MASK, reveal_chars: int = 0) -> str:
    """Return a masked version of *value*, optionally revealing trailing characters."""
    if not value:
        return mask
    if reveal_chars > 0 and len(value) > reveal_chars:
        return mask + value[-reveal_chars:]
    return mask


def mask_env(
    env: Dict[str, str],
    *,
    extra_patterns: Optional[Iterable[str]] = None,
    mask: str = DEFAULT_MASK,
    reveal_chars: int = 0,
    explicit_keys: Optional[Iterable[str]] = None,
) -> Dict[str, str]:
    """Return a copy of *env* with sensitive values replaced by *mask*.

    Args:
        env: The source environment dictionary.
        extra_patterns: Additional regex patterns to flag as sensitive.
        mask: The replacement string for masked values.
        reveal_chars: Number of trailing characters to keep visible.
        explicit_keys: Keys that should always be masked regardless of name.
    """
    forced = set(explicit_keys or [])
    result: Dict[str, str] = {}
    for key, value in env.items():
        if key in forced or is_sensitive_key(key, extra_patterns):
            result[key] = mask_value(value, mask=mask, reveal_chars=reveal_chars)
        else:
            result[key] = value
    return result
