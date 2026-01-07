import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from .schema import KnowledgeSummaryOutput

system_prompt = """
                you are an expert summarizer based on given knowledge context.
                Your job is to summarize and answer questions related to courses of a university. 
                You will be given information such as course name, some part of the course content, and user query.
                You will answer only based on the given knowledge as course content, unless explictly asked to be creative.
                You will summarize the context and deliver the answer in neatly formatted markdown 
                using bullet or numbered points whereever required.
                """


class KnowledgeLLM:
    def __init__(self, user=None) -> None:
        """
        Initialize KnowledgeLLM with optional user for API key resolution.
        
        Args:
            user: CustomUser instance (optional) - for user-specific API keys
        """
        from silicon.util.api_key_helper import get_api_key_for_provider
        
        parser = JsonOutputParser(pydantic_object=KnowledgeSummaryOutput)

        prompt = PromptTemplate(
            template="""{system_prompt}
                \n{format_instructions}\n
                The following is the course details and context:
                course name:{course_name}\nknowledge course content context:{knowledge_context}\nquery={query}\n
                """,
            input_variables=[
                "course_name",
                "knowledge_context",
                "system_prompt",
                "querys",
            ],
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

    def explain(self, document: str, context: str, query: str):
        return self.chain.invoke(
            {
                "system_prompt": system_prompt,
                "course_name": document,
                "knowledge_context": context,
                "query": query,
            }
        )
