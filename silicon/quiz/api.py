from typing import Optional

from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI, api_controller, route
from ninja_extra.pagination import (
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
    paginate,
)

from silicon._sdk import authentication, permissions
from silicon.quiz.schemas import EditQuiz, GenerateQuiz, QuizOut

from .services import QuizService


@api_controller(
    "v1/quiz",
    tags=["Quiz"],
    auth=[authentication.token_auth],
    permissions=[permissions.IsAuthenticated],
)
class QuizAPI:
    def __init__(self) -> None:
        # Default service for methods that don't need user-specific API keys
        self.service = QuizService()
    
    def _get_service(self, user=None):
        """Get QuizService instance with user context for API key resolution."""
        return QuizService(user=user)

    @route.post(
        "/document/{document_id}",
        url_name="generate-quiz",
        response={201: PaginatedResponseSchema[QuizOut]},
        description="Generates quiz based on the user given details for the specified document.",
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def generate_quiz(self, request, document_id: int, payload: GenerateQuiz):
        user = request.auth

        """generate quiz for the topic and query."""
        service = self._get_service(user=user)  # Use user-specific service
        return service.generate_quiz(
            document_id=document_id, payload=payload, user=user
        )

    # Get API to list all the generated questions by topic
    @route.get(
        "/{topic}/questions",
        url_name="get-quizes",
        response={201: PaginatedResponseSchema[QuizOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_quiz_questions(self, topic: str):
        return self.service.list_quizes(topic=topic)

    # API to delete quiz questions by ID.
    @route.delete(
        "/delete-question/{question_id}",
        url_name="delete-question",
        response={204: None, 404: str},
        description="Deletes the question by ID given in path parameter",
    )
    def delete_quiz_question(
        self,
        question_id: int,
    ):
        try:
            self.service.delete_mcq_by_id(question_id=question_id)
            return 204, None
        except HttpError as e:
            return 404, str(e)

    # API to delete quiz
    @route.delete(
        "/delete-quiz/{topic}",
        url_name="delete-quiz",
        response={204: None, 404: str},
        description="Deletes the complete quiz",
    )
    def delete_quiz(
        self,
        topic: str,
    ):
        try:
            self.service.delete_quiz(topic=topic)
            return 204, None
        except HttpError as e:
            return 404, str(e)

    @route.put("/{question_id}/update", url_name="edit-quiz", response={204: None})
    def edit_quiz(self, question_id: int, payload: EditQuiz):
        self.service.edit_quiz(
            question_id=question_id,
            question=payload.question,
            options=payload.options,
            correct=payload.correct,
        )
        return 204, None

    @route.get(
        "/{topic}/export-moodle",
        url_name="export-moodle",
        response={200: dict, 404: str},
        description="Exports the quiz to Moodle format (XML) and provides a download link.",
    )
    def export_quiz_to_moodle(self, topic: str):
        try:
            return self.service.export_to_moodle(topic=topic)
        except HttpError as e:
            return 404, str(e)
