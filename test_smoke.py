import sqlite3, os, time, requests
from werkzeug.security import generate_password_hash

BASE = 'http://127.0.0.1:5000'
DB = os.path.join(os.path.dirname(__file__), 'AdminLoginPanel', 'project_management.db')
print('DB', DB)
conn = sqlite3.connect(DB)
c = conn.cursor()
# create test user
pw = generate_password_hash('TestPass123!')
try:
    c.execute("INSERT INTO users (username, email, password, user_type_id, created_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", ('testuser','test@example.com', pw, 2))
    user_id = c.lastrowid
    print('created user', user_id)
except Exception as e:
    conn.rollback()
    c.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',))
    user_id = c.fetchone()[0]
    print('user exists', user_id)
# create project
try:
    c.execute("INSERT INTO projects (title, description, created_by_id, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ('Test Project','desc', user_id))
    project_id = c.lastrowid
    print('created project', project_id)
except Exception:
    conn.rollback()
    c.execute("SELECT id FROM projects WHERE title = ?", ('Test Project',))
    project_id = c.fetchone()[0]
    print('project exists', project_id)
# assign user to project
try:
    c.execute('INSERT OR IGNORE INTO project_assignments (user_id, project_id) VALUES (?, ?)', (user_id, project_id))
except Exception as e:
    print('assign error', e)
# create task assigned to user
try:
    c.execute("INSERT INTO tasks (title, project_id, created_by_id, assigned_to_id, created_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", ('Test Task', project_id, user_id, user_id))
    task_id = c.lastrowid
    print('created task', task_id)
except Exception:
    conn.rollback()
    c.execute('SELECT id FROM tasks WHERE title = ? AND project_id = ?', ('Test Task', project_id))
    task_id = c.fetchone()[0]
    print('task exists', task_id)
conn.commit()
conn.close()

# wait for server
print('waiting for server..')
for i in range(10):
    try:
        r = requests.get(BASE + '/health', timeout=2)
        if r.ok:
            print('server up')
            break
    except Exception:
        pass
    time.sleep(1)

# login
print('logging in')
r = requests.post(BASE + '/api/user/login', json={'email':'test@example.com','password':'TestPass123!'})
print('login', r.status_code, r.text)
if r.status_code!=200:
    raise SystemExit('login failed')
token = r.json().get('token')
headers = {'Authorization': 'Bearer ' + token}

# submit a daily report
payload = {'task_id': task_id, 'report_date': time.strftime('%Y-%m-%d'), 'work_description':'Worked on tests', 'time_spent': 2.5, 'status':'In Progress'}
r = requests.post(BASE + '/api/employee/daily-report', json=payload, headers=headers)
print('submit report', r.status_code, r.text)

# list reports as admin (should be forbidden for test user)
r = requests.get(BASE + '/api/daily-reports', headers=headers)
print('list as employee', r.status_code, r.text)

# now check admin listing by logging in as admin via OTP flow
r1 = requests.post(BASE + '/api/admin/login/step1', json={'email': 'anubha@gmail.com'})
print('admin step1', r1.status_code)
r2 = requests.post(BASE + '/api/admin/login/step2', json={'email':'anubha@gmail.com', 'otp': '654321'})
print('admin login', r2.status_code, r2.text)
adm_token = r2.json().get('session_token')
if adm_token:
    headers_admin = {'Authorization': 'Bearer ' + adm_token}
    r = requests.get(BASE + '/api/daily-reports', headers=headers_admin)
    print('admin list', r.status_code, r.text)
else:
    print('admin login failed')
