"""Integration tests: coercer used with EnvChainBuilder output."""

import pytest
from envchain.builder import EnvChainBuilder
from envchain.coercer import coerce_env, CoerceError


def _build_env():
    builder = EnvChainBuilder()
    builder.add_layer(
        {
            "APP_PORT": "5000",
            "APP_DEBUG": "false",
            "APP_WORKERS": "4",
            "APP_RATIO": "1.5",
            "APP_HOSTS": "web1,web2,web3",
            "APP_NAME": "envchain",
        }
    )
    return builder.build()


class TestCoercerBuilderIntegration:
    def test_int_coercion_from_built_env(self):
        env = _build_env()
        result = coerce_env(env, {"APP_PORT": "int", "APP_WORKERS": "int"})
        assert result["APP_PORT"] == 5000
        assert result["APP_WORKERS"] == 4

    def test_bool_coercion_from_built_env(self):
        env = _build_env()
        result = coerce_env(env, {"APP_DEBUG": "bool"})
        assert result["APP_DEBUG"] is False

    def test_list_coercion_from_built_env(self):
        env = _build_env()
        result = coerce_env(env, {"APP_HOSTS": "list"})
        assert result["APP_HOSTS"] == ["web1", "web2", "web3"]

    def test_float_coercion_from_built_env(self):
        env = _build_env()
        result = coerce_env(env, {"APP_RATIO": "float"})
        assert result["APP_RATIO"] == pytest.approx(1.5)

    def test_string_key_unaffected(self):
        env = _build_env()
        result = coerce_env(env, {"APP_PORT": "int"})
        assert result["APP_NAME"] == "envchain"

    def test_override_layer_coerced_correctly(self):
        builder = EnvChainBuilder()
        builder.add_layer({"PORT": "3000"})
        builder.add_layer({"PORT": "9000"})
        env = builder.build()
        result = coerce_env(env, {"PORT": "int"})
        assert result["PORT"] == 9000
