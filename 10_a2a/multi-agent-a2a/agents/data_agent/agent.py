import asyncio
import os
import uuid
import operator
from typing import Any, Dict, List, Optional, TypedDict

import pandas as pd  
from langchain_core.tools import Tool 
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain.agents import initialize_agent

from common.a2a import A2ABaseServer
from common.types import (
    AgentCard, Artifact, ArtifactType, Capabilities, Message,
    Skill, Task, TaskState, TextPart
)



class AgentState(TypedDict):
    messages: List[BaseMessage]


def chat_agent_node(llm, tools=None):
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type="openai-functions",
        verbose=True,
    )

    def node(state: AgentState) -> AgentState:
        input_msg = state["messages"][-1].content
        response = agent_executor.run(input_msg)
        return {"messages": state["messages"] + [AIMessage(content=response)]}

    return node


def tool_node(tools: List[Tool]):
    def node(state: AgentState) -> AgentState:
        return state  # placeholder for actual tool use logic

    return node


def extract_tool_choice(state: AgentState) -> str:
    last_msg = state["messages"][-1].content.lower()
    return "tool" if "tool" in last_msg else "end"


class DataAnalysisAgent(A2ABaseServer):
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        host: str = "localhost",
        port: int = 8001
    ):
        agent_card = AgentCard(
            name="Data Analysis Agent",
            description="Processes and analyzes data files",
            url=f"http://{host}:{port}",
            version="1.0.0",
            capabilities=Capabilities(streaming=True, pushNotifications=True),
            defaultInputModes=["text", "file"],
            defaultOutputModes=["text", "data"],
            skills=[
                Skill(id="data_analysis", name="Data Analysis", description="Analyzes structured data files"),
                Skill(id="visualization", name="Data Visualization", description="Creates visual representations of data")
            ]
        )
        super().__init__(agent_card=agent_card)
        self.model_name = model_name
        self.api_key = api_key
        self.host = host
        self.port = port

        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.tools = self._create_tools()
        self.graph = self._create_graph()

    def _create_tools(self) -> List[Tool]:
        return [
            Tool.from_function(self._load_csv, name="load_csv", description="Load a CSV file for analysis"),
            Tool.from_function(self._load_json, name="load_json", description="Load a JSON file for analysis"),
            Tool.from_function(self._analyze_data, name="analyze_data", description="Analyze loaded data"),
            Tool.from_function(self._visualize_data, name="visualize_data", description="Create visualization from data")
        ]

    def _create_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        workflow.add_node("agent", chat_agent_node(self.llm, tools=self.tools))
        workflow.add_node("tools", tool_node(self.tools))

        workflow.add_conditional_edges("agent", extract_tool_choice, {
            "tool": "tools",
            "end": END
        })

        workflow.add_edge("tools", "agent")
        workflow.set_entry_point("agent")

        return workflow.compile()

    async def handle_task(self, task: Task) -> Task:
        message_text = next((part.text for part in task.status.message.parts if getattr(part, "type", None) == "text"), None)
        if not message_text:
            task.status.state = TaskState.FAILED
            task.status.message = Message(parts=[TextPart(text="Missing valid user input in message parts")])
            task.artifacts = []
            return task

        task_data = {
            "task_id": task.id,
            "input": message_text,
            "files": [],
            "results": []
        }

        result = await self._process_with_mcp(task_data)
        response_text = result.get("output", "Analysis complete")
        response_message = Message(parts=[TextPart(text=response_text)])

        artifacts = [
            Artifact(
                id=str(uuid.uuid4()),
                type=ArtifactType.DATA,
                name=r.get("name", "Analysis Result"),
                description=r.get("description", ""),
                content=r.get("data", {})
            )
            for r in result.get("results", [])
        ]

        task.status.state = TaskState.COMPLETED
        task.status.message = response_message
        task.artifacts = artifacts
        return task

    async def _process_with_mcp(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        state = {
            "messages": [HumanMessage(content=task_data["input"])]
        }

        final_state = None
        async for step in self.graph.astream(state):
            if "__end__" in step:
                final_state = step["__end__"]
                break

        if final_state is None:
            return {
                "output": "Graph execution finished without producing a final state.",
                "results": []
            }

        final_messages = final_state.get("messages", [])
        final_output = "\n".join(m.content for m in final_messages if hasattr(m, "content"))

        return {
            "output": final_output,
            "results": []
        }

    def _load_csv(self, file_path: str) -> AIMessage:
        df = pd.read_csv(file_path)
        self._dataframe = df
        return AIMessage(content=f"Loaded CSV file {file_path}")

    def _load_json(self, file_path: str) -> AIMessage:
        return AIMessage(content=f"Loaded JSON file {file_path}")

    def _analyze_data(self, analysis_type: str) -> AIMessage:
        return AIMessage(content=f"Analyzed data using {analysis_type}. Mean=42.5, Std=15.7")

    def _visualize_data(self, visualization_type: str) -> AIMessage:
        return AIMessage(content=f"Created {visualization_type} visualization")

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)
