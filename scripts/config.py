import os
from pathlib import Path
from dotenv import load_dotenv

DEFAULT_BASE_DIR = Path("/home/ubuntu/pt_system")
BASE_DIR = DEFAULT_BASE_DIR if DEFAULT_BASE_DIR.exists() else Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "pt_data.db"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Slack (텔레그램 대체 채널)
#  - SLACK_BOT_TOKEN   : Bot User OAuth Token (xoxb-...)  스코프: chat:write, files:read
#  - SLACK_APP_TOKEN   : App-Level Token (xapp-...)       Socket Mode 용 (connections:write)
#  - SLACK_PT_CHANNEL  : 리포트/알림을 올릴 채널 ID (C...) — 봇이 초대돼 있어야 함
#  - SLACK_ALLOWED_USER: (선택) 이 유저(U...)만 응답. 비우면 모든 유저 허용
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
SLACK_PT_CHANNEL = os.getenv("SLACK_PT_CHANNEL", "")
SLACK_ALLOWED_USER = os.getenv("SLACK_ALLOWED_USER", "")

# 알림 채널 선택: 슬랙 토큰이 있으면 기본 slack, 아니면 telegram
NOTIFY_CHANNEL = os.getenv("NOTIFY_CHANNEL", "slack" if SLACK_BOT_TOKEN else "telegram").lower()