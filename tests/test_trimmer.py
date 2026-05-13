"""Tests for envchain.trimmer."""

import pytest

from envchain.trimmer import (
    TrimError,
    collapse_whitespace,
    trim_env,
    trim_env_values_collapsed,
    trim_key,
    trim_value,
)


# ---------------------------------------------------------------------------
# trim_value
# ---------------------------------------------------------------------------

class TestTrimValue:
    def test_strips_leading_trailing_spaces(self):
        assert trim_value("  hello  ") == "hello"

    def test_strips_newlines(self):
        assert trim_value("\nfoo\n") == "foo"

    def test_no_whitespace_unchanged(self):
        assert trim_value("unchanged") == "unchanged"

    def test_empty_string_returns_empty(self):
        assert trim_value("") == ""

    def test_custom_chars_stripped(self):
        assert trim_value("***value***", "*") == "value"

    def test_non_string_raises(self):
        with pytest.raises(TrimError):
            trim_value(123)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# trim_key
# ---------------------------------------------------------------------------

class TestTrimKey:
    def test_strips_and_uppercases(self):
        assert trim_key("  my_key  ") == "MY_KEY"

    def test_already_clean_key(self):
        assert trim_key("DATABASE_URL") == "DATABASE_URL"

    def test_lowercase_normalized(self):
        assert trim_key("host") == "HOST"

    def test_whitespace_only_raises(self):
        with pytest.raises(TrimError):
            trim_key("   ")

    def test_empty_string_raises(self):
        with pytest.raises(TrimError):
            trim_key("")

    def test_non_string_raises(self):
        with pytest.raises(TrimError):
            trim_key(42)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# trim_env
# ---------------------------------------------------------------------------

class TestTrimEnv:
    def test_values_stripped(self):
        result = trim_env({"KEY": "  value  "})
        assert result["KEY"] == "value"

    def test_keys_stripped(self):
        result = trim_env({" KEY ": "val"})
        assert "KEY" in result

    def test_normalize_keys_uppercases(self):
        result = trim_env({"host": "localhost"}, normalize_keys=True)
        assert "HOST" in result
        assert result["HOST"] == "localhost"

    def test_original_not_mutated(self):
        original = {"A": "  x  "}
        trim_env(original)
        assert original["A"] == "  x  "

    def test_empty_env_returns_empty(self):
        assert trim_env({}) == {}

    def test_empty_key_after_strip_raises(self):
        with pytest.raises(TrimError):
            trim_env({"   ": "value"})

    def test_custom_strip_chars(self):
        result = trim_env({"K": "##secret##"}, strip_chars="#")
        assert result["K"] == "secret"


# ---------------------------------------------------------------------------
# collapse_whitespace
# ---------------------------------------------------------------------------

class TestCollapseWhitespace:
    def test_multiple_spaces_collapsed(self):
        assert collapse_whitespace("foo   bar") == "foo bar"

    def test_tabs_and_newlines_collapsed(self):
        assert collapse_whitespace("a\t\nb") == "a b"

    def test_leading_trailing_stripped(self):
        assert collapse_whitespace("  hello world  ") == "hello world"

    def test_already_clean(self):
        assert collapse_whitespace("clean") == "clean"

    def test_non_string_raises(self):
        with pytest.raises(TrimError):
            collapse_whitespace(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# trim_env_values_collapsed
# ---------------------------------------------------------------------------

class TestTrimEnvValuesCollapsed:
    def test_collapses_all_values(self):
        env = {"A": "foo   bar", "B": "  baz  "}
        result = trim_env_values_collapsed(env)
        assert result["A"] == "foo bar"
        assert result["B"] == "baz"

    def test_keys_unchanged(self):
        env = {"my_key": "value"}
        result = trim_env_values_collapsed(env)
        assert "my_key" in result

    def test_empty_returns_empty(self):
        assert trim_env_values_collapsed({}) == {}
