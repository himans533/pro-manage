"""
User Hierarchy Utilities
========================
Helper functions for working with the hierarchical user structure in the Project Management System.

Hierarchy Structure:
- Super Admin (parent_user_id = NULL)
  ├── Project Coordinator 1 (parent_user_id = Super Admin ID)
  │   ├── Team Member 1
  │   ├── Team Member 2
  │   └── Team Member 3
  └── Project Coordinator 2 (parent_user_id = Super Admin ID)
      ├── Team Member 4
      └── Team Member 5
"""

import sqlite3
from typing import List, Dict, Optional, Tuple


class UserHierarchyManager:
    """Manages user hierarchical relationships."""
    
    def __init__(self, db_path: str):
        """Initialize with database path."""
        self.db_path = db_path
    
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    
    def set_parent(self, user_id: int, parent_user_id: Optional[int]) -> bool:
        """
        Set a parent for a user (establish hierarchy relationship).
        
        Args:
            user_id: The user to set parent for
            parent_user_id: The parent user ID (None for Super Admin)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Prevent circular hierarchy (user cannot be their own parent)
            if user_id == parent_user_id and parent_user_id is not None:
                print(f"Error: User {user_id} cannot be their own parent")
                return False
            
            cursor.execute(
                "UPDATE users SET parent_user_id = ? WHERE id = ?",
                (parent_user_id, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting parent: {e}")
            return False
    
    def get_direct_reports(self, manager_user_id: int) -> List[Dict]:
        """
        Get all direct reports (immediate subordinates) of a user.
        
        Args:
            manager_user_id: The manager's user ID
        
        Returns:
            List of user dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT id, username, email, user_type_id, parent_user_id, 
                       department, created_at
                FROM users 
                WHERE parent_user_id = ?
                ORDER BY username
                """,
                (manager_user_id,)
            )
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting direct reports: {e}")
            return []
    
    def get_all_subordinates(self, manager_user_id: int) -> List[Dict]:
        """
        Get ALL subordinates (direct + indirect) of a user recursively.
        
        Args:
            manager_user_id: The manager's user ID
        
        Returns:
            List of all subordinate user dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Recursive query to get all subordinates
            cursor.execute(
                """
                WITH RECURSIVE subordinates AS (
                    SELECT id, username, email, user_type_id, parent_user_id, 
                           department, 1 as level
                    FROM users 
                    WHERE parent_user_id = ?
                    
                    UNION ALL
                    
                    SELECT u.id, u.username, u.email, u.user_type_id, 
                           u.parent_user_id, u.department, s.level + 1
                    FROM users u
                    JOIN subordinates s ON u.parent_user_id = s.id
                )
                SELECT * FROM subordinates
                ORDER BY level, username
                """,
                (manager_user_id,)
            )
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting all subordinates: {e}")
            return []
    
    def get_parent_chain(self, user_id: int) -> List[Dict]:
        """
        Get the full parent chain (hierarchy upwards) for a user.
        Shows: User → Coordinator → Super Admin
        
        Args:
            user_id: The user's ID
        
        Returns:
            List of users from bottom to top in hierarchy
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Recursive query to get all parents
            cursor.execute(
                """
                WITH RECURSIVE parent_chain AS (
                    SELECT id, username, email, user_type_id, parent_user_id, 
                           1 as level
                    FROM users 
                    WHERE id = ?
                    
                    UNION ALL
                    
                    SELECT u.id, u.username, u.email, u.user_type_id, 
                           u.parent_user_id, pc.level + 1
                    FROM users u
                    JOIN parent_chain pc ON u.id = pc.parent_user_id
                )
                SELECT * FROM parent_chain
                ORDER BY level
                """,
                (user_id,)
            )
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting parent chain: {e}")
            return []
    
    def get_hierarchy_level(self, user_id: int) -> Optional[str]:
        """
        Determine the hierarchy level of a user based on parent_user_id.
        
        Args:
            user_id: The user's ID
        
        Returns:
            'Super Admin' if parent_user_id is NULL
            'Project Coordinator' or 'Team Member' based on user_type_id
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT parent_user_id, user_type_id FROM users WHERE id = ?",
                (user_id,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            if row['parent_user_id'] is None:
                return 'Super Admin'
            else:
                # Can determine more specific level if user_type_id is used
                return 'Team Member'
        except Exception as e:
            print(f"Error getting hierarchy level: {e}")
            return None
    
    def is_subordinate_of(self, user_id: int, manager_user_id: int) -> bool:
        """
        Check if a user is a subordinate (direct or indirect) of another user.
        
        Args:
            user_id: The user to check
            manager_user_id: The potential manager
        
        Returns:
            True if user_id is a subordinate of manager_user_id
        """
        subordinates = self.get_all_subordinates(manager_user_id)
        return any(sub['id'] == user_id for sub in subordinates)
    
    def get_organization_tree(self) -> List[Dict]:
        """
        Get the complete organization tree structure.
        
        Returns:
            List of Super Admins with their hierarchies
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get all super admins (parent_user_id = NULL)
            cursor.execute(
                """
                WITH RECURSIVE org_tree AS (
                    SELECT id, username, email, user_type_id, parent_user_id, 
                           department, 1 as level
                    FROM users 
                    WHERE parent_user_id IS NULL
                    
                    UNION ALL
                    
                    SELECT u.id, u.username, u.email, u.user_type_id, 
                           u.parent_user_id, u.department, ot.level + 1
                    FROM users u
                    JOIN org_tree ot ON u.parent_user_id = ot.id
                )
                SELECT * FROM org_tree
                ORDER BY level, parent_user_id, username
                """
            )
            
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            print(f"Error getting organization tree: {e}")
            return []


# =============================================
# USAGE EXAMPLES
# =============================================

def example_usage():
    """Demonstrate hierarchy manager usage."""
    
    manager = UserHierarchyManager('project_management.db')
    
    # Example 1: Set up hierarchy
    print("=== Setting up hierarchy ===")
    manager.set_parent(2, None)  # User 2 is Super Admin
    manager.set_parent(3, 2)     # User 3 reports to User 2 (Project Coordinator)
    manager.set_parent(4, 3)     # User 4 reports to User 3 (Team Member)
    manager.set_parent(5, 3)     # User 5 reports to User 3 (Team Member)
    
    # Example 2: Get direct reports
    print("\n=== Direct reports of Super Admin (User 2) ===")
    reports = manager.get_direct_reports(2)
    for user in reports:
        print(f"  - {user['username']} ({user['email']})")
    
    # Example 3: Get all subordinates
    print("\n=== All subordinates of Super Admin (User 2) ===")
    all_subs = manager.get_all_subordinates(2)
    for user in all_subs:
        print(f"  Level {user['level']}: {user['username']}")
    
    # Example 4: Get parent chain
    print("\n=== Parent chain for User 5 ===")
    chain = manager.get_parent_chain(5)
    for user in chain:
        print(f"  Level {user['level']}: {user['username']}")
    
    # Example 5: Check hierarchy level
    print("\n=== Hierarchy levels ===")
    for user_id in [2, 3, 4, 5]:
        level = manager.get_hierarchy_level(user_id)
        print(f"  User {user_id}: {level}")
    
    # Example 6: Check subordinate relationship
    print("\n=== Subordinate checks ===")
    print(f"  Is User 4 subordinate of User 2? {manager.is_subordinate_of(4, 2)}")
    print(f"  Is User 4 subordinate of User 3? {manager.is_subordinate_of(4, 3)}")
    print(f"  Is User 3 subordinate of User 4? {manager.is_subordinate_of(3, 4)}")
    
    # Example 7: Get full organization tree
    print("\n=== Full organization tree ===")
    tree = manager.get_organization_tree()
    for user in tree:
        indent = "  " * (user['level'] - 1)
        print(f"{indent}├─ {user['username']} (ID: {user['id']})")


if __name__ == '__main__':
    # Uncomment to run examples
    # example_usage()
    pass
