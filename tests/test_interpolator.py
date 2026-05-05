"""Tests for envchain.interpolator module."""

import pytest
from envchain.interpolator import interpolate, InterpolationError


class TestInterpolate:
    def test_no_references_unchanged(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        result = interpolate(env)
        assert result == {"HOST": "localhost", "PORT": "5432"}

    def test_curly_brace_syntax(self):
        env = {"BASE": "http://localhost", "URL": "${BASE}/api"}
        result = interpolate(env)
        assert result["URL"] == "http://localhost/api"

    def test_dollar_only_syntax(self):
        env = {"USER": "admin", "GREETING": "Hello $USER"}
        result = interpolate(env)
        assert result["GREETING"] == "Hello admin"

    def test_multiple_references_in_one_value(self):
        env = {"HOST": "db", "PORT": "5432", "DSN": "${HOST}:${PORT}"}
        result = interpolate(env)
        assert result["DSN"] == "db:5432"

    def test_chained_references(self):
        env = {"A": "hello", "B": "${A} world", "C": "${B}!"}
        result = interpolate(env)
        assert result["C"] == "hello world!"

    def test_undefined_ref_non_strict_leaves_placeholder(self):
        env = {"URL": "${UNDEFINED}/path"}
        result = interpolate(env, strict=False)
        assert result["URL"] == "${UNDEFINED}/path"

    def test_undefined_ref_strict_raises(self):
        env = {"URL": "${MISSING}/path"}
        with pytest.raises(InterpolationError) as exc_info:
            interpolate(env, strict=True)
        assert "MISSING" in str(exc_info.value)
        assert exc_info.value.key == "URL"

    def test_original_dict_not_mutated(self):
        env = {"BASE": "x", "FULL": "${BASE}y"}
        original = dict(env)
        interpolate(env)
        assert env == original

    def test_empty_env_returns_empty(self):
        assert interpolate({}) == {}

    def test_circular_reference_raises(self):
        env = {"A": "${B}", "B": "${A}"}
        with pytest.raises(InterpolationError) as exc_info:
            interpolate(env, strict=True)
        assert "depth" in str(exc_info.value).lower()

    def test_self_reference_raises(self):
        env = {"A": "${A}"}
        with pytest.raises(InterpolationError):
            interpolate(env, strict=True)

    def test_value_without_dollar_sign_unchanged(self):
        env = {"PATH": "/usr/bin:/usr/local/bin"}
        result = interpolate(env)
        assert result["PATH"] == "/usr/bin:/usr/local/bin"

    def test_interpolation_error_has_key_attribute(self):
        err = InterpolationError("test error", key="MY_KEY")
        assert err.key == "MY_KEY"
        assert str(err) == "test error"
