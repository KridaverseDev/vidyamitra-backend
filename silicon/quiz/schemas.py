from typing import Optional

from ninja import ModelSchema
from ninja.schema import Schema

from .models import Quiz


class GenerateQuiz(Schema):
    topic: str
    count: int
    query: str


class QuizOut(ModelSchema):
    class Meta:
        model = Quiz
        fields = "__all__"


class EditQuiz(Schema):
    question: str
    options: dict
    correct: str
