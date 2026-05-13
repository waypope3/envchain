"""Tests for envchain.aliaser."""

import pytest

from envchain.aliaser import AliasError, apply_aliases, invert_aliases, list_aliases


BASE_ENV = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


class TestApplyAliases:
    def test_alias_key_added(self):
        result = apply_aliases(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
        assert result["DATABASE_HOST"] == "localhost"

    def test_original_kept_by_default(self):
        result = apply_aliases(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
        assert "DB_HOST" in result

    def test_original_removed_when_keep_false(self):
        result = apply_aliases(BASE_ENV, {"DB_HOST": "DATABASE_HOST"}, keep_original=False)
        assert "DB_HOST" not in result
        assert result["DATABASE_HOST"] == "localhost"

    def test_multiple_aliases(self):
        aliases = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
        result = apply_aliases(BASE_ENV, aliases)
        assert result["DATABASE_HOST"] == "localhost"
        assert result["DATABASE_PORT"] == "5432"

    def test_missing_key_raises(self):
        with pytest.raises(AliasError, match="MISSING_KEY"):
            apply_aliases(BASE_ENV, {"MISSING_KEY": "ALIAS"})

    def test_missing_key_ok_when_missing_ok(self):
        result = apply_aliases(BASE_ENV, {"MISSING_KEY": "ALIAS"}, missing_ok=True)
        assert "ALIAS" not in result

    def test_empty_alias_name_raises(self):
        with pytest.raises(AliasError):
            apply_aliases(BASE_ENV, {"DB_HOST": ""})

    def test_base_not_mutated(self):
        original = dict(BASE_ENV)
        apply_aliases(BASE_ENV, {"DB_HOST": "DATABASE_HOST"})
        assert BASE_ENV == original

    def test_empty_aliases_returns_copy(self):
        result = apply_aliases(BASE_ENV, {})
        assert result == BASE_ENV
        assert result is not BASE_ENV

    def test_alias_overwrites_existing_key(self):
        env = {"A": "alpha", "B": "beta"}
        result = apply_aliases(env, {"A": "B"})
        assert result["B"] == "alpha"


class TestInvertAliases:
    def test_basic_inversion(self):
        aliases = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
        inverted = invert_aliases(aliases)
        assert inverted == {"DATABASE_HOST": "DB_HOST", "DATABASE_PORT": "DB_PORT"}

    def test_empty_aliases(self):
        assert invert_aliases({}) == {}

    def test_duplicate_alias_raises(self):
        aliases = {"KEY_A": "SHARED_ALIAS", "KEY_B": "SHARED_ALIAS"}
        with pytest.raises(AliasError, match="SHARED_ALIAS"):
            invert_aliases(aliases)

    def test_single_entry(self):
        assert invert_aliases({"ORIGINAL": "ALIAS"}) == {"ALIAS": "ORIGINAL"}


class TestListAliases:
    def test_returns_sorted_alias_names(self):
        aliases = {"Z_KEY": "Z_ALIAS", "A_KEY": "A_ALIAS", "M_KEY": "M_ALIAS"}
        result = list_aliases(aliases)
        assert result == ["A_ALIAS", "M_ALIAS", "Z_ALIAS"]

    def test_empty_returns_empty(self):
        assert list_aliases({}) == []

    def test_single_alias(self):
        assert list_aliases({"X": "Y"}) == ["Y"]
