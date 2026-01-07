from typing import TYPE_CHECKING, Optional

from django.http import HttpRequest
from ninja_extra.permissions.base import SAFE_METHODS, BasePermission

from silicon.user.models import CustomUser

if TYPE_CHECKING:
    from ninja_extra.controllers.base import ControllerBase  # pragma: no cover


def get_request_user(request: HttpRequest) -> Optional[CustomUser]:
    if request_auth := getattr(request, "auth", None):
        return request_auth
    return getattr(request, "user", None)


class AllowAny(BasePermission):
    """Allow any access.

    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the
    intention more explicit.
    """

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        return True


class IsAuthenticated(BasePermission):
    """Allows access only to authenticated users."""

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        user = get_request_user(request)  # type: ignore
        return bool(user and user.is_authenticated)


class IsAdminUser(BasePermission):
    """Allows access only to admin users."""

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        user = get_request_user(request)  # type: ignore
        return bool(user and user.is_staff)  # type: ignore


class IsAuthenticatedOrReadOnly(BasePermission):
    """The request is authenticated as a user, or is a read-only request."""

    def has_permission(
        self, request: HttpRequest, controller: "ControllerBase"
    ) -> bool:
        user = get_request_user(request)  # type: ignore
        return bool(request.method in SAFE_METHODS or user and user.is_authenticated)
