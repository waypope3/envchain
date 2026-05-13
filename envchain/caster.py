"""Type casting utilities for environment variable values."""

from typing import Any, Dict, Optional, Type


class CastError(Exception):
    def __init__(self, key: str, value: str, target_type: str, reason: str = ""):
        self.key = key
        self.value = value
        self.target_type = target_type
        msg = f"Cannot cast key '{key}' value '{value}' to {target_type}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


def cast_value(key: str, value: str, target_type: Type) -> Any:
    """Cast a single string value to the given Python type."""
    if target_type is str:
        return value
    if target_type is bool:
        lower = value.strip().lower()
        if lower in _BOOL_TRUE:
            return True
        if lower in _BOOL_FALSE:
            return False
        raise CastError(key, value, "bool", "unrecognised boolean literal")
    if target_type is int:
        try:
            return int(value)
        except ValueError:
            raise CastError(key, value, "int")
    if target_type is float:
        try:
            return float(value)
        except ValueError:
            raise CastError(key, value, "float")
    raise CastError(key, value, target_type.__name__, "unsupported target type")


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, Type],
    strict: bool = False,
) -> Dict[str, Any]:
    """Return a new dict with values cast according to *schema*.

    Args:
        env:    Source environment mapping (str -> str).
        schema: Mapping of key -> desired Python type.
        strict: If True, raise CastError for keys in *schema* that are absent
                from *env*.  If False, absent keys are silently skipped.

    Returns:
        A new dict containing all keys from *env*; keys present in *schema*
        are cast to the specified type, all others remain as strings.
    """
    result: Dict[str, Any] = dict(env)
    for key, target_type in schema.items():
        if key not in env:
            if strict:
                raise CastError(key, "", target_type.__name__, "key not found in env")
            continue
        result[key] = cast_value(key, env[key], target_type)
    return result
