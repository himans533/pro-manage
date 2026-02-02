import sqlite3
import os

DB_PATH = 'project_management.db'

def update_db():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Add Super Admin role
        cursor.execute("INSERT OR IGNORE INTO usertypes (user_role) VALUES ('Super Admin')")
        print("Added Super Admin role.")
        
        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_db()
