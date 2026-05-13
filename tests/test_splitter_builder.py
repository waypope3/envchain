"""Integration tests: splitter used with EnvChainBuilder output."""

from envchain.builder import EnvChainBuilder
from envchain.splitter import split_by_keys, split_by_prefix


def _build_env():
    builder = EnvChainBuilder()
    builder.add_layer({
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envchain",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
    })
    return builder.build().resolve()


class TestSplitterBuilderIntegration:
    def test_prefix_split_from_built_env(self):
        env = _build_env()
        result = split_by_prefix(env, ["DB", "APP"])
        assert result["DB"]["HOST"] == "localhost"
        assert result["DB"]["PORT"] == "5432"
        assert result["APP"]["NAME"] == "envchain"
        assert result["APP"]["ENV"] == "production"

    def test_other_bucket_contains_log_level(self):
        env = _build_env()
        result = split_by_prefix(env, ["DB", "APP"])
        assert "LOG_LEVEL" in result["__other__"]

    def test_key_split_from_built_env(self):
        env = _build_env()
        result = split_by_keys(
            env,
            {"database": ["DB_HOST", "DB_PORT"], "app": ["APP_NAME", "APP_ENV"]},
        )
        assert result["database"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
        assert result["app"] == {"APP_NAME": "envchain", "APP_ENV": "production"}
        assert result["__other__"] == {"LOG_LEVEL": "info"}

    def test_override_layer_reflected_in_split(self):
        builder = EnvChainBuilder()
        builder.add_layer({"DB_HOST": "localhost", "APP_NAME": "base"})
        builder.add_layer({"DB_HOST": "prod-db"})
        env = builder.build().resolve()
        result = split_by_prefix(env, ["DB"])
        assert result["DB"]["HOST"] == "prod-db"

    def test_empty_prefix_list_all_other(self):
        env = _build_env()
        result = split_by_prefix(env, [])
        assert set(result["__other__"].keys()) == set(env.keys())
