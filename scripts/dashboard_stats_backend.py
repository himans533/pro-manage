"""
DASHBOARD STATISTICS ENDPOINT
File: AdminLoginPanel/app.py
Add this route around line 2745 (before get_employee_projects)

This endpoint provides dashboard statistics for employees and coordinators:
- Active Projects (status = 'Active')
- Pending Projects (status = 'Pending')
- Active Tasks (status = 'In Progress' or 'Pending')
- Pending Tasks (status = 'Pending')
- Overdue Tasks (deadline < TODAY and status != 'Completed')
"""

from datetime import datetime
from flask import jsonify

# ============================================================================
# ENDPOINT: GET /api/dashboard/stats
# ============================================================================

@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def get_dashboard_stats():
    """
    Get dashboard statistics for the logged-in user.
    Returns counts for:
    - Active Projects
    - Pending Projects
    - Active Tasks
    - Pending Tasks
    - Overdue Tasks
    """
    conn = None
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "User ID not found"}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get today's date for overdue calculation
        today = datetime.now().strftime('%Y-%m-%d')
        
        # ====================================================================
        # COUNT 1: ACTIVE PROJECTS
        # Status = 'Active'
        # User is creator OR assigned to project
        # ====================================================================
        cursor.execute('''
            SELECT COUNT(DISTINCT p.id) as count
            FROM projects p
            WHERE (p.created_by_id = ? OR p.id IN (
                SELECT project_id FROM project_assignments WHERE user_id = ?
                UNION
                SELECT project_id FROM project_team_members WHERE user_id = ?
            ))
            AND LOWER(p.status) = 'active'
        ''', (user_id, user_id, user_id))
        active_projects = cursor.fetchone()['count'] or 0
        
        # ====================================================================
        # COUNT 2: PENDING PROJECTS
        # Status = 'Pending'
        # User is creator OR assigned to project
        # ====================================================================
        cursor.execute('''
            SELECT COUNT(DISTINCT p.id) as count
            FROM projects p
            WHERE (p.created_by_id = ? OR p.id IN (
                SELECT project_id FROM project_assignments WHERE user_id = ?
                UNION
                SELECT project_id FROM project_team_members WHERE user_id = ?
            ))
            AND LOWER(p.status) = 'pending'
        ''', (user_id, user_id, user_id))
        pending_projects = cursor.fetchone()['count'] or 0
        
        # ====================================================================
        # COUNT 3: ACTIVE TASKS
        # Status = 'In Progress' or 'Pending'
        # Task assigned to user OR created by user
        # ====================================================================
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM tasks t
            WHERE (t.assigned_to_id = ? OR t.created_by_id = ?)
            AND LOWER(t.status) IN ('in progress', 'pending')
        ''', (user_id, user_id))
        active_tasks = cursor.fetchone()['count'] or 0
        
        # ====================================================================
        # COUNT 4: PENDING TASKS
        # Status = 'Pending'
        # Task assigned to user OR created by user
        # ====================================================================
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM tasks t
            WHERE (t.assigned_to_id = ? OR t.created_by_id = ?)
            AND LOWER(t.status) = 'pending'
        ''', (user_id, user_id))
        pending_tasks = cursor.fetchone()['count'] or 0
        
        # ====================================================================
        # COUNT 5: OVERDUE TASKS
        # Deadline < TODAY and Status != 'Completed'
        # Task assigned to user OR created by user
        # ====================================================================
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM tasks t
            WHERE (t.assigned_to_id = ? OR t.created_by_id = ?)
            AND LOWER(t.status) != 'completed'
            AND t.deadline < ?
        ''', (user_id, user_id, today))
        overdue_tasks = cursor.fetchone()['count'] or 0
        
        conn.close()
        
        return jsonify({
            "success": True,
            "data": {
                "active_projects": active_projects,
                "pending_projects": pending_projects,
                "active_tasks": active_tasks,
                "pending_tasks": pending_tasks,
                "overdue_tasks": overdue_tasks
            }
        }), 200
        
    except Exception as e:
        if conn:
            conn.close()
        print(f"[ERROR] /api/dashboard/stats failed: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# HELPER FUNCTION: Get today's date
# ============================================================================

def get_today():
    """Return today's date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')
