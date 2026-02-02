"""
Backend logic for adding team members to projects.
Add these functions to AdminLoginPanel/app.py
"""

from flask import jsonify, request
from functools import wraps
import sqlite3

# ============================================================================
# ENDPOINT 1: Get eligible team members for a project
# ============================================================================
# Route: GET /api/coordinator/eligible-team-members/<int:project_id>
# Purpose: Return list of employees whose parent_user_id = coordinator_id
# Called by: Modal when it opens

@app.route('/api/coordinator/eligible-team-members/<int:project_id>', methods=['GET'])
def get_eligible_team_members(project_id):
    """
    Get list of employees eligible to be added as team members to a project.
    Only employees whose parent_user_id = logged-in coordinator's id are eligible.
    """
    try:
        # Get logged-in user (coordinator)
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # First, verify project exists and user is the coordinator
        cursor.execute('''
            SELECT id, project_coordinator_id 
            FROM projects 
            WHERE id = ? AND project_coordinator_id = ?
        ''', (project_id, user_id))
        
        project = cursor.fetchone()
        if not project:
            conn.close()
            return jsonify({"error": "Project not found or access denied"}), 403

        # Get all employees under this coordinator (parent_user_id = coordinator's id)
        # Exclude employees already added to this project
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.user_type_id
            FROM users u
            WHERE u.parent_user_id = ?
              AND u.id NOT IN (
                SELECT user_id FROM project_team_members 
                WHERE project_id = ?
              )
            ORDER BY u.username ASC
        ''', (user_id, project_id))

        employees = cursor.fetchall()
        conn.close()

        # Convert rows to dictionaries
        employee_list = [
            {
                'id': emp['id'],
                'username': emp['username'],
                'email': emp['email'],
                'user_type_id': emp['user_type_id']
            }
            for emp in employees
        ]

        return jsonify({
            "employees": employee_list,
            "count": len(employee_list)
        }), 200

    except Exception as e:
        print(f"Error fetching eligible team members: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ENDPOINT 2: Add team members to project
# ============================================================================
# Route: POST /api/coordinator/add-team-members/<int:project_id>
# Purpose: Add selected employees to project with validation
# Validates: Max 3 members, all belong to coordinator, no duplicates

@app.route('/api/coordinator/add-team-members/<int:project_id>', methods=['POST'])
def add_team_members_to_project(project_id):
    """
    Add team members to a project.
    
    Request body:
    {
        "user_ids": [1, 2, 3]  // Array of employee IDs (max 3)
    }
    
    Validation:
    - Project must exist
    - User must be the project coordinator
    - user_ids must be employees under this coordinator
    - Maximum 3 employees can be added
    - No duplicate assignments
    """
    try:
        # Get logged-in user (coordinator)
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        # Parse request
        data = request.get_json() or {}
        user_ids = data.get('user_ids', [])

        # Validation: user_ids must be a list
        if not isinstance(user_ids, list):
            return jsonify({"error": "user_ids must be a list"}), 400

        # Validation: Maximum 3 team members
        if len(user_ids) > 3:
            return jsonify({"error": "Maximum 3 team members can be added to a project"}), 400

        # Validation: At least 1 member selected
        if len(user_ids) < 1:
            return jsonify({"error": "Please select at least 1 team member"}), 400

        # Remove duplicates from list
        user_ids = list(set(user_ids))

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

        # Verify all user_ids belong to employees under this coordinator
        placeholders = ','.join('?' * len(user_ids))
        cursor.execute(f'''
            SELECT COUNT(*) as count
            FROM users
            WHERE parent_user_id = ? AND id IN ({placeholders})
        ''', [user_id] + user_ids)
        
        result = cursor.fetchone()
        if result['count'] != len(user_ids):
            conn.close()
            return jsonify({"error": "Some employees are not under your supervision"}), 403

        # Add team members to project
        # Use INSERT OR IGNORE to skip duplicates silently
        added_count = 0
        try:
            for emp_id in user_ids:
                cursor.execute('''
                    INSERT OR IGNORE INTO project_team_members (project_id, user_id)
                    VALUES (?, ?)
                ''', (project_id, emp_id))
                added_count += cursor.rowcount
            
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.close()
            return jsonify({"error": "Failed to add team members. Some may already be assigned."}), 400

        conn.close()

        return jsonify({
            "message": f"Successfully added {added_count} team member(s) to project",
            "added_count": added_count
        }), 201

    except Exception as e:
        print(f"Error adding team members: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ENDPOINT 3: Get team members of a project (Optional - for display)
# ============================================================================
# Route: GET /api/coordinator/project-team-members/<int:project_id>
# Purpose: Get current team members assigned to project
# Can be used to display current assignments

@app.route('/api/coordinator/project-team-members/<int:project_id>', methods=['GET'])
def get_project_team_members(project_id):
    """
    Get list of team members currently assigned to a project.
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Not authenticated"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify access (coordinator or admin)
        cursor.execute('''
            SELECT id FROM projects 
            WHERE id = ? AND (project_coordinator_id = ? OR created_by_id = ?)
        ''', (project_id, user_id, user_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Access denied"}), 403

        # Get team members
        cursor.execute('''
            SELECT 
                ptm.id,
                ptm.user_id,
                u.username,
                u.email,
                ptm.assigned_at
            FROM project_team_members ptm
            JOIN users u ON ptm.user_id = u.id
            WHERE ptm.project_id = ?
            ORDER BY u.username ASC
        ''', (project_id,))

        members = cursor.fetchall()
        conn.close()

        team_list = [
            {
                'id': m['id'],
                'user_id': m['user_id'],
                'username': m['username'],
                'email': m['email'],
                'assigned_at': m['assigned_at']
            }
            for m in members
        ]

        return jsonify({
            "team_members": team_list,
            "count": len(team_list)
        }), 200

    except Exception as e:
        print(f"Error fetching project team members: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================================
# HELPER: Check if user is project coordinator
# ============================================================================

def is_project_coordinator(user_id):
    """Helper function to check if user is a Project Coordinator"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT ut.user_role 
            FROM users u
            JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ? AND ut.user_role = 'Project Coordinator'
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    except Exception as e:
        print(f"Error checking user role: {e}")
        return False


# ============================================================================
# OPTIONAL: Remove team member from project
# ============================================================================
# Route: DELETE /api/coordinator/remove-team-member/<int:project_id>/<int:user_id>
# Purpose: Remove a team member from a project

@app.route('/api/coordinator/remove-team-member/<int:project_id>/<int:user_id>', methods=['DELETE'])
def remove_team_member_from_project(project_id, user_id):
    """
    Remove a team member from a project.
    Only the project coordinator can remove team members.
    """
    try:
        coordinator_id = session.get('user_id')
        if not coordinator_id:
            return jsonify({"error": "Not authenticated"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify coordinator has access to project
        cursor.execute('''
            SELECT id FROM projects 
            WHERE id = ? AND project_coordinator_id = ?
        ''', (project_id, coordinator_id))
        
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "Access denied"}), 403

        # Delete team member assignment
        cursor.execute('''
            DELETE FROM project_team_members
            WHERE project_id = ? AND user_id = ?
        ''', (project_id, user_id))

        conn.commit()
        affected = cursor.rowcount
        conn.close()

        if affected == 0:
            return jsonify({"error": "Team member assignment not found"}), 404

        return jsonify({
            "message": "Team member removed successfully"
        }), 200

    except Exception as e:
        print(f"Error removing team member: {e}")
        return jsonify({"error": str(e)}), 500
