"""Integration tests: filter functions applied to EnvChainBuilder output."""

import pytest
from envchain.builder import EnvChainBuilder
from envchain.filter import (
    filter_by_predicate,
    filter_by_value,
    filter_non_empty,
    filter_by_type,
    reject_by_predicate,
)


def _build_env():
    builder = EnvChainBuilder()
    builder.add_layer({"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production", "SECRET": ""})
    builder.add_layer({"APP_ENV": "staging", "DEBUG": "false"})
    return builder.build()


class TestFilterBuilderIntegration:
    def test_filter_by_prefix_from_built_env(self):
        env = _build_env()
        result = filter_by_predicate(env, lambda k, v: k.startswith("DB_"))
        assert set(result.keys()) == {"DB_HOST", "DB_PORT"}

    def test_filter_non_empty_removes_blank_secret(self):
        env = _build_env()
        result = filter_non_empty(env)
        assert "SECRET" not in result
        assert "DB_HOST" in result

    def test_filter_by_value_finds_false_flags(self):
        env = _build_env()
        result = filter_by_value(env, ["false"])
        assert result == {"DEBUG": "false"}

    def test_reject_db_keys_from_built_env(self):
        env = _build_env()
        result = reject_by_predicate(env, lambda k, v: k.startswith("DB_"))
        assert "DB_HOST" not in result
        assert "DB_PORT" not in result
        assert "APP_ENV" in result

    def test_filter_by_type_all_strings(self):
        env = _build_env()
        result = filter_by_type(env, str)
        # All values from builder are strings, so nothing removed
        assert set(result.keys()) == set(env.keys())

    def test_later_layer_override_visible_after_filter(self):
        env = _build_env()
        # APP_ENV was overridden to 'staging' by second layer
        result = filter_by_value(env, ["staging"])
        assert result == {"APP_ENV": "staging"}
