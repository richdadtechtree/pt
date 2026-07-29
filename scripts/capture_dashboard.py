"""
대시보드 화면을 헤드리스 크롬(Playwright)으로 캡처해서 텔레그램으로 전송한다.

대시보드는 Chart.js(canvas) + CDN 스크립트를 사용하므로 실제 브라우저 렌더링이 필요하다.
매일 cron으로 실행하는 것을 전제로 한다.

사전 준비(최초 1회):
    ~/pt_system/venv/bin/pip install playwright
    ~/pt_system/venv/bin/playwright install chromium
    sudo ~/pt_system/venv/bin/playwright install-deps chromium   # 시스템 라이브러리

수동 실행:
    ~/pt_system/venv/bin/python ~/pt_system/scripts/capture_dashboard.py
"""
import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

import requests
from scripts.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

DASHBOARD_URL = "http://127.0.0.1:5000/"
SHOT_PATH = Path("/tmp/pt_dashboard.png")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def capture(url: str, out_path: Path) -> None:
    """헤드리스 크롬으로 페이지를 렌더링하고 전체 화면을 PNG로 저장한다."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 900},
                                device_scale_factor=2)
        # networkidle: CDN 스크립트(Chart.js, lucide) 로드 완료까지 대기
        page.goto(url, wait_until="networkidle", timeout=60_000)
        # Chart.js 애니메이션이 끝나도록 잠시 더 대기
        page.wait_for_timeout(2500)
        page.screenshot(path=str(out_path), full_page=True)
        browser.close()


def send_photo(photo_path: Path, caption: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("Telegram 설정(TELEGRAM_BOT_TOKEN/CHAT_ID)이 비어 있습니다.")
    with open(photo_path, "rb") as f:
        res = requests.post(
            f"{API_URL}/sendPhoto",
            data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
            files={"photo": f},
            timeout=60,
        )
    # 이미지가 너무 크거나 비율 제한에 걸리면 문서로 재전송(무압축)
    if not res.ok:
        with open(photo_path, "rb") as f:
            res = requests.post(
                f"{API_URL}/sendDocument",
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": caption},
                files={"document": f},
                timeout=120,
            )
    res.raise_for_status()


def send_text(text: str) -> None:
    requests.post(
        f"{API_URL}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
        timeout=15,
    )


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    caption = f"[PT 대시보드] {today}"
    try:
        capture(DASHBOARD_URL, SHOT_PATH)
        send_photo(SHOT_PATH, caption)
        print(f"전송 완료: {SHOT_PATH} -> Telegram")
    except Exception as e:
        # 실패해도 조용히 죽지 않고 텔레그램으로 사유를 알린다
        msg = f"[PT 대시보드 캡처 실패] {today}\n{type(e).__name__}: {e}"
        print(msg, file=sys.stderr)
        try:
            send_text(msg)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
