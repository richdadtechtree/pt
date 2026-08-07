import subprocess
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts.config import BASE_DIR

def run_cmd(args):
    res = subprocess.run(args, cwd=BASE_DIR, capture_output=True, text=True)
    return res

def check_and_update():
    # 1. 원격 저장소 정보 갱신
    run_cmd(["git", "fetch", "origin", "main"])
    
    # 2. 로컬과 원격 해시 비교
    local_hash = run_cmd(["git", "rev-parse", "HEAD"]).stdout.strip()
    remote_hash = run_cmd(["git", "rev-parse", "origin/main"]).stdout.strip()
    
    if local_hash == remote_hash:
        # 변경 사항 없음
        return
        
    print(f"새로운 업데이트 발견! {local_hash[:7]} -> {remote_hash[:7]}")
    
    # 3. 변경 대상 파일 파악 (어떤 서비스가 재시작되어야 하는지 분석)
    diff_res = run_cmd(["git", "diff", "--name-only", "HEAD", "origin/main"])
    changed_files = diff_res.stdout.splitlines()
    
    # 4. Pull 수행
    pull_res = run_cmd(["git", "pull", "origin", "main"])
    if pull_res.returncode != 0:
        print(f"Git Pull 에러 발생:\n{pull_res.stderr}")
        return
        
    print("Git pull 성공적으로 수행 완료.")
    
    # 5. 변경된 파일에 따라 서비스 선택적 재시작
    restart_bot = False
    restart_dashboard = False

    for f in changed_files:
        if f.startswith("scripts/") or f.startswith("reports/") or f == "init_db.py":
            restart_bot = True
        if f.startswith("dashboard/") or f == "init_db.py":
            restart_dashboard = True

    if restart_bot:
        # 슬랙 봇으로 전환됨. pt-slack 이 있으면 재시작, 없으면 조용히 넘어가고
        # (구성에 따라) 텔레그램 봇도 존재하면 재시작. 활성화된 서비스만 반응한다.
        for svc in ("pt-slack.service", "pt-telegram.service"):
            print(f"봇 서비스({svc}) 재시작 시도...")
            res = subprocess.run(["sudo", "systemctl", "restart", svc])
            if res.returncode == 0:
                print(f"{svc} 재시작 완료.")
            else:
                print(f"{svc} 재시작 건너뜀(미설치/비활성).")

    if restart_dashboard:
        print("대시보드 서비스(pt-dashboard.service) 재시작 중...")
        res = subprocess.run(["sudo", "systemctl", "restart", "pt-dashboard.service"])
        if res.returncode == 0:
            print("대시보드 서비스가 정상적으로 재시작되었습니다.")
        else:
            print("대시보드 서비스 재시작 실패.")

if __name__ == "__main__":
    check_and_update()
