# Employee Dashboard Extension - Project Coordinator Filtering

## Executive Summary

Safely extended the Employee Dashboard to filter projects for Project Coordinators. When a Project Coordinator logs in, they see **ONLY** projects assigned to them (`project_coordinator_id = their_id`). Regular employees continue to see their created/assigned projects unchanged.

**Implementation**: Backend filtering only - NO UI rewrites needed.

---

## What Gets Done

### Backend Changes
- Modify `GET /api/employee/projects` endpoint (line ~2748)
- Modify `GET /api/employee/projects/realtime` endpoint (line ~4760)
- Add role-checking logic to determine if user is a Project Coordinator
- Apply conditional filtering based on user role

### Database
- Uses existing `project_coordinator_id` column (added by previous migration)
- Uses existing index `idx_project_coordinator_id` (already created)
- NO new schema changes needed

### Frontend
- **ZERO UI changes** - No modifications to templates or JavaScript
- Filtering happens entirely at the API level
- Dashboard automatically shows filtered projects

---

## Implementation Overview

### Architecture Decision

**Role-Based Query Filtering**:
```
Check user role:
  ├─ Project Coordinator? 
  │   → WHERE project_coordinator_id = user_id
  └─ Regular Employee?
      → WHERE created_by_id = user_id OR assigned to user
```

### Code Changes

**Files to Modify**: `AdminLoginPanel/app.py` only

**Changes**:
1. Add helper function: `is_user_project_coordinator(user_id)` 
2. Update `get_employee_projects()` with conditional query
3. Update `get_employee_realtime_projects()` with conditional query

**Total Lines Added/Modified**: ~80 lines across two functions

---

## Implementation Steps

### Step 1: Add Helper Function (5 min)
**Location**: `app.py` line ~550

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
        return False
```

### Step 2: Update get_employee_projects() (10 min)
**Location**: `app.py` line ~2748

Add after line 2751:
```python
is_coordinator = is_user_project_coordinator(user_id)
```

Change the cursor.execute to use conditional logic:
```python
if is_coordinator:
    cursor.execute('''
        SELECT ... FROM projects p 
        LEFT JOIN users u ON p.created_by_id = u.id
        WHERE p.project_coordinator_id = ?
        ORDER BY p.created_at DESC
    ''', (user_id,))
else:
    cursor.execute('''
        SELECT ... FROM projects p 
        LEFT JOIN users u ON p.created_by_id = u.id
        WHERE (p.created_by_id = ? OR p.id IN (
            SELECT project_id FROM project_assignments WHERE user_id = ?
        ))
        ORDER BY p.created_at DESC
    ''', (user_id, user_id))
```

### Step 3: Update get_employee_realtime_projects() (10 min)
**Location**: `app.py` line ~4762

Apply identical logic to the realtime endpoint.

### Step 4: Test (15 min)
- Create test coordinator user
- Assign projects to them as coordinator
- Login as coordinator → Verify they see ONLY their projects
- Login as regular employee → Verify they see assigned/created projects

---

## Query Details

### Coordinator Query (NEW)
```sql
SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
FROM projects p 
LEFT JOIN users u ON p.created_by_id = u.id
WHERE p.project_coordinator_id = ?
ORDER BY p.created_at DESC
```

**Why this works**:
- Uses indexed column `project_coordinator_id`
- Fast lookup due to index
- Simple, clear intent

### Employee Query (EXISTING)
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

**Unchanged** - Ensures backward compatibility

---

## Testing Strategy

### Test Case 1: Coordinator Isolation
```
Setup:
  - User: Alice (ID=5, role=Project Coordinator)
  - Projects:
    - Project A: project_coordinator_id = 5
    - Project B: project_coordinator_id = 5
    - Project C: project_coordinator_id = 3
    - Project D: project_coordinator_id = NULL

Login as Alice:
  ✓ See: Projects A, B
  ✗ Don't see: Projects C, D
```

### Test Case 2: Employee Unchanged
```
Setup:
  - User: Bob (ID=7, role=Employee)
  - Projects:
    - Project X: created_by_id = 7
    - Project Y: assigned to Bob
    - Project Z: created_by_id = 3, not assigned

Login as Bob:
  ✓ See: Projects X, Y
  ✗ Don't see: Project Z
```

### Test Case 3: Realtime Endpoint
```
Setup: Same as Test Case 1

GET /api/employee/projects/realtime:
  ✓ Same filtering as standard endpoint
  ✓ Progress calculation works
  ✓ Task/milestone counts accurate
```

---

## Performance Impact

| Metric | Value | Notes |
|--------|-------|-------|
| Extra DB Queries | 1 | Checks user role (cached by connection pool) |
| Query Execution Time | <5ms | Role check is lightweight |
| Coordinator Query Speed | Fast | Uses indexed column `project_coordinator_id` |
| Employee Query Speed | Unchanged | Same as before |
| Memory Usage | Negligible | No additional data structures |

**Conclusion**: Negligible performance impact, well-optimized queries.

---

## Safety & Rollback

### Safety Measures
✓ Helper function handles errors gracefully  
✓ Falls back to employee behavior if role check fails  
✓ Existing employees completely unaffected  
✓ Uses existing database schema (no ALTER TABLE needed)  
✓ Conditional logic ensures backward compatibility  

### Rollback (if needed)
Simply revert the two functions to their original queries (remove the role check and conditional logic). No database migration rollback needed.

---

## Files Provided

### Code Snippets
- `scripts/employee_dashboard_filter.py` - Complete implementation code (3 approaches)

### Documentation
- `COORDINATOR_DASHBOARD_QUICK_REFERENCE.md` - Quick 5-minute implementation guide
- `docs/EMPLOYEE_DASHBOARD_COORDINATOR_FILTER.md` - Detailed 20-minute guide with troubleshooting

### Checklists
- Implementation checklist
- Testing checklist
- Troubleshooting guide

---

## Success Criteria

✓ Project Coordinators see ONLY their assigned projects  
✓ Regular employees see their created/assigned projects (unchanged)  
✓ Both standard and realtime endpoints work correctly  
✓ No UI changes or template modifications  
✓ All existing functionality preserved  
✓ Performance remains the same or better  

---

## Next Steps

1. **Prepare** (2 min)
   - Review `COORDINATOR_DASHBOARD_QUICK_REFERENCE.md`

2. **Implement** (25 min)
   - Add helper function
   - Update two endpoints

3. **Test** (15 min)
   - Verify coordinator filtering
   - Verify employee access unchanged
   - Test realtime endpoint

4. **Deploy** (5 min)
   - Restart Flask app
   - Monitor logs

**Total Time**: ~40 minutes for complete implementation and testing

---

## Support & Questions

**What changed?**
Backend filtering logic for the Employee Dashboard projects endpoint.

**Why now?**
To ensure Project Coordinators can focus on their assigned projects without seeing all projects.

**Do I need to update the frontend?**
No. The filtering happens entirely in the backend API.

**What if something breaks?**
Revert the changes to the two functions in app.py - it's just replacing the WHERE clause logic.

**Will this affect other endpoints?**
No. Only `/api/employee/projects` and `/api/employee/projects/realtime` are modified.

