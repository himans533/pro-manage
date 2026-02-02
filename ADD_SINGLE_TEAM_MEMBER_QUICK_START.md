# Add New Team Member - Quick Start (15 minutes)

## What Does This Do?

Adds a green "Add New Team Member" button to Project Details page.

Coordinators can add individual employees one at a time to their projects.

## Files to Modify

| File | What | Time |
|------|------|------|
| `AdminLoginPanel/app.py` | Add 2 endpoints | 10 min |
| `AdminLoginPanel/templates/project-detail.html` | Add button + modal + JS | 5 min |

## Implementation (15 minutes total)

### Backend (10 min)

1. Open `AdminLoginPanel/app.py`
2. Go to line ~4500
3. Copy all code from `/scripts/add_single_team_member_backend.py`
4. Paste into app.py

That's it! Two new endpoints are added:
- `POST /api/coordinator/add-team-member/<project_id>`
- `GET /api/coordinator/available-team-members/<project_id>`

### Frontend (5 min)

1. Open `AdminLoginPanel/templates/project-detail.html`
2. Go to end of file (before `</body>`)
3. Copy all code from `/scripts/add_single_team_member_modal.html`
4. Paste before `</body>`

That's it! Button and modal now available.

## Testing (2 min)

1. Login as Project Coordinator
2. Open any project
3. Look for green "Add New Team Member" button
4. Click it
5. Select employee from dropdown
6. Click "Add Team Member"
7. Verify success message
8. Check team members list updated

## Key Points

✓ Uses existing `project_team_members` table  
✓ Max 3 members per project enforced  
✓ Only can add own team members (parent_user_id = coordinator)  
✓ Non-breaking: works with existing code  
✓ Simple dropdown interface  

## Files

```
Implementation:
  /scripts/add_single_team_member_backend.py (198 lines)
  /scripts/add_single_team_member_modal.html (248 lines)

Documentation:
  /docs/ADD_SINGLE_TEAM_MEMBER_IMPLEMENTATION.md (260 lines)
  /ADD_SINGLE_TEAM_MEMBER_QUICK_START.md (this file)
```

## Need Help?

See `/docs/ADD_SINGLE_TEAM_MEMBER_IMPLEMENTATION.md` for detailed guide.
