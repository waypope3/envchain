"""Group environment variables by prefix or custom mapping."""

from typing import Dict, List, Optional, Callable


class GroupError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def group_by_prefix(
    env: Dict[str, str],
    separator: str = "_",
    lowercase_groups: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Group keys by their first segment before the separator.

    Keys with no separator are placed under the empty-string group.
    """
    if not isinstance(separator, str) or len(separator) == 0:
        raise GroupError("separator must be a non-empty string")

    groups: Dict[str, Dict[str, str]] = {}
    for key, value in env.items():
        if separator in key:
            group, remainder = key.split(separator, 1)
        else:
            group, remainder = "", key

        if lowercase_groups:
            group = group.lower()

        groups.setdefault(group, {})[remainder] = value

    return groups


def group_by_mapping(
    env: Dict[str, str],
    mapping: Dict[str, List[str]],
    include_unmatched: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Group keys according to an explicit group -> [keys] mapping.

    If *include_unmatched* is True, unmatched keys appear under '__other__'.
    """
    groups: Dict[str, Dict[str, str]] = {key: {} for key in mapping}
    unmatched: Dict[str, str] = {}

    assigned = set()
    for group, keys in mapping.items():
        for k in keys:
            if k in env:
                groups[group][k] = env[k]
                assigned.add(k)

    if include_unmatched:
        for k, v in env.items():
            if k not in assigned:
                unmatched[k] = v
        if unmatched:
            groups["__other__"] = unmatched

    return groups


def group_by_predicate(
    env: Dict[str, str],
    predicates: Dict[str, Callable[[str, str], bool]],
    include_unmatched: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Group keys by applying callable predicates (group_name -> predicate)."""
    groups: Dict[str, Dict[str, str]] = {name: {} for name in predicates}
    unmatched: Dict[str, str] = {}

    for k, v in env.items():
        matched = False
        for group, pred in predicates.items():
            if pred(k, v):
                groups[group][k] = v
                matched = True
                break
        if not matched and include_unmatched:
            unmatched[k] = v

    if include_unmatched and unmatched:
        groups["__other__"] = unmatched

    return groups
