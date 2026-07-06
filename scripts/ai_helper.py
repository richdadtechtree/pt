import os
from google import genai
from scripts.config import GEMINI_API_KEY, GEMINI_MODEL, BASE_DIR

# 새로운 클라이언트 초기화
client = genai.Client(api_key=GEMINI_API_KEY)

def load_markdown_file(filename):
    file_path = BASE_DIR / filename
    if file_path.exists():
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"{filename} 읽기 오류: {e}")
    return ""

def generate_response(prompt):
    # USER.md와 SOUL.md 파일 읽기 시도
    user_info = load_markdown_file("USER.md")
    soul_info = load_markdown_file("SOUL.md")
    
    # 기본 프로필 백업 (파일이 없을 경우 대비)
    default_user_info = """
    - 이름: 이형준
    - 운동 목적: 체지방 감량과 근력 향상
    - 운동 수준: 초보자 (주 3회 가능)
    - 장소/선호: 헬스장, 테니스, 야외 러닝
    """
    
    default_soul_info = """
    - 역할: 20년 차 베테랑 전문 PT 트레이너 (건강/운동 코칭만 답함. 투자/뉴스 질문은 신문 봇에게 패스)
    - 코칭: 2~3일 안 움직이면 경각심을 주고 불량 식단 시 구체적으로 경고
    - 성격: 차분하고 지속 가능한 루틴 우선, 실천 가능성 중시
    - 말투: 한국어로 짧고 명확하게, 5줄 이내 답변
    """
    
    user_profile = user_info if user_info.strip() else default_user_info
    bot_soul = soul_info if soul_info.strip() else default_soul_info

    try:
        full_prompt = f"""
당신은 다음 규칙과 프로필에 기반하여 작동하는 AI PT 코치입니다.

[사용자 프로필 정보]
{user_profile}

[코칭 스타일 및 규칙 (SOUL)]
{bot_soul}

위 규칙과 성격, 말투를 엄격하게 준수하여 사용자의 입력에 답변해 주세요.

사용자의 입력: {prompt}
"""
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"AI 답변 생성 중 오류가 발생했습니다: {e}"