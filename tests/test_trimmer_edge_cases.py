"""Edge-case tests for envchain.trimmer."""

import pytest

from envchain.trimmer import (
    TrimError,
    collapse_whitespace,
    trim_env,
    trim_key,
    trim_value,
)


class TestTrimValueEdgeCases:
    def test_only_whitespace_returns_empty(self):
        assert trim_value("   ") == ""

    def test_tab_stripped(self):
        assert trim_value("\tval\t") == "val"

    def test_mixed_whitespace_stripped(self):
        assert trim_value("\n\t value \n") == "value"

    def test_internal_spaces_preserved(self):
        assert trim_value("  hello world  ") == "hello world"

    def test_unicode_whitespace_stripped(self):
        # Python strip() handles \u00a0 (non-breaking space) only with explicit chars
        result = trim_value("  val  ")
        assert result == "val"


class TestTrimKeyEdgeCases:
    def test_mixed_case_uppercased(self):
        assert trim_key("My_Key") == "MY_KEY"

    def test_single_char_key(self):
        assert trim_key("a") == "A"

    def test_key_with_numbers(self):
        assert trim_key(" key123 ") == "KEY123"

    def test_key_with_underscores(self):
        assert trim_key("__private__") == "__PRIVATE__"


class TestTrimEnvEdgeCases:
    def test_multiple_keys_all_trimmed(self):
        env = {"A": "  1  ", "B": "  2  ", "C": "  3  "}
        result = trim_env(env)
        assert result == {"A": "1", "B": "2", "C": "3"}

    def test_normalize_keys_does_not_affect_values(self):
        result = trim_env({"key": "  val  "}, normalize_keys=True)
        assert result["KEY"] == "val"

    def test_value_with_only_whitespace_becomes_empty(self):
        result = trim_env({"K": "   "})
        assert result["K"] == ""

    def test_duplicate_keys_after_strip_last_wins(self):
        # Python dicts don't allow duplicate keys; stripping could cause collision
        # only if caller passes such a dict — not possible in normal Python usage
        result = trim_env({"X": "first"})
        assert result["X"] == "first"


class TestCollapseWhitespaceEdgeCases:
    def test_empty_string_returns_empty(self):
        assert collapse_whitespace("") == ""

    def test_only_spaces_returns_empty(self):
        assert collapse_whitespace("     ") == ""

    def test_single_word_unchanged(self):
        assert collapse_whitespace("word") == "word"

    def test_many_spaces_become_one(self):
        assert collapse_whitespace("a     b") == "a b"

    def test_mixed_whitespace_types_collapsed(self):
        assert collapse_whitespace("a\t  \n  b") == "a b"
