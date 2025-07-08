from typing import List

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import END, MessageGraph
from src.reflexion.chains import first_responder, revisor
from src.reflexion.tool_executor import tool_node

# from chains import first_responder, revisor
# from tool_executor import tool_node
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages  # ✅ 병합 함수

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

MAX_ITERATIONS = 2
builder = MessageGraph()
builder.add_node("draft", first_responder)
builder.add_node("execute_tools", tool_node)
builder.add_node("revise", revisor)
builder.add_edge("draft", "execute_tools")
builder.add_edge("execute_tools", "revise")


def event_loop(state: List[BaseMessage]) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state)
    num_iterations = count_tool_visits
    if num_iterations > MAX_ITERATIONS:
        return END
    return "execute_tools"
#def event_loop(state: AgentState) -> str:
#    count = sum(msg.type == "tool" for msg in state["messages"])
#    return END if count > MAX_ITERATIONS else "execute_tools"


builder.add_conditional_edges("revise", event_loop)
builder.set_entry_point("draft")
graph = builder.compile()
graph.get_graph().draw_mermaid_png(output_file_path="graph.png")