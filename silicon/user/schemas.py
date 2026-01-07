# Create your schemas here.
from ninja import Schema


class AuthorStamp(Schema):
    id: int
    first_name: str


class APIKeyCreate(Schema):
    """Schema for creating/updating an API key."""
    provider: str  # "openai", "gemini", or "grok"
    api_key: str  # The actual API key (will be encrypted)
    
    class Config:
        # Allow extra validation
        extra = "forbid"


class APIKeyOut(Schema):
    """Schema for API key response (key is never returned, only metadata)."""
    id: int
    provider: str
    provider_display: str
    is_active: bool
    created_at: str
    updated_at: str