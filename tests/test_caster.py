"""Tests for envchain.caster."""

import pytest

from envchain.caster import CastError, cast_env, cast_value


# ---------------------------------------------------------------------------
# cast_value
# ---------------------------------------------------------------------------

class TestCastValue:
    def test_str_passthrough(self):
        assert cast_value("K", "hello", str) == "hello"

    def test_int_valid(self):
        assert cast_value("PORT", "8080", int) == 8080

    def test_int_negative(self):
        assert cast_value("OFFSET", "-3", int) == -3

    def test_int_invalid_raises(self):
        with pytest.raises(CastError) as exc_info:
            cast_value("PORT", "abc", int)
        assert "PORT" in str(exc_info.value)

    def test_float_valid(self):
        assert cast_value("RATIO", "3.14", float) == pytest.approx(3.14)

    def test_float_invalid_raises(self):
        with pytest.raises(CastError):
            cast_value("RATIO", "not_a_float", float)

    def test_bool_true_variants(self):
        for raw in ("true", "True", "TRUE", "1", "yes", "on"):
            assert cast_value("FLAG", raw, bool) is True

    def test_bool_false_variants(self):
        for raw in ("false", "False", "FALSE", "0", "no", "off"):
            assert cast_value("FLAG", raw, bool) is False

    def test_bool_invalid_raises(self):
        with pytest.raises(CastError) as exc_info:
            cast_value("FLAG", "maybe", bool)
        assert "bool" in str(exc_info.value)

    def test_unsupported_type_raises(self):
        with pytest.raises(CastError) as exc_info:
            cast_value("K", "v", list)
        assert "unsupported" in str(exc_info.value)


# ---------------------------------------------------------------------------
# cast_env
# ---------------------------------------------------------------------------

class TestCastEnv:
    def test_no_schema_returns_copy(self):
        env = {"A": "1", "B": "hello"}
        result = cast_env(env, {})
        assert result == env
        assert result is not env

    def test_casts_specified_keys(self):
        env = {"PORT": "9000", "DEBUG": "true", "RATE": "0.5", "NAME": "app"}
        schema = {"PORT": int, "DEBUG": bool, "RATE": float}
        result = cast_env(env, schema)
        assert result["PORT"] == 9000
        assert result["DEBUG"] is True
        assert result["RATE"] == pytest.approx(0.5)
        assert result["NAME"] == "app"  # untouched

    def test_unrelated_keys_preserved(self):
        env = {"X": "hello", "PORT": "80"}
        result = cast_env(env, {"PORT": int})
        assert result["X"] == "hello"

    def test_missing_key_skipped_by_default(self):
        env = {"A": "1"}
        result = cast_env(env, {"MISSING": int})
        assert "MISSING" not in result

    def test_missing_key_strict_raises(self):
        env = {"A": "1"}
        with pytest.raises(CastError) as exc_info:
            cast_env(env, {"MISSING": int}, strict=True)
        assert "MISSING" in str(exc_info.value)

    def test_original_env_not_mutated(self):
        env = {"PORT": "8080"}
        cast_env(env, {"PORT": int})
        assert env["PORT"] == "8080"  # still a string

    def test_cast_error_propagates(self):
        env = {"PORT": "not_a_number"}
        with pytest.raises(CastError):
            cast_env(env, {"PORT": int})
