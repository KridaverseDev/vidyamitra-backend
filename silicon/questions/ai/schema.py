from langchain_core.pydantic_v1 import BaseModel, Field


class QuestionItem(BaseModel):
    q_num: str = Field(description="question number")
    question: str = Field(description="question")
    marks: str = Field(description="marks allotted")
    blooms_level: int = Field(description="bloom's level of the question")
    difficulty: str = Field(
        description="Difficulty of the question, E, M, H for Easy, Medium and Hard respectively"
    )
    course_outcome: int = Field(
        description="Course Outcome of the question based on the syllabus."
    )


class Questions(BaseModel):
    questions: list[QuestionItem] = Field(description="list of questions")


class SelectedQuestionIds(BaseModel):
    question_ids: list[int] = Field(description="list of ids of selected questions")
