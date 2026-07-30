"""OpenAI(GPT) 공통 호출 헬퍼.

리포트 생성(daily/weekly)과 AI 코칭 응답(ai_helper)에서 함께 쓴다.
설정은 scripts.config 의 OPENAI_API_KEY / OPENAI_MODEL 을 사용.
"""
import base64

from openai import OpenAI

from scripts.config import OPENAI_API_KEY, OPENAI_MODEL

_client = None


def _get_client():
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 가 설정되지 않았습니다(.env 확인).")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def generate_text(prompt, model=None):
    """텍스트 프롬프트 → 텍스트 응답."""
    resp = _get_client().chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


def generate_vision(image_bytes, prompt, mime_type="image/jpeg", model=None):
    """이미지 + 프롬프트 → 텍스트 응답 (GPT 비전)."""
    b64 = base64.b64encode(image_bytes).decode()
    resp = _get_client().chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
                ],
            }
        ],
    )
    return resp.choices[0].message.content
