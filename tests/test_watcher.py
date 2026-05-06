"""Tests for envchain.watcher."""

import pytest
from unittest.mock import MagicMock
from envchain.watcher import EnvWatcher, WatcherError, _hash_env


class TestHashEnv:
    def test_same_dict_same_hash(self):
        env = {"A": "1", "B": "2"}
        assert _hash_env(env) == _hash_env(env)

    def test_different_dict_different_hash(self):
        assert _hash_env({"A": "1"}) != _hash_env({"A": "2"})

    def test_order_independent(self):
        e1 = {"A": "1", "B": "2"}
        e2 = {"B": "2", "A": "1"}
        assert _hash_env(e1) == _hash_env(e2)

    def test_empty_dict(self):
        assert isinstance(_hash_env({}), str)
        assert len(_hash_env({})) == 64


class TestEnvWatcherInit:
    def test_non_callable_source_raises(self):
        with pytest.raises(WatcherError):
            EnvWatcher(source="not_callable")

    def test_non_positive_interval_raises(self):
        with pytest.raises(WatcherError):
            EnvWatcher(source=lambda: {}, interval=0)

    def test_negative_interval_raises(self):
        with pytest.raises(WatcherError):
            EnvWatcher(source=lambda: {}, interval=-1.0)

    def test_valid_init(self):
        w = EnvWatcher(source=lambda: {"X": "1"}, interval=1.0)
        assert w._interval == 1.0


class TestCheckOnce:
    def test_first_check_returns_false(self):
        w = EnvWatcher(source=lambda: {"A": "1"})
        assert w.check_once() is False

    def test_no_change_returns_false(self):
        w = EnvWatcher(source=lambda: {"A": "1"})
        w.check_once()
        assert w.check_once() is False

    def test_change_detected_returns_true(self):
        state = [{"A": "1"}]
        w = EnvWatcher(source=lambda: state[0])
        w.check_once()
        state[0] = {"A": "2"}
        assert w.check_once() is True

    def test_callback_invoked_on_change(self):
        state = [{"A": "1"}]
        w = EnvWatcher(source=lambda: state[0])
        cb = MagicMock()
        w.on_change(cb)
        w.check_once()
        state[0] = {"A": "2"}
        w.check_once()
        cb.assert_called_once()
        old, new = cb.call_args[0]
        assert old == {"A": "1"}
        assert new == {"A": "2"}

    def test_callback_not_invoked_without_change(self):
        w = EnvWatcher(source=lambda: {"A": "1"})
        cb = MagicMock()
        w.on_change(cb)
        w.check_once()
        w.check_once()
        cb.assert_not_called()

    def test_multiple_callbacks_all_invoked(self):
        state = [{"A": "1"}]
        w = EnvWatcher(source=lambda: state[0])
        cb1, cb2 = MagicMock(), MagicMock()
        w.on_change(cb1)
        w.on_change(cb2)
        w.check_once()
        state[0] = {"A": "9"}
        w.check_once()
        cb1.assert_called_once()
        cb2.assert_called_once()


class TestOnChange:
    def test_non_callable_raises(self):
        w = EnvWatcher(source=lambda: {})
        with pytest.raises(WatcherError):
            w.on_change("not_a_function")


class TestReset:
    def test_reset_clears_state(self):
        state = [{"A": "1"}]
        w = EnvWatcher(source=lambda: state[0])
        w.check_once()
        w.reset()
        # After reset first check should return False again
        assert w.check_once() is False

    def test_change_detected_after_reset(self):
        state = [{"A": "1"}]
        w = EnvWatcher(source=lambda: state[0])
        w.check_once()
        state[0] = {"A": "2"}
        w.reset()
        w.check_once()  # seeds with new state
        state[0] = {"A": "3"}
        assert w.check_once() is True


class TestWatch:
    def test_watch_max_checks(self):
        call_count = [0]

        def source():
            call_count[0] += 1
            return {"tick": str(call_count[0])}

        w = EnvWatcher(source=source, interval=0.001)
        w.watch(max_checks=3)
        assert call_count[0] == 3
