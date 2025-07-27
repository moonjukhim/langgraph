###

##### 1. 필요사항

  - Python 3.12 이상 버전
  - UV (pip install pip)
  - Agent server (sample)
  - OpenAI API Key


##### 2. UI Application

```bash
cd 10_a2a/multi-agent-a2a
python -m venv .venv
.venv/Scripts/activate
pip install -r requirements.txt
cp env.sample .env
```

##### 3. Running agents

```bash
python -m main --agent data --host localhost --port 8001
python -m main --agent planning --host localhost --port 8002
python -m main --agent creative --host localhost --port 8003
python -m main --agent host --host localhost --port 8000
python run_ui.py --port 7860
```

##### 4. Web UI

visit http://localhost:7860 to access the web UI.
 