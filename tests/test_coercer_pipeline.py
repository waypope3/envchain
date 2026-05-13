"""Pipeline integration: coercion as a pipeline step."""

import pytest
from envchain.pipeline import EnvPipeline
from envchain.coercer import coerce_env
from envchain.builder import EnvChainBuilder


def _coerce_step(rules):
    """Return a pipeline-compatible callable that coerces env values."""
    def step(env):
        return coerce_env(env, rules)
    return step


class TestCoercerPipelineIntegration:
    def _base_env(self):
        builder = EnvChainBuilder()
        builder.add_layer({
            "PORT": "8080",
            "DEBUG": "yes",
            "WORKERS": "2",
            "TAGS": "alpha,beta,gamma",
        })
        return builder.build()

    def test_pipeline_coerces_int(self):
        pipeline = EnvPipeline()
        pipeline.add_step(_coerce_step({"PORT": "int", "WORKERS": "int"}))
        result = pipeline.run(self._base_env())
        assert result["PORT"] == 8080
        assert result["WORKERS"] == 2

    def test_pipeline_coerces_bool(self):
        pipeline = EnvPipeline()
        pipeline.add_step(_coerce_step({"DEBUG": "bool"}))
        result = pipeline.run(self._base_env())
        assert result["DEBUG"] is True

    def test_pipeline_coerces_list(self):
        pipeline = EnvPipeline()
        pipeline.add_step(_coerce_step({"TAGS": "list"}))
        result = pipeline.run(self._base_env())
        assert result["TAGS"] == ["alpha", "beta", "gamma"]

    def test_pipeline_chained_coerce_steps(self):
        pipeline = EnvPipeline()
        pipeline.add_step(_coerce_step({"PORT": "int"}))
        pipeline.add_step(_coerce_step({"DEBUG": "bool"}))
        result = pipeline.run(self._base_env())
        assert result["PORT"] == 8080
        assert result["DEBUG"] is True

    def test_pipeline_does_not_mutate_original(self):
        env = self._base_env()
        original_port = env["PORT"]
        pipeline = EnvPipeline()
        pipeline.add_step(_coerce_step({"PORT": "int"}))
        pipeline.run(env)
        assert env["PORT"] == original_port
