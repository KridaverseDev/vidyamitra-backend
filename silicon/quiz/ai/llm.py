import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from .schema import GeneratedQuiz

system_prompt = """
                you are an expert professor who can assess students understanding on concepts. 
                You specialize in creating MCQ questions for engineering students based on given the 
                given course and its context. For the given topic Generate questions with varying mix of differnt difficulty
                levels (easy, medium, hard).
                """


class QuizGeneratorLLM:
    def __init__(self, user=None) -> None:
        """
        Initialize QuizGeneratorLLM with optional user for API key resolution.
        
        Args:
            user: CustomUser instance (optional) - for user-specific API keys
        """
        from silicon.util.api_key_helper import get_api_key_for_provider
        
        parser = JsonOutputParser(pydantic_object=GeneratedQuiz)

        prompt = PromptTemplate(
            template="Generate Quiz.\n{format_instructions}\n\
                context:{context}\ntopic:{topic}\n\nnumber of quizzes:{count}\n",
            input_variables=["count", "topic", "context"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

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
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=openai_key,
        )

        self.chain = prompt | model | parser

    def generate(
        self,
        topic: str,
        count: int,
        context: str,
    ):
        return self.chain.invoke(
            {
                "topic": topic,
                "count": count,
                "context": context,
            }
        )
