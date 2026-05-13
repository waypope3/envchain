"""Integration tests: aliaser used with EnvChainBuilder."""

import pytest

from envchain.builder import EnvChainBuilder
from envchain.aliaser import apply_aliases, AliasError


def _build_env():
    builder = EnvChainBuilder()
    builder.add_layer({"DB_HOST": "db.internal", "DB_PORT": "5432", "SECRET_KEY": "s3cr3t"})
    builder.add_layer({"APP_ENV": "staging"})
    return builder.build().resolve()


class TestAliasBuilderIntegration:
    def test_alias_applied_to_built_env(self):
        env = _build_env()
        result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"})
        assert result["DATABASE_HOST"] == "db.internal"

    def test_original_preserved_after_alias(self):
        env = _build_env()
        result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"})
        assert result["DB_HOST"] == "db.internal"

    def test_alias_with_keep_original_false(self):
        env = _build_env()
        result = apply_aliases(env, {"DB_HOST": "DATABASE_HOST"}, keep_original=False)
        assert "DB_HOST" not in result
        assert result["DATABASE_HOST"] == "db.internal"

    def test_multiple_aliases_from_builder(self):
        env = _build_env()
        aliases = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
        result = apply_aliases(env, aliases)
        assert result["DATABASE_HOST"] == "db.internal"
        assert result["DATABASE_PORT"] == "5432"
        assert result["DB_HOST"] == "db.internal"

    def test_missing_key_raises_for_built_env(self):
        env = _build_env()
        with pytest.raises(AliasError, match="NONEXISTENT"):
            apply_aliases(env, {"NONEXISTENT": "ALIAS"})

    def test_missing_ok_skips_absent_key(self):
        env = _build_env()
        result = apply_aliases(env, {"NONEXISTENT": "ALIAS"}, missing_ok=True)
        assert "ALIAS" not in result
