"""Tests for envchain.tagger module."""

import pytest
from envchain.tagger import (
    TaggerError,
    tag_keys,
    get_tags,
    filter_by_tag,
    remove_tag,
    list_tags,
)

SAMPLE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "prod", "SECRET_KEY": "abc"}


class TestTagKeys:
    def test_basic_tagging(self):
        reg = tag_keys(SAMPLE_ENV, ["DB_HOST", "DB_PORT"], "database")
        assert "database" in reg["DB_HOST"]
        assert "database" in reg["DB_PORT"]

    def test_multiple_tags_on_same_key(self):
        reg = tag_keys(SAMPLE_ENV, ["SECRET_KEY"], "sensitive")
        reg = tag_keys(SAMPLE_ENV, ["SECRET_KEY"], "auth", registry=reg)
        assert reg["SECRET_KEY"] == {"sensitive", "auth"}

    def test_missing_key_raises(self):
        with pytest.raises(TaggerError, match="MISSING"):
            tag_keys(SAMPLE_ENV, ["MISSING"], "mytag")

    def test_empty_tag_raises(self):
        with pytest.raises(TaggerError, match="non-empty"):
            tag_keys(SAMPLE_ENV, ["DB_HOST"], "")

    def test_whitespace_tag_raises(self):
        with pytest.raises(TaggerError, match="non-empty"):
            tag_keys(SAMPLE_ENV, ["DB_HOST"], "   ")

    def test_returns_new_registry_when_none_provided(self):
        reg = tag_keys(SAMPLE_ENV, ["APP_ENV"], "runtime")
        assert isinstance(reg, dict)
        assert "APP_ENV" in reg

    def test_does_not_mutate_existing_registry(self):
        reg = {"DB_HOST": {"database"}}
        original = {"DB_HOST": {"database"}}
        tag_keys(SAMPLE_ENV, ["APP_ENV"], "runtime", registry=reg)
        assert reg["DB_HOST"] == original["DB_HOST"]


class TestGetTags:
    def test_returns_tags_for_known_key(self):
        reg = {"DB_HOST": {"database", "internal"}}
        assert get_tags("DB_HOST", reg) == {"database", "internal"}

    def test_returns_empty_set_for_unknown_key(self):
        assert get_tags("UNKNOWN", {}) == set()

    def test_returns_copy_not_reference(self):
        reg = {"DB_HOST": {"database"}}
        tags = get_tags("DB_HOST", reg)
        tags.add("extra")
        assert "extra" not in reg["DB_HOST"]


class TestFilterByTag:
    def test_returns_only_tagged_keys(self):
        reg = tag_keys(SAMPLE_ENV, ["DB_HOST", "DB_PORT"], "database")
        result = filter_by_tag(SAMPLE_ENV, "database", reg)
        assert set(result.keys()) == {"DB_HOST", "DB_PORT"}

    def test_no_matching_tag_returns_empty(self):
        result = filter_by_tag(SAMPLE_ENV, "nonexistent", {})
        assert result == {}

    def test_values_preserved(self):
        reg = tag_keys(SAMPLE_ENV, ["DB_HOST"], "database")
        result = filter_by_tag(SAMPLE_ENV, "database", reg)
        assert result["DB_HOST"] == "localhost"


class TestRemoveTag:
    def test_removes_specific_tag(self):
        reg = {"DB_HOST": {"database", "internal"}}
        updated = remove_tag("DB_HOST", "internal", reg)
        assert "internal" not in updated["DB_HOST"]
        assert "database" in updated["DB_HOST"]

    def test_key_removed_when_no_tags_left(self):
        reg = {"DB_HOST": {"database"}}
        updated = remove_tag("DB_HOST", "database", reg)
        assert "DB_HOST" not in updated

    def test_does_not_mutate_original(self):
        reg = {"DB_HOST": {"database"}}
        remove_tag("DB_HOST", "database", reg)
        assert "DB_HOST" in reg

    def test_remove_nonexistent_tag_is_safe(self):
        reg = {"DB_HOST": {"database"}}
        updated = remove_tag("DB_HOST", "ghost", reg)
        assert updated["DB_HOST"] == {"database"}


class TestListTags:
    def test_all_unique_tags_returned(self):
        reg = {"DB_HOST": {"database"}, "SECRET_KEY": {"sensitive", "database"}}
        assert list_tags(reg) == {"database", "sensitive"}

    def test_empty_registry_returns_empty_set(self):
        assert list_tags({}) == set()
