# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from django.conf import settings

# sourcery skip: use-fstring-for-concatenation
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from ninja_extra import NinjaExtraAPI

from silicon.authentication.api import AuthenticationAPI
from silicon.knowledge.api import KnowledgeAPI
from silicon.questions.api import QuestionPaperAPI
from silicon.quiz.api import QuizAPI
from silicon.slides.api import PresentationAPI
from silicon.user.api import UserAPI

api = NinjaExtraAPI(
    title="Silicon AdminAPI",
    version="0.0.1",
    description="Silicon AdminAPI service",
    # csrf=True,
)


api.register_controllers(AuthenticationAPI)
api.register_controllers(UserAPI)
api.register_controllers(QuizAPI)
api.register_controllers(KnowledgeAPI)
api.register_controllers(PresentationAPI)
api.register_controllers(QuestionPaperAPI)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"", api.urls),
    re_path(r"__debug__", include("debug_toolbar.urls")),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
