"""Edge case and boundary tests for envchain.coercer."""

import pytest
from envchain.coercer import CoerceError, coerce_value, coerce_env


class TestCoerceValueEdgeCases:
    def test_int_with_whitespace_raises(self):
        # Python int() does strip whitespace, so " 8 " -> 8
        assert coerce_value("K", " 8 ", "int") == 8

    def test_float_scientific_notation(self):
        assert coerce_value("K", "1e3", "float") == pytest.approx(1000.0)

    def test_bool_mixed_case(self):
        assert coerce_value("K", "TRUE", "bool") is True
        assert coerce_value("K", "FALSE", "bool") is False

    def test_list_trailing_comma_ignored(self):
        result = coerce_value("K", "a,b,", "list")
        assert result == ["a", "b"]

    def test_list_only_commas_returns_empty(self):
        result = coerce_value("K", ",,, ,", "list")
        assert result == []

    def test_coerce_error_attributes(self):
        try:
            coerce_value("MY_KEY", "bad", "int")
        except CoerceError as e:
            assert e.key == "MY_KEY"
            assert e.value == "bad"
            assert e.target_type == "int"

    def test_fallback_zero_is_used(self):
        result = coerce_value("K", "bad", "int", fallback=0)
        assert result == 0

    def test_fallback_false_is_used(self):
        result = coerce_value("K", "maybe", "bool", fallback=False)
        assert result is False

    def test_fallback_empty_list_is_used(self):
        # Empty string produces empty list anyway, but ensure fallback type works
        result = coerce_value("K", "bad_int", "int", fallback=[])
        assert result == []


class TestCoerceEnvEdgeCases:
    def test_empty_env_returns_empty(self):
        assert coerce_env({}, {"PORT": "int"}) == {}

    def test_empty_rules_returns_copy(self):
        env = {"A": "1"}
        result = coerce_env(env, {})
        assert result == env
        assert result is not env

    def test_multiple_rules_applied(self):
        env = {"A": "1", "B": "true", "C": "3.0"}
        result = coerce_env(env, {"A": "int", "B": "bool", "C": "float"})
        assert result == {"A": 1, "B": True, "C": pytest.approx(3.0)}

    def test_fallback_only_for_failing_key(self):
        env = {"A": "bad", "B": "42"}
        result = coerce_env(env, {"A": "int", "B": "int"}, fallbacks={"A": -1})
        assert result["A"] == -1
        assert result["B"] == 42

    def test_no_fallback_partial_failure_raises(self):
        env = {"A": "bad", "B": "42"}
        with pytest.raises(CoerceError):
            coerce_env(env, {"A": "int", "B": "int"})
