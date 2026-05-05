"""Tests for envchain.differ module."""

import pytest
from envchain.differ import diff_envs, EnvDiff


class TestDiffEnvs:
    def test_identical_dicts_no_changes(self):
        env = {"A": "1", "B": "2"}
        result = diff_envs(env, env.copy())
        assert not result.has_changes
        assert result.unchanged == env

    def test_added_keys_detected(self):
        before = {"A": "1"}
        after = {"A": "1", "B": "2"}
        result = diff_envs(before, after)
        assert result.added == {"B": "2"}
        assert not result.removed
        assert not result.changed

    def test_removed_keys_detected(self):
        before = {"A": "1", "B": "2"}
        after = {"A": "1"}
        result = diff_envs(before, after)
        assert result.removed == {"B": "2"}
        assert not result.added
        assert not result.changed

    def test_changed_values_detected(self):
        before = {"A": "old", "B": "same"}
        after = {"A": "new", "B": "same"}
        result = diff_envs(before, after)
        assert result.changed == {"A": ("old", "new")}
        assert result.unchanged == {"B": "same"}
        assert result.has_changes

    def test_empty_before_all_added(self):
        result = diff_envs({}, {"X": "1", "Y": "2"})
        assert result.added == {"X": "1", "Y": "2"}
        assert not result.removed
        assert not result.changed

    def test_empty_after_all_removed(self):
        result = diff_envs({"X": "1", "Y": "2"}, {})
        assert result.removed == {"X": "1", "Y": "2"}
        assert not result.added

    def test_ignore_keys_excluded(self):
        before = {"A": "1", "SECRET": "old"}
        after = {"A": "1", "SECRET": "new"}
        result = diff_envs(before, after, ignore_keys=["SECRET"])
        assert not result.has_changes
        assert "SECRET" not in result.changed

    def test_ignore_keys_added_not_reported(self):
        result = diff_envs({}, {"IGNORED": "val"}, ignore_keys=["IGNORED"])
        assert not result.added

    def test_both_empty_no_changes(self):
        result = diff_envs({}, {})
        assert not result.has_changes


class TestEnvDiffSummary:
    def test_summary_no_changes(self):
        d = EnvDiff()
        assert d.summary() == "(no changes)"

    def test_summary_added(self):
        d = EnvDiff(added={"NEW_KEY": "val"})
        assert "+ NEW_KEY='val'" in d.summary()

    def test_summary_removed(self):
        d = EnvDiff(removed={"OLD_KEY": "val"})
        assert "- OLD_KEY='val'" in d.summary()

    def test_summary_changed(self):
        d = EnvDiff(changed={"KEY": ("old", "new")})
        summary = d.summary()
        assert "~ KEY" in summary
        assert "'old'" in summary
        assert "'new'" in summary

    def test_summary_multiple_entries_sorted(self):
        d = EnvDiff(added={"Z": "1", "A": "2"})
        lines = d.summary().splitlines()
        assert lines[0].startswith("+ A")
        assert lines[1].startswith("+ Z")
