"""Tests for extract_scopes / merge_scopes round-trip and edge cases."""
import pytest
from envchain.scoper import extract_scopes, merge_scopes, scope_env, ScopeError


class TestExtractScopesEdgeCases:
    def test_multiple_separators_in_key(self):
        env = {"PROD__DB__HOST": "localhost"}
        result = extract_scopes(env)
        # Only first separator is used as partition
        assert result["PROD"] == {"DB__HOST": "localhost"}

    def test_all_keys_unscoped(self):
        env = {"FOO": "bar", "BAZ": "qux"}
        result = extract_scopes(env)
        assert result == {"": {"FOO": "bar", "BAZ": "qux"}}

    def test_scope_names_uppercased_by_scope_env(self):
        result = scope_env({"key": "val"}, "MyScope")
        assert "MYSCOPE__key" in result

    def test_extract_then_merge_preserves_values(self):
        original = {
            "PROD__HOST": "prod.host",
            "PROD__PORT": "443",
            "DEV__HOST": "dev.host",
        }
        assert merge_scopes(extract_scopes(original)) == original

    def test_merge_empty_scoped_dict(self):
        assert merge_scopes({}) == {}

    def test_merge_scope_with_empty_string_scope(self):
        scoped = {"": {"BARE": "1"}, "PROD": {"X": "2"}}
        result = merge_scopes(scoped)
        assert result["BARE"] == "1"
        assert result["PROD__X"] == "2"

    def test_extract_single_separator_char(self):
        env = {"A_B": "val"}
        result = extract_scopes(env, separator="_")
        assert result["A"] == {"B": "val"}

    def test_scope_env_non_dict_raises(self):
        with pytest.raises(ScopeError):
            scope_env(None, "prod")
