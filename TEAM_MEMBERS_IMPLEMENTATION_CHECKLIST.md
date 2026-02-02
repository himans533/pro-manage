# Add Team Members - Implementation Checklist

## Pre-Implementation

- [ ] User hierarchy is set up correctly
  - [ ] Coordinator exists with `parent_user_id = NULL` or Super Admin
  - [ ] Team members exist with `parent_user_id = coordinator_id`
  - [ ] Project exists with `project_coordinator_id = coordinator_id`

- [ ] Database access confirmed
  - [ ] Can connect to SQLite database
  - [ ] Foreign key constraints enabled
  - [ ] Can run ALTER TABLE commands

- [ ] Code access confirmed
  - [ ] Can edit `AdminLoginPanel/app.py`
  - [ ] Can edit `AdminLoginPanel/templates/project-detail.html`
  - [ ] Can run database scripts

---

## Implementation Steps

### Phase 1: Database (5 minutes)

- [ ] Review SQL script: `/scripts/create_project_team_members_table.sql`
- [ ] Run SQL migration:
  ```bash
  sqlite3 AdminLoginPanel/project_management.db < scripts/create_project_team_members_table.sql
  ```
- [ ] Verify table created:
  ```sql
  SELECT name FROM sqlite_master WHERE type='table' AND name='project_team_members';
  ```
- [ ] Verify indexes created:
  ```sql
  SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_project_team_members%';
  ```

### Phase 2: Backend (10 minutes)

- [ ] Open `AdminLoginPanel/app.py`
- [ ] Find appropriate location (around line 4552)
- [ ] Copy code from `/scripts/backend_team_members_logic.py`
- [ ] Add all 4 functions to app.py:
  - [ ] `get_eligible_team_members()`
  - [ ] `add_team_members_to_project()`
  - [ ] `get_project_team_members()`
  - [ ] `remove_team_member_from_project()`
- [ ] Save app.py
- [ ] Verify syntax (Flask should start without errors)

### Phase 3: Frontend (5 minutes)

- [ ] Open `AdminLoginPanel/templates/project-detail.html`
- [ ] Find the route that renders this template
- [ ] Update route to pass `is_coordinator`:
  ```python
  is_coordinator = (project['project_coordinator_id'] == session.get('user_id'))
  ```
- [ ] Find closing `</body>` tag in project-detail.html
- [ ] Add modal HTML from `/scripts/team_members_modal_insertion.html`
- [ ] Save project-detail.html

### Phase 4: Testing (15 minutes)

- [ ] Start Flask app
- [ ] Login as Project Coordinator
- [ ] Navigate to project details
- [ ] Verify "Add Team Members" button appears
- [ ] Click button to open modal
- [ ] Verify employee list loads
- [ ] Test selection (2-3 members)
- [ ] Test max limit (try 4th member)
- [ ] Submit and verify database
- [ ] Refresh page and confirm members persist

---

## Verification Steps

### Database Verification

```sql
-- Check table exists
.tables

-- Check table structure
.schema project_team_members

-- Check indexes
SELECT * FROM sqlite_master WHERE type='index' AND tbl_name='project_team_members';

-- Verify sample data (after testing)
SELECT * FROM project_team_members LIMIT 5;
```

### Backend Verification

```python
# Test in Python console
import requests

# Test endpoint (replace with real IDs)
response = requests.get('/api/coordinator/eligible-team-members/1')
print(response.json())
```

### Frontend Verification

```javascript
// Open browser console while on project-detail page
// Test API call
fetch('/api/coordinator/eligible-team-members/1')
  .then(r => r.json())
  .then(d => console.log(d))
```

---

## Test Cases

### Test Case 1: Modal Opens
- [ ] Login as coordinator
- [ ] Open project assigned to coordinator
- [ ] "Add Team Members" button visible
- [ ] Click button
- [ ] Modal appears with loading spinner
- [ ] Employee list loads after ~1s

### Test Case 2: Select Members
- [ ] Modal shows employee list
- [ ] Can check employee checkbox
- [ ] Counter updates (0 → 1 → 2 → 3)
- [ ] Progress bar fills proportionally
- [ ] Submit button enables

### Test Case 3: Enforce Limits
- [ ] Modal shows 3+ employees
- [ ] Can check up to 3 members
- [ ] 4th checkbox won't check
- [ ] Error message appears
- [ ] Counter stays at 3

### Test Case 4: Submit and Save
- [ ] Select 2-3 members
- [ ] Click "Add Selected Members"
- [ ] Button shows loading spinner
- [ ] Success message appears
- [ ] Modal closes
- [ ] Page reloads
- [ ] Team Members table shows new members

### Test Case 5: Database Integrity
- [ ] Query `project_team_members` table
- [ ] Verify project_id and user_id populated
- [ ] Verify no duplicates (UNIQUE constraint works)
- [ ] Verify assigned_at timestamp set

### Test Case 6: Access Control
- [ ] Non-coordinator cannot add members
  - [ ] Button hidden
  - [ ] API returns 403 if forced
- [ ] Cannot add members from other coordinators
  - [ ] API returns 403
- [ ] Cannot exceed 3 members
  - [ ] API returns 400

---

## Troubleshooting

### Issue: Button Doesn't Appear

**Cause:** `is_coordinator` not passed to template

**Solution:**
```python
# In admin_project_detail() function
is_coordinator = (project['project_coordinator_id'] == session.get('user_id'))
return render_template('project-detail.html', project=project, is_coordinator=is_coordinator)
```

### Issue: Modal Opens but "No Employees" Message

**Cause:** Team members don't have correct `parent_user_id`

**Solution:**
```sql
-- Check if team members have correct parent_user_id
SELECT id, username, parent_user_id FROM users WHERE parent_user_id = <coordinator_id>;

-- Update if needed
UPDATE users SET parent_user_id = <coordinator_id> WHERE id IN (1, 2, 3);
```

### Issue: "Cannot Select More Than 1" 

**Cause:** JavaScript error or Bootstrap not loaded

**Solution:**
- Check browser console for errors
- Verify Bootstrap 5 CSS/JS loaded
- Check that JavaScript is enabled

### Issue: "Access Denied" on Submit

**Cause:** Session expired or user not coordinator

**Solution:**
- Refresh page and login again
- Verify user is in Project Coordinator role
- Check `project_coordinator_id` in database

### Issue: Members Not Saving

**Cause:** Backend endpoints not added or syntax error

**Solution:**
- Check Flask console for errors
- Verify all 4 functions added to app.py
- Verify indentation correct
- Restart Flask app

### Issue: "Maximum 3 Members" but only allowed 2

**Cause:** Validation mismatch in code

**Solution:**
- Check `MAX_MEMBERS = 3` in JavaScript
- Check backend validation allows 3
- Check database allows UNIQUE (project_id, user_id)

---

## Success Criteria

After implementation, the feature should:

- [ ] Show "Add Team Members" button on project details page
- [ ] Button only visible for project coordinators
- [ ] Modal opens and loads employee list
- [ ] Can select 2-3 employees
- [ ] Cannot select more than 3
- [ ] Cannot add already-assigned members
- [ ] Submit creates entries in `project_team_members` table
- [ ] Team members appear in project team list
- [ ] Data persists after page refresh
- [ ] All API endpoints return correct responses
- [ ] All validations work (access control, limits, etc)

---

## Rollback Plan

If something goes wrong:

```sql
-- Drop the new table if needed
DROP TABLE IF EXISTS project_team_members;

-- Remove from app.py:
-- - All 4 functions added
-- - Revert to previous version if in Git

-- Remove from project-detail.html:
-- - Modal HTML
-- - Button HTML
-- - JavaScript
-- - Revert to previous version if in Git
```

---

## Documentation Files

- **Quick Start:** `TEAM_MEMBERS_QUICK_START.md`
- **Full Guide:** `docs/ADD_TEAM_MEMBERS_IMPLEMENTATION.md`
- **This Checklist:** `TEAM_MEMBERS_IMPLEMENTATION_CHECKLIST.md`
- **SQL:** `scripts/create_project_team_members_table.sql`
- **Backend:** `scripts/backend_team_members_logic.py`
- **Frontend:** `scripts/team_members_modal_insertion.html`

---

**Status:** Ready to implement
**Estimated Time:** 30-45 minutes total
