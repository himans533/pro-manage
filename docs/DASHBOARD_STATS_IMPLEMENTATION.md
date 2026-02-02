# Dashboard Statistics Implementation Guide

## Overview

This guide covers the implementation of dashboard statistics cards on the Employee Dashboard. The feature displays 5 key metrics calculated from tasks and project deadlines.

## What Gets Added

### 1. Backend Endpoint
New API endpoint: `GET /api/dashboard/stats`

**Returns:**
```json
{
  "success": true,
  "data": {
    "active_projects": 5,
    "pending_projects": 2,
    "active_tasks": 12,
    "pending_tasks": 3,
    "overdue_tasks": 1
  }
}
```

### 2. Frontend Cards
5 responsive dashboard cards showing real-time statistics with:
- Beautiful gradient backgrounds (light mode)
- Accessible dark mode support
- Smooth animations
- Auto-refresh every 30 seconds

### 3. Database Queries
5 SQL queries calculating:
- Active Projects: `status = 'Active'`
- Pending Projects: `status = 'Pending'`
- Active Tasks: `status IN ('In Progress', 'Pending')`
- Pending Tasks: `status = 'Pending'`
- Overdue Tasks: `deadline < TODAY AND status != 'Completed'`

## Implementation Steps

### Step 1: Backend Code (10 min)

1. Open `AdminLoginPanel/app.py`
2. Find line 2745 (before `get_employee_projects()` function)
3. Copy entire backend code from `/scripts/dashboard_stats_backend.py`
4. Paste it before `get_employee_projects()`

**Key imports used:**
- `from datetime import datetime` (already imported)
- `from flask import jsonify` (already imported)

### Step 2: Frontend HTML (5 min)

1. Open `AdminLoginPanel/templates/employee-dashboard.html`
2. Find the section after page header (around line 150-200)
3. Copy entire HTML section from `/scripts/dashboard_stats_cards.html`
4. Paste it right after the main page title, before other content

**Important:** The HTML includes:
- Bootstrap 5 classes for responsive grid
- FontAwesome icons (already in template)
- Embedded CSS styles
- JavaScript for API calls and auto-refresh

## Statistics Calculation Logic

### Active Projects
```sql
WHERE (created_by_id = user_id OR user in project_assignments OR user in project_team_members)
  AND status = 'Active'
```

### Pending Projects
Same query but `status = 'Pending'`

### Active Tasks
```sql
WHERE (assigned_to_id = user_id OR created_by_id = user_id)
  AND status IN ('In Progress', 'Pending')
```

### Pending Tasks
```sql
WHERE (assigned_to_id = user_id OR created_by_id = user_id)
  AND status = 'Pending'
```

### Overdue Tasks
```sql
WHERE (assigned_to_id = user_id OR created_by_id = user_id)
  AND status != 'Completed'
  AND deadline < TODAY
```

## API Endpoint Details

### GET /api/dashboard/stats

**Authentication:** Required (login_required decorator)

**Response:**
- `200 OK`: Returns stats object
- `401 Unauthorized`: User not logged in
- `500 Server Error`: Database error

**Auto-refresh:** Frontend automatically refreshes every 30 seconds

## Responsive Design

| Screen Size | Layout |
|-------------|--------|
| > 1400px | 5 columns (all cards in one row) |
| 1200-1399px | 4 columns (wrap to 2 rows) |
| 768-1199px | 3 columns (tablet layout) |
| 576-767px | 2 columns (mobile layout) |
| < 576px | 1 column (stacked) |

## Styling Features

### Light Mode
- Gradient backgrounds for each card type
- Color-coded by metric type
- White text on colored backgrounds

### Dark Mode
- Solid backgrounds matching dark theme
- Colored left border (4px) indicating card type
- Better contrast for dark environments

## Database Performance Notes

All queries use indexed columns:
- `user_id` in assignments table (indexed)
- `status` in tasks/projects table (use LOWER() for case-insensitive)
- `deadline` in tasks table (indexed)
- `created_by_id` in projects (indexed)

Expected query time: < 100ms per endpoint with proper indexing

## Testing Checklist

- [ ] Backend endpoint returns valid JSON
- [ ] Cards display on page load
- [ ] Numbers update correctly for logged-in user
- [ ] Stats refresh every 30 seconds
- [ ] Light mode displays properly
- [ ] Dark mode displays properly
- [ ] Responsive layout works on all screen sizes
- [ ] Overdue calculation includes past deadlines
- [ ] Active/Pending status filtering works correctly

## Troubleshooting

**Cards show "N/A":**
- Check browser console for errors
- Verify `/api/dashboard/stats` endpoint responds
- Check user is logged in

**Stats not updating:**
- Refresh page
- Check if auto-refresh interval is running
- Clear browser cache

**Wrong numbers:**
- Verify project/task status values in database
- Check deadline format is YYYY-MM-DD
- Ensure user assignments are correct

## Integration Notes

- Works with existing user roles (Employee, Coordinator, Admin)
- Respects user permissions automatically
- Shows only user's own data (no cross-user visibility)
- Compatible with dark mode toggle

## Future Enhancements

- Click cards to filter list view
- Add date range selector
- Export statistics as CSV
- Add trend charts (sparklines)
- Set custom refresh intervals
