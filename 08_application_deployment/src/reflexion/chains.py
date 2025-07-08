from dotenv import load_dotenv

load_dotenv()
import datetime

from langchain_core.output_parsers import JsonOutputToolsParser, PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.reflexion.tool_classes import AnswerQuestion, ReviseAnswer

llm = ChatOpenAI(model="gpt-4o-mini")
parser = JsonOutputToolsParser(return_id=True)

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """당신은 전문적인 연구자입니다.
                Current time: {time}

                1. {first_instruction}
                2. 답변을 되돌아보고 비판하세요. 개선을 극대화하기 위해 진지하게 비판하세요.
                3. 정보를 확인하고 답변을 개선하기 위해 검색어를 추천하세요""",
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "사용자의 질문에 필요한 형식을 사용하여 답변하세요."),
    ]
).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)


first_responder = actor_prompt_template.partial(
    first_instruction="250개 단어 내로 자세한 답변을 하세요."
) | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
validator = PydanticToolsParser(tools=[AnswerQuestion])


revise_instructions = """새로운 정보를 사용하여 이전 답변을 수정하세요.
                        - 이전 비평을 활용하여 답변에 중요한 정보를 추가하세요.
                            - 수정된 답변의 검증을 위해 반드시 인용 번호를 포함하세요.
                            - 답변 하단에 "참고문헌" 섹션을 추가하세요(참고문헌은 단어 제한에 포함되지 않습니다). 다음 형식으로 작성하세요:
                                - [1] https://example.com
                                - [2] https://example.com
                        - 이전 비평을 활용하여 답변에서 불필요한 정보를 제거하고 250 단어를 넘지 않도록 작성하세요.
"""


revisor = actor_prompt_template.partial(
    first_instruction=revise_instructions
) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")
