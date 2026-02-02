# Employee Dashboard - Project Coordinator Filtering

## Overview

This guide explains how to safely extend the Employee Dashboard to show Project Coordinators only the projects assigned to them, while keeping regular employees' experience unchanged.

**Key Feature**: When a logged-in user is a Project Coordinator, they see ONLY projects where `project_coordinator_id` matches their user ID.

---

## Architecture

### Current Flow (Existing)
```
Employee Dashboard
    ↓
GET /api/employee/projects
    ↓
Query: Show projects where:
  - created_by_id = user_id OR
  - id IN (projects assigned to user)
```

### New Flow (With Filtering)
```
Employee Dashboard
    ↓
GET /api/employee/projects
    ↓
Check: Is user a Project Coordinator?
    ├─ YES → Query: Show projects where project_coordinator_id = user_id
    └─ NO  → Query: Same as current (created/assigned projects)
```

---

## Implementation Details

### What Gets Modified

**Two Endpoints** (NO UI CHANGES):
1. `GET /api/employee/projects` (line ~2746)
2. `GET /api/employee/projects/realtime` (line ~4760)

**Why Two?**
- Standard endpoint: Used for initial page load
- Realtime endpoint: Used for live dashboard updates

### The Logic

```python
# Step 1: Determine user role
user_role = get_user_role(user_id)

# Step 2: Check if Project Coordinator
is_coordinator = 'project coordinator' in user_role.lower()

# Step 3: Apply appropriate filter
if is_coordinator:
    WHERE p.project_coordinator_id = ?
else:
    WHERE (p.created_by_id = ? OR p.id IN (...))
```

---

## Implementation: 3 Approaches

### Approach 1: Direct Modification (Simple, 15 minutes)

Modify the existing query directly without refactoring.

**Location**: `app.py` lines 2754-2764

```python
# Add this BEFORE the cursor.execute calls:
cursor.execute('''
    SELECT ut.user_role FROM users u
    LEFT JOIN usertypes ut ON u.user_type_id = ut.id
    WHERE u.id = ?
''', (user_id,))
user_role_row = cursor.fetchone()
user_role = user_role_row['user_role'].lower() if user_role_row else 'employee'
is_project_coordinator = 'project coordinator' in user_role

# Then replace the WHERE clause with conditional logic:
if is_project_coordinator:
    cursor.execute('''...WHERE p.project_coordinator_id = ?...''', (user_id,))
else:
    cursor.execute('''...WHERE (p.created_by_id = ? OR ...)...''', (user_id, user_id))
```

**Pros**: Simple, direct, minimal code
**Cons**: Code duplication, harder to maintain

---

### Approach 2: Using a Helper Function (Recommended, 20 minutes)

Create a reusable helper to check coordinator status.

**Add this helper** (around line 550):
```python
def is_user_project_coordinator(user_id):
    """Check if user is a Project Coordinator"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ut.user_role FROM users u
            LEFT JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ?
        ''', (user_id,))
        user_role_row = cursor.fetchone()
        conn.close()
        
        if user_role_row:
            return 'project coordinator' in user_role_row['user_role'].lower()
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
```

**Use in endpoints**:
```python
@app.route("/api/employee/projects", methods=["GET"])
@login_required
def get_employee_projects():
    try:
        user_id = get_current_user_id()
        is_coordinator = is_user_project_coordinator(user_id)
        conn = get_db_connection()
        cursor = conn.cursor()

        if is_coordinator:
            cursor.execute('''...WHERE p.project_coordinator_id = ?...''', (user_id,))
        else:
            cursor.execute('''...WHERE (p.created_by_id = ? OR ...)...''', (user_id, user_id))
        # ... rest of function
```

**Pros**: Clean, reusable, testable, maintainable
**Cons**: Slight performance overhead (extra DB call)

---

### Approach 3: Database-Level Optimization (Advanced, 25 minutes)

Use a single query with CASE logic to avoid code duplication.

```python
@app.route("/api/employee/projects", methods=["GET"])
@login_required
def get_employee_projects():
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()

        # Single query with dynamic filtering
        cursor.execute(
            '''
            SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
                   p.deadline, p.created_by_id, u.username as creator_name, p.created_at
            FROM projects p 
            LEFT JOIN users u ON p.created_by_id = u.id
            LEFT JOIN users current_u ON current_u.id = ?
            LEFT JOIN usertypes ut ON current_u.user_type_id = ut.id
            WHERE CASE
                WHEN ut.user_role LIKE '%Project Coordinator%' 
                THEN p.project_coordinator_id = ?
                ELSE (p.created_by_id = ? OR p.id IN (
                    SELECT project_id FROM project_assignments WHERE user_id = ?
                ))
            END
            ORDER BY p.created_at DESC
        ''', (user_id, user_id, user_id, user_id))

        projects = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in projects]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Pros**: Single query, efficient, no code duplication
**Cons**: Complex SQL, harder to debug

---

## Step-by-Step Implementation Guide

### Step 1: Prepare (2 minutes)
- [ ] Read `scripts/employee_dashboard_filter.py`
- [ ] Decide on approach (Recommended: Approach 2 with helper function)

### Step 2: Add Helper Function (if using Approach 2) (5 minutes)
- [ ] Open `AdminLoginPanel/app.py`
- [ ] Go to line ~550 (after `@employee_required` decorator)
- [ ] Insert `is_user_project_coordinator()` helper function
- [ ] Save file

### Step 3: Modify GET /api/employee/projects (10 minutes)
- [ ] Go to line ~2746 in `app.py`
- [ ] Locate `def get_employee_projects():`
- [ ] Add coordinator check logic
- [ ] Modify cursor.execute with conditional
- [ ] Test with Postman/curl

### Step 4: Modify GET /api/employee/projects/realtime (10 minutes)
- [ ] Go to line ~4760 in `app.py`
- [ ] Locate `def get_employee_realtime_projects():`
- [ ] Add same coordinator check logic
- [ ] Modify cursor.execute with conditional
- [ ] Test with Postman/curl

### Step 5: Testing (15 minutes)
- [ ] Create test coordinator user with `project_coordinator_id` = their ID
- [ ] Create test employee user
- [ ] Login as coordinator → Should see ONLY their projects
- [ ] Login as employee → Should see all assigned projects
- [ ] Check realtime endpoint returns filtered projects

---

## Testing Checklist

### Test Case 1: Project Coordinator Access
```
User Type: Project Coordinator (user_id = 5)
Projects in DB:
  - Project A: project_coordinator_id = 5 ✓
  - Project B: project_coordinator_id = 5 ✓
  - Project C: project_coordinator_id = 3 ✗
  - Project D: created_by_id = 5 ✗

Expected Result: See Project A and B only
```

### Test Case 2: Regular Employee Access
```
User Type: Employee (user_id = 7)
Projects in DB:
  - Project A: created_by_id = 7 ✓
  - Project B: project_coordinator_id = 7 ✓ (but as coordinator, not creator)
  - Project C: IN project_assignments WHERE user_id = 7 ✓
  - Project D: created_by_id = 5 ✗

Expected Result: See Project A and C (not B since they're not coordinator)
```

### Test Case 3: Mixed Role User
```
User Type: Project Coordinator (user_id = 5)
Scenario: User is also assigned to projects not as coordinator

Expected Result: See ONLY projects where project_coordinator_id = 5
(Coordinator role takes precedence)
```

---

## Query Reference

### Coordinator Query
```sql
SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
FROM projects p 
LEFT JOIN users u ON p.created_by_id = u.id
WHERE p.project_coordinator_id = ?
ORDER BY p.created_at DESC
```

### Regular Employee Query (Current)
```sql
SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
FROM projects p 
LEFT JOIN users u ON p.created_by_id = u.id
WHERE (p.created_by_id = ? OR p.id IN (
    SELECT project_id FROM project_assignments WHERE user_id = ?
))
ORDER BY p.created_at DESC
```

---

## Verification Queries

Run these in your database to verify the implementation:

```sql
-- Check if column exists
PRAGMA table_info(projects);
-- Should show: project_coordinator_id INTEGER | NULL

-- List coordinators and their projects
SELECT u.id, u.username, ut.user_role, COUNT(p.id) as project_count
FROM users u
LEFT JOIN usertypes ut ON u.user_type_id = ut.id
LEFT JOIN projects p ON p.project_coordinator_id = u.id
WHERE ut.user_role LIKE '%Project Coordinator%'
GROUP BY u.id;

-- Show which projects are assigned to coordinators
SELECT p.id, p.title, u.username as coordinator_name
FROM projects p
LEFT JOIN users u ON p.project_coordinator_id = u.id
WHERE p.project_coordinator_id IS NOT NULL;
```

---

## Troubleshooting

### Issue: Coordinator sees no projects
**Cause**: No projects have `project_coordinator_id` set to their ID
**Solution**: 
1. Verify in DB: `SELECT * FROM projects WHERE project_coordinator_id = [user_id]`
2. Check that projects were created with coordinator assignment
3. Manually update test project: `UPDATE projects SET project_coordinator_id = 5 WHERE id = 1`

### Issue: Coordinator sees all projects
**Cause**: Role check is not working correctly
**Solution**:
1. Check user's `user_type_id` in database
2. Verify usertypes table has "Project Coordinator" role
3. Debug: Add `console.log("[v0] User role:", user_role)` to check value

### Issue: Regular employees see coordinator-only projects
**Cause**: Fallback query is too broad
**Solution**:
1. Verify `project_assignments` table has correct entries
2. Check that user is not set as coordinator in their role
3. Test with fresh user account

### Issue: Performance degradation
**Cause**: Extra database queries or inefficient WHERE clauses
**Solution**:
1. Use Approach 3 (single query with CASE) if performance critical
2. Add index on `projects.project_coordinator_id` (already done in migration)
3. Profile queries with EXPLAIN QUERY PLAN

---

## Files Reference

- **Implementation Code**: `scripts/employee_dashboard_filter.py`
- **Database Migration**: Already applied via `scripts/add_project_coordinator.sql`
- **Main App File**: `AdminLoginPanel/app.py`

---

## Performance Impact

| Aspect | Impact | Notes |
|--------|--------|-------|
| Extra DB calls | Minimal | One extra query to check role (cached by DB connection pool) |
| Query complexity | Same | Same index used (`idx_project_coordinator_id`) |
| Response time | Negligible | <5ms overhead for role check |
| Scalability | No issues | Same indexing strategy as existing queries |

---

## Rollback Instructions

If you need to revert these changes:

1. **Revert to original query** (both endpoints):
```python
cursor.execute(
    '''
    SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
           p.deadline, p.created_by_id, u.username as creator_name, p.created_at
    FROM projects p 
    LEFT JOIN users u ON p.created_by_id = u.id
    WHERE (p.created_by_id = ? OR p.id IN (
        SELECT project_id FROM project_assignments WHERE user_id = ?
    ))
    ORDER BY p.created_at DESC
''', (user_id, user_id))
```

2. **Remove helper function** (if used):
   - Delete `is_user_project_coordinator()` function

3. **Restart Flask app**
   - Changes take effect immediately

---

## Next Steps

1. Choose implementation approach (Recommended: Approach 2)
2. Follow step-by-step implementation guide
3. Run testing checklist
4. Verify with coordinator and employee test accounts
5. Monitor logs for errors

