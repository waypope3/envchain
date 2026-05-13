"""Integration tests: EnvStack used alongside EnvChainBuilder."""

import pytest

from envchain.builder import EnvChainBuilder
from envchain.stacker import EnvStack, StackError


def _build_env(**kwargs) -> dict:
    b = EnvChainBuilder()
    b.add_layer(kwargs)
    return b.build().resolve()


class TestStackerBuilderIntegration:
    def test_push_built_env_and_peek(self):
        env = _build_env(APP_ENV="staging", PORT="8080")
        stack = EnvStack(name="staging")
        stack.push(env)
        assert stack.peek()["APP_ENV"] == "staging"

    def test_two_builds_stacked_top_wins(self):
        base = _build_env(DB_HOST="localhost", LOG_LEVEL="info")
        override = _build_env(DB_HOST="prod-db", TIMEOUT="30")
        stack = EnvStack()
        stack.push(base)
        stack.push(override)
        merged = stack.merged()
        assert merged["DB_HOST"] == "prod-db"
        assert merged["LOG_LEVEL"] == "info"
        assert merged["TIMEOUT"] == "30"

    def test_pop_restores_previous_layer(self):
        base = _build_env(STAGE="base")
        top = _build_env(STAGE="top")
        stack = EnvStack()
        stack.push(base)
        stack.push(top)
        stack.pop()
        assert stack.peek()["STAGE"] == "base"

    def test_clear_then_rebuild(self):
        env = _build_env(X="1")
        stack = EnvStack()
        stack.push(env)
        stack.clear()
        assert stack.depth == 0
        stack.push(_build_env(X="2"))
        assert stack.merged()["X"] == "2"

    def test_stack_name_preserved_through_operations(self):
        stack = EnvStack(name="ci")
        stack.push(_build_env(CI="true"))
        stack.pop()
        assert stack.name == "ci"

    def test_merged_empty_after_clear(self):
        stack = EnvStack()
        stack.push(_build_env(A="1"))
        stack.clear()
        assert stack.merged() == {}
