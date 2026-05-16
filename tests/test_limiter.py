"""Tests for envchain.limiter."""

import pytest

from envchain.limiter import (
    LimitError,
    limit_env,
    limit_keys,
    limit_value_length,
)


# ---------------------------------------------------------------------------
# limit_keys
# ---------------------------------------------------------------------------

class TestLimitKeys:
    _env = {"A": "1", "B": "2", "C": "3", "D": "4"}

    def test_first_strategy_default(self):
        result = limit_keys(self._env, 2)
        assert list(result.keys()) == ["A", "B"]

    def test_last_strategy(self):
        result = limit_keys(self._env, 2, strategy="last")
        assert list(result.keys()) == ["C", "D"]

    def test_alpha_strategy(self):
        env = {"ZEBRA": "z", "APPLE": "a", "MANGO": "m"}
        result = limit_keys(env, 2, strategy="alpha")
        assert list(result.keys()) == ["APPLE", "MANGO"]

    def test_max_keys_zero_returns_empty(self):
        result = limit_keys(self._env, 0)
        assert result == {}

    def test_max_keys_exceeds_length_returns_all(self):
        result = limit_keys(self._env, 100)
        assert result == self._env

    def test_negative_max_keys_raises(self):
        with pytest.raises(LimitError, match="max_keys must be >= 0"):
            limit_keys(self._env, -1)

    def test_unknown_strategy_raises(self):
        with pytest.raises(LimitError, match="Unknown strategy"):
            limit_keys(self._env, 2, strategy="random")

    def test_does_not_mutate_input(self):
        original = dict(self._env)
        limit_keys(self._env, 2)
        assert self._env == original

    def test_empty_env_returns_empty(self):
        assert limit_keys({}, 5) == {}


# ---------------------------------------------------------------------------
# limit_value_length
# ---------------------------------------------------------------------------

class TestLimitValueLength:
    def test_values_within_limit_unchanged(self):
        env = {"KEY": "hello"}
        assert limit_value_length(env, 10) == {"KEY": "hello"}

    def test_exceeding_value_raises_by_default(self):
        env = {"KEY": "toolongvalue"}
        with pytest.raises(LimitError, match="exceeds max_length"):
            limit_value_length(env, 5)

    def test_truncate_shortens_value(self):
        env = {"KEY": "toolongvalue"}
        result = limit_value_length(env, 7, truncate=True, placeholder="...")
        assert result["KEY"] == "tool..."
        assert len(result["KEY"]) == 7

    def test_truncate_placeholder_fits_within_max(self):
        result = limit_value_length({"K": "abcdef"}, 4, truncate=True, placeholder="--")
        assert result["K"] == "ab--"

    def test_max_length_zero_truncate(self):
        result = limit_value_length({"K": "abc"}, 0, truncate=True, placeholder="")
        assert result["K"] == ""

    def test_negative_max_length_raises(self):
        with pytest.raises(LimitError, match="max_length must be >= 0"):
            limit_value_length({"K": "v"}, -1)

    def test_empty_env_returns_empty(self):
        assert limit_value_length({}, 5) == {}

    def test_does_not_mutate_input(self):
        env = {"K": "short"}
        limit_value_length(env, 10)
        assert env == {"K": "short"}


# ---------------------------------------------------------------------------
# limit_env (combined)
# ---------------------------------------------------------------------------

class TestLimitEnv:
    def test_both_limits_applied(self):
        env = {"A": "hello", "B": "world", "C": "extra"}
        result = limit_env(env, max_keys=2, max_value_length=3, truncate_values=True)
        assert list(result.keys()) == ["A", "B"]
        for v in result.values():
            assert len(v) <= 3

    def test_only_key_limit(self):
        env = {"X": "1", "Y": "2", "Z": "3"}
        result = limit_env(env, max_keys=2)
        assert len(result) == 2

    def test_only_value_limit(self):
        env = {"X": "short", "Y": "verylongvalue"}
        with pytest.raises(LimitError):
            limit_env(env, max_value_length=5)

    def test_no_limits_returns_copy(self):
        env = {"A": "1", "B": "2"}
        result = limit_env(env)
        assert result == env
        assert result is not env

    def test_key_strategy_forwarded(self):
        env = {"Z": "1", "A": "2", "M": "3"}
        result = limit_env(env, max_keys=1, key_strategy="alpha")
        assert list(result.keys()) == ["A"]
