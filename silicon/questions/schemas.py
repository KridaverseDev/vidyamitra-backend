from typing import Optional

from ninja import ModelSchema
from ninja.schema import Schema

from silicon.questions.models import FavoriteQuestion, Label, Question


class DifficultyDistribution(Schema):
    easy: int
    medium: int
    hard: int

    def __str__(self) -> str:
        return f"{self.easy} Easy questions, {self.medium} Medium questions, {self.hard} Hard questions"


class BloomsDistribution(Schema):
    l1: int  # Remembering
    l2: int  # Understanding
    l3: int  # Applying
    l4: int  # Analyzing
    l5: int  # Evaluating
    l6: int  # Creating

    def __str__(self) -> str:
        levels = {
            "Level 1 Questions": self.l1,
            "Level 2 Questions": self.l2,
            "Level 3 Questions": self.l3,
            "Level 4 Questions": self.l4,
            "Level 5 Questions": self.l5,
            "Level 6 Questions": self.l6,
        }
        # Filter out levels with count 0 and format as 'Lx=count'
        non_zero_levels = [
            f"{lvl}={count}" for lvl, count in levels.items() if count > 0
        ]

        # Join the non-zero levels with ', ' and return as string
        return ", ".join(non_zero_levels)


class GenerateQuestionPaperIn(Schema):
    question_ids: list[int]  # List of question IDs to be generated


class GenrateQuestionIn(Schema):
    syllabus_id: int
    document_id: int
    count: int
    user_prompt: str
    difficulty_distribution: DifficultyDistribution
    blooms_distribution: BloomsDistribution


class ValidateQuestionIn(Schema):
    question_ids: list[int]  # List of question IDs to be validated


class QuestionOut(ModelSchema):
    class Meta:
        model = Question
        fields = [
            "id",
            "course",
            "course_outcome",
            "question",
            "marks",
            "validated",
            "difficulty",
            "blooms_level",
            "created",
            "updated",
        ]


class DeleteQuestionIn(Schema):
    question_ids: list[int]


class UpdateQuestionIn(Schema):
    question_ids: list[int]


class UpdateQuestion(Schema):
    question: Optional[str] = None
    marks: Optional[int] = None
    difficulty: Optional[str] = None
    blooms_level: Optional[int] = None
    validated: Optional[bool] = None
    course_outcome: Optional[int] = None


class FavoriteQuestionIn(Schema):
    question_id: int


class FavoriteQuestionOut(ModelSchema):
    question: QuestionOut

    class Meta:
        model = FavoriteQuestion
        fields = ["id", "question"]


class AddQuestionIn(Schema):
    question: str
    marks: int
    difficulty: str
    blooms_level: int
    validated: bool
    course_outcome: int


class CreateLabelIn(Schema):
    name: str


class AddLabelToQuestionIn(Schema):
    question_id: int
    label_ids: list[int]


class LabelOut(ModelSchema):
    class Meta:
        model = Label
        fields = ["id", "name"]


class QuestionsByLabelIn(Schema):
    label_id: int
