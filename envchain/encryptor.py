"""Simple symmetric encryption/decryption for sensitive env values."""

import base64
import hashlib
import os
from typing import Dict, Optional


class EncryptionError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from a passphrase using SHA-256."""
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


def encrypt_value(value: str, passphrase: str) -> str:
    """Encrypt a single string value using XOR + base64 encoding.

    Returns a base64-encoded encrypted string prefixed with 'enc:'.
    """
    key = _derive_key(passphrase)
    value_bytes = value.encode("utf-8")
    # Use repeating key XOR
    encrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(value_bytes))
    encoded = base64.b64encode(encrypted).decode("utf-8")
    return f"enc:{encoded}"


def decrypt_value(value: str, passphrase: str) -> str:
    """Decrypt a value previously encrypted with encrypt_value.

    Raises EncryptionError if the value is not in the expected format.
    """
    if not value.startswith("enc:"):
        raise EncryptionError(f"Value does not appear to be encrypted: {value!r}")
    encoded = value[4:]
    try:
        encrypted = base64.b64decode(encoded.encode("utf-8"))
    except Exception as exc:
        raise EncryptionError(f"Failed to base64-decode encrypted value: {exc}") from exc
    key = _derive_key(passphrase)
    decrypted = bytes(b ^ key[i % len(key)] for i, b in enumerate(encrypted))
    return decrypted.decode("utf-8")


def encrypt_dict(
    env: Dict[str, str],
    passphrase: str,
    keys: Optional[list] = None,
) -> Dict[str, str]:
    """Encrypt selected (or all) keys in an env dict.

    If keys is None, all values are encrypted.
    Already-encrypted values (prefixed 'enc:') are left as-is.
    """
    result = dict(env)
    targets = keys if keys is not None else list(env.keys())
    for k in targets:
        if k in result and not result[k].startswith("enc:"):
            result[k] = encrypt_value(result[k], passphrase)
    return result


def decrypt_dict(
    env: Dict[str, str],
    passphrase: str,
    keys: Optional[list] = None,
) -> Dict[str, str]:
    """Decrypt selected (or all) encrypted keys in an env dict.

    Non-encrypted values are passed through unchanged.
    """
    result = dict(env)
    targets = keys if keys is not None else list(env.keys())
    for k in targets:
        if k in result and result[k].startswith("enc:"):
            result[k] = decrypt_value(result[k], passphrase)
    return result
