import sqlite3
import os

DB_PATH = 'project_management.db'

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM usertypes")
        print("User Types:")
        for row in cursor.fetchall():
            print(row)
            
        cursor.execute("PRAGMA table_info(daily_task_reports)")
        print("\nDaily Task Reports Schema:")
        for row in cursor.fetchall():
            print(row)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_db()
