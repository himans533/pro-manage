# Project Coordinator Assignment - Verification Checklist

## Pre-Implementation Verification

### ✅ System Requirements Check

- [ ] SQLite 3.x installed and working
- [ ] Python 3.6+ environment
- [ ] Flask running
- [ ] Database file accessible: `AdminLoginPanel/project_management.db`
- [ ] Project Coordinator usertype exists in database
- [ ] At least one user with Project Coordinator role exists
- [ ] Admin access to modify files

### ✅ Documentation Review

- [ ] README.md read and understood
- [ ] COORDINATOR_QUICK_START.md reviewed
- [ ] Selected appropriate guide for experience level
- [ ] Understand 3-step implementation process
- [ ] Know where to insert HTML code
- [ ] Understand database migration

---

## Implementation Verification

### Phase 1: Database Migration

**File:** `scripts/add_project_coordinator.sql`

**Steps to verify:**
1. [ ] Script file exists and is readable
2. [ ] Backup created: `project_management.db.backup`
3. [ ] Migration executed without errors:
   ```bash
   sqlite3 AdminLoginPanel/project_management.db < scripts/add_project_coordinator.sql
   ```
4. [ ] No "already exists" errors (OK - means idempotent)
5. [ ] Column added successfully

**Verification queries:**
```sql
-- Check column exists
☐ PRAGMA table_info(projects);
   (Should show: project_coordinator_id | INTEGER | 0 | | 0)

-- Check foreign key
☐ PRAGMA foreign_key_list(projects);
   (Should show: FK to users.id)

-- Check index
☐ SELECT name FROM sqlite_master WHERE type='index' AND name LIKE '%coordinator%';
   (Should return: idx_project_coordinator_id)

-- Test NULL default
☐ INSERT INTO projects (title, created_by_id) VALUES ('Test', 1);
SELECT project_coordinator_id FROM projects WHERE title='Test';
   (Should return: NULL)
```

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Phase 2: Frontend Integration

**File:** `AdminLoginPanel/templates/admin-dashboard.html`

**Location:** After line 2662 (after projReportingTime form-group)

**Verification steps:**

1. [ ] HTML dropdown inserted correctly
2. [ ] File saved without syntax errors
3. [ ] Check for required ID: `projCoordinator`
4. [ ] Verify form-group class applied
5. [ ] Helper text present and readable
6. [ ] No CSS conflicts

**Verification queries:**
```html
<!-- Check dropdown exists -->
☐ Search for: id="projCoordinator"
   (Should find exactly 1 match)

<!-- Check label exists -->
☐ Search for: "Assign Project Coordinator"
   (Should find the label)

<!-- Check default option -->
☐ Search for: "-- Select a Project Coordinator --"
   (Should find the placeholder option)
```

**JavaScript Functions Verification:**

```javascript
// Check function exists
☐ Search for: function loadProjectCoordinators()
   (Should find the function definition)

// Check API call
☐ Search for: /api/project-coordinators
   (Should find in fetch call)

// Check projectDraft modification
☐ Search for: projectDraft.project_coordinator_id
   (Should find assignment)

// Check payload inclusion
☐ Search for: project_coordinator_id: projectDraft.project_coordinator_id
   (Should find in finalizeProject payload)
```

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Phase 3: Backend Integration

**File:** `AdminLoginPanel/app.py`

**Verification steps:**

1. [ ] New endpoint added
2. [ ] @admin_required decorator present
3. [ ] SQL query returns Project Coordinator users
4. [ ] Response JSON formatted correctly
5. [ ] create_employee_project() accepts coordinator_id
6. [ ] Coordinator validation logic added
7. [ ] INSERT statement includes coordinator_id
8. [ ] get_admin_projects() query updated
9. [ ] LEFT JOIN to users for coordinator name
10. [ ] No syntax errors in file

**Verification queries:**
```python
# Check endpoint exists
☐ Search for: @app.route("/api/project-coordinators", methods=["GET"])
   (Should find the endpoint)

# Check authorization
☐ Search for: @admin_required above endpoint
   (Should find the decorator)

# Check coordinator validation
☐ Search for: user_type_id = ut.id
   (Should find usertype join)

# Check coordinator assignment in INSERT
☐ Search for: (title, description, ..., project_coordinator_id)
   (Should find column name)

# Check updated query
☐ Search for: LEFT JOIN users uc ON p.project_coordinator_id = uc.id
   (Should find the join)
```

**Verification Result:** ☐ PASS / ☐ FAIL

---

## Functional Testing

### Test 1: Endpoint Availability

**Objective:** Verify `/api/project-coordinators` endpoint works

**Steps:**
```bash
☐ curl http://localhost:5000/api/project-coordinators
  (Should return: 200 OK with JSON array)

☐ Check response has proper structure:
  [
    {"id": X, "username": "...", "email": "...", "department": "..."},
    ...
  ]
```

**Expected Result:** 
- Status: 200 OK
- Content-Type: application/json
- Returns list of coordinators

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 2: Project Creation Without Coordinator

**Objective:** Verify backward compatibility

**Steps:**
1. [ ] Open Create Project modal
2. [ ] Fill in basic details (title, description, deadline)
3. [ ] Leave Project Coordinator dropdown empty
4. [ ] Submit form
5. [ ] Verify success message

**Database Verification:**
```sql
☐ SELECT project_coordinator_id FROM projects 
  WHERE title='<test-title>';
  (Should return: NULL)
```

**Expected Result:**
- Project created successfully
- `project_coordinator_id = NULL` in database
- No errors or warnings

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 3: Project Creation WITH Coordinator

**Objective:** Verify coordinator assignment works

**Steps:**
1. [ ] Open Create Project modal
2. [ ] Fill in basic details
3. [ ] Select a Project Coordinator from dropdown
4. [ ] Submit form
5. [ ] Verify success message

**Database Verification:**
```sql
☐ SELECT project_coordinator_id FROM projects 
  WHERE title='<test-title>';
  (Should return: <coordinator_id>)

☐ SELECT u.username FROM projects p
  LEFT JOIN users u ON p.project_coordinator_id = u.id
  WHERE p.id=<project_id>;
  (Should return: coordinator username)
```

**Expected Result:**
- Project created successfully
- `project_coordinator_id` is set correctly
- Coordinator name matches selection

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 4: Invalid Coordinator Handling

**Objective:** Verify validation works

**Steps:**
1. [ ] Manually send API request with invalid coordinator_id
   ```bash
   curl -X POST http://localhost:5000/api/employee/projects \
     -H "Content-Type: application/json" \
     -d '{"title": "Test", "project_coordinator_id": 99999}'
   ```
2. [ ] Verify request handled gracefully
3. [ ] Check database doesn't store invalid ID

**Expected Result:**
- Invalid coordinator rejected or set to NULL
- No database errors
- Request completes successfully

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 5: Admin Dashboard Display

**Objective:** Verify coordinator info displayed correctly

**Steps:**
1. [ ] Create project with coordinator
2. [ ] Navigate to admin dashboard
3. [ ] View projects list
4. [ ] Check project shows coordinator name

**Expected Result:**
- Coordinator name displays in projects table
- All project information correct
- No display errors

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 6: Dropdown Population

**Objective:** Verify dropdown only shows Project Coordinators

**Steps:**
1. [ ] Open Create Project modal
2. [ ] Wait for dropdown to load
3. [ ] Verify no duplicate entries
4. [ ] Check all entries are Project Coordinator users
5. [ ] Verify count matches database

**Database Verification:**
```sql
☐ SELECT COUNT(*) FROM users u
  INNER JOIN usertypes ut ON u.user_type_id = ut.id
  WHERE ut.user_role = 'Project Coordinator';
  (Should match number of dropdown options - 1 for blank)
```

**Expected Result:**
- Dropdown loads successfully
- Shows only Project Coordinators
- No errors in console
- Count matches database

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 7: Query Projects by Coordinator

**Objective:** Verify querying works correctly

**Steps:**
```sql
☐ SELECT COUNT(*) FROM projects 
  WHERE project_coordinator_id = 2;

☐ SELECT p.title, u.username FROM projects p
  LEFT JOIN users u ON p.project_coordinator_id = u.id
  WHERE p.project_coordinator_id = 2;

☐ Verify results match created projects
```

**Expected Result:**
- Queries return correct results
- Coordinator names displayed
- Count matches expectations

**Verification Result:** ☐ PASS / ☐ FAIL

---

## Performance Testing

### Test 8: Index Performance

**Objective:** Verify index is used and queries are fast

**Steps:**
```sql
☐ EXPLAIN QUERY PLAN
  SELECT * FROM projects WHERE project_coordinator_id = 2;
  (Should show: SEARCH projects USING idx_project_coordinator_id)

☐ Run query multiple times
  SELECT * FROM projects WHERE project_coordinator_id = 2;
  (Should complete instantly)
```

**Expected Result:**
- Query uses index
- Response time < 100ms even with large dataset
- No table scans

**Verification Result:** ☐ PASS / ☐ FAIL

---

## Data Integrity Testing

### Test 9: Foreign Key Constraint

**Objective:** Verify foreign key prevents invalid assignments

**Steps:**
```sql
☐ Try to insert invalid coordinator:
  INSERT INTO projects (title, created_by_id, project_coordinator_id)
  VALUES ('Test', 1, 99999);
  (Should fail with FK error)

☐ Try to delete coordinator (if FK has CASCADE):
  DELETE FROM users WHERE id = 2;
  (Should cascade or set to NULL based on FK definition)
```

**Expected Result:**
- Invalid coordinator insertion rejected
- FK constraint enforced
- Data integrity maintained

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 10: Data Consistency

**Objective:** Verify data remains consistent

**Steps:**
```sql
☐ Check no orphaned references:
  SELECT p.id, p.project_coordinator_id FROM projects p
  WHERE p.project_coordinator_id NOT IN (SELECT id FROM users)
  AND p.project_coordinator_id IS NOT NULL;
  (Should return: No rows)

☐ Check no invalid user types:
  SELECT u.id, u.username FROM users u
  LEFT JOIN projects p ON u.id = p.project_coordinator_id
  WHERE p.project_coordinator_id IS NOT NULL
  AND u.user_type_id NOT IN (SELECT id FROM usertypes WHERE user_role = 'Project Coordinator');
  (Should return: No rows)
```

**Expected Result:**
- No orphaned references
- All coordinators have correct role
- Data consistent

**Verification Result:** ☐ PASS / ☐ FAIL

---

## Security Testing

### Test 11: Authorization Check

**Objective:** Verify only admins can access coordinator endpoint

**Steps:**
1. [ ] Test without authentication (should fail)
2. [ ] Test with non-admin user (should fail)
3. [ ] Test with admin user (should succeed)

**Expected Result:**
- Non-admin requests rejected with 403
- Admin requests succeed with 200
- Authorization enforced

**Verification Result:** ☐ PASS / ☐ FAIL

---

### Test 12: Input Validation

**Objective:** Verify all inputs validated

**Steps:**
1. [ ] Try with empty coordinator_id (should work - NULL)
2. [ ] Try with non-numeric coordinator_id (should fail gracefully)
3. [ ] Try with SQL injection attempt (should fail)
4. [ ] Try with coordinator that doesn't exist (should handle)

**Expected Result:**
- All malicious inputs rejected
- Graceful error messages
- No SQL injection possible
- Data integrity maintained

**Verification Result:** ☐ PASS / ☐ FAIL

---

## Browser Console Testing

### Test 13: JavaScript Errors

**Objective:** Verify no JavaScript errors

**Steps:**
1. [ ] Open Create Project modal
2. [ ] Open browser developer tools (F12)
3. [ ] Check console for errors
4. [ ] Try to create project
5. [ ] Check console during process

**Expected Result:**
- No errors in console
- No warnings
- Network requests succeed
- Form submission successful

**Verification Result:** ☐ PASS / ☐ FAIL

---

## Final Sign-Off

### Overall Status

**All Tests Completed:**
- [ ] Pre-Implementation: ___/13 Checks
- [ ] Database: ___/5 Tests
- [ ] Frontend: ___/4 Tests
- [ ] Backend: ___/7 Tests
- [ ] Functional: ___/13 Tests

**Overall Result:** ☐ PASS / ☐ FAIL

### Issues Found

```
1. [No issues found]
   ☐ No issues
   ☐ Minor issues (document below)
   ☐ Major issues (requires fixes)

Issue Details:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

### Sign-Off

- **Verified By:** _________________ 
- **Date:** _________________ 
- **Time Spent:** _________________ 
- **Status:** ☐ READY FOR PRODUCTION

---

## Post-Deployment Verification

### 48-Hour Monitoring

After deployment, verify for 48 hours:

- [ ] No database errors in logs
- [ ] No application errors
- [ ] Projects create successfully
- [ ] Coordinators assign correctly
- [ ] Admin dashboard responsive
- [ ] No performance degradation
- [ ] Users report no issues

### Monthly Verification

**First week of each month:**
- [ ] Review database for data integrity
- [ ] Check coordinator assignments are correct
- [ ] Verify no orphaned references
- [ ] Review application logs
- [ ] Check performance metrics

---

## Rollback Plan (If Needed)

If critical issues found:

1. **Stop Application**
   ```bash
   systemctl stop flask-app
   ```

2. **Restore Database**
   ```bash
   cp AdminLoginPanel/project_management.db.backup AdminLoginPanel/project_management.db
   ```

3. **Revert Code**
   ```bash
   git revert <commit-hash>
   ```

4. **Restart Application**
   ```bash
   systemctl start flask-app
   ```

---

## Documentation

- [ ] All verification steps documented
- [ ] Issues recorded if any
- [ ] Sign-off obtained
- [ ] Team notified
- [ ] Documentation updated

---

**Verification Complete!** ✅

Your implementation is verified and ready for use.
