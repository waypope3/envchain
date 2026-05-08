"""Tests for envchain.sanitizer."""

import pytest

from envchain.sanitizer import (
    SanitizeError,
    sanitize_env,
    sanitize_key,
    sanitize_value,
)


# ---------------------------------------------------------------------------
# sanitize_key
# ---------------------------------------------------------------------------

class TestSanitizeKey:
    def test_valid_key_returned_unchanged(self):
        assert sanitize_key('MY_VAR') == 'MY_VAR'

    def test_leading_underscore_valid(self):
        assert sanitize_key('_PRIVATE') == '_PRIVATE'

    def test_alphanumeric_valid(self):
        assert sanitize_key('Var123') == 'Var123'

    def test_invalid_key_raises_by_default(self):
        with pytest.raises(SanitizeError):
            sanitize_key('MY-VAR')

    def test_leading_digit_raises_by_default(self):
        with pytest.raises(SanitizeError):
            sanitize_key('1VAR')

    def test_replace_invalid_hyphen(self):
        assert sanitize_key('MY-VAR', replace_invalid=True) == 'MY_VAR'

    def test_replace_invalid_leading_digit(self):
        assert sanitize_key('1VAR', replace_invalid=True) == '_1VAR'

    def test_replace_custom_replacement_char(self):
        assert sanitize_key('MY.VAR', replace_invalid=True, replacement='X') == 'MYXVAR'

    def test_non_string_key_raises(self):
        with pytest.raises(SanitizeError):
            sanitize_key(123)  # type: ignore[arg-type]

    def test_empty_after_sanitization_raises(self):
        with pytest.raises(SanitizeError):
            sanitize_key('---', replace_invalid=True, replacement='')


# ---------------------------------------------------------------------------
# sanitize_value
# ---------------------------------------------------------------------------

class TestSanitizeValue:
    def test_plain_string_unchanged(self):
        assert sanitize_value('hello world') == 'hello world'

    def test_null_bytes_stripped_by_default(self):
        assert sanitize_value('val\x00ue') == 'value'

    def test_null_bytes_kept_when_disabled(self):
        assert sanitize_value('val\x00ue', strip_null_bytes=False) == 'val\x00ue'

    def test_non_string_raises(self):
        with pytest.raises(SanitizeError):
            sanitize_value(42)  # type: ignore[arg-type]

    def test_empty_string_ok(self):
        assert sanitize_value('') == ''


# ---------------------------------------------------------------------------
# sanitize_env
# ---------------------------------------------------------------------------

class TestSanitizeEnv:
    def test_clean_env_returned_unchanged(self):
        env = {'HOST': 'localhost', 'PORT': '8080'}
        result = sanitize_env(env)
        assert result == env

    def test_does_not_mutate_input(self):
        env = {'KEY': 'val\x00ue'}
        original = dict(env)
        sanitize_env(env)
        assert env == original

    def test_null_bytes_stripped_in_values(self):
        result = sanitize_env({'KEY': 'a\x00b'})
        assert result['KEY'] == 'ab'

    def test_invalid_key_raises_without_replace(self):
        with pytest.raises(SanitizeError):
            sanitize_env({'bad-key': 'value'})

    def test_invalid_key_replaced(self):
        result = sanitize_env({'bad-key': 'value'}, replace_invalid_keys=True)
        assert 'bad_key' in result

    def test_duplicate_sanitized_keys_raises(self):
        with pytest.raises(SanitizeError, match='Duplicate'):
            sanitize_env({'bad-key': 'v1', 'bad.key': 'v2'}, replace_invalid_keys=True)

    def test_empty_env_returns_empty(self):
        assert sanitize_env({}) == {}
