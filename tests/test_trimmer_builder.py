"""Integration tests: trimmer used via EnvChainBuilder."""

import pytest

from envchain.builder import EnvChainBuilder
from envchain.trimmer import TrimError


def _builder_trimmed(**kv: str) -> EnvChainBuilder:
    return EnvChainBuilder().add_trimmed(kv)


class TestBuilderTrimmedLayer:
    def test_values_trimmed_in_resolved_env(self):
        result = _builder_trimmed(HOST="  localhost  ").build()
        assert result["HOST"] == "localhost"

    def test_keys_trimmed_in_resolved_env(self):
        builder = EnvChainBuilder().add_trimmed({" PORT ": "8080"})
        result = builder.build()
        assert "PORT" in result
        assert result["PORT"] == "8080"

    def test_normalize_keys_uppercases(self):
        builder = EnvChainBuilder().add_trimmed({"host": "db"}, normalize_keys=True)
        result = builder.build()
        assert "HOST" in result
        assert result["HOST"] == "db"

    def test_trimmed_layer_overrides_earlier_layer(self):
        builder = (
            EnvChainBuilder()
            .add_layer({"API_URL": "old"})
            .add_trimmed({"API_URL": "  new  "})
        )
        result = builder.build()
        assert result["API_URL"] == "new"

    def test_earlier_layer_not_mutated(self):
        base = {"KEY": "  spaced  "}
        EnvChainBuilder().add_layer(base).add_trimmed({"OTHER": "x"}).build()
        assert base["KEY"] == "  spaced  "

    def test_empty_trimmed_layer_merges_cleanly(self):
        result = (
            EnvChainBuilder()
            .add_layer({"A": "1"})
            .add_trimmed({})
            .build()
        )
        assert result["A"] == "1"

    def test_to_dict_contains_trimmed_values(self):
        d = _builder_trimmed(SECRET="  abc  ").to_dict()
        assert d["SECRET"] == "abc"

    def test_to_dotenv_contains_trimmed_values(self):
        dotenv = _builder_trimmed(TOKEN="  xyz  ").to_dotenv()
        assert "TOKEN=xyz" in dotenv
