# Add Team Members Feature - Quick Start (5 Minutes)

## What This Does
Project Coordinators can select 2-3 employees from their team to assign to projects.

## 3-Step Implementation

### Step 1: Database (2 min)
```bash
sqlite3 AdminLoginPanel/project_management.db < scripts/create_project_team_members_table.sql
```

Creates `project_team_members` table with indexes.

### Step 2: Backend (2 min)
Copy all code from `/scripts/backend_team_members_logic.py` into `AdminLoginPanel/app.py` 

Add it near line 4552 (after other project routes)

### Step 3: Frontend (1 min)
Add this code to `AdminLoginPanel/templates/project-detail.html` before `</body>`:

```html
<!-- From /scripts/team_members_modal_insertion.html -->
<!-- Copy everything and paste before </body> -->
```

**Done!** Test it:
- Login as coordinator
- Open project details
- Click "Add Team Members to Project"

---

## What Gets Created

| Component | Where | What |
|-----------|-------|------|
| Table | Database | `project_team_members` |
| Endpoints | Backend | 4 API routes |
| Modal | Frontend | Dialog to select members |

---

## Key Requirements

- ✓ Coordinator must be project owner (`project_coordinator_id`)
- ✓ Team members must have `parent_user_id = coordinator_id`
- ✓ Max 3 members per project
- ✓ Bootstrap 5 on page

---

## Testing

```
1. Login as coordinator
2. Go to project
3. Click "Add Team Members"
4. Select 2-3 employees
5. Click "Add Selected Members"
6. Page reloads with new team members
```

---

## Files to Copy

1. `/scripts/create_project_team_members_table.sql` → Run SQL
2. `/scripts/backend_team_members_logic.py` → Copy to app.py
3. `/scripts/team_members_modal_insertion.html` → Add to project-detail.html

---

## API Endpoints

```
GET  /api/coordinator/eligible-team-members/<project_id>
POST /api/coordinator/add-team-members/<project_id>
GET  /api/coordinator/project-team-members/<project_id>  (optional)
DEL  /api/coordinator/remove-team-member/<project_id>/<user_id>  (optional)
```

---

**Time to implement: ~5-10 minutes**
**See `docs/ADD_TEAM_MEMBERS_IMPLEMENTATION.md` for detailed guide**
