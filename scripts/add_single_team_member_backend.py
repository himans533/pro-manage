"""
Backend logic for adding a single team member to a project.
Add these functions to AdminLoginPanel/app.py around line 4500

This endpoint allows Project Coordinators to add individual employees to projects
one at a time, in addition to the bulk "Add Team Members to Project" feature.
"""

from flask import jsonify, request, session

# ============================================================================
# ENDPOINT: Add a single team member to project
# ============================================================================
# Route: POST /api/coordinator/add-team-member/<int:project_id>
# Purpose: Add a single employee to project_team_members table
# Called by: "Add New Team Member" button modal

@app.route('/api/coordinator/add-team-member/<int:project_id>', methods=['POST'])
def add_single_team_member(project_id):
    """
    Add a single employee to a project's team members.
    
    Request body:
    {
        "user_id": 42
    }
    
    Validation:
    - Project must exist
    - User must be the project coordinator
    - Employee must have parent_user_id = coordinator_id (must be under coordinator)
    - Employee not already in project_team_members
    - Max 3 members per project (check before adding)
    
    Response:
    {
        "success": true,
        "message": "Employee added to project",
        "user_id": 42,
        "username": "john_doe"
    }
    """
    try:
        # Get logged-in user (coordinator)
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        # Parse request
        data = request.get_json() or {}
        employee_id = data.get('user_id')
        
        if not employee_id:
            return jsonify({"error": "user_id is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Verify project exists and user is the coordinator
        cursor.execute('''
            SELECT id, project_coordinator_id 
            FROM projects 
            WHERE id = ? AND project_coordinator_id = ?
        ''', (project_id, user_id))
        
        project = cursor.fetchone()
        if not project:
            conn.close()
            return jsonify({"error": "Project not found or you are not the coordinator"}), 403

        # 2. Verify employee exists and is under this coordinator
        cursor.execute('''
            SELECT id, username, email, parent_user_id
            FROM users 
            WHERE id = ? AND parent_user_id = ?
        ''', (employee_id, user_id))
        
        employee = cursor.fetchone()
        if not employee:
            conn.close()
            return jsonify({"error": "Employee not found or not under your supervision"}), 403

        # 3. Check if employee already in project_team_members
        cursor.execute('''
            SELECT id FROM project_team_members 
            WHERE project_id = ? AND user_id = ?
        ''', (project_id, employee_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({"error": "Employee already added to this project"}), 409

        # 4. Check current team member count (max 3)
        cursor.execute('''
            SELECT COUNT(*) as count FROM project_team_members 
            WHERE project_id = ?
        ''', (project_id,))
        
        result = cursor.fetchone()
        count = result['count'] if result else 0
        
        if count >= 3:
            conn.close()
            return jsonify({"error": "Maximum 3 team members already added to this project"}), 400

        # 5. Add employee to project_team_members
        cursor.execute('''
            INSERT INTO project_team_members (project_id, user_id)
            VALUES (?, ?)
        ''', (project_id, employee_id))
        
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": f"Employee {employee['username']} added to project",
            "user_id": employee['id'],
            "username": employee['username'],
            "email": employee['email']
        }), 201

    except Exception as e:
        print(f"Error adding team member: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# OPTIONAL: Get available team members (not yet added to project)
# ============================================================================
# Route: GET /api/coordinator/available-team-members/<int:project_id>
# Purpose: Get list of eligible employees for this project (not already added)
# Called by: "Add New Team Member" modal to populate dropdown

@app.route('/api/coordinator/available-team-members/<int:project_id>', methods=['GET'])
def get_available_team_members(project_id):
    """
    Get list of employees available to be added (not already in project_team_members).
    Only employees whose parent_user_id = logged-in coordinator's id.
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify project exists and user is the coordinator
        cursor.execute('''
            SELECT id, project_coordinator_id 
            FROM projects 
            WHERE id = ? AND project_coordinator_id = ?
        ''', (project_id, user_id))
        
        project = cursor.fetchone()
        if not project:
            conn.close()
            return jsonify({"error": "Project not found or access denied"}), 403

        # Get employees under this coordinator NOT already in project
        cursor.execute('''
            SELECT u.id, u.username, u.email
            FROM users u
            WHERE u.parent_user_id = ?
              AND u.id NOT IN (
                SELECT user_id FROM project_team_members 
                WHERE project_id = ?
              )
            ORDER BY u.username ASC
        ''', (user_id, project_id))

        employees = [dict(emp) for emp in cursor.fetchall()]
        
        # Check if max reached
        cursor.execute('''
            SELECT COUNT(*) as count FROM project_team_members 
            WHERE project_id = ?
        ''', (project_id,))
        
        result = cursor.fetchone()
        current_count = result['count'] if result else 0
        can_add = current_count < 3

        conn.close()

        return jsonify({
            "employees": employees,
            "available": len(employees),
            "current_count": current_count,
            "can_add": can_add,
            "max_members": 3
        }), 200

    except Exception as e:
        print(f"Error fetching available team members: {e}")
        return jsonify({"error": str(e)}), 500
