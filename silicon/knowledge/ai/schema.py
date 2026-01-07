from langchain_core.pydantic_v1 import BaseModel, Field


class KnowledgeSummaryOutput(BaseModel):
    response: str = Field(description="Summarised knowledge")
