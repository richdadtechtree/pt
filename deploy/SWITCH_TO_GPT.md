# 전체 모델을 GPT로 전환

Gemini 사용을 중단하고 오픈클로 에이전트 + pt_system 리포트를 모두 OpenAI(GPT)로 통일한다.
OpenAI 키는 유출되지 않았으므로 **재발급 불필요** — 기존 키를 그대로 쓴다.

## 이미 코드에서 바뀐 것 (pt 레포)

| 파일 | 변경 |
|---|---|
| `scripts/config.py` | `GEMINI_*` 제거 → `OPENAI_API_KEY`, `OPENAI_MODEL`(기본 `gpt-4o-mini`) |
| `scripts/llm.py` (신규) | OpenAI 공통 호출 헬퍼 `generate_text` / `generate_vision` |
| `reports/daily_report.py`, `weekly_report.py` | Gemini 직접호출 → `generate_text` |
| `scripts/ai_helper.py` | GPT로 전환(텍스트/이미지). 페르소나 로직은 유지 |
| `scripts/test_gemini.py*` | 삭제 |

## 서버 반영 (pt_system)

```bash
cd ~/pt_system
git fetch origin claude/newspaper-briefing-openclo-fzhmn7
git checkout origin/claude/newspaper-briefing-openclo-fzhmn7 -- \
  scripts/config.py scripts/llm.py scripts/ai_helper.py scripts/telegram_polling.py \
  reports/daily_report.py reports/weekly_report.py
git rm -q scripts/test_gemini.py scripts/test_gemini.py.save 2>/dev/null || true

# OpenAI 파이썬 패키지 설치
venv/bin/pip install openai

# .env 편집: Gemini 줄 제거 + OpenAI 추가
nano .env
#   (삭제) GEMINI_API_KEY=..., GEMINI_MODEL=...
#   (추가) OPENAI_API_KEY=sk-...        ← 오픈클로가 쓰는 기존 OpenAI 키와 동일한 값
#   (추가) OPENAI_MODEL=gpt-4o-mini
```

> OpenAI 키를 모르면 https://platform.openai.com/api-keys 에서 확인/발급.
> (이건 재발급이 아니라 단순 조회/신규 — 보안 이슈 아님)

검증:
```bash
venv/bin/python reports/daily_report.py     # GPT가 생성한 리포트가 출력되면 성공
```

## 오픈클로 에이전트 모델 변경 (openclaw.json)

`~/.openclaw/openclaw.json` 의 `agents.defaults.model` / `models` 를 OpenAI로 교체:

```jsonc
"model": {
  "primary": "openai/gpt-4o-mini",
  "fallbacks": ["openai/gpt-4o"]
},
"models": {
  "openai/gpt-4o-mini": {},
  "openai/gpt-4o": {}
}
```

- `auth.profiles` 의 `google:default` 는 지워도 되고 둬도 무방(안 쓰이면 무시됨).
  대신 **OpenAI 인증이 등록돼 있어야** 한다. 아침/저녁 신문 브리핑 cron이 이미
  `openai/gpt-4o-mini` 로 정상 동작 중이므로 OpenAI 인증은 이미 있는 상태다.
- 반영:
  ```bash
  openclaw gateway restart
  openclaw gateway status
  ```
- 신문봇/PT봇에 메시지를 보내 GPT로 정상 응답하는지 확인.

## 참고

- 신문 브리핑 cron(morning/evening)은 원래 `openai/gpt-4o-mini` 라 변경 불필요.
- PT 일일/주간 리포트 cron은 모델을 따로 지정 안 했으므로, 위 default 변경으로 자동 GPT.
- 모델명은 계정에서 사용 가능한 것으로 조정 가능(`gpt-4o`, `gpt-4o-mini`, `gpt-4.1` 등).
