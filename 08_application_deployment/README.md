## Run Locally

Clone the project:

```bash
git clone <repository-url>
cd reflexion-agent
```

Install dependencies:

```bash
pip install -U "langgraph-cli[inmem]"
```

Start the agent in local:

```bash
langgraph dev
```

```text
Ready!
API: http://localhost:2024
Docs: http://localhost:2024/docs
```

```bash
python main.py
```

## Development Setup

1. Get your API keys:

   - [OpenAI Platform](https://platform.openai.com/) for GPT-4 access
   - [Tavily](https://tavily.com/) for search functionality
   - [LangSmith](https://smith.langchain.com/) (optional) for tracing

2. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your API keys

## Running Tests

To run tests, use the following command:

```bash
poetry run pytest . -s -v
```