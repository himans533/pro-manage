# Add Team Members to Project - Complete Implementation Guide

## Overview

This feature allows Project Coordinators to add 2-3 team members (employees under their supervision) to their assigned projects. The implementation includes:

- New database table: `project_team_members`
- Backend API endpoints for managing team assignments
- Modal UI for selecting team members
- Full validation and error handling

---

## Part 1: Database Setup

### 1.1 Create New Table

Run the following SQL to create the `project_team_members` table:

```sql
CREATE TABLE IF NOT EXISTS project_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_project_team_members_project_id 
ON project_team_members(project_id);

CREATE INDEX IF NOT EXISTS idx_project_team_members_user_id 
ON project_team_members(user_id);
```

**File:** `/scripts/create_project_team_members_table.sql`

**Steps:**
```bash
# Option 1: Using sqlite3 CLI
sqlite3 AdminLoginPanel/project_management.db < scripts/create_project_team_members_table.sql

# Option 2: Run from Python
import sqlite3
conn = sqlite3.connect('AdminLoginPanel/project_management.db')
cursor = conn.cursor()
with open('scripts/create_project_team_members_table.sql', 'r') as f:
    cursor.executescript(f.read())
conn.commit()
conn.close()
```

---

## Part 2: Backend Implementation

### 2.1 Add Backend Endpoints

Add these functions to `AdminLoginPanel/app.py`:

**File:** `/scripts/backend_team_members_logic.py`

The file contains 4 main endpoints:

1. **GET `/api/coordinator/eligible-team-members/<project_id>`**
   - Returns list of employees under the coordinator
   - Excludes already-assigned members
   - Called when modal opens

2. **POST `/api/coordinator/add-team-members/<project_id>`**
   - Adds selected employees to project
   - Validates max 3 members
   - Validates all employees belong to coordinator
   - Creates entries in `project_team_members` table

3. **GET `/api/coordinator/project-team-members/<project_id>`** (Optional)
   - Returns current team members of a project
   - Useful for displaying team info

4. **DELETE `/api/coordinator/remove-team-member/<project_id>/<user_id>`** (Optional)
   - Removes a team member from project

### 2.2 Implementation Steps

1. Open `AdminLoginPanel/app.py`
2. Find a suitable location (near other project routes, around line 4552)
3. Copy the 4 endpoint functions from `/scripts/backend_team_members_logic.py`
4. Paste them into the app.py file
5. Save the file

**Verification:**
```python
# Test that endpoints exist
# These should work after adding the code:
# - GET /api/coordinator/eligible-team-members/1
# - POST /api/coordinator/add-team-members/1
```

---

## Part 3: Frontend Implementation

### 3.1 Update Project Detail Template

**File:** `/AdminLoginPanel/templates/project-detail.html`

#### Step 1: Add Template Variables in Backend

In your `admin_project_detail()` function, add:

```python
# Check if logged-in user is the project coordinator
is_coordinator = (project['project_coordinator_id'] == session.get('user_id'))

return render_template(
    'project-detail.html',
    project=project,
    members=members,
    tasks=tasks,
    is_coordinator=is_coordinator  # Add this line
)
```

#### Step 2: Insert Modal HTML

Add the modal code from `/scripts/team_members_modal_insertion.html` to `project-detail.html`:

**Location:** Right before the closing `</body>` tag

**What to insert:**
- Button for opening modal
- Modal dialog HTML
- JavaScript for modal functionality

### 3.2 File Structure

```
project-detail.html
├── Head section (existing)
├── Body
│   ├── Header with back button (existing)
│   ├── Project summary card (existing)
│   ├── Add Team Members button (NEW - from modal file)
│   ├── Team Members table (existing)
│   ├── Tasks table (existing)
│   └── Bootstrap JS imports (existing)
│
└── Before </body> tag
    ├── Add Team Members Modal (NEW - from modal file)
    └── Modal JavaScript (NEW - from modal file)
```

---

## Part 4: User Hierarchy Requirements

This feature requires proper user hierarchy setup:

```
Super Admin (parent_user_id = NULL)
    ↓
Project Coordinator (parent_user_id = Super Admin id)
    ↓
Team Members/Employees (parent_user_id = Coordinator id)
```

**Verify hierarchy:**
```sql
-- Check coordinator's team
SELECT id, username, parent_user_id 
FROM users 
WHERE parent_user_id = <coordinator_id>;

-- Should return the team members
```

---

## Part 5: Testing & Verification

### 5.1 Pre-Implementation Checklist

- [ ] Coordinator user exists with `user_type_id = 'Project Coordinator'`
- [ ] Team member users exist with `parent_user_id = coordinator_id`
- [ ] Project exists with `project_coordinator_id = coordinator_id`
- [ ] Database migration script ready

### 5.2 Test Scenarios

**Test 1: Load Modal**
```
1. Login as Project Coordinator
2. Go to Project Details page
3. Click "Add Team Members to Project" button
4. Modal should open and show loading spinner
5. Employee list should populate after 1-2 seconds
```

**Test 2: Select Members**
```
1. Modal is open with employee list visible
2. Check 2-3 checkboxes
3. Counter should update to show selected count
4. Progress bar should fill
5. Submit button should become enabled
```

**Test 3: Exceed Limit**
```
1. Modal is open
2. Try to select 4th member
3. 4th checkbox should uncheck automatically
4. Error message should appear: "Maximum 3 team members..."
5. Counter should remain at 3
```

**Test 4: Add Members**
```
1. Select 2-3 members
2. Click "Add Selected Members"
3. Submit button should show loading spinner
4. After 1-2 seconds, success message appears
5. Page reloads
6. Team Members table should show new members
```

**Test 5: Verify Database**
```sql
-- After adding members, verify they're in the table
SELECT ptm.*, u.username 
FROM project_team_members ptm
JOIN users u ON ptm.user_id = u.id
WHERE ptm.project_id = <project_id>;

-- Should show the newly added members
```

### 5.3 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Button doesn't appear | `is_coordinator` not set in template | Check `admin_project_detail()` passes `is_coordinator=True` |
| Modal opens but shows "No employees" | Wrong `parent_user_id` in database | Verify team members have `parent_user_id = coordinator_id` |
| Can't select more than 1 member | JavaScript error | Check browser console for errors, verify Bootstrap 5 loaded |
| "Access Denied" error | User is not project coordinator | Verify `project.project_coordinator_id = session['user_id']` |
| Members not saving | Backend endpoint missing | Verify all 4 functions added to `app.py` |

---

## Part 6: Feature Details

### 6.1 Selection Rules

- **Minimum:** 1 team member (can add single member)
- **Maximum:** 3 team members per project
- **Eligibility:** Only employees with `parent_user_id = coordinator_id`
- **Duplicates:** Automatically prevented by UNIQUE constraint

### 6.2 Data Model

```
project_team_members table:
├── id (auto-increment)
├── project_id (FK to projects.id)
├── user_id (FK to users.id)
├── assigned_at (timestamp)
└── Unique(project_id, user_id)
```

### 6.3 Security

- ✓ Validates coordinator owns the project
- ✓ Validates all members belong to coordinator
- ✓ Prevents duplicate assignments
- ✓ Row-level validation
- ✓ Session-based authentication

---

## Part 7: Integration with Existing Features

### 7.1 Team Members Display

Update team members table to include `project_team_members`:

```sql
SELECT u.*, 
       COUNT(DISTINCT t.id) as tasks_count,
       COUNT(DISTINCT a.id) as activities_count
FROM project_team_members ptm
JOIN users u ON ptm.user_id = u.id
LEFT JOIN tasks t ON u.id = t.assigned_to_id
LEFT JOIN activities a ON u.id = a.user_id
WHERE ptm.project_id = ?
GROUP BY u.id
```

### 7.2 Query Team Members

```python
# Get team members for a project
def get_project_team_members(project_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.* FROM project_team_members ptm
        JOIN users u ON ptm.user_id = u.id
        WHERE ptm.project_id = ?
    ''', (project_id,))
    return cursor.fetchall()
```

---

## Part 8: Advanced Features (Optional)

### 8.1 Remove Team Member

Use the DELETE endpoint:
```javascript
fetch(`/api/coordinator/remove-team-member/${projectId}/${userId}`, {
  method: 'DELETE'
})
```

### 8.2 Edit Team Members

Create another modal to modify assignments:
```javascript
// Load current members
fetch(`/api/coordinator/project-team-members/${projectId}`)
  .then(r => r.json())
  .then(data => displayCurrentMembers(data.team_members))
```

### 8.3 Team Workload

Query task assignments across coordinator's projects:
```sql
SELECT u.username, COUNT(t.id) as tasks_assigned,
       COUNT(DISTINCT t.project_id) as projects
FROM project_team_members ptm
JOIN users u ON ptm.user_id = u.id
LEFT JOIN tasks t ON u.id = t.assigned_to_id
WHERE ptm.project_id IN (
  SELECT id FROM projects WHERE project_coordinator_id = ?
)
GROUP BY u.id
```

---

## Summary

| Component | Location | Lines |
|-----------|----------|-------|
| SQL Table | `/scripts/create_project_team_members_table.sql` | 24 |
| Backend | `/scripts/backend_team_members_logic.py` | 330 |
| Frontend | `/scripts/team_members_modal_insertion.html` | 180 |
| **Total** | - | **534** |

**Implementation Time:** 30-45 minutes
**Testing Time:** 15-20 minutes
**Total:** ~1 hour

---

## Files Reference

1. **Database:** `scripts/create_project_team_members_table.sql`
2. **Backend:** `scripts/backend_team_members_logic.py`
3. **Frontend:** `scripts/team_members_modal_insertion.html`
4. **This Guide:** `docs/ADD_TEAM_MEMBERS_IMPLEMENTATION.md`
