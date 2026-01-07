from typing import Optional

from ninja import ModelSchema, Schema, Field

from silicon.knowledge.models import Document, Course
from silicon.user.schemas import AuthorStamp


class SchoolOut(Schema):
    id: int
    name: str
    is_active: bool


class CourseOut(Schema):
    id: int
    name: str
    course_code: str
    semester: int
    school: SchoolOut
    syllabus_document: Optional["SyllabusOut"] = None

    @staticmethod
    def resolve_syllabus_document(obj):
        if not obj.documents:
            return
        return obj.documents.filter(type=Document.SYLLABUS).first()

    class Meta:
        model = Course
        fields = "__all__"


class DocumentDetail(ModelSchema):
    created_by: AuthorStamp

    class Meta:
        model = Document
        fields = "__all__"


class SyllabusOut(ModelSchema):
    class Meta:
        model = Document
        fields = ["id", "name", "file"]
