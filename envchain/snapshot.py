"""Snapshot module for capturing and restoring env chain states."""

import json
import copy
from datetime import datetime, timezone
from typing import Optional


class SnapshotError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def create_snapshot(env: dict, label: Optional[str] = None) -> dict:
    """Create a snapshot of the given env dict with metadata."""
    return {
        "label": label or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": copy.deepcopy(env),
    }


def restore_snapshot(snapshot: dict) -> dict:
    """Return a deep copy of the env data from a snapshot."""
    if "data" not in snapshot:
        raise SnapshotError("Invalid snapshot: missing 'data' key.")
    return copy.deepcopy(snapshot["data"])


def save_snapshot_to_file(snapshot: dict, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)


def load_snapshot_from_file(path: str) -> dict:
    """Load a snapshot from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Failed to load snapshot from '{path}': {exc}") from exc
    if "data" not in snapshot:
        raise SnapshotError(f"Snapshot file '{path}' is missing 'data' key.")
    return snapshot


def diff_with_snapshot(current: dict, snapshot: dict) -> dict:
    """Return a dict describing changes between a snapshot and current env."""
    previous = snapshot.get("data", {})
    added = {k: current[k] for k in current if k not in previous}
    removed = {k: previous[k] for k in previous if k not in current}
    changed = {
        k: {"before": previous[k], "after": current[k]}
        for k in current
        if k in previous and current[k] != previous[k]
    }
    return {"added": added, "removed": removed, "changed": changed}
