import asyncio
from langgraph_sdk import get_client
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage

from dotenv import load_dotenv
load_dotenv()

async def invoke_retrieval_assistant():
    
    # deployment_url = "[PROJECT_ID].us.langgraph.app"
    deployment_url = "http://localhost:2024"
    
    
    client = get_client(url=deployment_url)

    try:
        # Create a new thread
        thread = await client.threads.create(
            # Optional: Add metadata if needed
            metadata={
                "user_id": "example_user",
                "session": "retrieval_session"
            }
        )

        # Prepare the input for the retrieval graph
        input_messages = [
            {"role": "user", "content": "NPU에 대한 고충 영역을 식별하고 이를 해결하기 위해 자본 투자를 유치한 스타트업 목록을 나열하세요."}
        ]
        
        assistant_id = "agent"

        async for event in client.runs.stream(
            thread_id=thread["thread_id"],
            assistant_id=assistant_id,
            input=input_messages,
            stream_mode="updates"  # Stream updates as they occur
        ):
            # Process and print each event
            print(f"Receiving event of type: {event.event}")
            print(event.data)
            print("\n")

    except Exception as e:
        print(f"An error occurred: {e}")


asyncio.run(invoke_retrieval_assistant())
