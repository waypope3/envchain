"""Tests for envchain.splitter."""

import pytest

from envchain.splitter import SplitError, split_by_keys, split_by_predicate, split_by_prefix


# ---------------------------------------------------------------------------
# split_by_prefix
# ---------------------------------------------------------------------------

class TestSplitByPrefix:
    def _env(self):
        return {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "APP_NAME": "myapp",
            "APP_DEBUG": "true",
            "UNRELATED": "value",
        }

    def test_basic_split(self):
        result = split_by_prefix(self._env(), ["DB", "APP"])
        assert result["DB"] == {"HOST": "localhost", "PORT": "5432"}
        assert result["APP"] == {"NAME": "myapp", "DEBUG": "true"}

    def test_unmatched_goes_to_other(self):
        result = split_by_prefix(self._env(), ["DB", "APP"])
        assert result["__other__"] == {"UNRELATED": "value"}

    def test_strip_prefix_false_keeps_full_key(self):
        result = split_by_prefix(self._env(), ["DB"], strip_prefix=False)
        assert "DB_HOST" in result["DB"]
        assert "DB_PORT" in result["DB"]

    def test_empty_env_returns_empty_buckets(self):
        result = split_by_prefix({}, ["DB", "APP"])
        assert result["DB"] == {}
        assert result["APP"] == {}
        assert result["__other__"] == {}

    def test_no_prefixes_all_go_to_other(self):
        result = split_by_prefix({"FOO": "bar"}, [])
        assert result["__other__"] == {"FOO": "bar"}

    def test_invalid_separator_raises(self):
        with pytest.raises(SplitError):
            split_by_prefix({"A": "1"}, ["A"], separator="")

    def test_first_matching_prefix_wins(self):
        env = {"A_B_KEY": "val"}
        result = split_by_prefix(env, ["A", "A_B"])
        assert "B_KEY" in result["A"]
        assert result["A_B"] == {}


# ---------------------------------------------------------------------------
# split_by_predicate
# ---------------------------------------------------------------------------

class TestSplitByPredicate:
    def test_basic_predicate(self):
        env = {"SECRET_KEY": "abc", "PORT": "8080", "TOKEN": "xyz"}
        predicates = {
            "sensitive": lambda k, v: "SECRET" in k or "TOKEN" in k,
            "numeric": lambda k, v: v.isdigit(),
        }
        result = split_by_predicate(env, predicates)
        assert "SECRET_KEY" in result["sensitive"]
        assert "TOKEN" in result["sensitive"]
        assert "PORT" in result["numeric"]
        assert result["__other__"] == {}

    def test_unmatched_goes_to_other(self):
        env = {"FOO": "bar"}
        result = split_by_predicate(env, {"digits": lambda k, v: v.isdigit()})
        assert result["__other__"] == {"FOO": "bar"}

    def test_empty_env(self):
        result = split_by_predicate({}, {"x": lambda k, v: True})
        assert result["x"] == {}
        assert result["__other__"] == {}


# ---------------------------------------------------------------------------
# split_by_keys
# ---------------------------------------------------------------------------

class TestSplitByKeys:
    def test_basic_split(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = split_by_keys(env, {"group1": ["A", "B"], "group2": ["C"]})
        assert result["group1"] == {"A": "1", "B": "2"}
        assert result["group2"] == {"C": "3"}
        assert result["__other__"] == {}

    def test_missing_key_skipped_by_default(self):
        env = {"A": "1"}
        result = split_by_keys(env, {"g": ["A", "MISSING"]})
        assert result["g"] == {"A": "1"}

    def test_missing_key_strict_raises(self):
        with pytest.raises(SplitError, match="MISSING"):
            split_by_keys({"A": "1"}, {"g": ["A", "MISSING"]}, strict=True)

    def test_unassigned_keys_go_to_other(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = split_by_keys(env, {"g": ["A"]})
        assert "B" in result["__other__"]
        assert "C" in result["__other__"]

    def test_empty_env_and_groups(self):
        result = split_by_keys({}, {})
        assert result["__other__"] == {}
