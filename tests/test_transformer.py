"""Tests for envchain.transformer module."""

import pytest
from envchain.transformer import (
    TransformError,
    transform_env,
)


class TestTransformEnv:
    BASE = {"PORT": "8080", "DEBUG": "true", "RATIO": "3.14", "TAGS": "a,b,c"}

    def test_no_rules_returns_copy(self):
        result = transform_env(self.BASE, {})
        assert result == self.BASE
        assert result is not self.BASE

    def test_int_transform(self):
        result = transform_env(self.BASE, {"PORT": "int"})
        assert result["PORT"] == 8080
        assert isinstance(result["PORT"], int)

    def test_float_transform(self):
        result = transform_env(self.BASE, {"RATIO": "float"})
        assert result["RATIO"] == pytest.approx(3.14)

    def test_bool_true_variants(self):
        for val in ("true", "1", "yes", "on", "True", "YES"):
            env = {"FLAG": val}
            result = transform_env(env, {"FLAG": "bool"})
            assert result["FLAG"] is True

    def test_bool_false_variants(self):
        for val in ("false", "0", "no", "off", "False", "NO"):
            env = {"FLAG": val}
            result = transform_env(env, {"FLAG": "bool"})
            assert result["FLAG"] is False

    def test_bool_invalid_raises(self):
        with pytest.raises(TransformError) as exc_info:
            transform_env({"FLAG": "maybe"}, {"FLAG": "bool"})
        assert "FLAG" in str(exc_info.value)

    def test_list_transform(self):
        result = transform_env(self.BASE, {"TAGS": "list"})
        assert result["TAGS"] == ["a", "b", "c"]

    def test_list_strips_whitespace(self):
        env = {"TAGS": " a , b , c "}
        result = transform_env(env, {"TAGS": "list"})
        assert result["TAGS"] == ["a", "b", "c"]

    def test_upper_transform(self):
        env = {"NAME": "hello"}
        result = transform_env(env, {"NAME": "upper"})
        assert result["NAME"] == "HELLO"

    def test_lower_transform(self):
        env = {"NAME": "HELLO"}
        result = transform_env(env, {"NAME": "lower"})
        assert result["NAME"] == "hello"

    def test_strip_transform(self):
        env = {"NAME": "  hello  "}
        result = transform_env(env, {"NAME": "strip"})
        assert result["NAME"] == "hello"

    def test_missing_key_in_env_skipped(self):
        result = transform_env({"A": "1"}, {"MISSING": "int"})
        assert "MISSING" not in result

    def test_unknown_transform_raises(self):
        with pytest.raises(TransformError) as exc_info:
            transform_env({"A": "1"}, {"A": "nonexistent"})
        assert "nonexistent" in str(exc_info.value)

    def test_custom_transform(self):
        custom = {"reverse": lambda v: v[::-1]}
        env = {"WORD": "hello"}
        result = transform_env(env, {"WORD": "reverse"}, custom=custom)
        assert result["WORD"] == "olleh"

    def test_untransformed_keys_preserved(self):
        result = transform_env(self.BASE, {"PORT": "int"})
        assert result["DEBUG"] == "true"
        assert result["TAGS"] == "a,b,c"

    def test_int_invalid_raises(self):
        with pytest.raises(TransformError):
            transform_env({"PORT": "abc"}, {"PORT": "int"})
