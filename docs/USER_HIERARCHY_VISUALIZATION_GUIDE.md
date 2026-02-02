# User Hierarchy Visualization - Implementation Guide

## Overview
This feature adds a read-only organizational hierarchy visualization to the Super Admin Dashboard. Displays the complete structure from Super Admin down to individual tasks.

## Architecture

### Hierarchy Structure
```
Super Admin (parent_user_id = NULL)
  ├── Project Coordinator (parent_user_id = Super Admin ID)
  │    ├── Team Member (parent_user_id = Coordinator ID)
  │    │    ├── Project (assigned via project_team_members)
  │    │    │    ├── Milestone
  │    │    │    │    └── Task
```

### Database Queries
The backend uses recursive queries and joins to fetch the complete hierarchy:
- **Users table**: parent_user_id column for relationships
- **Projects table**: project_coordinator_id for coordinator assignment
- **project_team_members**: Links users to projects
- **Milestones**: Linked to projects
- **Tasks**: Linked to milestones

## Implementation Steps

### Step 1: Add Backend Routes (10 min)

**Location**: `AdminLoginPanel/app.py` (around line 2750)

**Code**: Copy entire `/scripts/user_hierarchy_backend.py`

**Key endpoints**:
1. `GET /api/hierarchy/full` - Detailed hierarchy with all fields
2. `GET /api/hierarchy/tree` - Simplified tree structure for frontend rendering

**Authentication**: Both endpoints require `@super_admin_required` decorator

### Step 2: Add Frontend Modal & Button (10 min)

**Location**: `AdminLoginPanel/templates/admin-dashboard.html`

**Two insertions**:

1. **Button insertion** (around line 1929, in `action-buttons` div):
```html
<div class="action-card">
    <h3><i class="fas fa-sitemap"></i> User Hierarchy</h3>
    <p>View organizational structure and team relationships</p>
    <button class="btn btn-primary" onclick="openHierarchyModal()">View Hierarchy</button>
</div>
```

2. **Modal insertion** (before `</body>` tag, around line 5500):
Copy entire `/scripts/user_hierarchy_modal_insertion.html`

### Step 3: Test (5 min)

1. Login as Super Admin
2. Go to Admin Dashboard
3. Locate "User Hierarchy" button in action cards
4. Click to open modal
5. Verify tree displays correctly
6. Test expand/collapse functionality
7. Test search filter

## Features

### User Interface
- **Interactive Tree View**: Click to expand/collapse nodes
- **Expand/Collapse All**: Bulk control buttons
- **Search Filter**: Search by name or email (auto-expands matches)
- **Color-coded Icons**: Different colors for different hierarchy levels
- **Loading States**: Shows spinner while fetching
- **Error Handling**: Displays error message if load fails

### Functionality
- **Read-only View**: No editing capabilities
- **Auto-collapse**: Nodes collapsed by default (for performance)
- **Search Auto-expand**: Matching nodes expand automatically
- **Keyboard Navigation**: Close modal with Escape key
- **Responsive**: Works on desktop, tablet, mobile

### Security
- **Super Admin Only**: Requires admin authentication
- **@super_admin_required**: Decorator on all endpoints
- **Session Validation**: Checks session for admin status
- **Server-side Filtering**: No client-side data exposure

## Database Queries

### Get All Super Admins
```sql
SELECT DISTINCT u.id, u.username, u.email
FROM users u
WHERE u.parent_user_id IS NULL
ORDER BY u.username
```

### Get Coordinators Under Super Admin
```sql
SELECT u.id, u.username, u.email
FROM users u
WHERE u.parent_user_id = ?
AND LOWER(u.user_type) LIKE '%coordinator%'
```

### Get Team Members Under Coordinator
```sql
SELECT u.id, u.username, u.email
FROM users u
WHERE u.parent_user_id = ?
AND (LOWER(u.user_type) LIKE '%team%' OR LOWER(u.user_type) LIKE '%employee%')
```

### Get Projects for User
```sql
SELECT DISTINCT p.id, p.title, p.description, p.status
FROM projects p
JOIN project_team_members ptm ON p.id = ptm.project_id
WHERE ptm.user_id = ?
```

### Get Milestones in Project
```sql
SELECT m.id, m.title, m.description, m.status
FROM milestones m
WHERE m.project_id = ?
```

### Get Tasks in Milestone
```sql
SELECT t.id, t.title, t.description, t.status, t.deadline
FROM tasks t
WHERE t.milestone_id = ?
```

## Performance Considerations

### Query Optimization
- Uses JOINs instead of multiple queries
- Filters by hierarchy relationships
- Indexes on parent_user_id, project_id, milestone_id
- Lazy loading via frontend collapse/expand

### Frontend Optimization
- Renders tree once on load
- No re-fetching on expand/collapse
- Search filter uses CSS display:none (not DOM removal)
- Escape key handling for modal closure

## Testing Checklist

- [ ] Backend routes added to app.py
- [ ] Button appears in admin dashboard
- [ ] Modal opens when button clicked
- [ ] Tree loads with data
- [ ] Super Admins display at top level
- [ ] Coordinators display under Super Admins
- [ ] Team Members display under Coordinators
- [ ] Projects display under Team Members
- [ ] Milestones display under Projects
- [ ] Tasks display under Milestones
- [ ] Expand/collapse toggle works
- [ ] Expand All button works
- [ ] Collapse All button works
- [ ] Search filter works with names
- [ ] Search filter works with emails
- [ ] Matching nodes auto-expand
- [ ] Non-admin users cannot access
- [ ] Modal closes on X button
- [ ] Modal closes on Escape key
- [ ] Modal closes on outside click

## Troubleshooting

### Modal doesn't open
- Check browser console for JavaScript errors
- Verify `openHierarchyModal()` function is defined
- Ensure button `onclick` handler is spelled correctly

### Tree doesn't load
- Check Network tab for API response
- Verify `/api/hierarchy/tree` endpoint returns 200
- Check if user is Super Admin (403 if not)
- Check database connection and hierarchy data

### Search not working
- Verify search input ID is `hierarchySearch`
- Check if `filterHierarchyTree()` function is called on keyup
- Ensure nodes have text content to match

### Performance issues
- Check for N+1 queries in backend
- Verify indexes on parent_user_id columns
- Consider pagination for very large hierarchies
- Profile database queries with EXPLAIN

## Future Enhancements

1. **Export**: Export hierarchy as JSON/CSV
2. **Sync**: Real-time updates via WebSocket
3. **Drill-down**: Click to view full details of each node
4. **Filters**: Filter by user type, status, project
5. **Statistics**: Show counts (e.g., "5 coordinators, 23 team members")
6. **Breadcrumb**: Show current path in hierarchy
7. **Print**: Print-friendly hierarchy view
8. **Comparison**: Compare two branches

## Files Modified

1. **AdminLoginPanel/app.py** - Added 2 new endpoints + helper functions
2. **AdminLoginPanel/templates/admin-dashboard.html** - Added button + modal + styles + scripts

## Files Created

1. **scripts/user_hierarchy_backend.py** - Backend implementation reference
2. **scripts/user_hierarchy_modal_insertion.html** - Frontend implementation reference
3. **docs/USER_HIERARCHY_VISUALIZATION_GUIDE.md** - This file

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the Testing Checklist
3. Verify all files were copied correctly
4. Check browser console for errors
5. Check server logs for backend errors
