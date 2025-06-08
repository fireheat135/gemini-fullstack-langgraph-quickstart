"""Encryption utilities for sensitive data like API keys."""

import base64

from cryptography.fernet import Fernet

from .config import settings


def generate_encryption_key() -> str:
    """Generate a new encryption key."""
    return Fernet.generate_key().decode()


def get_encryption_key() -> bytes:
    """Get the encryption key from settings."""
    # Use SECRET_KEY for simplicity in development
    key = settings.SECRET_KEY.encode()
    key = key[:32].ljust(32, b'0')  # Ensure 32 bytes
    return base64.urlsafe_b64encode(key)


def encrypt_value(value: str) -> str:
    """Encrypt a string value."""
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        encrypted_value = fernet.encrypt(value.encode())
        return encrypted_value.decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt value: {str(e)}")


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt an encrypted string value."""
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        decrypted_value = fernet.decrypt(encrypted_value.encode())
        return decrypted_value.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt value: {str(e)}")


# Aliases for backward compatibility
encrypt_api_key = encrypt_value
decrypt_api_key = decrypt_value


def is_encryption_configured() -> bool:
    """Check if encryption is properly configured."""
    try:
        get_encryption_key()
        return True
    except ValueError:
        return False