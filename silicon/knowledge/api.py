from typing import Optional

from django.shortcuts import get_object_or_404
from ninja import File, Form, UploadedFile
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI, api_controller, route
from ninja_extra.pagination import (
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
    paginate,
)

from silicon._sdk import authentication, permissions
from silicon.knowledge.schemas import CourseOut, DocumentDetail, SchoolOut
from silicon.knowledge.services import (
    CourseService,
    DocumentService,
    SchoolService,
)


# class based definition
@api_controller(
    "v1/knowledge",
    tags=["Knowledge"],
    auth=[authentication.token_auth],
    permissions=[permissions.IsAuthenticated],
)
class KnowledgeAPI:
    def __init__(self) -> None:
        self.course_service = CourseService()
        # DocumentService will be initialized per-request with user context
        self.school_service = SchoolService()
    
    def _get_document_service(self, user=None):
        """Get DocumentService instance with user context for API key resolution."""
        return DocumentService(user=user)

    """Api calls for School."""

    @route.get(
        "/schools",
        url_name="list-schools",
        response={200: PaginatedResponseSchema[SchoolOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_schools(self):
        return self.school_service.list_schools()

    """Api calls for Course."""

    @route.get(
        "/courses",
        url_name="list-courses",
        response={200: PaginatedResponseSchema[CourseOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_courses(self):
        return self.course_service.list_courses()

    @route.get(
        "/my-courses/",
        url_name="my-courses",
        response={200: PaginatedResponseSchema[CourseOut]},
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def my_courses(self, request):
        user = request.auth
        return self.course_service.my_courses(user)

    @route.get(
        "/courses/search",
        url_name="search-courses",
        response=PaginatedResponseSchema[CourseOut],
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def search_courses(self, name: str):
        return self.course_service.search_courses(name)

    """Api calls for Document."""

    @route.post(
        "/course/{course_id}/upload-document",
        url_name="upload-document",
        response={204: None},
    )
    def upload(
        self,
        request,
        name: str,
        course_id: int,
        is_syllabus: bool,
        document: UploadedFile = File(...),
    ):
        user = request.auth
        documents_service = self._get_document_service(user=user)
        documents_service.save_document(
            name, course_id, document, is_syllabus, user
        )

    @route.get(
        "/course/{id}/documents",
        url_name="list-documents",
        response=PaginatedResponseSchema[DocumentDetail],
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def list_documents(self, request, id: int):
        user = request.auth
        documents_service = self._get_document_service(user=user)
        return documents_service.list_documents(course_id=id)

    @route.get("/query", url_name="query-knowledge")
    def query(self, request, namespace: str, query: str):
        user = request.auth
        documents_service = self._get_document_service(user=user)
        return documents_service.query(namespace, query)

    @route.get(
        "/documents/search",
        url_name="search-document",
        response=PaginatedResponseSchema[DocumentDetail],
    )
    @paginate(PageNumberPaginationExtra, page_size=10)
    def search(self, request, namespace: str):
        user = request.auth
        documents_service = self._get_document_service(user=user)
        return documents_service.search_documents(namespace)

    @route.put(
        "/document/{document_id}", url_name="edit-document", response={204: None}
    )
    def edit_document(
        self,
        request,
        document_id: int,
        new_name: Optional[str] = None,
    ):
        user = request.auth
        documents_service = self._get_document_service(user=user)
        return documents_service.edit_document(
            document_id=document_id,
            new_name=new_name,
        )

    @route.delete(
        "/document/{document_id}", url_name="delete-document", response={204: None}
    )
    def delete_document(self, request, document_id: int) -> None:
        user = request.auth
        documents_service = self._get_document_service(user=user)
        return documents_service.delete_document(document_id)
