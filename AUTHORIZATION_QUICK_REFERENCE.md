# Authorization System - Quick Reference

## One-Liner Rules

- **Super Admin** → Sees `*` (everything)
- **Project Coordinator** → Sees `projects WHERE project_coordinator_id = me` + `tasks IN my_projects` + `team WHERE parent_user_id = me`
- **Team Member** → Sees `tasks WHERE assigned_to_id = me` only

---

## Copy-Paste Decorators

### Only Super Admin
```python
@super_admin_only(DB_PATH)
def endpoint():
    return jsonify({'data': 'super admin only'})
```

### Coordinator or Admin
```python
@coordinator_or_admin(DB_PATH)
def endpoint():
    return jsonify({'data': 'coordinator+'})
```

---

## Copy-Paste Checks

### Check Project Access
```python
if not user_can_view_project(user_id, project_id, DB_PATH):
    return jsonify({'error': 'Access denied'}), 403
```

### Check Task Access
```python
if not user_can_view_task(user_id, task_id, DB_PATH):
    return jsonify({'error': 'Access denied'}), 403
```

### Filter Projects by Role
```python
projects = get_filtered_projects(user_id, DB_PATH)
```

### Filter Tasks by Role
```python
tasks = get_filtered_tasks(user_id, DB_PATH)
```

### Filter Team Members by Role
```python
team = get_filtered_team_members(user_id, DB_PATH)
```

---

## Test Cases

### Super Admin Test
```
Login as Super Admin
GET /api/projects → See ALL projects ✓
GET /api/hierarchy/full → See full hierarchy ✓
```

### Coordinator Test
```
Login as Coordinator (user_id=5)
GET /api/projects → See ONLY projects where project_coordinator_id=5 ✓
GET /api/projects/99 (other coordinator) → 403 Forbidden ✓
GET /api/coordinator/team → See ONLY team where parent_user_id=5 ✓
```

### Team Member Test
```
Login as Team Member (user_id=10)
GET /api/tasks → See ONLY tasks where assigned_to_id=10 ✓
GET /api/coordinator/team → 403 Forbidden ✓
GET /api/hierarchy/full → 403 Forbidden ✓
```

---

## Integration Checklist

- [ ] Import middleware into app.py
- [ ] Add `@super_admin_only(DB_PATH)` to hierarchy endpoints
- [ ] Add `@coordinator_or_admin(DB_PATH)` to coordinator endpoints
- [ ] Replace project queries with `get_filtered_projects()`
- [ ] Replace task queries with `get_filtered_tasks()`
- [ ] Add access checks to specific resource endpoints
- [ ] Test with 3 different user roles
- [ ] Verify 403 responses are returned correctly
- [ ] Check logs for errors

---

## File Locations

- **Middleware**: `/scripts/authorization_middleware.py` (516 lines)
- **Full Guide**: `/docs/AUTHORIZATION_IMPLEMENTATION_GUIDE.md` (390 lines)
- **This File**: `/AUTHORIZATION_QUICK_REFERENCE.md`
