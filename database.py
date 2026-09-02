import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "production_reports.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Test records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            job_no TEXT NOT NULL,
            customer TEXT,
            conveyor_no TEXT,
            capacity TEXT,
            created_at TEXT NOT NULL,
            data_json TEXT NOT NULL,
            docx_filename TEXT NOT NULL
        )
    """)

    # 2. User accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Technician',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed default admin and technician users with hashed passwords if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        admin_hash = generate_password_hash("admin")
        tech_hash = generate_password_hash("123")
        cursor.execute("INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                       ("admin", admin_hash, "System Administrator", "Admin", now))
        cursor.execute("INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                       ("tech", tech_hash, "Field Technician", "Technician", now))
    else:
        # Re-hash plain text passwords if legacy accounts exist
        cursor.execute("SELECT id, username, password_hash FROM users")
        rows = cursor.fetchall()
        for user_id, uname, pwd_hash in rows:
            if pwd_hash and not pwd_hash.startswith("scrypt:") and not pwd_hash.startswith("pbkdf2:"):
                new_hash = generate_password_hash(pwd_hash)
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))

    conn.commit()
    conn.close()

def save_record(user_name, job_no, customer, conveyor_no, capacity, data_dict, docx_filename):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_json = json.dumps(data_dict)

    cursor.execute("""
        INSERT INTO records (user_name, job_no, customer, conveyor_no, capacity, created_at, data_json, docx_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_name, job_no, customer, conveyor_no, capacity, created_at, data_json, docx_filename))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def get_all_records():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_name, job_no, customer, conveyor_no, capacity, created_at, docx_filename FROM records ORDER BY id DESC")
    rows = cursor.fetchall()
    records = [dict(row) for row in rows]
    conn.close()
    return records

def get_record_by_id(record_id):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        res = dict(row)
        res["data"] = json.loads(res["data_json"])
        return res
    return None

def get_all_users():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY id ASC")
    rows = cursor.fetchall()
    users = [dict(row) for row in rows]
    conn.close()
    return users

def create_user(username, password, full_name, role):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hashed_pwd = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                   (username, hashed_pwd, full_name, role, created_at))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def verify_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, full_name, role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        user_dict = dict(row)
        stored_hash = user_dict.pop("password_hash")
        if check_password_hash(stored_hash, password):
            return user_dict
    return None

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
