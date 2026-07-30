"""LLM 공통 호출 헬퍼 (Gemini / OpenAI 전환 가능).

리포트 생성(daily/weekly)과 사진 분석·코칭(ai_helper)에서 함께 쓴다.
공급자는 scripts.config 의 LLM_PROVIDER("gemini" 또는 "openai")로 결정한다.
.env 의 LLM_PROVIDER 한 줄만 바꾸면 코드 수정 없이 전환된다.
"""
import base64

from scripts.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY, GEMINI_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
)

_gemini_client = None
_openai_client = None


# ───────────────────────── 공개 API ─────────────────────────
def generate_text(prompt, model=None):
    """텍스트 프롬프트 → 텍스트 응답."""
    if LLM_PROVIDER == "openai":
        return _openai_text(prompt, model)
    return _gemini_text(prompt, model)


def generate_vision(image_bytes, prompt, mime_type="image/jpeg", model=None):
    """이미지 + 프롬프트 → 텍스트 응답 (비전)."""
    if LLM_PROVIDER == "openai":
        return _openai_vision(image_bytes, prompt, mime_type, model)
    return _gemini_vision(image_bytes, prompt, mime_type, model)


# ───────────────────────── Gemini ─────────────────────────
def _gem():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY 가 설정되지 않았습니다(.env 확인).")
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


def _gemini_text(prompt, model=None):
    resp = _gem().models.generate_content(
        model=model or GEMINI_MODEL,
        contents=prompt,
    )
    return resp.text


def _gemini_vision(image_bytes, prompt, mime_type, model=None):
    from google.genai import types
    resp = _gem().models.generate_content(
        model=model or GEMINI_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
    )
    return resp.text


# ───────────────────────── OpenAI ─────────────────────────
def _oai():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 가 설정되지 않았습니다(.env 확인).")
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


def _openai_text(prompt, model=None):
    resp = _oai().chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


def _openai_vision(image_bytes, prompt, mime_type, model=None):
    b64 = base64.b64encode(image_bytes).decode()
    resp = _oai().chat.completions.create(
        model=model or OPENAI_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
            ],
        }],
    )
    return resp.choices[0].message.content
