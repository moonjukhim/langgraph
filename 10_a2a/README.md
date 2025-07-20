###

##### 1. 필요사항

  - Python 3.12 이상 버전
  - UV (pip install pip)
  - Agent server (sample)
  - API Key 혹은 Vertex AI


##### 2. UI Application

```bash
cd ui
python -m venv .venv
.venv/Scripts/activate
pip install uv
pip install -e .

# 
echo "GOOGLE_API_KEY=your_api_key_here" >> .env

uv run main.py
```

##### 3
 
```bash
cd samples/python/agents/langgraph
```

