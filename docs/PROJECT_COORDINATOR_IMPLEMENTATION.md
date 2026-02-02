# Project Coordinator Assignment Implementation Guide

## Overview
This guide walks through implementing the Project Coordinator assignment feature for the Project Management System. Super Admins can now assign a Project Coordinator when creating projects, and that relationship is stored in the database.

## Prerequisites
- Database with users and usertypes tables already populated
- Project Coordinator usertype already exists in the database
- Access to admin-dashboard.html and app.py

## Step-by-Step Implementation

### Step 1: Database Migration

**File:** `/scripts/add_project_coordinator.sql`

Execute the migration to add the new column:

```bash
sqlite3 AdminLoginPanel/project_management.db < scripts/add_project_coordinator.sql
```

**What this does:**
- Adds `project_coordinator_id` column to projects table (nullable INTEGER)
- Creates a foreign key constraint to ensure referential integrity
- Creates an index for performance optimization

**Verify the migration:**
```sql
PRAGMA table_info(projects);
-- Should show: project_coordinator_id | INTEGER | 0 | | 0
```

---

### Step 2: Add HTML Dropdown to Project Creation Form

**File:** `AdminLoginPanel/templates/admin-dashboard.html`

**Location:** Insert after line 2662 (after the Reporting Time form-group)

**Code to insert:**
```html
<div class="form-group">
    <label for="projCoordinator">
        <i class="fas fa-user-tie"></i> Assign Project Coordinator
        <span class="text-muted" style="font-size: 0.85em; font-weight: normal;">(Optional)</span>
    </label>
    <select id="projCoordinator" class="form-control" style="padding: 10px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-secondary);">
        <option value="">-- Select a Project Coordinator --</option>
        <!-- Populated dynamically by JavaScript -->
    </select>
    <small class="form-text text-muted" style="margin-top: 5px; display: block; font-size: 0.8em;">
        <i class="fas fa-info-circle"></i> Select a user with Project Coordinator role to oversee this project
    </small>
</div>
```

**Why this works:**
- Form-group styling is already defined in the CSS
- The dropdown ID `projCoordinator` will be referenced by JavaScript
- Optional label helps users understand they can skip this

---

### Step 3: Add JavaScript Functions (in admin-dashboard.html)

**Location:** Add these functions to the JavaScript section at the bottom of admin-dashboard.html

**Function 1: Load Project Coordinators on modal open**

```javascript
// Call this when openHierarchicalProjectModal() is invoked
async function loadProjectCoordinators() {
    try {
        const response = await fetch('/api/project-coordinators');
        const coordinators = await response.json();
        
        const coordinatorSelect = document.getElementById('projCoordinator');
        coordinatorSelect.innerHTML = '<option value="">-- Select a Project Coordinator --</option>';
        
        coordinators.forEach(coordinator => {
            const option = document.createElement('option');
            option.value = coordinator.id;
            option.textContent = `${coordinator.username} (${coordinator.department})`;
            coordinatorSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading coordinators:', error);
    }
}
```

**Function 2: Modify openHierarchicalProjectModal()**

Find the existing `openHierarchicalProjectModal()` function and add this line:

```javascript
function openHierarchicalProjectModal() {
    // ... existing code ...
    
    // Add this line to load coordinators
    loadProjectCoordinators();
    
    // ... rest of existing code ...
}
```

**Function 3: Store coordinator in draft object**

Modify `saveDraftProject()` to capture the coordinator selection:

```javascript
function saveDraftProject(event) {
    event.preventDefault();
    
    // ... existing code ...
    
    // Add coordinator to draft object
    projectDraft.project_coordinator_id = document.getElementById('projCoordinator').value || null;
    
    // ... rest of existing code ...
}
```

**Function 4: Include coordinator in submission**

Modify `finalizeProject()` to send coordinator in the API request:

```javascript
async function finalizeProject() {
    try {
        const payload = {
            title: projectDraft.title,
            description: projectDraft.description,
            deadline: projectDraft.deadline,
            reporting_time: projectDraft.reporting_time,
            project_coordinator_id: projectDraft.project_coordinator_id, // Add this line
            team_members: projectDraft.team_members,
            milestones: projectDraft.milestones
        };
        
        // ... existing API call logic ...
    } catch (error) {
        // ... error handling ...
    }
}
```

---

### Step 4: Add Backend Endpoint (app.py)

**File:** `AdminLoginPanel/app.py`

**Location:** Add BEFORE the `create_employee_project()` function (around line 2773)

```python
@app.route("/api/project-coordinators", methods=["GET"])
@admin_required
def get_project_coordinators():
    """
    Get all users with 'Project Coordinator' role for dropdown assignment.
    Returns only users who have been granted the Project Coordinator usertype.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all users with 'Project Coordinator' usertype
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.department
            FROM users u
            INNER JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE ut.user_role = 'Project Coordinator'
            ORDER BY u.username ASC
        ''')
        
        coordinators = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': row['id'],
            'username': row['username'],
            'email': row['email'],
            'department': row['department'] or 'Not Specified'
        } for row in coordinators]), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

---

### Step 5: Modify create_employee_project() (app.py)

**Location:** Lines 2804-2808 in app.py

**Original code:**
```python
cursor.execute(
    '''
    INSERT INTO projects (title, description, deadline, reporting_time, created_by_id)
    VALUES (?,?,?,?,?)
''', (title, description, deadline or None, reporting_time, user_id))
```

**Replace with:**
```python
# Get project_coordinator_id from request
project_coordinator_id = data.get("project_coordinator_id")

# Validate coordinator if provided
if project_coordinator_id:
    try:
        project_coordinator_id = int(project_coordinator_id)
        # Verify coordinator exists and has correct role
        cursor.execute('''
            SELECT u.id FROM users u
            INNER JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ? AND ut.user_role = 'Project Coordinator'
        ''', (project_coordinator_id,))
        if not cursor.fetchone():
            project_coordinator_id = None  # Invalid coordinator, ignore
    except (ValueError, TypeError):
        project_coordinator_id = None

cursor.execute(
    '''
    INSERT INTO projects 
    (title, description, deadline, reporting_time, created_by_id, project_coordinator_id)
    VALUES (?,?,?,?,?,?)
''', (title, description, deadline or None, reporting_time, user_id, project_coordinator_id))
```

---

### Step 6: Update get_admin_projects() Query (app.py)

**Location:** Line 3776-3787 in app.py

**Original query:**
```python
cursor.execute('''
SELECT p.id, p.title, p.description, p.status, p.progress,
p.deadline, p.created_by_id, u.username as creator_name,
p.created_at, COUNT(DISTINCT pa.user_id) as team_count,
COUNT(DISTINCT t.id) as task_count
FROM projects p
LEFT JOIN users u ON p.created_by_id = u.id
LEFT JOIN project_assignments pa ON p.id = pa.project_id
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, u.username
ORDER BY p.created_at DESC
''')
```

**Updated query:**
```python
cursor.execute('''
SELECT p.id, p.title, p.description, p.status, p.progress,
p.deadline, p.created_by_id, u.username as creator_name,
p.project_coordinator_id, uc.username as coordinator_name,
p.created_at, COUNT(DISTINCT pa.user_id) as team_count,
COUNT(DISTINCT t.id) as task_count
FROM projects p
LEFT JOIN users u ON p.created_by_id = u.id
LEFT JOIN users uc ON p.project_coordinator_id = uc.id
LEFT JOIN project_assignments pa ON p.id = pa.project_id
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, u.username, uc.username
ORDER BY p.created_at DESC
''')
```

---

## Verification Checklist

After implementation, verify the following:

- [ ] Database migration executed successfully
- [ ] New column appears in projects table: `project_coordinator_id`
- [ ] HTML dropdown appears in project creation form
- [ ] Dropdown is populated when modal opens
- [ ] New endpoint `/api/project-coordinators` returns coordinators
- [ ] Project creation works with and without coordinator selection
- [ ] Coordinator information is stored in database
- [ ] Projects list shows coordinator names in admin dashboard

---

## Testing the Feature

### Test 1: Create Project Without Coordinator
1. Open Create Project modal
2. Fill in basic details
3. Leave Project Coordinator blank
4. Submit
5. Verify: `project_coordinator_id` is NULL in database

### Test 2: Create Project With Coordinator
1. Open Create Project modal
2. Fill in basic details
3. Select a Project Coordinator from dropdown
4. Submit
5. Verify: `project_coordinator_id` is set to coordinator's ID in database

### Test 3: Query Projects by Coordinator
```sql
-- Get all projects for a specific coordinator
SELECT * FROM projects WHERE project_coordinator_id = 2;

-- Get projects without a coordinator
SELECT * FROM projects WHERE project_coordinator_id IS NULL;

-- Count projects per coordinator
SELECT uc.username, COUNT(p.id) as project_count
FROM projects p
LEFT JOIN users uc ON p.project_coordinator_id = uc.id
GROUP BY p.project_coordinator_id;
```

---

## Optional Enhancements

### Enhancement 1: Project Coordinator Dashboard
Add a new endpoint for coordinators to view their assigned projects:

```python
@app.route("/api/coordinator/projects", methods=["GET"])
@login_required
def get_coordinator_projects():
    user_id = get_current_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.* FROM projects p
        WHERE p.project_coordinator_id = ?
        ORDER BY p.created_at DESC
    ''', (user_id,))
    
    projects = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in projects]), 200
```

### Enhancement 2: Update Coordinator Assignment
Add endpoint to reassign coordinators:

```python
@app.route("/api/admin/projects/<int:project_id>/coordinator", methods=["PUT"])
@admin_required
def update_project_coordinator(project_id):
    data = request.get_json() or {}
    new_coordinator_id = data.get("project_coordinator_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Validate and update
    cursor.execute(
        'UPDATE projects SET project_coordinator_id = ? WHERE id = ?',
        (new_coordinator_id or None, project_id)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Coordinator updated"}), 200
```

### Enhancement 3: Display Coordinator in Project Details
Update the project detail view to show the assigned coordinator prominently.

---

## Troubleshooting

### Issue: Dropdown shows no coordinators
- **Cause:** No users have "Project Coordinator" usertype
- **Solution:** Create Project Coordinator users first, ensure usertype is correct

### Issue: Coordinator not saved to database
- **Cause:** Frontend not sending coordinator_id or validation failing
- **Solution:** Check browser console for errors, verify API endpoint is working

### Issue: SQL Error "table projects has no column named project_coordinator_id"
- **Cause:** Migration not executed
- **Solution:** Run the SQL migration script

---

## Files Modified

1. **AdminLoginPanel/templates/admin-dashboard.html**
   - Added dropdown HTML form-group
   - Added JavaScript functions to load coordinators
   - Modified saveDraftProject() and finalizeProject()

2. **AdminLoginPanel/app.py**
   - Added `/api/project-coordinators` endpoint
   - Modified `create_employee_project()` to handle coordinator_id
   - Updated `get_admin_projects()` query with joins

3. **AdminLoginPanel/project_management.db** (via SQL migration)
   - Added `project_coordinator_id` column
   - Added foreign key constraint
   - Added index for performance

---

## Summary

The Project Coordinator assignment feature is now fully integrated. Super Admins can:
- Assign a Project Coordinator when creating projects
- Leave it blank if not needed
- View assigned coordinators in project lists
- Later reassign coordinators if needed (with enhancement)

The feature is backward compatible and doesn't affect existing projects or functionality.
