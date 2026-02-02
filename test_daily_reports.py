import sqlite3
import os
import json
from AdminLoginPanel.app import get_db_connection, app, get_current_user_id
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'AdminLoginPanel', 'project_management.db')
print('Using DB:', DB_PATH)

# Ensure table exists
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS daily_task_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    report_date DATE NOT NULL,
    project_id INTEGER NOT NULL,
    task_title TEXT NOT NULL,
    task_assigned_by_id INTEGER NOT NULL,
    communication_details TEXT,
    result_of_effort TEXT,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

# Ensure a test user exists
cursor.execute("SELECT id FROM users WHERE username = ?", ('test_user',))
row = cursor.fetchone()
if row:
    user_id = row[0]
    print('Found existing test user id', user_id)
else:
    # find an employee usertype id
    cursor.execute("SELECT id FROM usertypes WHERE user_role = ?", ('Employee',))
    ut = cursor.fetchone()
    utid = ut[0] if ut else 2
    cursor.execute("INSERT INTO users (username, email, password, user_type_id, granted) VALUES (?, ?, ?, ?, 1)",
                   ('test_user', 'test_user@example.com', generate_password_hash('Password!@#'), utid))
    conn.commit()
    user_id = cursor.lastrowid
    print('Created test user id', user_id)

# Ensure a test project exists
cursor.execute("SELECT id FROM projects WHERE title = ?", ('Test Project',))
row = cursor.fetchone()
if row:
    project_id = row[0]
    print('Found project id', project_id)
else:
    cursor.execute("INSERT INTO projects (title, description, created_by_id) VALUES (?, ?, ?)",
                   ('Test Project', 'Auto-created for tests', user_id))
    conn.commit()
    project_id = cursor.lastrowid
    print('Created project id', project_id)

conn.close()

with app.test_client() as client:
    # Simulate logged-in employee
    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['user_type'] = 'employee'

    payload = {
        'date': '2026-01-29',
        'employee_id': user_id,
        'project_id': project_id,
        'task': 'Implemented test endpoint',
        'assigned_by': user_id,
        'communication': 'email: test_user@example.com',
        'result': 'Work completed',
        'remarks': 'No remarks'
    }

    print('Submitting daily report...')
    resp = client.post('/api/admin/daily_reports', json=payload)
    print('POST status:', resp.status_code)
    try:
        print('POST response:', resp.get_json())
    except Exception:
        print('POST response (text):', resp.data.decode())

    # Now fetch as admin
    with client.session_transaction() as sess:
        sess.clear()
        sess['admin'] = True
        sess['user_type'] = 'admin'

    print('Fetching daily reports as admin...')
    resp = client.get('/api/admin/daily_reports')
    print('GET status:', resp.status_code)
    data = resp.get_json()
    print('Number of reports returned:', len(data) if isinstance(data, list) else 'N/A')
    if isinstance(data, list) and data:
        print('Sample report:', json.dumps(data[0], indent=2))

print('Test script finished.')
