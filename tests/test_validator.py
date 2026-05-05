"""Tests for envchain.validator module."""

import pytest
from envchain.validator import ValidationError, assert_keys_present, validate


class TestValidate:
    def test_valid_env_no_error(self):
        validate({"HOST": "localhost", "PORT": "8080"}, required=["HOST", "PORT"])

    def test_missing_required_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate({"HOST": "localhost"}, required=["HOST", "PORT", "DB"])
        err = exc_info.value
        assert "PORT" in err.missing
        assert "DB" in err.missing
        assert "HOST" not in err.missing

    def test_wrong_type_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            validate({"RETRIES": "three"}, types={"RETRIES": int})
        err = exc_info.value
        assert "RETRIES" in err.invalid
        assert "int" in err.invalid["RETRIES"]

    def test_correct_type_no_error(self):
        validate({"RETRIES": 3, "DEBUG": True}, types={"RETRIES": int, "DEBUG": bool})

    def test_non_empty_flag_raises_on_blank(self):
        with pytest.raises(ValidationError) as exc_info:
            validate({"HOST": "  ", "PORT": "8080"}, non_empty=True)
        err = exc_info.value
        assert "HOST" in err.invalid

    def test_non_empty_flag_passes_on_filled(self):
        validate({"HOST": "localhost", "PORT": "8080"}, non_empty=True)

    def test_combined_missing_and_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            validate(
                {"HOST": "localhost", "RETRIES": "bad"},
                required=["HOST", "SECRET"],
                types={"RETRIES": int},
            )
        err = exc_info.value
        assert "SECRET" in err.missing
        assert "RETRIES" in err.invalid

    def test_empty_env_no_required_no_error(self):
        validate({})

    def test_missing_required_message_contains_keys(self):
        with pytest.raises(ValidationError) as exc_info:
            validate({}, required=["API_KEY"])
        assert "API_KEY" in str(exc_info.value)

    def test_type_check_skips_missing_keys(self):
        # Key not in env should not cause a type error
        validate({}, types={"MISSING_KEY": int})


class TestAssertKeysPresent:
    def test_all_present_returns_empty(self):
        result = assert_keys_present({"A": 1, "B": 2}, ["A", "B"])
        assert result == []

    def test_some_missing_returns_list(self):
        result = assert_keys_present({"A": 1}, ["A", "B", "C"])
        assert set(result) == {"B", "C"}

    def test_empty_env_returns_all_keys(self):
        result = assert_keys_present({}, ["X", "Y"])
        assert set(result) == {"X", "Y"}

    def test_empty_keys_list_returns_empty(self):
        result = assert_keys_present({"A": 1}, [])
        assert result == []
