"""Schedule periodic env refresh tasks tied to an EnvWatcher."""

import threading
from typing import Callable, Dict, Optional
from envchain.watcher import EnvWatcher, WatcherError


class SchedulerError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class EnvRefreshScheduler:
    """Run an EnvWatcher in a background thread, refreshing on a set interval."""

    def __init__(self, watcher: EnvWatcher, on_error: Optional[Callable[[Exception], None]] = None):
        if not isinstance(watcher, EnvWatcher):
            raise SchedulerError("watcher must be an EnvWatcher instance")
        self._watcher = watcher
        self._on_error = on_error
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._check_count = 0

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    @property
    def check_count(self) -> int:
        return self._check_count

    def start(self) -> None:
        """Start background polling thread."""
        if self.is_running:
            raise SchedulerError("scheduler is already running")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        """Signal the background thread to stop and wait for it."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def _run(self) -> None:
        import time
        while not self._stop_event.is_set():
            try:
                self._watcher.check_once()
                self._check_count += 1
            except Exception as exc:
                if self._on_error:
                    self._on_error(exc)
            self._stop_event.wait(timeout=self._watcher._interval)

    def reset_count(self) -> None:
        """Reset the internal check counter."""
        self._check_count = 0
