"""Patch (partially update) an env dict with a set of changes, supporting add, update, and delete operations."""

from typing import Any, Dict, Optional


class PatchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


DELETE_SENTINEL = object()


def patch_env(
    base: Dict[str, Any],
    patch: Dict[str, Any],
    delete_marker: Optional[str] = None,
) -> Dict[str, Any]:
    """Apply a patch dict to a base env dict.

    Keys in patch override keys in base.
    If delete_marker is set, any patch value equal to delete_marker causes
    the key to be removed from the result.

    Args:
        base: The original env dict.
        patch: Changes to apply.
        delete_marker: Optional string value that signals key deletion.

    Returns:
        A new dict with the patch applied.

    Raises:
        PatchError: If base or patch are not dicts.
    """
    if not isinstance(base, dict):
        raise PatchError("base must be a dict")
    if not isinstance(patch, dict):
        raise PatchError("patch must be a dict")

    result = dict(base)
    for key, value in patch.items():
        if delete_marker is not None and value == delete_marker:
            result.pop(key, None)
        else:
            result[key] = value
    return result


def patch_keys(
    base: Dict[str, Any],
    updates: Dict[str, Any],
    keys: list,
) -> Dict[str, Any]:
    """Apply only specific keys from updates onto base.

    Args:
        base: The original env dict.
        updates: Source of new values.
        keys: List of keys to apply from updates.

    Returns:
        A new dict with only the specified keys patched.

    Raises:
        PatchError: If a requested key is missing from updates.
    """
    if not isinstance(base, dict):
        raise PatchError("base must be a dict")
    if not isinstance(updates, dict):
        raise PatchError("updates must be a dict")

    result = dict(base)
    for key in keys:
        if key not in updates:
            raise PatchError(f"Key '{key}' not found in updates")
        result[key] = updates[key]
    return result
