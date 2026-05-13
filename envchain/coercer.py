"""Type coercion for env var values with configurable rules and fallbacks."""

from typing import Any, Callable, Dict, Optional


class CoerceError(Exception):
    def __init__(self, key: str, value: str, target_type: str, reason: str = ""):
        self.key = key
        self.value = value
        self.target_type = target_type
        msg = f"Cannot coerce '{key}={value}' to {target_type}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


_BOOL_TRUE = {"1", "true", "yes", "on", "enabled"}
_BOOL_FALSE = {"0", "false", "no", "off", "disabled"}


def coerce_value(key: str, value: str, target_type: str, fallback: Any = None) -> Any:
    """Coerce a single string value to the given target type.

    Supported types: 'str', 'int', 'float', 'bool', 'list'.
    If fallback is not None, returns it on failure instead of raising.
    """
    try:
        if target_type == "str":
            return value
        if target_type == "int":
            return int(value)
        if target_type == "float":
            return float(value)
        if target_type == "bool":
            lower = value.strip().lower()
            if lower in _BOOL_TRUE:
                return True
            if lower in _BOOL_FALSE:
                return False
            raise CoerceError(key, value, "bool", "unrecognised boolean literal")
        if target_type == "list":
            return [item.strip() for item in value.split(",") if item.strip()]
        raise CoerceError(key, value, target_type, "unknown target type")
    except CoerceError:
        if fallback is not None:
            return fallback
        raise
    except (ValueError, TypeError) as exc:
        if fallback is not None:
            return fallback
        raise CoerceError(key, value, target_type, str(exc)) from exc


def coerce_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    fallbacks: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply coercion rules to an env dict.

    Args:
        env: Source environment mapping (string values).
        rules: Mapping of key -> target_type.
        fallbacks: Optional per-key fallback values on failure.

    Returns:
        New dict with coerced values; keys not in rules remain as strings.
    """
    fallbacks = fallbacks or {}
    result: Dict[str, Any] = dict(env)
    for key, target_type in rules.items():
        if key not in env:
            continue
        result[key] = coerce_value(
            key, env[key], target_type, fallback=fallbacks.get(key)
        )
    return result
