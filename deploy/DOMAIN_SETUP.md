# PT 대시보드에 DuckDNS 도메인 + HTTPS 붙이기

개인 건강 기록이므로 **도메인 + HTTPS + 로그인**을 한 세트로 적용한다.

최종 결과: `https://<서브도메인>.duckdns.org` 로 접속 → 로그인 → 대시보드.

---

## 0단계. 서버 공인 IP 확인

```bash
curl -s ifconfig.me; echo
```

## 1단계. DuckDNS 도메인 발급 (브라우저)

1. https://www.duckdns.org 접속 → Google/GitHub 로 로그인
2. `sub domain` 칸에 원하는 이름 입력(예: `richdad-pt`) → **add domain**
   → `richdad-pt.duckdns.org` 생성됨
3. 그 줄의 `current ip` 칸에 0단계에서 확인한 공인 IP 입력 → **update ip**
4. 페이지 상단의 **token** 값을 복사해 둔다 (비밀값)

## 2단계. IP 자동 갱신 cron (Oracle IP가 바뀌어도 도메인 유지)

토큰이 들어가므로 **레포가 아니라** `~/duckdns/` 에 만든다(깃에 커밋 금지).

```bash
mkdir -p ~/duckdns
cat > ~/duckdns/duck.sh <<'EOF'
#!/bin/sh
SUB="여기에_서브도메인"    # 예: richdad-pt
TOKEN="여기에_토큰"
echo url="https://www.duckdns.org/update?domains=${SUB}&token=${TOKEN}&ip=" \
  | curl -k -o ~/duckdns/duck.log -K -
EOF
chmod 700 ~/duckdns/duck.sh
~/duckdns/duck.sh && cat ~/duckdns/duck.log   # "OK" 가 떠야 성공

# 5분마다 자동 갱신
( crontab -l 2>/dev/null; echo "*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1" ) | crontab -
```

## 3단계. 방화벽 열기 (80, 443) — Oracle은 이중이라 둘 다

1. **Oracle Cloud 콘솔** → 인스턴스 → VCN → Security List(또는 NSG) →
   Ingress Rule 추가: Source `0.0.0.0/0`, TCP **80**, **443**
2. 서버 내부 방화벽:
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   # iptables 기반이면:
   # sudo iptables -I INPUT -p tcp --dport 80  -j ACCEPT
   # sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
   ```

## 4단계. Nginx 리버스 프록시 + 로그인

```bash
sudo apt-get update
sudo apt-get install -y nginx apache2-utils

# 로그인 계정 생성 (ID: hyungjun, PW 입력 프롬프트)
sudo htpasswd -c /etc/nginx/.htpasswd hyungjun

# 템플릿 복사 후 서브도메인 치환
sudo cp ~/pt_system/deploy/nginx-pt-dashboard.conf.template \
        /etc/nginx/sites-available/pt-dashboard
sudo sed -i 's/SUBDOMAIN/여기에_서브도메인/g' /etc/nginx/sites-available/pt-dashboard
sudo ln -sf /etc/nginx/sites-available/pt-dashboard /etc/nginx/sites-enabled/pt-dashboard

sudo nginx -t && sudo systemctl reload nginx
```

이 시점에 `http://<서브도메인>.duckdns.org` 로 들어가면 로그인 후 대시보드가 보인다(아직 http).

## 5단계. HTTPS 인증서 (Let's Encrypt, 무료·자동갱신)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d 여기에_서브도메인.duckdns.org
# 이메일 입력, 약관 동의, "Redirect(HTTP→HTTPS)" 선택
```

끝나면 `https://<서브도메인>.duckdns.org` 로 접속된다. 인증서는 certbot 타이머가 자동 갱신한다.

## 6단계. 마무리·보안 점검

- 대시보드는 계속 `127.0.0.1:5000` 뒤에서 돌고, 외부는 오직 Nginx(80/443)로만 열린다.
  5000 포트는 Oracle Security List에 넣지 않는다(외부 직접 노출 금지).
- 폰에서 `https://<서브도메인>.duckdns.org` 접속 → 공유 메뉴 → **홈 화면에 추가** 하면
  앱 아이콘처럼 쓸 수 있다.
- 도메인이 생겼으니, 매일 캡처를 텔레그램으로 보내던 cron(`capture_dashboard.py`)은
  꺼도 되고 병행해도 된다.

## 점검 명령

```bash
nslookup 여기에_서브도메인.duckdns.org      # 서버 공인 IP가 나와야 함
curl -sI https://여기에_서브도메인.duckdns.org   # 401(로그인 요구) 또는 200
sudo systemctl status nginx --no-pager | head -5
```
