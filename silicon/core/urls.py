"""URL configuration for quiz project."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from knowledge.api import KnowledgeAPI
from ninja_extra import NinjaExtraAPI, api_controller, http_get
from questions.api import QuestionPaperAPI
from quiz.api import QuizAPI
from slides.api import PresentationAPI
from user.api import UserAPI

api = NinjaExtraAPI(
    title="vidyamitra",
    version="0.0.1",
    description="ai backend for reva university",
)

api.register_controllers(QuizAPI)
api.register_controllers(KnowledgeAPI)
api.register_controllers(PresentationAPI)
api.register_controllers(QuestionPaperAPI)
api.register_controllers(UserAPI)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", api.urls),
    re_path(r"static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
