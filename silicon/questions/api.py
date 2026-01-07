from typing import Optional
from io import BytesIO
import requests

from django.contrib.auth import aget_user
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse
from ninja import File, Form, UploadedFile
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI, api_controller, route
from ninja_extra.pagination import (
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
    paginate,
)

from silicon._sdk import authentication, permissions
from silicon._sdk.error_handler import ErrorMessage, error_handler
from silicon.knowledge.models import Course
from silicon.knowledge.schemas import DocumentDetail
from silicon.questions.models import FavoriteQuestion, Label, Question
from silicon.questions.paper_template.internals_paper import IAPaperTemplate
from silicon.questions.schemas import (
    AddLabelToQuestionIn,
    AddQuestionIn,
    CreateLabelIn,
    DeleteQuestionIn,
    FavoriteQuestionIn,
    FavoriteQuestionOut,
    GenerateQuestionPaperIn,
    GenrateQuestionIn,
    LabelOut,
    QuestionOut,
    QuestionsByLabelIn,
    UpdateQuestion,
    ValidateQuestionIn,
)
from silicon.questions.services import ImageService, QuestionPaperService
from silicon.user.models import CustomUser


# API controller for managing question papers and related operations.
@api_controller(
    "v1/question",
    tags=["Question Bank"],
    auth=[authentication.token_auth],
    permissions=[permissions.IsAuthenticated],
)
class QuestionPaperAPI:
    def __init__(self) -> None:
        # Default service for methods that don't need user-specific API keys
        self.service = QuestionPaperService()
    
    def _get_service(self, user=None):
        """Get QuestionPaperService instance with user context for API key resolution."""
        return QuestionPaperService(user=user)

    # Route to generate a question paper for a specific course.
    @route.post(
        "/paper/course/{id}",
        url_name="generate-paper",
        description="Generates a question paper for the specified course ID and returns a downloadable DOCX file.",
    )
    @error_handler
    def generate_question_paper(
        self, request, id: int, payload: GenerateQuestionPaperIn
    ):
        """
        Generate a question paper as a DOCX file and return it for download.
        
        Returns:
            HttpResponse with DOCX file attachment
        """
        try:
            service = self._get_service(user=request.auth)
            result = service.generate_question_paper(id, payload.question_ids)
            
            # result is a dict with "file_path" containing S3 URL
            file_url = result.get("file_path")
            
            if not file_url:
                raise HttpError(500, "Failed to generate question paper file")
            
            # Download the file from S3 URL
            response = requests.get(file_url)
            if response.status_code != 200:
                raise HttpError(500, f"Failed to download generated file from S3: {response.status_code}")
            
            # Extract filename from URL
            filename = file_url.split("/")[-1]
            
            # Create HTTP response with file
            http_response = HttpResponse(
                response.content,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            http_response["Content-Disposition"] = f'attachment; filename="{filename}"'
            http_response["Content-Length"] = len(response.content)
            
            return http_response
            
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except requests.RequestException as e:
            raise HttpError(500, f"Failed to download file: {str(e)}")
        except Exception as e:
            raise HttpError(500, f"Error generating question paper: {str(e)}")

    # Route to generate questions for a specific course using provided input.
    @route.post(
        "/course/{id}",
        url_name="generate-questions",
        response={201: PaginatedResponseSchema[QuestionOut]},
        description="Generates a question based on the user given details for the specified course ID.",
    )
    @error_handler
    @paginate(PageNumberPaginationExtra, page_size=25)
    def genrate_questions(self, request, id: int, payload: GenrateQuestionIn):
        user = request.auth
        user_prompt = payload.user_prompt
        try:
            service = self._get_service(user=user)
            return service.generate_questions(
                course_id=id, payload=payload, user=user, user_prompt=user_prompt
            )
        except ObjectDoesNotExist as e:
            raise HttpError(404, f"Resource not found: {str(e)}")
        except ValidationError as e:
            raise HttpError(400, f"Validation error: {str(e)}")
        except ValueError as e:
            # Catch API key errors and other value errors
            error_msg = str(e)
            if "API key" in error_msg or "key not found" in error_msg.lower():
                raise HttpError(400, f"API key error: {error_msg}. Please add your API key via POST /v1/user/api-keys/")
            raise HttpError(400, f"Invalid input: {error_msg}")
        except KeyError as e:
            # Catch missing keys in response (e.g., "response" key missing)
            raise HttpError(500, f"Unexpected response format: Missing key '{str(e)}'. Please check backend logs.")
        except Exception as e:
            # Log the full error for debugging
            import traceback
            error_detail = str(e)
            # Provide more helpful error messages for common issues
            if "namespace" in error_detail.lower() or "not found" in error_detail.lower():
                raise HttpError(404, f"Document namespace not found. Please ensure documents are uploaded and processed. Error: {error_detail}")
            elif "pinecone" in error_detail.lower():
                raise HttpError(500, f"Pinecone error: {error_detail}. Check PINECONE_API_KEY and PINECONE_INDEX_NAME.")
            elif "openai" in error_detail.lower() or "gpt" in error_detail.lower():
                raise HttpError(500, f"OpenAI API error: {error_detail}. Check your OpenAI API key.")
            elif "gemini" in error_detail.lower() or "google" in error_detail.lower():
                raise HttpError(500, f"Gemini API error: {error_detail}. Check your Gemini API key.")
            else:
                # Generic error with more detail
                raise HttpError(500, f"Internal server error: {error_detail}. Check backend logs for details.")

    @route.post(
        "/add/",
        url_name="add-question",
        response={201: QuestionOut},
        description="Add a question manually.",
    )
    def add_question(self, request, course_id: int, payload: AddQuestionIn):
        user = request.auth
        try:
            service = self._get_service(user=user)
            question = service.add_question_manually(
                payload=payload, course_id=course_id, user=user
            )
            return question
        except ValidationError as e:
            raise HttpError(400, str(ErrorMessage.QUESTION_ERR_03))
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    # Route to validate a list of questions by their IDs.
    @route.post("/validate/", url_name="validate-question", response={200: dict})
    def validate_question(self, request, payload: ValidateQuestionIn):
        """
        Validate questions by setting their validated field to True.
        
        Returns:
            {"message": "Questions validated successfully", "count": number_of_questions}
        """
        try:
            self.service.validate_question(payload=payload)
            return {
                "message": "Questions validated successfully",
                "count": len(payload.question_ids)
            }
        except ObjectDoesNotExist as e:
            raise HttpError(404, f"Question not found: {str(e)}")
        except Exception as e:
            raise HttpError(500, f"Error validating questions: {str(e)}")

    # Route to invalidate a list of questions by their IDs.
    @route.post("/invalidate/", url_name="invalidate-question", response={200: dict})
    def invalidate_question(self, request, payload: ValidateQuestionIn):
        """
        Invalidate questions by setting their validated field to False.
        
        Returns:
            {"message": "Questions invalidated successfully", "count": number_of_questions}
        """
        try:
            self.service.invalidate_question(payload=payload)
            return {
                "message": "Questions invalidated successfully",
                "count": len(payload.question_ids)
            }
        except ObjectDoesNotExist as e:
            raise HttpError(404, f"Question not found: {str(e)}")
        except Exception as e:
            raise HttpError(500, f"Error invalidating questions: {str(e)}")

    # Route to list questions for a specific course with pagination.

    @route.get(
        "/course/{course_id}/questions",
        url_name="list-questions",
        response={200: PaginatedResponseSchema[QuestionOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_questions(
        self, request, course_id: int, is_valid: bool = True
    ) -> PaginatedResponseSchema[QuestionOut]:
        try:
            return self.service.list_questions(course=course_id, is_valid=is_valid)
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    # Route to delete a specific question by its ID.
    @route.delete("/delete", url_name="delete-question", response={201: None})
    def delete_question(self, payload: DeleteQuestionIn) -> None:
        try:
            self.service.delete_question(payload=payload)
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    # Route to update a specific question by its ID.
    @route.put("/{id}", url_name="update-question", response={201: None})
    def update_questions(self, id: int, payload: UpdateQuestion):
        try:
            return self.service.update_question(id, payload=payload)
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except ValidationError as e:
            raise HttpError(400, ErrorMessage.QUESTION_ERR_03)
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    @route.post("/question/{id}/upload_image/")
    @error_handler
    def upload_image(
        self, id: int, image: UploadedFile = File(...), description: str = Form(...)
    ):
        try:
            # Call your ImageService to handle the upload
            question = ImageService.upload_image(id, image, description)
            return {
                "message": "Image and description uploaded successfully",
                "question_id": id,
                "image_url": question.image.url,
                "description": question.image_description,
            }
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except ValidationError as e:
            raise HttpError(400, str(ErrorMessage.QUESTION_ERR_03))
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    # Route to mark favorites question by its ID.
    @route.post(
        "/{id}/favorite", url_name="mark-favorite", response={201: FavoriteQuestionOut}
    )
    @error_handler
    def mark_favorite_question(self, request, id: int):
        user = request.auth
        try:
            return self.service.mark_favorite(question_id=id, user=user)
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except ValidationError as e:
            raise HttpError(400, str(ErrorMessage.QUESTION_ERR_03))
        except HttpError as e:
            raise
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    # Route to remove favorites question by its ID.
    @route.delete("/{id}/favorite", url_name="remove-favorite", response={204: None})
    @error_handler
    def remove_favorite_question(self, request, id: int):
        user = request.auth
        self.service.remove_favorite(question_id=id, user_id=user.id)

    @route.get(
        "/favorites/",
        url_name="list-favorites",
        response={200: PaginatedResponseSchema[FavoriteQuestionOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_favorite_questions(
        self, request, course: Optional[int] = None
    ) -> PaginatedResponseSchema[FavoriteQuestionOut]:
        user = request.auth
        try:
            favorites = self.service.list_favorites(course=course, user=user)
            return favorites
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))

    # Route to create a new label.
    @route.post(
        "/labels/",
        url_name="create-label",
        response={201: LabelOut},
        description="Create a new label.",
    )
    def create_label(self, request, payload: CreateLabelIn):
        user = request.auth
        try:
            label_name = payload.name
            label = self.service.create_label(label_name, user)
            return label
        except ValidationError as e:
            raise HttpError(400, str(ErrorMessage.QUESTION_ERR_03))
        except Exception as e:
            raise HttpError(500, str(e))

    # Route to list all labels.
    @route.get("/labels/", url_name="list-labels", response={200: list[LabelOut]})
    def list_labels(self, request) -> list[LabelOut]:
        try:
            return Label.objects.all()
        except Exception as e:
            raise HttpError(500, str(e))

    # Route to add a label to a specific question by its ID.
    @route.post("/add_label/", url_name="add-label-to-question")
    def add_labels_to_question(self, request, payload: AddLabelToQuestionIn):
        user = request.auth
        try:
            return self.service.add_labels_to_question(
                question_id=payload.question_id, label_ids=payload.label_ids, user=user
            )
        except ValidationError as e:
            raise HttpError(400, str(ErrorMessage.QUESTION_ERR_03))
        except Exception as e:
            raise HttpError(500, str(e))

    # Route to list questions by a specific label.
    @route.get(
        "/labels/{label_id}/questions",
        url_name="list-questions-by-label",
        response={200: PaginatedResponseSchema[QuestionOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_questions_by_label(
        self, request, label_id: int
    ) -> PaginatedResponseSchema[QuestionOut]:
        try:
            return self.service.list_questions_by_label(label_id=label_id)
        except ObjectDoesNotExist:
            raise HttpError(404, ErrorMessage.QUESTION_ERR_01)
        except Exception as e:
            raise HttpError(500, str(ErrorMessage.QUESTION_ERR_02))
