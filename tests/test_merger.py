"""Tests for envchain.merger module."""

import pytest
from envchain.merger import (
    merge_replace,
    merge_keep_existing,
    merge_additive,
    merge_strict,
    get_strategy,
    apply_merge,
    MergeError,
)


class TestMergeReplace:
    def test_override_replaces_base(self):
        result = merge_replace({"A": "1"}, {"A": "2"})
        assert result["A"] == "2"

    def test_new_keys_added(self):
        result = merge_replace({"A": "1"}, {"B": "2"})
        assert result == {"A": "1", "B": "2"}

    def test_base_not_mutated(self):
        base = {"A": "1"}
        merge_replace(base, {"A": "2"})
        assert base["A"] == "1"


class TestMergeKeepExisting:
    def test_base_value_preserved(self):
        result = merge_keep_existing({"A": "1"}, {"A": "99"})
        assert result["A"] == "1"

    def test_new_keys_from_override_added(self):
        result = merge_keep_existing({"A": "1"}, {"B": "2"})
        assert result["B"] == "2"

    def test_empty_base_takes_all_override(self):
        result = merge_keep_existing({}, {"X": "hello"})
        assert result == {"X": "hello"}


class TestMergeAdditive:
    def test_strings_concatenated_with_colon(self):
        result = merge_additive({"PATH": "/usr/bin"}, {"PATH": "/usr/local/bin"})
        assert result["PATH"] == "/usr/bin:/usr/local/bin"

    def test_non_string_replaced(self):
        result = merge_additive({"COUNT": 1}, {"COUNT": 2})
        assert result["COUNT"] == 2

    def test_new_key_added(self):
        result = merge_additive({"A": "x"}, {"B": "y"})
        assert result["B"] == "y"


class TestMergeStrict:
    def test_no_overlap_succeeds(self):
        result = merge_strict({"A": "1"}, {"B": "2"})
        assert result == {"A": "1", "B": "2"}

    def test_overlapping_key_raises(self):
        with pytest.raises(MergeError) as exc_info:
            merge_strict({"A": "1"}, {"A": "2"})
        assert "A" in exc_info.value.message

    def test_empty_override_no_error(self):
        result = merge_strict({"A": "1"}, {})
        assert result == {"A": "1"}


class TestGetStrategy:
    def test_valid_strategy_returned(self):
        fn = get_strategy("replace")
        assert callable(fn)

    def test_unknown_strategy_raises(self):
        with pytest.raises(MergeError):
            get_strategy("nonexistent")


class TestApplyMerge:
    def test_multiple_layers_replace(self):
        layers = [{"A": "1"}, {"A": "2"}, {"B": "3"}]
        result = apply_merge(layers, strategy="replace")
        assert result == {"A": "2", "B": "3"}

    def test_empty_layers_returns_empty(self):
        assert apply_merge([], strategy="replace") == {}

    def test_keep_existing_across_layers(self):
        layers = [{"A": "first"}, {"A": "second"}, {"B": "new"}]
        result = apply_merge(layers, strategy="keep_existing")
        assert result["A"] == "first"
        assert result["B"] == "new"

    def test_strict_raises_on_duplicate(self):
        with pytest.raises(MergeError):
            apply_merge([{"A": "1"}, {"A": "2"}], strategy="strict")
