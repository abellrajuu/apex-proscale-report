import sqlite3
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_PATH = os.path.join(BASE_DIR, "database_sqlite.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    try:
        cursor = conn.cursor()
        # Enable WAL mode for high concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        
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
                docx_filename TEXT NOT NULL,
                status TEXT DEFAULT 'Pending Verification',
                tested_by TEXT,
                verified_by TEXT,
                verified_at TEXT,
                hod_by TEXT,
                hod_at TEXT
            )
        """)

        # 2. User accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Production Engineer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Read admin and tech credentials securely from .env
        admin_user = os.environ.get("ADMIN_USERNAME", "admin").strip()
        admin_pass = os.environ.get("ADMIN_PASSWORD", "Admin@2026!").strip()
        tech_user = os.environ.get("TECH_USERNAME", "tech").strip()
        tech_pass = os.environ.get("TECH_PASSWORD", "Tech@2026!").strip()

        # Seed admin and technician users with hashed passwords if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            admin_hash = generate_password_hash(admin_pass)
            tech_hash = generate_password_hash(tech_pass)
            cursor.execute("INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                           (admin_user, admin_hash, "System Administrator", "Admin", now))
            cursor.execute("INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                           (tech_user, tech_hash, "Field Technician", "Production Engineer", now))
        else:
            # Sync admin password from .env if admin account exists
            cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (admin_user,))
            admin_row = cursor.fetchone()
            if admin_row:
                admin_hash = generate_password_hash(admin_pass)
                cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (admin_hash, admin_row[0]))

            # Re-hash plain text passwords if legacy accounts exist
            cursor.execute("SELECT id, username, password_hash FROM users")
            rows = cursor.fetchall()
            valid_prefixes = ("scrypt:", "pbkdf2:", "argon2:", "bcrypt:", "$2b$", "$2a$")
            for user_id, uname, pwd_hash in rows:
                if pwd_hash and not any(pwd_hash.startswith(prefix) for prefix in valid_prefixes):
                    new_hash = generate_password_hash(pwd_hash)
                    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))

        conn.commit()
    finally:
        conn.close()

def save_record(user_name, job_no, customer, conveyor_no, capacity, data_dict, docx_filename):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now_dt = datetime.now()
        created_at = now_dt.strftime("%Y-%m-%d %H:%M:%S")
        data_json = json.dumps(data_dict)

        # Check for rapid duplicate submission (within 10 seconds)
        cursor.execute("""
            SELECT id, created_at FROM records 
            WHERE job_no = ? AND user_name = ? AND docx_filename = ? 
            ORDER BY id DESC LIMIT 1
        """, (job_no, user_name, docx_filename))
        recent_row = cursor.fetchone()
        if recent_row:
            try:
                prev_time = datetime.strptime(recent_row["created_at"], "%Y-%m-%d %H:%M:%S")
                if (now_dt - prev_time).total_seconds() < 10:
                    # Return existing record ID instead of creating a duplicate
                    return recent_row["id"]
            except Exception:
                pass

        cursor.execute("""
            INSERT INTO records (user_name, job_no, customer, conveyor_no, capacity, created_at, data_json, docx_filename)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_name, job_no, customer, conveyor_no, capacity, created_at, data_json, docx_filename))

        record_id = cursor.lastrowid
        conn.commit()
        return record_id
    finally:
        conn.close()

def get_all_records():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_name, job_no, customer, conveyor_no, capacity, created_at, docx_filename FROM records ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_record_by_id(record_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        if row:
            res = dict(row)
            res["data"] = json.loads(res["data_json"])
            return res
        return None
    finally:
        conn.close()

def get_all_users():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_user_by_id(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, role, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_user(username, password, full_name, role):
    if get_user_by_username(username):
        raise ValueError(f"Username '{username}' already exists.")
        
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hashed_pwd = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                       (username, hashed_pwd, full_name, role, created_at))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id
    finally:
        conn.close()

def update_user_role(user_id, role):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found.")
    if user["username"] == "admin" and role != "Admin":
        raise ValueError("Cannot revoke Admin role from primary admin account.")
        
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        return True
    finally:
        conn.close()

def delete_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found.")
    if user["username"] == "admin":
        raise ValueError("Primary superadmin account 'admin' cannot be deleted.")

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, full_name, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            user_dict = dict(row)
            stored_hash = user_dict.pop("password_hash")
            if check_password_hash(stored_hash, password):
                return user_dict
        return None
    finally:
        conn.close()

def get_pending_records(role):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if role == 'Verifying Engineer':
            cursor.execute("SELECT * FROM records WHERE status = 'Pending Verification' ORDER BY id DESC")
        elif role == 'HOD':
            cursor.execute("SELECT * FROM records WHERE status = 'Pending HOD' ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM records ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def update_record_approval(record_id, user_full_name, role):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        if not row:
            return None
            
        data = dict(row)
        data_dict = json.loads(data['data_json'])
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if role in ['Verifying Engineer', 'Admin'] and data['status'] == 'Pending Verification':
            status = 'Pending HOD'
            cursor.execute("UPDATE records SET status = ?, verified_by = ?, verified_at = ? WHERE id = ?", (status, user_full_name, now_str, record_id))
            data_dict['verified_by'] = user_full_name
            data_dict['verified_at'] = now_str
            data_dict['approved_by'] = user_full_name + " (Verified)"
                
        elif role in ['HOD', 'Admin']:
            status = 'Approved'
            cursor.execute("UPDATE records SET status = ?, hod_by = ?, hod_at = ? WHERE id = ?", (status, user_full_name, now_str, record_id))
            data_dict['hod_by'] = user_full_name
            data_dict['hod_at'] = now_str
            data_dict['approved_by'] = user_full_name + " (HOD)"
            
        new_json = json.dumps(data_dict)
        cursor.execute("UPDATE records SET data_json = ? WHERE id = ?", (new_json, record_id))
        docx_filename = data['docx_filename']
        
        conn.commit()
        return data_dict, docx_filename
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_PATH)
