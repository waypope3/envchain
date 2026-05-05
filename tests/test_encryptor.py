"""Tests for envchain.encryptor module."""

import pytest
from envchain.encryptor import (
    EncryptionError,
    decrypt_dict,
    decrypt_value,
    encrypt_dict,
    encrypt_value,
)

PASSPHRASE = "supersecret"


class TestEncryptDecryptValue:
    def test_encrypt_returns_enc_prefix(self):
        result = encrypt_value("hello", PASSPHRASE)
        assert result.startswith("enc:")

    def test_roundtrip_simple_value(self):
        original = "my_password_123"
        encrypted = encrypt_value(original, PASSPHRASE)
        decrypted = decrypt_value(encrypted, PASSPHRASE)
        assert decrypted == original

    def test_roundtrip_empty_string(self):
        encrypted = encrypt_value("", PASSPHRASE)
        assert decrypt_value(encrypted, PASSPHRASE) == ""

    def test_roundtrip_special_characters(self):
        original = "p@$$w0rd!#%&*()"
        assert decrypt_value(encrypt_value(original, PASSPHRASE), PASSPHRASE) == original

    def test_different_passphrases_produce_different_ciphertext(self):
        enc1 = encrypt_value("value", "pass1")
        enc2 = encrypt_value("value", "pass2")
        assert enc1 != enc2

    def test_decrypt_wrong_passphrase_gives_wrong_result(self):
        encrypted = encrypt_value("secret", PASSPHRASE)
        result = decrypt_value(encrypted, "wrongpass")
        assert result != "secret"

    def test_decrypt_non_encrypted_raises(self):
        with pytest.raises(EncryptionError) as exc_info:
            decrypt_value("plaintext", PASSPHRASE)
        assert "not appear to be encrypted" in exc_info.value.message

    def test_decrypt_malformed_base64_raises(self):
        with pytest.raises(EncryptionError) as exc_info:
            decrypt_value("enc:!!not_valid_base64!!", PASSPHRASE)
        assert "base64" in exc_info.value.message


class TestEncryptDict:
    def test_encrypts_all_values_by_default(self):
        env = {"A": "foo", "B": "bar"}
        result = encrypt_dict(env, PASSPHRASE)
        assert result["A"].startswith("enc:")
        assert result["B"].startswith("enc:")

    def test_encrypts_only_specified_keys(self):
        env = {"SECRET": "val1", "PUBLIC": "val2"}
        result = encrypt_dict(env, PASSPHRASE, keys=["SECRET"])
        assert result["SECRET"].startswith("enc:")
        assert result["PUBLIC"] == "val2"

    def test_already_encrypted_values_skipped(self):
        env = {"A": "plain"}
        first = encrypt_dict(env, PASSPHRASE)
        second = encrypt_dict(first, PASSPHRASE)
        assert first["A"] == second["A"]

    def test_original_dict_not_mutated(self):
        env = {"A": "original"}
        encrypt_dict(env, PASSPHRASE)
        assert env["A"] == "original"


class TestDecryptDict:
    def test_decrypts_all_encrypted_values(self):
        env = {"A": "foo", "B": "bar"}
        encrypted = encrypt_dict(env, PASSPHRASE)
        decrypted = decrypt_dict(encrypted, PASSPHRASE)
        assert decrypted == env

    def test_non_encrypted_values_passed_through(self):
        env = {"A": encrypt_value("secret", PASSPHRASE), "B": "plain"}
        result = decrypt_dict(env, PASSPHRASE)
        assert result["A"] == "secret"
        assert result["B"] == "plain"

    def test_decrypts_only_specified_keys(self):
        env = {"A": encrypt_value("alpha", PASSPHRASE), "B": encrypt_value("beta", PASSPHRASE)}
        result = decrypt_dict(env, PASSPHRASE, keys=["A"])
        assert result["A"] == "alpha"
        assert result["B"].startswith("enc:")
