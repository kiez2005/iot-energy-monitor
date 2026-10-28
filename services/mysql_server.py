"""
MySQL Protocol Server (Port 3306) - Tương thích 100% với Node-RED (node-red-node-mysql / mysql2) và Python (mysql-connector / pymysql)
- Nếu cổng 3306 đã có MySQL/MariaDB thật chạy sẵn thì giữ nguyên.
- Nếu chưa cài MySQL Server hệ thống, script này khởi chạy một MySQL Server chuẩn giao thức TCP 3306
  sử dụng mysql-mimic + SQLite backend tại `database/smart_energy_db.sqlite`, tự động khởi tạo bảng
  `energy_logs` và `alert_logs` cùng dữ liệu mẫu ban đầu.
"""

import asyncio
import datetime
import os
import re
import socket
import sqlite3
import sys
from mysql_mimic import MysqlServer, Session

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOST = "127.0.0.1"
PORT = 3306
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "database", "smart_energy_db.sqlite")


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex((host, port)) == 0


def init_database():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS energy_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recorded_at TEXT DEFAULT (datetime('now', 'localtime')),
            device_id TEXT DEFAULT 'ESP32_PZEM_MAIN',
            voltage REAL NOT NULL,
            current_amp REAL NOT NULL,
            power_watt REAL NOT NULL,
            energy_kwh REAL NOT NULL,
            power_factor REAL NOT NULL,
            frequency REAL NOT NULL,
            living_room_w REAL DEFAULT 0,
            kitchen_w REAL DEFAULT 0,
            bedroom_w REAL DEFAULT 0,
            relay_state TEXT DEFAULT 'ON',
            status_alert TEXT DEFAULT 'NORMAL'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS alert_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_time TEXT DEFAULT (datetime('now', 'localtime')),
            alert_type TEXT NOT NULL,
            power_watt REAL NOT NULL,
            voltage REAL NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # Chèn dữ liệu mẫu ban đầu nếu bảng đang trống để Dashboard có sẵn lịch sử ngay khi mở
    cur.execute("SELECT COUNT(*) FROM energy_logs")
    count = cur.fetchone()[0]
    if count == 0:
        now = datetime.datetime.now()
        sample_rows = [
            (
                (now - datetime.timedelta(minutes=5 - i)).strftime("%Y-%m-%d %H:%M:%S"),
                "ESP32_PZEM_MAIN",
                round(220.5 + (i % 3) * 1.2, 1),
                round((1450 + i * 180) / (221.0 * 0.92), 2),
                1450 + i * 180,
                round(125.100 + i * 0.015, 3),
                0.92,
                50.0,
                350 + i * 20,
                700 + i * 100,
                400 + i * 60,
                "ON",
                "NORMAL"
            )
            for i in range(5)
        ]
        cur.executemany("""
            INSERT INTO energy_logs (
                recorded_at, device_id, voltage, current_amp, power_watt,
                energy_kwh, power_factor, frequency, living_room_w,
                kitchen_w, bedroom_w, relay_state, status_alert
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_rows)
        conn.commit()
        print(f"[MYSQL-SERVER 3306] Đã khởi tạo 5 bản ghi lịch sử mẫu trong smart_energy_db.")

    conn.close()


def translate_mysql_to_sqlite(sql: str) -> str:
    """Chuyển đổi các cú pháp đặc thù của MySQL sang SQLite tương đương."""
    s = sql.strip()
    # NOW() -> datetime('now', 'localtime')
    s = re.sub(r"\bNOW\s*\(\s*\)", "datetime('now', 'localtime')", s, flags=re.IGNORECASE)
    s = re.sub(r"\bCURDATE\s*\(\s*\)", "date('now', 'localtime')", s, flags=re.IGNORECASE)
    # DATE_FORMAT(col, '%H:%i:%s %d/%m') -> strftime('%H:%M:%S %d/%m', col)
    def repl_date_format(match):
        col = match.group(1).strip()
        fmt = match.group(2)
        fmt = fmt.replace("%i", "%M").replace("%s", "%S")
        return f"strftime('{fmt}', {col})"

    s = re.sub(
        r"DATE_FORMAT\s*\(\s*([^,]+)\s*,\s*'([^']+)'\s*\)",
        repl_date_format,
        s,
        flags=re.IGNORECASE,
    )
    return s


class SqliteMySQLSession(Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.create_function("VERSION", 0, lambda: "8.0.35-SmartEnergy-IoT")

    async def query(self, expression, sql, attrs):
        q_upper = sql.strip().upper()

        # Xử lý các câu lệnh hệ thống của MySQL Client / mysql2 / Node-RED
        if q_upper.startswith("SELECT VERSION()"):
            return [("8.0.35-SmartEnergy-IoT",)], ["version()"]
        if q_upper.startswith(("SET ", "USE ", "CREATE DATABASE", "SHOW WARNINGS")):
            return [], []
        if "SELECT @@" in q_upper:
            return [(1,)], ["value"]
        if q_upper.startswith("SHOW TABLES"):
            return [("energy_logs",), ("alert_logs",)], ["Tables_in_smart_energy_db"]

        translated_sql = translate_mysql_to_sqlite(sql)
        cur = self.conn.cursor()
        try:
            cur.execute(translated_sql)
            if cur.description:
                columns = [col[0] for col in cur.description]
                rows = cur.fetchall()
                return rows, columns
            else:
                self.conn.commit()
                print(f"[MYSQL-SERVER 3306] Thực thi thành công: {translated_sql[:95]}...")
                return [], []
        except Exception as e:
            print(f"[MYSQL-SERVER 3306] Lỗi SQL: {e} | Query: {translated_sql}")
            raise


async def main():
    if is_port_in_use(HOST, PORT):
        print(f"[MYSQL-SERVER 3306] Phát hiện MySQL Server đã chạy sẵn trên {HOST}:{PORT}.")
        return

    init_database()
    server = MysqlServer(session_factory=SqliteMySQLSession)
    await server.start_server(host=HOST, port=PORT)
    print("================================================================")
    print(f"🗄️  MySQL Server (smart_energy_db) đang chạy tại {HOST}:{PORT}")
    print(f"📁 File dữ liệu lưu tại: {DB_FILE}")
    print("================================================================")
    await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
