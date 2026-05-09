"""Integration tests for tagger used alongside EnvChainBuilder."""

import pytest
from envchain.builder import EnvChainBuilder
from envchain.tagger import tag_keys, filter_by_tag, list_tags


def _build_env():
    builder = EnvChainBuilder()
    builder.add_layer({"DB_HOST": "localhost", "DB_PORT": "5432"})
    builder.add_layer({"APP_ENV": "staging", "SECRET_KEY": "s3cr3t"})
    return builder.build()


class TestTaggerBuilderIntegration:
    def test_tag_and_filter_from_built_env(self):
        env = _build_env()
        reg = tag_keys(env, ["DB_HOST", "DB_PORT"], "database")
        subset = filter_by_tag(env, "database", reg)
        assert "DB_HOST" in subset
        assert "DB_PORT" in subset
        assert "APP_ENV" not in subset

    def test_sensitive_tag_isolates_secret(self):
        env = _build_env()
        reg = tag_keys(env, ["SECRET_KEY"], "sensitive")
        sensitive = filter_by_tag(env, "sensitive", reg)
        assert list(sensitive.keys()) == ["SECRET_KEY"]

    def test_multiple_tags_list_all(self):
        env = _build_env()
        reg = tag_keys(env, ["DB_HOST"], "database")
        reg = tag_keys(env, ["SECRET_KEY"], "sensitive", registry=reg)
        reg = tag_keys(env, ["APP_ENV"], "runtime", registry=reg)
        tags = list_tags(reg)
        assert tags == {"database", "sensitive", "runtime"}

    def test_filter_returns_correct_values(self):
        env = _build_env()
        reg = tag_keys(env, ["DB_HOST"], "infra")
        result = filter_by_tag(env, "infra", reg)
        assert result["DB_HOST"] == "localhost"

    def test_untagged_keys_not_in_any_filter(self):
        env = _build_env()
        reg = tag_keys(env, ["DB_HOST"], "database")
        result = filter_by_tag(env, "database", reg)
        assert "APP_ENV" not in result
        assert "SECRET_KEY" not in result
