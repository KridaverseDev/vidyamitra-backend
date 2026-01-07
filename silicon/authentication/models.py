from django.db import models
from ninja.errors import HttpError

from silicon.user.models import CustomUser


class FirebaseSocialAccountManager(models.Manager):
    def create_social_user(self, user: CustomUser, uid: str, provider: str):
        account = self.model(user=user, provider_uid=uid, provider=provider)
        account.save()
        return account

    def is_account_exists(self, provider, uid):
        """method to check if user exists for given provider and
        provider_pk."""
        return self.filter(provider=provider, provider_uid=uid).exists()

    def get_account(self, provider, uid):
        """method to check if user exists for given provider and
        provider_pk."""
        try:
            fb_use = self.select_related("user").get(
                provider=provider, provider_uid=uid
            )
            return fb_use.user

        except Exception as ex:
            print(f"Auth Error: {ex}")
            print(f">>> {provider=} || {uid=}")

            raise HttpError(401, "Invalid token or User does not exist") from ex


class FirebaseSocialAccount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    provider_uid = models.CharField(max_length=50)
    provider = models.CharField(max_length=20)

    objects: FirebaseSocialAccountManager = FirebaseSocialAccountManager()
