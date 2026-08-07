"""
Slack PT 봇 (telegram_polling.py 의 슬랙 버전, Socket Mode).

텔레그램 봇과 동일한 파이프라인을 그대로 재사용한다:
  - 텍스트  → scripts/save_message.py 로 DB 저장 + ai_helper.generate_response 코칭 답변
  - 사진    → ai_helper.generate_image_response 로 분석 → [기록 데이터] 저장 + [코칭 피드백] 답변
  - 명령    → 일일/주간 리포트 생성 후 회신, 도움말

Socket Mode 라 공개 URL 이 필요 없다(아웃바운드 웹소켓). 앱 토큰(xapp-)과 봇 토큰(xoxb-)만 있으면 된다.

필요 패키지:  slack_sdk   (venv/bin/pip install slack_sdk)
필요 스코프:  chat:write, files:read, channels:history, groups:history, im:history, mpim:history
이벤트 구독:  message.channels, message.groups, message.im, message.mpim
.env:        SLACK_BOT_TOKEN, SLACK_APP_TOKEN, (선택)SLACK_PT_CHANNEL, (선택)SLACK_ALLOWED_USER

실행:  venv/bin/python scripts/slack_bot.py     (systemd: pt-slack.service)
"""
import sys
import threading
import subprocess
from pathlib import Path

sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import requests
from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from scripts.config import (
    SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_PT_CHANNEL, SLACK_ALLOWED_USER, BASE_DIR,
)
from scripts.ai_helper import generate_response, generate_image_response

# 명령 별칭 (텔레그램의 /daily·/weekly·/help 를 슬랙에서 자연스럽게)
DAILY_CMDS = {"/daily", "daily", "일일", "일일리포트", "일간리포트", "오늘리포트"}
WEEKLY_CMDS = {"/weekly", "weekly", "주간", "주간리포트"}
HELP_CMDS = {"/help", "help", "도움말", "사용법"}

_web = WebClient(token=SLACK_BOT_TOKEN)
_seen = set()          # 이벤트 중복 처리 방지 (event ts)
_seen_lock = threading.Lock()
_BOT_USER_ID = None


def post(channel, text):
    if not text:
        return
    try:
        _web.chat_postMessage(channel=channel, text=text,
                              unfurl_links=False, unfurl_media=False)
    except Exception as e:
        print(f"[slack] 전송 실패: {e}", file=sys.stderr)


def run_report(kind):
    """일일/주간 리포트 스크립트를 실행하고 stdout 반환."""
    script = "reports/daily_report.py" if kind == "daily" else "reports/weekly_report.py"
    try:
        res = subprocess.run(
            [sys.executable, str(BASE_DIR / script)],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            return f"[오류] {kind} 리포트 생성 실패:\n{res.stderr.strip()}"
        out = res.stdout.strip()
        title = "[일일 PT 리포트]" if kind == "daily" else "[주간 PT 리포트]"
        return f"{title}\n\n" + (out if out else "리포트 생성 내용이 없습니다.")
    except Exception as e:
        return f"[오류] {kind} 리포트 실행 예외: {e}"


def save_text(text):
    """save_message.py 를 슬랙 소스로 호출하고 [기록 완료] stdout 반환."""
    try:
        res = subprocess.run(
            [sys.executable, str(BASE_DIR / "scripts/save_message.py"), "--source", "slack", text],
            capture_output=True, text=True,
        )
        if res.returncode != 0:
            return f"[기록 저장 실패]\n{res.stderr.strip()}"
        return res.stdout.strip()
    except Exception as e:
        return f"[기록 저장 예외] {e}"


def handle_text(channel, text):
    low = text.strip().lower()
    if low in HELP_CMDS:
        post(channel,
             "사용법\n- 운동/식단/체중을 자연스럽게 입력하세요.\n"
             "- `daily`(또는 일일리포트): 일일 리포트\n"
             "- `weekly`(또는 주간리포트): 주간 리포트\n"
             "- 사진을 올리면 운동/식단을 분석해 기록합니다.")
        return
    if low in DAILY_CMDS:
        post(channel, run_report("daily"))
        return
    if low in WEEKLY_CMDS:
        post(channel, run_report("weekly"))
        return

    # 일반 기록 저장 + AI 코칭
    saved = save_text(text)
    try:
        ai = generate_response(text)
    except Exception as e:
        ai = f"(코칭 생성 오류: {e})"
    parts = [p for p in (saved, ai) if p]
    post(channel, "\n\n".join(parts) if parts else "기록할 내용을 찾지 못했습니다.")


def download_slack_file(file_obj):
    """url_private_download 를 봇 토큰으로 받아 bytes + mime 반환."""
    url = file_obj.get("url_private_download") or file_obj.get("url_private")
    if not url:
        return None, None
    r = requests.get(url, headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}, timeout=30)
    r.raise_for_status()
    mime = file_obj.get("mimetype", "image/jpeg")
    return r.content, mime


def handle_files(channel, files, caption):
    images = [f for f in files if (f.get("mimetype", "").startswith("image/"))]
    if not images:
        return
    post(channel, "사진을 분석하고 있습니다. 잠시만 기다려 주세요...")
    try:
        image_bytes, mime = download_slack_file(images[0])
    except Exception as e:
        post(channel, f"사진 다운로드 중 오류: {e}")
        return
    if not image_bytes:
        post(channel, "사진 파일을 받지 못했습니다.")
        return
    try:
        raw = generate_image_response(image_bytes, mime_type=mime)
    except Exception as e:
        post(channel, f"사진 분석 중 오류: {e}")
        return

    # [기록 데이터] / [코칭 피드백] 파싱 (텔레그램 봇과 동일)
    db_text, coaching = "", ""
    if "[기록 데이터]" in raw:
        parts = raw.split("[코칭 피드백]", 1)
        db_text = parts[0].replace("[기록 데이터]", "").strip()
        coaching = parts[1].strip() if len(parts) > 1 else ""
    else:
        coaching = raw.strip()

    if caption and db_text:
        db_text += f"\n{caption}"
    elif caption and not db_text:
        db_text = caption

    saved = save_text(db_text) if db_text.strip() else ""
    out = [p for p in (saved, coaching) if p]
    post(channel, "\n\n".join(out) if out else "사진에서 기록할 내용을 찾지 못했습니다.")


def handle_event(event):
    # 봇/시스템 메시지, 편집/삭제 이벤트는 무시
    if event.get("type") != "message":
        return
    if event.get("bot_id") or event.get("subtype") in ("bot_message", "message_changed", "message_deleted"):
        return
    user = event.get("user")
    if not user or user == _BOT_USER_ID:
        return
    if SLACK_ALLOWED_USER and user != SLACK_ALLOWED_USER:
        return
    channel = event.get("channel")
    channel_type = event.get("channel_type")  # im, channel, group, mpim
    # 채널 제한: 지정 채널이면 그 채널만, 아니면 DM(im)은 항상 허용
    if SLACK_PT_CHANNEL and channel != SLACK_PT_CHANNEL and channel_type != "im":
        return

    files = event.get("files") or []
    text = (event.get("text") or "").strip()
    if files:
        handle_files(channel, files, text)
    elif text:
        handle_text(channel, text)


def process(client: SocketModeClient, req: SocketModeRequest):
    # 즉시 ack (슬랙 3초 재시도 방지) 후 백그라운드 처리
    client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
    if req.type != "events_api":
        return
    event = (req.payload or {}).get("event", {})
    ts = event.get("ts") or (req.payload or {}).get("event_id")
    if ts:
        with _seen_lock:
            if ts in _seen:
                return
            _seen.add(ts)
            if len(_seen) > 2000:
                _seen.clear()
    threading.Thread(target=handle_event, args=(event,), daemon=True).start()


def main():
    global _BOT_USER_ID
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        raise RuntimeError("SLACK_BOT_TOKEN / SLACK_APP_TOKEN 이 설정되지 않았습니다(.env 확인).")
    try:
        _BOT_USER_ID = _web.auth_test().get("user_id")
    except Exception as e:
        print(f"[slack] auth_test 실패: {e}", file=sys.stderr)

    sm = SocketModeClient(app_token=SLACK_APP_TOKEN, web_client=_web)
    sm.socket_mode_request_listeners.append(process)
    sm.connect()
    print("AI PT Slack 봇이 시작되었습니다 (Socket Mode).")
    if SLACK_PT_CHANNEL:
        post(SLACK_PT_CHANNEL, "AI PT 트레이너가 슬랙에서 시작되었습니다. 오늘 기록을 보내주세요. 💪")
    threading.Event().wait()


if __name__ == "__main__":
    main()
