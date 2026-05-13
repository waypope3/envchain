"""Tests for envchain.coercer."""

import pytest
from envchain.coercer import CoerceError, coerce_value, coerce_env


class TestCoerceValue:
    def test_str_passthrough(self):
        assert coerce_value("K", "hello", "str") == "hello"

    def test_int_valid(self):
        assert coerce_value("PORT", "8080", "int") == 8080

    def test_int_negative(self):
        assert coerce_value("OFFSET", "-5", "int") == -5

    def test_int_invalid_raises(self):
        with pytest.raises(CoerceError) as exc_info:
            coerce_value("PORT", "abc", "int")
        assert "PORT" in str(exc_info.value)

    def test_float_valid(self):
        assert coerce_value("RATIO", "3.14", "float") == pytest.approx(3.14)

    def test_float_invalid_raises(self):
        with pytest.raises(CoerceError):
            coerce_value("RATIO", "not_a_float", "float")

    def test_bool_true_variants(self):
        for val in ("1", "true", "True", "TRUE", "yes", "on", "enabled"):
            assert coerce_value("FLAG", val, "bool") is True

    def test_bool_false_variants(self):
        for val in ("0", "false", "False", "FALSE", "no", "off", "disabled"):
            assert coerce_value("FLAG", val, "bool") is False

    def test_bool_invalid_raises(self):
        with pytest.raises(CoerceError) as exc_info:
            coerce_value("FLAG", "maybe", "bool")
        assert "bool" in str(exc_info.value)

    def test_list_comma_separated(self):
        result = coerce_value("HOSTS", "a,b,c", "list")
        assert result == ["a", "b", "c"]

    def test_list_strips_whitespace(self):
        result = coerce_value("HOSTS", " a , b , c ", "list")
        assert result == ["a", "b", "c"]

    def test_list_single_item(self):
        assert coerce_value("HOSTS", "only", "list") == ["only"]

    def test_list_empty_string_returns_empty_list(self):
        assert coerce_value("HOSTS", "", "list") == []

    def test_unknown_type_raises(self):
        with pytest.raises(CoerceError) as exc_info:
            coerce_value("K", "v", "datetime")
        assert "unknown target type" in str(exc_info.value)

    def test_fallback_returned_on_failure(self):
        result = coerce_value("PORT", "bad", "int", fallback=9999)
        assert result == 9999

    def test_fallback_none_still_raises(self):
        with pytest.raises(CoerceError):
            coerce_value("PORT", "bad", "int", fallback=None)


class TestCoerceEnv:
    def _env(self):
        return {
            "PORT": "8080",
            "DEBUG": "true",
            "RATIO": "0.5",
            "HOSTS": "a,b",
            "NAME": "myapp",
        }

    def test_no_rules_returns_copy(self):
        env = self._env()
        result = coerce_env(env, {})
        assert result == env
        assert result is not env

    def test_int_rule_applied(self):
        result = coerce_env(self._env(), {"PORT": "int"})
        assert result["PORT"] == 8080

    def test_bool_rule_applied(self):
        result = coerce_env(self._env(), {"DEBUG": "bool"})
        assert result["DEBUG"] is True

    def test_float_rule_applied(self):
        result = coerce_env(self._env(), {"RATIO": "float"})
        assert result["RATIO"] == pytest.approx(0.5)

    def test_list_rule_applied(self):
        result = coerce_env(self._env(), {"HOSTS": "list"})
        assert result["HOSTS"] == ["a", "b"]

    def test_unruled_keys_unchanged(self):
        result = coerce_env(self._env(), {"PORT": "int"})
        assert result["NAME"] == "myapp"

    def test_missing_key_in_env_skipped(self):
        result = coerce_env(self._env(), {"MISSING": "int"})
        assert "MISSING" not in result

    def test_fallback_used_on_bad_value(self):
        env = {"PORT": "oops"}
        result = coerce_env(env, {"PORT": "int"}, fallbacks={"PORT": 80})
        assert result["PORT"] == 80

    def test_no_fallback_raises_on_bad_value(self):
        env = {"PORT": "oops"}
        with pytest.raises(CoerceError):
            coerce_env(env, {"PORT": "int"})

    def test_original_not_mutated(self):
        env = {"PORT": "8080"}
        coerce_env(env, {"PORT": "int"})
        assert env["PORT"] == "8080"
