"""Encryption utilities for sensitive data like API keys."""

import base64
from typing import str

from cryptography.fernet import Fernet

from .config import settings


def generate_encryption_key() -> str:
    """Generate a new encryption key."""
    return Fernet.generate_key().decode()


def get_encryption_key() -> bytes:
    """Get the encryption key from settings."""
    if not settings.ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY not set in environment variables")
    
    return settings.ENCRYPTION_KEY.encode()


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure storage."""
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        encrypted_key = fernet.encrypt(api_key.encode())
        return base64.b64encode(encrypted_key).decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt API key: {str(e)}")


def decrypt_api_key(encrypted_api_key: str) -> str:
    """Decrypt an API key for use."""
    try:
        key = get_encryption_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.b64decode(encrypted_api_key.encode())
        decrypted_key = fernet.decrypt(encrypted_bytes)
        return decrypted_key.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt API key: {str(e)}")


def is_encryption_configured() -> bool:
    """Check if encryption is properly configured."""
    try:
        get_encryption_key()
        return True
    except ValueError:
        return False