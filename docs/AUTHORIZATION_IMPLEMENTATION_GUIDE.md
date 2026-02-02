# Authorization Implementation Guide

## Overview

This guide explains how to implement role-based access control (RBAC) across your Project Management System using the authorization middleware provided in `/scripts/authorization_middleware.py`.

**Key Principle:** No authentication is modified. Only authorization checks are added.

---

## Access Control Model

### Role Definitions

| Role | Level | Access |
|------|-------|--------|
| Super Admin | 3 | All projects, all tasks, all users, all hierarchy |
| Project Coordinator | 2 | Only their assigned projects + their team members |
| Team Member | 1 | Only their assigned tasks |

### Data Visibility Rules

```
Super Admin → SEES EVERYTHING

Project Coordinator → SEES:
  • Projects where project_coordinator_id = their_id
  • Team members where parent_user_id = their_id
  • Tasks in their projects
  • Team member tasks

Team Member → SEES:
  • Only tasks assigned_to_id = their_id
  • Their own daily reports
  • Cannot see other team members
```

---

## Import & Setup

### Step 1: Import the Module

Add to top of `AdminLoginPanel/app.py`:

```python
from scripts.authorization_middleware import (
    get_current_user_id,
    get_current_user_role,
    is_super_admin,
    is_coordinator,
    is_team_member,
    user_can_view_project,
    user_can_view_task,
    user_can_view_team_member,
    get_filtered_projects,
    get_filtered_tasks,
    get_filtered_team_members,
    super_admin_only,
    coordinator_or_admin,
    ROLE_SUPER_ADMIN,
    ROLE_COORDINATOR,
    ROLE_TEAM_MEMBER
)
```

### Step 2: Make DB_PATH Global

Ensure `DB_PATH` is defined at module level (it already is in your app.py):

```python
DB_PATH = os.path.join(os.path.dirname(__file__), 'project_management.db')
```

---

## Implementation Patterns

### Pattern 1: Super Admin Only Access

```python
@app.route('/api/hierarchy/full')
@login_required
@super_admin_only(DB_PATH)
def get_full_hierarchy():
    """Only Super Admin can access"""
    # Code here is automatically protected
    return jsonify({'hierarchy': 'data'})
```

### Pattern 2: Coordinator & Admin Access

```python
@app.route('/api/coordinator/team')
@login_required
@coordinator_or_admin(DB_PATH)
def get_coordinator_team():
    """Only Coordinators and Super Admin can access"""
    user_id = get_current_user_id()
    team = get_filtered_team_members(user_id, DB_PATH)
    return jsonify({'team': team})
```

### Pattern 3: Role-Based Filtering (Projects)

```python
@app.route('/api/projects')
@login_required
def get_projects():
    """Returns filtered projects based on user role"""
    user_id = get_current_user_id()
    
    # Automatically filters:
    # - Super Admin: all projects
    # - Coordinator: only their projects
    # - Team Member: only assigned projects
    projects = get_filtered_projects(user_id, DB_PATH)
    
    return jsonify({'projects': projects})
```

### Pattern 4: Role-Based Filtering (Tasks)

```python
@app.route('/api/tasks')
@login_required
def get_tasks():
    """Returns filtered tasks based on user role"""
    user_id = get_current_user_id()
    
    # Automatically filters:
    # - Super Admin: all tasks
    # - Coordinator: tasks in their projects
    # - Team Member: only assigned tasks
    tasks = get_filtered_tasks(user_id, DB_PATH)
    
    return jsonify({'tasks': tasks})
```

### Pattern 5: Specific Resource Access Check

```python
@app.route('/api/projects/<int:project_id>')
@login_required
def get_project_detail(project_id):
    """Access check before returning project"""
    user_id = get_current_user_id()
    
    # Check if user can view this project
    if not user_can_view_project(user_id, project_id, DB_PATH):
        return jsonify({'error': 'Access denied'}), 403
    
    # Proceed with getting project
    conn = get_db_connection()
    project = conn.execute(
        'SELECT * FROM projects WHERE id = ?',
        (project_id,)
    ).fetchone()
    conn.close()
    
    return jsonify(dict(project))
```

### Pattern 6: Task Access Check

```python
@app.route('/api/tasks/<int:task_id>')
@login_required
def get_task_detail(task_id):
    """Access check for task"""
    user_id = get_current_user_id()
    
    # Check if user can view this task
    if not user_can_view_task(user_id, task_id, DB_PATH):
        return jsonify({'error': 'Access denied'}), 403
    
    # Proceed with getting task
    conn = get_db_connection()
    task = conn.execute(
        'SELECT * FROM tasks WHERE id = ?',
        (task_id,)
    ).fetchone()
    conn.close()
    
    return jsonify(dict(task))
```

---

## Endpoints to Protect

### Immediate Priority (High Risk)

1. **GET /api/hierarchy/full** - Add `@super_admin_only(DB_PATH)`
2. **GET /api/coordinator/<coordinator_id>/details** - Add coordinator access check
3. **GET /api/projects** - Replace with filtered query
4. **GET /api/projects/<project_id>** - Add access check
5. **GET /api/tasks** - Replace with filtered query
6. **GET /api/tasks/<task_id>** - Add access check
7. **GET /api/daily-reports** - Already has filtering, verify it's correct

### Medium Priority

1. **GET /api/coordinator/eligible-team-members/<project_id>** - Verify coordinator can only see their project
2. **POST /api/coordinator/add-team-members/<project_id>** - Verify coordinator ownership
3. **DELETE /api/coordinator/remove-team-member/<project_id>/<user_id>** - Verify coordinator ownership

### Lower Priority

1. Dashboard stats endpoints - Verify role-based calculations
2. Project creation - Verify creator becomes coordinator or assignment
3. Task assignment - Verify coordinator can only assign to their team

---

## Query Optimization Examples

### Before: Showing all projects

```python
@app.route('/api/projects')
def get_all_projects():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    return jsonify([dict(p) for p in projects])
    # PROBLEM: Shows all projects to everyone!
```

### After: Role-based filtering

```python
@app.route('/api/projects')
@login_required
def get_filtered_projects_endpoint():
    user_id = get_current_user_id()
    projects = get_filtered_projects(user_id, DB_PATH)
    return jsonify(projects)
    # SECURE: Each role sees only their projects
```

---

## Testing Your Authorization

### Test 1: Super Admin Access

```bash
# Login as Super Admin
# Request: GET /api/hierarchy/full
# Expected: 200 OK with full hierarchy

# Request: GET /api/projects
# Expected: 200 OK with ALL projects
```

### Test 2: Coordinator Access

```bash
# Login as Project Coordinator (e.g., user_id=5)
# Request: GET /api/projects
# Expected: 200 OK with only projects where project_coordinator_id=5

# Request: GET /api/projects/<OTHER_COORDINATOR_PROJECT>
# Expected: 403 Forbidden
```

### Test 3: Team Member Access

```bash
# Login as Team Member (e.g., user_id=10)
# Request: GET /api/projects
# Expected: 200 OK with only projects they're assigned to

# Request: GET /api/tasks
# Expected: 200 OK with only tasks assigned_to_id=10

# Request: GET /api/coordinator/team
# Expected: 403 Forbidden
```

---

## Database Schema Requirements

Your existing schema already supports authorization:

```sql
-- Users table (already exists)
users (id, username, email, user_type_id, parent_user_id)

-- Hierarchy maintained via parent_user_id:
-- Super Admin: parent_user_id = NULL
-- Coordinator: parent_user_id = Super Admin ID
-- Team Member: parent_user_id = Coordinator ID

-- Projects table (needs coordinator assignment)
projects (id, title, project_coordinator_id, ...)

-- Team assignments
project_team_members (project_id, user_id)

-- Tasks (already has hierarchy)
tasks (id, title, project_id, assigned_to_id, created_by_id, ...)
```

---

## Error Messages (User Friendly)

```python
# 403 Forbidden - Access Denied
{
    "error": "Access denied to this project",
    "code": "ACCESS_DENIED"
}

# 403 Forbidden - Role Required
{
    "error": "Coordinator access required",
    "code": "ROLE_REQUIRED"
}

# 404 Not Found (if resource doesn't exist for user)
{
    "error": "Resource not found",
    "code": "NOT_FOUND"
}
```

---

## Troubleshooting

### Issue: "Access denied" appears for valid user

**Check:**
1. Is user_id in session correctly?
2. Is user_type correctly set in login?
3. Is parent_user_id correctly set in database?
4. Run: `SELECT id, username, user_type_id, parent_user_id FROM users;`

### Issue: Coordinator can't see their projects

**Check:**
1. Is `project_coordinator_id` set in projects table?
2. Run: `SELECT id, title, project_coordinator_id FROM projects WHERE project_coordinator_id = 5;`
3. Verify coordinator's ID matches

### Issue: Team member sees all tasks

**Check:**
1. Is task filtering working?
2. Run: `SELECT id, title, assigned_to_id FROM tasks WHERE assigned_to_id = 10;`
3. Verify task assignment is correct

---

## Deployment Checklist

- [ ] Import authorization middleware into app.py
- [ ] Test 1-2 endpoints with authorization
- [ ] Verify Super Admin still has full access
- [ ] Test Coordinator sees only their projects
- [ ] Test Team Member sees only assigned tasks
- [ ] Test cross-role denials (Coordinator can't see other coordinator's projects)
- [ ] Test API error responses are secure (don't leak data)
- [ ] Update frontend to handle 403 responses gracefully
- [ ] Monitor logs for authorization violations
- [ ] Document any custom roles or exceptions

---

## Security Notes

1. **No Authentication Changed:** Login process remains unchanged
2. **Database Level:** Queries are filtered at DB level (not just frontend hiding)
3. **Session Validation:** Check `get_current_user_id()` always returns valid user
4. **Role Caching:** Consider caching role lookups if performance becomes issue
5. **Audit Logging:** Consider logging denied access attempts

---

## Next Steps

1. Copy `/scripts/authorization_middleware.py` functions into your app.py or import as module
2. Start with highest-risk endpoints (hierarchy, project listing)
3. Add access checks incrementally
4. Test thoroughly before deploying to production
5. Monitor for any authorization-related errors in logs
