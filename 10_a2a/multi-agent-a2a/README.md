# A2A Multi-Agent System

This project implements a multi-agent system using the Agent2Agent (A2A) protocol, showcasing its capabilities compared to the Message Context Protocol (MCP).

## Features

- Dynamic agent discovery via AgentCards
- Direct agent-to-agent communication
- Rich content types through the A2A Part system
- Task management with full lifecycle
- Streaming and push notifications
- Artifact system for complex outputs

## System Architecture

```
[User Interface (Web App)]
         |
         v
[Host Agent (Orchestrator)]
         |
         v
[A2A Protocol]
     /       \       \
    v         v       v
[Agent 1]  [Agent 2]  [Agent 3]
   MCP        |        |
    |         |        |
[Tools]    [Tools]   [Tools]
```

## Components

1. **Web UI**: Built with Gradio for user interaction
2. **Host Agent**: Built with Google ADK, orchestrates other agents
3. **Specialized Agents**:
   - **Data Analysis Agent**: Built with LangGraph, uses MCP for tool calling
   - **Planning Agent**: Built with CrewAI
   - **Creative Agent**: Custom framework

## Setup

### Prerequisites

- Python 3.12+
- API keys for LLM (`.env` 파일)

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  
   # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file from the sample:
   ```
   cp env.sample .env
   ```

## Running the System

### Option 1: Running Individual Components

Start each agent separately:

1. **Data Analysis Agent**:
   ```
   python -m main --agent data --host localhost --port 8001
   ```

2. **Planning Agent**:
   ```
   python -m main --agent planning --host localhost --port 8002
   ```

3. **Creative Agent**:
   ```
   python -m main --agent creative --host localhost --port 8003
   ```

4. **Host Agent**:
   ```
   python -m main --agent host --host localhost --port 8000
   ```

5. **Web UI**:
   ```
   python run_ui.py --port 7860
   ```

You can override the model settings from the command line:
```
python -m main --agent data --model llama3 --base-url http://localhost:11434/v1
```

Then visit `http://localhost:7860` to access the web UI.
