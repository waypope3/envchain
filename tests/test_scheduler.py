"""Tests for envchain.scheduler."""

import time
import pytest
from unittest.mock import MagicMock
from envchain.watcher import EnvWatcher
from envchain.scheduler import EnvRefreshScheduler, SchedulerError


def _make_watcher(env=None):
    env = env or {"KEY": "value"}
    return EnvWatcher(source=lambda: env, interval=0.05)


class TestSchedulerInit:
    def test_invalid_watcher_raises(self):
        with pytest.raises(SchedulerError):
            EnvRefreshScheduler(watcher="bad")

    def test_valid_init(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        assert not s.is_running

    def test_check_count_starts_at_zero(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        assert s.check_count == 0


class TestSchedulerStartStop:
    def test_is_running_after_start(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        s.start()
        assert s.is_running
        s.stop()

    def test_not_running_after_stop(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        s.start()
        s.stop(timeout=2.0)
        assert not s.is_running

    def test_double_start_raises(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        s.start()
        with pytest.raises(SchedulerError):
            s.start()
        s.stop()

    def test_checks_accumulate(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        s.start()
        time.sleep(0.2)
        s.stop(timeout=2.0)
        assert s.check_count >= 1


class TestSchedulerErrorHandler:
    def test_on_error_called_when_source_raises(self):
        errors = []

        def bad_source():
            raise RuntimeError("boom")

        watcher = EnvWatcher(source=bad_source, interval=0.05)
        s = EnvRefreshScheduler(watcher=watcher, on_error=errors.append)
        s.start()
        time.sleep(0.2)
        s.stop(timeout=2.0)
        assert len(errors) >= 1
        assert isinstance(errors[0], RuntimeError)

    def test_no_error_handler_does_not_crash(self):
        def bad_source():
            raise ValueError("oops")

        watcher = EnvWatcher(source=bad_source, interval=0.05)
        s = EnvRefreshScheduler(watcher=watcher)
        s.start()
        time.sleep(0.15)
        s.stop(timeout=2.0)
        assert not s.is_running


class TestResetCount:
    def test_reset_sets_count_to_zero(self):
        s = EnvRefreshScheduler(watcher=_make_watcher())
        s.start()
        time.sleep(0.2)
        s.stop(timeout=2.0)
        assert s.check_count >= 1
        s.reset_count()
        assert s.check_count == 0

    def test_callback_triggered_via_scheduler(self):
        state = [{"X": "1"}]
        changes = []
        watcher = EnvWatcher(source=lambda: state[0], interval=0.05)
        watcher.on_change(lambda old, new: changes.append((old, new)))
        s = EnvRefreshScheduler(watcher=watcher)
        s.start()
        time.sleep(0.08)
        state[0] = {"X": "2"}
        time.sleep(0.15)
        s.stop(timeout=2.0)
        assert len(changes) >= 1
        assert changes[0][1] == {"X": "2"}
