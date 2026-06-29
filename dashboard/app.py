from pathlib import Path
import sys

# 프로젝트 경로 설정
sys.path.append(str(Path("/home/ubuntu/pt_system")))

from flask import Flask, render_template_string
from scripts.db import get_conn

app = Flask(__name__)

# 대시보드 HTML 템플릿
HTML = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI PT 대시보드</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f7f9; color: #222; }
    header { background: #111827; color: white; padding: 24px; }
    main { max-width: 1100px; margin: 0 auto; padding: 24px; }
    h1 { margin: 0; font-size: 28px; }
    h2 { margin-top: 32px; font-size: 20px; }
    .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; }
    .value { font-size: 28px; font-weight: 700; margin-top: 8px; }
    table { width: 100%; border-collapse: collapse; background: white; margin-top: 10px; }
    th, td { border-bottom: 1px solid #e5e7eb; padding: 10px; text-align: left; vertical-align: top; }
    th { background: #f3f4f6; }
    pre { white-space: pre-wrap; line-height: 1.6; }
    @media (max-width: 800px) { .grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 520px) { .grid { grid-template-columns: 1fr; } main { padding: 14px; } }
  </style>
</head>
<body>
  <header>
    <h1>AI PT 대시보드</h1>
    <p>운동, 식단, 체중, 리포트를 한 곳에서 확인합니다.</p>
  </header>
  <main>
    <section class="grid">
      <div class="card"><div>운동 기록</div><div class="value">{{ workout_count }}</div></div>
      <div class="card"><div>식단 기록</div><div class="value">{{ meal_count }}</div></div>
      <div class="card"><div>바이탈 기록</div><div class="value">{{ vital_count }}</div></div>
      <div class="card"><div>최근 체중</div><div class="value">{{ latest_weight or "-" }}</div></div>
    </section>
    <h2>최근 AI 리포트</h2>
    <div class="card">
      <pre>{{ latest_report or "아직 리포트가 없습니다." }}</pre>
    </div>
    <h2>최근 운동 기록</h2>
    <table>
      <tr><th>날짜</th><th>운동</th><th>메모</th></tr>
      {% for row in workouts %}
      <tr><td>{{ row.record_date }}</td><td>{{ row.exercise_name }}</td><td>{{ row.memo }}</td></tr>
      {% endfor %}
    </table>
    <h2>최근 식단 기록</h2>
    <table>
      <tr><th>날짜</th><th>구분</th><th>내용</th></tr>
      {% for row in meals %}
      <tr><td>{{ row.record_date }}</td><td>{{ row.meal_type or "-" }}</td><td>{{ row.food_text }}</td></tr>
      {% endfor %}
    </table>
    <h2>최근 체중/수면</h2>
    <table>
      <tr><th>날짜</th><th>체중</th><th>수면</th><th>컨디션</th></tr>
      {% for row in vitals %}
      <tr><td>{{ row.record_date }}</td><td>{{ row.body_weight_kg or "-" }}</td><td>{{ row.sleep_hours or "-" }}</td><td>{{ row.condition_text or "-" }}</td></tr>
      {% endfor %}
    </table>
  </main>
</body>
</html>
"""

@app.route("/")
def index():
    conn = get_conn()
    workout_count = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()[0]
    meal_count = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    vital_count = conn.execute("SELECT COUNT(*) FROM vitals").fetchone()[0]
    
    latest_weight_row = conn.execute("SELECT body_weight_kg FROM vitals WHERE body_weight_kg IS NOT NULL ORDER BY record_date DESC, id DESC LIMIT 1").fetchone()
    latest_weight = latest_weight_row[0] if latest_weight_row else None
    
    latest_report_row = conn.execute("SELECT report_text FROM reports ORDER BY created_at DESC, id DESC LIMIT 1").fetchone()
    latest_report = latest_report_row[0] if latest_report_row else None
    
    workouts = conn.execute("SELECT * FROM workouts ORDER BY record_date DESC, id DESC LIMIT 20").fetchall()
    meals = conn.execute("SELECT * FROM meals ORDER BY record_date DESC, id DESC LIMIT 20").fetchall()
    vitals = conn.execute("SELECT * FROM vitals ORDER BY record_date DESC, id DESC LIMIT 20").fetchall()
    
    conn.close()
    
    return render_template_string(
        HTML,
        workout_count=workout_count,
        meal_count=meal_count,
        vital_count=vital_count,
        latest_weight=latest_weight,
        latest_report=latest_report,
        workouts=workouts,
        meals=meals,
        vitals=vitals,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)