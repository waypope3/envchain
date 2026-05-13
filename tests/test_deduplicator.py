"""Tests for envchain.deduplicator."""
import pytest

from envchain.deduplicator import (
    DeduplicateError,
    deduplicate_values,
    find_duplicate_keys,
    has_duplicate_values,
)


# ---------------------------------------------------------------------------
# deduplicate_values
# ---------------------------------------------------------------------------

class TestDeduplicateValues:
    def test_no_duplicates_unchanged(self):
        env = {"A": "1", "B": "2", "C": "3"}
        result = deduplicate_values(env)
        assert result == env

    def test_duplicate_value_keep_first(self):
        env = {"A": "x", "B": "y", "C": "x"}
        result = deduplicate_values(env, keep="first")
        assert "A" in result
        assert "C" not in result
        assert result["B"] == "y"

    def test_duplicate_value_keep_last(self):
        env = {"A": "x", "B": "y", "C": "x"}
        result = deduplicate_values(env, keep="last")
        assert "C" in result
        assert "A" not in result

    def test_all_same_value_keep_first(self):
        env = {"A": "v", "B": "v", "C": "v"}
        result = deduplicate_values(env, keep="first")
        assert len(result) == 1
        assert "A" in result

    def test_all_same_value_keep_last(self):
        env = {"A": "v", "B": "v", "C": "v"}
        result = deduplicate_values(env, keep="last")
        assert len(result) == 1
        assert "C" in result

    def test_empty_dict_returns_empty(self):
        assert deduplicate_values({}) == {}

    def test_does_not_mutate_input(self):
        env = {"A": "1", "B": "1"}
        original = dict(env)
        deduplicate_values(env)
        assert env == original

    def test_invalid_keep_raises(self):
        with pytest.raises(DeduplicateError, match="keep strategy"):
            deduplicate_values({"A": "1"}, keep="random")

    def test_returns_copy_not_same_object(self):
        env = {"A": "1", "B": "2"}
        result = deduplicate_values(env)
        assert result is not env


# ---------------------------------------------------------------------------
# find_duplicate_keys
# ---------------------------------------------------------------------------

class TestFindDuplicateKeys:
    def test_no_duplicates_returns_empty(self):
        env = {"A": "1", "B": "2"}
        assert find_duplicate_keys(env) == {}

    def test_single_duplicate_pair(self):
        env = {"A": "x", "B": "y", "C": "x"}
        dupes = find_duplicate_keys(env)
        assert "x" in dupes
        assert set(dupes["x"]) == {"A", "C"}

    def test_multiple_duplicate_groups(self):
        env = {"A": "1", "B": "1", "C": "2", "D": "2"}
        dupes = find_duplicate_keys(env)
        assert set(dupes["1"]) == {"A", "B"}
        assert set(dupes["2"]) == {"C", "D"}

    def test_empty_dict_returns_empty(self):
        assert find_duplicate_keys({}) == {}


# ---------------------------------------------------------------------------
# has_duplicate_values
# ---------------------------------------------------------------------------

class TestHasDuplicateValues:
    def test_no_duplicates_returns_false(self):
        assert has_duplicate_values({"A": "1", "B": "2"}) is False

    def test_with_duplicates_returns_true(self):
        assert has_duplicate_values({"A": "x", "B": "x"}) is True

    def test_empty_dict_returns_false(self):
        assert has_duplicate_values({}) is False

    def test_single_key_returns_false(self):
        assert has_duplicate_values({"A": "only"}) is False
