from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-5.4")
print("\u2713 모델 준비 완료")

# Observability 설정 (선택) - LangSmith 또는 Langfuse
# .env에 키를 설정하거나, 아래 주석을 해제하여 직접 입력하세요.
# os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
# os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
# os.environ["LANGFUSE_HOST"] = "https://lf.ddok.ai"
import os

# LangSmith: LANGSMITH_TRACING=true 시 자동 활성화 (코드 수정 불필요)
if os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_API_KEY", os.environ.get("LANGSMITH_API_KEY", ""))
    os.environ.setdefault("LANGCHAIN_PROJECT", os.environ.get("LANGSMITH_PROJECT", "default"))
    print(f"LangSmith tracing ON \u2014 project: {os.environ['LANGCHAIN_PROJECT']}")

# Langfuse: invoke/stream 호출 시 config={"callbacks": [langfuse_handler]} 전달
langfuse_handler = None
if os.environ.get("LANGFUSE_SECRET_KEY"):
    from langfuse.langchain import CallbackHandler
    langfuse_handler = CallbackHandler()
    print(f"Langfuse tracing ON \u2014 {os.environ.get('LANGFUSE_HOST', '')}")

# Langfuse config: pass to invoke/stream/batch calls
lf_config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}

#=========================================================
# Langchain
#=========================================================

from langchain.tools import tool
from langchain.agents import create_agent

@tool
def check_error(a: str) -> str:
    """에러를 감지합니다."""
    print("[TOOL CALL] check_error") # 로그성 출력문 추가
    return "에러 발생"

print("도구 목록:")

for t in [check_error]:
    print(f" - {t.name}: {t.description}")

agent = create_agent(
    model=model,
    # tools=[check_error, a, b, c, ...],
    tools=[check_error],
    system_prompt="당신은 품질설계 개발자입니다.",
)

print("\u2713 에이전트 생성 완료")

result = agent.invoke(
    {"messages": [{"role": "user", "content": "[INFO] 로그가 보입니다. 에러인가요?"}]},
    config=lf_config,
)

print("에이전트 응답:", result["messages"][-1].content)
