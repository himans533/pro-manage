import sqlite3, os, sys

DB_PATH = os.path.join(os.path.dirname(__file__), 'AdminLoginPanel', 'project_management.db')
print('Using DB:', DB_PATH)
if not os.path.exists(DB_PATH):
    print('ERROR: DB not found at', DB_PATH)
    sys.exit(2)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_task_reports'")
if c.fetchone():
    print('daily_task_reports: EXISTS')
else:
    print('daily_task_reports: MISSING')

c.execute('PRAGMA table_info(daily_task_reports)')
cols = c.fetchall()
print('Columns (name TYPE):')
for col in cols:
    print('-', col[1], col[2])

try:
    c.execute('SELECT COUNT(*) FROM daily_task_reports')
    print('Report rows:', c.fetchone()[0])
except Exception as e:
    print('Count query failed:', e)

conn.close()
