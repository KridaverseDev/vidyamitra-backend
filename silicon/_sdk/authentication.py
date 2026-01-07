import logging
import os
import secrets
from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.security import APIKeyHeader

from silicon._sdk.error_handler import ErrorMessage
from silicon.authentication.services import AuthenticationService

logger = logging.getLogger()

User = get_user_model()


class AuthenticationToken(APIKeyHeader):
    """Custom Auth to check the validity of firebase token in request
    header."""

    param_name = "Authorization"

    auth_service = AuthenticationService()

    def authenticate(self, request, key):
        # if testing then return the request.user object
        if settings.TESTING:
            return request.user

        if not key:
            raise HttpError(403, ErrorMessage.AUTH_ERR_103)
        return self.auth_service.authorize(request, key)

    def get_token_from_query(self, scope):
        """Get token from url query string.

        Args:
            scope (dict): Websocket Scope dict

        Raises:
            HttpError: 400, Invalid token

        Returns:
            str: extracted token
        """
        query = scope["query_string"].decode("utf-8")

        try:
            return query.split("=")[1]
        except Exception as ex:
            raise HttpError(400, ErrorMessage.AUTH_ERR_104) from ex


token_auth = AuthenticationToken()
