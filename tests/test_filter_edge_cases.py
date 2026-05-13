"""Edge case tests for envchain.filter."""

import pytest
from envchain.filter import (
    FilterError,
    filter_by_predicate,
    filter_by_value,
    filter_non_empty,
    filter_by_type,
    reject_by_predicate,
)


class TestFilterEdgeCases:
    def test_predicate_exception_propagates(self):
        def bad_predicate(k, v):
            raise ValueError("boom")

        with pytest.raises(ValueError, match="boom"):
            filter_by_predicate({"A": "1"}, bad_predicate)

    def test_filter_by_value_preserves_order(self):
        env = {"Z": "x", "A": "x", "M": "x"}
        result = filter_by_value(env, ["x"])
        assert list(result.keys()) == ["Z", "A", "M"]

    def test_filter_non_empty_zero_is_kept(self):
        # 0 is not None or "", so it should be kept
        env = {"A": 0, "B": "", "C": None}
        result = filter_non_empty(env)
        assert "A" in result
        assert "B" not in result
        assert "C" not in result

    def test_filter_by_type_bool_is_int_subtype(self):
        # bool is a subclass of int in Python
        env = {"A": True, "B": 42, "C": "string"}
        result = filter_by_type(env, int)
        # Both True (bool) and 42 (int) should match
        assert "A" in result
        assert "B" in result
        assert "C" not in result

    def test_reject_returns_independent_copy(self):
        env = {"A": "1", "B": "2"}
        result = reject_by_predicate(env, lambda k, v: k == "A")
        result["C"] = "3"
        assert "C" not in env

    def test_filter_by_predicate_returns_independent_copy(self):
        env = {"A": "1", "B": "2"}
        result = filter_by_predicate(env, lambda k, v: True)
        result["NEW"] = "x"
        assert "NEW" not in env

    def test_filter_by_value_with_none_in_allowed(self):
        env = {"A": None, "B": "val", "C": None}
        result = filter_by_value(env, [None])
        assert result == {"A": None, "C": None}

    def test_filter_by_type_empty_env(self):
        assert filter_by_type({}, str) == {}

    def test_reject_all_keys_with_underscore(self):
        env = {"_PRIVATE": "1", "PUBLIC": "2", "_HIDDEN": "3"}
        result = reject_by_predicate(env, lambda k, v: k.startswith("_"))
        assert result == {"PUBLIC": "2"}
