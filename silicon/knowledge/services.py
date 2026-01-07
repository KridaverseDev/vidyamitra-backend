import os
import tempfile
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.shortcuts import aget_object_or_404, get_object_or_404
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from ninja import UploadedFile
from ninja.errors import HttpError

from silicon.knowledge.ai.llm import KnowledgeLLM
from silicon.knowledge.models import Course, Document, School
from silicon.knowledge.pinecone_client import PineconeClient
from silicon.user.models import CustomUser


class SchoolService:
    def list_schools(self):
        return School.objects.all().order_by("name")


class CourseService:

    def list_courses(self):
        return (
            Course.objects.prefetch_related(
                "documents",
            )
            .select_related(
                "school",
                "created_by",
            )
            .filter(is_active=True)
        )

    def my_courses(self, user: CustomUser):
        return (
            user.my_courses
            .prefetch_related("documents", "school")
            .select_related("school", "created_by")
            .filter(is_active=True)
            .all()
        )

    def search_courses(self, name: str):
        return (
            Course.objects.select_related(
                "school",
                "created_by",
            )
            .filter(name__icontains=name)
            .all()
        )


class DocumentService:
    def __init__(self, user=None) -> None:
        """
        Initialize DocumentService.
        
        Args:
            user: Authenticated user (optional) - for user-specific API keys
        """
        self.user = user
        self.llm = KnowledgeLLM(user=user)  # Pass user for API key resolution
        # Use OpenAI embeddings only
        self.vectorstore = PineconeClient(user=user, force_openai=True)

    def save_document(
        self, name: str, course_id: int, file: UploadedFile, is_syllabus: bool, user
    ):
        try:
            course = Course.objects.get(pk=course_id)
            doc = Document.objects.create(
                created_by=user,
                namespace=name,
                name=name,
                course=course,
                file=file,
                type=Document.SYLLABUS if is_syllabus else Document.OTHER,
            )
            
            # Ensure the file is saved and get the file path
            # Use doc.file.path for local file system, or handle URL for remote storage
            temp_file_created = False
            try:
                # Try to get the file path (works for local storage)
                file_path = doc.file.path
                if not os.path.exists(file_path):
                    raise ValueError("File path does not exist")
            except (ValueError, NotImplementedError, AttributeError):
                # If path is not available (e.g., using S3), save to temp file
                # Reset file pointer to beginning
                file.seek(0)
                
                # Create a temporary file
                file_extension = os.path.splitext(file.name)[1] if file.name else '.tmp'
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                try:
                    # Read the uploaded file content and write to temp file
                    file_content = file.read()
                    tmp_file.write(file_content)
                    file_path = tmp_file.name
                    temp_file_created = True
                finally:
                    tmp_file.close()
            
            # Create appropriate loader based on file type
            if file.name and file.name.lower().endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            elif file.name and file.name.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path)

            # Create vectorstore with user-specific API keys (OpenAI only)
            vectorstore = PineconeClient(user=user, force_openai=True)
            vectorstore.save(name, loader)
            
            # Clean up temporary file if it was created
            if temp_file_created:
                try:
                    if os.path.exists(file_path):
                        os.unlink(file_path)
                except Exception:
                    pass  # Ignore cleanup errors
                    
        except Exception as e:
            raise HttpError(400, str(e))

    def query(self, namespace: str, query: str):
        # Use user-specific vectorstore for queries (OpenAI only)
        vectorstore = PineconeClient(user=self.user, force_openai=True)
        result = vectorstore.search(namespace, query)
        return self.llm.explain(namespace, str(result), query)

    def multi_query(self, namespace: str, query: str):
        # Use user-specific vectorstore for queries (OpenAI only)
        vectorstore = PineconeClient(user=self.user, force_openai=True)
        result = vectorstore.query(namespace, query)
        return self.llm.explain(namespace, str(result), query)

    def delete_document(self, document_id: int):
        try:
            document = get_object_or_404(Document, id=document_id)
            namespace = document.namespace
            document.delete()
            to_delete = Document.objects.filter(namespace=namespace).exists()

            if not to_delete:
                self.vectorstore.delete_namespace(namespace)
        except Exception as e:
            raise HttpError(400, str(e))

    def list_documents(self, course_id: int):
        return (
            Document.objects
            .select_related("created_by")
            .filter(course_id=course_id)
            .order_by("-created")  # Order by creation date (newest first)
        )

    def search_documents(self, namespace: str):
        return (
            Document.objects.select_related("course", "created_by")
            .filter(name__icontains=namespace)
            .all()
        )

    def edit_document(self, document_id, new_name):
        document = Document.objects.get(pk=document_id)

        if new_name:
            document.name = new_name
        document.save()
