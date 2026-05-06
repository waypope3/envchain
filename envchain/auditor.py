"""Audit log for tracking env variable changes across chain operations."""

from datetime import datetime, timezone
from typing import Any


class AuditEntry:
    def __init__(self, operation: str, key: str, old_value: Any = None, new_value: Any = None, source: str = ""):
        self.operation = operation
        self.key = key
        self.old_value = old_value
        self.new_value = new_value
        self.source = source
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "source": self.source,
        }

    def __repr__(self) -> str:
        return f"AuditEntry(op={self.operation!r}, key={self.key!r}, source={self.source!r})"


class EnvAuditor:
    def __init__(self):
        self._log: list[AuditEntry] = []

    def record(self, operation: str, key: str, old_value: Any = None, new_value: Any = None, source: str = "") -> None:
        entry = AuditEntry(operation, key, old_value=old_value, new_value=new_value, source=source)
        self._log.append(entry)

    def record_layer(self, base: dict, overlay: dict, source: str = "") -> None:
        """Record all changes introduced by applying overlay on top of base."""
        for key, new_val in overlay.items():
            if key not in base:
                self.record("add", key, old_value=None, new_value=new_val, source=source)
            elif base[key] != new_val:
                self.record("override", key, old_value=base[key], new_value=new_val, source=source)
            else:
                self.record("unchanged", key, old_value=new_val, new_value=new_val, source=source)

    def get_log(self) -> list[dict]:
        return [entry.to_dict() for entry in self._log]

    def filter_by_operation(self, operation: str) -> list[dict]:
        return [e.to_dict() for e in self._log if e.operation == operation]

    def filter_by_key(self, key: str) -> list[dict]:
        return [e.to_dict() for e in self._log if e.key == key]

    def clear(self) -> None:
        self._log.clear()

    def __len__(self) -> int:
        return len(self._log)
