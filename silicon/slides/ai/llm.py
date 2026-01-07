import os
from django.conf import settings
from jinja2 import Template
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from .schema import Presentation


class SlideGeneratorLLM:
    def __init__(self, user=None):
        """
        Initialize SlideGeneratorLLM with optional user for API key resolution.
        
        Args:
            user: CustomUser instance (optional) - for user-specific API keys
        """
        from silicon.util.api_key_helper import get_api_key_for_provider
        
        # Get OpenAI API key (user-specific or environment variable)
        openai_key = None
        if user:
            openai_key = get_api_key_for_provider(user, "openai")
        if not openai_key:
            openai_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or add a user API key via POST /v1/user/api-keys/ with provider='openai'"
            )

        # Use OpenAI instead of Gemini for consistency
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=openai_key,
        )

        # Load template
        template_path = settings.BASE_DIR / "templates"
        with open(
            f"{template_path}/generate_presentation.md", "r", encoding="utf-8"
        ) as file:
            self.generate_presentation_template = Template(file.read())

    def _generate_presentation_chain(self):
        parser = JsonOutputParser(pydantic_object=Presentation)

        prompt = PromptTemplate(
            template=self.generate_presentation_template.render(),
            input_variables=["count", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        return prompt | self.model | parser

    def generate_presentation(self, title: str, count: int, context: str):
        return self._generate_presentation_chain().invoke(
            {"title": title, "count": count, "context": context}
        )
