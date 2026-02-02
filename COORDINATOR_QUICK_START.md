# Project Coordinator Assignment - Quick Start

## 3-Step Implementation

### 1️⃣ Database Migration
```bash
cd AdminLoginPanel
sqlite3 project_management.db < ../scripts/add_project_coordinator.sql
```

### 2️⃣ Add HTML Dropdown
**File:** `AdminLoginPanel/templates/admin-dashboard.html`  
**Location:** After line 2662 (after `projReportingTime` form-group)

**Insert:**
```html
<div class="form-group">
    <label for="projCoordinator">
        <i class="fas fa-user-tie"></i> Assign Project Coordinator
        <span class="text-muted" style="font-size: 0.85em; font-weight: normal;">(Optional)</span>
    </label>
    <select id="projCoordinator" class="form-control" style="padding: 10px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-secondary);">
        <option value="">-- Select a Project Coordinator --</option>
    </select>
    <small class="form-text text-muted" style="margin-top: 5px; display: block; font-size: 0.8em;">
        <i class="fas fa-info-circle"></i> Select a user with Project Coordinator role to oversee this project
    </small>
</div>
```

### 3️⃣ Backend Code
**File:** `AdminLoginPanel/app.py`

**A) Add endpoint (before line 2773):**
```python
@app.route("/api/project-coordinators", methods=["GET"])
@admin_required
def get_project_coordinators():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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

**B) Modify create_employee_project() (lines 2804-2808):**

FROM:
```python
cursor.execute(
    '''
    INSERT INTO projects (title, description, deadline, reporting_time, created_by_id)
    VALUES (?,?,?,?,?)
''', (title, description, deadline or None, reporting_time, user_id))
```

TO:
```python
project_coordinator_id = data.get("project_coordinator_id")

if project_coordinator_id:
    try:
        project_coordinator_id = int(project_coordinator_id)
        cursor.execute('''
            SELECT u.id FROM users u
            INNER JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ? AND ut.user_role = 'Project Coordinator'
        ''', (project_coordinator_id,))
        if not cursor.fetchone():
            project_coordinator_id = None
    except (ValueError, TypeError):
        project_coordinator_id = None

cursor.execute(
    '''
    INSERT INTO projects 
    (title, description, deadline, reporting_time, created_by_id, project_coordinator_id)
    VALUES (?,?,?,?,?,?)
''', (title, description, deadline or None, reporting_time, user_id, project_coordinator_id))
```

**C) Add JavaScript functions to admin-dashboard.html** (at the end, before `</script>`):

```javascript
// Load coordinators when modal opens
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

// Call this in openHierarchicalProjectModal()
// Add: loadProjectCoordinators();

// Add to projectDraft in saveDraftProject()
// Add: projectDraft.project_coordinator_id = document.getElementById('projCoordinator').value || null;

// Add to payload in finalizeProject()
// Add: project_coordinator_id: projectDraft.project_coordinator_id,
```

---

## Verify Installation

```sql
-- Check if column exists
PRAGMA table_info(projects);

-- Test: Create project with coordinator
INSERT INTO projects (title, description, created_by_id, project_coordinator_id)
VALUES ('Test Project', 'Test', 1, 2);

-- Test: Query projects by coordinator
SELECT * FROM projects WHERE project_coordinator_id = 2;
```

---

## Usage

1. **Super Admin creates project:**
   - Opens "Create New Project" modal
   - Fills in project details
   - Selects a Project Coordinator from dropdown (optional)
   - Submits form

2. **Data stored:**
   - `project_coordinator_id` is saved in projects table
   - Can be NULL if no coordinator selected
   - Can be updated later if needed

3. **Query projects by coordinator:**
   ```sql
   SELECT * FROM projects WHERE project_coordinator_id = <coordinator_id>;
   ```

---

## Files Changed

| File | Changes |
|------|---------|
| `project_management.db` | Added `project_coordinator_id` column via SQL migration |
| `admin-dashboard.html` | Added dropdown form-group + JS functions |
| `app.py` | Added endpoint + modified create_project + updated query |

---

## Need More Info?

See `/docs/PROJECT_COORDINATOR_IMPLEMENTATION.md` for detailed step-by-step guide with testing procedures.
