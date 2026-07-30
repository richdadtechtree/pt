import os
from pathlib import Path
from dotenv import load_dotenv

DEFAULT_BASE_DIR = Path("/home/ubuntu/pt_system")
BASE_DIR = DEFAULT_BASE_DIR if DEFAULT_BASE_DIR.exists() else Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "pt_data.db"))

# LLM 공급자 선택: "gemini" 또는 "openai" (.env 한 줄로 전환)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# Gemini (기본)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

# OpenAI(GPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")