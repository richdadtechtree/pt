"""
텔레그램으로 받은 운동/식단 사진을 OpenAI 비전으로 분석해 DB에 저장한다.

오픈클로 pt-trainer 에이전트가 사진을 받으면 이 스크립트를 exec로 호출한다:
    python3 /home/ubuntu/pt_system/scripts/analyze_photo.py [이미지경로]
- 경로를 주면 그 이미지를, 안 주면 ~/.openclaw/media/inbound 의 '가장 최근 이미지'를 분석한다.
- 모델의 비전 입력에 의존하지 않고, 파일을 직접 읽어 OpenAI 비전으로 분석하므로 확실하다.
"""
import os
import sys
import glob
from pathlib import Path

sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.ai_helper import generate_image_response
from scripts.save_message import (
    save_raw_message,
    save_workout_if_present,
    save_meal_if_present,
    save_vitals_if_present,
)

INBOUND_DIRS = [
    os.path.expanduser("~/.openclaw/media/inbound"),
    "/home/ubuntu/.openclaw/media/inbound",
]
IMAGE_EXTS = ("*.jpg", "*.jpeg", "*.png", "*.webp")


def newest_image():
    files = []
    for d in INBOUND_DIRS:
        if os.path.isdir(d):
            for ext in IMAGE_EXTS:
                files += glob.glob(os.path.join(d, ext))
    return max(files, key=os.path.getmtime) if files else None


def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else newest_image()
    if not img_path or not os.path.exists(img_path):
        print("[사진 분석 실패] 분석할 이미지 파일을 찾지 못했습니다.")
        sys.exit(1)

    mime = "image/png" if img_path.lower().endswith(".png") else "image/jpeg"
    with open(img_path, "rb") as f:
        image_bytes = f.read()

    raw = generate_image_response(image_bytes, mime_type=mime)

    # [기록 데이터] / [코칭 피드백] 파싱
    db_text, coaching = "", ""
    if "[기록 데이터]" in raw:
        parts = raw.split("[코칭 피드백]", 1)
        db_text = parts[0].replace("[기록 데이터]", "").strip()
        coaching = parts[1].strip() if len(parts) > 1 else ""
    else:
        coaching = raw.strip()

    # DB 저장
    saved = ""
    if db_text:
        save_raw_message(db_text)
        w = save_workout_if_present(db_text)
        m = save_meal_if_present(db_text)
        v = save_vitals_if_present(db_text)
        saved = (
            "[기록 완료]\n"
            f"- 운동: {w}개\n"
            f"- 식단: {m}개\n"
            f"- 바이탈: {'저장됨' if v else '없음'}"
        )

    blocks = [b for b in (db_text, saved, coaching) if b]
    print("\n\n".join(blocks) if blocks else "[사진 분석 실패] 분석 결과가 비어 있습니다.")


if __name__ == "__main__":
    main()
