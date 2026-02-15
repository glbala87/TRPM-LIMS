"""
Field-level encryption utilities for PHI (Protected Health Information).

Provides encryption and decryption utilities using the cryptography library
for secure storage of sensitive patient data in compliance with HIPAA
and other healthcare data protection regulations.
"""
import base64
import os
from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_encryption_key():
    """
    Retrieve or generate the encryption key from settings.

    The key should be stored securely in environment variables
    or a secrets management system in production.
    """
    # Try to get the key from settings
    key = getattr(settings, 'PHI_ENCRYPTION_KEY', None)

    if key is None:
        # Fall back to SECRET_KEY-derived key (not recommended for production)
        # In production, always set PHI_ENCRYPTION_KEY explicitly
        secret_key = settings.SECRET_KEY.encode()
        salt = getattr(settings, 'PHI_ENCRYPTION_SALT', b'trpm-lims-phi-salt')

        if isinstance(salt, str):
            salt = salt.encode()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key))
    elif isinstance(key, str):
        key = key.encode()

    return key


class FieldEncryptor:
    """
    Utility class for encrypting and decrypting field values.

    Uses Fernet symmetric encryption (AES-128-CBC with HMAC).
    """

    _instance = None
    _fernet = None

    def __new__(cls):
        """Singleton pattern to reuse the Fernet instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._fernet = Fernet(get_encryption_key())
        return cls._instance

    def encrypt(self, value):
        """
        Encrypt a string value.

        Args:
            value: The plaintext string to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        encrypted = self._fernet.encrypt(value.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_value):
        """
        Decrypt an encrypted string value.

        Args:
            encrypted_value: The base64-encoded encrypted string

        Returns:
            The original plaintext string
        """
        if encrypted_value is None:
            return None

        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode('utf-8'))
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception:
            # If decryption fails, return the original value
            # This handles migration from unencrypted to encrypted data
            return encrypted_value


class EncryptedTextField(models.TextField):
    """
    A TextField that automatically encrypts data before saving
    and decrypts when retrieving.

    Usage:
        class Patient(models.Model):
            ssn = EncryptedTextField(verbose_name="Social Security Number")
    """

    description = "An encrypted text field for storing PHI"

    def __init__(self, *args, **kwargs):
        self.encryptor = FieldEncryptor()
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Encrypt the value before saving to the database."""
        if value is None:
            return None
        return self.encryptor.encrypt(value)

    def from_db_value(self, value, expression, connection):
        """Decrypt the value when reading from the database."""
        if value is None:
            return None
        return self.encryptor.decrypt(value)

    def to_python(self, value):
        """Convert the value to a Python object."""
        if value is None:
            return None
        # Don't decrypt here as the value might already be decrypted
        return value


class EncryptedCharField(models.CharField):
    """
    A CharField that automatically encrypts data before saving
    and decrypts when retrieving.

    Note: The max_length should account for the encryption overhead.
    Encrypted values are approximately 1.5x the original length.

    Usage:
        class Patient(models.Model):
            phone = EncryptedCharField(max_length=500, verbose_name="Phone Number")
    """

    description = "An encrypted char field for storing PHI"

    def __init__(self, *args, **kwargs):
        self.encryptor = FieldEncryptor()
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Encrypt the value before saving to the database."""
        if value is None:
            return None
        return self.encryptor.encrypt(value)

    def from_db_value(self, value, expression, connection):
        """Decrypt the value when reading from the database."""
        if value is None:
            return None
        return self.encryptor.decrypt(value)

    def to_python(self, value):
        """Convert the value to a Python object."""
        if value is None:
            return None
        return value


def encrypt_value(value):
    """
    Convenience function to encrypt a value.

    Args:
        value: The plaintext string to encrypt

    Returns:
        Base64-encoded encrypted string
    """
    encryptor = FieldEncryptor()
    return encryptor.encrypt(value)


def decrypt_value(encrypted_value):
    """
    Convenience function to decrypt a value.

    Args:
        encrypted_value: The base64-encoded encrypted string

    Returns:
        The original plaintext string
    """
    encryptor = FieldEncryptor()
    return encryptor.decrypt(encrypted_value)


def generate_new_key():
    """
    Generate a new encryption key.

    Use this to generate a key for PHI_ENCRYPTION_KEY setting.
    Store the generated key securely!

    Returns:
        A base64-encoded Fernet key
    """
    return Fernet.generate_key().decode('utf-8')


class PHIMixin:
    """
    Mixin class that provides PHI encryption/decryption utilities
    for model classes.

    Usage:
        class Patient(PHIMixin, models.Model):
            _phi_fields = ['ssn', 'phone_number', 'email']
            ssn = models.CharField(max_length=500)
            phone_number = models.CharField(max_length=500)
            email = models.CharField(max_length=500)
    """

    _phi_fields = []
    _encryptor = None

    @classmethod
    def get_encryptor(cls):
        """Get or create the encryptor instance."""
        if cls._encryptor is None:
            cls._encryptor = FieldEncryptor()
        return cls._encryptor

    def encrypt_phi_fields(self):
        """Encrypt all PHI fields before saving."""
        encryptor = self.get_encryptor()
        for field_name in self._phi_fields:
            value = getattr(self, field_name, None)
            if value is not None and not self._is_encrypted(value):
                setattr(self, field_name, encryptor.encrypt(value))

    def decrypt_phi_fields(self):
        """Decrypt all PHI fields after loading."""
        encryptor = self.get_encryptor()
        for field_name in self._phi_fields:
            value = getattr(self, field_name, None)
            if value is not None:
                setattr(self, field_name, encryptor.decrypt(value))

    def _is_encrypted(self, value):
        """
        Check if a value appears to be already encrypted.
        This is a heuristic check based on the Fernet format.
        """
        if not isinstance(value, str):
            return False
        try:
            # Fernet tokens are base64 encoded and have a specific structure
            decoded = base64.urlsafe_b64decode(value.encode('utf-8'))
            return len(decoded) > 32  # Fernet tokens are at least 32 bytes
        except Exception:
            return False
