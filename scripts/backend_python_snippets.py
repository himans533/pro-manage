# ============================================================================
# BACKEND CODE SNIPPETS FOR PROJECT COORDINATOR ASSIGNMENT
# ============================================================================
# Location: AdminLoginPanel/app.py
# These snippets should be integrated into the existing project creation logic
# ============================================================================

# ============================================================================
# SNIPPET 1: Add this to the get_admin_projects() route (around line 3769)
# To include project_coordinator_id in the response
# ============================================================================

# MODIFY this query in get_admin_projects():
# FROM:
"""
SELECT p.id, p.title, p.description, p.status, p.progress,
p.deadline, p.created_by_id, u.username as creator_name,
p.created_at, COUNT(DISTINCT pa.user_id) as team_count,
COUNT(DISTINCT t.id) as task_count
FROM projects p
LEFT JOIN users u ON p.created_by_id = u.id
LEFT JOIN project_assignments pa ON p.id = pa.project_id
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, u.username
ORDER BY p.created_at DESC
"""

# TO:
"""
SELECT p.id, p.title, p.description, p.status, p.progress,
p.deadline, p.created_by_id, u.username as creator_name,
p.project_coordinator_id, uc.username as coordinator_name,
p.created_at, COUNT(DISTINCT pa.user_id) as team_count,
COUNT(DISTINCT t.id) as task_count
FROM projects p
LEFT JOIN users u ON p.created_by_id = u.id
LEFT JOIN users uc ON p.project_coordinator_id = uc.id
LEFT JOIN project_assignments pa ON p.id = pa.project_id
LEFT JOIN tasks t ON p.id = t.project_id
GROUP BY p.id, u.username, uc.username
ORDER BY p.created_at DESC
"""


# ============================================================================
# SNIPPET 2: NEW ENDPOINT - Get available Project Coordinators
# Add this BEFORE the create_employee_project() function (around line 2773)
# ============================================================================

@app.route("/api/project-coordinators", methods=["GET"])
@admin_required
def get_project_coordinators():
    """
    Get all users with 'Project Coordinator' role for dropdown assignment.
    Returns only users who have been granted the Project Coordinator usertype.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all users with 'Project Coordinator' usertype
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.department
            FROM users u
            INNER JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE ut.user_role = 'Project Coordinator'
            ORDER BY u.username ASC
        ''')
        
        coordinators = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': row['id'],
            'username': row['username'],
            'email': row['email'],
            'department': row['department'] or 'Not Specified'
        } for row in coordinators]), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# SNIPPET 3: MODIFY create_employee_project() function
# Location: Around line 2804-2808
# ============================================================================

# MODIFY the INSERT statement:
# FROM:
"""
cursor.execute(
    '''
    INSERT INTO projects (title, description, deadline, reporting_time, created_by_id)
    VALUES (?,?,?,?,?)
''', (title, description, deadline or None, reporting_time, user_id))
"""

# TO:
"""
# Get project_coordinator_id from request
project_coordinator_id = data.get("project_coordinator_id")

# Validate coordinator if provided
if project_coordinator_id:
    try:
        project_coordinator_id = int(project_coordinator_id)
        # Verify coordinator exists and has correct role
        cursor.execute('''
            SELECT u.id FROM users u
            INNER JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ? AND ut.user_role = 'Project Coordinator'
        ''', (project_coordinator_id,))
        if not cursor.fetchone():
            project_coordinator_id = None  # Invalid coordinator, ignore
    except (ValueError, TypeError):
        project_coordinator_id = None

cursor.execute(
    '''
    INSERT INTO projects 
    (title, description, deadline, reporting_time, created_by_id, project_coordinator_id)
    VALUES (?,?,?,?,?,?)
''', (title, description, deadline or None, reporting_time, user_id, project_coordinator_id))
"""


# ============================================================================
# SNIPPET 4: OPTIONAL - Add helper function to get coordinator's projects
# Add this somewhere in app.py for utility purposes
# ============================================================================

def get_coordinator_projects(coordinator_id):
    """
    Get all projects assigned to a specific Project Coordinator.
    Useful for the coordinator dashboard to see their assigned projects.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.title, p.description, p.status, p.progress,
                   p.deadline, p.created_at, u.username as created_by
            FROM projects p
            LEFT JOIN users u ON p.created_by_id = u.id
            WHERE p.project_coordinator_id = ?
            ORDER BY p.created_at DESC
        ''', (coordinator_id,))
        
        projects = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in projects]
        
    except Exception as e:
        print(f"Error fetching coordinator projects: {e}")
        return []


# ============================================================================
# SNIPPET 5: OPTIONAL - Update project_coordinator_id
# Add this endpoint if you want to reassign coordinators later
# ============================================================================

@app.route("/api/admin/projects/<int:project_id>/coordinator", methods=["PUT"])
@admin_required
def update_project_coordinator(project_id):
    """
    Update the Project Coordinator assigned to a project.
    Only Super Admin can perform this action.
    """
    try:
        data = request.get_json() or {}
        project_coordinator_id = data.get("project_coordinator_id")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify project exists
        cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Project not found"}), 404
        
        # Validate coordinator if provided
        if project_coordinator_id:
            try:
                project_coordinator_id = int(project_coordinator_id)
                # Verify coordinator exists and has correct role
                cursor.execute('''
                    SELECT u.id FROM users u
                    INNER JOIN usertypes ut ON u.user_type_id = ut.id
                    WHERE u.id = ? AND ut.user_role = 'Project Coordinator'
                ''', (project_coordinator_id,))
                if not cursor.fetchone():
                    conn.close()
                    return jsonify({"error": "Invalid Project Coordinator"}), 400
            except (ValueError, TypeError):
                conn.close()
                return jsonify({"error": "Invalid coordinator ID"}), 400
        
        # Update project coordinator
        cursor.execute(
            'UPDATE projects SET project_coordinator_id = ? WHERE id = ?',
            (project_coordinator_id or None, project_id)
        )
        
        conn.commit()
        conn.close()
        
        user_id = get_current_user_id()
        log_activity(
            user_id,
            'project_coordinator_updated',
            f'Updated project {project_id} coordinator assignment',
            project_id=project_id
        )
        
        return jsonify({"message": "Project coordinator updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# INTEGRATION SUMMARY
# ============================================================================
# 1. Apply the SQL migration to add the column
# 2. Add SNIPPET 2 endpoint to fetch coordinators for dropdown
# 3. Insert the HTML dropdown in the project creation form
# 4. Modify create_employee_project() with SNIPPET 3 logic
# 5. Update get_admin_projects() query with new joins
# 6. (OPTIONAL) Add SNIPPET 4 and 5 for full functionality
#
# After integration:
# - Super Admin can assign Project Coordinator when creating projects
# - project_coordinator_id is stored in projects table
# - Coordinators can view their assigned projects
# - Coordinators can be reassigned if needed
# ============================================================================
