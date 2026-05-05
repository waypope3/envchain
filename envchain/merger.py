"""Merge strategies for combining environment variable layers."""

from typing import Any, Dict, Callable


class MergeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def merge_replace(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Later values completely replace earlier ones (default behavior)."""
    result = dict(base)
    result.update(override)
    return result


def merge_keep_existing(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Only add keys not already present in base (base takes priority)."""
    result = dict(base)
    for key, value in override.items():
        if key not in result:
            result[key] = value
    return result


def merge_additive(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Concatenate string values with a separator; non-strings use replace."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], str) and isinstance(value, str):
            result[key] = result[key] + ":" + value
        else:
            result[key] = value
    return result


def merge_strict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Raise MergeError if override tries to redefine an existing key."""
    result = dict(base)
    for key, value in override.items():
        if key in result:
            raise MergeError(
                f"Key '{key}' already defined in base layer and strict merge is active."
            )
        result[key] = value
    return result


STRATEGIES: Dict[str, Callable] = {
    "replace": merge_replace,
    "keep_existing": merge_keep_existing,
    "additive": merge_additive,
    "strict": merge_strict,
}


def get_strategy(name: str) -> Callable:
    """Retrieve a merge strategy function by name."""
    if name not in STRATEGIES:
        raise MergeError(
            f"Unknown merge strategy '{name}'. Available: {list(STRATEGIES.keys())}"
        )
    return STRATEGIES[name]


def apply_merge(
    layers: list,
    strategy: str = "replace",
) -> Dict[str, Any]:
    """Apply a named merge strategy across a list of dicts."""
    fn = get_strategy(strategy)
    result: Dict[str, Any] = {}
    for layer in layers:
        result = fn(result, layer)
    return result
