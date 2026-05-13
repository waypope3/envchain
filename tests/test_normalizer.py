"""Tests for envchain.normalizer module."""

import pytest
from envchain.normalizer import (
    NormalizeError,
    normalize_key,
    normalize_value,
    normalize_env,
)


class TestNormalizeKey:
    def test_upper_case_default(self):
        assert normalize_key("my_key") == "MY_KEY"

    def test_lower_case(self):
        assert normalize_key("MY_KEY", case="lower") == "my_key"

    def test_preserve_case(self):
        assert normalize_key("My_Key", case="preserve") == "My_Key"

    def test_strips_whitespace(self):
        assert normalize_key("  MY_KEY  ") == "MY_KEY"

    def test_invalid_case_raises(self):
        with pytest.raises(NormalizeError, match="Unsupported case"):
            normalize_key("key", case="title")

    def test_non_string_raises(self):
        with pytest.raises(NormalizeError, match="string"):
            normalize_key(123)

    def test_already_upper_unchanged(self):
        assert normalize_key("DB_HOST") == "DB_HOST"


class TestNormalizeValue:
    def test_strips_whitespace_by_default(self):
        assert normalize_value("  hello  ") == "hello"

    def test_no_strip_preserves_whitespace(self):
        assert normalize_value("  hello  ", strip=False) == "  hello  "

    def test_collapse_whitespace(self):
        assert normalize_value("hello   world", collapse_whitespace=True) == "hello world"

    def test_collapse_with_strip(self):
        assert normalize_value("  hello   world  ", strip=True, collapse_whitespace=True) == "hello world"

    def test_empty_string_returns_empty(self):
        assert normalize_value("") == ""

    def test_non_string_raises(self):
        with pytest.raises(NormalizeError, match="string"):
            normalize_value(42)

    def test_no_change_needed(self):
        assert normalize_value("production") == "production"


class TestNormalizeEnv:
    def test_keys_uppercased_by_default(self):
        result = normalize_env({"db_host": "localhost", "db_port": "5432"})
        assert "DB_HOST" in result
        assert "DB_PORT" in result

    def test_values_stripped(self):
        result = normalize_env({"KEY": "  value  "})
        assert result["KEY"] == "value"

    def test_empty_env_returns_empty(self):
        assert normalize_env({}) == {}

    def test_does_not_mutate_input(self):
        original = {"key": "  val  "}
        normalize_env(original)
        assert original["key"] == "  val  "

    def test_duplicate_after_normalization_raises(self):
        with pytest.raises(NormalizeError, match="Duplicate key"):
            normalize_env({"db_host": "a", "DB_HOST": "b"})

    def test_lower_case_keys(self):
        result = normalize_env({"MY_VAR": "1"}, case="lower")
        assert "my_var" in result

    def test_preserve_case(self):
        result = normalize_env({"My_Var": "x"}, case="preserve")
        assert "My_Var" in result

    def test_collapse_whitespace_in_values(self):
        result = normalize_env({"MSG": "hello   world"}, collapse_whitespace=True)
        assert result["MSG"] == "hello world"

    def test_returns_new_dict(self):
        env = {"A": "1"}
        result = normalize_env(env)
        assert result is not env
