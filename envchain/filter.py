"""envchain.filter — Filter env variables by value predicates."""

from typing import Any, Callable, Dict, List, Optional


class FilterError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


def filter_by_predicate(
    env: Dict[str, Any],
    predicate: Callable[[str, Any], bool],
) -> Dict[str, Any]:
    """Return a new dict containing only entries where predicate(key, value) is True."""
    if not callable(predicate):
        raise FilterError("predicate must be callable")
    return {k: v for k, v in env.items() if predicate(k, v)}


def filter_by_value(
    env: Dict[str, Any],
    allowed_values: List[Any],
) -> Dict[str, Any]:
    """Return entries whose value is in allowed_values."""
    if not isinstance(allowed_values, list):
        raise FilterError("allowed_values must be a list")
    return {k: v for k, v in env.items() if v in allowed_values}


def filter_non_empty(env: Dict[str, Any]) -> Dict[str, Any]:
    """Return entries where the value is a non-empty string (or non-None)."""
    return {k: v for k, v in env.items() if v not in (None, "")}


def filter_by_type(
    env: Dict[str, Any],
    expected_type: type,
) -> Dict[str, Any]:
    """Return only entries whose value is an instance of expected_type."""
    if not isinstance(expected_type, type):
        raise FilterError("expected_type must be a type")
    return {k: v for k, v in env.items() if isinstance(v, expected_type)}


def reject_by_predicate(
    env: Dict[str, Any],
    predicate: Callable[[str, Any], bool],
) -> Dict[str, Any]:
    """Inverse of filter_by_predicate — remove entries where predicate is True."""
    if not callable(predicate):
        raise FilterError("predicate must be callable")
    return {k: v for k, v in env.items() if not predicate(k, v)}
