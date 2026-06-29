import time
import subprocess
from pathlib import Path
import sys
import requests

# 1. 프로젝트 루트를 경로에 추가 (매뉴얼 12장 기준)
sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

# 2. 매뉴얼에서 정의한 모듈 임포트
from scripts.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BASE_DIR
from scripts.send_telegram import send_message

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def get_updates(offset=None):
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        res = requests.get(f"{API_URL}/getUpdates", params=params, timeout=40)
        res.raise_for_status()
        return res.json().get("result", [])
    except Exception as e:
        print(f"Update 조회 오류: {e}")
        return []

def handle_text(text):
    # /daily 리포트 요청 처리
    if text == "/daily":
        result = subprocess.run(
            ["python3", str(BASE_DIR / "reports/daily_report.py")],
            capture_output=True, text=True
        )
        send_message("[일일 PT 리포트]\n\n" + (result.stdout.strip() if result.stdout.strip() else "리포트 생성 내용이 없습니다."))
        return

    # /weekly 리포트 요청 처리
    if text == "/weekly":
        result = subprocess.run(
            ["python3", str(BASE_DIR / "reports/weekly_report.py")],
            capture_output=True, text=True
        )
        send_message("[주간 PT 리포트]\n\n" + (result.stdout.strip() if result.stdout.strip() else "주간 데이터가 없습니다."))
        return

    # /help 도움말
    if text == "/help":
        send_message("사용법\n- 운동/식단/체중을 자연스럽게 입력하세요.\n- /daily: 일일 리포트\n- /weekly: 주간 리포트\n- /help: 도움말")
        return

    # 일반 기록 저장 스크립트 실행
    result = subprocess.run(
        ["python3", str(BASE_DIR / "scripts/save_message.py"), text],
        capture_output=True, text=True
    )
    send_message(result.stdout.strip())

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN이 설정되지 않았습니다.")
        
    offset = None
    send_message("AI PT 트레이너가 시작되었습니다. 오늘 기록을 보내주세요.")
    
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = str(message.get("chat", {}).get("id", ""))
                
                # 설정된 Chat ID 확인
                if str(TELEGRAM_CHAT_ID) and chat_id != str(TELEGRAM_CHAT_ID):
                    continue
                    
                text = message.get("text", "").strip()
                if text:
                    handle_text(text)
        except Exception as e:
            print(f"오류 발생: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()