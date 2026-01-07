from langchain_core.pydantic_v1 import BaseModel, Field


class QuizSchema(BaseModel):
    question: str = Field(description="quiz question based on the topic")
    option_a: str = Field(description="first option for the quiz question")
    option_b: str = Field(description="second option for the quiz question")
    option_c: str = Field(description="third option for the quiz question")
    option_d: str = Field(description="fourth option for the quiz question")
    correct: str = Field(description="correct option number for the quiz question")


class GeneratedQuiz(BaseModel):
    topic: str = Field(description="quiz topic")
    count: int = Field(description="number of quizzes that are generated")
    quizzes: list[QuizSchema] = Field(description="list of all generated quizzes")
