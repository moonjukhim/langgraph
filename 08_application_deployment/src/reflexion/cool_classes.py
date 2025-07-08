from typing import List

from pydantic import BaseModel, Field


class Reflection(BaseModel):
    missing: str = Field(description="누락된 부분에 대한 비판")
    superfluous: str = Field(description="불필요한 것에 대한 비판")


class AnswerQuestion(BaseModel):
    """Answer the question."""

    answer: str = Field(description="질문에 대한 답변은 250개의 단어 내로 작성")
    reflection: Reflection = Field(description="첫 번째 답변에 대한 평가")
    search_queries: List[str] = Field(
        description="현재 답변에 대한 비판을 해결하기 위한 개선 사항을 조사하기 위한 1~3개의 검색어"
    )


# Forcing citation in the model encourages grounded responses
class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question."""

    references: List[str] = Field(
        description="업데이트된 답변에 대한 동기를 인용"
    )
