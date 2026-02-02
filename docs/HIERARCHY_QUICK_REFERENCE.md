# User Hierarchy - Quick Reference Guide

## TL;DR

A `parent_user_id` column (self-referential FK) creates a 3-level hierarchy:
- **NULL** = Super Admin
- **Manager ID** = Team Member under that manager
- Unlimited levels supported via recursive queries

## Setup

```bash
# 1. Apply migration
sqlite3 AdminLoginPanel/project_management.db < scripts/add_user_hierarchy.sql

# 2. Verify
python scripts/test_hierarchy_migration.py
```

## Common Operations

### Get Team Members

```python
from scripts.hierarchy_utils import UserHierarchyManager
manager = UserHierarchyManager('project_management.db')

# Direct reports only
team = manager.get_direct_reports(user_id)

# All subordinates (recursive)
all_team = manager.get_all_subordinates(user_id)
```

### Get Manager/Boss

```python
# Get reporting chain
chain = manager.get_parent_chain(user_id)

# Direct manager is second item
if len(chain) > 1:
    direct_manager = chain[1]
```

### Set Hierarchy

```python
# Make user_3 report to user_2
manager.set_parent(user_3, user_2)

# Make user_2 a Super Admin
manager.set_parent(user_2, None)
```

### Check If Subordinate

```python
is_report = manager.is_subordinate_of(user_4, user_2)
```

## SQL Cheat Sheet

### All Super Admins
```sql
SELECT * FROM users WHERE parent_user_id IS NULL;
```

### Direct Reports
```sql
SELECT * FROM users WHERE parent_user_id = ?;
```

### All Subordinates (Recursive)
```sql
WITH RECURSIVE subs AS (
    SELECT id FROM users WHERE parent_user_id = ?
    UNION ALL
    SELECT u.id FROM users u JOIN subs ON u.parent_user_id = subs.id
)
SELECT * FROM users WHERE id IN (SELECT id FROM subs);
```

### Full Org Chart
```sql
WITH RECURSIVE org AS (
    SELECT id, username, parent_user_id, 1 as lvl
    FROM users WHERE parent_user_id IS NULL
    UNION ALL
    SELECT u.id, u.username, u.parent_user_id, o.lvl + 1
    FROM users u JOIN org o ON u.parent_user_id = o.id
)
SELECT * FROM org ORDER BY lvl, parent_user_id;
```

## Flask Integration

```python
from scripts.hierarchy_utils import UserHierarchyManager

hierarchy = UserHierarchyManager(DB_PATH)

# List my team
@app.route('/api/team')
def my_team():
    user_id = session['user_id']
    return jsonify(hierarchy.get_all_subordinates(user_id))

# Org chart
@app.route('/api/org-chart')
def org_chart():
    return jsonify(hierarchy.get_organization_tree())
```

## Database Schema

```sql
-- New column (already added by migration)
ALTER TABLE users ADD COLUMN parent_user_id INTEGER DEFAULT NULL;

-- Foreign key (self-referential)
ALTER TABLE users ADD CONSTRAINT fk_parent_user 
FOREIGN KEY (parent_user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Index for performance
CREATE INDEX idx_parent_user_id ON users(parent_user_id);
```

## Python API

| Method | Use Case |
|--------|----------|
| `set_parent(user, parent)` | Assign/change manager |
| `get_direct_reports(user)` | Get immediate team |
| `get_all_subordinates(user)` | Get entire subtree |
| `get_parent_chain(user)` | Get hierarchy upwards |
| `get_hierarchy_level(user)` | Get user's position |
| `is_subordinate_of(user, mgr)` | Check relationship |
| `get_organization_tree()` | Get full org chart |

## Query Pattern

All queries follow this structure:

1. **Simple lookups** → Direct SQL or single method call
2. **Recursive needs** → Use CTE (WITH RECURSIVE) or method
3. **Performance** → Index already created, just use it

## Examples

### Example 1: Build Team Report

```python
manager = UserHierarchyManager('project_management.db')

def generate_team_report(manager_id):
    team = manager.get_all_subordinates(manager_id)
    for member in team:
        print(f"Level {member['level']}: {member['username']}")
```

### Example 2: Check Authority

```python
def can_manage(current_user_id, target_user_id):
    """Check if current_user can manage target_user"""
    return manager.is_subordinate_of(target_user_id, current_user_id)
```

### Example 3: Approval Chain

```python
def get_approval_chain(user_id):
    """Get all managers in approval hierarchy"""
    chain = manager.get_parent_chain(user_id)
    return chain[1:] if len(chain) > 1 else []  # Skip the user itself
```

## Gotchas

❌ Don't do this:
```python
# No circular hierarchy
manager.set_parent(user_2, user_3)  # user_2 -> user_3
manager.set_parent(user_3, user_2)  # Creates circle!
```

✅ Do this:
```python
# Verify before setting
if not manager.is_subordinate_of(parent_id, child_id):
    manager.set_parent(child_id, parent_id)
```

## Limits

- **Hierarchy depth:** Unlimited (recursive)
- **Team size:** Unlimited
- **Performance:** O(1) for direct reports, O(n) for recursive
- **Index:** Ensures fast lookups on parent_user_id

## Verification

```bash
# Check if setup is correct
python scripts/test_hierarchy_migration.py

# Expected output: ✓ All critical tests passed!
```

## Files

| File | Purpose |
|------|---------|
| `scripts/add_user_hierarchy.sql` | Database migration |
| `scripts/hierarchy_utils.py` | Python API |
| `scripts/test_hierarchy_migration.py` | Verification |
| `docs/USER_HIERARCHY_GUIDE.md` | Full documentation |

## Need Help?

1. **Setup issues** → Run `test_hierarchy_migration.py`
2. **Query problems** → Check `USER_HIERARCHY_GUIDE.md`
3. **API questions** → See `hierarchy_utils.py` docstrings
4. **Examples** → Look at Flask integration section above

---

**Remember:** 
- `parent_user_id = NULL` → Super Admin
- `parent_user_id = X` → Reports to user X
- Everything is recursive-capable via SQL CTEs
- Python methods handle recursion for you
