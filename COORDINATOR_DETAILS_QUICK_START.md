# Coordinator Details - Quick Start (15 Minutes)

## What This Does
Click on any Project Coordinator in the hierarchy view to see:
- Team members list
- Assigned projects with progress
- All tasks assigned to the team with status

## 3 Simple Steps

### Step 1: Add Backend (7 min)
**File:** `AdminLoginPanel/app.py`  
**Line:** ~2750 (after existing hierarchy code)  
**Action:** Copy entire `scripts/coordinator_details_backend.py` and paste

### Step 2: Add Modal (5 min)
**File:** `AdminLoginPanel/templates/admin-dashboard.html`  
**Line:** Before `</body>` tag (~5500)  
**Action:** Copy entire `scripts/coordinator_details_modal.html` and paste

### Step 3: Enable Clicks (3 min)
**In the hierarchy tree rendering code, find coordinator nodes and add:**
```html
onclick="openCoordinatorDetails(${coordinator.id})"
```

Example:
```html
<div class="hierarchy-node" 
     onclick="openCoordinatorDetails(2)">
    John Coordinator
</div>
```

## Done!

Restart Flask and test:
1. Go to Admin Dashboard
2. Click "User Hierarchy"
3. Click any Coordinator name
4. Details modal appears ✓

## What You'll See

### Tab 1: Team Members
- List of all employees under coordinator
- Email addresses

### Tab 2: Projects
- Project name
- Status (Active/Pending/Completed)
- How many team members assigned
- Total tasks and completed tasks
- Progress bar

### Tab 3: Assigned Tasks
- Task name
- Assigned to (team member)
- Project name
- Status badge
- Priority badge
- Deadline
- Progress bar

## Troubleshooting

**Modal doesn't open?**
- Add `onclick="openCoordinatorDetails(coordinatorId)"` to coordinator nodes

**No data shows up?**
- Coordinator needs team members assigned
- Team members need projects assigned
- Check browser console for errors

**Getting 404 error?**
- Did you add the backend code to app.py?
- Restart Flask after adding backend

## Files Involved

```
Backend:
  └── scripts/coordinator_details_backend.py (244 lines)
     → Add to AdminLoginPanel/app.py

Frontend:
  └── scripts/coordinator_details_modal.html (742 lines)
     → Add to AdminLoginPanel/templates/admin-dashboard.html

Integration:
  └── scripts/hierarchy_coordinator_click_integration.js (reference)
     → Shows how to hook up clicks
```

## Next Steps

After basic implementation, you can:
- Customize colors and styling
- Add search/filter functionality
- Export data to CSV
- Add edit capabilities
