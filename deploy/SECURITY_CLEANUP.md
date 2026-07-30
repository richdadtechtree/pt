# 보안 정리 런북 (openclaw 레포)

`richdadtechtree/openclaw` 가 public 으로 노출돼 비밀정보/개인 대화가 깃에 올라가 있었다.
`pt` 레포는 점검 결과 **깨끗함(조치 불필요)**. 아래는 openclaw 레포 전용.

> 핵심 원칙: **노출된 토큰은 이미 유출된 것으로 간주 → "재발급"이 진짜 해결책.**
> 깃 히스토리 삭제는 마무리이지, 그것만으로는 안전해지지 않는다. PART A를 반드시 먼저.

노출된 항목(모두 `openclaw.json.bak*` 안):
- 텔레그램 봇 토큰 2개 (신문봇 `default`, PT봇 `pt`)
- 게이트웨이 인증 토큰 (`gateway.auth.token`)
- Brave 검색 API 키

> ✅ 커밋 전체 스캔 결과 **Google/Gemini 및 OpenAI API 키 원문은 깃에 올라간 적 없음**
> (오픈클로 secret store에 별도 저장 — `credentials/` 는 추적 안 됨).
> 따라서 위 3종만 재발급하면 되고, **OpenAI 키는 재발급 불필요**.
> Gemini 키는 유출은 아니지만 어차피 안 쓸 거라 삭제 권장(A-4).

---

## PART A. 유출된 비밀정보 재발급 (가장 중요)

재발급 대상은 **텔레그램 봇 2개 · 게이트웨이 토큰 · Brave 키** 3종뿐.
(OpenAI 키는 유출 안 됐으니 그대로 사용, Gemini 키는 삭제만.)

### A-1. 텔레그램 봇 토큰 2개
1. 텔레그램 **@BotFather** → `/mybots` → 신문봇 선택 → **API Token → Revoke current token** → 새 토큰 복사
2. PT봇도 동일하게 revoke + 새 토큰
3. 서버에서 `~/.openclaw/openclaw.json` 의
   `channels.telegram.accounts.default.botToken` / `...pt.botToken` 을 새 토큰으로 교체
4. PT봇 토큰은 `~/pt_system/.env` 의 `TELEGRAM_BOT_TOKEN` 에도 쓰이므로 같이 교체
   (대시보드 캡처 전송 `capture_dashboard.py` 가 사용)

### A-2. 게이트웨이 인증 토큰
```bash
openssl rand -hex 24    # 새 토큰 생성
```
→ `~/.openclaw/openclaw.json` 의 `gateway.auth.token` 값을 이걸로 교체.

### A-3. Brave 검색 API 키
Brave Search API 대시보드에서 키 **재발급** → `~/.openclaw/openclaw.json` 의
`plugins.entries.brave.config.webSearch.apiKey` 교체.

### A-4. Google/Gemini API 키 (유출 아님 — 삭제만)
Gemini는 더 이상 쓰지 않으므로 유출 여부와 무관하게 정리한다.
https://aistudio.google.com/apikey → 기존 키 **삭제(Delete)** →
`~/pt_system/.env` 의 `GEMINI_*` 줄 제거(이미 OpenAI로 전환됨).

> OpenAI 키는 재발급 대상이 아니다. 전 모델을 GPT로 전환하는 방법은
> `deploy/SWITCH_TO_GPT.md` 참고.

### A-5. 반영
```bash
openclaw gateway restart
openclaw gateway status          # running 확인
# 텔레그램 신문봇/PT봇에 아무 메시지나 보내 정상 응답 확인
```

---

## PART B. 깃에서 위험 파일 제거 (레포 새로 만들기 = 가장 확실)

개인 백업 레포라 히스토리 보존 가치가 없다. **레포 삭제 후 깨끗하게 새로** 올리는 것이
남은 캐시/옛 커밋까지 100% 없애는 가장 확실한 방법.

### B-1. 통째로 백업 (되돌릴 안전장치)
```bash
tar czf ~/openclaw-backup-$(date +%F).tar.gz -C ~ .openclaw
ls -lh ~/openclaw-backup-*.tar.gz
```

### B-2. GitHub 에서 레포 삭제
github.com/richdadtechtree/openclaw → **Settings → 맨 아래 Danger Zone → Delete this repository**
그다음 같은 이름 `openclaw` 로 **새 레포 생성 (반드시 Private!)**, README 등 체크 해제(빈 레포).

### B-3. 새 .gitignore 작성
```bash
cd ~/.openclaw
cat > .gitignore <<'EOF'
# ── 비밀정보 / 설정(토큰 포함) ──
openclaw.json
openclaw.json.*
*.bak
*.bak.*
.env
.env.*
credentials/
identity/

# ── 런타임 상태 / 개인 데이터 ──
agents/*/sessions/
agents/*/memory/
workspace/memory/
memory/
tasks/
cron/runs/
media/

# ── DB / 로그 / 캐시 ──
*.sqlite
*.sqlite-*
*.sqlite3
*.log
__pycache__/
node_modules/
npm/node_modules/
venv/
.venv/
EOF
```

### B-4. 옛 히스토리 완전 삭제 + 새 히스토리
```bash
cd ~/.openclaw
rm -rf .git
git init
git add -A

# ⚠️ 안전 게이트: 위험 파일이 안 잡히는지 반드시 확인
git ls-files | grep -iE 'session|\.bak|\.sqlite|openclaw\.json|token|\.env|^media/' \
  && echo "⚠️ 위험파일 남음 → .gitignore 수정 후 git rm --cached 재실행" \
  || echo "✅ 위험파일 없음 — 진행 OK"
```
"✅ 위험파일 없음" 이 떠야 다음으로.

```bash
git commit -m "clean init: exclude secrets and runtime state"
git branch -M main
git remote remove origin 2>/dev/null
git remote add origin https://github.com/richdadtechtree/openclaw.git
git push -u origin main
```

> 새 레포에는 유용한 설정만 올라간다:
> `agents/*/AGENTS.md·SOUL.md·USER.md·TOOLS.md·INTEGRATION.md`, `workspace/*.md`,
> `workspace/news_fetcher.py`, `cron/jobs.json`, `requirements.txt`, `plugin-skills/` 등.

---

## PART C. 검증
```bash
# 새 레포가 private 인지, 위험 파일이 안 올라갔는지
git ls-files | wc -l                       # 599 → 60~70개 수준으로 줄어야 정상
git ls-files | grep -iE 'session|\.bak|\.sqlite|openclaw\.json' || echo "✅ clean"
```
GitHub 웹에서 레포 우측에 **Private** 배지 확인. `openclaw.json.bak` 등이 안 보이면 완료.

---

## 참고
- 레포 삭제가 부담되면 대안: 삭제 없이 `rm -rf .git && git init` 후 **force push** +
  옛 원격 브랜치 전부 삭제(`git push origin --delete <브랜치>`). 단, GitHub가 옛 커밋
  SHA를 잠시 캐시할 수 있어 삭제-재생성보다 덜 확실하다. → 그래서 PART B(삭제 후 생성) 추천.
- 이후 정기 백업이 필요하면, 이 clean 상태에서 가끔 `git add -A && git commit && git push`
  하면 .gitignore 덕분에 비밀/런타임 파일은 자동 제외된다.
