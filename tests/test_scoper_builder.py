"""Integration tests: scoper used through EnvChainBuilder."""
import pytest
from envchain.builder import EnvChainBuilder
from envchain.scoper import ScopeError


class TestBuilderScopedLayer:
    def test_add_scoped_prefixes_keys(self):
        builder = EnvChainBuilder()
        builder.add_scoped({"HOST": "db.local", "PORT": "5432"}, "prod")
        result = builder.resolve()
        assert result["PROD__HOST"] == "db.local"
        assert result["PROD__PORT"] == "5432"

    def test_add_scoped_does_not_mutate_input(self):
        original = {"KEY": "value"}
        builder = EnvChainBuilder()
        builder.add_scoped(original, "staging")
        assert "STAGING__KEY" not in original

    def test_multiple_scopes_coexist(self):
        builder = EnvChainBuilder()
        builder.add_scoped({"A": "1"}, "dev")
        builder.add_scoped({"A": "2"}, "prod")
        result = builder.resolve()
        assert result["DEV__A"] == "1"
        assert result["PROD__A"] == "2"

    def test_scoped_layer_overrides_earlier_same_key(self):
        builder = EnvChainBuilder()
        builder.add_dict({"PROD__DB": "old"})
        builder.add_scoped({"DB": "new"}, "prod")
        result = builder.resolve()
        assert result["PROD__DB"] == "new"

    def test_resolve_scope_returns_only_matching(self):
        builder = EnvChainBuilder()
        builder.add_scoped({"HOST": "localhost"}, "prod")
        builder.add_scoped({"HOST": "devhost"}, "dev")
        prod_env = builder.resolve_scope("prod")
        assert prod_env == {"HOST": "localhost"}

    def test_resolve_scope_empty_when_no_match(self):
        builder = EnvChainBuilder()
        builder.add_dict({"UNRELATED": "val"})
        result = builder.resolve_scope("prod")
        assert result == {}

    def test_add_scoped_empty_scope_raises(self):
        builder = EnvChainBuilder()
        with pytest.raises(ScopeError):
            builder.add_scoped({"K": "v"}, "")

    def test_resolve_scope_empty_scope_raises(self):
        builder = EnvChainBuilder()
        builder.add_dict({"X": "1"})
        with pytest.raises(ScopeError):
            builder.resolve_scope("")
