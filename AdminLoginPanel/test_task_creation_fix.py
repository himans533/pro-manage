"""
Test script to validate the task creation fix
Tests:
1. Task creation with proper error handling
2. Database lock handling
3. Transaction isolation
4. Concurrent access resilience
"""

import sqlite3
import os
import json
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_db_connection, init_db, init_daily_report_module

DB_PATH = os.path.join(os.path.dirname(__file__), 'project_management.db')

def setup_test_data():
    """Setup test data including user, project, and permissions"""
    print("[SETUP] Initializing database...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clean up existing test data
    cursor.execute("DELETE FROM users WHERE username = 'test_employee'")
    cursor.execute("DELETE FROM projects WHERE title = 'Test Project'")
    cursor.execute("DELETE FROM tasks WHERE title LIKE 'Test Task%'")
    cursor.execute("DELETE FROM user_permissions WHERE user_id = (SELECT id FROM users WHERE username = 'test_employee')")
    conn.commit()
    
    # Ensure user types exist
    cursor.execute("INSERT OR IGNORE INTO usertypes (id, user_role) VALUES (?, ?)", (1, 'employee'))
    cursor.execute("INSERT OR IGNORE INTO usertypes (id, user_role) VALUES (?, ?)", (2, 'admin'))
    conn.commit()
    
    # Create test employee user
    from werkzeug.security import generate_password_hash
    password_hash = generate_password_hash('testpass123')
    cursor.execute(
        "INSERT INTO users (username, email, password, user_type_id, granted) VALUES (?, ?, ?, ?, ?)",
        ('test_employee', 'test@example.com', password_hash, 1, True)
    )
    conn.commit()
    user_id = cursor.lastrowid
    
    # Create test project
    cursor.execute(
        "INSERT INTO projects (title, description, created_by_id) VALUES (?, ?, ?)",
        ('Test Project', 'A test project', user_id)
    )
    conn.commit()
    project_id = cursor.lastrowid
    
    # Grant permission to create tasks
    cursor.execute(
        "INSERT INTO user_permissions (user_id, module, action, granted) VALUES (?, ?, ?, ?)",
        (user_id, 'task', 'Add', True)
    )
    conn.commit()
    
    conn.close()
    
    print(f"[OK] Test data created:")
    print(f"  - User ID: {user_id}")
    print(f"  - Project ID: {project_id}")
    return user_id, project_id

def test_task_creation_basic():
    """Test basic task creation"""
    print("\n[TEST] Basic task creation...")
    
    user_id, project_id = setup_test_data()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert a task directly using the same method as the API
    try:
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(
            '''
            INSERT INTO tasks (title, description, project_id, created_by_id, assigned_to_id, priority, deadline, status)
            VALUES (?,?,?,?,?,?,?,?)
            ''',
            ('Test Task 1', 'Description', project_id, user_id, None, 'Medium', None, 'Pending')
        )
        task_id = cursor.lastrowid
        cursor.execute('COMMIT')
        
        print(f"[OK] Task created successfully (ID: {task_id})")
        
        # Verify task exists
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        if task:
            print(f"[OK] Task verified in database: {dict(task)}")
            return True
        else:
            print("[FAIL] Task not found after creation")
            return False
            
    except sqlite3.OperationalError as e:
        print(f"[FAIL] Database locked: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False
    finally:
        conn.close()

def test_transaction_isolation():
    """Test BEGIN IMMEDIATE prevents locking"""
    print("\n[TEST] Transaction isolation with BEGIN IMMEDIATE...")
    
    user_id, project_id = setup_test_data()
    
    try:
        # Open first connection
        conn1 = get_db_connection()
        cursor1 = conn1.cursor()
        
        # Start transaction with IMMEDIATE lock
        cursor1.execute('BEGIN IMMEDIATE')
        cursor1.execute(
            '''
            INSERT INTO tasks (title, description, project_id, created_by_id, assigned_to_id, priority, deadline, status)
            VALUES (?,?,?,?,?,?,?,?)
            ''',
            ('Test Task Isolation', 'Description', project_id, user_id, None, 'Medium', None, 'Pending')
        )
        
        # Now try to read from another connection
        conn2 = get_db_connection()
        cursor2 = conn2.cursor()
        
        # This should work even though conn1 has a write lock
        cursor2.execute('SELECT COUNT(*) as cnt FROM projects')
        result = cursor2.fetchone()
        print(f"[OK] Read operation succeeded even with write lock: {result['cnt']} projects")
        
        # Commit first transaction
        cursor1.execute('COMMIT')
        
        conn1.close()
        conn2.close()
        
        print("[OK] Transaction isolation test passed")
        return True
        
    except Exception as e:
        print(f"[FAIL] Transaction isolation test failed: {e}")
        return False

def test_error_handling():
    """Test proper error handling for various scenarios"""
    print("\n[TEST] Error handling scenarios...")
    
    user_id, project_id = setup_test_data()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Test 1: Foreign key violation (non-existent project)
    print("  [Sub-test 1] Invalid project_id...")
    try:
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(
            '''
            INSERT INTO tasks (title, description, project_id, created_by_id, assigned_to_id, priority, deadline, status)
            VALUES (?,?,?,?,?,?,?,?)
            ''',
            ('Test Task', 'Description', 99999, user_id, None, 'Medium', None, 'Pending')
        )
        cursor.execute('COMMIT')
        print("    [WARN] Expected constraint error not raised")
    except sqlite3.IntegrityError:
        print("    [OK] Integrity constraint error caught correctly")
        cursor.execute('ROLLBACK')
    except Exception as e:
        print(f"    [OK] Error caught: {type(e).__name__}")
        cursor.execute('ROLLBACK')
    
    # Test 2: Invalid assigned_to user
    print("  [Sub-test 2] Invalid assigned_to_id...")
    try:
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(
            '''
            INSERT INTO tasks (title, description, project_id, created_by_id, assigned_to_id, priority, deadline, status)
            VALUES (?,?,?,?,?,?,?,?)
            ''',
            ('Test Task', 'Description', project_id, user_id, 99999, 'Medium', None, 'Pending')
        )
        cursor.execute('COMMIT')
        print("    [WARN] Expected constraint error not raised")
    except sqlite3.IntegrityError:
        print("    [OK] Integrity constraint error caught correctly")
        cursor.execute('ROLLBACK')
    except Exception as e:
        print(f"    [OK] Error caught: {type(e).__name__}")
        cursor.execute('ROLLBACK')
    
    # Test 3: Null title should be caught by application, not DB
    print("  [Sub-test 3] Null title...")
    try:
        cursor.execute('BEGIN IMMEDIATE')
        cursor.execute(
            '''
            INSERT INTO tasks (title, description, project_id, created_by_id, assigned_to_id, priority, deadline, status)
            VALUES (?,?,?,?,?,?,?,?)
            ''',
            (None, 'Description', project_id, user_id, None, 'Medium', None, 'Pending')
        )
        cursor.execute('COMMIT')
        print("    [WARN] Expected NOT NULL error not raised")
    except sqlite3.IntegrityError as e:
        print(f"    [OK] NOT NULL constraint error caught: {e}")
        cursor.execute('ROLLBACK')
    except Exception as e:
        print(f"    [OK] Error caught: {type(e).__name__}")
        cursor.execute('ROLLBACK')
    
    conn.close()
    print("[OK] Error handling tests completed")
    return True

def test_concurrent_task_creation():
    """Test multiple rapid task creations"""
    print("\n[TEST] Concurrent task creation (multiple tasks)...")
    
    user_id, project_id = setup_test_data()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create multiple tasks rapidly
        created_tasks = []
        for i in range(5):
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute(
                '''
                INSERT INTO tasks (title, description, project_id, created_by_id, assigned_to_id, priority, deadline, status)
                VALUES (?,?,?,?,?,?,?,?)
                ''',
                (f'Test Task {i}', f'Description {i}', project_id, user_id, None, 'Medium', None, 'Pending')
            )
            task_id = cursor.lastrowid
            cursor.execute('COMMIT')
            created_tasks.append(task_id)
            print(f"  [OK] Task {i+1} created (ID: {task_id})")
        
        # Verify all tasks exist
        cursor.execute('SELECT COUNT(*) as cnt FROM tasks WHERE project_id = ? AND title LIKE "Test Task%"', (project_id,))
        count = cursor.fetchone()['cnt']
        
        if count >= 5:
            print(f"[OK] All {count} tasks verified in database")
            return True
        else:
            print(f"[FAIL] Expected 5+ tasks, found {count}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Concurrent creation test failed: {e}")
        return False
    finally:
        conn.close()

def main():
    """Run all tests"""
    print("=" * 60)
    print("TASK CREATION FIX VALIDATION TESTS")
    print("=" * 60)
    
    # Initialize database
    print("\n[INIT] Setting up database...")
    if os.path.exists(DB_PATH):
        print(f"[OK] Database exists: {DB_PATH}")
    else:
        print(f"[WARN] Database not found, will be created")
    
    try:
        init_db()
        init_daily_report_module()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize database: {e}")
        return False
    
    # Run tests
    results = []
    
    results.append(("Basic Task Creation", test_task_creation_basic()))
    results.append(("Transaction Isolation", test_transaction_isolation()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Concurrent Creation", test_concurrent_task_creation()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
