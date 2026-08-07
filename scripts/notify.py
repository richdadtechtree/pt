"""통합 알림 (Slack 우선, Telegram 폴백).

리포트 전송(reports/send_*.py)이 채널에 상관없이 이걸 부르면,
NOTIFY_CHANNEL(기본: 슬랙 토큰 있으면 slack) 에 따라 알맞은 채널로 보낸다.
텔레그램에서 슬랙으로 갈아타는 동안 코드 한 곳만 보게 하려는 목적.
"""
import sys
from pathlib import Path

sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.config import NOTIFY_CHANNEL, SLACK_BOT_TOKEN, SLACK_PT_CHANNEL


def send_message(text):
    """설정된 채널로 텍스트 전송. 슬랙 우선, 실패/미설정 시 텔레그램 폴백."""
    prefer_slack = NOTIFY_CHANNEL == "slack" and SLACK_BOT_TOKEN and SLACK_PT_CHANNEL
    if prefer_slack:
        try:
            from scripts.send_slack import send_message as slack_send
            return slack_send(text)
        except Exception as e:
            print(f"[notify] 슬랙 전송 실패, 텔레그램으로 폴백: {e}", file=sys.stderr)
    from scripts.send_telegram import send_message as tg_send
    return tg_send(text)


if __name__ == "__main__":
    send_message("AI PT 트레이너 통합 알림 테스트입니다.")
    print("전송 완료")
