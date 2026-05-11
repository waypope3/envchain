"""Tests for envchain.grouper."""

import pytest
from envchain.grouper import (
    GroupError,
    group_by_prefix,
    group_by_mapping,
    group_by_predicate,
)


# ---------------------------------------------------------------------------
# group_by_prefix
# ---------------------------------------------------------------------------

class TestGroupByPrefix:
    def test_basic_grouping(self):
        env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"}
        result = group_by_prefix(env)
        assert result["DB"] == {"HOST": "localhost", "PORT": "5432"}
        assert result["APP"] == {"NAME": "myapp"}

    def test_no_separator_key_goes_to_empty_group(self):
        env = {"PLAIN": "value", "DB_HOST": "localhost"}
        result = group_by_prefix(env)
        assert result[""] == {"PLAIN": "value"}
        assert result["DB"] == {"HOST": "localhost"}

    def test_lowercase_groups(self):
        env = {"DB_HOST": "localhost", "APP_NAME": "x"}
        result = group_by_prefix(env, lowercase_groups=True)
        assert "db" in result
        assert "app" in result

    def test_custom_separator(self):
        env = {"DB.HOST": "localhost", "DB.PORT": "5432"}
        result = group_by_prefix(env, separator=".")
        assert result["DB"] == {"HOST": "localhost", "PORT": "5432"}

    def test_empty_env_returns_empty(self):
        assert group_by_prefix({}) == {}

    def test_empty_separator_raises(self):
        with pytest.raises(GroupError):
            group_by_prefix({"KEY": "val"}, separator="")

    def test_does_not_mutate_input(self):
        env = {"A_B": "1"}
        group_by_prefix(env)
        assert env == {"A_B": "1"}


# ---------------------------------------------------------------------------
# group_by_mapping
# ---------------------------------------------------------------------------

class TestGroupByMapping:
    def test_basic_mapping(self):
        env = {"HOST": "localhost", "PORT": "5432", "TOKEN": "abc"}
        mapping = {"database": ["HOST", "PORT"], "auth": ["TOKEN"]}
        result = group_by_mapping(env, mapping)
        assert result["database"] == {"HOST": "localhost", "PORT": "5432"}
        assert result["auth"] == {"TOKEN": "abc"}

    def test_missing_key_in_env_skipped(self):
        env = {"HOST": "localhost"}
        mapping = {"db": ["HOST", "PORT"]}
        result = group_by_mapping(env, mapping)
        assert "PORT" not in result["db"]

    def test_include_unmatched(self):
        env = {"HOST": "localhost", "EXTRA": "val"}
        mapping = {"db": ["HOST"]}
        result = group_by_mapping(env, mapping, include_unmatched=True)
        assert result["__other__"] == {"EXTRA": "val"}

    def test_no_unmatched_when_flag_false(self):
        env = {"HOST": "localhost", "EXTRA": "val"}
        mapping = {"db": ["HOST"]}
        result = group_by_mapping(env, mapping, include_unmatched=False)
        assert "__other__" not in result


# ---------------------------------------------------------------------------
# group_by_predicate
# ---------------------------------------------------------------------------

class TestGroupByPredicate:
    def test_basic_predicate(self):
        env = {"DB_HOST": "localhost", "APP_NAME": "myapp", "DB_PORT": "5432"}
        predicates = {
            "db": lambda k, v: k.startswith("DB_"),
            "app": lambda k, v: k.startswith("APP_"),
        }
        result = group_by_predicate(env, predicates)
        assert set(result["db"].keys()) == {"DB_HOST", "DB_PORT"}
        assert result["app"] == {"APP_NAME": "myapp"}

    def test_unmatched_included(self):
        env = {"X": "1", "DB_HOST": "h"}
        predicates = {"db": lambda k, v: k.startswith("DB_")}
        result = group_by_predicate(env, predicates, include_unmatched=True)
        assert result["__other__"] == {"X": "1"}

    def test_unmatched_excluded_by_default(self):
        env = {"X": "1", "DB_HOST": "h"}
        predicates = {"db": lambda k, v: k.startswith("DB_")}
        result = group_by_predicate(env, predicates)
        assert "__other__" not in result

    def test_empty_env_all_groups_empty(self):
        predicates = {"db": lambda k, v: True}
        result = group_by_predicate({}, predicates)
        assert result == {"db": {}}
