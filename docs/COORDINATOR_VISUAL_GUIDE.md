# Project Coordinator Assignment - Visual Guide

## Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USERTYPES                            │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ user_role: 'Project Coordinator' | 'Employee' | etc.      │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │ references
                           │
┌─────────────────────────────────────────────────────────────┐
│                         USERS                               │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ username                                                    │
│ email                                                       │
│ user_type_id (FK) ──────────────────► usertypes.id         │
│ department                                                  │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
         ▲                               ▲
         │                               │
    created_by_id              project_coordinator_id
         │                               │
         └───────┬──────────────────────┘
                 │
┌─────────────────────────────────────────────────────────────┐
│                       PROJECTS                              │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ title                                                       │
│ description                                                 │
│ status                                                      │
│ deadline                                                    │
│ created_by_id (FK) ───► users.id                           │
│ project_coordinator_id (FK) ─► users.id  ◄── NEW COLUMN    │
│ created_at                                                  │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
         │
         │ has many
         ▼
┌─────────────────────────────────────────────────────────────┐
│                        TASKS                                │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                     │
│ title                                                       │
│ project_id (FK) ──► projects.id                            │
│ assigned_to_id (FK) ──► users.id                           │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## User Interface Flow

### Create Project Modal - Project Details Step

```
┌──────────────────────────────────────────────────────────────┐
│            Create New Project                    [X]          │
├──────────────────────────────────────────────────────────────┤
│ Step: [1] Project Details [2] Team [3] Milestones [4] Review │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Project Title *                                            │
│  [Enter project title........................]              │
│                                                              │
│  Description                                                │
│  [Enter project description.....................]          │
│                                                              │
│  Deadline                                                   │
│  [____-__-__]                                              │
│                                                              │
│  Reporting Time                                             │
│  [09:00]                                                   │
│                                                              │
│  👤 Assign Project Coordinator        (Optional)  ◄── NEW   │
│  [-- Select a Project Coordinator --  ▼]                   │
│   └─ Coordinator 1 (Engineering)                           │
│   └─ Coordinator 2 (Design)                                │
│   └─ Coordinator 3 (QA)                                    │
│  ℹ️  Select a user with Project Coordinator role           │
│                                                              │
│  Team Members                                               │
│  ☑️ Employee 1  ☑️ Employee 2  ☑️ Employee 3               │
│                                                              │
│                  [Cancel] [Save & Add Milestones]           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

```
admin-dashboard.html (Frontend)
├─ HTML
│  └─ createProjectModal
│     └─ Dropdown: projCoordinator (NEW)
│
├─ JavaScript
│  ├─ loadProjectCoordinators()          (NEW)
│  │  └─ Fetches from /api/project-coordinators
│  │
│  ├─ openHierarchicalProjectModal()     (MODIFIED)
│  │  └─ Calls loadProjectCoordinators()
│  │
│  ├─ saveDraftProject()                 (MODIFIED)
│  │  └─ Captures projCoordinator value
│  │
│  └─ finalizeProject()                  (MODIFIED)
│     └─ Includes project_coordinator_id in payload
│
└─ CSS
   └─ form-group (existing styles work)


app.py (Backend)
├─ /api/project-coordinators              (NEW)
│  └─ Returns list of Project Coordinator users
│
├─ /api/employee/projects [POST]          (MODIFIED)
│  ├─ Validates coordinator_id
│  └─ Stores in database
│
└─ /api/admin/projects [GET]             (MODIFIED)
   └─ Returns coordinator_name in response
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      USER INTERACTION                            │
│                                                                  │
│  Super Admin clicks "Create Project"                             │
│                    ▼                                             │
│  Modal opens → loadProjectCoordinators() called                 │
│                    ▼                                             │
│         API Request to /api/project-coordinators                │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         Backend Processing
                   │
         SELECT FROM users u
         JOIN usertypes ut ON u.user_type_id = ut.id
         WHERE ut.user_role = 'Project Coordinator'
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              API Response (JSON)                                 │
│                                                                  │
│  [                                                               │
│    {"id": 2, "username": "Coordinator 1", "department": "Eng"},│
│    {"id": 3, "username": "Coordinator 2", "department": "Des"},│
│    {"id": 4, "username": "Coordinator 3", "department": "QA"}  │
│  ]                                                               │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         Frontend Processing
                   │
         Populate dropdown with options
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              USER SELECTS COORDINATOR                            │
│                                                                  │
│  Dropdown shows:                                                 │
│  [-- Select a Project Coordinator --]                           │
│   Coordinator 1 (Engineering)    ◄── Selected by user           │
│   Coordinator 2 (Design)                                        │
│   Coordinator 3 (QA)                                            │
│                                                                  │
│  User clicks "Save & Add Milestones"                            │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         Frontend Processing
                   │
         saveDraftProject(event)
         ├─ projectDraft.title = "..."
         ├─ projectDraft.description = "..."
         ├─ projectDraft.deadline = "..."
         ├─ projectDraft.reporting_time = "09:00"
         └─ projectDraft.project_coordinator_id = 2  ◄── NEW
                   │
         finalizeProject()
         ├─ payload.title = "..."
         ├─ payload.description = "..."
         ├─ payload.deadline = "..."
         ├─ payload.reporting_time = "09:00"
         ├─ payload.team_members = [...]
         ├─ payload.milestones = [...]
         └─ payload.project_coordinator_id = 2  ◄── NEW
                   │
         API Request: POST /api/employee/projects
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              BACKEND VALIDATION & STORAGE                        │
│                                                                  │
│  Validate:                                                       │
│  1. Is project_coordinator_id valid? → Query users table        │
│  2. Does coordinator have correct role? → Check usertypes       │
│  3. Does coordinator exist? → Verify ID                         │
│                                                                  │
│  If valid:                                                       │
│    INSERT INTO projects (                                       │
│      title, description, deadline,                              │
│      reporting_time, created_by_id,                             │
│      project_coordinator_id  ◄── STORED                         │
│    ) VALUES (...)                                               │
│                                                                  │
│  If invalid:                                                     │
│    Set project_coordinator_id = NULL                            │
│    (Project created without coordinator)                         │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         API Response
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│              FRONTEND SUCCESS                                    │
│                                                                  │
│  {                                                               │
│    "id": 42,                                                     │
│    "title": "New Project",                                       │
│    "message": "Project created successfully!"                   │
│  }                                                               │
│                                                                  │
│  ✓ Project created with coordinator_id = 2                      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Query Examples & Results

### Query 1: Get Projects by Coordinator

```sql
SELECT p.id, p.title, p.status, p.deadline, u.username as created_by
FROM projects p
LEFT JOIN users u ON p.created_by_id = u.id
WHERE p.project_coordinator_id = 2;
```

**Result:**
```
id | title              | status     | deadline   | created_by
───┼────────────────────┼────────────┼────────────┼───────────
42 | Mobile App Rewrite | In Progress | 2024-06-30 | super_admin
45 | Website Redesign   | Planning   | 2024-07-15 | super_admin
50 | API Integration    | In Progress | 2024-06-20 | coordinator_1
```

---

### Query 2: Projects Without Coordinator

```sql
SELECT p.id, p.title, p.status, u.username as created_by
FROM projects p
LEFT JOIN users u ON p.created_by_id = u.id
WHERE p.project_coordinator_id IS NULL;
```

**Result:**
```
id | title           | status  | created_by
───┼─────────────────┼─────────┼───────────
35 | Legacy Cleanup  | Planning | admin
38 | Bug Fixes       | Active  | admin
```

---

### Query 3: Projects with Coordinator Details

```sql
SELECT 
  p.id, 
  p.title, 
  creator.username as created_by,
  coordinator.username as coordinator,
  p.status
FROM projects p
LEFT JOIN users creator ON p.created_by_id = creator.id
LEFT JOIN users coordinator ON p.project_coordinator_id = coordinator.id
ORDER BY p.created_at DESC;
```

**Result:**
```
id | title           | created_by   | coordinator    | status
───┼─────────────────┼──────────────┼────────────────┼─────────
50 | API Integration | super_admin  | Coordinator 3  | Active
45 | Website Redesign| super_admin  | Coordinator 2  | Planning
42 | Mobile App      | super_admin  | Coordinator 1  | Progress
38 | Bug Fixes       | admin        | (NULL)         | Active
35 | Legacy Cleanup  | admin        | (NULL)         | Planning
```

---

### Query 4: Coordinator Workload

```sql
SELECT 
  coordinator.username,
  COUNT(p.id) as project_count,
  COUNT(CASE WHEN p.status = 'In Progress' THEN 1 END) as active_projects
FROM projects p
LEFT JOIN users coordinator ON p.project_coordinator_id = coordinator.id
GROUP BY p.project_coordinator_id
ORDER BY project_count DESC;
```

**Result:**
```
username      | project_count | active_projects
──────────────┼───────────────┼────────────────
Coordinator 1 |             5 |               3
Coordinator 2 |             4 |               2
Coordinator 3 |             3 |               1
(NULL)        |             2 |               1
```

---

## API Endpoint Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     NEW ENDPOINT                            │
├─────────────────────────────────────────────────────────────┤
│ GET /api/project-coordinators                              │
│                                                             │
│ Authentication: @admin_required                            │
│                                                             │
│ Response:                                                  │
│ [                                                          │
│   {                                                        │
│     "id": 2,                                              │
│     "username": "john_coordinator",                        │
│     "email": "john@company.com",                          │
│     "department": "Engineering"                           │
│   },                                                       │
│   {                                                        │
│     "id": 3,                                              │
│     "username": "sarah_coordinator",                       │
│     "email": "sarah@company.com",                         │
│     "department": "Design"                                │
│   }                                                        │
│ ]                                                         │
│                                                             │
│ Status Codes:                                              │
│ 200 - Success, coordinators returned                      │
│ 403 - Unauthorized (not admin)                            │
│ 500 - Server error                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Status Checklist

```
DATABASE
  ✓ Column added: project_coordinator_id
  ✓ Foreign key constraint created
  ✓ Index created for performance
  
FRONTEND
  □ HTML dropdown inserted
  □ loadProjectCoordinators() function added
  □ saveDraftProject() modified
  □ finalizeProject() modified
  
BACKEND
  □ /api/project-coordinators endpoint created
  □ create_employee_project() modified
  □ get_admin_projects() query updated
  
TESTING
  □ Create project without coordinator
  □ Create project with coordinator
  □ Verify database stores value
  □ Verify dropdown shows correct users
  □ Verify API returns coordinators
  
DEPLOYMENT
  □ Database backed up
  □ Migration applied
  □ Code changes deployed
  □ Tests passed in production
```

---

## Timeline View

```
Time →

 Minute 0: Drop-down loads          ◄─ loadProjectCoordinators()
           │
           ▼
 Minute ~50ms: API returns coordinators ◄─ /api/project-coordinators

           ✓ Dropdown populated

           │ User selects coordinator
           ▼

 Minute 2000ms: Form submitted       ◄─ finalizeProject()

           ✓ Data sent to backend

           │
           ▼

 Minute 2100ms: Backend validates coordinator

           ✓ Validation passed

           │
           ▼

 Minute 2150ms: Project inserted into DB
           │
           ├─ INSERT INTO projects
           │  (title, ..., project_coordinator_id)
           │
           ▼

 Minute 2200ms: Response returned   ◄─ Success

           ✓ Modal closes
           ✓ Project appears in list
           ✓ Coordinator assigned
```

---

## Error Handling Flow

```
User selects invalid coordinator
            │
            ▼
Form submitted with invalid ID
            │
            ▼
Backend validation:
  │
  ├─ Is ID integer? → NO → Set to NULL
  │
  ├─ Does user exist? → NO → Set to NULL
  │
  ├─ Has correct role? → NO → Set to NULL
  │
  └─ All checks pass? → YES → Use coordinator_id
            │
            ▼
Project created:
  │
  ├─ If valid: coordinator_id = selected ID
  │
  └─ If invalid: coordinator_id = NULL
            │
            ▼
Success response (either way)
Project still created, with or without coordinator
```

---

## Summary

The Project Coordinator Assignment system is fully integrated with:
- Clean database schema with proper constraints
- Intuitive user interface with dropdown selection
- Robust backend validation and error handling
- Backward compatibility (existing projects unaffected)
- Performance optimization through indexing
