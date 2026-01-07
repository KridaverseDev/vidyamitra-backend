"""Services for user API key management."""

import os
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction

from silicon.user.models import CustomUser, UserAPIKey


class APIKeyEncryptionService:
    """Service for encrypting and decrypting API keys."""

    @staticmethod
    def _get_encryption_key():
        """Get or generate encryption key from settings."""
        # Use a secret key from settings, or generate one
        # In production, this should be in environment variables
        key = getattr(settings, "API_KEY_ENCRYPTION_KEY", None)
        
        if not key:
            # Generate a key (only for development - should be set in production)
            key = Fernet.generate_key()
            print(f"WARNING: Generated encryption key. Set API_KEY_ENCRYPTION_KEY in settings for production!")
        
        # If key is a string, convert to bytes
        if isinstance(key, str):
            key = key.encode()
        
        return key

    @staticmethod
    def encrypt(plaintext: str) -> str:
        """Encrypt an API key."""
        key = APIKeyEncryptionService._get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(plaintext.encode())
        return encrypted.decode()

    @staticmethod
    def decrypt(encrypted_text: str) -> str:
        """Decrypt an API key."""
        key = APIKeyEncryptionService._get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_text.encode())
        return decrypted.decode()


class UserAPIKeyService:
    """Service for managing user API keys."""

    @staticmethod
    def create_or_update_api_key(user: CustomUser, provider: str, api_key: str) -> UserAPIKey:
        """Create or update an API key for a user."""
        # Normalize provider to lowercase and strip whitespace
        provider = provider.lower().strip()
        
        # Strip API key to remove any leading/trailing whitespace or newlines
        api_key = api_key.strip()
        
        # Validate provider
        valid_providers = [choice[0] for choice in UserAPIKey.Provider.choices]
        if provider not in valid_providers:
            valid_list = ", ".join(valid_providers)
            raise ValidationError(
                f"Invalid provider '{provider}'. Must be one of: {valid_list}"
            )
        
        # Validate API key is not empty after stripping
        if not api_key:
            raise ValidationError("API key cannot be empty")

        # Encrypt the API key
        try:
            encrypted_key = APIKeyEncryptionService.encrypt(api_key)
        except Exception as e:
            raise ValidationError(f"Failed to encrypt API key: {str(e)}")

        # Create or update
        try:
            api_key_obj, created = UserAPIKey.objects.update_or_create(
                user=user,
                provider=provider,
                defaults={
                    "encrypted_key": encrypted_key,
                    "is_active": True,
                }
            )
        except Exception as e:
            # Check if it's a database error (table doesn't exist)
            error_msg = str(e)
            if "no such table" in error_msg.lower() or "relation" in error_msg.lower():
                raise ValidationError(
                    "Database table not found. Please run migrations: "
                    "python manage.py makemigrations user && python manage.py migrate"
                )
            raise ValidationError(f"Failed to save API key: {error_msg}")

        return api_key_obj

    @staticmethod
    def get_user_api_key(user: CustomUser, provider: str) -> str | None:
        """
        Get decrypted API key for a user and provider.
        Returns None if not found or not active.
        Falls back to environment variable if user key not found.
        """
        try:
            api_key_obj = UserAPIKey.objects.get(
                user=user,
                provider=provider,
                is_active=True
            )
            return APIKeyEncryptionService.decrypt(api_key_obj.encrypted_key)
        except UserAPIKey.DoesNotExist:
            # Fallback to environment variable
            env_key_map = {
                "openai": "OPENAI_API_KEY",
                "gemini": "GOOGLE_API_KEY",
                "grok": "GROK_API_KEY",
            }
            env_key_name = env_key_map.get(provider.lower())
            if env_key_name:
                return os.environ.get(env_key_name)
            return None

    @staticmethod
    def list_user_api_keys(user: CustomUser):
        """List all API keys for a user (without decrypted values)."""
        return UserAPIKey.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    def delete_api_key(user: CustomUser, api_key_id: int) -> bool:
        """Delete an API key. Returns True if deleted, False if not found."""
        try:
            api_key_obj = UserAPIKey.objects.get(id=api_key_id, user=user)
            api_key_obj.delete()
            return True
        except UserAPIKey.DoesNotExist:
            return False

    @staticmethod
    def toggle_api_key_status(user: CustomUser, api_key_id: int) -> UserAPIKey | None:
        """Toggle the active status of an API key."""
        try:
            api_key_obj = UserAPIKey.objects.get(id=api_key_id, user=user)
            api_key_obj.is_active = not api_key_obj.is_active
            api_key_obj.save()
            return api_key_obj
        except UserAPIKey.DoesNotExist:
            return None

