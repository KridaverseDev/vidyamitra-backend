import os
import re
import uuid
from enum import Enum
from io import BytesIO

import boto3
import markdown
import pptx
from django.conf import settings
from pptx.util import Pt

GENERATED_SLIDES_FOLDER = os.environ.get("GENERATED_SLIDES_FOLDER")
TEMPLATE_FOLDER = os.environ.get("TEMPLATE_FOLDER")


class SlideType(Enum):
    COVER = 0
    BASE = 1
    THANKYOU = 2


class GeneratePresentation:
    def new(self, prs_name: str):
        # Use template if available, otherwise create blank presentation
        if TEMPLATE_FOLDER and os.path.exists(TEMPLATE_FOLDER):
            self.presentation = pptx.Presentation(TEMPLATE_FOLDER)
        else:
            # Create a blank presentation if no template
            self.presentation = pptx.Presentation()
            # Add basic layouts if needed
            if len(self.presentation.slide_layouts) < 3:
                # Use default layouts
                pass
        self._cover_slide(prs_name)

    def new_slide(self, title, content):
        md = markdown.Markdown()
        html = md.convert(content)

        # Remove empty <li> and <ul> tags
        cleaned_html = re.sub(r"<li>\s*</li>", "", html)
        cleaned_html = re.sub(r"<ul>\s*</ul>", "", cleaned_html)
        cleaned_html = re.sub(
            r"<ul>(.*?)</ul>",
            lambda match: match.group(1) if re.search(r"<li>", match.group(1)) else "",
            cleaned_html,
            flags=re.DOTALL,
        )

        # Use appropriate slide layout
        try:
            if len(self.presentation.slide_layouts) > SlideType.BASE.value:
                self.base_slide_layout = self.presentation.slide_layouts[SlideType.BASE.value]
            else:
                # Use title and content layout (usually index 1) or blank
                self.base_slide_layout = self.presentation.slide_layouts[1] if len(self.presentation.slide_layouts) > 1 else self.presentation.slide_layouts[0]
        except:
            # Fallback to blank layout
            self.base_slide_layout = self.presentation.slide_layouts[6] if len(self.presentation.slide_layouts) > 6 else self.presentation.slide_layouts[0]
        
        slide = self.presentation.slides.add_slide(self.base_slide_layout)

        # Set slide title if placeholder exists
        if slide.shapes.title:
            slide.shapes.title.text = title
        else:
            # Add title as text box
            left = top = pptx.util.Inches(0.5)
            width = height = pptx.util.Inches(9)
            title_box = slide.shapes.add_textbox(left, top, width, height)
            title_frame = title_box.text_frame
            title_frame.text = title
            title_frame.paragraphs[0].font.size = Pt(30)
            title_frame.paragraphs[0].font.bold = True

        # Get body shape for content
        try:
            if len(slide.shapes.placeholders) > 1:
                body_shape = slide.shapes.placeholders[1]
            else:
                # Create text box for content if no placeholder
                left = top = pptx.util.Inches(0.5)
                width = height = pptx.util.Inches(9)
                body_shape = slide.shapes.add_textbox(left, top + pptx.util.Inches(1.5), width, height)
            tf = body_shape.text_frame
            tf.clear()
        except:
            # Fallback: create text box
            left = top = pptx.util.Inches(0.5)
            width = height = pptx.util.Inches(9)
            body_shape = slide.shapes.add_textbox(left, top + pptx.util.Inches(1.5), width, height)
            tf = body_shape.text_frame
            tf.clear()

        lines = html.split("\n")
        in_list = False
        level = 0

        for line in lines:
            line = line.strip()
            print(f"Processing line: '{line}'")

            # Detect and handle unordered list items and nesting
            if "<ul>" in line:
                in_list = True
                level += 1
            elif "</ul>" in line:
                in_list = False
                level -= 1
            elif "<li>" in line and in_list:
                # Create bullet point
                bullet = tf.add_paragraph()
                bullet.level = level - 1

                # Remove list tags and apply formatting only to the specific text
                line_content = re.sub(r"<li>|</li>", "", line).strip()
                print(f"Line content after processing: '{line_content}'")

                # Only add if line_content is not empty
                if line_content:
                    self._add_text_with_formatting(bullet, line_content)

            # Handle headings and subheadings
            elif "<h1>" in line:
                heading_text = re.sub(r"<.*?>", "", line).strip()
                if heading_text:  # Only add if not empty
                    heading = tf.add_paragraph()
                    heading.text = heading_text
                    heading.font.size = Pt(24)
                    heading.font.bold = True
            elif "<h2>" in line:
                subheading_text = re.sub(r"<.*?>", "", line).strip()
                if subheading_text:  # Only add if not empty
                    subheading = tf.add_paragraph()
                    subheading.text = subheading_text
                    subheading.font.size = Pt(20)
                    subheading.font.bold = True

            # Handle paragraph content without applying tags to the entire text
            elif "<p>" in line:
                para_content = re.sub(r"<p>|</p>", "", line).strip()
                if para_content:  # Only add if not empty
                    para = tf.add_paragraph()
                    self._add_text_with_formatting(para, para_content)

    def _add_text_with_formatting(self, paragraph, content):
        # Split content by bold and italic tags to handle specific formatting
        segments = re.split(r"(<.*?>)", content)
        bold = False
        italic = False

        for segment in segments:
            if segment == "<strong>" or segment == "<b>":
                bold = True
            elif segment == "</strong>" or segment == "</b>":
                bold = False
            elif segment == "<em>" or segment == "<i>":
                italic = True
            elif segment == "</em>" or segment == "</i>":
                italic = False
            elif segment.strip():  # Only add non-empty segments
                # Add each segment of text with the specified formatting
                run = paragraph.add_run()
                run.text = segment
                if bold:
                    run.font.bold = True
                if italic:
                    run.font.italic = True

    def _cover_slide(self, prs_name):
        # Use title slide layout (index 0) or blank layout if available
        try:
            if len(self.presentation.slide_layouts) > SlideType.COVER.value:
                first_slide_layout = self.presentation.slide_layouts[SlideType.COVER.value]
            else:
                first_slide_layout = self.presentation.slide_layouts[0]  # Use first available layout
            slide = self.presentation.slides.add_slide(first_slide_layout)
            # Set title if placeholder exists
            if slide.shapes.title:
                slide.shapes.title.text = prs_name
            else:
                # Add text box if no title placeholder
                left = top = width = height = pptx.util.Inches(1)
                text_box = slide.shapes.add_textbox(left, top, width, height)
                text_frame = text_box.text_frame
                text_frame.text = prs_name
                text_frame.paragraphs[0].font.size = Pt(44)
                text_frame.paragraphs[0].font.bold = True
        except Exception as e:
            # Fallback: create blank slide and add title
            blank_layout = self.presentation.slide_layouts[6] if len(self.presentation.slide_layouts) > 6 else self.presentation.slide_layouts[0]
            slide = self.presentation.slides.add_slide(blank_layout)
            left = top = width = height = pptx.util.Inches(1)
            text_box = slide.shapes.add_textbox(left, top, width, height)
            text_frame = text_box.text_frame
            text_frame.text = prs_name
            text_frame.paragraphs[0].font.size = Pt(44)
            text_frame.paragraphs[0].font.bold = True

    def _thank_you_slide(self):
        # Use thank you slide layout if available, otherwise use blank
        try:
            if len(self.presentation.slide_layouts) > SlideType.THANKYOU.value:
                last_slide_layout = self.presentation.slide_layouts[SlideType.THANKYOU.value]
            else:
                last_slide_layout = self.presentation.slide_layouts[0]  # Use first layout
            slide = self.presentation.slides.add_slide(last_slide_layout)
            # Add "Thank You" text
            if slide.shapes.title:
                slide.shapes.title.text = "Thank You"
            else:
                left = top = width = height = pptx.util.Inches(1)
                text_box = slide.shapes.add_textbox(left, top, width, height)
                text_frame = text_box.text_frame
                text_frame.text = "Thank You"
                text_frame.paragraphs[0].font.size = Pt(44)
                text_frame.paragraphs[0].font.bold = True
        except Exception as e:
            # Fallback: create blank slide with "Thank You"
            blank_layout = self.presentation.slide_layouts[6] if len(self.presentation.slide_layouts) > 6 else self.presentation.slide_layouts[0]
            slide = self.presentation.slides.add_slide(blank_layout)
            left = top = width = height = pptx.util.Inches(1)
            text_box = slide.shapes.add_textbox(left, top, width, height)
            text_frame = text_box.text_frame
            text_frame.text = "Thank You"
            text_frame.paragraphs[0].font.size = Pt(44)
            text_frame.paragraphs[0].font.bold = True

    def save(self, filename: str):
        """Save presentation to S3 and return file URL."""
        self._thank_you_slide()
        
        # Clean filename for file system
        safe_filename = re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')
        unique_id = uuid.uuid4().hex[:4]
        pptx_filename = f"{safe_filename}_{unique_id}.pptx"
        
        # Save the presentation to an in-memory buffer
        buffer = BytesIO()
        self.presentation.save(buffer)
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
            f"generated/presentations/{pptx_filename}",
        )
        
        # Generate the S3 file path (URL)
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/generated/presentations/{pptx_filename}"
        
        return {"file_path": file_url, "filename": pptx_filename}
