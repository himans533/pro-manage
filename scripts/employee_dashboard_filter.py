# EMPLOYEE DASHBOARD FILTERING FOR PROJECT COORDINATORS
# This code extends the existing get_employee_projects() and get_employee_realtime_projects()
# to filter projects for Project Coordinator users

# ============================================================================
# OPTION 1: MODIFIED get_employee_projects() - For Standard Project List
# ============================================================================
# Location: Around line 2748 in app.py
# Replace the WHERE clause in the existing query

"""
CURRENT CODE (lines 2760-2762):
            WHERE (p.created_by_id = ? OR p.id IN (
                SELECT project_id FROM project_assignments WHERE user_id = ?
            ))

UPDATED CODE WITH PROJECT COORDINATOR FILTER:
"""

@app.route("/api/employee/projects", methods=["GET"])
@login_required
def get_employee_projects():
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()

        # NEW: Check if user is a Project Coordinator
        cursor.execute('''
            SELECT ut.user_role FROM users u
            LEFT JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ?
        ''', (user_id,))
        user_role_row = cursor.fetchone()
        user_role = user_role_row['user_role'].lower() if user_role_row else 'employee'
        is_project_coordinator = 'project coordinator' in user_role

        # MODIFIED QUERY: Add coordinator filter
        if is_project_coordinator:
            # Project Coordinators see only projects assigned to them
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
                       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
                FROM projects p 
                LEFT JOIN users u ON p.created_by_id = u.id
                WHERE p.project_coordinator_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))
        else:
            # Non-coordinators see projects where they are creator or assigned
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
                       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
                FROM projects p 
                LEFT JOIN users u ON p.created_by_id = u.id
                WHERE (p.created_by_id = ? OR p.id IN (
                    SELECT project_id FROM project_assignments WHERE user_id = ?
                ))
                ORDER BY p.created_at DESC
            ''', (user_id, user_id))

        projects = cursor.fetchall()
        conn.close()

        return jsonify([dict(row) for row in projects]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OPTION 2: MODIFIED get_employee_realtime_projects() - For Real-time Dashboard
# ============================================================================
# Location: Around line 4762 in app.py
# Replace the WHERE clause in the existing query

"""
CURRENT CODE (lines 4784-4786):
            WHERE (p.created_by_id = ? OR p.id IN (
                SELECT project_id FROM project_assignments WHERE user_id = ?
            )) AND p.status != 'Completed'

UPDATED CODE WITH PROJECT COORDINATOR FILTER:
"""

@app.route("/api/employee/projects/realtime", methods=["GET"])
@login_required
def get_employee_realtime_projects():
    """Get real-time project updates with calculated progress percentage"""
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()

        # NEW: Check if user is a Project Coordinator
        cursor.execute('''
            SELECT ut.user_role FROM users u
            LEFT JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ?
        ''', (user_id,))
        user_role_row = cursor.fetchone()
        user_role = user_role_row['user_role'].lower() if user_role_row else 'employee'
        is_project_coordinator = 'project coordinator' in user_role

        # MODIFIED QUERY: Add coordinator filter
        if is_project_coordinator:
            # Project Coordinators see only projects assigned to them
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status,
                       p.deadline, p.reporting_time, p.created_at, p.updated_at,
                       u.username as creator_name,
                       COUNT(DISTINCT t.id) as total_tasks,
                       SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
                       COUNT(DISTINCT m.id) as total_milestones,
                       SUM(CASE WHEN m.status = 'Completed' THEN 1 ELSE 0 END) as completed_milestones,
                       COUNT(DISTINCT pa.user_id) as team_size
                FROM projects p
                LEFT JOIN users u ON p.created_by_id = u.id
                LEFT JOIN tasks t ON p.id = t.project_id
                LEFT JOIN milestones m ON p.id = m.project_id
                LEFT JOIN project_assignments pa ON p.id = pa.project_id
                WHERE p.project_coordinator_id = ? AND p.status != 'Completed'
                GROUP BY p.id, u.username
                ORDER BY p.updated_at DESC
            ''', (user_id,))
        else:
            # Non-coordinators see projects where they are creator or assigned
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status,
                       p.deadline, p.reporting_time, p.created_at, p.updated_at,
                       u.username as creator_name,
                       COUNT(DISTINCT t.id) as total_tasks,
                       SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks,
                       COUNT(DISTINCT m.id) as total_milestones,
                       SUM(CASE WHEN m.status = 'Completed' THEN 1 ELSE 0 END) as completed_milestones,
                       COUNT(DISTINCT pa.user_id) as team_size
                FROM projects p
                LEFT JOIN users u ON p.created_by_id = u.id
                LEFT JOIN tasks t ON p.id = t.project_id
                LEFT JOIN milestones m ON p.id = m.project_id
                LEFT JOIN project_assignments pa ON p.id = pa.project_id
                WHERE (p.created_by_id = ? OR p.id IN (
                    SELECT project_id FROM project_assignments WHERE user_id = ?
                )) AND p.status != 'Completed'
                GROUP BY p.id, u.username
                ORDER BY p.updated_at DESC
            ''', (user_id, user_id))

        projects = cursor.fetchall()

        # Calculate live progress percentage for each project
        result = []
        for row in projects:
            project_dict = dict(row)
            total_tasks = project_dict.get('total_tasks') or 0
            completed_tasks = project_dict.get('completed_tasks') or 0
            total_milestones = project_dict.get('total_milestones') or 0
            completed_milestones = project_dict.get('completed_milestones') or 0

            # Calculate progress: if no tasks, progress is 0
            if total_tasks > 0:
                progress = int((completed_tasks / total_tasks) * 100)
            elif total_milestones > 0:
                progress = int((completed_milestones / total_milestones) * 100)
            else:
                progress = 0

            project_dict['progress'] = progress
            result.append(project_dict)

        conn.close()
        return jsonify(result), 200
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OPTION 3: HELPER FUNCTION (Recommended for DRY code)
# ============================================================================
# Add this helper function near the top of app.py (around line 550)

def is_user_project_coordinator(user_id):
    """
    Check if a user is a Project Coordinator
    
    Returns:
        bool: True if user role contains 'project coordinator', False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ut.user_role FROM users u
            LEFT JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ?
        ''', (user_id,))
        user_role_row = cursor.fetchone()
        conn.close()
        
        if user_role_row:
            user_role = user_role_row['user_role'].lower()
            return 'project coordinator' in user_role
        return False
    except Exception as e:
        print(f"Error checking if user is project coordinator: {str(e)}")
        return False


# Then refactor the functions to use this helper:
def get_employee_projects_with_helper():
    """Using the helper function - CLEANER APPROACH"""
    try:
        user_id = get_current_user_id()
        is_coordinator = is_user_project_coordinator(user_id)
        conn = get_db_connection()
        cursor = conn.cursor()

        if is_coordinator:
            # Project Coordinators see only their assigned projects
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
                       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
                FROM projects p 
                LEFT JOIN users u ON p.created_by_id = u.id
                WHERE p.project_coordinator_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,))
        else:
            # Regular employees see their created/assigned projects
            cursor.execute(
                '''
                SELECT DISTINCT p.id, p.title, p.description, p.status, p.progress, 
                       p.deadline, p.created_by_id, u.username as creator_name, p.created_at
                FROM projects p 
                LEFT JOIN users u ON p.created_by_id = u.id
                WHERE (p.created_by_id = ? OR p.id IN (
                    SELECT project_id FROM project_assignments WHERE user_id = ?
                ))
                ORDER BY p.created_at DESC
            ''', (user_id, user_id))

        projects = cursor.fetchall()
        conn.close()
        return jsonify([dict(row) for row in projects]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# KEY CHANGES SUMMARY
# ============================================================================
# 1. Added user role check to determine if user is a Project Coordinator
# 2. Added conditional query logic:
#    - If Project Coordinator: Show only projects where project_coordinator_id = user_id
#    - If Regular Employee: Show projects where user is creator or assigned
# 3. Applied same logic to both standard and real-time project endpoints
# 4. No UI changes needed - filtering happens at backend
# 5. Backward compatible - regular employees unaffected

