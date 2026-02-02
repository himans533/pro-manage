# User Hierarchy - Visual Guide

## Hierarchy Structure

### Basic 3-Level Organization

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Level 1: SUPER ADMIN                                       │
│  Alice (id: 1, parent_user_id: NULL)                       │
│                                                             │
│  ├─ Level 2: PROJECT COORDINATOR                           │
│  │  Bob (id: 2, parent_user_id: 1)                        │
│  │                                                          │
│  │  ├─ Level 3: TEAM MEMBER                                │
│  │  │  Charlie (id: 3, parent_user_id: 2)                 │
│  │  │                                                       │
│  │  └─ Level 3: TEAM MEMBER                                │
│  │     David (id: 4, parent_user_id: 2)                   │
│  │                                                          │
│  └─ Level 2: PROJECT COORDINATOR                           │
│     Eve (id: 5, parent_user_id: 1)                        │
│                                                             │
│     ├─ Level 3: TEAM MEMBER                                │
│     │  Frank (id: 6, parent_user_id: 5)                   │
│     │                                                       │
│     └─ Level 3: TEAM MEMBER                                │
│        Grace (id: 7, parent_user_id: 5)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Database Representation

### Users Table

| id | username | email | parent_user_id | role |
|----|----------|-------|-----------------|------|
| 1 | alice | alice@co.com | NULL | Super Admin |
| 2 | bob | bob@co.com | 1 | Project Coordinator |
| 3 | charlie | charlie@co.com | 2 | Team Member |
| 4 | david | david@co.com | 2 | Team Member |
| 5 | eve | eve@co.com | 1 | Project Coordinator |
| 6 | frank | frank@co.com | 5 | Team Member |
| 7 | grace | grace@co.com | 5 | Team Member |

### Key Pattern

```
parent_user_id = NULL    → Root/Super Admin (Alice)
parent_user_id = 1       → Reports to Alice (Bob, Eve)
parent_user_id = 2       → Reports to Bob (Charlie, David)
parent_user_id = 5       → Reports to Eve (Frank, Grace)
```

## Query Patterns Visualized

### Query 1: Get Direct Reports of Bob

```
Query: SELECT * FROM users WHERE parent_user_id = 2

Result:
    Alice (1)
    ├─ Bob (2) ◄── Query starts here
    │  ├─ Charlie (3) ◄── Returns only these
    │  └─ David (4) ◄── Returns only these
    └─ Eve (5)
       ├─ Frank (6)
       └─ Grace (7)
```

### Query 2: Get All Subordinates of Bob (Recursive)

```
Query: WITH RECURSIVE subs AS (...)
       SELECT * WHERE id IN subordinates

Result:
    Alice (1)
    ├─ Bob (2) ◄── Query starts here
    │  ├─ Charlie (3) ◄── Returns these (direct)
    │  └─ David (4) ◄── Returns these (direct)
    │     ├─ Any subordinates of 3
    │     └─ Any subordinates of 4
    └─ Eve (5)
       ├─ Frank (6)
       └─ Grace (7)
```

### Query 3: Get Parent Chain of Charlie

```
Query: WITH RECURSIVE chain AS (...)
       SELECT * FROM chain ORDER BY level

Result:
    Alice (1)
    ├─ Bob (2)
    │  └─ Charlie (3) ◄── Query starts here
    │     Path: 3 → 2 → 1 → NULL
    │     Returns:
    │     1. Charlie (level 1, parent_user_id: 2)
    │     2. Bob (level 2, parent_user_id: 1)
    │     3. Alice (level 3, parent_user_id: NULL)
    └─ Eve (5)
       ├─ Frank (6)
       └─ Grace (7)
```

### Query 4: Full Organization Tree

```
Query: WITH RECURSIVE org AS (...)
       SELECT * ORDER BY level, parent_user_id

Result (in order):
Level 1: Alice (parent_user_id: NULL)
         │
Level 2: ├─ Bob (parent_user_id: 1)
         └─ Eve (parent_user_id: 1)
         │
Level 3: ├─ Charlie (parent_user_id: 2)
         ├─ David (parent_user_id: 2)
         ├─ Frank (parent_user_id: 5)
         └─ Grace (parent_user_id: 5)
```

## Operation Visualizations

### Operation 1: Set Parent (Assign Manager)

```
BEFORE:
Alice (1)
├─ Bob (2)
└─ Eve (5)
   ├─ Frank (6)
   └─ Grace (7)

Command:
manager.set_parent(frank_id=6, parent_id=2)
OR
UPDATE users SET parent_user_id = 2 WHERE id = 6

AFTER:
Alice (1)
├─ Bob (2)
│  └─ Frank (6) ◄── Moved!
└─ Eve (5)
   └─ Grace (7)
```

### Operation 2: Remove Hierarchy (Make Super Admin)

```
BEFORE:
Alice (1)
├─ Bob (2)
│  └─ Charlie (3)
│     └─ David (4)

Command:
manager.set_parent(charlie_id=3, parent_id=None)
OR
UPDATE users SET parent_user_id = NULL WHERE id = 3

AFTER:
Alice (1)         Charlie (3) ◄── Now independent
├─ Bob (2)        └─ David (4)
└─ ...

Note: David still reports to Charlie
```

## Hierarchy Levels

### Level Determination

```
How to determine hierarchy level:

SELECT * FROM users
- If parent_user_id IS NULL          → Level 1: Super Admin
- If parent_user_id NOT NULL         → Check their parent_user_id
  - If their parent IS NULL          → Level 2: Under Super Admin
  - If their parent NOT NULL         → Level 3 or deeper

Visual:
parent_user_id = NULL   ─→  Level 1 (Super Admin)
        ↓
    (has users with this as parent_user_id)
        ↓
    Level 2 (Coordinators)
        ↓
    (has users with this as parent_user_id)
        ↓
    Level 3 (Team Members)
        ↓
    And so on...
```

## Flask Integration Flowchart

```
┌─────────────────────────────────────────────────────┐
│        Flask Application Request                    │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
GET /team    GET /org-chart   GET /manager/<id>
    │              │              │
    │              │              │
    ▼              ▼              ▼
hierarchy.     hierarchy.     hierarchy.
get_direct_    get_org_       get_parent_
reports()      tree()         chain()
    │              │              │
    │              │              │
    ▼              ▼              ▼
Query DB:      Query DB:      Query DB:
SELECT *       WITH            WITH
FROM users     RECURSIVE       RECURSIVE
WHERE          org AS (...)    chain AS (...)
parent_user_   ...             ...
id = ?
    │              │              │
    │              │              │
    ▼              ▼              ▼
Return       Return         Return
Direct       Full Org       Parent Chain
Reports      Tree           to Super Admin
    │              │              │
    └──────────────┴──────────────┘
                   │
                   ▼
          JSON Response to Client
```

## Data Flow Example

### Scenario: Bob Wants to See His Team

```
1. User Bob Logs In
   ├─ session['user_id'] = 2
   └─ Authenticated

2. Bob Clicks "My Team"
   │
   └─→ GET /api/team
       └─→ user_id = session['user_id'] = 2

3. Flask Route Handler
   │
   └─→ hierarchy.get_direct_reports(2)
       └─→ Python Function

4. Python Function
   │
   └─→ SELECT * FROM users WHERE parent_user_id = 2
       │
       ├─ Charlie (id: 3)
       └─ David (id: 4)

5. Database Returns
   │
   └─→ Cursor with 2 rows

6. Python Converts to List of Dicts
   │
   ├─ {'id': 3, 'username': 'charlie', 'email': '...'}
   └─ {'id': 4, 'username': 'david', 'email': '...'}

7. Flask JSONifies
   │
   └─→ [{'id': 3, ...}, {'id': 4, ...}]

8. Client Receives
   │
   └─→ Bob sees his team: Charlie, David
```

## Complex Query Visualization

### Recursive Query: Find All Subordinates

```
Initial Query:
SELECT id FROM users WHERE parent_user_id = 2 (Bob's direct reports)
Results: 3, 4 (Charlie, David)

First Recursion:
SELECT id FROM users WHERE parent_user_id = 3 OR parent_user_id = 4
Results: (any users under Charlie or David)

Second Recursion:
SELECT id FROM users WHERE parent_user_id = (results from first recursion)
Results: (any users under those)

Continue until no more results...

Final Results Combined:
├─ 3 (Charlie) - direct report
├─ 4 (David) - direct report
├─ Any child of 3
├─ Any child of 4
├─ Any child of children
└─ ...
```

## Performance Characteristics

```
Operation                    Complexity    Indexed?
────────────────────────────────────────────────────
Get direct reports           O(n)          Yes ✓
Get all subordinates         O(n log n)    Yes ✓
Get parent chain             O(h)          Yes ✓
Get hierarchy level          O(h)          Yes ✓
Check subordination          O(n)          Yes ✓
Set parent                   O(1)          Yes ✓
Get org tree                 O(n log n)    Yes ✓

Legend:
n = number of users
h = hierarchy depth
✓ = index on parent_user_id ensures fast lookups
```

## Common Mistakes

### ❌ Mistake 1: Circular Hierarchy

```
Bob (2) → parent_user_id = 3 (Charlie)
Charlie (3) → parent_user_id = 2 (Bob)

CYCLE! Bob reports to Charlie, Charlie reports to Bob.

Solution:
✓ Check before setting:
  if not manager.is_subordinate_of(parent_id, child_id):
      manager.set_parent(child_id, parent_id)
```

### ❌ Mistake 2: Forgetting NULL = Super Admin

```
❌ Query: SELECT * FROM users WHERE parent_user_id = NULL
   Result: No results (NULL comparison)

✓ Query: SELECT * FROM users WHERE parent_user_id IS NULL
   Result: Super Admins (Alice)
```

### ❌ Mistake 3: Not Using Indices

```
❌ Slow query:
   SELECT * FROM users WHERE username = 'bob'
   (No index on username)

✓ Fast query:
   SELECT * FROM users WHERE parent_user_id = 2
   (Index exists on parent_user_id)
```

## Summary

```
┌─────────────────────────────────────────┐
│   User Hierarchy System Summary         │
├─────────────────────────────────────────┤
│                                         │
│ Column: parent_user_id (INT, nullable)  │
│                                         │
│ NULL value        = Super Admin         │
│ Non-null value    = Reports to user ID  │
│                                         │
│ Self-referential foreign key            │
│ Creates unlimited depth hierarchy       │
│                                         │
│ All queries supported via Python API    │
│ or direct SQL with recursion            │
│                                         │
│ Performance optimized with index        │
│ Backward compatible (existing data OK)  │
│                                         │
└─────────────────────────────────────────┘
```
