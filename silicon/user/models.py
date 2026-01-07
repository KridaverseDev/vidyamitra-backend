from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    my_courses = models.ManyToManyField(
        "knowledge.Course", related_name="faculties", blank=True
    )

    class Meta(AbstractUser.Meta):
        verbose_name_plural = _("Users")
        swappable = "AUTH_USER_MODEL"
        indexes = [models.Index(fields=["username"])]

    def __str__(self):
        return str(self.username)

    @property
    def full_name(self):
        return self.get_full_name()


class UserAPIKey(models.Model):
    """Model to store encrypted API keys for users."""

    class Provider(models.TextChoices):
        OPENAI = "openai", "OpenAI"
        GEMINI = "gemini", "Google Gemini"
        GROK = "grok", "Grok (xAI)"

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="api_keys",
        help_text="User who owns this API key",
    )
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        help_text="API provider (OpenAI, Gemini, Grok)",
    )
    encrypted_key = models.TextField(
        help_text="Encrypted API key stored securely"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this API key is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User API Key"
        verbose_name_plural = "User API Keys"
        unique_together = [["user", "provider"]]
        indexes = [
            models.Index(fields=["user", "provider"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_provider_display()}"