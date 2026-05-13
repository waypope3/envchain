"""Tests for envchain.filter."""

import pytest
from envchain.filter import (
    FilterError,
    filter_by_predicate,
    filter_by_value,
    filter_non_empty,
    filter_by_type,
    reject_by_predicate,
)


class TestFilterByPredicate:
    def test_keeps_matching_entries(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = filter_by_predicate(env, lambda k, v: v == "2")
        assert result == {"B": "2"}

    def test_empty_env_returns_empty(self):
        assert filter_by_predicate({}, lambda k, v: True) == {}

    def test_no_match_returns_empty(self):
        env = {"X": "hello"}
        result = filter_by_predicate(env, lambda k, v: k == "MISSING")
        assert result == {}

    def test_non_callable_raises(self):
        with pytest.raises(FilterError, match="callable"):
            filter_by_predicate({"A": "1"}, "not_a_function")

    def test_does_not_mutate_input(self):
        env = {"A": "1", "B": "2"}
        original = dict(env)
        filter_by_predicate(env, lambda k, v: k == "A")
        assert env == original

    def test_key_based_predicate(self):
        env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
        result = filter_by_predicate(env, lambda k, v: k.startswith("DB_"))
        assert set(result.keys()) == {"DB_HOST", "DB_PORT"}


class TestFilterByValue:
    def test_keeps_allowed_values(self):
        env = {"A": "yes", "B": "no", "C": "yes"}
        result = filter_by_value(env, ["yes"])
        assert result == {"A": "yes", "C": "yes"}

    def test_empty_allowed_returns_empty(self):
        env = {"A": "1"}
        assert filter_by_value(env, []) == {}

    def test_non_list_raises(self):
        with pytest.raises(FilterError, match="list"):
            filter_by_value({"A": "1"}, "yes")

    def test_multiple_allowed_values(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = filter_by_value(env, ["1", "3"])
        assert set(result.keys()) == {"A", "C"}


class TestFilterNonEmpty:
    def test_removes_empty_string(self):
        env = {"A": "hello", "B": "", "C": "world"}
        result = filter_non_empty(env)
        assert result == {"A": "hello", "C": "world"}

    def test_removes_none_values(self):
        env = {"A": "value", "B": None}
        result = filter_non_empty(env)
        assert result == {"A": "value"}

    def test_all_non_empty_unchanged(self):
        env = {"A": "x", "B": "y"}
        assert filter_non_empty(env) == env

    def test_empty_env_returns_empty(self):
        assert filter_non_empty({}) == {}


class TestFilterByType:
    def test_keeps_strings(self):
        env = {"A": "hello", "B": 42, "C": "world"}
        result = filter_by_type(env, str)
        assert result == {"A": "hello", "C": "world"}

    def test_keeps_ints(self):
        env = {"A": "hello", "B": 42, "C": 7}
        result = filter_by_type(env, int)
        assert result == {"B": 42, "C": 7}

    def test_invalid_type_arg_raises(self):
        with pytest.raises(FilterError, match="type"):
            filter_by_type({"A": "1"}, "str")


class TestRejectByPredicate:
    def test_removes_matching_entries(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = reject_by_predicate(env, lambda k, v: v == "2")
        assert result == {"A": "1", "C": "3"}

    def test_non_callable_raises(self):
        with pytest.raises(FilterError, match="callable"):
            reject_by_predicate({}, 42)

    def test_reject_all_returns_empty(self):
        env = {"A": "1"}
        result = reject_by_predicate(env, lambda k, v: True)
        assert result == {}

    def test_reject_none_returns_all(self):
        env = {"A": "1", "B": "2"}
        result = reject_by_predicate(env, lambda k, v: False)
        assert result == env
