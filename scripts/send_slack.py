"""Slack 발송 헬퍼 (send_telegram.py 의 슬랙 버전).

리포트/알림을 SLACK_PT_CHANNEL 로 보낸다. chat.postMessage 사용.
"""
import sys
from pathlib import Path

sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import requests
from scripts.config import SLACK_BOT_TOKEN, SLACK_PT_CHANNEL


def send_message(text, channel=None, thread_ts=None):
    """텍스트를 슬랙 채널에 보낸다. 실패 시 예외."""
    token = SLACK_BOT_TOKEN
    ch = channel or SLACK_PT_CHANNEL
    if not token or not ch:
        raise RuntimeError("Slack 설정(SLACK_BOT_TOKEN/SLACK_PT_CHANNEL)이 비어 있습니다.")
    payload = {
        "channel": ch,
        "text": text,
        "unfurl_links": False,
        "unfurl_media": False,
    }
    if thread_ts:
        payload["thread_ts"] = thread_ts
    res = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json; charset=utf-8"},
        json=payload,
        timeout=20,
    )
    res.raise_for_status()
    data = res.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack 전송 실패: {data.get('error')}")
    return data


if __name__ == "__main__":
    send_message("AI PT 트레이너 Slack 발송 테스트입니다.")
    print("전송 완료")
