"""Integration tests: filter functions composed via EnvPipeline."""

import pytest
from envchain.pipeline import EnvPipeline
from envchain.filter import filter_non_empty, filter_by_predicate, reject_by_predicate


class TestFilterPipelineIntegration:
    def _base_env(self):
        return {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "APP_ENV": "production",
            "SECRET_KEY": "",
            "DEBUG": "false",
        }

    def test_pipeline_filter_non_empty_then_prefix(self):
        pipeline = EnvPipeline()
        pipeline.add_step(filter_non_empty)
        pipeline.add_step(lambda env: filter_by_predicate(env, lambda k, v: k.startswith("DB_")))
        result = pipeline.run(self._base_env())
        assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}

    def test_pipeline_reject_then_non_empty(self):
        pipeline = EnvPipeline()
        pipeline.add_step(lambda env: reject_by_predicate(env, lambda k, v: k.startswith("DB_")))
        pipeline.add_step(filter_non_empty)
        result = pipeline.run(self._base_env())
        assert "DB_HOST" not in result
        assert "SECRET_KEY" not in result
        assert "APP_ENV" in result

    def test_pipeline_does_not_mutate_original(self):
        env = self._base_env()
        original = dict(env)
        pipeline = EnvPipeline()
        pipeline.add_step(filter_non_empty)
        pipeline.run(env)
        assert env == original

    def test_empty_env_through_pipeline(self):
        pipeline = EnvPipeline()
        pipeline.add_step(filter_non_empty)
        pipeline.add_step(lambda env: filter_by_predicate(env, lambda k, v: True))
        result = pipeline.run({})
        assert result == {}
