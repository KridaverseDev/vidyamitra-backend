from django.conf import settings
from django.db import models

from silicon.knowledge.models import Course, Document
from silicon.user.models import CustomUser


class QuestionDifficulty(models.TextChoices):
    EASY = "E", "Easy"
    MEDIUM = "M", "Medium"
    HARD = "H", "Hard"


class BloomsLevel(models.IntegerChoices):
    REMEMBERING = 1, "Remembering"
    UNDERSTANDING = 2, "Understanding"
    APPLYING = 3, "Applying"
    ANALYSING = 4, "Analysing"
    EVALUATING = 5, "Evaluating"
    CREATING = 6, "Creating"


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="labels_created",
    )

    def __str__(self):
        return self.name


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_outcome = models.IntegerField(blank=True, null=True)
    question = models.TextField(max_length=1024, verbose_name="Question")
    marks = models.IntegerField(verbose_name="Marks")
    validated = models.BooleanField(default=False)
    difficulty = models.CharField(
        choices=QuestionDifficulty.choices,
        default=QuestionDifficulty.MEDIUM,
        max_length=1,
    )
    blooms_level = models.IntegerField(choices=BloomsLevel.choices)
    image = models.ImageField(upload_to="question_images/", null=True, blank=True)
    image_description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="questions"
    )
    labels = models.ManyToManyField(Label, related_name="questions", blank=True)

    def __str__(self):
        return f"{self.question} (Course: {self.course})"


class FavoriteQuestion(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="favorites"
    )
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_questions",
    )
