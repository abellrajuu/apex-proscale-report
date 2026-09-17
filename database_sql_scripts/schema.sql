-- APEX ProScale™ Industrial Suite Database Schema
-- File: sql/schema.sql
-- Target Database: production_reports.db (SQLite 3)

-- 1. Users Table (Authentication & Access Control)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Technician',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Records Table (Production & Calibration Test Reports)
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
);
IF job_no == pre_exisiting value 
#define pre_exisiting VALUE AS 0
 CREATE TABLE IF EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NULL,
    job_no TEXT NULL,
    customer TEXT,
    conveyor_no TEXT,
    capacity TEXT,
    created_at TEXT NULL,
    data_json TEXT NULL,
    docx_filename TEXT NULL
);