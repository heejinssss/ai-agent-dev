from datetime import datetime

from langchain_core.tools import tool

# import 추가
# ==========================================================================
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import base64

from pathlib import Path

from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
# ==========================================================================


# path 및 공통변수 선언
# ==========================================================================
BASE_DIR = Path(__file__).parent.parent
TOKEN_PATH = BASE_DIR / 'token.json'
CREDS_PATH = BASE_DIR / 'credentials.json'
SCOPES = ['https://mail.google.com/']
# ==========================================================================


@tool
def read_log() -> str:
    """로그 파일을 읽어서 내용을 반환합니다. 테스트 로그 파일의 경로는 고정되어 있습니다."""
    file_path = "./logs.txt"
    loader = TextLoader(file_path, encoding="utf-8")
    logs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],
        chunk_size=1000,
        chunk_overlap=0,
    )

    splits = text_splitter.split_documents(logs)

    return splits


@tool
def send_email(subject: str, body: str) -> str:
    """이메일을 담당자에게 전송합니다.

    Args:
        subject: 이메일 제목 ("[품질설계 에러 발생 (긴급도 상)] 에러 요약")
        body: 이메일 본문 (에러 분석 내용)
    """
    creds = None
    if TOKEN_PATH.is_file():
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    message = EmailMessage()
    message["From"] = "baebbang0424@gmail.com"
    message["To"] = "baebbang0424@gmail.com"
    message["Subject"] = subject
    message.set_content(body)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')
    service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return f"이메일 전송 완료: {subject}"
