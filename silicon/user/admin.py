from django.contrib import admin
from django.apps import apps
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.contrib.auth.forms import UserChangeForm

# Register your models here.
from .models import CustomUser, UserAPIKey
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

Course = apps.get_model("knowledge", "Course")


class MyCoursesForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        widgets = {
            "my_courses": AutocompleteSelectMultiple(
                CustomUser.my_courses.field,
                admin.site,
                attrs={"style": "width: 600px"},
            ),
        }


@admin.register(CustomUser)
class CustomUserAdmin(DefaultUserAdmin):
    form = MyCoursesForm
    # autocomplete_fields = ["my_courses"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Courses"), {"fields": ("my_courses",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(UserAPIKey)
class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "is_active", "created_at", "updated_at")
    list_filter = ("provider", "is_active", "created_at")
    search_fields = ("user__username", "user__email", "provider")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "provider", "is_active")}),
        ("Encrypted Data", {"fields": ("encrypted_key",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    
    def has_change_permission(self, request, obj=None):
        # Only allow viewing encrypted key, not editing it directly
        return super().has_change_permission(request, obj)
