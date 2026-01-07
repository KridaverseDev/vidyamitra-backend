from django.db import models

from silicon.user.models import CustomUser


class School(models.Model):
    name = models.CharField(max_length=512, verbose_name="school name")
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="school_created"
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=512, verbose_name="course name")
    course_code = models.CharField(max_length=512, verbose_name="course code")
    semester = models.IntegerField(verbose_name="semester")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="course_created"
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


def document_dir(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"knowledge/{filename}"


class Document(models.Model):
    SYLLABUS = "SYLLABUS"
    OTHER = "OTHER"
    DOC_TYPE = ((SYLLABUS, "Syllabus"), (OTHER, "Other"))

    namespace = models.CharField(max_length=512, verbose_name="vectorstore namespace")
    name = models.CharField(max_length=512, verbose_name="document name")
    file = models.FileField(upload_to=document_dir, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="documents"
    )
    type = models.CharField(choices=DOC_TYPE, default=OTHER, max_length=9)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="document_created",
    )

    def __str__(self):
        return self.name
