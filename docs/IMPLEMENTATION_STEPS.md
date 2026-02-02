# User Hierarchy Implementation - Step-by-Step Guide

## Overview

This guide walks you through implementing the user hierarchy system in the existing Project Management application. The implementation is **non-destructive** and **fully backward compatible**.

## Timeline: 5-10 minutes

## Prerequisites

- Access to the SQLite database at `AdminLoginPanel/project_management.db`
- Python 3.x installed
- Terminal/command line access

## Step 1: Backup Database (Optional but Recommended)

```bash
# Create a backup
cp AdminLoginPanel/project_management.db AdminLoginPanel/project_management.db.backup

echo "✓ Database backed up successfully"
```

**Why:** Safety first. If anything goes wrong, you have a backup to restore.

## Step 2: Apply Database Migration

### Option A: Using SQLite CLI (Recommended)

```bash
# Navigate to project root
cd /path/to/project

# Apply migration
sqlite3 AdminLoginPanel/project_management.db < scripts/add_user_hierarchy.sql

echo "✓ Migration applied successfully"
```

### Option B: Manual SQL in Python

```python
import sqlite3

conn = sqlite3.connect('AdminLoginPanel/project_management.db')
conn.execute('PRAGMA foreign_keys = ON')
cursor = conn.cursor()

# Add column
cursor.execute('ALTER TABLE users ADD COLUMN parent_user_id INTEGER DEFAULT NULL')

# Add foreign key
cursor.execute('''
    ALTER TABLE users ADD CONSTRAINT fk_parent_user 
    FOREIGN KEY (parent_user_id) REFERENCES users(id) ON DELETE SET NULL
''')

# Add index
cursor.execute('CREATE INDEX IF NOT EXISTS idx_parent_user_id ON users(parent_user_id)')

conn.commit()
conn.close()

print("✓ Migration applied successfully")
```

## Step 3: Verify Migration

### Run Verification Script

```bash
# Run the test script
python scripts/test_hierarchy_migration.py
```

**Expected Output:**
```
============================================================
User Hierarchy Migration Verification
============================================================

Database: AdminLoginPanel/project_management.db

✓ Checking for parent_user_id column...
  ✓ Column exists with type: INTEGER

✓ Checking foreign key constraints...
  ✓ Foreign key constraint found

✓ Checking indexes...
  ✓ Index on parent_user_id found

✓ Testing hierarchy functionality...
  ✓ Can update parent_user_id to NULL (Super Admin)
  ✓ Query WHERE parent_user_id IS NULL returns: X users

============================================================
Verification Summary
============================================================
✓ PASS: Column exists
✓ PASS: Foreign key constraints
✓ PASS: Index optimization
✓ PASS: Functionality test

✓ All critical tests passed!

The user hierarchy system is ready to use.
See docs/USER_HIERARCHY_GUIDE.md for usage information.
============================================================
```

**If tests fail:** Check the output for specific errors and review the troubleshooting section at the bottom.

## Step 4: Initialize Hierarchy in Application

### Add to Flask Application (`app.py`)

```python
# Add near the top of app.py, after imports
from scripts.hierarchy_utils import UserHierarchyManager

# Initialize the hierarchy manager after creating app
app = Flask(__name__)

# ... other Flask setup ...

# Initialize hierarchy manager
hierarchy_manager = UserHierarchyManager(DB_PATH)
```

## Step 5: Set Initial Hierarchy (Optional)

Set up the initial hierarchy structure with your existing users.

### Option A: Using Python Script

```python
# scripts/setup_initial_hierarchy.py
from hierarchy_utils import UserHierarchyManager

def setup_initial_hierarchy():
    manager = UserHierarchyManager('AdminLoginPanel/project_management.db')
    
    # Example: Set up user relationships
    # These are example IDs - replace with actual user IDs from your database
    
    # Make user 1 a Super Admin (already NULL by default)
    manager.set_parent(1, None)
    
    # Make user 2 and 3 report to user 1
    manager.set_parent(2, 1)
    manager.set_parent(3, 1)
    
    # Make user 4 and 5 report to user 2
    manager.set_parent(4, 2)
    manager.set_parent(5, 2)
    
    print("✓ Initial hierarchy set up successfully")

if __name__ == '__main__':
    setup_initial_hierarchy()
```

Run it:
```bash
python scripts/setup_initial_hierarchy.py
```

### Option B: SQL Command

```sql
-- Replace IDs with your actual user IDs
UPDATE users SET parent_user_id = NULL WHERE id = 1;  -- Super Admin
UPDATE users SET parent_user_id = 1 WHERE id IN (2, 3);  -- Coordinators
UPDATE users SET parent_user_id = 2 WHERE id IN (4, 5);  -- Team Members
```

## Step 6: Add API Endpoints to Flask

Add these endpoints to your Flask application to expose hierarchy functionality:

```python
# Add to app.py

@app.route('/api/hierarchy/team', methods=['GET'])
def get_my_team():
    """Get all team members of current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    team = hierarchy_manager.get_direct_reports(user_id)
    return jsonify(team)


@app.route('/api/hierarchy/org-chart', methods=['GET'])
def get_org_chart():
    """Get complete organization chart"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    org_tree = hierarchy_manager.get_organization_tree()
    return jsonify(org_tree)


@app.route('/api/hierarchy/chain/<int:user_id>', methods=['GET'])
def get_user_chain(user_id):
    """Get reporting chain for a user"""
    auth_user_id = session.get('user_id')
    if not auth_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chain = hierarchy_manager.get_parent_chain(user_id)
    return jsonify(chain)


@app.route('/api/hierarchy/manager/<int:user_id>', methods=['GET'])
def get_user_manager(user_id):
    """Get direct manager of a user"""
    auth_user_id = session.get('user_id')
    if not auth_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chain = hierarchy_manager.get_parent_chain(user_id)
    if len(chain) > 1:
        return jsonify(chain[1])  # Direct parent
    return jsonify({'error': 'No manager assigned'}), 404


@app.route('/api/hierarchy/subordinates/<int:user_id>', methods=['GET'])
def get_all_subordinates(user_id):
    """Get all subordinates of a user"""
    auth_user_id = session.get('user_id')
    if not auth_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    subordinates = hierarchy_manager.get_all_subordinates(user_id)
    return jsonify(subordinates)


@app.route('/api/hierarchy/set-parent/<int:user_id>/<int:parent_id>', methods=['POST'])
def set_parent(user_id, parent_id):
    """Set parent for a user (admin only)"""
    auth_user_id = session.get('user_id')
    if not auth_user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Add permission check here (only admins can set hierarchy)
    success = hierarchy_manager.set_parent(user_id, parent_id)
    return jsonify({'success': success})
```

## Step 7: Test the Implementation

### Test 1: Direct API Calls

```bash
# Test organization chart endpoint
curl http://localhost:5000/api/hierarchy/org-chart

# Test team endpoint
curl http://localhost:5000/api/hierarchy/team

# Test user chain endpoint
curl http://localhost:5000/api/hierarchy/chain/3
```

### Test 2: Python Console

```python
from scripts.hierarchy_utils import UserHierarchyManager

manager = UserHierarchyManager('AdminLoginPanel/project_management.db')

# Test getting reports
reports = manager.get_direct_reports(1)
print(f"Reports: {reports}")

# Test getting chain
chain = manager.get_parent_chain(3)
print(f"Chain: {chain}")

# Test org tree
tree = manager.get_organization_tree()
print(f"Org Tree: {tree}")
```

## Step 8: Update Frontend (if applicable)

If you have HTML templates, add hierarchy display:

```html
<!-- admin-dashboard.html -->
<div id="organization-chart">
    <h2>Organization Hierarchy</h2>
    <div id="org-tree"></div>
</div>

<script>
    // Fetch and display org chart
    fetch('/api/hierarchy/org-chart')
        .then(response => response.json())
        .then(data => {
            console.log('Organization chart:', data);
            // Render hierarchy visualization
        });
    
    // Fetch user's team
    fetch('/api/hierarchy/team')
        .then(response => response.json())
        .then(data => {
            console.log('My team:', data);
            // Render team list
        });
</script>
```

## Step 9: Document Changes

Add documentation to your project:

```markdown
# User Hierarchy System

## Overview
This project now includes a hierarchical user structure with the following levels:
- **Super Admin**: parent_user_id = NULL
- **Project Coordinator**: parent_user_id = Super Admin ID
- **Team Member**: parent_user_id = Coordinator ID

## Database Schema
- Added `parent_user_id` column to users table
- Self-referential foreign key constraint
- Index on parent_user_id for performance

## API Endpoints
- `GET /api/hierarchy/team` - Get my team members
- `GET /api/hierarchy/org-chart` - Get full organization chart
- `GET /api/hierarchy/chain/<user_id>` - Get reporting chain
- `GET /api/hierarchy/manager/<user_id>` - Get user's manager
- `GET /api/hierarchy/subordinates/<user_id>` - Get all subordinates
- `POST /api/hierarchy/set-parent/<user_id>/<parent_id>` - Set hierarchy

## Usage Examples
See docs/USER_HIERARCHY_GUIDE.md for detailed examples.
```

## Step 10: Train Team

Brief summary for your development team:

```
User Hierarchy Implementation Complete!

What's New:
✓ Added parent_user_id column to users table
✓ Created self-referential foreign key
✓ Added efficient index on parent_user_id

How to Use:
- Use UserHierarchyManager class for queries
- Call get_direct_reports() for team
- Call get_all_subordinates() for full subtree
- Call get_parent_chain() for reporting line

Documentation:
- docs/USER_HIERARCHY_GUIDE.md - Complete guide
- docs/HIERARCHY_QUICK_REFERENCE.md - Quick reference
- scripts/hierarchy_utils.py - Python API

Questions?
See docs/ folder or review example code in this guide.
```

## Troubleshooting

### Issue: "Column already exists"

**Cause:** Migration already applied

**Solution:**
```sql
-- Verify column exists
PRAGMA table_info(users);
-- Look for parent_user_id in the output
```

### Issue: "No such table: users"

**Cause:** Database path wrong

**Solution:**
```bash
# Check database location
find . -name "project_management.db"

# Update paths in scripts accordingly
```

### Issue: Foreign key constraint error

**Cause:** Foreign keys not enabled

**Solution:**
```python
# Ensure in database connection:
conn.execute('PRAGMA foreign_keys = ON')
```

### Issue: Verification script fails

**Cause:** Migration not applied correctly

**Solution:**
```bash
# Re-run migration
sqlite3 AdminLoginPanel/project_management.db < scripts/add_user_hierarchy.sql

# Re-run verification
python scripts/test_hierarchy_migration.py
```

## Rollback (If Needed)

If you need to revert the changes:

```bash
# Option 1: Restore backup
cp AdminLoginPanel/project_management.db.backup AdminLoginPanel/project_management.db

# Option 2: Manually remove column (if no backup)
# WARNING: This removes all hierarchy data!
sqlite3 AdminLoginPanel/project_management.db << EOF
DROP INDEX idx_parent_user_id;
ALTER TABLE users DROP COLUMN parent_user_id;
EOF
```

## Success Checklist

- [ ] Database migration applied
- [ ] Verification script passes
- [ ] Hierarchy manager initialized in Flask app
- [ ] API endpoints tested
- [ ] Hierarchy relationships set up
- [ ] Documentation updated
- [ ] Team trained on new system
- [ ] No errors in application logs
- [ ] Frontend displays hierarchy (if applicable)
- [ ] Backup created and stored safely

## What's Next?

1. **Org Chart UI**: Build visual representation of hierarchy
2. **Approval Workflows**: Route approvals up the chain
3. **Access Control**: Implement role-based permissions
4. **Notifications**: Alert managers of subordinate activities
5. **Reporting**: Generate team performance reports

## Support

For detailed information, refer to:
- `/docs/USER_HIERARCHY_GUIDE.md` - Full documentation
- `/docs/HIERARCHY_QUICK_REFERENCE.md` - Quick reference
- `/scripts/hierarchy_utils.py` - API documentation
- `/docs/HIERARCHY_VISUAL_GUIDE.md` - Visual examples

---

**Congratulations!** Your user hierarchy system is now ready to use. 🎉
