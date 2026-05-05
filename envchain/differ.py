"""Diff utilities for comparing two resolved env layers or chains."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class EnvDiff:
    """Represents the diff between two environment snapshots."""
    added: Dict[str, Any] = field(default_factory=dict)
    removed: Dict[str, Any] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = []
        for k, v in sorted(self.added.items()):
            lines.append(f"+ {k}={v!r}")
        for k, v in sorted(self.removed.items()):
            lines.append(f"- {k}={v!r}")
        for k, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {k}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "(no changes)"


def diff_envs(
    before: Dict[str, Any],
    after: Dict[str, Any],
    ignore_keys: Optional[List[str]] = None,
) -> EnvDiff:
    """Compute the diff between two env dicts.

    Args:
        before: The original environment mapping.
        after: The new environment mapping.
        ignore_keys: Optional list of keys to exclude from comparison.

    Returns:
        An EnvDiff instance describing additions, removals, and changes.
    """
    ignore = set(ignore_keys or [])
    before_filtered = {k: v for k, v in before.items() if k not in ignore}
    after_filtered = {k: v for k, v in after.items() if k not in ignore}

    before_keys = set(before_filtered)
    after_keys = set(after_filtered)

    added = {k: after_filtered[k] for k in after_keys - before_keys}
    removed = {k: before_filtered[k] for k in before_keys - after_keys}
    changed = {}
    unchanged = {}

    for k in before_keys & after_keys:
        if before_filtered[k] != after_filtered[k]:
            changed[k] = (before_filtered[k], after_filtered[k])
        else:
            unchanged[k] = before_filtered[k]

    return EnvDiff(added=added, removed=removed, changed=changed, unchanged=unchanged)
