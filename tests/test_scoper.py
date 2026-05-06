"""Tests for envchain.scoper."""
import pytest
from envchain.scoper import (
    ScopeError,
    scope_env,
    unscope_env,
    extract_scopes,
    merge_scopes,
)


class TestScopeEnv:
    def test_basic_prefix(self):
        result = scope_env({"KEY": "val"}, "prod")
        assert result == {"PROD__KEY": "val"}

    def test_multiple_keys(self):
        result = scope_env({"A": "1", "B": "2"}, "dev")
        assert "DEV__A" in result
        assert "DEV__B" in result

    def test_empty_env_returns_empty(self):
        assert scope_env({}, "prod") == {}

    def test_empty_scope_raises(self):
        with pytest.raises(ScopeError):
            scope_env({"K": "v"}, "")

    def test_custom_separator(self):
        result = scope_env({"X": "1"}, "test", separator=".")
        assert "TEST.X" in result

    def test_non_dict_raises(self):
        with pytest.raises(ScopeError):
            scope_env("not_a_dict", "prod")


class TestUnscopeEnv:
    def test_strips_matching_prefix(self):
        env = {"PROD__DB": "localhost", "PROD__PORT": "5432"}
        result = unscope_env(env, "prod")
        assert result == {"DB": "localhost", "PORT": "5432"}

    def test_drops_non_matching_keys(self):
        env = {"PROD__A": "1", "DEV__B": "2"}
        result = unscope_env(env, "prod")
        assert "A" in result
        assert "DEV__B" not in result

    def test_empty_scope_raises(self):
        with pytest.raises(ScopeError):
            unscope_env({"K": "v"}, "")

    def test_no_matching_keys_returns_empty(self):
        result = unscope_env({"DEV__X": "1"}, "prod")
        assert result == {}


class TestExtractScopes:
    def test_groups_by_scope(self):
        env = {"PROD__A": "1", "DEV__B": "2", "GLOBAL": "g"}
        result = extract_scopes(env)
        assert result["PROD"] == {"A": "1"}
        assert result["DEV"] == {"B": "2"}
        assert result[""]["GLOBAL"] == "g"

    def test_empty_env(self):
        assert extract_scopes({}) == {}

    def test_custom_separator(self):
        env = {"S.K": "v"}
        result = extract_scopes(env, separator=".")
        assert result["S"] == {"K": "v"}


class TestMergeScopes:
    def test_roundtrip(self):
        original = {"PROD__A": "1", "DEV__B": "2"}
        scoped = extract_scopes(original)
        merged = merge_scopes(scoped)
        assert merged == original

    def test_empty_scope_key_passthrough(self):
        scoped = {"": {"BARE": "val"}}
        result = merge_scopes(scoped)
        assert result == {"BARE": "val"}
