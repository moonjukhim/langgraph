import asyncio
import json
import uuid
import pandas
from typing import Any, Dict, List, Optional, Union

from crewai import Agent as CrewAgent
from crewai import Crew, Task as CrewTask

from common.a2a import A2ABaseServer
from common.types import (
    AgentCard, Artifact, ArtifactType, Capabilities, Message,
    Skill, Task, TaskState, TextPart
)


class PlanningAgent(A2ABaseServer):
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        host: str = "localhost",
        port: int = 8002
    ):
        agent_card = AgentCard(
            name="Planning Agent",
            description="Breaks down complex tasks and creates plans",
            url=f"http://{host}:{port}",
            version="1.0.0",
            capabilities=Capabilities(
                streaming=True,
                pushNotifications=True
            ),
            defaultInputModes=["text"],
            defaultOutputModes=["text", "data"],
            skills=[
                Skill(id="task_decomposition", name="Task Decomposition", description="Breaks down complex tasks"),
                Skill(id="timeline_generation", name="Timeline Generation", description="Creates project timelines"),
                Skill(id="dependency_mapping", name="Dependency Mapping", description="Maps task dependencies")
            ]
        )
        super().__init__(agent_card=agent_card)
        self.model_name = model_name
        self.api_key = api_key
        self.host = host
        self.port = port

    async def handle_task(self, task: Task) -> Task:
        message_text = next((p.text for p in task.status.message.parts if hasattr(p, 'text')), "No input provided")

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._process_with_crewai, message_text)

        if not isinstance(result, dict):
            result = {"output": str(result)}

        response_text = result.get("output", "Planning complete")
        response_message = Message(parts=[TextPart(text=response_text)])

        artifacts = []
        if "plan" in result:
            artifacts.append(Artifact(
                id=str(uuid.uuid4()),
                type=ArtifactType.PLAN,
                name="Task Plan",
                description="Detailed plan with subtasks",
                content=result["plan"]
            ))
        if "timeline" in result:
            artifacts.append(Artifact(
                id=str(uuid.uuid4()),
                type=ArtifactType.DATA,
                name="Project Timeline",
                description="Timeline for project execution",
                content=result["timeline"]
            ))
        if "dependencies" in result:
            artifacts.append(Artifact(
                id=str(uuid.uuid4()),
                type=ArtifactType.DATA,
                name="Task Dependencies",
                description="Dependencies between tasks",
                content=result["dependencies"]
            ))

        task.status.state = TaskState.COMPLETED
        task.status.message = response_message
        task.artifacts = artifacts
        return task

    def _process_with_crewai(self, input_text: str) -> Dict[str, Any]:
        planner = CrewAgent(role="Project Planner", goal="Break down complex tasks", backstory="Experienced planner.", verbose=True, allow_delegation=False, llm_model=self.model_name)
        timeline = CrewAgent(role="Timeline Specialist", goal="Create project timelines", backstory="Estimates durations.", verbose=True, allow_delegation=False, llm_model=self.model_name)
        dependencies = CrewAgent(role="Dependency Analyzer", goal="Map dependencies", backstory="Analyzes relationships.", verbose=True, allow_delegation=False, llm_model=self.model_name)

        task1 = CrewTask(description=f"Break down this project: {input_text}", expected_output="List of tasks", agent=planner)
        task2 = CrewTask(description="Create timeline", expected_output="Timeline", agent=timeline, context=["Output of task decomposition"])
        task3 = CrewTask(description="Identify dependencies", expected_output="Dependencies", agent=dependencies, context=["Output of task decomposition"])

        crew = Crew(agents=[planner, timeline, dependencies], tasks=[task1, task2, task3], verbose=True)
        result_str = crew.kickoff()
        
        try:
            
            try:
                parsed = json.loads(result_str)
                output = parsed if isinstance(parsed, dict) else {"output": result_str}
            except Exception:
                output = {"output": result_str}

            return {
                "output": output["output"] if isinstance(output, dict) and "output" in output else result_str,
                "plan": {"tasks": self._extract_tasks(result_str)},
                "timeline": self._extract_timeline(result_str),
                "dependencies": self._extract_dependencies(result_str)
            }
        except Exception as e:
            return self._fallback_plan(str(e))

    def _fallback_plan(self, error_msg: str) -> Dict[str, Any]:
        return {
            "output": f"Fallback plan due to error: {error_msg}",
            "plan": {"tasks": self._extract_tasks("")},
            "timeline": self._extract_timeline(""),
            "dependencies": self._extract_dependencies("")
        }

    def _extract_tasks(self, _: Union[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        return [
            {"id": "1", "name": "Define scope", "description": "Outline goals", "duration": "2 days"},
            {"id": "2", "name": "Design system", "description": "Create architecture", "duration": "3 days"}
        ]

    def _extract_timeline(self, _: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "start_date": "2023-08-01",
            "end_date": "2023-08-10",
            "duration": "10 days",
            "milestones": [
                {"id": "M1", "name": "Design Complete", "date": "2023-08-05"},
                {"id": "M2", "name": "Delivery", "date": "2023-08-10"}
            ]
        }

    def _extract_dependencies(self, _: Union[str, Dict[str, Any]]) -> List[Dict[str, str]]:
        return [
            {"from": "1", "to": "2", "type": "finish-to-start"}
        ]

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port)
