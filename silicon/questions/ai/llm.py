from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from django.conf import settings
from .schema import Questions, SelectedQuestionIds


class QuestionPaperGeneratorLLM:
    # model = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-pro", convert_system_message_to_human=True, temperature=0.0
    # )
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

    def __init__(self):

        templates_path = (
            settings.BASE_DIR / "templates" / "generate_questions_prompt_template.md"
        )

        with open(templates_path, "r", encoding="utf-8") as file:
            self._template = Template(file.read())
        print("Templates directory:", templates_path)

    def _get_prompt_from_jinja2(
        self, template_name, input_variables, partial_variables={}, placeholders={}
    ):
        """Loads a .md file as a Jinja2 template and converts it into a
        LangChain PromptTemplate.

        Parameters:
            template_name: Filename of the prompt ('generate_questions_prompt_template.md').
            input_variables: List of variable names for the PromptTemplate.
            partial_variables: Dictionary of partial variables for PromptTemplate.
            placeholders: Dictionary of placeholders to replace in the Jinja2 template.
        """
        prompt_string = self._template.render(placeholders)

        prompt_template = PromptTemplate(
            template=prompt_string,
            input_variables=input_variables,
            partial_variables=partial_variables,
        )
        return prompt_template

    def _get_question_chain(self):
        parser = JsonOutputParser(pydantic_object=Questions)

        prompt = self._get_prompt_from_jinja2(
            template_name="generate_questions_prompt_template.md",
            input_variables=[
                "course",
                "context",
                "syllabus_context",
                "count",
                "user_prompt",
                "difficulty_distribution",
                "blooms_distribution",
            ],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        return prompt | self.model | parser

    def generate_questions(
        self,
        course: str,
        context: str,
        syllabus_context: str,
        count: int,
        user_prompt: str,
        difficulty_distribution: str,
        blooms_distribution: str,
    ):
        input_data = {
            "course": course,
            "context": context,
            "syllabus_context": syllabus_context,
            "count": count,
            "user_prompt": user_prompt,
            "difficulty_distribution": difficulty_distribution,
            "blooms_distribution": blooms_distribution,
        }

        try:
            return self._get_question_chain().invoke(input_data)
        except Exception as e:
            print("Error during question generation:", e)
            raise
