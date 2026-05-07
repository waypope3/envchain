"""Tests for envchain.selector module."""

import pytest
from envchain.selector import (
    SelectorError,
    exclude_keys,
    rename_keys,
    select_by_pattern,
    select_by_prefix,
    select_keys,
)


SAMPLE = {
    "APP_HOST": "localhost",
    "APP_PORT": "8080",
    "DB_HOST": "db.local",
    "DB_PORT": "5432",
    "DEBUG": "true",
}


class TestSelectKeys:
    def test_returns_only_requested_keys(self):
        result = select_keys(SAMPLE, ["APP_HOST", "DEBUG"])
        assert result == {"APP_HOST": "localhost", "DEBUG": "true"}

    def test_missing_key_raises(self):
        with pytest.raises(SelectorError, match="MISSING"):
            select_keys(SAMPLE, ["APP_HOST", "MISSING"])

    def test_empty_key_list_returns_empty(self):
        assert select_keys(SAMPLE, []) == {}


class TestExcludeKeys:
    def test_removes_specified_keys(self):
        result = exclude_keys(SAMPLE, ["DEBUG", "APP_PORT"])
        assert "DEBUG" not in result
        assert "APP_PORT" not in result
        assert "APP_HOST" in result

    def test_nonexistent_key_ignored(self):
        result = exclude_keys(SAMPLE, ["NONEXISTENT"])
        assert result == SAMPLE

    def test_empty_exclusion_returns_full_copy(self):
        assert exclude_keys(SAMPLE, []) == SAMPLE


class TestSelectByPattern:
    def test_matches_prefix_pattern(self):
        result = select_by_pattern(SAMPLE, r"^APP_")
        assert set(result.keys()) == {"APP_HOST", "APP_PORT"}

    def test_strip_match_removes_prefix(self):
        result = select_by_pattern(SAMPLE, r"^APP_", strip_match=True)
        assert "HOST" in result
        assert "PORT" in result
        assert result["HOST"] == "localhost"

    def test_no_match_returns_empty(self):
        result = select_by_pattern(SAMPLE, r"^XYZ_")
        assert result == {}

    def test_strip_match_skips_exact_match_key(self):
        env = {"APP_": "val", "APP_KEY": "other"}
        result = select_by_pattern(env, r"^APP_", strip_match=True)
        assert "APP_" not in result
        assert "KEY" in result


class TestSelectByPrefix:
    def test_returns_matching_keys_stripped(self):
        result = select_by_prefix(SAMPLE, "DB_")
        assert result == {"HOST": "db.local", "PORT": "5432"}

    def test_no_strip_preserves_full_keys(self):
        result = select_by_prefix(SAMPLE, "DB_", strip_prefix=False)
        assert "DB_HOST" in result

    def test_empty_prefix_raises(self):
        with pytest.raises(SelectorError):
            select_by_prefix(SAMPLE, "")

    def test_no_match_returns_empty(self):
        assert select_by_prefix(SAMPLE, "NOPE_") == {}


class TestRenameKeys:
    def test_renames_existing_key(self):
        result = rename_keys(SAMPLE, {"DEBUG": "VERBOSE"})
        assert "VERBOSE" in result
        assert "DEBUG" not in result
        assert result["VERBOSE"] == "true"

    def test_nonexistent_key_ignored_by_default(self):
        result = rename_keys(SAMPLE, {"MISSING": "NEW"})
        assert "NEW" not in result

    def test_strict_raises_on_missing_key(self):
        with pytest.raises(SelectorError, match="MISSING"):
            rename_keys(SAMPLE, {"MISSING": "NEW"}, strict=True)

    def test_does_not_mutate_original(self):
        original = dict(SAMPLE)
        rename_keys(SAMPLE, {"DEBUG": "VERBOSE"})
        assert SAMPLE == original
