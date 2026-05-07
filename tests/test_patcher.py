import pytest
from envchain.patcher import patch_env, patch_keys, PatchError


class TestPatchEnv:
    def test_basic_override(self):
        result = patch_env({"A": "1", "B": "2"}, {"A": "99"})
        assert result["A"] == "99"
        assert result["B"] == "2"

    def test_new_key_added(self):
        result = patch_env({"A": "1"}, {"B": "2"})
        assert result["A"] == "1"
        assert result["B"] == "2"

    def test_base_not_mutated(self):
        base = {"A": "1"}
        patch_env(base, {"A": "99"})
        assert base["A"] == "1"

    def test_empty_patch_returns_copy(self):
        base = {"A": "1"}
        result = patch_env(base, {})
        assert result == base
        assert result is not base

    def test_empty_base_with_patch(self):
        result = patch_env({}, {"X": "10"})
        assert result == {"X": "10"}

    def test_delete_marker_removes_key(self):
        result = patch_env({"A": "1", "B": "2"}, {"A": "__DELETE__"}, delete_marker="__DELETE__")
        assert "A" not in result
        assert result["B"] == "2"

    def test_delete_marker_missing_key_is_noop(self):
        result = patch_env({"A": "1"}, {"Z": "__DELETE__"}, delete_marker="__DELETE__")
        assert "Z" not in result
        assert result["A"] == "1"

    def test_no_delete_marker_keeps_value(self):
        result = patch_env({"A": "1"}, {"A": "__DELETE__"})
        assert result["A"] == "__DELETE__"

    def test_invalid_base_raises(self):
        with pytest.raises(PatchError, match="base must be a dict"):
            patch_env("not-a-dict", {})

    def test_invalid_patch_raises(self):
        with pytest.raises(PatchError, match="patch must be a dict"):
            patch_env({}, "not-a-dict")


class TestPatchKeys:
    def test_applies_specified_keys_only(self):
        base = {"A": "1", "B": "2", "C": "3"}
        updates = {"A": "99", "B": "88", "C": "77"}
        result = patch_keys(base, updates, ["A", "C"])
        assert result["A"] == "99"
        assert result["B"] == "2"
        assert result["C"] == "77"

    def test_missing_key_in_updates_raises(self):
        with pytest.raises(PatchError, match="Key 'X' not found in updates"):
            patch_keys({"A": "1"}, {"B": "2"}, ["X"])

    def test_base_not_mutated(self):
        base = {"A": "1"}
        patch_keys(base, {"A": "99"}, ["A"])
        assert base["A"] == "1"

    def test_empty_keys_list_returns_copy(self):
        base = {"A": "1"}
        result = patch_keys(base, {"A": "99"}, [])
        assert result == base
        assert result is not base

    def test_invalid_base_raises(self):
        with pytest.raises(PatchError, match="base must be a dict"):
            patch_keys(None, {}, [])

    def test_invalid_updates_raises(self):
        with pytest.raises(PatchError, match="updates must be a dict"):
            patch_keys({}, None, [])
