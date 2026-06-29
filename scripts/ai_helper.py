import os
from google import genai
from scripts.config import GEMINI_API_KEY, GEMINI_MODEL

# 새로운 클라이언트 초기화
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_response(prompt):
    try:
        full_prompt = f"""
        당신은 10년 차 베테랑 전문 PT 트레이너입니다. 
        사용자의 운동 기록이나 질문에 대해 따뜻하고 전문적으로 답변하세요.
        부위별 운동 추천을 요청받으면 구체적인 종목 3가지를 추천하세요.
        사용자의 입력: {prompt}
        """
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=full_prompt,
        )
        return response.text
    except Exception as e:
        return f"AI 답변 생성 중 오류가 발생했습니다: {e}"