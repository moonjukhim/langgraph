"""
Creative Agent for content generation.
"""
import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from common.a2a import A2ABaseServer
from common.types import (
    AgentCard, Artifact, ArtifactType, Capabilities, Message, 
    Skill, Task, TaskState, TaskStatus, TextPart
)


class CreativeAgent(A2ABaseServer):
    """Creative Agent that generates creative content.
    
    This agent specializes in generating creative text content,
    stories, and formatted output.
    """
    
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        host: str = "localhost",
        port: int = 8003
    ):
        """Initialize the Creative Agent.
        
        Args:
            model_name: Name of the LLM to use
            api_key: API key for the LLM
            host: Host to bind to
            port: Port to bind to
        """
        # Create AgentCard
        agent_card = AgentCard(
            name="Creative Agent",
            description="Generates creative content based on prompts",
            url=f"http://{host}:{port}",
            version="1.0.0",
            capabilities=Capabilities(
                streaming=True,
                pushNotifications=True
            ),
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            skills=[
                Skill(
                    id="text_generation",
                    name="Text Generation",
                    description="Generates creative text content"
                ),
                Skill(
                    id="story_creation",
                    name="Story Creation",
                    description="Creates compelling stories"
                ),
                Skill(
                    id="content_formatting",
                    name="Content Formatting",
                    description="Formats content for various purposes"
                )
            ]
        )
        
        # Initialize A2A server
        super().__init__(agent_card=agent_card)
        
        # Save configuration
        self.model_name = model_name
        self.api_key = api_key
        self.host = host
        self.port = port
        self.openai_client = AsyncOpenAI()
        
        # Configure content types and templates
        self.content_types = {
            "blog": {
                "sections": ["introduction", "body", "conclusion"],
                "word_count": 500
            },
            "story": {
                "sections": ["setting", "characters", "plot", "resolution"],
                "word_count": 1000
            },
            "social": {
                "sections": ["headline", "body", "call_to_action"],
                "word_count": 200
            },
            "email": {
                "sections": ["greeting", "body", "closing"],
                "word_count": 300
            }
        }
    
    async def handle_task(self, task: Task) -> Task:
        """Handle a creative content generation task.
        
        Args:
            task: Task to handle
            
        Returns:
            Updated task with results
        """
        # Extract message
        message_text = "No input provided"
        print(f"Task: {task}")
        if task.status.message and task.status.message.parts:
            for part in task.status.message.parts:
                if hasattr(part, 'text'):
                    message_text = part.text
                    break
        
        # Determine content type based on message
        content_type = self._determine_content_type(message_text)
        content = await self._generate_content(message_text, content_type)
        
        # Create response message
        response_text = content.get("summary", "Content generation complete")
        response_message = Message(parts=[TextPart(text=response_text)])
        
        # Create artifact for the main content
        artifact_id = str(uuid.uuid4())
        artifact = Artifact(
            id=artifact_id,
            type=ArtifactType.DOCUMENT,
            name=content.get("title", "Generated Content"),
            description=content.get("description", "Creative content based on your prompt"),
            content={
                "content_type": content_type,
                "full_text": content.get("full_text", ""),
                "sections": content.get("sections", {})
            }
        )
        
        # Update task with results
        task.status.state = TaskState.COMPLETED
        task.status.message = response_message
        task.artifacts = [artifact]
        
        return task
    
    def _determine_content_type(self, message: str) -> str:
        """Determine the type of content to generate based on the message.
        
        Args:
            message: User message
            
        Returns:
            Content type
        """
        message_lower = message.lower()
        print(f"Message: {message_lower}")
        
        if any(kw in message_lower for kw in ["blog", "article", "post"]):
            return "blog"
        elif any(kw in message_lower for kw in ["story", "narrative", "tale"]):
            return "story"
        elif any(kw in message_lower for kw in ["social", "twitter", "facebook", "instagram"]):
            return "social"
        elif any(kw in message_lower for kw in ["email", "message", "communication"]):
            return "email"
        else:
            # Default to blog
            return "blog"
    
    async def _generate_content(self, prompt: str, content_type: str) -> Dict[str, Any]:
        instruction = f"""
            You are a helpful assistant that generates creative {content_type} content.

            Please write a full {content_type} based on this prompt:
            "{prompt}"

            Return your response in JSON format with these fields:
            - title
            - description
            - summary
            - full_text
            - sections (based on content_type, e.g., intro/body/conclusion for blog)
            
            Do not use markdown code blocks like ```json. Just return raw JSON text.
        """

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a creative writer bot."},
                    {"role": "user", "content": instruction}
                ],
                temperature=0.7
            )
            content_str = response.choices[0].message.content.strip()
            
            #content_data = json.loads(content_str)
            #content_data["word_count"] = len(content_data.get("full_text", "").split())
            # return content_data
            
            # 🔐 검사: 응답이 JSON처럼 보이는지
            if not content_str.startswith("{"):
                raise ValueError("OpenAI did not return valid JSON. Raw content:\n" + content_str)

            # 🧪 JSON 파싱
            content_data = json.loads(content_str)
            content_data["word_count"] = len(content_data.get("full_text", "").split())
            return content_data
        except Exception as e:
            return {
                "title": "Generation Failed",
                "description": str(e),
                "summary": "Failed to generate content",
                "full_text": "",
                "sections": {},
                "word_count": 0
            }
    
    def run(self):
        """Run the agent server."""
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port) 