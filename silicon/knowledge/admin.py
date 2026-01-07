from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

# Register your models here.
from .models import Course, Document, School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    actions = ["make_active"]

    @admin.action(description="Mark selected school as active")
    def make_active(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "course__name", "created"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["name", "course_code", "is_active"]
    list_filter = ["is_active", "school__name"]
    search_fields = ["name", "course_code"]

    actions = ["make_active"]

    @admin.action(description="Mark selected cources as active")
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet[Any], search_term: str
    ) -> tuple[QuerySet[Any], bool]:

        # Check if the request is for the autocomplete and return only active courses
        if (
            request.resolver_match
            and request.resolver_match.app_name == "admin"
            and request.resolver_match.url_name == "autocomplete"
        ):
            queryset, use_distinct = super().get_search_results(
                request, queryset, search_term
            )
            queryset = queryset.filter(is_active=True)
            return queryset, use_distinct

        return super().get_search_results(request, queryset, search_term)
