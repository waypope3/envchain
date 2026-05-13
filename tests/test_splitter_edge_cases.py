"""Edge-case tests for envchain.splitter."""

import pytest

from envchain.splitter import SplitError, split_by_keys, split_by_predicate, split_by_prefix


class TestSplitByPrefixEdgeCases:
    def test_key_equal_to_prefix_no_separator_not_matched(self):
        """'DB' should NOT match prefix 'DB' with separator '_' unless 'DB_' prefix."""
        env = {"DB": "value", "DB_HOST": "h"}
        result = split_by_prefix(env, ["DB"])
        assert "HOST" in result["DB"]
        assert "DB" in result["__other__"]

    def test_custom_separator_dot(self):
        env = {"app.name": "myapp", "app.version": "1.0", "other": "x"}
        result = split_by_prefix(env, ["app"], separator=".")
        assert result["app"] == {"name": "myapp", "version": "1.0"}
        assert result["__other__"] == {"other": "x"}

    def test_overlapping_prefixes_first_wins(self):
        env = {"FOO_BAR_KEY": "v"}
        result = split_by_prefix(env, ["FOO", "FOO_BAR"])
        assert "BAR_KEY" in result["FOO"]
        assert result["FOO_BAR"] == {}

    def test_all_keys_match_single_prefix(self):
        env = {"X_A": "1", "X_B": "2"}
        result = split_by_prefix(env, ["X"])
        assert result["X"] == {"A": "1", "B": "2"}
        assert result["__other__"] == {}

    def test_non_string_separator_raises(self):
        with pytest.raises(SplitError):
            split_by_prefix({"A_B": "v"}, ["A"], separator=None)  # type: ignore


class TestSplitByPredicateEdgeCases:
    def test_predicate_receives_key_and_value(self):
        seen = []
        env = {"K": "V"}

        def capture(k, v):
            seen.append((k, v))
            return False

        split_by_predicate(env, {"g": capture})
        assert seen == [("K", "V")]

    def test_empty_predicates_all_other(self):
        env = {"A": "1", "B": "2"}
        result = split_by_predicate(env, {})
        assert result["__other__"] == env

    def test_first_matching_predicate_wins(self):
        env = {"KEY": "42"}
        predicates = {
            "alpha": lambda k, v: True,
            "beta": lambda k, v: True,
        }
        result = split_by_predicate(env, predicates)
        assert "KEY" in result["alpha"]
        assert result["beta"] == {}


class TestSplitByKeysEdgeCases:
    def test_key_in_multiple_groups_assigned_to_first(self):
        """A key listed in two groups should appear in the first group only."""
        env = {"A": "1", "B": "2"}
        result = split_by_keys(env, {"g1": ["A"], "g2": ["A", "B"]})
        assert result["g1"] == {"A": "1"}
        # A is already assigned; g2 should only get B
        assert "A" not in result["__other__"]
        assert result["g2"]["B"] == "2"

    def test_empty_group_list_returns_empty_bucket(self):
        env = {"A": "1"}
        result = split_by_keys(env, {"empty_group": []})
        assert result["empty_group"] == {}
        assert result["__other__"] == {"A": "1"}

    def test_strict_mode_missing_key_message(self):
        with pytest.raises(SplitError, match="'GHOST'"):
            split_by_keys({"A": "1"}, {"g": ["GHOST"]}, strict=True)
