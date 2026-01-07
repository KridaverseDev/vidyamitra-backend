"""Utility functions to get API keys for LLM services."""

import os
from typing import Optional

from django.conf import settings


def get_api_key_for_provider(user, provider: str) -> Optional[str]:
    """
    Get API key for a provider, checking user's keys first, then environment variables.
    
    Args:
        user: The authenticated user (or None)
        provider: One of "openai", "gemini", "grok"
    
    Returns:
        API key string or None if not found
    """
    # Try to get from user's API keys first
    if user and user.is_authenticated:
        try:
            from silicon.user.services import UserAPIKeyService
            user_key = UserAPIKeyService.get_user_api_key(user, provider)
            if user_key:
                return user_key
        except Exception:
            # If service not available or error, fall through to env vars
            pass
    
    # Fallback to environment variables
    env_key_map = {
        "openai": "OPENAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "grok": "GROK_API_KEY",
    }
    
    env_key_name = env_key_map.get(provider.lower())
    if env_key_name:
        return os.environ.get(env_key_name)
    
    return None

