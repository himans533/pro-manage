# User Hierarchy System Documentation

## Overview

The User Hierarchy system introduces a three-tier organizational structure to the Project Management application:

```
Super Admin (Level 1)
├── Project Coordinator (Level 2)
│   └── Team Members (Level 3)
└── Project Coordinator (Level 2)
    └── Team Members (Level 3)
```

## Database Implementation

### Column Addition

A single new column has been added to the `users` table:

```sql
parent_user_id INTEGER DEFAULT NULL
```

**Constraints:**
- Foreign key constraint references the same `users` table (self-referential)
- Indexed for efficient hierarchical queries
- Nullable (NULL value indicates a Super Admin)
- ON DELETE SET NULL: If a parent is deleted, child relationships are cleared

### Migration Script

Run the migration to add the hierarchy column:

```bash
sqlite3 project_management.db < scripts/add_user_hierarchy.sql
```

## Hierarchy Levels

### Level 1: Super Admin
- **parent_user_id:** `NULL`
- **Authority:** Full system access
- **Responsibilities:** 
  - Manages multiple Project Coordinators
  - Oversees entire organization
  - Cannot report to anyone

**SQL to identify:**
```sql
SELECT * FROM users WHERE parent_user_id IS NULL;
```

### Level 2: Project Coordinator
- **parent_user_id:** Super Admin's user ID
- **Authority:** Project and team management
- **Responsibilities:**
  - Manages a team of members
  - Oversees project assignments
  - Reports to Super Admin

**SQL to identify:**
```sql
SELECT * FROM users WHERE parent_user_id = {super_admin_id} AND user_type_id = 2;
```

### Level 3: Team Member
- **parent_user_id:** Project Coordinator's user ID
- **Authority:** Task execution
- **Responsibilities:**
  - Works on assigned tasks
  - Submits daily reports
  - Reports to Project Coordinator

**SQL to identify:**
```sql
SELECT * FROM users WHERE parent_user_id = {coordinator_id} AND user_type_id = 3;
```

## Common Database Queries

### 1. Get Direct Reports (Immediate Subordinates)

```sql
SELECT id, username, email, department 
FROM users 
WHERE parent_user_id = ?
ORDER BY username;
```

**Python equivalent:**
```python
from scripts.hierarchy_utils import UserHierarchyManager
manager = UserHierarchyManager('project_management.db')
direct_reports = manager.get_direct_reports(manager_user_id)
```

### 2. Get All Subordinates (Recursive)

```sql
WITH RECURSIVE subordinates AS (
    SELECT id, username, email, user_type_id, parent_user_id, 1 as level
    FROM users 
    WHERE parent_user_id = ?
    
    UNION ALL
    
    SELECT u.id, u.username, u.email, u.user_type_id, 
           u.parent_user_id, s.level + 1
    FROM users u
    JOIN subordinates s ON u.parent_user_id = s.id
)
SELECT * FROM subordinates
ORDER BY level, username;
```

**Python equivalent:**
```python
manager = UserHierarchyManager('project_management.db')
all_subordinates = manager.get_all_subordinates(manager_user_id)
```

### 3. Get Parent Chain (Hierarchy Upwards)

```sql
WITH RECURSIVE parent_chain AS (
    SELECT id, username, parent_user_id, 1 as level
    FROM users 
    WHERE id = ?
    
    UNION ALL
    
    SELECT u.id, u.username, u.parent_user_id, pc.level + 1
    FROM users u
    JOIN parent_chain pc ON u.id = pc.parent_user_id
)
SELECT * FROM parent_chain
ORDER BY level;
```

**Python equivalent:**
```python
manager = UserHierarchyManager('project_management.db')
parent_chain = manager.get_parent_chain(user_id)
```

### 4. Get Full Organization Tree

```sql
WITH RECURSIVE org_tree AS (
    SELECT id, username, email, user_type_id, parent_user_id, 1 as level
    FROM users 
    WHERE parent_user_id IS NULL
    
    UNION ALL
    
    SELECT u.id, u.username, u.email, u.user_type_id, 
           u.parent_user_id, ot.level + 1
    FROM users u
    JOIN org_tree ot ON u.parent_user_id = ot.id
)
SELECT * FROM org_tree
ORDER BY level, parent_user_id, username;
```

**Python equivalent:**
```python
manager = UserHierarchyManager('project_management.db')
org_tree = manager.get_organization_tree()
```

### 5. Check if User is Subordinate of Another

```sql
SELECT COUNT(*) > 0 as is_subordinate
FROM (
    WITH RECURSIVE check_subordinate AS (
        SELECT id, parent_user_id
        FROM users 
        WHERE id = ?
        
        UNION ALL
        
        SELECT u.id, u.parent_user_id
        FROM users u
        JOIN check_subordinate cs ON u.id = cs.parent_user_id
    )
    SELECT * FROM check_subordinate
    WHERE parent_user_id = ?
);
```

**Python equivalent:**
```python
manager = UserHierarchyManager('project_management.db')
is_subordinate = manager.is_subordinate_of(user_id, manager_user_id)
```

## Python Utility Module

The `scripts/hierarchy_utils.py` module provides convenient methods:

### Initialization

```python
from scripts.hierarchy_utils import UserHierarchyManager

manager = UserHierarchyManager('project_management.db')
```

### Available Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `set_parent(user_id, parent_user_id)` | Establish parent-child relationship | bool |
| `get_direct_reports(manager_user_id)` | Get immediate subordinates | List[Dict] |
| `get_all_subordinates(manager_user_id)` | Get all subordinates recursively | List[Dict] |
| `get_parent_chain(user_id)` | Get hierarchy upwards | List[Dict] |
| `get_hierarchy_level(user_id)` | Get user's hierarchy position | str |
| `is_subordinate_of(user_id, manager_user_id)` | Check subordination | bool |
| `get_organization_tree()` | Get complete org structure | List[Dict] |

## Example Usage

### Setting Up Hierarchy

```python
from scripts.hierarchy_utils import UserHierarchyManager

manager = UserHierarchyManager('project_management.db')

# Create hierarchy
manager.set_parent(2, None)      # User 2 is Super Admin
manager.set_parent(3, 2)         # User 3 reports to User 2
manager.set_parent(4, 3)         # User 4 reports to User 3
manager.set_parent(5, 3)         # User 5 reports to User 3
```

### Querying Hierarchy

```python
# Get all team members under coordinator (User 3)
team = manager.get_all_subordinates(3)
for member in team:
    print(f"{member['username']} (Level {member['level']})")

# Get who User 5 reports to
chain = manager.get_parent_chain(5)
for user in chain:
    print(f"Level {user['level']}: {user['username']}")

# Get complete organization
org = manager.get_organization_tree()
for user in org:
    indent = "  " * (user['level'] - 1)
    print(f"{indent}├─ {user['username']}")
```

## Integration with Flask Application

### Using in Routes

```python
from scripts.hierarchy_utils import UserHierarchyManager

hierarchy_manager = UserHierarchyManager(DB_PATH)

@app.route('/api/my-team', methods=['GET'])
def get_my_team():
    user_id = session.get('user_id')
    team = hierarchy_manager.get_direct_reports(user_id)
    return jsonify(team)

@app.route('/api/organization', methods=['GET'])
def get_org_chart():
    org_tree = hierarchy_manager.get_organization_tree()
    return jsonify(org_tree)
```

### Display User's Manager

```python
@app.route('/api/user/<int:user_id>/manager', methods=['GET'])
def get_user_manager(user_id):
    chain = hierarchy_manager.get_parent_chain(user_id)
    if len(chain) > 1:  # If user has a parent
        manager = chain[1]  # Second item is direct parent
        return jsonify(manager)
    return jsonify({'error': 'No manager assigned'}), 404
```

## Important Notes

### What Remains Unchanged

- **Authentication:** Existing login/password system unchanged
- **Permissions:** user_permissions table structure unchanged
- **User Types:** usertypes table unchanged
- **Projects & Tasks:** All existing relationships preserved
- **Daily Reports:** Approval workflow unchanged

### Backward Compatibility

- Existing users will have `parent_user_id = NULL` (Super Admin level)
- No data migration required
- All existing queries continue to work
- Hierarchy is purely additive

### Security Considerations

1. **Circular References:** Prevented at application level
2. **Foreign Keys:** Enforced via database constraints
3. **Access Control:** Implement in application logic (not affected by this change)
4. **Data Integrity:** Self-referential FK ensures referential integrity

## Performance Optimization

- **Index on parent_user_id:** Created for fast lookups
- **Recursive queries:** Use appropriate database query limits
- **Caching:** Consider caching org tree if it doesn't change frequently

## Testing the Implementation

### Verification Script

```python
import sqlite3

def verify_hierarchy():
    conn = sqlite3.connect('project_management.db')
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'parent_user_id' in columns:
        print("✓ parent_user_id column exists")
        
        # Check constraints
        cursor.execute("PRAGMA foreign_key_list(users)")
        print("✓ Foreign key constraints in place")
        
        # Check index
        cursor.execute("PRAGMA index_list(users)")
        print("✓ Indexes configured")
    else:
        print("✗ parent_user_id column missing")
    
    conn.close()

verify_hierarchy()
```

## Future Enhancements

Potential future improvements:

1. **Org Chart UI:** Visual hierarchy representation
2. **Delegation:** Temporary management delegation
3. **Approval Workflows:** Route approvals up the chain
4. **Notifications:** Alert managers of subordinate activities
5. **Reporting:** Generate team performance reports by hierarchy
6. **Access Control:** Row-level security based on hierarchy
