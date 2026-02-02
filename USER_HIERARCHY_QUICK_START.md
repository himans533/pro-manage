# User Hierarchy Visualization - Quick Start (15 minutes)

## What It Does
Shows organizational hierarchy tree:
```
Super Admin
  ├── Coordinator 1
  │    ├── Team Member 1 → Projects → Milestones → Tasks
  │    └── Team Member 2 → Projects → Milestones → Tasks
  └── Coordinator 2
       ├── Team Member 3 → Projects → Milestones → Tasks
```

## Installation

### Step 1: Backend (5 min)
1. Open `AdminLoginPanel/app.py`
2. Go to line ~2750 (after get_employee_projects function)
3. Copy ALL code from `/scripts/user_hierarchy_backend.py`
4. Paste it into app.py

### Step 2: Frontend - Button (2 min)
1. Open `AdminLoginPanel/templates/admin-dashboard.html`
2. Find `</div>` after line 1928 (end of action-buttons)
3. Add this button before the closing `</div>`:

```html
<div class="action-card">
    <h3><i class="fas fa-sitemap"></i> User Hierarchy</h3>
    <p>View organizational structure and team relationships</p>
    <button class="btn btn-primary" onclick="openHierarchyModal()">View Hierarchy</button>
</div>
```

### Step 3: Frontend - Modal (5 min)
1. Same file: Find `</body>` tag (around line 5500)
2. Copy entire `/scripts/user_hierarchy_modal_insertion.html`
3. Paste BEFORE the `</body>` tag

### Step 4: Restart (1 min)
```bash
# Restart Flask app
python AdminLoginPanel/app.py
```

## Test It (2 min)
1. Login as Super Admin
2. Go to Admin Dashboard
3. Look for "User Hierarchy" button
4. Click it → Modal opens with tree

## That's It!

### Features You Get
✓ Expandable/collapsible tree view  
✓ Search by name or email  
✓ Expand/Collapse All buttons  
✓ Color-coded by role  
✓ Read-only (no edits)  
✓ Mobile responsive  

### Common Issues
- Button not showing? Check you added it to the right place
- Modal not opening? Check browser console for errors
- Tree not loading? Check user is Super Admin (not regular admin)

## Quick Reference: What Each Icon Means

| Icon | Meaning | Color |
|------|---------|-------|
| 👑 | Super Admin | Purple |
| 🎩 | Coordinator | Purple-dark |
| 👤 | Team Member | Green |
| 📁 | Project | Orange |
| 🚩 | Milestone | Orange-light |
| ✓ | Task | Blue |

## Troubleshooting

### Modal not opening?
```javascript
// In browser console, type:
console.log(openHierarchyModal);
// Should not say "undefined"
```

### Tree not loading?
```
Network tab → Click on /api/hierarchy/tree
Check Response status (should be 200, not 403)
If 403 → Not super admin
```

### Button not appearing?
Search for "View Hierarchy" in HTML  
Should be in action-buttons section  

## That's All!
You now have a complete organizational hierarchy viewer. All data is read-only and requires Super Admin access.
