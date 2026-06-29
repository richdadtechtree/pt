from pathlib import Path
import subprocess
import sys
sys.path.append(str(Path("/home/ubuntu/pt_system")))
from scripts.send_telegram import send_message
result = subprocess.run(
    ["python3", "/home/ubuntu/pt_system/reports/daily_report.py"],
    capture_output=True,
    text=True,
    check=True,
)
send_message("[일일 PT 리포트]\n\n" + result.stdout.strip()) print("일일 리포트 전송 완료")
