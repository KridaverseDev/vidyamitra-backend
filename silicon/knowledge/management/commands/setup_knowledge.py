import csv
import requests
from django.core.management.base import BaseCommand
from silicon.knowledge.models import Course, School
from silicon.user.models import CustomUser
from django.db import transaction
from tqdm import tqdm


class Command(BaseCommand):
    help = "Ingest data from S3 CSV file URLs into School, Program, and Course models"

    s3_url = "https://reva-vidyamitra-dev.s3.ap-south-1.amazonaws.com/master-course-details/CourseData.csv"

    def fetch_csv_data(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()

    def handle(self, *args, **kwargs):
        user, created = CustomUser.objects.get_or_create(email="admin@vidyamitra.ai")
        self.stdout.write(f"Using user: {user.email}")

        with transaction.atomic():
            self.stdout.write("Ingesting Schools and Courses...")
            csv_data = csv.reader(self.fetch_csv_data(self.s3_url))
            next(csv_data)

            new_courses = []

            schools = {school.name: school for school in School.objects.all()}

            courses = set(
                Course.objects.select_related("school").values_list(
                    "name", "course_code", "school__name"
                )
            )

            for row in tqdm(csv_data, desc="Processing rows", unit="row"):
                csv_course_name, csv_course_code, csv_school_name = (
                    row[0].strip(),
                    row[1].strip(),
                    row[2].strip(),
                )

                if csv_school_name and csv_school_name not in schools:
                    school, _ = School.objects.get_or_create(
                        name=csv_school_name,
                        defaults={
                            "created_by": user,
                            "is_active": False,
                        },
                    )
                    schools[csv_school_name] = school

                # Process Course
                if (
                    csv_course_name,
                    csv_course_code,
                    csv_school_name,
                ) not in courses:
                    new_courses.append(
                        Course(
                            name=csv_course_name,
                            course_code=csv_course_code,
                            school=schools[csv_school_name],
                            semester=1,
                            created_by=user,
                            is_active=False,
                        )
                    )

            Course.objects.bulk_create(new_courses)
            self.stdout.write(f"{len(new_courses)} courses created.")

        self.stdout.write(self.style.SUCCESS("Data ingestion completed."))
