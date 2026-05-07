"""EnvComparator — compare two env dicts and produce structured reports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class CompareError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass
class CompareResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)
    unchanged: Dict[str, str] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts: List[str] = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        if self.unchanged:
            parts.append(f"={len(self.unchanged)} unchanged")
        return ", ".join(parts) if parts else "no changes"

    def to_dict(self) -> dict:
        return {
            "added": dict(self.added),
            "removed": dict(self.removed),
            "changed": {k: {"before": v[0], "after": v[1]} for k, v in self.changed.items()},
            "unchanged": dict(self.unchanged),
        }


def compare_envs(
    before: Dict[str, str],
    after: Dict[str, str],
    keys: Optional[List[str]] = None,
) -> CompareResult:
    """Compare two env dicts and return a CompareResult.

    If *keys* is provided, only those keys are considered.
    """
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise CompareError("Both 'before' and 'after' must be dicts.")

    scope = set(keys) if keys is not None else set(before) | set(after)

    result = CompareResult()
    for key in scope:
        in_before = key in before
        in_after = key in after
        if in_before and in_after:
            if before[key] == after[key]:
                result.unchanged[key] = after[key]
            else:
                result.changed[key] = (before[key], after[key])
        elif in_after:
            result.added[key] = after[key]
        elif in_before:
            result.removed[key] = before[key]

    return result
