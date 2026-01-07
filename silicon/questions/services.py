from typing import List

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError

from silicon._sdk.authentication import User
from silicon.knowledge.models import Course, Document
from silicon.knowledge.services import DocumentService
from silicon.questions.ai.llm import QuestionPaperGeneratorLLM
from silicon.questions.models import FavoriteQuestion, Label, Question
from silicon.questions.paper_template.internals_paper import IAPaperTemplate
from silicon.questions.schemas import (
    AddQuestionIn,
    DeleteQuestionIn,
    GenrateQuestionIn,
    QuestionOut,
    UpdateQuestion,
    ValidateQuestionIn,
)
from silicon.user.models import CustomUser


class QuestionPaperService:
    def __init__(self, user=None) -> None:
        # Pass user to DocumentService for user-specific API keys
        self.document_service = DocumentService(user=user)
        self.service = QuestionPaperGeneratorLLM()
        self.course = Course()  # Ensure this is properly initialized

    def generate_question_paper(self, course_id: int, question_ids: list[int]):
        template = IAPaperTemplate()
        course = Course.objects.get(id=course_id)
        questions = Question.objects.filter(id__in=question_ids)

        template.template(course)

        for i, q in enumerate(questions):
            template.add_question(
                i + 1,
                q.question,
                q.marks,
                q.blooms_level,
                q.course_outcome,
                q.image,
                q.image_description,
            )

        return template.save()

    # Asynchronously generates questions for a course based on provided knowledge.
    def generate_questions(
        self,
        course_id: int,
        payload: GenrateQuestionIn,
        user: CustomUser,
        user_prompt: str,
    ):
        course = Course.objects.get(id=course_id)
        document = Document.objects.get(id=payload.document_id)
        syllabus = Document.objects.get(id=payload.syllabus_id)

        # query coursework from vectorstore
        course_context = self.document_service.multi_query(
            namespace=document.namespace,
            query="Suggest topics and its details that can be used to set question paper for internal exams",
        )
        print("Context Content:", course_context)

        # query syllabus from vectorstore
        syllabus_context = self.document_service.multi_query(
            namespace=syllabus.namespace,
            query="Get the course outcomes for the course.",
        )
        print("Syllabus Context Content:", syllabus_context)

        # Generate questions using the provided service.
        generated_questions = self.service.generate_questions(
            course=course.name,
            context=course_context["response"],
            syllabus_context=syllabus_context["response"],
            count=payload.count,
            user_prompt=user_prompt,
            difficulty_distribution=payload.difficulty_distribution.__str__(),
            blooms_distribution=payload.blooms_distribution.__str__(),
        )

        print(f"{generated_questions=}")

        questions = []
        for q in generated_questions["questions"]:
            questions_instance = Question.objects.create(
                course_id=course_id,
                marks=q["marks"],
                question=q["question"],
                difficulty=q["difficulty"],
                blooms_level=q["blooms_level"],
                course_outcome=q["course_outcome"],
                user=user,
            )

            questions_instance.save()

            questions.append(questions_instance)

        # Return the generated questions.
        return questions

    # Method to add a question manually
    def add_question_manually(
        self, course_id: int, payload: AddQuestionIn, user: CustomUser
    ):
        question = Question.objects.create(
            course_id=course_id,
            course_outcome=payload.course_outcome,
            question=payload.question,
            marks=payload.marks,
            difficulty=payload.difficulty,
            blooms_level=payload.blooms_level,
            user=user,
            validated=payload.validated,
        )
        return question

    def validate_question(self, payload: ValidateQuestionIn):
        for question_id in payload.question_ids:
            q = Question.objects.get(id=question_id)
            q.validated = True
            q.save()

    def invalidate_question(self, payload: ValidateQuestionIn):
        for question_id in payload.question_ids:
            q = Question.objects.get(id=question_id)
            q.validated = False
            q.save()

    def list_questions(self, course: int, is_valid: bool):
        return Question.objects.filter(course=course, validated=is_valid)

    def delete_question(self, payload: DeleteQuestionIn):
        for question_id in payload.question_ids:
            q = Question.objects.get(id=question_id)
            q.delete()

    def update_question(self, id: int, payload: UpdateQuestion):
        q = Question.objects.get(id=id)
        if payload.question is not None:
            q.question = payload.question
        if payload.marks is not None:
            q.marks = payload.marks
        if payload.difficulty is not None:
            q.difficulty = payload.difficulty
        if payload.blooms_level is not None:
            q.blooms_level = payload.blooms_level
        if payload.validated is not None:
            q.validated = payload.validated
        if payload.course_outcome is not None:
            q.course_outcome = payload.course_outcome
        q.save()
        return q

    def mark_favorite(self, question_id: int, user: User):  # type: ignore
        try:
            question = Question.objects.get(id=question_id)
            if not question.validated:
                raise ValidationError(
                    "Cannot mark an unvalidated question as favorite."
                )
        except Question.DoesNotExist:
            raise HttpError(404, "Question not found")

        favorite_exists = FavoriteQuestion.objects.filter(
            question=question, user=user
        ).exists()

        if favorite_exists:
            raise HttpError(400, "Question is already marked as favorite")

        favorite = FavoriteQuestion.objects.create(question=question, user=user)

        return favorite

    def remove_favorite(self, question_id: int, user_id=int):
        try:
            favorite = FavoriteQuestion.objects.get(
                question_id=question_id, user_id=user_id
            )
            favorite.delete()
            return True
        except FavoriteQuestion.DoesNotExist:
            raise HttpError(400, "The question is not marked as a favorite.")

    # List favorite questions
    def list_favorites(self, course: int, user: User):  # type: ignore
        return FavoriteQuestion.objects.filter(question__course=course).select_related(
            "question"
        )

    def create_label(self, name: str, user: CustomUser):
        if Label.objects.filter(name=name).exists():
            raise ValidationError(f"Label '{name}' already exists.")
        label = Label.objects.create(name=name, user=user)
        return label

    def add_labels_to_question(
        self, question_id: int, label_ids: list[int], user: CustomUser
    ):
        question = Question.objects.get(id=question_id)
        labels = Label.objects.filter(id__in=label_ids)

        if not labels.exists():
            raise ValidationError(
                f"No valid labels found for the provided label_ids: {label_ids}"
            )

        question.labels.add(*labels)
        return True

    def list_questions_by_label(self, label_id: int):
        label = Label.objects.get(id=label_id)
        return Question.objects.filter(labels=label)


class ImageService:
    @staticmethod
    def upload_image(question_id: int, image: UploadedFile, description: str = ""):
        question = get_object_or_404(Question, id=question_id)

        if not isinstance(image, UploadedFile):
            raise ValidationError("Invalid file upload.")

        file_name = default_storage.save(f"questions/{image.name}", image)

        question.image = file_name
        question.image_description = description
        question.save()

        return question
