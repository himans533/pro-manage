# Task Assignment Implementation Guide

## Overview
When a Project Coordinator creates a task under a milestone, the "Assign Employee" dropdown shows ONLY employees from the `project_team_members` table for that project.

## What Gets Changed

### 1. Backend Changes (app.py)
Add one new endpoint to handle filtering employees by project team members.

### 2. Frontend Changes (employee-dashboard.html)
- Add JavaScript event listener
- Update dropdown population function
- Dynamic filtering based on selected project

### 3. HTML Changes
Minimal - Just add one `onchange` attribute to existing dropdown

---

## Implementation Steps

### Step 1: Add Backend Endpoint (15 minutes)

**File:** `AdminLoginPanel/app.py`

**Location:** Add around line 2900 (before `create_employee_task()` function)

**Code to Add:**
```python
@app.route("/api/projects/<int:project_id>/eligible-assignees", methods=["GET"])
@login_required
def get_eligible_task_assignees(project_id):
    """
    Get eligible team members for task assignment in a project.
    
    For Project Coordinators:
    - Returns ONLY users from project_team_members table for this project
    
    For Regular Employees:
    - Returns all employees (backward compatibility)
    """
    conn = None
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "User ID not found"}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current user's role
        cursor.execute('SELECT user_type FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_type = user['user_type']
        
        # Verify project exists
        cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Project not found"}), 404
        
        # IMPORTANT: Only Project Coordinators get filtered list
        if user_type == 'Project Coordinator':
            # Get only team members assigned to this project
            cursor.execute('''
                SELECT DISTINCT u.id, u.username, u.email
                FROM users u
                INNER JOIN project_team_members ptm ON u.id = ptm.user_id
                WHERE ptm.project_id = ?
                ORDER BY u.username
            ''', (project_id,))
        else:
            # Regular employees see all employees (original behavior)
            cursor.execute('''
                SELECT id, username, email
                FROM users
                WHERE user_type IN ('Employee', 'Project Coordinator')
                ORDER BY username
            ''')
        
        assignees = cursor.fetchall()
        
        # Convert Row objects to dictionaries
        result = [
            {
                'id': row['id'],
                'username': row['username'],
                'email': row['email']
            }
            for row in assignees
        ]
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching eligible assignees: {str(e)}")
        return jsonify({"error": "Failed to fetch eligible assignees"}), 500
    finally:
        if conn:
            conn.close()
```

---

### Step 2: Add Backend Validation (5 minutes)

**File:** `AdminLoginPanel/app.py`

**Location:** Inside `create_employee_task()` function, after line 3006 (after assigned user verification)

**Code to Add:**
```python
            # NEW: If coordinator, verify assigned employee is in project_team_members
            if assigned_to_id:
                cursor.execute('SELECT user_type FROM users WHERE id = ?', (user_id,))
                user_record = cursor.fetchone()
                
                if user_record and user_record['user_type'] == 'Project Coordinator':
                    # Coordinator can only assign from project_team_members
                    cursor.execute('''
                        SELECT 1 FROM project_team_members 
                        WHERE project_id = ? AND user_id = ?
                    ''', (project_id, assigned_to_id))
                    
                    if not cursor.fetchone():
                        return jsonify({
                            "error": "This employee is not assigned to this project. "
                                   "Please add them to the project team first."
                        }), 403
```

---

### Step 3: Update HTML (2 minutes)

**File:** `AdminLoginPanel/templates/employee-dashboard.html`

**Location:** Line 2684 (Task Project select)

**Change From:**
```html
<select id="taskProject" required>
  <option value="">Select a project</option>
</select>
```

**Change To:**
```html
<select id="taskProject" required onchange="handleTaskProjectChange(this.value)">
  <option value="">Select a project</option>
</select>
```

---

### Step 4: Add Frontend JavaScript (10 minutes)

**File:** `AdminLoginPanel/templates/employee-dashboard.html`

**Location:** In the main `<script>` section (around line 2700 onwards)

**Add These Functions:**

```javascript
async function populateTaskAssigneeDropdown(projectId) {
    /**
     * Load eligible assignees for the selected project.
     * If coordinator: shows only project_team_members
     * If employee: shows all employees
     */
    
    const assigneeSelect = document.getElementById("taskAssignee");
    if (!assigneeSelect) return;
    
    try {
        assigneeSelect.innerHTML = '<option value="">Loading...</option>';
        
        const token = localStorage.getItem('employee_token');
        const response = await fetch(
            `${API_BASE}/projects/${projectId}/eligible-assignees`,
            {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        if (!response.ok) {
            console.error("[v0] Failed to fetch eligible assignees:", response.status);
            assigneeSelect.innerHTML = '<option value="">Error loading employees</option>';
            return;
        }
        
        const assignees = await response.json();
        
        assigneeSelect.innerHTML = '<option value="">Unassigned</option>' +
            assignees.map(emp => 
                `<option value="${emp.id}">${emp.username}</option>`
            ).join('');
        
        console.log("[v0] Assignee dropdown populated with", assignees.length, "team members");
        
    } catch (error) {
        console.error("[v0] Error populating assignee dropdown:", error);
        assigneeSelect.innerHTML = '<option value="">Error loading employees</option>';
    }
}

function handleTaskProjectChange(projectId) {
    if (projectId) {
        populateTaskAssigneeDropdown(parseInt(projectId));
    }
}
```

---

## Database Schema Reference

The `project_team_members` table structure (created in previous deliverable):
```sql
CREATE TABLE project_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)
);
```

---

## How It Works

### Flow Diagram

```
User selects Project in Task Form
    ↓
onchange="handleTaskProjectChange(projectId)" triggers
    ↓
populateTaskAssigneeDropdown(projectId) called
    ↓
Fetch /api/projects/{projectId}/eligible-assignees
    ↓
Backend checks user role:
    ├─ Project Coordinator? → Query project_team_members table
    └─ Regular Employee? → Return all employees
    ↓
Dropdown populated with filtered list
    ↓
User selects employee
    ↓
Task created with assigned_to_id
    ↓
Backend validates assignment (coordinator check)
    ↓
Task saved or rejected if invalid assignment
```

---

## Testing Checklist

### Test Case 1: Coordinator Creates Task
1. Login as Project Coordinator
2. Open project where you're assigned members
3. Click "Create Task"
4. Select the project
5. Verify: "Assign To" dropdown shows ONLY team members from project_team_members
6. Select a team member and create task
7. Verify: Task created successfully

### Test Case 2: Coordinator Tries Invalid Assignment
1. Login as Coordinator
2. Create task payload with employee NOT in project_team_members
3. Verify: Backend rejects with error message

### Test Case 3: Employee Creates Task (Backward Compatibility)
1. Login as regular Employee
2. Create task
3. Verify: "Assign To" shows all employees (original behavior)
4. Create task successfully

### Test Case 4: Multiple Projects
1. Login as Coordinator
2. Create tasks in different projects
3. Verify: Different team members shown for each project

---

## Troubleshooting

### Issue: Dropdown shows "Error loading employees"
**Solution:**
- Check browser console for API errors
- Verify endpoint is properly added to app.py
- Ensure project_id is being passed correctly

### Issue: Coordinator sees all employees instead of filtered
**Solution:**
- Check user_type in database for the coordinator
- Verify project_team_members table has correct entries
- Check database query for INNER JOIN issues

### Issue: Task creation fails with "employee not in project team"
**Solution:**
- Ensure employee was added to project_team_members
- Check project_id matches in dropdown and backend
- Verify database constraints are correct

---

## Performance Notes

- Queries use INNER JOIN which is efficient
- Index on project_team_members(project_id) ensures fast lookups
- Dropdown loads asynchronously (doesn't block form)
- Backward compatible (regular employees unaffected)

---

## Security Notes

- Frontend validation: user_type checked on backend
- Backend validation: coordinator can only assign team members
- Role-based access: Coordinators get filtered list
- CSRF protection: Uses existing session/token auth

---

## Files Created

1. `/scripts/task_assignment_backend_solution.py` - Backend code
2. `/scripts/task_assignment_frontend_changes.js` - Frontend code  
3. `/scripts/task_assignment_html_changes.html` - HTML changes
4. `/docs/TASK_ASSIGNMENT_IMPLEMENTATION.md` - This guide
5. `/TASK_ASSIGNMENT_QUICK_START.md` - Quick reference
6. `/TASK_ASSIGNMENT_SUMMARY.md` - Executive summary

---

## Next Steps

1. Add backend endpoint to app.py
2. Add validation logic to create_employee_task()
3. Update employee-dashboard.html with onchange attribute
4. Add JavaScript functions to script section
5. Test all scenarios
6. Deploy to production

---

**Estimated Implementation Time:** 30 minutes
**Files Modified:** 2 (app.py, employee-dashboard.html)
**Lines Added:** ~80 backend + ~30 frontend + ~1 HTML
