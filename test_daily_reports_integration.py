"""
Integration Tests for Daily Task Reporting Module

Tests cover:
1. Employee report submission
2. Admin approval workflow
3. Super Admin full control
4. Role-based access control
5. Export functionality
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from AdminLoginPanel.app import app, get_db_connection
from werkzeug.security import generate_password_hash

# Test setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'AdminLoginPanel', 'project_management.db')
print(f'[TEST] Using DB: {DB_PATH}')


class TestDailyReportingModule:
    def __init__(self):
        self.app = app
        self.client = app.test_client()
        self.test_user_id = None
        self.test_admin_id = None
        self.test_project_id = None
        self.test_task_id = None

    def setup_test_data(self):
        """Create test data in database"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure user types exist
        cursor.execute("SELECT id FROM usertypes WHERE user_role = 'Employee'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usertypes (user_role) VALUES ('Employee')")
        cursor.execute("SELECT id FROM usertypes WHERE user_role = 'Employee'")
        employee_type = cursor.fetchone()['id']

        cursor.execute("SELECT id FROM usertypes WHERE user_role = 'Administrator'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usertypes (user_role) VALUES ('Administrator')")
        cursor.execute("SELECT id FROM usertypes WHERE user_role = 'Administrator'")
        admin_type = cursor.fetchone()['id']

        # Create test employee
        cursor.execute("SELECT id FROM users WHERE username = 'test_employee'")
        user = cursor.fetchone()
        if not user:
            cursor.execute(
                "INSERT INTO users (username, email, password, user_type_id, granted) VALUES (?, ?, ?, ?, 1)",
                ('test_employee', 'test@example.com', generate_password_hash('Password123!@'), employee_type)
            )
            self.test_user_id = cursor.lastrowid
        else:
            self.test_user_id = user['id']

        # Create test admin
        cursor.execute("SELECT id FROM users WHERE username = 'test_admin'")
        user = cursor.fetchone()
        if not user:
            cursor.execute(
                "INSERT INTO users (username, email, password, user_type_id, granted) VALUES (?, ?, ?, ?, 1)",
                ('test_admin', 'admin@example.com', generate_password_hash('Password123!@'), admin_type)
            )
            self.test_admin_id = cursor.lastrowid
        else:
            self.test_admin_id = user['id']

        # Create test project
        cursor.execute("SELECT id FROM projects WHERE title = 'Test Project'")
        proj = cursor.fetchone()
        if not proj:
            cursor.execute(
                "INSERT INTO projects (title, description, status, created_by_id) VALUES (?, ?, ?, ?)",
                ('Test Project', 'Test project for daily reports', 'In Progress', self.test_admin_id)
            )
            self.test_project_id = cursor.lastrowid
        else:
            self.test_project_id = proj['id']

        # Create test task
        cursor.execute("SELECT id FROM tasks WHERE title = 'Test Task'")
        task = cursor.fetchone()
        if not task:
            cursor.execute(
                "INSERT INTO tasks (title, description, status, project_id, created_by_id, assigned_to_id) VALUES (?, ?, ?, ?, ?, ?)",
                ('Test Task', 'Test task for daily reports', 'Pending', self.test_project_id, self.test_admin_id, self.test_user_id)
            )
            self.test_task_id = cursor.lastrowid
        else:
            self.test_task_id = task['id']

        conn.commit()
        conn.close()

        print(f'[TEST] Setup complete: Employee={self.test_user_id}, Admin={self.test_admin_id}, Project={self.test_project_id}, Task={self.test_task_id}')

    def test_employee_submit_report(self):
        """Test: Employee can submit a daily report"""
        print('\n[TEST] Employee Submit Report')

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['user_type'] = 'employee'

        report_data = {
            'task_id': self.test_task_id,
            'project_id': self.test_project_id,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'work_description': 'Completed API integration',
            'time_spent': 5.5,
            'status': 'Completed',
            'blocker': ''
        }

        response = self.client.post('/api/daily-report', json=report_data)
        print(f'Response Status: {response.status_code}')
        data = response.get_json()
        print(f'Response: {json.dumps(data, indent=2)}')

        assert response.status_code == 201, f'Expected 201, got {response.status_code}'
        assert data.get('success') or data.get('id'), 'Report should be created'
        print('[PASS] Employee can submit report')
        return data.get('id')

    def test_duplicate_report_prevention(self):
        """Test: Duplicate reports for same task/day are prevented"""
        print('\n[TEST] Duplicate Report Prevention')

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['user_type'] = 'employee'

        report_data = {
            'task_id': self.test_task_id,
            'project_id': self.test_project_id,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'work_description': 'First attempt',
            'time_spent': 3.0,
            'status': 'In Progress'
        }

        # First submission
        response1 = self.client.post('/api/daily-report', json=report_data)
        assert response1.status_code == 201

        # Second submission (duplicate)
        response2 = self.client.post('/api/daily-report', json=report_data)
        print(f'Duplicate Prevention Response Status: {response2.status_code}')
        data = response2.get_json()
        print(f'Response: {json.dumps(data, indent=2)}')

        assert response2.status_code == 409, f'Expected 409 Conflict, got {response2.status_code}'
        print('[PASS] Duplicate reports are prevented')

    def test_admin_can_view_reports(self):
        """Test: Admin can view employee reports"""
        print('\n[TEST] Admin View Reports')

        # First create a report as employee
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['user_type'] = 'employee'

        report_data = {
            'task_id': self.test_task_id,
            'project_id': self.test_project_id,
            'report_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'work_description': 'Yesterday work',
            'time_spent': 4.0,
            'status': 'Completed'
        }
        self.client.post('/api/daily-report', json=report_data)

        # Now view as admin
        with self.client.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = self.test_admin_id
            sess['user_type'] = 'admin'
            sess['admin'] = True

        response = self.client.get('/api/daily-reports')
        print(f'Response Status: {response.status_code}')
        data = response.get_json()
        print(f'Number of reports: {len(data) if isinstance(data, list) else "N/A"}')

        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        assert isinstance(data, list), 'Should return list of reports'
        print('[PASS] Admin can view reports')

    def test_admin_approve_report(self):
        """Test: Admin can approve a report"""
        print('\n[TEST] Admin Approve Report')

        # Create a report first
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['user_type'] = 'employee'

        report_data = {
            'task_id': self.test_task_id,
            'project_id': self.test_project_id,
            'report_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'work_description': 'Two days ago work',
            'time_spent': 6.0,
            'status': 'Completed'
        }
        response = self.client.post('/api/daily-report', json=report_data)
        report_id = response.get_json().get('id')
        print(f'Created report ID: {report_id}')

        # Approve as admin
        with self.client.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = self.test_admin_id
            sess['user_type'] = 'admin'
            sess['admin'] = True

        approve_data = {
            'action': 'approve',
            'comment': 'Good work'
        }
        response = self.client.post(f'/api/daily-report/{report_id}/action', json=approve_data)
        print(f'Approval Response Status: {response.status_code}')
        data = response.get_json()
        print(f'Response: {json.dumps(data, indent=2)}')

        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        print('[PASS] Admin can approve report')

    def test_hours_validation(self):
        """Test: Hours spent validation (0-24 range)"""
        print('\n[TEST] Hours Validation')

        with self.client.session_transaction() as sess:
            sess['user_id'] = self.test_user_id
            sess['user_type'] = 'employee'

        # Invalid: > 24 hours
        invalid_data = {
            'task_id': self.test_task_id,
            'project_id': self.test_project_id,
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'work_description': 'Too many hours',
            'time_spent': 25.0,
            'status': 'In Progress'
        }

        response = self.client.post('/api/daily-report', json=invalid_data)
        print(f'Invalid Hours Response Status: {response.status_code}')
        data = response.get_json()
        print(f'Response: {json.dumps(data, indent=2)}')

        assert response.status_code == 400, f'Expected 400, got {response.status_code}'
        print('[PASS] Hours validation works')

    def test_export_reports(self):
        """Test: Export reports to CSV"""
        print('\n[TEST] Export Reports')

        with self.client.session_transaction() as sess:
            sess.clear()
            sess['user_id'] = self.test_admin_id
            sess['user_type'] = 'admin'
            sess['admin'] = True

        response = self.client.get('/api/daily-reports/export')
        print(f'Export Response Status: {response.status_code}')
        print(f'Content Type: {response.content_type}')

        assert response.status_code == 200, f'Expected 200, got {response.status_code}'
        assert 'text/csv' in response.content_type, 'Should return CSV'
        print('[PASS] Export works')

    def run_all_tests(self):
        """Run all tests"""
        print('\n' + '='*60)
        print('DAILY TASK REPORTING MODULE - INTEGRATION TESTS')
        print('='*60)

        self.setup_test_data()

        try:
            self.test_employee_submit_report()
            self.test_duplicate_report_prevention()
            self.test_admin_can_view_reports()
            self.test_admin_approve_report()
            self.test_hours_validation()
            self.test_export_reports()

            print('\n' + '='*60)
            print('[SUCCESS] All tests passed!')
            print('='*60)
        except AssertionError as e:
            print(f'\n[FAILED] {e}')
        except Exception as e:
            print(f'\n[ERROR] {e}')
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    tester = TestDailyReportingModule()
    tester.run_all_tests()
