"""Tests for envchain.sorter."""

import pytest

from envchain.sorter import (
    SorterError,
    sort_keys,
    sort_by_value,
    sort_by_custom,
    prioritise_keys,
)


SAMPLE = {"ZEBRA": "z", "ALPHA": "a", "MANGO": "m"}


class TestSortKeys:
    def test_returns_sorted_alphabetically(self):
        result = sort_keys(SAMPLE)
        assert list(result.keys()) == ["ALPHA", "MANGO", "ZEBRA"]

    def test_reverse_order(self):
        result = sort_keys(SAMPLE, reverse=True)
        assert list(result.keys()) == ["ZEBRA", "MANGO", "ALPHA"]

    def test_does_not_mutate_input(self):
        original = dict(SAMPLE)
        sort_keys(SAMPLE)
        assert SAMPLE == original

    def test_empty_dict_returns_empty(self):
        assert sort_keys({}) == {}

    def test_single_entry(self):
        assert sort_keys({"ONLY": "val"}) == {"ONLY": "val"}


class TestSortByValue:
    def test_sorted_by_value(self):
        result = sort_by_value(SAMPLE)
        assert list(result.values()) == ["a", "m", "z"]

    def test_reverse_by_value(self):
        result = sort_by_value(SAMPLE, reverse=True)
        assert list(result.values()) == ["z", "m", "a"]

    def test_empty_dict(self):
        assert sort_by_value({}) == {}


class TestSortByCustom:
    def test_sort_by_value_length(self):
        env = {"A": "longer", "B": "x", "C": "mid"}
        result = sort_by_custom(env, key_fn=lambda item: len(item[1]))
        assert list(result.keys()) == ["B", "C", "A"]

    def test_non_callable_raises(self):
        with pytest.raises(SorterError):
            sort_by_custom(SAMPLE, key_fn="not_callable")  # type: ignore[arg-type]

    def test_reverse_flag_respected(self):
        env = {"A": "1", "B": "22", "C": "333"}
        result = sort_by_custom(env, key_fn=lambda item: len(item[1]), reverse=True)
        assert list(result.keys()) == ["C", "B", "A"]


class TestPrioritiseKeys:
    def test_priority_keys_come_first(self):
        result = prioritise_keys(SAMPLE, priority=["ZEBRA", "ALPHA"])
        keys = list(result.keys())
        assert keys[0] == "ZEBRA"
        assert keys[1] == "ALPHA"

    def test_remaining_keys_sorted(self):
        env = {"C": "c", "A": "a", "B": "b"}
        result = prioritise_keys(env, priority=["C"])
        assert list(result.keys()) == ["C", "A", "B"]

    def test_missing_priority_key_ignored(self):
        result = prioritise_keys(SAMPLE, priority=["MISSING", "ALPHA"])
        assert list(result.keys())[0] == "ALPHA"

    def test_empty_priority(self):
        result = prioritise_keys(SAMPLE, priority=[])
        assert list(result.keys()) == ["ALPHA", "MANGO", "ZEBRA"]

    def test_reverse_rest(self):
        env = {"A": "a", "B": "b", "C": "c"}
        result = prioritise_keys(env, priority=["B"], reverse_rest=True)
        assert list(result.keys()) == ["B", "C", "A"]

    def test_does_not_mutate_input(self):
        original = dict(SAMPLE)
        prioritise_keys(SAMPLE, priority=["ZEBRA"])
        assert SAMPLE == original
