"""Tests for envchain.renamer."""
import pytest

from envchain.renamer import (
    RenameError,
    build_rename_mapping,
    rename_by,
    rename_keys,
)


class TestRenameKeys:
    def test_basic_rename(self):
        env = {"OLD_KEY": "value"}
        result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
        assert result == {"NEW_KEY": "value"}

    def test_unmapped_keys_preserved(self):
        env = {"A": "1", "B": "2"}
        result = rename_keys(env, {"A": "ALPHA"})
        assert result == {"ALPHA": "1", "B": "2"}

    def test_empty_mapping_returns_copy(self):
        env = {"X": "x", "Y": "y"}
        result = rename_keys(env, {})
        assert result == env
        assert result is not env

    def test_empty_env_returns_empty(self):
        assert rename_keys({}, {"A": "B"}) == {}

    def test_base_not_mutated(self):
        env = {"KEY": "val"}
        rename_keys(env, {"KEY": "OTHER"})
        assert "KEY" in env

    def test_collision_raises(self):
        env = {"A": "1", "B": "2"}
        with pytest.raises(RenameError, match="collision"):
            rename_keys(env, {"A": "C", "B": "C"})

    def test_strict_missing_key_raises(self):
        env = {"A": "1"}
        with pytest.raises(RenameError, match="strict"):
            rename_keys(env, {"MISSING": "NEW"}, strict=True)

    def test_strict_all_present_no_error(self):
        env = {"A": "1", "B": "2"}
        result = rename_keys(env, {"A": "ALPHA", "B": "BETA"}, strict=True)
        assert result == {"ALPHA": "1", "BETA": "2"}

    def test_invalid_mapping_type_raises(self):
        with pytest.raises(RenameError):
            rename_keys({"A": "1"}, "not-a-dict")  # type: ignore


class TestRenameBy:
    def test_uppercase_transform(self):
        env = {"db_host": "localhost", "db_port": "5432"}
        result = rename_by(env, str.upper)
        assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_prefix_added(self):
        env = {"HOST": "h", "PORT": "p"}
        result = rename_by(env, lambda k: f"APP_{k}")
        assert result == {"APP_HOST": "h", "APP_PORT": "p"}

    def test_collision_raises(self):
        env = {"a": "1", "A": "2"}
        with pytest.raises(RenameError, match="collision"):
            rename_by(env, str.upper)

    def test_non_callable_raises(self):
        with pytest.raises(RenameError, match="callable"):
            rename_by({"A": "1"}, "not-callable")  # type: ignore

    def test_empty_env_returns_empty(self):
        assert rename_by({}, str.upper) == {}

    def test_base_not_mutated(self):
        env = {"key": "val"}
        rename_by(env, str.upper)
        assert "key" in env


class TestBuildRenameMapping:
    def test_generates_correct_mapping(self):
        env = {"db_host": "h", "db_port": "p"}
        mapping = build_rename_mapping(env, str.upper)
        assert mapping == {"db_host": "DB_HOST", "db_port": "DB_PORT"}

    def test_empty_env_returns_empty(self):
        assert build_rename_mapping({}, str.upper) == {}

    def test_identity_func(self):
        env = {"A": "1", "B": "2"}
        mapping = build_rename_mapping(env, lambda k: k)
        assert mapping == {"A": "A", "B": "B"}
