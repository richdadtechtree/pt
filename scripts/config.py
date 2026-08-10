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

# 텔레그램 발송 on/off 스위치.
# PT 관련 톡을 보내지 않으려면 그대로 두거나 .env 에 TELEGRAM_ENABLED=false 로 지정.
# 다시 켜려면 .env 에 TELEGRAM_ENABLED=true 로 설정.
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)