"""Tests for envchain.chain.EnvChain."""

import pytest

from envchain.chain import EnvChain


class TestEnvChainResolve:
    def test_empty_chain_returns_empty_dict(self):
        chain = EnvChain()
        assert chain.resolve() == {}

    def test_base_layer_preserved(self):
        chain = EnvChain(base={"APP_ENV": "development", "PORT": "8080"})
        assert chain.resolve() == {"APP_ENV": "development", "PORT": "8080"}

    def test_later_layer_overrides_earlier(self):
        chain = EnvChain(base={"PORT": "8080", "DEBUG": "true"})
        chain.add_layer({"PORT": "9090"})
        resolved = chain.resolve()
        assert resolved["PORT"] == "9090"
        assert resolved["DEBUG"] == "true"

    def test_multiple_layers_merged_in_order(self):
        chain = (
            EnvChain(base={"A": "1", "B": "2"})
            .add_layer({"B": "20", "C": "3"})
            .add_layer({"C": "30", "D": "4"})
        )
        assert chain.resolve() == {"A": "1", "B": "20", "C": "30", "D": "4"}

    def test_resolve_does_not_mutate_layers(self):
        base = {"X": "original"}
        chain = EnvChain(base=base)
        chain.resolve()
        assert base == {"X": "original"}


class TestEnvChainGet:
    def test_get_existing_key(self):
        chain = EnvChain(base={"DB_URL": "postgres://localhost/mydb"})
        assert chain.get("DB_URL") == "postgres://localhost/mydb"

    def test_get_missing_key_returns_none(self):
        chain = EnvChain()
        assert chain.get("MISSING") is None

    def test_get_missing_key_with_default(self):
        chain = EnvChain()
        assert chain.get("MISSING", "fallback") == "fallback"


class TestEnvChainStage:
    def test_stage_inherits_parent_variables(self):
        root = EnvChain(base={"APP_ENV": "base", "LOG_LEVEL": "info"})
        prod = root.stage("production", {"APP_ENV": "production"})
        assert prod.get("LOG_LEVEL") == "info"

    def test_stage_overrides_take_precedence(self):
        root = EnvChain(base={"APP_ENV": "base", "PORT": "8080"})
        prod = root.stage("production", {"APP_ENV": "production", "PORT": "443"})
        assert prod.get("APP_ENV") == "production"
        assert prod.get("PORT") == "443"

    def test_stage_does_not_mutate_parent(self):
        root = EnvChain(base={"APP_ENV": "base"})
        root.stage("staging", {"APP_ENV": "staging"})
        assert root.get("APP_ENV") == "base"

    def test_nested_stages(self):
        root = EnvChain(base={"A": "root", "B": "root"})
        staging = root.stage("staging", {"A": "staging"})
        canary = staging.stage("canary", {"B": "canary"})
        assert canary.get("A") == "staging"
        assert canary.get("B") == "canary"


class TestEnvChainFluent:
    def test_add_layer_returns_self(self):
        chain = EnvChain()
        result = chain.add_layer({"K": "V"})
        assert result is chain

    def test_layer_count_increments(self):
        chain = EnvChain(base={"X": "1"})
        assert chain.layer_count == 1
        chain.add_layer({"Y": "2"})
        assert chain.layer_count == 2
