"""
TASK ASSIGNMENT BACKEND SOLUTION
==================================
Filters employees based on project_team_members table.
When a Coordinator creates a task under a milestone, only team members assigned to that project are shown.

BACKEND QUERY FOR FILTERING
============================
Location: /AdminLoginPanel/app.py - Add new endpoint around line 2900

"""

# =============================================================================
# OPTION 1: NEW ENDPOINT - Recommended for clean architecture
# =============================================================================
# Add this NEW endpoint to app.py (around line 2900, before create_employee_task)

@app.route("/api/projects/<int:project_id>/eligible-assignees", methods=["GET"])
@login_required
def get_eligible_task_assignees(project_id):
    """
    Get eligible team members for task assignment in a project.
    
    For Project Coordinators:
    - Returns ONLY users from project_team_members table for this project
    
    For Regular Employees:
    - Returns all employees (backward compatibility)
    
    Response:
    [
        {"id": 1, "username": "John Doe", "email": "john@example.com"},
        {"id": 2, "username": "Jane Smith", "email": "jane@example.com"},
        ...
    ]
    """
    conn = None
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "User ID not found"}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current user's role
        cursor.execute('SELECT user_type FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_type = user['user_type']
        
        # Verify project exists
        cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Project not found"}), 404
        
        # IMPORTANT: Only Project Coordinators get filtered list
        if user_type == 'Project Coordinator':
            # Get only team members assigned to this project
            cursor.execute('''
                SELECT DISTINCT u.id, u.username, u.email
                FROM users u
                INNER JOIN project_team_members ptm ON u.id = ptm.user_id
                WHERE ptm.project_id = ?
                ORDER BY u.username
            ''', (project_id,))
        else:
            # Regular employees see all employees (original behavior)
            cursor.execute('''
                SELECT id, username, email
                FROM users
                WHERE user_type IN ('Employee', 'Project Coordinator')
                ORDER BY username
            ''')
        
        assignees = cursor.fetchall()
        
        # Convert Row objects to dictionaries
        result = [
            {
                'id': row['id'],
                'username': row['username'],
                'email': row['email']
            }
            for row in assignees
        ]
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error fetching eligible assignees: {str(e)}")
        return jsonify({"error": "Failed to fetch eligible assignees"}), 500
    finally:
        if conn:
            conn.close()


# =============================================================================
# OPTION 2: MODIFY EXISTING ENDPOINT - If you prefer minimal changes
# =============================================================================
# Find create_employee_task() around line 2913
# Add this validation BEFORE inserting the task:

# BEFORE INSERTION (around line 3001-3006), add this check:
"""
            # IMPORTANT: If user is Project Coordinator, verify assigned employee is in project_team_members
            if assigned_to_id:
                # Check if user is a coordinator
                cursor.execute('SELECT user_type FROM users WHERE id = ?', (user_id,))
                user = cursor.fetchone()
                
                if user and user['user_type'] == 'Project Coordinator':
                    # Coordinator can only assign from project_team_members
                    cursor.execute('''
                        SELECT 1 FROM project_team_members 
                        WHERE project_id = ? AND user_id = ?
                    ''', (project_id, assigned_to_id))
                    
                    if not cursor.fetchone():
                        return jsonify({
                            "error": "Employee not assigned to this project. "
                                   "Add them to project team members first."
                        }), 403
"""


# =============================================================================
# DATABASE QUERY REFERENCE (SQLite)
# =============================================================================

QUERY_GET_PROJECT_TEAM_MEMBERS = """
SELECT DISTINCT u.id, u.username, u.email
FROM users u
INNER JOIN project_team_members ptm ON u.id = ptm.user_id
WHERE ptm.project_id = ?
ORDER BY u.username
"""

QUERY_GET_COORDINATOR_ELIGIBLE_ASSIGNEES = """
SELECT DISTINCT u.id, u.username, u.email, u.user_type
FROM users u
INNER JOIN project_team_members ptm ON u.id = ptm.user_id
WHERE ptm.project_id = ?
  AND u.user_type = 'Employee'
  AND u.id != ?  -- Exclude current coordinator
ORDER BY u.username
"""

QUERY_VALIDATE_EMPLOYEE_IN_PROJECT_TEAM = """
SELECT 1 FROM project_team_members 
WHERE project_id = ? AND user_id = ?
"""


# =============================================================================
# MIGRATION SUMMARY
# =============================================================================
"""
1. Add new endpoint: GET /api/projects/<project_id>/eligible-assignees
   - Returns filtered list of team members for Coordinators
   - Returns all employees for regular Employees (backward compatible)

2. OR modify: POST /api/employee/tasks validation
   - Add check to ensure Coordinator can only assign from project_team_members

3. Update frontend JavaScript (see task_assignment_frontend_changes.js)
   - Modify loadEmployeesForAssignment() to use new endpoint
   - Filter dropdown dynamically based on selected project
"""
