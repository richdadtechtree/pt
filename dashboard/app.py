from pathlib import Path
import sys

# 프로젝트 경로 설정
sys.path.append(str(Path("/home/ubuntu/pt_system")))
sys.path.append(str(Path(__file__).resolve().parents[1]))

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
  <!-- Google Fonts & Lucide Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    :root {
      --bg-primary: #0b0f19;
      --bg-secondary: #131a26;
      --bg-tertiary: #1b2434;
      --accent-cyan: #06b6d4;
      --accent-emerald: #10b981;
      --accent-purple: #8b5cf6;
      --accent-amber: #f59e0b;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --border-color: #243048;
      --card-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.3);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    header {
      background: linear-gradient(135deg, var(--bg-secondary) 0%, #0f172a 100%);
      border-bottom: 1px solid var(--border-color);
      padding: 24px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }

    .brand-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-icon {
      background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
      width: 42px;
      height: 42px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 0 15px rgba(6, 182, 212, 0.4);
    }

    header h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
      background: linear-gradient(to right, #ffffff, #93c5fd);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    header p {
      font-size: 14px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .nav-tabs {
      display: flex;
      gap: 8px;
      background-color: var(--bg-primary);
      padding: 6px;
      border-radius: 10px;
      border: 1px solid var(--border-color);
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 10px 18px;
      font-size: 14px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background-color: rgba(255, 255, 255, 0.05);
    }

    .tab-btn.active {
      color: white;
      background-color: var(--bg-tertiary);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      border: 1px solid var(--border-color);
    }

    main {
      flex: 1;
      max-width: 1280px;
      width: 100%;
      margin: 0 auto;
      padding: 32px 40px;
    }

    .grid-stats {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-bottom: 32px;
    }

    .stat-card {
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
      overflow: hidden;
      box-shadow: var(--card-shadow);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .stat-card:hover {
      transform: translateY(-4px);
      border-color: rgba(255, 255, 255, 0.15);
    }

    .stat-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 4px;
      height: 100%;
    }

    .stat-card.workouts::before { background-color: var(--accent-cyan); }
    .stat-card.meals::before { background-color: var(--accent-emerald); }
    .stat-card.vitals::before { background-color: var(--accent-purple); }
    .stat-card.weight::before { background-color: var(--accent-amber); }

    .stat-label {
      font-size: 13px;
      text-transform: uppercase;
      font-weight: 700;
      color: var(--text-muted);
      letter-spacing: 0.5px;
    }

    .stat-value {
      font-family: 'Outfit', sans-serif;
      font-size: 32px;
      font-weight: 800;
      color: white;
      margin-top: 6px;
    }

    .stat-icon {
      background-color: var(--bg-tertiary);
      width: 50px;
      height: 50px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--border-color);
    }

    .stat-card.workouts .stat-icon { color: var(--accent-cyan); }
    .stat-card.meals .stat-icon { color: var(--accent-emerald); }
    .stat-card.vitals .stat-icon { color: var(--accent-purple); }
    .stat-card.weight .stat-icon { color: var(--accent-amber); }

    .dashboard-content {
      display: none;
      animation: fadeIn 0.3s ease-in-out forwards;
    }

    .dashboard-content.active {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .dashboard-grid {
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 24px;
    }

    .card {
      background-color: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 28px;
      box-shadow: var(--card-shadow);
      margin-bottom: 24px;
    }

    .card-title {
      font-family: 'Outfit', sans-serif;
      font-size: 20px;
      font-weight: 700;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: white;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 12px;
    }

    .card-title i {
      color: var(--accent-cyan);
    }

    .report-box {
      background-color: var(--bg-tertiary);
      border-radius: 12px;
      padding: 24px;
      border: 1px solid var(--border-color);
      font-size: 15px;
      line-height: 1.7;
      white-space: pre-wrap;
      color: #e2e8f0;
      position: relative;
    }

    .report-box::after {
      content: '""';
      position: absolute;
      right: 20px;
      bottom: 10px;
      font-size: 80px;
      color: rgba(255, 255, 255, 0.03);
      font-family: serif;
      line-height: 1;
    }

    .table-container {
      overflow-x: auto;
      border-radius: 12px;
      border: 1px solid var(--border-color);
      background-color: var(--bg-secondary);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    th {
      background-color: var(--bg-tertiary);
      color: var(--text-muted);
      font-weight: 600;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 14px 18px;
      border-bottom: 1px solid var(--border-color);
    }

    td {
      padding: 16px 18px;
      border-bottom: 1px solid var(--border-color);
      color: #cbd5e1;
      font-size: 14px;
      vertical-align: middle;
    }

    tr:last-child td {
      border-bottom: none;
    }

    tr:hover td {
      background-color: rgba(255, 255, 255, 0.02);
    }

    .badge {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
    }

    .badge-breakfast { background-color: rgba(16, 185, 129, 0.15); color: #34d399; }
    .badge-lunch { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .badge-dinner { background-color: rgba(6, 182, 212, 0.15); color: #22d3ee; }
    .badge-snack { background-color: rgba(139, 92, 246, 0.15); color: #a78bfa; }
    .badge-default { background-color: rgba(156, 163, 175, 0.15); color: #d1d5db; }

    .condition-text {
      background-color: var(--bg-tertiary);
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      border: 1px solid var(--border-color);
      color: var(--text-main);
    }

    .date-col {
      font-weight: 500;
      color: var(--text-muted);
      white-space: nowrap;
    }

    .exercise-badge {
      background-color: rgba(6, 182, 212, 0.1);
      color: var(--accent-cyan);
      border: 1px solid rgba(6, 182, 212, 0.2);
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
    }

    .empty-state {
      text-align: center;
      padding: 40px 20px;
      color: var(--text-muted);
      font-size: 14px;
    }

    .empty-state i {
      display: block;
      margin: 0 auto 12px;
      color: var(--border-color);
    }

    @media (max-width: 1024px) {
      .dashboard-grid { grid-template-columns: 1fr; }
      .grid-stats { grid-template-columns: repeat(2, 1fr); }
    }

    @media (max-width: 768px) {
      header { padding: 20px; flex-direction: column; align-items: stretch; }
      .nav-tabs { width: 100%; justify-content: space-around; }
      main { padding: 20px; }
      .grid-stats { grid-template-columns: 1fr; }
    }

    .delete-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    .delete-btn:hover {
      color: #ef4444;
      background-color: rgba(239, 68, 68, 0.1);
    }
    .delete-btn i {
      width: 16px;
      height: 16px;
    }
  </style>
</head>
<body>
  <header>
    <div class="brand-section">
      <div class="brand-icon">
        <i data-lucide="dumbbell"></i>
      </div>
      <div>
        <h1>AI PT 대시보드</h1>
        <p>운동, 식단, 체중, 리포트를 한 곳에서 실시간 확인합니다.</p>
      </div>
    </div>
    
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('tab-overview')">
        <i data-lucide="layout-dashboard"></i> 오버뷰
      </button>
      <button class="tab-btn" onclick="switchTab('tab-workouts')">
        <i data-lucide="activity"></i> 운동 기록
      </button>
      <button class="tab-btn" onclick="switchTab('tab-meals')">
        <i data-lucide="salad"></i> 식단 기록
      </button>
      <button class="tab-btn" onclick="switchTab('tab-vitals')">
        <i data-lucide="heart-pulse"></i> 체중 & 바이탈
      </button>
    </div>
  </header>

  <main>
    <!-- KPI Stats Section -->
    <section class="grid-stats">
      <div class="stat-card workouts">
        <div>
          <div class="stat-label">누적 운동 기록</div>
          <div class="stat-value">{{ workout_count }}</div>
        </div>
        <div class="stat-icon"><i data-lucide="flame"></i></div>
      </div>
      <div class="stat-card meals">
        <div>
          <div class="stat-label">누적 식단 기록</div>
          <div class="stat-value">{{ meal_count }}</div>
        </div>
        <div class="stat-icon"><i data-lucide="apple"></i></div>
      </div>
      <div class="stat-card vitals">
        <div>
          <div class="stat-label">누적 바이탈</div>
          <div class="stat-value">{{ vital_count }}</div>
        </div>
        <div class="stat-icon"><i data-lucide="scale"></i></div>
      </div>
      <div class="stat-card weight">
        <div>
          <div class="stat-label">최근 체중</div>
          <div class="stat-value">{{ latest_weight or "-" }} <span style="font-size:16px; font-weight:normal; color:var(--text-muted);">{{ "kg" if latest_weight else "" }}</span></div>
        </div>
        <div class="stat-icon"><i data-lucide="trending-up"></i></div>
      </div>
    </section>

    <!-- Tab 1: Overview -->
    <div id="tab-overview" class="dashboard-content active">
      <div class="dashboard-grid">
        <!-- Left column: AI Report -->
        <div class="card">
          <div class="card-title">
            <i data-lucide="sparkles" style="color: var(--accent-purple);"></i> 최근 AI 피드백 리포트
          </div>
          {% if latest_report %}
          <div class="report-box">{{ latest_report }}</div>
          {% else %}
          <div class="empty-state">
            <i data-lucide="message-square-off" size="48"></i>
            아직 리포트가 생성되지 않았습니다. 텔레그램에서 /daily 또는 /weekly를 입력해 리포트를 생성해 보세요.
          </div>
          {% endif %}
        </div>

        <!-- Right column: Quick overview of latest activity -->
        <div class="card">
          <div class="card-title">
            <i data-lucide="clock" style="color: var(--accent-amber);"></i> 실시간 운동 현황
          </div>
          {% if workouts %}
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>운동</th>
                  <th>날짜</th>
                </tr>
              </thead>
              <tbody>
                {% for row in workouts[:5] %}
                <tr>
                  <td><span class="exercise-badge">{{ row.exercise_name }}</span></td>
                  <td class="date-col">{{ row.record_date }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% else %}
          <div class="empty-state">
            <i data-lucide="clipboard-list" size="48"></i>
            오늘 등록된 운동 내역이 없습니다.
          </div>
          {% endif %}
        </div>
      </div>
    </div>

    <!-- Tab 2: Workouts -->
    <div id="tab-workouts" class="dashboard-content">
      <div class="card">
        <div class="card-title"><i data-lucide="activity"></i> 전체 운동 기록 내역</div>
        {% if workouts %}
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th style="width: 150px;">날짜</th>
                <th style="width: 250px;">운동 종목</th>
                <th>상세 메모</th>
                <th style="width: 80px; text-align: center;">삭제</th>
              </tr>
            </thead>
            <tbody>
              {% for row in workouts %}
              <tr>
                <td class="date-col">{{ row.record_date }}</td>
                <td><span class="exercise-badge">{{ row.exercise_name }}</span></td>
                <td>{{ row.memo or "-" }}</td>
                <td style="text-align: center;">
                  <button class="delete-btn" onclick="deleteRecord('workouts', {{ row.id }})" title="삭제">
                    <i data-lucide="trash-2"></i>
                  </button>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
        <div class="empty-state">
          <i data-lucide="award" size="48"></i>
          운동 기록이 비어 있습니다. 텔레그램을 통해 첫 운동을 등록해 보세요!
        </div>
        {% endif %}
      </div>
    </div>

    <!-- Tab 3: Meals -->
    <div id="tab-meals" class="dashboard-content">
      <div class="card">
        <div class="card-title"><i data-lucide="salad"></i> 전체 식단 기록 내역</div>
        {% if meals %}
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th style="width: 150px;">날짜</th>
                <th style="width: 120px;">식사 구분</th>
                <th>메뉴 및 상세 내용</th>
                <th style="width: 80px; text-align: center;">삭제</th>
              </tr>
            </thead>
            <tbody>
              {% for row in meals %}
              <tr>
                <td class="date-col">{{ row.record_date }}</td>
                <td>
                  {% if row.meal_type == '아침' %}
                    <span class="badge badge-breakfast">아침</span>
                  {% elif row.meal_type == '점심' %}
                    <span class="badge badge-lunch">점심</span>
                  {% elif row.meal_type == '저녁' %}
                    <span class="badge badge-dinner">저녁</span>
                  {% elif row.meal_type == '간식' %}
                    <span class="badge badge-snack">간식</span>
                  {% else %}
                    <span class="badge badge-default">{{ row.meal_type or "미분류" }}</span>
                  {% endif %}
                </td>
                <td>{{ row.food_text }}</td>
                <td style="text-align: center;">
                  <button class="delete-btn" onclick="deleteRecord('meals', {{ row.id }})" title="삭제">
                    <i data-lucide="trash-2"></i>
                  </button>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
        <div class="empty-state">
          <i data-lucide="cookie" size="48"></i>
          식단 기록이 비어 있습니다. 오늘 먹은 음식을 텔레그램에 적어 보세요!
        </div>
        {% endif %}
      </div>
    </div>

    <!-- Tab 4: Vitals -->
    <div id="tab-vitals" class="dashboard-content">
      <div class="card">
        <div class="card-title"><i data-lucide="scale"></i> 체중 & 수면 및 컨디션 기록</div>
        {% if vitals %}
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th style="width: 180px;">날짜</th>
                <th style="width: 150px;">체중 (kg)</th>
                <th style="width: 150px;">수면 시간 (시간)</th>
                <th>컨디션 및 메모</th>
                <th style="width: 80px; text-align: center;">삭제</th>
              </tr>
            </thead>
            <tbody>
              {% for row in vitals %}
              <tr>
                <td class="date-col">{{ row.record_date }}</td>
                <td style="font-weight: 600; color: white;">{{ row.body_weight_kg or "-" }} {{ "kg" if row.body_weight_kg else "" }}</td>
                <td>{{ row.sleep_hours or "-" }} {{ "시간" if row.sleep_hours else "" }}</td>
                <td>
                  {% if row.condition_text %}
                    <span class="condition-text">{{ row.condition_text }}</span>
                  {% else %}
                    -
                  {% endif %}
                </td>
                <td style="text-align: center;">
                  <button class="delete-btn" onclick="deleteRecord('vitals', {{ row.id }})" title="삭제">
                    <i data-lucide="trash-2"></i>
                  </button>
                </td>
              </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
        {% else %}
        <div class="empty-state">
          <i data-lucide="line-chart" size="48"></i>
          바이탈 기록이 아직 없습니다. 체중이나 수면 시간을 입력해 보세요!
        </div>
        {% endif %}
      </div>
    </div>
  </main>

  <script>
    // Lucide 아이콘 초기화
    lucide.createIcons();

    // 탭 전환 함수
    function switchTab(tabId) {
      // 모든 탭 콘텐츠 숨기기
      const contents = document.querySelectorAll('.dashboard-content');
      contents.forEach(c => c.classList.remove('active'));

      // 모든 탭 버튼 active 클래스 해제
      const buttons = document.querySelectorAll('.tab-btn');
      buttons.forEach(b => b.classList.remove('active'));

      // 선택한 탭 콘텐츠 표시 및 버튼 활성화
      const targetContent = document.getElementById(tabId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
      
      // 해당 탭을 트리거하는 버튼 활성화
      const targetBtn = Array.from(buttons).find(b => b.getAttribute('onclick').includes(tabId));
      if (targetBtn) {
        targetBtn.classList.add('active');
      }

      // sessionStorage에 현재 탭 상태 저장
      sessionStorage.setItem('activeTab', tabId);
    }

    // 페이지 로드 시 기존 탭 상태 복원
    window.addEventListener('DOMContentLoaded', () => {
      const savedTab = sessionStorage.getItem('activeTab');
      if (savedTab && document.getElementById(savedTab)) {
        switchTab(savedTab);
      } else {
        switchTab('tab-overview');
      }
    });

    // 기록 삭제 함수
    function deleteRecord(category, id) {
      if (confirm('정말로 이 기록을 삭제하시겠습니까?')) {
        fetch('/delete/' + category + '/' + id, {
          method: 'POST'
        }).then(response => {
          if (response.ok) {
            location.reload();
          } else {
            alert('삭제에 실패했습니다.');
          }
        }).catch(err => {
          console.error(err);
          alert('오류가 발생했습니다.');
        });
      }
    }
  </script>
</body>
</html>
"""


@app.route("/delete/<string:category>/<int:record_id>", methods=["POST"])
def delete_record(category, record_id):
    if category not in ["workouts", "meals", "vitals"]:
        return "Invalid category", 400
    
    conn = get_conn()
    try:
        conn.execute(f"DELETE FROM {category} WHERE id = ?", (record_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"Error: {e}", 500
    finally:
        conn.close()
    return "OK", 200


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