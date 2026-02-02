# Employee Dashboard Coordinator Filter - Quick Reference

## What's Being Changed?

**Backend filtering only** - No UI changes.

When a Project Coordinator logs into the Employee Dashboard, they now see ONLY projects where `project_coordinator_id = their user_id`.

Regular employees continue to see projects where they are creator or assigned.

---

## Implementation Time: ~40 minutes

### 1. Choose Approach (2 min)
**Recommended: Approach 2 (Helper Function)** - Clean, maintainable, testable

---

### 2. Add Helper Function (5 min)
**Location**: `AdminLoginPanel/app.py` around line 550

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
        return 'project coordinator' in user_role_row['user_role'].lower() if user_role_row else False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
```

---

### 3. Modify get_employee_projects() (10 min)
**Location**: `AdminLoginPanel/app.py` line ~2748

**FIND THIS**:
```python
@app.route("/api/employee/projects", methods=["GET"])
@login_required
def get_employee_projects():
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()

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

        projects = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in projects]), 200
```

**REPLACE WITH THIS**:
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
            # Project Coordinators see only projects assigned to them
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
                       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
                FROM projects p 
                LEFT JOIN users u ON p.created_by_id = u.id
                WHERE p.project_coordinator_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))
        else:
            # Regular employees see their created/assigned projects
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

        projects = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in projects]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

### 4. Modify get_employee_realtime_projects() (10 min)
**Location**: `AdminLoginPanel/app.py` line ~4762

**FIND THIS LINE**:
```python
WHERE (p.created_by_id = ? OR p.id IN (
    SELECT project_id FROM project_assignments WHERE user_id = ?
)) AND p.status != 'Completed'
```

**ADD THIS BEFORE THE QUERY** (after line 4767):
```python
is_coordinator = is_user_project_coordinator(user_id)
```

**REPLACE THE WHERE CLAUSE WITH**:
```python
if is_coordinator:
    WHERE p.project_coordinator_id = ? AND p.status != 'Completed'
    # params: (user_id,)
else:
    WHERE (p.created_by_id = ? OR p.id IN (
        SELECT project_id FROM project_assignments WHERE user_id = ?
    )) AND p.status != 'Completed'
    # params: (user_id, user_id)
```

---

## Test It

### Login as Project Coordinator
```
Expected: See ONLY projects where project_coordinator_id = their_id
```

### Login as Regular Employee
```
Expected: See projects where they are creator or assigned
```

### Check Realtime Endpoint
```
GET /api/employee/projects/realtime
Expected: Same filtering as standard endpoint
```

---

## Key Points

✓ No UI changes - Backend only  
✓ Backward compatible - Existing employees unaffected  
✓ Uses existing column - `project_coordinator_id` (already added)  
✓ Proper role checking - Checks user_type for "Project Coordinator"  
✓ Index-optimized - Uses existing index on project_coordinator_id  

---

## Files

- **Implementation Code**: `/scripts/employee_dashboard_filter.py`
- **Full Guide**: `/docs/EMPLOYEE_DASHBOARD_COORDINATOR_FILTER.md`
- **App File**: `AdminLoginPanel/app.py`

---

## Quick Rollback

If needed, revert to original queries (remove coordinator check and go back to original WHERE clause).

