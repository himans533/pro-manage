# Add New Team Member - Implementation Guide

## Overview

This feature adds an "Add New Team Member" button to the Project Details page that allows Project Coordinators to add individual employees to a project one at a time.

**Key Differences from "Add Team Members to Project":**
- "Add Team Members to Project": Bulk add 2-3 members at once
- "Add New Team Member": Add single member, can be used repeatedly

## Files to Modify

### 1. Backend: `AdminLoginPanel/app.py`

**Location:** Around line 4500 (after existing endpoints)

**What to add:**
- `add_single_team_member()` - POST endpoint to add one employee
- `get_available_team_members()` - GET endpoint to fetch eligible employees

See: `/scripts/add_single_team_member_backend.py`

**Time:** 10 minutes

### 2. Frontend: `AdminLoginPanel/templates/project-detail.html`

**Location:** Before closing `</body>` tag

**What to add:**
- Button: "Add New Team Member"
- Modal dialog with dropdown
- JavaScript to handle selection and API calls

See: `/scripts/add_single_team_member_modal.html`

**Time:** 5 minutes

## Step-by-Step Implementation

### Step 1: Add Backend Endpoints (10 min)

1. Open `/AdminLoginPanel/app.py`
2. Go to around line 4500 (after other coordinator endpoints)
3. Copy the entire content from `/scripts/add_single_team_member_backend.py`
4. Paste into app.py

**Endpoints added:**
```
POST /api/coordinator/add-team-member/<project_id>
  - Adds single employee to project_team_members
  - Validates: max 3 members, employee ownership, no duplicates

GET /api/coordinator/available-team-members/<project_id>
  - Returns employees not yet added to project
  - Used to populate dropdown
```

### Step 2: Add Frontend Button and Modal (5 min)

1. Open `/AdminLoginPanel/templates/project-detail.html`
2. Find the coordinator actions div or header section
3. Copy content from `/scripts/add_single_team_member_modal.html`
4. Paste before closing `</body>` tag

**Key elements:**
- Button (green, "Add New Team Member")
- Modal with employee dropdown
- JavaScript for loading and submitting

### Step 3: Ensure is_coordinator Variable (1 min)

In the backend route that renders `project-detail.html`, make sure to pass:
```python
is_coordinator = (session.get('user_id') == project.project_coordinator_id)
render_template('project-detail.html', 
                project=project,
                members=members,
                tasks=tasks,
                is_coordinator=is_coordinator)
```

## How It Works

### Coordinator Workflow

1. **Views Project Details Page**
   - Sees "Add New Team Member" button (green) in coordinator actions
   - Only visible to coordinators

2. **Clicks Button**
   - Modal opens
   - Backend fetches available employees
   - Employees dropdown populates

3. **Selects Employee**
   - Selects from dropdown
   - "Add Team Member" button enables

4. **Clicks Add**
   - Backend validates:
     - Employee is under coordinator
     - Not already in project
     - Max 3 members not exceeded
   - Employee added to `project_team_members`
   - Success message shown
   - Page reloads to show updated list

### Data Flow

```
Click "Add New Team Member" button
         ↓
Modal opens
         ↓
GET /api/coordinator/available-team-members/<project_id>
         ↓
Backend checks:
  - User is coordinator for project
  - Fetch employees with parent_user_id = coordinator
  - Exclude employees already in project_team_members
  - Check if max reached
         ↓
Dropdown populated with available employees
         ↓
Coordinator selects employee
         ↓
Click "Add Team Member"
         ↓
POST /api/coordinator/add-team-member/<project_id>
  with { "user_id": selected_id }
         ↓
Backend validates:
  - Project exists
  - User is coordinator
  - Employee under coordinator
  - Not already added
  - Max 3 not exceeded
         ↓
INSERT into project_team_members
         ↓
Success response
         ↓
Page reloads
         ↓
Updated team list visible
```

## Database Impact

**Table:** `project_team_members` (already created)

**Query:**
```sql
INSERT INTO project_team_members (project_id, user_id)
VALUES (?, ?)
```

**Validation queries:**
- Check project coordinator ownership
- Check employee parent_user_id
- Check for duplicates
- Count current members

## Error Handling

### Possible Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Not authenticated" | User not logged in | User must log in |
| "Project not found or you are not the coordinator" | Not coordinator | Only coordinators can use |
| "Employee not found or not under your supervision" | Employee not in hierarchy | Can only add own team |
| "Employee already added to this project" | Duplicate | Choose different employee |
| "Maximum 3 team members already added" | Limit reached | Remove member first |

## Validation Rules

```python
✓ User must be authenticated
✓ User must be project coordinator
✓ Employee must exist
✓ Employee.parent_user_id must = coordinator.id
✓ Employee not already in project_team_members
✓ Current count < 3
✓ Project must exist
```

## Response Examples

### Success Response
```json
{
  "success": true,
  "message": "Employee john_doe added to project",
  "user_id": 42,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Error Response
```json
{
  "error": "Maximum 3 team members already added to this project"
}
```

## Testing Checklist

- [ ] Login as Project Coordinator
- [ ] Open project details page
- [ ] See green "Add New Team Member" button
- [ ] Click button → Modal opens
- [ ] Modal loads employees dropdown
- [ ] Select employee → Button enables
- [ ] Click Add → Success message
- [ ] Page reloads → Employee in team list
- [ ] Try adding duplicate → Error message
- [ ] Try adding 4th member → Error about max limit
- [ ] Login as regular employee → No button visible
- [ ] Try accessing API directly as non-coordinator → 403 error

## Troubleshooting

### Button Not Visible
- Check `is_coordinator` passed to template
- Check user is project coordinator in database

### Dropdown Empty
- Check employees exist with `parent_user_id = coordinator_id`
- Check not all already added

### Add Fails with "Access Denied"
- Verify coordinator ownership in database
- Check employee's parent_user_id

### "Maximum 3 Members" Error
- Remove a team member first using remove endpoint
- Or create separate "Remove Team Member" feature

## Performance Considerations

- Uses indexed queries on `parent_user_id` and project lookup
- Dropdown loads on modal open (not page load)
- No pagination needed (typically < 10 employees per coordinator)

## Security

- Session-based authentication required
- Coordinator verification on each request
- Employee ownership validation
- CSRF protection via Flask
- SQL parameterized queries (no injection risk)

## Related Features

- "Add Team Members to Project" - Bulk add 2-3 at once
- "View Project Team" - See current team members
- "Remove Team Member" - Remove individual members (optional)
