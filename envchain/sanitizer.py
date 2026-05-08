"""Sanitize environment variable keys and values."""

import re


class SanitizeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


_VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def sanitize_key(key: str, *, replace_invalid: bool = False, replacement: str = '_') -> str:
    """Return a sanitized env var key.

    If *replace_invalid* is True, characters that are not alphanumeric or
    underscores are replaced with *replacement* and a leading digit is
    prefixed with '_'.  Otherwise a SanitizeError is raised.
    """
    if not isinstance(key, str):
        raise SanitizeError(f"Key must be a string, got {type(key).__name__}")
    if replace_invalid:
        sanitized = re.sub(r'[^A-Za-z0-9_]', replacement, key)
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized
        if not sanitized:
            raise SanitizeError("Key is empty after sanitization")
        return sanitized
    if not _VALID_KEY_RE.match(key):
        raise SanitizeError(
            f"Invalid env var key {key!r}: must start with a letter or underscore "
            "and contain only alphanumeric characters or underscores"
        )
    return key


def sanitize_value(value: str, *, strip_null_bytes: bool = True) -> str:
    """Return a sanitized env var value.

    Raises SanitizeError if *value* is not a string.  Null bytes are stripped
    by default because they are not valid in POSIX environment variables.
    """
    if not isinstance(value, str):
        raise SanitizeError(f"Value must be a string, got {type(value).__name__}")
    if strip_null_bytes:
        value = value.replace('\x00', '')
    return value


def sanitize_env(
    env: dict,
    *,
    replace_invalid_keys: bool = False,
    replacement: str = '_',
    strip_null_bytes: bool = True,
) -> dict:
    """Return a new dict with all keys and values sanitized.

    Duplicate keys produced by key sanitization raise SanitizeError.
    """
    result: dict = {}
    for key, value in env.items():
        clean_key = sanitize_key(key, replace_invalid=replace_invalid_keys, replacement=replacement)
        clean_value = sanitize_value(value, strip_null_bytes=strip_null_bytes)
        if clean_key in result:
            raise SanitizeError(
                f"Duplicate key {clean_key!r} produced during sanitization"
            )
        result[clean_key] = clean_value
    return result
