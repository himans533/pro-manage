# Task Assignment - Quick Start (5 minutes)

## What's Being Changed
When Coordinator creates a task, "Assign Employee" dropdown shows **ONLY project team members**.

## The 4 Changes

### 1. Backend Endpoint (15 min) - app.py, line 2900
Copy entire `@app.route("/api/projects/...` function from `task_assignment_backend_solution.py`

### 2. Backend Validation (5 min) - app.py, line 3007
Add the coordinator validation check after assigned user verification

### 3. HTML Attribute (1 min) - employee-dashboard.html, line 2684
Change:
```html
<select id="taskProject" required>
```
To:
```html
<select id="taskProject" required onchange="handleTaskProjectChange(this.value)">
```

### 4. JavaScript Functions (10 min) - employee-dashboard.html, script section
Add `populateTaskAssigneeDropdown()` and `handleTaskProjectChange()` functions from `task_assignment_frontend_changes.js`

## Result
- Coordinator selects project → Dropdown auto-fills with only that project's team members
- Regular employee → Sees all employees (unchanged)
- Backend validates → Can't assign non-team members

## Files Reference
- Backend: `/scripts/task_assignment_backend_solution.py`
- Frontend: `/scripts/task_assignment_frontend_changes.js`
- HTML: `/scripts/task_assignment_html_changes.html`
- Full Guide: `/docs/TASK_ASSIGNMENT_IMPLEMENTATION.md`

## Testing (5 min)
1. Login as Coordinator
2. Create task in a project
3. Select the project
4. Verify: "Assign To" shows only team members
5. Create task ✓

Done!
