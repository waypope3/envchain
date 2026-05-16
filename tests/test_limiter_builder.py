"""Integration tests: limiter used on output from EnvChainBuilder."""

import pytest

from envchain.builder import EnvChainBuilder
from envchain.limiter import LimitError, limit_env, limit_keys, limit_value_length


def _build_env() -> dict:
    builder = EnvChainBuilder()
    builder.add_layer(
        {
            "APP_NAME": "myapp",
            "APP_ENV": "production",
            "APP_SECRET": "supersecretvalue",
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }
    )
    return builder.build()


class TestLimiterBuilderIntegration:
    def test_limit_keys_from_built_env(self):
        env = _build_env()
        result = limit_keys(env, 3, strategy="alpha")
        assert len(result) == 3
        assert list(result.keys()) == sorted(result.keys())

    def test_limit_value_length_truncates_secret(self):
        env = _build_env()
        result = limit_value_length(env, 10, truncate=True)
        assert len(result["APP_SECRET"]) <= 10
        # short values are untouched
        assert result["APP_NAME"] == "myapp"

    def test_limit_value_raises_without_truncate(self):
        env = _build_env()
        with pytest.raises(LimitError, match="APP_SECRET"):
            limit_value_length(env, 5)

    def test_limit_env_combined_on_builder_output(self):
        env = _build_env()
        result = limit_env(
            env,
            max_keys=3,
            max_value_length=10,
            key_strategy="alpha",
            truncate_values=True,
        )
        assert len(result) <= 3
        for v in result.values():
            assert len(v) <= 10

    def test_original_env_not_mutated(self):
        env = _build_env()
        original_copy = dict(env)
        limit_env(env, max_keys=2, max_value_length=4, truncate_values=True)
        assert env == original_copy
