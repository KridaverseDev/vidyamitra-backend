from langchain_core.pydantic_v1 import BaseModel, Field


class Slide(BaseModel):
    title: str = Field(description="Title of the slide based on the context")
    content: list[str] = Field(
        description="A list of concise bullet points directly related to the title and context"
    )


class Presentation(BaseModel):
    slides: list[Slide] = Field(
        description="A list of slides based on the provided context"
    )
