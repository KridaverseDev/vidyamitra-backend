import uuid
from enum import Enum
from io import BytesIO

import boto3
import requests
from django.conf import settings
from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Length, Pt
from docx.styles.style import ParagraphStyle
from docx.table import Table

from silicon.knowledge.models import Course


class IAVersion(Enum):
    IA1 = 1
    IA2 = 2


class IAPaperTemplate:
    ACAD_YEAR = "2024-2025"

    def template(self, course: Course):
        self.version = "1"
        self.course_name = course.name
        self.school = course.school.name
        self.program = ""
        self.course_code = course.course_code
        self.semester = course.semester
        self.new()
        self.logo()
        # self.title()
        self.course_info()
        self.note()
        self.create_questions_table()

    def new(self):
        self.document = Document()
        sections = self.document.sections
        for section in sections:
            section.top_margin = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin = Cm(2)
            section.right_margin = Cm(2)

    def logo(self):
        # URL of the logo image
        logo_url = "https://reva-vidyamitra.s3.ap-south-1.amazonaws.com/assets/logo.png"

        # Download the image from the URL
        response = requests.get(logo_url)
        if response.status_code == 200:
            logo_buffer = BytesIO(response.content)
            logo_buffer.seek(0)  # Reset buffer to the beginning

            # Add the logo to the document from the buffer
            paragraph = self.document.add_paragraph()
            run = paragraph.add_run()
            run.add_picture(logo_buffer, width=Inches(1.5))  # Add the logo from buffer
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            print("Failed to download the image. Status code:", response.status_code)

    def course_info(self):
        paragraph = self.document.add_paragraph()
        paragraph_format = paragraph.paragraph_format
        paragraph_format.space_after = Pt(0)
        paragraph_format.space_before = Pt(0)
        # Add course details point by point
        paragraph.add_run(f"School: {self.school}\n").bold = True
        paragraph.add_run(f"Program: {self.program}\n").bold = True
        paragraph.add_run(
            f"Academic Year: {self.ACAD_YEAR} (Semester: {self.semester})\n"
        ).bold = True
        paragraph.add_run(f"Course: {self.course_name}\n").bold = True
        paragraph.add_run(f"Course code: {self.course_code}\n").bold = True
        paragraph.add_run(f"Max Marks: 40\n").bold = True

        # Center align the paragraph
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # paragraph_format = paragraph.paragraph_format
        # paragraph_format.space_after = Cm(0)

    def note(self):
        paragraph = self.document.add_paragraph()
        paragraph.add_run(f"Note: Answer Any Four Full Question").bold = True
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        # table = self.document.add_table(1, 2)
        # set_table_borders(table)
        # table.rows[0].cells[0].text = "Note:"
        # table.rows[0].cells[0].width = Inches(1)
        # table.rows[0].cells[1].text = "Answer Any Four Full Questions"
        # table.rows[0].cells[1].width = Inches(5)

    def add_question(
        self,
        number: str,
        q: str,
        marks: str,
        blooms_level: str,
        co: str = None,
        image_path: str = None,
        image_description: str = None,
    ):
        # Add a new row for the question
        row = self.questions_table.add_row()

        # Fill in the question details
        row.cells[0].text = str(number)
        row.cells[1].text = q.strip()
        row.cells[2].text = str(marks)
        row.cells[3].text = str(blooms_level)
        row.cells[4].text = str(co)

        # Add an image if it's present
        if image_path:
            image_cell = row.cells[1]
            paragraph = image_cell.add_paragraph()
            image_full_path = f"{settings.MEDIA_ROOT}/{image_path}"
            run = paragraph.add_run()
            run.add_picture(image_full_path, width=Inches(3))

            if image_description:
                description_paragraph = image_cell.add_paragraph()
                description_paragraph.add_run(image_description)
                description_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    def create_questions_table(self):
        self.document.add_paragraph()
        table = self.document.add_table(1, 5)
        set_table_borders(table)

        table.rows[0].cells[0].text = "Q.No."
        table.rows[0].cells[0].width = Inches(0.75)

        table.rows[0].cells[1].text = "Questions"
        table.rows[0].cells[1].width = Inches(22)

        table.rows[0].cells[2].text = "Marks"
        table.rows[0].cells[2].width = Inches(0.5)

        table.rows[0].cells[3].text = "Bloom's Level"
        table.rows[0].cells[3].width = Inches(0.8)

        table.rows[0].cells[4].text = "CO"
        table.rows[0].cells[4].width = Inches(0.3)

        for row in table.rows:
            for cell in row.cells:
                paragraph = cell.paragraphs[0]
                paragraph_format = paragraph.paragraph_format
                paragraph_format.space_after = Pt(0)  # Reduce space after
                paragraph_format.space_before = Pt(0)
        self.questions_table = table
        return table

    def srn(self, table: Table):
        set_table_borders(table)

        # Fill the first column with "SRN" in bold text
        first_cell = table.cell(0, 0)
        paragraph = first_cell.add_paragraph()
        run = paragraph.add_run("SRN")
        run.bold = True

        # Align the paragraph in the first cell to the center
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Center-align the table on the page horizontally and top align vertically
        table.alignment = WD_TABLE_ALIGNMENT.RIGHT

    # def title(self):
    #     paragraph = self.document.add_paragraph()
    #     paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    #     run = paragraph.add_run(self.school)
    #     run.bold = True

    #     paragraph = self.document.add_paragraph()
    #     paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    #     run = paragraph.add_run(
    #         f"Semester {self.semester}  IA{self.version} Examination"
    #     )
    #     run.bold = True

    # {self.course_name}\nCourse Code: {self.course_code}

    # title = cell.add_paragraph()
    # title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    # title.add_run(f"IA{self.version} SCHEME AND SOLUTION").bold = True

    def header(self):
        base = f"{settings.BASE_DIR}/media/assets/"

        header_table = self.document.add_table(rows=1, cols=2)
        set_table_borders(header_table)

        # Add REVA image
        image_cell = header_table.cell(0, 0)
        paragraph = image_cell.add_paragraph()
        run = paragraph.add_run()
        run.add_picture(base + "logo.png", width=Inches(1))
        # Add course info
        info_cell = header_table.cell(0, 1)
        info_paragraph = info_cell.add_paragraph()
        info_run = info_paragraph.add_run()
        info_run.text = f"{self.school}\nCourse Name: {self.course_name}\nCourse Code: {self.course_code}\t\tSemester{self.semester}"
        info_run.bold = True

    def save(self):
        unique_id = uuid.uuid4().hex[:4]
        paper_name = (
            f"IA{self.version}_SEM{self.semester}_{self.course_code}_{unique_id}.docx"
        )

        # Save the document to an in-memory buffer
        buffer = BytesIO()
        self.document.save(buffer)
        buffer.seek(0)

        # Initialize S3 client
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION_NAME,
        )

        # Upload the file to S3
        s3_client.upload_fileobj(
            buffer,
            settings.AWS_STORAGE_BUCKET_NAME,
            f"generated/ia_papers/{paper_name}",
        )

        # Generate the S3 file path (URL)
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/generated/ia_papers/{paper_name}"

        return {"file_path": file_url}


# Function to set table borders
def set_table_borders(table):
    tbl = table._tbl  # Get the table XML element
    tblPr = tbl.tblPr  # Get the table properties element
    tblBorders = OxmlElement("w:tblBorders")

    for border_name in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "0")  # Size of the border
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "000000")  # Color of the border
        tblBorders.append(border)

    tblPr.append(tblBorders)
