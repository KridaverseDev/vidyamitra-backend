import os
from io import BytesIO
from typing import Optional

import boto3
from django.conf import settings
from django.shortcuts import get_object_or_404
from moodlexport.python_to_moodle import Category, Question
from ninja.errors import HttpError

from silicon.knowledge.models import Document
from silicon.knowledge.services import DocumentService
from silicon.quiz.ai.llm import QuizGeneratorLLM
from silicon.quiz.schemas import GenerateQuiz
from silicon.user.models import CustomUser

from .models import Quiz


class QuizService:
    def __init__(self, user=None) -> None:
        """
        Initialize QuizService with optional user for API key resolution.
        
        Args:
            user: CustomUser instance (optional) - for user-specific API keys
        """
        self.user = user
        self.llm = QuizGeneratorLLM(user=user)  # Pass user for API key resolution
        self.knowledge = DocumentService(user=user)  # Pass user for API key resolution

    def generate_quiz(self, document_id: int, payload: GenerateQuiz, user: CustomUser):
        doc = get_object_or_404(Document, pk=document_id)
        topic = self.updated_topic(payload.topic)

        context = self.knowledge.multi_query(
            namespace=doc.namespace,
            query="Suggest topics and its details that can be used to set MCQ quiz to assess students.",
        )
        print("Context Content:", context)

        generated_quiz = self.llm.generate(
            topic=topic,
            count=payload.count,
            context=context["response"],
        )

        print(f"{generated_quiz=}")

        quiz_ids = []
        if "quizzes" in generated_quiz:
            for q in generated_quiz["quizzes"]:
                quiz_instance = Quiz.objects.create(
                    topic=topic,
                    question=q["question"],
                    options={
                        "option_a": q["option_a"],
                        "option_b": q["option_b"],
                        "option_c": q["option_c"],
                        "option_d": q["option_d"],
                    },
                    correct=q["correct"],
                    users=user,
                )
                quiz_ids.append(quiz_instance.id)
                print(f"Created Quiz Instance: {quiz_instance}")

        else:
            print("No quizzes generated. Check the structure of generated_quiz.")

        # Return QuerySet for pagination (ordered by creation date, newest first)
        if quiz_ids:
            return Quiz.objects.filter(id__in=quiz_ids).order_by("-created")
        else:
            return Quiz.objects.none()

    def updated_topic(self, topic: str) -> str:
        """Normalize topic: lowercase, replace spaces/underscores with hyphens."""
        return "-".join(topic.lower().replace(" ", "-").replace("_", "-").split())

    def list_quizes(self, topic: str):
        updated_topic = self.updated_topic(topic)
        # Use case-insensitive filter to handle both old (uppercase) and new (lowercase) topics
        return Quiz.objects.filter(topic__iexact=updated_topic).order_by("-created")

    def delete_mcq_by_id(self, question_id: int):
        question = get_object_or_404(Quiz, pk=question_id)
        question.delete()
        print(f"Deleted Quiz Question ID: {question_id}")

    def delete_quiz(self, topic: str):
        topic = self.updated_topic(topic)
        # Use case-insensitive filter for consistency
        quizes = Quiz.objects.filter(topic__iexact=topic)
        quizes.delete()

    def edit_quiz(
        self,
        question_id: int,
        question: Optional[str],
        options: Optional[dict],
        correct: Optional[str],
    ):
        quiz = Quiz.objects.get(pk=question_id)

        if question is not None:
            quiz.question = question
        if options is not None:
            quiz.options = options
        if correct is not None:
            quiz.correct = correct

        quiz.save()
        return quiz

    def export_to_moodle(self, topic: str):
        topic = self.updated_topic(topic)

        # Use case-insensitive filter for consistency
        quizzes = Quiz.objects.filter(topic__iexact=topic)
        if not quizzes.exists():
            raise ValueError("No quizzes found for the given topic.")

        category = Category(topic)

        for quiz in quizzes:
            moodle_question = Question("multichoice")
            moodle_question.text(quiz.question)

            # Map correct answer to option key
            # Handle both numeric ("1", "2", "3", "4") and letter ("a", "b", "c", "d") formats
            correct_value = quiz.correct.strip().lower()
            
            # Create mapping: "1" -> "a", "2" -> "b", "3" -> "c", "4" -> "d"
            # Or if already letter format, use as-is
            number_to_letter = {"1": "a", "2": "b", "3": "c", "4": "d"}
            if correct_value in number_to_letter:
                correct_letter = number_to_letter[correct_value]
            else:
                # Assume it's already in letter format
                correct_letter = correct_value

            # Add answers with proper grades (100% for correct, 0% for incorrect)
            for k, v in quiz.options.items():
                option_letter = k.split("option_")[-1]  # "a", "b", "c", or "d"
                is_correct = (option_letter == correct_letter)
                # Moodle expects percentage: 100.0 for correct, 0.0 for incorrect
                grade = 100.0 if is_correct else 0.0
                moodle_question.answer(v, grade)

            moodle_question.addto(category)

        file_path = f"/home/radhika3377/majorproject/vidyamitra/backend"

        category.savexml()

        s3_path = self.save_to_s3(f"{topic}.xml")
        os.remove(f"{file_path}/{topic}.xml")

        return s3_path

    def save_to_s3(self, filename: str):
        buffer = BytesIO()
        with open(filename, "rb") as f:
            buffer.write(f.read())
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
            f"generated/moodle_xml/{filename}",
        )

        # Generate the S3 file path (URL)
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/generated/moodle_xml/{filename}"

        return {"file_path": file_url}
