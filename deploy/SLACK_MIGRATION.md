# 텔레그램 → 슬랙 이전 (PT 봇)

PT 트레이너 대화·기록·리포트를 **슬랙**으로 옮긴다. DB / 대시보드 / 리포트 생성 로직은
그대로 두고, **입력 채널만 텔레그램 → 슬랙**으로 교체한다.

## 무엇이 바뀌나
| | 이전(텔레그램) | 이후(슬랙) |
|---|---|---|
| 대화 봇 | `scripts/telegram_polling.py` (`pt-telegram.service`) | `scripts/slack_bot.py` (`pt-slack.service`) |
| 저장 | `save_message.py` (source=telegram) | 동일 스크립트, `--source slack` |
| 리포트 전송 | `send_telegram.py` | `notify.py` → 슬랙 우선 |
| DB / 대시보드 | `pt_data.db` / Flask :5000 | **변경 없음** |

- 슬랙 봇은 **Socket Mode**(아웃바운드 웹소켓)라 공개 URL 이 필요 없다.
- 기존 파이프라인(`save_message.py`, `ai_helper.py`, `reports/*`)을 100% 재사용 → 대시보드/리포트는 즉시 그대로 작동.

---

## 0) 전제: 전용 슬랙 앱 (openclaw 슬랙과 분리 권장)

openclaw 게이트웨이가 이미 쓰는 슬랙 앱과 **같은 앱을 쓰면 두 봇이 같은 메시지에 이중 반응**한다.
PT 봇 전용 슬랙 앱을 새로 만드는 것을 권장한다.

1. <https://api.slack.com/apps> → **Create New App** → From scratch → 워크스페이스 선택
2. **Socket Mode** 켜기 → App-Level Token 생성(스코프 `connections:write`) → **`xapp-...` 복사**
3. **OAuth & Permissions → Bot Token Scopes** 추가:
   `chat:write`, `files:read`, `channels:history`, `groups:history`, `im:history`, `mpim:history`
4. **Event Subscriptions → Subscribe to bot events**:
   `message.channels`, `message.groups`, `message.im`, `message.mpim`
5. **Install to Workspace** → **Bot User OAuth Token `xoxb-...` 복사**
6. PT 채널을 하나 만들고(예: `#pt`) 봇을 초대(`/invite @봇이름`). 채널 ID(`C...`)는
   채널명 우클릭 → 링크 복사에서 확인.
7. (선택) 내 유저 ID(`U...`)만 응답하게 하려면 프로필 → 멤버 ID 복사.

> DM 으로 대화하려면 앱 **Home → Messages Tab** 을 켜고 봇에게 DM. (`SLACK_PT_CHANNEL` 을
> 비워도 DM 은 항상 응답한다.)

---

## 1) 코드 반영 + 패키지

이 변경은 `claude/slack-migration` 브랜치에 있다. 확인 후 **main 에 머지**하면
`auto_update.py` 가 자동 pull·재시작한다. 먼저 서버에서 직접 적용해 검증해도 된다:

```bash
cd ~/pt_system
git fetch origin claude/slack-migration
git checkout origin/claude/slack-migration -- \
  scripts/slack_bot.py scripts/send_slack.py scripts/notify.py \
  scripts/config.py scripts/save_message.py scripts/auto_update.py \
  reports/send_daily_report.py reports/send_weekly_report.py deploy/pt-slack.service

venv/bin/pip install slack_sdk
```

## 2) .env 추가

```bash
nano ~/pt_system/.env
```
```
SLACK_BOT_TOKEN=xoxb-...        # Bot User OAuth Token
SLACK_APP_TOKEN=xapp-...        # App-Level Token (Socket Mode)
SLACK_PT_CHANNEL=C0XXXXXXX      # PT 채널 ID (리포트/시작 알림 대상). DM만 쓸거면 비워도 됨
SLACK_ALLOWED_USER=U0XXXXXXX    # (선택) 이 유저만 응답. 비우면 전체 허용
# NOTIFY_CHANNEL=slack          # (기본값 자동: SLACK_BOT_TOKEN 있으면 slack)
```

## 3) 슬랙 봇 서비스 등록

```bash
sudo cp ~/pt_system/deploy/pt-slack.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pt-slack
journalctl -u pt-slack -f            # "시작되었습니다 (Socket Mode)" 확인
```
슬랙 PT 채널(또는 DM)에 `오늘 벤치 40kg 10회 5세트, 점심 닭가슴살, 체중 74kg 수면 7시간`
처럼 보내 **[기록 완료] + 코칭 답변**이 오는지 확인. `daily` / `weekly` 도 확인.

## 4) 리포트 크론 (텔레그램 → 슬랙)

리포트 senders 는 `notify.py`(슬랙 우선)로 바뀌었으므로 **크론은 그대로 두면 자동으로 슬랙 전송**된다.
현재 크론이 `send_daily_report.py`/`send_weekly_report.py` 를 호출하는지만 확인:
```bash
crontab -l | grep -i report
```
없으면 추가(예: 매일 21:00 일일, 일요일 20:00 주간):
```
0 21 * * *  cd /home/ubuntu/pt_system && venv/bin/python reports/send_daily_report.py
0 20 * * 0  cd /home/ubuntu/pt_system && venv/bin/python reports/send_weekly_report.py
```

## 5) 텔레그램 중단

```bash
sudo systemctl disable --now pt-telegram      # 폴링 봇 정지
# 대시보드 캡처를 텔레그램으로 보내던 크론이 있으면 주석 처리
crontab -l | grep -i capture_dashboard
```
> `capture_dashboard.py` 는 텔레그램 전용이라 슬랙 버전이 필요하면 별도 요청. 지금은 웹
> 대시보드(`mystatus-btr.duckdns.org`)로 직접 보면 되므로 캡처 전송은 꺼도 무방.

## 6) 정리 (선택)

- 예전 잔재 빈 DB 제거(대시보드는 절대경로 `pt_data.db` 를 읽으므로 무해하지만 혼동 방지):
  ```bash
  ls -l ~/pt_system/dashboard/pt_data.db && rm -f ~/pt_system/dashboard/pt_data.db
  ```

---

## 검증 체크리스트
- [ ] `journalctl -u pt-slack -f` 에 오류 없이 연결됨
- [ ] 슬랙에 기록 메시지 → `[기록 완료]` + 코칭 답변
- [ ] `daily` / `weekly` → 리포트 회신
- [ ] 사진 업로드 → 분석·기록
- [ ] 대시보드(`mystatus-btr.duckdns.org`)에 방금 기록 반영
- [ ] `pt-telegram` 정지, 이중 응답 없음
