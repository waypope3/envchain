"""Tests for envchain.comparator."""

import pytest

from envchain.comparator import CompareError, CompareResult, compare_envs


class TestCompareEnvs:
    def test_identical_dicts_no_differences(self):
        env = {"A": "1", "B": "2"}
        result = compare_envs(env, env)
        assert not result.has_differences

    def test_added_key_detected(self):
        result = compare_envs({"A": "1"}, {"A": "1", "B": "2"})
        assert "B" in result.added
        assert result.added["B"] == "2"

    def test_removed_key_detected(self):
        result = compare_envs({"A": "1", "B": "2"}, {"A": "1"})
        assert "B" in result.removed
        assert result.removed["B"] == "2"

    def test_changed_value_detected(self):
        result = compare_envs({"A": "old"}, {"A": "new"})
        assert "A" in result.changed
        assert result.changed["A"] == ("old", "new")

    def test_unchanged_value_recorded(self):
        result = compare_envs({"A": "same"}, {"A": "same"})
        assert "A" in result.unchanged

    def test_empty_before_all_added(self):
        result = compare_envs({}, {"X": "1", "Y": "2"})
        assert set(result.added.keys()) == {"X", "Y"}
        assert not result.removed

    def test_empty_after_all_removed(self):
        result = compare_envs({"X": "1", "Y": "2"}, {})
        assert set(result.removed.keys()) == {"X", "Y"}
        assert not result.added

    def test_keys_filter_limits_scope(self):
        before = {"A": "1", "B": "2"}
        after = {"A": "9", "B": "2", "C": "3"}
        result = compare_envs(before, after, keys=["A"])
        assert "A" in result.changed
        assert "B" not in result.unchanged
        assert "C" not in result.added

    def test_invalid_before_raises(self):
        with pytest.raises(CompareError):
            compare_envs("not-a-dict", {})

    def test_invalid_after_raises(self):
        with pytest.raises(CompareError):
            compare_envs({}, 42)

    def test_has_differences_true_when_changes(self):
        result = compare_envs({"A": "1"}, {"A": "2"})
        assert result.has_differences

    def test_has_differences_false_when_equal(self):
        result = compare_envs({"A": "1"}, {"A": "1"})
        assert not result.has_differences


class TestCompareResultSummary:
    def test_no_changes_summary(self):
        result = compare_envs({"A": "1"}, {"A": "1"})
        assert result.summary() == "no changes"

    def test_summary_contains_added(self):
        result = compare_envs({}, {"A": "1"})
        assert "+1 added" in result.summary()

    def test_summary_contains_removed(self):
        result = compare_envs({"A": "1"}, {})
        assert "-1 removed" in result.summary()

    def test_summary_contains_changed(self):
        result = compare_envs({"A": "old"}, {"A": "new"})
        assert "~1 changed" in result.summary()

    def test_to_dict_structure(self):
        result = compare_envs({"A": "old", "B": "same"}, {"A": "new", "B": "same", "C": "c"})
        d = result.to_dict()
        assert set(d.keys()) == {"added", "removed", "changed", "unchanged"}
        assert d["changed"]["A"] == {"before": "old", "after": "new"}
        assert d["added"]["C"] == "c"
        assert d["unchanged"]["B"] == "same"
