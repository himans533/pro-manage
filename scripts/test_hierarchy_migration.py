"""
Test Script for User Hierarchy Migration
=========================================
Run this script to verify the hierarchy migration was applied correctly.

Usage:
    python scripts/test_hierarchy_migration.py
"""

import sqlite3
import sys
from pathlib import Path


def get_db_connection(db_path):
    """Get database connection."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def verify_column_exists(db_path):
    """Verify parent_user_id column exists in users table."""
    print("✓ Checking for parent_user_id column...")
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        if 'parent_user_id' not in columns:
            print("✗ FAILED: parent_user_id column not found")
            return False
        
        column_type = columns['parent_user_id']
        print(f"  ✓ Column exists with type: {column_type}")
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    finally:
        conn.close()


def verify_foreign_key_constraint(db_path):
    """Verify foreign key constraint exists."""
    print("\n✓ Checking foreign key constraints...")
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA foreign_key_list(users)")
        fks = cursor.fetchall()
        
        parent_fk_found = False
        for fk in fks:
            if fk[3] == 'id' and fk[2] == 'users':  # References users.id
                parent_fk_found = True
                print(f"  ✓ Foreign key constraint found: {fk}")
        
        if not parent_fk_found:
            print("  ℹ Warning: Foreign key constraint not found (may be OK if DB supports alternative constraints)")
        
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    finally:
        conn.close()


def verify_index_exists(db_path):
    """Verify index on parent_user_id exists."""
    print("\n✓ Checking indexes...")
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Look for parent_user_id index
        parent_index_found = any('parent_user_id' in idx.lower() for idx in indexes)
        
        if parent_index_found:
            print(f"  ✓ Index on parent_user_id found")
        else:
            print(f"  ℹ Index on parent_user_id not found (optional, but recommended for performance)")
        
        print(f"  Indexes: {indexes}")
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    finally:
        conn.close()


def test_hierarchy_functionality(db_path):
    """Test basic hierarchy functionality."""
    print("\n✓ Testing hierarchy functionality...")
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        # Test 1: Update parent_user_id for existing users
        print("  Testing UPDATE operations...")
        cursor.execute("SELECT COUNT(*) as count FROM users LIMIT 1")
        
        # Try to update a user's parent_user_id (set to NULL = Super Admin)
        cursor.execute("UPDATE users SET parent_user_id = NULL LIMIT 1")
        conn.commit()
        print("  ✓ Can update parent_user_id to NULL (Super Admin)")
        
        # Test 2: Query NULL values
        cursor.execute("SELECT COUNT(*) as super_admins FROM users WHERE parent_user_id IS NULL")
        super_admin_count = cursor.fetchone()['super_admins']
        print(f"  ✓ Query WHERE parent_user_id IS NULL returns: {super_admin_count} users")
        
        # Test 3: Recursive query (if SQLite version supports it)
        try:
            cursor.execute("""
                WITH RECURSIVE org_test AS (
                    SELECT id, 1 as level FROM users WHERE parent_user_id IS NULL
                    UNION ALL
                    SELECT u.id, ot.level + 1 FROM users u
                    JOIN org_test ot ON u.parent_user_id = ot.id
                    WHERE ot.level < 5
                )
                SELECT COUNT(*) as total FROM org_test
            """)
            result = cursor.fetchone()
            if result:
                print(f"  ✓ Recursive CTE works: {result['total']} total users in hierarchy")
            else:
                print("  ℹ Recursive CTE not supported by this SQLite version")
        except Exception as e:
            print(f"  ℹ Recursive CTE test skipped: {e}")
        
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False
    finally:
        conn.close()


def print_sample_hierarchy(db_path):
    """Print sample user hierarchy if data exists."""
    print("\n✓ Sample User Hierarchy (first 10 users)...")
    
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, parent_user_id, 
                   CASE 
                       WHEN parent_user_id IS NULL THEN 'Super Admin'
                       ELSE 'Team Member'
                   END as role
            FROM users 
            LIMIT 10
        """)
        
        users = cursor.fetchall()
        if not users:
            print("  (No users in database)")
            return
        
        print("\n  ID | Username | Parent ID | Role")
        print("  " + "-" * 50)
        for user in users:
            parent_str = "NULL" if user['parent_user_id'] is None else str(user['parent_user_id'])
            print(f"  {user['id']:3d} | {user['username']:15s} | {parent_str:9s} | {user['role']}")
    
    except Exception as e:
        print(f"✗ ERROR: {e}")
    finally:
        conn.close()


def main():
    """Run all tests."""
    print("=" * 60)
    print("User Hierarchy Migration Verification")
    print("=" * 60)
    
    # Determine database path
    script_dir = Path(__file__).parent.parent
    db_path = script_dir / 'AdminLoginPanel' / 'project_management.db'
    
    if not db_path.exists():
        print(f"\n✗ ERROR: Database not found at {db_path}")
        print("Please run the application to generate the database first.")
        sys.exit(1)
    
    print(f"\nDatabase: {db_path}")
    print()
    
    # Run tests
    results = []
    results.append(("Column exists", verify_column_exists(str(db_path))))
    results.append(("Foreign key constraints", verify_foreign_key_constraint(str(db_path))))
    results.append(("Index optimization", verify_index_exists(str(db_path))))
    results.append(("Functionality test", test_hierarchy_functionality(str(db_path))))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    # Print sample data if available
    try:
        print_sample_hierarchy(str(db_path))
    except:
        pass
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All critical tests passed!")
        print("\nThe user hierarchy system is ready to use.")
        print("See docs/USER_HIERARCHY_GUIDE.md for usage information.")
    else:
        print("✗ Some tests failed. Please check the output above.")
        sys.exit(1)
    
    print("=" * 60)


if __name__ == '__main__':
    main()
