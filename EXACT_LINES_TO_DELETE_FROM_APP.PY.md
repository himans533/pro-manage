# Exact Lines to Delete from app.py

## WARNING: Make a Backup First!
```bash
cp AdminLoginPanel/app.py AdminLoginPanel/app.py.backup
```

---

## Function Deletion Guide

### DELETION SET 1: OLD create_daily_report() Function
**Delete from Line 949 to Line 1063 (115 lines)**

**Starts with:**
```python
@app.route('/api/daily-report', methods=['POST'])
@login_required
def create_daily_report():
    """Submit a daily report.
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Replaced by `create_daily_report_unified()`

---

### DELETION SET 2: OLD list_daily_reports() Function
**Delete from Line 1066 to Line 1140 (75 lines)**

**Starts with:**
```python
@app.route('/api/daily-reports', methods=['GET'])
@login_required
def list_daily_reports():
    """List daily reports with filters and pagination. Role-based visibility."""
```

**Ends with:**
```python
    except Exception as e:
        logger.exception('list_daily_reports failed')
```

**Why**: Replaced by `list_daily_reports_unified()`

---

### DELETION SET 3: OLD update_daily_report() Function - VERSION 1
**Delete from Line 1143 to Line 1200 (58 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/<int:report_id>', methods=['PUT'])
@login_required
def edit_daily_report(report_id):
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Replaced by `update_daily_report_unified()`

---

### DELETION SET 4: OLD action_daily_report() Function - VERSION 1
**Delete from Line 1203 to Line 1238 (36 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/<int:report_id>/action', methods=['POST'])
@login_required
def action_daily_report(report_id):
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Replaced by `action_daily_report_unified()`

---

### DELETION SET 5: OLD delete_daily_report() Function - VERSION 1
**Delete from Line 1240 to Line 1262 (23 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/<int:report_id>', methods=['DELETE'])
@login_required
def delete_daily_report(report_id):
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Replaced by `delete_daily_report_unified()`

---

### DELETION SET 6: get_admin_dashboard_stats() Function
**Delete from Line 1455 to Line 1520 (66 lines)**

**Starts with:**
```python
@app.route("/api/admin/dashboard/stats", methods=["GET"])
@login_required
def get_admin_dashboard_stats():
```

**Ends with:**
```python
        return jsonify({"error": str(e)}), 500
```

**Why**: Replaced by `get_dashboard_stats_unified()`

---

### DELETION SET 7: ALL create_daily_report_api() and duplicate routing block
**Delete from Line 1531 to Line 1735 (205 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/submit', methods=['POST'])
@app.route('/api/admin/daily_reports', methods=['POST'])
@login_required
def create_daily_report_api():
    """Submit a daily report.
```

**This includes:**
- `create_daily_report_api()` function
- `list_daily_reports_api()` function  
- `admin_get_daily_reports()` function
- All overlapping route decorators

**Ends with:** The `create_daily_report_api()` function's `except Exception` block

**Why**: Functionality merged into unified versions

---

### DELETION SET 8: DUPLICATE list_daily_reports_api() and surrounding
**Already covered in SET 7**

**Note**: The old `list_daily_reports_api()` is part of the block to delete in SET 7

---

### DELETION SET 9: OLD update_daily_report() Function - VERSION 2
**Delete from Line 1687 to Line 1790 (104 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/<int:report_id>', methods=['PUT'])
@login_required
def update_daily_report(report_id):
```

**This version handles multiple routes:**
```python
@app.route('/api/daily-report/<int:report_id>', methods=['PUT'])
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Duplicate of earlier update function. Unified version kept.

---

### DELETION SET 10: OLD action_daily_report_api() Function
**Delete from Line 1790 to Line 1850 (61 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/<int:report_id>/action', methods=['POST'])
@app.route('/api/daily-reports/<int:report_id>/approve', methods=['POST'])
@app.route('/api/daily-reports/<int:report_id>/reject', methods=['POST'])
@login_required
def action_daily_report_api(report_id):
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Replaced by `action_daily_report_unified()`

---

### DELETION SET 11: OLD delete_daily_report_api() Function
**Delete from Line 1853 to Line 1887 (35 lines)**

**Starts with:**
```python
@app.route('/api/daily-report/<int:report_id>', methods=['DELETE'])
@login_required
def delete_daily_report_api(report_id):
```

**Ends with:**
```python
        return jsonify({'error': str(e)}), 500
```

**Why**: Replaced by `delete_daily_report_unified()`

---

### DELETION SET 12: get_employee_dashboard_stats() Function
**Delete from Line 3453 to Line 3500 (48 lines)**

**Starts with:**
```python
@app.route("/api/employee/dashboard/stats", methods=["GET"])
@login_required
def get_employee_dashboard_stats():
```

**Ends with:**
```python
        return jsonify({"error": str(e)}), 500
```

**Why**: Replaced by `get_dashboard_stats_unified()`

---

## Summary of Deletions

| Set # | Function | Lines | Start | End |
|-------|----------|-------|-------|-----|
| 1 | create_daily_report() | 115 | 949 | 1063 |
| 2 | list_daily_reports() | 75 | 1066 | 1140 |
| 3 | edit_daily_report() | 58 | 1143 | 1200 |
| 4 | action_daily_report() | 36 | 1203 | 1238 |
| 5 | delete_daily_report() | 23 | 1240 | 1262 |
| 6 | get_admin_dashboard_stats() | 66 | 1455 | 1520 |
| 7 | create_daily_report_api() + block | 205 | 1531 | 1735 |
| 9 | update_daily_report() v2 | 104 | 1687 | 1790 |
| 10 | action_daily_report_api() | 61 | 1790 | 1850 |
| 11 | delete_daily_report_api() | 35 | 1853 | 1887 |
| 12 | get_employee_dashboard_stats() | 48 | 3453 | 3500 |
| **TOTAL** | **11 Functions** | **~620 lines** | - | - |

---

## Deletion Procedure (Step by Step)

### Method 1: Manual Deletion (Safe but Tedious)
1. Open `AdminLoginPanel/app.py` in your editor
2. Go to line 949 (Ctrl+G or Cmd+G)
3. Select from line 949 to line 1063 (115 lines)
4. Press Delete
5. Repeat for each deletion set below
6. Save file
7. Test endpoints

### Method 2: Using Find & Replace (Faster)
1. Open `AdminLoginPanel/app.py` 
2. Use Find & Replace (Ctrl+H / Cmd+H)
3. Find: `def create_daily_report():`
4. Replace with: (nothing - delete)
5. Find: `def list_daily_reports():`
6. Replace with: (nothing - delete)
7. Repeat for all 11 functions

### Method 3: Script-Based Deletion (Safest)
```python
# Script to mark lines for deletion (creates a backup first)
import shutil

# Backup
shutil.copy('AdminLoginPanel/app.py', 'AdminLoginPanel/app.py.backup')

# Read file
with open('AdminLoginPanel/app.py', 'r') as f:
    lines = f.readlines()

# Lines to delete (0-indexed)
deletions = [
    (948, 1063),      # Set 1: create_daily_report
    (1065, 1140),     # Set 2: list_daily_reports
    (1142, 1200),     # Set 3: edit_daily_report
    (1202, 1238),     # Set 4: action_daily_report
    (1239, 1262),     # Set 5: delete_daily_report
    (1454, 1520),     # Set 6: get_admin_dashboard_stats
    (1530, 1735),     # Set 7: create_daily_report_api block
    (1686, 1790),     # Set 9: update_daily_report v2
    (1789, 1850),     # Set 10: action_daily_report_api
    (1852, 1887),     # Set 11: delete_daily_report_api
    (3452, 3500),     # Set 12: get_employee_dashboard_stats
]

# Remove duplicates and sort in reverse (so indices don't shift)
deletions.sort(reverse=True)

for start, end in deletions:
    del lines[start:end]

# Write back
with open('AdminLoginPanel/app.py', 'w') as f:
    f.writelines(lines)

print("Deletion complete. Original saved as app.py.backup")
```

---

## Verification After Deletion

### Check 1: Verify Functions Removed
```bash
grep -n "def create_daily_report():" AdminLoginPanel/app.py
# Should return: nothing (file not found / no match)

grep -n "def list_daily_reports():" AdminLoginPanel/app.py
# Should return: nothing

grep -n "def get_employee_dashboard_stats():" AdminLoginPanel/app.py
# Should return: nothing
```

### Check 2: Verify New Functions Added
```bash
grep -n "def create_daily_report_unified():" AdminLoginPanel/app.py
# Should return: line number

grep -n "def list_daily_reports_unified():" AdminLoginPanel/app.py
# Should return: line number

grep -n "def get_dashboard_stats_unified():" AdminLoginPanel/app.py
# Should return: line number
```

### Check 3: Test Endpoints
```bash
# Test create
curl -X POST http://localhost:5000/api/daily-reports \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "work_description": "test", "time_spent": 8}'

# Test list
curl http://localhost:5000/api/daily-reports

# Test dashboard stats
curl http://localhost:5000/api/dashboard/stats
```

---

## If Deletion Goes Wrong

### Rollback Immediately
```bash
cp AdminLoginPanel/app.py.backup AdminLoginPanel/app.py
systemctl restart flask-app
```

### Or Use Git
```bash
git checkout AdminLoginPanel/app.py
```

---

## Notes

- **Line numbers may shift** as you delete each set - verify line numbers after each deletion
- **Order matters** - delete from bottom to top to avoid line number shifts
- **Backup first** - always keep a backup of the original file
- **Test after each set** - delete one set, test, then proceed to next
- **Keep git history** - commit before and after for easy rollback

Good luck! 🚀
