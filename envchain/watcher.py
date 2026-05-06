"""Watch env sources for changes and notify on drift."""

import time
import hashlib
import json
from typing import Callable, Dict, Optional


class WatcherError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _hash_env(env: Dict[str, str]) -> str:
    """Return a stable hash of the env dict contents."""
    serialized = json.dumps(env, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


class EnvWatcher:
    """Poll an env source and invoke a callback when the resolved env changes."""

    def __init__(self, source: Callable[[], Dict[str, str]], interval: float = 5.0):
        if not callable(source):
            raise WatcherError("source must be callable")
        if interval <= 0:
            raise WatcherError("interval must be positive")
        self._source = source
        self._interval = interval
        self._last_hash: Optional[str] = None
        self._callbacks: list = []

    def on_change(self, callback: Callable[[Dict[str, str], Dict[str, str]], None]) -> None:
        """Register a callback invoked with (old_env, new_env) on change."""
        if not callable(callback):
            raise WatcherError("callback must be callable")
        self._callbacks.append(callback)

    def check_once(self) -> bool:
        """Check source once. Returns True if a change was detected."""
        current_env = self._source()
        current_hash = _hash_env(current_env)
        if self._last_hash is None:
            self._last_hash = current_hash
            self._last_env = current_env
            return False
        if current_hash != self._last_hash:
            old_env = self._last_env
            self._last_hash = current_hash
            self._last_env = current_env
            for cb in self._callbacks:
                cb(old_env, current_env)
            return True
        return False

    def watch(self, max_checks: Optional[int] = None) -> None:
        """Block and poll until max_checks reached (or forever if None)."""
        checks = 0
        while max_checks is None or checks < max_checks:
            self.check_once()
            checks += 1
            if max_checks is None or checks < max_checks:
                time.sleep(self._interval)

    def reset(self) -> None:
        """Reset internal state so next check_once treats env as fresh."""
        self._last_hash = None
        self._last_env = {}
