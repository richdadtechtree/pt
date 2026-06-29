import sqlite3
from pathlib import Path

DB_PATH = Path("/home/ubuntu/pt_system/pt_data.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 👈 누락되었던 핵심 코드입니다!
    return conn