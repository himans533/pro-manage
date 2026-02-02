# Integration Checklist - Implementation in Order

Follow this checklist to properly integrate all features. Check off each item as you complete it.

## Phase 1: Database Setup (5 minutes)

- [ ] **Add user hierarchy column**
  - File: `/scripts/add_user_hierarchy.sql`
  - Execute against your database
  - Adds `parent_user_id` column to `users` table

- [ ] **Add project coordinator column**
  - File: `/scripts/add_project_coordinator.sql`
  - Execute against your database
  - Adds `project_coordinator_id` column to `projects` table

- [ ] **Create team members table**
  - File: `/scripts/create_project_team_members_table.sql`
  - Execute against your database
  - Creates `project_team_members` table with indexes

- [ ] **Verify database changes**
  - Run: `sqlite3 AdminLoginPanel/project_management.db ".schema"`
  - Check for: `parent_user_id`, `project_coordinator_id`, `project_team_members` table

## Phase 2: Backend Implementation (30 minutes)

### Authorization Functions (Most Important First)
- [ ] **Copy authorization middleware**
  - From: `/scripts/authorization_middleware.py`
  - Into: `AdminLoginPanel/app.py` (around line 2000)
  - Functions: `is_super_admin()`, `is_coordinator()`, `is_team_member()`, decorators

### Dashboard & Statistics
- [ ] **Add dashboard stats endpoint**
  - From: `/scripts/dashboard_stats_backend.py`
  - Into: `AdminLoginPanel/app.py` (around line 2750)
  - Endpoint: `GET /api/dashboard/stats`

### Hierarchy Features
- [ ] **Add hierarchy endpoints**
  - From: `/scripts/user_hierarchy_backend.py`
  - Into: `AdminLoginPanel/app.py` (around line 3000)
  - Endpoints: `/api/hierarchy/full`, `/api/hierarchy/tree`

- [ ] **Add coordinator details endpoint**
  - From: `/scripts/coordinator_details_backend.py`
  - Into: `AdminLoginPanel/app.py` (around line 3200)
  - Endpoint: `GET /api/coordinator/<coordinator_id>/details`

### Employee Dashboard Filtering
- [ ] **Add employee dashboard filter**
  - From: `/scripts/employee_dashboard_filter.py`
  - Into: `AdminLoginPanel/app.py` (update existing `get_employee_projects()`)
  - Modify: Add role check to filter by coordinator

### Team Management
- [ ] **Add team members endpoints**
  - From: `/scripts/backend_team_members_logic.py`
  - Into: `AdminLoginPanel/app.py` (around line 3400)
  - Endpoints: `/api/coordinator/add-team-members/<project_id>`, etc.

- [ ] **Add single team member endpoint**
  - From: `/scripts/add_single_team_member_backend.py`
  - Into: `AdminLoginPanel/app.py` (around line 3500)
  - Endpoint: `POST /api/coordinator/add-team-member/<project_id>`

### Task Assignment
- [ ] **Add task assignment filtering**
  - From: `/scripts/task_assignment_backend_solution.py`
  - Into: `AdminLoginPanel/app.py` (around line 3600)
  - Endpoint: `GET /api/projects/<project_id>/eligible-assignees`

### Project Coordinator
- [ ] **Add project coordinator assignment**
  - From: `/scripts/backend_python_snippets.py`
  - Into: `AdminLoginPanel/app.py` (around line 3100)
  - Modify: `create_employee_project()` to save coordinator

- [ ] **Test backend**
  - Restart Flask server
  - Test each endpoint with curl or Postman
  - Verify responses and error handling

## Phase 3: Frontend - Admin Dashboard (20 minutes)

### Add Buttons & Navigation
- [ ] **Add "👥 User Hierarchy" button**
  - From: Dashboard action cards section
  - Into: `admin-dashboard.html` (around line 1925)
  - Add: `onclick="openHierarchyModal()"`

- [ ] **Add project coordinator dropdown in project creation**
  - From: `/scripts/html_dropdown_insertion.html`
  - Into: `admin-dashboard.html` (around line 2662)
  - ID: `projectCoordinatorSelect`

- [ ] **Add "Add Team Members" button to project details**
  - From: `/scripts/team_members_modal_insertion.html` (header section)
  - Into: `project-detail.html` (near project title)
  - ID: `addTeamMembersBtn`

### Add Modals
- [ ] **Add hierarchy modal**
  - From: `/scripts/user_hierarchy_modal_insertion.html`
  - Into: `admin-dashboard.html` (before `</body>`)
  - ID: `hierarchyModal`

- [ ] **Add coordinator details modal**
  - From: `/scripts/coordinator_details_modal.html`
  - Into: `admin-dashboard.html` (before `</body>`)
  - ID: `coordinatorDetailsModal`

- [ ] **Add team members bulk add modal**
  - From: `/scripts/team_members_modal_insertion.html`
  - Into: `project-detail.html` (before `</body>`)
  - ID: `addTeamMembersModal`

- [ ] **Add team member single add modal**
  - From: `/scripts/add_single_team_member_modal.html`
  - Into: `project-detail.html` (before `</body>`)
  - ID: `addSingleMemberModal`

### Add Statistics
- [ ] **Add dashboard statistics cards**
  - From: `/scripts/dashboard_stats_cards.html`
  - Into: `admin-dashboard.html` (after page header, around line 200)
  - IDs: `statsContainer`

## Phase 4: Frontend - Employee Dashboard (15 minutes)

### Add Statistics
- [ ] **Add dashboard statistics cards**
  - From: `/scripts/dashboard_stats_cards.html`
  - Into: `employee-dashboard.html` (after page header, around line 200)
  - IDs: `statsContainer`

### Task Form Updates
- [ ] **Update task project dropdown**
  - From: `/scripts/task_assignment_html_changes.html`
  - Into: `employee-dashboard.html` (task form section)
  - Add: `onchange="handleTaskProjectChange(this.value)"`

- [ ] **Add task assignee dropdown container**
  - From: `/scripts/task_assignment_html_changes.html`
  - Into: `employee-dashboard.html` (in task form)
  - Note: Dropdown will be populated dynamically

### Add Modals
- [ ] **Add add-team-member button**
  - From: `/scripts/add_single_team_member_modal.html` (button section)
  - Into: Project detail page (as coordinator)

- [ ] **Add JavaScript functions for task filtering**
  - From: `/scripts/task_assignment_frontend_changes.js`
  - Into: `employee-dashboard.html` (in script section)
  - Functions: `populateTaskAssigneeDropdown()`, `handleTaskProjectChange()`

## Phase 5: Testing (30 minutes)

### Setup Test Data
- [ ] **Create test users**
  - Super Admin (user_id=1, parent_user_id=NULL)
  - Coordinator (user_id=2, parent_user_id=1)
  - Team Member 1 (user_id=3, parent_user_id=2)
  - Team Member 2 (user_id=4, parent_user_id=2)

### Test Hierarchy Features
- [ ] **Test hierarchy visualization**
  - Login as Super Admin
  - Go to Admin Dashboard
  - Click "👥 User Hierarchy"
  - Verify tree displays all users

- [ ] **Test hierarchy search**
  - Use search filter
  - Verify nodes expand to show matches

- [ ] **Test coordinator details**
  - Click on coordinator in tree
  - Verify shows team members, projects, tasks

### Test Authorization
- [ ] **Test Super Admin access**
  - Login as Super Admin
  - Access: `/api/hierarchy/full` ✓
  - See: All projects, all tasks

- [ ] **Test Coordinator access**
  - Login as Coordinator
  - Access: `/api/hierarchy/full` ✗ (should be denied)
  - See: Only their projects
  - See: Only their team members

- [ ] **Test Team Member access**
  - Login as Team Member
  - See: Only their tasks
  - Cannot: Access projects directly

### Test Team Management
- [ ] **Test add team members (bulk)**
  - Project detail → "Add Team Members" button
  - Select 2-3 members
  - Verify saved to database

- [ ] **Test add team member (single)**
  - Project detail → "Add New Team Member" button
  - Select one member
  - Verify added without duplicates

- [ ] **Test max 3 member limit**
  - Try to add 4th member
  - Verify error message

### Test Task Assignment
- [ ] **Test task dropdown filtering**
  - Create task in project with team members
  - "Assign Employee" dropdown
  - Verify shows ONLY team members
  - NOT all employees

- [ ] **Test dashboard statistics**
  - Dashboard loads stats cards
  - Counts update correctly
  - Auto-refresh every 30 seconds

- [ ] **Test project coordinator assignment**
  - Create project
  - Assign coordinator dropdown appears
  - Select and save coordinator

## Phase 6: Cleanup (Optional)

- [ ] **Backup /scripts directory** (for reference later)
- [ ] **Delete /scripts directory** (if satisfied with integration)
- [ ] **Remove temporary SQL files** if desired
- [ ] **Keep /IMPLEMENTATION_GUIDE.md** for future reference

## Troubleshooting During Integration

### Issue: Backend endpoint returns 404
- **Check**: Did you restart Flask after adding code?
- **Check**: Is the route decorator correct? (`@app.route(...)`)
- **Check**: Is there a syntax error in the code?

### Issue: Modal doesn't open
- **Check**: Does the HTML ID match the JavaScript function?
- **Check**: Are the JavaScript functions defined?
- **Check**: Is there a JavaScript error in console?

### Issue: Dropdown is empty
- **Check**: Does the API endpoint return data?
- **Check**: Is the endpoint being called? (Check Network tab)
- **Check**: Is the user a coordinator with team members?

### Issue: Statistics don't show
- **Check**: Does `/api/dashboard/stats` work? (Test in browser)
- **Check**: Is the JavaScript loading? (Check console)
- **Check**: Does the user have projects/tasks?

### Issue: Access denied errors
- **Check**: Is user logged in?
- **Check**: Is user in correct role?
- **Check**: Is authorization check working?

## Final Verification

After all integration:

- [ ] Application starts without errors
- [ ] Super Admin can access all features
- [ ] Coordinator sees only their data
- [ ] Team Member sees only their tasks
- [ ] All modals open and close correctly
- [ ] All dropdowns populate correctly
- [ ] Dashboard statistics display
- [ ] No console errors
- [ ] Responsive on mobile
- [ ] All links work
- [ ] No duplicate code
- [ ] No unused imports

## You're Done!

Once all items are checked, your system is fully integrated with:
- ✓ Role-based hierarchy (Super Admin → Coordinator → Team Member)
- ✓ Project coordinator assignment
- ✓ Team member management (2-3 members per project)
- ✓ Task assignment filtering
- ✓ Dashboard statistics
- ✓ Hierarchy visualization
- ✓ Coordinator details view
- ✓ Complete authorization system

Good luck with the implementation!
