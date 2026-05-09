"""Tag and filter environment variables with arbitrary metadata labels."""

from typing import Dict, List, Optional, Set


class TaggerError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def tag_keys(
    env: Dict[str, str],
    keys: List[str],
    tag: str,
    registry: Optional[Dict[str, Set[str]]] = None,
) -> Dict[str, Set[str]]:
    """Associate a tag with a list of keys. Returns updated registry."""
    if not tag or not tag.strip():
        raise TaggerError("Tag must be a non-empty string.")
    if registry is None:
        registry = {}
    for key in keys:
        if key not in env:
            raise TaggerError(f"Key '{key}' not found in env.")
        registry.setdefault(key, set()).add(tag)
    return registry


def get_tags(key: str, registry: Dict[str, Set[str]]) -> Set[str]:
    """Return all tags associated with a given key."""
    return set(registry.get(key, set()))


def filter_by_tag(
    env: Dict[str, str],
    tag: str,
    registry: Dict[str, Set[str]],
) -> Dict[str, str]:
    """Return a subset of env containing only keys tagged with the given tag."""
    return {k: v for k, v in env.items() if tag in registry.get(k, set())}


def remove_tag(
    key: str,
    tag: str,
    registry: Dict[str, Set[str]],
) -> Dict[str, Set[str]]:
    """Remove a specific tag from a key. Returns updated registry."""
    updated = {k: set(v) for k, v in registry.items()}
    if key in updated:
        updated[key].discard(tag)
        if not updated[key]:
            del updated[key]
    return updated


def list_tags(registry: Dict[str, Set[str]]) -> Set[str]:
    """Return all unique tags present across the registry."""
    all_tags: Set[str] = set()
    for tags in registry.values():
        all_tags.update(tags)
    return all_tags
