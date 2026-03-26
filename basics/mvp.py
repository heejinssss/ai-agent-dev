# MVP 실습

# 환경 설정: .env 파일에서 API 키를 로드합니다.
from dotenv import load_dotenv
import os

load_dotenv()
assert os.environ.get("OPENAI_API_KEY"), "OPENAI_API_KEY가 설정되지 않았습니다!"
print("환경 설정 완료")

# Observability 설정 (선택) - LangSmith 또는 Langfuse
# .env에 키를 설정하거나, 아래 주석을 해제하여 직접 입력하세요.
# os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-..."
# os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-..."
# os.environ["LANGFUSE_HOST"] = "https://lf.ddok.ai"

# LangSmith: LANGSMITH_TRACING=true 시 자동 활성화 (코드 수정 불필요)
if os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_API_KEY", os.environ.get("LANGSMITH_API_KEY", ""))
    os.environ.setdefault("LANGCHAIN_PROJECT", os.environ.get("LANGSMITH_PROJECT", "default"))
    print(f"LangSmith tracing ON — project: {os.environ['LANGCHAIN_PROJECT']}")

# Langfuse: invoke/stream 호출 시 config={"callbacks": [langfuse_handler]} 전달
langfuse_handler = None
if os.environ.get("LANGFUSE_SECRET_KEY"):
    from langfuse.langchain import CallbackHandler
    langfuse_handler = CallbackHandler()
    print(f"Langfuse tracing ON — {os.environ.get('LANGFUSE_HOST', '')}")
# Langfuse config: pass to invoke/stream/batch calls
lf_config = {"callbacks": [langfuse_handler]} if langfuse_handler else {}

# uv add langchain_community

from langchain_community.document_loaders import TextLoader

file_path = "./log.txt"
loader = TextLoader(file_path, encoding="utf-8")
logs = loader.load()
logs

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 샘플 문서 생성 — 실제 환경에서는 PDF, 웹 등에서 로드합니다.
# Document 객체는 page_content(본문)와 metadata(출처 등)로 구성됩니다.
raw_docs = [
    Document(page_content="LangGraph는 LLM으로 상태 기반 멀티 액터 "
        "애플리케이션을 구축하기 위한 프레임워크입니다.",
        metadata={"source": "langgraph-docs"}),
    Document(page_content="에이전트는 도구를 사용하여 외부 시스템과 "
        "상호작용합니다. ReAct 패턴은 추론과 행동을 번갈아 수행합니다.",
        metadata={"source": "agent-guide"}),
]
print(f"문서 {len(raw_docs)}개 로드됨.")
# RecursiveCharacterTextSplitter: 문서를 의미 단위로 분할합니다.
# chunk_size: 각 청크의 최대 문자 수 (1000자)
# chunk_overlap: 인접 청크 간 겹치는 문자 수 (200자) — 경계 부분의 정보 손실 방지
text_splitter = RecursiveCharacterTextSplitter(
    # chunk_size=10, chunk_overlap=5,
    chunk_size=1000, chunk_overlap=200,
)
splits = text_splitter.split_documents(logs)

# 분할 결과 확인: 각 청크의 앞부분을 출력합니다.
for i, doc in enumerate(splits):
    print(f"청크 {i}: {doc.page_content[:60]}...")
print(f"총 청크 수: {len(splits)}")
