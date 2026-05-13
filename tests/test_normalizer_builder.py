"""Integration tests for normalizer used via EnvChainBuilder pipeline."""

import pytest
from envchain.builder import EnvChainBuilder
from envchain.normalizer import normalize_env, NormalizeError


def _build_normalized(layers, case="upper", strip_values=True):
    """Helper: build env from layers and normalize the result."""
    builder = EnvChainBuilder()
    for layer in layers:
        builder.add_layer(layer)
    resolved = builder.build().resolve()
    return normalize_env(resolved, case=case, strip_values=strip_values)


class TestNormalizerBuilderIntegration:
    def test_built_env_keys_uppercased(self):
        result = _build_normalized([{"db_host": "localhost"}])
        assert "DB_HOST" in result
        assert result["DB_HOST"] == "localhost"

    def test_built_env_values_stripped(self):
        result = _build_normalized([{"KEY": "  trimmed  "}])
        assert result["KEY"] == "trimmed"

    def test_multiple_layers_merged_then_normalized(self):
        result = _build_normalized([
            {"app_env": "  staging  "},
            {"app_version": "  1.2.3  "},
        ])
        assert result["APP_ENV"] == "staging"
        assert result["APP_VERSION"] == "1.2.3"

    def test_override_layer_value_normalized(self):
        result = _build_normalized([
            {"MODE": "  debug  "},
            {"MODE": "  production  "},
        ])
        assert result["MODE"] == "production"

    def test_lower_case_normalization_from_builder(self):
        result = _build_normalized([{"MY_VAR": "hello"}], case="lower")
        assert "my_var" in result
        assert result["my_var"] == "hello"

    def test_duplicate_keys_raises_after_normalization(self):
        with pytest.raises(NormalizeError, match="Duplicate key"):
            _build_normalized([{"db_host": "a", "DB_HOST": "b"}])

    def test_empty_builder_normalizes_to_empty(self):
        result = _build_normalized([])
        assert result == {}
