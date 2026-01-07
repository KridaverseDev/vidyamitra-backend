# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).
import os

__VERSION__ = "v0.1.0"


__APP_MODE__ = os.environ.get("APP_MODE", "local")

print(f"{__APP_MODE__=}")
if __APP_MODE__ in ("LOCAL", "local"):
    from silicon._settings.local import *  # noqa: F403
if __APP_MODE__ in ("DEV", "dev"):
    from silicon._settings.development import *  # noqa: F403
elif __APP_MODE__ in ("PROD", "prod"):
    from silicon._settings.production import *  # type: ignore # noqa: F403


ROOT_URLCONF = "silicon._microservices.admin.urls"
