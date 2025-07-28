###

##### 1. 필요사항

  - Python 3.12 이상 버전
  - Virtual Environment(or UV)
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
 
다음 각각의 쿼리를 실행
- Data Analysis: 이 판매 데이터를 분석하여 추세를 파악하세요.
- Planning: 새로운 모바일 앱 출시를 위한 프로젝트 계획을 만들어보세요
- Creative Content: 생성형 AI에 대한 블로그 게시물 작성
- Combined Task: 고객 데이터를 분석하고 결과를 바탕으로 마케팅 계획 수립
