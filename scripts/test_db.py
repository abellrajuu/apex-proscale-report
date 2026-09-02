import sqlite3
conn = sqlite3.connect('belt_scale.db')
print(conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
