"""Value transformation utilities for env variable processing."""

from typing import Any, Callable, Dict, Optional


class TransformError(Exception):
    def __init__(self, key: str, reason: str):
        self.key = key
        self.reason = reason
        super().__init__(f"Transform failed for '{key}': {reason}")


def _to_bool(value: str) -> bool:
    if value.lower() in ("true", "1", "yes", "on"):
        return True
    if value.lower() in ("false", "0", "no", "off"):
        return False
    raise ValueError(f"Cannot convert '{value}' to bool")


def _to_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to int")


def _to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to float")


def _to_list(value: str, delimiter: str = ",") -> list:
    return [item.strip() for item in value.split(delimiter) if item.strip()]


BUILTIN_TRANSFORMS: Dict[str, Callable[[str], Any]] = {
    "bool": _to_bool,
    "int": _to_int,
    "float": _to_float,
    "list": _to_list,
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
}


def transform_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    custom: Optional[Dict[str, Callable[[str], Any]]] = None,
) -> Dict[str, Any]:
    """Apply named transforms to specific keys in an env dict.

    Args:
        env: The source environment dict.
        rules: Mapping of key -> transform name.
        custom: Optional additional named transforms.

    Returns:
        A new dict with transformed values; untransformed keys are copied as-is.

    Raises:
        TransformError: If a transform name is unknown or conversion fails.
    """
    available = {**BUILTIN_TRANSFORMS, **(custom or {})}
    result: Dict[str, Any] = dict(env)

    for key, transform_name in rules.items():
        if transform_name not in available:
            raise TransformError(key, f"unknown transform '{transform_name}'")
        if key not in env:
            continue
        try:
            result[key] = available[transform_name](env[key])
        except (ValueError, TypeError) as exc:
            raise TransformError(key, str(exc)) from exc

    return result
