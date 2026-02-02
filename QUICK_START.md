# User Hierarchy System - Quick Start Card

## ⚡ 5-Minute Setup

### 1️⃣ Apply Migration
```bash
sqlite3 AdminLoginPanel/project_management.db < scripts/add_user_hierarchy.sql
```

### 2️⃣ Verify Installation
```bash
python scripts/test_hierarchy_migration.py
```
**Expected:** ✓ All critical tests passed!

### 3️⃣ Add to Flask App
```python
from scripts.hierarchy_utils import UserHierarchyManager
hierarchy_manager = UserHierarchyManager(DB_PATH)
```

### 4️⃣ Use in Code
```python
team = hierarchy_manager.get_direct_reports(user_id)
```

**Done!** ✅

---

## 🎯 Core Concept (One Sentence)

**A single nullable `parent_user_id` column creates unlimited hierarchy depth where NULL = Super Admin.**

---

## 📋 Database Schema Change

```sql
-- What's New in users table:
ALTER TABLE users ADD COLUMN parent_user_id INTEGER DEFAULT NULL;

-- Self-referential FK:
ALTER TABLE users ADD FOREIGN KEY (parent_user_id) REFERENCES users(id);

-- Performance index:
CREATE INDEX idx_parent_user_id ON users(parent_user_id);
```

---

## 🐍 Python API (7 Methods)

```python
manager = UserHierarchyManager('project_management.db')

# Set hierarchy
manager.set_parent(user_3, parent=user_2)

# Get team
manager.get_direct_reports(manager_id)           # Direct reports only
manager.get_all_subordinates(manager_id)         # Full team (recursive)

# Get reporting line
manager.get_parent_chain(user_id)                # Chain upwards
manager.get_hierarchy_level(user_id)             # Position in hierarchy

# Check relationship
manager.is_subordinate_of(user_4, user_2)        # Boolean check

# Get full org
manager.get_organization_tree()                  # Complete structure
```

---

## 🌐 Flask API (6 Endpoints)

```python
@app.route('/api/hierarchy/team')                    # My team
@app.route('/api/hierarchy/org-chart')              # Full org
@app.route('/api/hierarchy/chain/<id>')             # User's chain
@app.route('/api/hierarchy/manager/<id>')           # User's manager
@app.route('/api/hierarchy/subordinates/<id>')      # All subordinates
@app.route('/api/hierarchy/set-parent/<id>/<pid>', methods=['POST'])  # Set parent
```

---

## 🔍 Key SQL Queries

### Get Super Admins
```sql
SELECT * FROM users WHERE parent_user_id IS NULL;
```

### Get Direct Reports
```sql
SELECT * FROM users WHERE parent_user_id = ?;
```

### Get All Subordinates (Recursive)
```sql
WITH RECURSIVE subs AS (
    SELECT id FROM users WHERE parent_user_id = ?
    UNION ALL
    SELECT u.id FROM users u JOIN subs ON u.parent_user_id = subs.id
)
SELECT * FROM users WHERE id IN (SELECT id FROM subs);
```

### Get Full Org Tree
```sql
WITH RECURSIVE org AS (
    SELECT id, username, parent_user_id, 1 as level FROM users WHERE parent_user_id IS NULL
    UNION ALL
    SELECT u.id, u.username, u.parent_user_id, o.level + 1 FROM users u JOIN org ON u.parent_user_id = o.id
)
SELECT * FROM org ORDER BY level, parent_user_id;
```

---

## 📊 Hierarchy Visual

```
NULL (Super Admin)
├── 1
│   ├── 2
│   │   ├── 3
│   │   └── 4
│   └── 5
└── 6
    └── 7
        └── 8
```

**NULL** = Top level  
**Integer** = Reports to that user

---

## ✅ What's NOT Changed

- ✓ Authentication
- ✓ Permissions
- ✓ User types
- ✓ Projects & tasks
- ✓ Daily reports
- ✓ All existing queries

---

## 🚨 Common Gotchas

❌ **DON'T:** `WHERE parent_user_id = NULL`  
✅ **DO:** `WHERE parent_user_id IS NULL`

❌ **DON'T:** Create circular hierarchy  
✅ **DO:** Check before setting: `is_subordinate_of(parent_id, child_id)`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `docs/README.md` | Navigation hub |
| `docs/IMPLEMENTATION_STEPS.md` | Full setup guide |
| `docs/USER_HIERARCHY_GUIDE.md` | Complete reference |
| `docs/HIERARCHY_QUICK_REFERENCE.md` | Quick lookup |
| `docs/HIERARCHY_VISUAL_GUIDE.md` | Diagrams & examples |

---

## 🆘 Troubleshooting

**Column not found?**  
→ Run: `sqlite3 AdminLoginPanel/project_management.db < scripts/add_user_hierarchy.sql`

**Verification fails?**  
→ Check error message in test output, review [docs/IMPLEMENTATION_STEPS.md#troubleshooting](docs/IMPLEMENTATION_STEPS.md#troubleshooting)

**Query returns nothing?**  
→ Remember: `WHERE parent_user_id IS NULL` (not `= NULL`)

---

## 🎓 Learning Paths

**5 min:** Read this card  
**15 min:** Run `test_hierarchy_migration.py` + read Quick Reference  
**30 min:** Follow Implementation Steps  
**1 hour:** Read Complete Guide + try examples  

---

## 📦 Files Included

```
scripts/
├── add_user_hierarchy.sql          ← Database migration
├── hierarchy_utils.py              ← Python API class
└── test_hierarchy_migration.py     ← Verification script

docs/
├── README.md                       ← Start here
├── IMPLEMENTATION_STEPS.md         ← Setup guide
├── USER_HIERARCHY_GUIDE.md         ← Complete reference
├── HIERARCHY_QUICK_REFERENCE.md    ← Quick lookup
└── HIERARCHY_VISUAL_GUIDE.md       ← Diagrams
```

---

## 🏁 Success Criteria

- ✅ Migration applies without errors
- ✅ Test script passes all checks
- ✅ Can query hierarchy in code
- ✅ Flask endpoints return data
- ✅ No errors in logs

---

## 🚀 You're Ready!

1. Apply migration
2. Run verification
3. Add to Flask app
4. Start using!

**For details:** Read `docs/README.md`  
**For examples:** Check `docs/HIERARCHY_QUICK_REFERENCE.md`  
**For setup:** Follow `docs/IMPLEMENTATION_STEPS.md`

---

## 📞 Need Help?

- **Setup issues?** → Run `test_hierarchy_migration.py`
- **Usage questions?** → See `docs/HIERARCHY_QUICK_REFERENCE.md`
- **Code examples?** → Check `docs/USER_HIERARCHY_GUIDE.md`
- **Visual guide?** → Read `docs/HIERARCHY_VISUAL_GUIDE.md`

---

**Remember:** `parent_user_id = NULL` means Super Admin. Everything else reports to that user ID. 🎯

**Print this card. Keep it handy. Share with your team.** 📌
