"""Integration tests: renamer used alongside EnvChainBuilder."""
from envchain.builder import EnvChainBuilder
from envchain.renamer import rename_by, rename_keys


def _build_env():
    return (
        EnvChainBuilder()
        .add_layer({"db_host": "localhost", "db_port": "5432", "app_debug": "true"})
        .build()
        .resolve()
    )


class TestRenamerBuilderIntegration:
    def test_rename_keys_from_built_env(self):
        env = _build_env()
        result = rename_keys(env, {"db_host": "DATABASE_HOST", "db_port": "DATABASE_PORT"})
        assert "DATABASE_HOST" in result
        assert "DATABASE_PORT" in result
        assert result["DATABASE_HOST"] == "localhost"

    def test_rename_by_uppercase_from_built_env(self):
        env = _build_env()
        result = rename_by(env, str.upper)
        assert "DB_HOST" in result
        assert "DB_PORT" in result
        assert "APP_DEBUG" in result

    def test_original_env_not_mutated_after_rename(self):
        env = _build_env()
        rename_keys(env, {"db_host": "NEW_HOST"})
        assert "db_host" in env
        assert "NEW_HOST" not in env

    def test_rename_then_second_layer_merge(self):
        base = (
            EnvChainBuilder()
            .add_layer({"host": "old", "port": "80"})
            .build()
            .resolve()
        )
        renamed = rename_keys(base, {"host": "SERVER_HOST", "port": "SERVER_PORT"})
        override = {"SERVER_HOST": "new"}
        merged = {**renamed, **override}
        assert merged["SERVER_HOST"] == "new"
        assert merged["SERVER_PORT"] == "80"
