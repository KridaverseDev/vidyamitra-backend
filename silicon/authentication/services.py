import csv
import logging

import firebase_admin
from django import db
from django.contrib.auth import get_user_model
from firebase_admin import auth, credentials
from injector import inject
from ninja.errors import HttpError

from silicon._sdk.error_handler import ErrorMessage
from silicon.authentication.models import FirebaseSocialAccount
from silicon.authentication.schemas import FirebaseTokenIn

logger = logging.getLogger()


User = get_user_model()


class AuthenticationService:
    @inject
    def __init__(self) -> None:
        logger.info("---- Using AuthenticationService ----")

    def authorize(self, request, bearer_token: str):
        """Authorize wsgi client using firebase bearer token.

        Args:
            request (_type_): request object
            bearer_token (str): firebase_token
        """
        return self.firebase_login(bearer_token)

    def firebase_login(self, bearer_token: str):
        # decode the token from payload
        decoded_token, sign_in_provider, uid = self._validate_firebase_token(
            bearer_token
        )
        print(f">>> {decoded_token=}")

        # check account exists for provider_id and uid
        if FirebaseSocialAccount.objects.is_account_exists(
            uid=uid, provider=sign_in_provider
        ):
            # get already existing social account
            return FirebaseSocialAccount.objects.get_account(sign_in_provider, uid)

        return self._firebase_email_login(decoded_token, sign_in_provider, uid)

    def _firebase_email_login(self, decoded_token, sign_in_provider, uid):
        user_email = decoded_token.get("email")
        # filter user for decoded email
        user = User.objects.filter(email=user_email)

        # create new account if user doesn't exist
        if not user.exists():
            return self._create_new_account(
                user_email, decoded_token, sign_in_provider, uid
            )

        return user.first()

    def _create_new_account(self, user_email: str, decoded_token, provider_id, uid):
        user = User.objects.create(
            username=user_email.split("@")[0],
            email=user_email,
            first_name=decoded_token.get("name"),
        )
        if not FirebaseSocialAccount.objects.is_account_exists(provider_id, uid):
            FirebaseSocialAccount.objects.create_social_user(
                user=user,
                uid=uid,
                provider=provider_id,
            )
        return user

    @staticmethod
    def _validate_firebase_token(bearer_token: str):
        """Validate firebase token and return token, provider_id and uid.

        Args:
            bearer_token (str): firebase id token

        Raises:
            HttpError: 401, Token Expired
            HttpError: 403, Firebase token not valid
            HttpError: 500, Invalid token

        Returns:
            _type_: _description_
        """
        try:
            decoded_token = auth.verify_id_token(bearer_token)
        except firebase_admin._token_gen.ExpiredIdTokenError as e:
            raise HttpError(401, ErrorMessage.AUTH_ERR_100) from e
        except firebase_admin._auth_utils.InvalidIdTokenError as e:
            logger.error(e)
            raise HttpError(403, ErrorMessage.AUTH_ERR_101) from e

        if not bearer_token or not decoded_token:
            raise HttpError(403, ErrorMessage.AUTH_ERR_102)

        try:
            uid = decoded_token.get("uid")
            sign_in_provider = decoded_token.get("firebase").get("sign_in_provider")
        except Exception as exc:
            raise HttpError(500, ErrorMessage.AUTH_ERR_105) from exc

        return decoded_token, sign_in_provider, uid
