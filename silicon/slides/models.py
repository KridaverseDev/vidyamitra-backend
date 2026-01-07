from django.conf import settings
from django.db import models
from markdownfield.models import MarkdownField

from silicon.knowledge.models import Course


class Presentation(models.Model):
    """Model representing a  **Presentation**.\n."""

    title = models.CharField(max_length=250)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    query = models.CharField(max_length=1000)
    created = models.DateField(auto_now=False, auto_now_add=True)
    updated = models.DateField(auto_now=True, auto_now_add=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="presentation_author",
    )

    def __str__(self):
        return self.title


class Slides(models.Model):
    """Model to store slide of a presentation."""

    title = models.CharField(max_length=250)
    content = MarkdownField()
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    updated = models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.title


class Favorite(models.Model):
    ppt = models.ForeignKey(
        Presentation, related_name="favorite_presentation", on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_author",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ppt", "user"],
                name="secondary_key",
                violation_error_message="This presentation is already marked as favorite",
            )
        ]
