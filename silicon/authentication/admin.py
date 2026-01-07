# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from django.contrib import admin
from django.contrib.auth import get_user_model

from silicon.authentication.models import FirebaseSocialAccount

User = get_user_model()


class FirebaseSocialAccountAdmin(admin.ModelAdmin):
    # override list_display too
    list_display = (
        "user",
        "provider_uid",
        "provider",
    )

    model = FirebaseSocialAccount


admin.site.register(FirebaseSocialAccount, FirebaseSocialAccountAdmin)
