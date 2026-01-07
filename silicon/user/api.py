from ninja_extra import ControllerBase, api_controller, route
from ninja.errors import HttpError
from django.core.exceptions import ValidationError

from silicon._sdk import authentication, permissions
from silicon.authentication.schemas import AuthUserOut
from silicon.user import schemas, services


# API controller for managing question papers and related operations.
@api_controller(
    "v1/user",
    tags=["User"],
    auth=[authentication.token_auth],
    permissions=[permissions.IsAuthenticated],
)
class UserAPI(ControllerBase):
    @route.get("/me", url_name="me", response={200: AuthUserOut})
    def me(self, request):
        return request.auth

    @route.post(
        "/api-keys/",
        url_name="create-api-key",
        response={201: schemas.APIKeyOut},
    )
    def create_api_key(self, request, payload: schemas.APIKeyCreate):
        """Create or update an API key for the authenticated user."""
        try:
            # Validate payload
            if not payload.provider or not payload.provider.strip():
                raise HttpError(400, "Provider is required")
            if not payload.api_key or not payload.api_key.strip():
                raise HttpError(400, "API key is required")
            
            # Strip whitespace from both fields
            provider = payload.provider.strip()
            api_key = payload.api_key.strip()
            
            api_key_obj = services.UserAPIKeyService.create_or_update_api_key(
                user=request.auth,
                provider=provider,
                api_key=api_key,
            )
            
            return {
                "id": api_key_obj.id,
                "provider": api_key_obj.provider,
                "provider_display": api_key_obj.get_provider_display(),
                "is_active": api_key_obj.is_active,
                "created_at": api_key_obj.created_at.isoformat(),
                "updated_at": api_key_obj.updated_at.isoformat(),
            }
        except ValidationError as e:
            raise HttpError(400, str(e))
        except HttpError:
            raise
        except Exception as e:
            import traceback
            error_detail = str(e)
            # Log the full traceback for debugging
            print(f"Error creating API key: {error_detail}")
            print(traceback.format_exc())
            raise HttpError(400, f"Invalid request: {error_detail}")

    @route.get(
        "/api-keys/",
        url_name="list-api-keys",
        response={200: list[schemas.APIKeyOut]},
    )
    def list_api_keys(self, request):
        """List all API keys for the authenticated user."""
        api_keys = services.UserAPIKeyService.list_user_api_keys(user=request.auth)
        
        return [
            {
                "id": key.id,
                "provider": key.provider,
                "provider_display": key.get_provider_display(),
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat(),
                "updated_at": key.updated_at.isoformat(),
            }
            for key in api_keys
        ]

    @route.put(
        "/api-keys/{api_key_id}",
        url_name="update-api-key",
        response={200: schemas.APIKeyOut},
    )
    def update_api_key(self, request, api_key_id: int, payload: schemas.APIKeyCreate):
        """Update an existing API key."""
        try:
            # Validate payload
            if not payload.provider or not payload.provider.strip():
                raise HttpError(400, "Provider is required")
            if not payload.api_key or not payload.api_key.strip():
                raise HttpError(400, "API key is required")
            
            # Check if the API key exists and belongs to user
            from silicon.user.models import UserAPIKey
            try:
                existing_key = UserAPIKey.objects.get(id=api_key_id, user=request.auth)
            except UserAPIKey.DoesNotExist:
                raise HttpError(404, "API key not found")
            
            api_key_obj = services.UserAPIKeyService.create_or_update_api_key(
                user=request.auth,
                provider=payload.provider,
                api_key=payload.api_key,
            )
            
            return {
                "id": api_key_obj.id,
                "provider": api_key_obj.provider,
                "provider_display": api_key_obj.get_provider_display(),
                "is_active": api_key_obj.is_active,
                "created_at": api_key_obj.created_at.isoformat(),
                "updated_at": api_key_obj.updated_at.isoformat(),
            }
        except ValidationError as e:
            raise HttpError(400, str(e))
        except HttpError:
            raise
        except Exception as e:
            raise HttpError(400, f"Invalid request: {str(e)}")

    @route.delete(
        "/api-keys/{api_key_id}",
        url_name="delete-api-key",
        response={200: dict},
    )
    def delete_api_key(self, request, api_key_id: int):
        """Delete an API key."""
        deleted = services.UserAPIKeyService.delete_api_key(
            user=request.auth,
            api_key_id=api_key_id,
        )
        
        if not deleted:
            raise HttpError(404, "API key not found")
        
        return {"message": "API key deleted successfully"}

    @route.patch(
        "/api-keys/{api_key_id}/toggle",
        url_name="toggle-api-key",
        response={200: schemas.APIKeyOut},
    )
    def toggle_api_key(self, request, api_key_id: int):
        """Toggle the active status of an API key."""
        api_key_obj = services.UserAPIKeyService.toggle_api_key_status(
            user=request.auth,
            api_key_id=api_key_id,
        )
        
        if not api_key_obj:
            raise HttpError(404, "API key not found")
        
        return {
            "id": api_key_obj.id,
            "provider": api_key_obj.provider,
            "provider_display": api_key_obj.get_provider_display(),
            "is_active": api_key_obj.is_active,
            "created_at": api_key_obj.created_at.isoformat(),
            "updated_at": api_key_obj.updated_at.isoformat(),
        }
