"""Tests for envchain.masker."""

import pytest
from envchain.masker import (
    is_sensitive_key,
    mask_value,
    mask_env,
    DEFAULT_MASK,
)


class TestIsSensitiveKey:
    def test_password_variants(self):
        assert is_sensitive_key("DB_PASSWORD")
        assert is_sensitive_key("passwd")
        assert is_sensitive_key("user_pwd")

    def test_token_and_secret(self):
        assert is_sensitive_key("GITHUB_TOKEN")
        assert is_sensitive_key("APP_SECRET")
        assert is_sensitive_key("API_KEY")

    def test_non_sensitive_key(self):
        assert not is_sensitive_key("HOST")
        assert not is_sensitive_key("PORT")
        assert not is_sensitive_key("DEBUG")

    def test_extra_patterns_match(self):
        assert is_sensitive_key("MY_PIN", extra_patterns=[r"pin"])

    def test_extra_patterns_no_match(self):
        assert not is_sensitive_key("HOST", extra_patterns=[r"pin"])


class TestMaskValue:
    def test_default_mask(self):
        assert mask_value("supersecret") == DEFAULT_MASK

    def test_custom_mask(self):
        assert mask_value("supersecret", mask="[HIDDEN]") == "[HIDDEN]"

    def test_reveal_chars(self):
        result = mask_value("supersecret", reveal_chars=3)
        assert result == DEFAULT_MASK + "ret"

    def test_reveal_chars_short_value(self):
        # value shorter than reveal_chars → fully masked
        assert mask_value("ab", reveal_chars=5) == DEFAULT_MASK

    def test_empty_value_returns_mask(self):
        assert mask_value("") == DEFAULT_MASK


class TestMaskEnv:
    def _sample_env(self):
        return {
            "HOST": "localhost",
            "PORT": "5432",
            "DB_PASSWORD": "s3cr3t",
            "API_KEY": "abc123",
        }

    def test_sensitive_keys_masked(self):
        result = mask_env(self._sample_env())
        assert result["DB_PASSWORD"] == DEFAULT_MASK
        assert result["API_KEY"] == DEFAULT_MASK

    def test_non_sensitive_keys_unchanged(self):
        result = mask_env(self._sample_env())
        assert result["HOST"] == "localhost"
        assert result["PORT"] == "5432"

    def test_original_not_mutated(self):
        env = self._sample_env()
        mask_env(env)
        assert env["DB_PASSWORD"] == "s3cr3t"

    def test_explicit_keys_always_masked(self):
        env = {"HOST": "localhost", "CUSTOM": "value"}
        result = mask_env(env, explicit_keys=["HOST"])
        assert result["HOST"] == DEFAULT_MASK
        assert result["CUSTOM"] == "value"

    def test_reveal_chars_propagated(self):
        env = {"DB_PASSWORD": "abcdef"}
        result = mask_env(env, reveal_chars=2)
        assert result["DB_PASSWORD"].endswith("ef")

    def test_extra_patterns(self):
        env = {"MY_PIN": "1234", "NAME": "alice"}
        result = mask_env(env, extra_patterns=[r"pin"])
        assert result["MY_PIN"] == DEFAULT_MASK
        assert result["NAME"] == "alice"
