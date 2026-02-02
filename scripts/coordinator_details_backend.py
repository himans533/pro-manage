"""
Coordinator Details Backend - Flask Routes
Provides detailed view of a Project Coordinator's team, projects, and tasks
"""

from flask import jsonify, session, g, request
from functools import wraps


# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================
def super_admin_required(f):
    """Decorator to ensure only Super Admin can access coordinator details"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_admin = session.get('admin') or session.get('user_type') == 'admin'
        if not is_admin:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# MAIN COORDINATOR DETAILS ENDPOINT
# ============================================================================
@app.route('/api/coordinator/<int:coordinator_id>/details', methods=['GET'])
@super_admin_required
def get_coordinator_details(coordinator_id):
    """
    Fetches complete details for a Project Coordinator including:
    - Coordinator info
    - Number of team members
    - Assigned projects
    - Tasks assigned by coordinator to team members with status
    
    Returns JSON structure:
    {
        "coordinator": {
            "id": 2,
            "name": "Coordinator Name",
            "email": "coordinator@example.com"
        },
        "team_members": [
            {
                "id": 3,
                "name": "Team Member 1",
                "email": "member@example.com"
            }
        ],
        "team_count": 5,
        "projects": [
            {
                "id": 10,
                "title": "Project A",
                "status": "Active",
                "team_members_assigned": 3,
                "tasks_count": 12,
                "tasks_completed": 5
            }
        ],
        "tasks": [
            {
                "id": 100,
                "title": "Task 1",
                "status": "In Progress",
                "priority": "High",
                "deadline": "2026-03-15",
                "assigned_to": "Team Member 1",
                "project_title": "Project A",
                "created_at": "2026-02-02"
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify coordinator exists
        cursor.execute('''
            SELECT u.id, u.username, u.email
            FROM users u
            WHERE u.id = ?
            AND (LOWER(u.user_type) LIKE '%coordinator%')
        ''', (coordinator_id,))
        
        coordinator = cursor.fetchone()
        if not coordinator:
            conn.close()
            return jsonify({"error": "Coordinator not found"}), 404
        
        # Get all team members under coordinator
        team_members = _get_team_members_list(cursor, coordinator_id)
        
        # Get projects assigned to this coordinator
        projects = _get_coordinator_projects(cursor, coordinator_id, team_members)
        
        # Get tasks assigned by coordinator to team members
        tasks = _get_coordinator_tasks(cursor, coordinator_id, team_members)
        
        response = {
            "coordinator": {
                "id": coordinator['id'],
                "name": coordinator['username'],
                "email": coordinator['email']
            },
            "team_members": team_members,
            "team_count": len(team_members),
            "projects": projects,
            "project_count": len(projects),
            "tasks": tasks,
            "tasks_count": len(tasks)
        }
        
        conn.close()
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error fetching coordinator details: {str(e)}")
        return jsonify({"error": "Failed to fetch coordinator details"}), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_team_members_list(cursor, coordinator_id):
    """Get all Team Members under a Coordinator"""
    cursor.execute('''
        SELECT u.id, u.username, u.email
        FROM users u
        WHERE u.parent_user_id = ?
        AND (LOWER(u.user_type) LIKE '%team%' 
             OR LOWER(u.user_type) LIKE '%employee%')
        ORDER BY u.username
    ''', (coordinator_id,))
    
    members = cursor.fetchall()
    return [
        {
            "id": m['id'],
            "name": m['username'],
            "email": m['email']
        }
        for m in members
    ]


def _get_coordinator_projects(cursor, coordinator_id, team_members):
    """Get all projects where team members are assigned"""
    if not team_members:
        return []
    
    member_ids = [m['id'] for m in team_members]
    placeholders = ','.join('?' * len(member_ids))
    
    cursor.execute(f'''
        SELECT DISTINCT 
            p.id,
            p.title,
            p.status,
            (
                SELECT COUNT(DISTINCT ptm.user_id)
                FROM project_team_members ptm
                WHERE ptm.project_id = p.id
                AND ptm.user_id IN ({placeholders})
            ) as team_members_assigned,
            (
                SELECT COUNT(*)
                FROM tasks t
                WHERE t.project_id = p.id
            ) as tasks_count,
            (
                SELECT COUNT(*)
                FROM tasks t
                WHERE t.project_id = p.id
                AND LOWER(t.status) = 'completed'
            ) as tasks_completed,
            p.created_at
        FROM projects p
        JOIN project_team_members ptm ON p.id = ptm.project_id
        WHERE ptm.user_id IN ({placeholders})
        ORDER BY p.created_at DESC
    ''', member_ids + member_ids + member_ids)
    
    projects = cursor.fetchall()
    return [
        {
            "id": p['id'],
            "title": p['title'],
            "status": p['status'],
            "team_members_assigned": p['team_members_assigned'],
            "tasks_count": p['tasks_count'],
            "tasks_completed": p['tasks_completed'],
            "created_at": p['created_at']
        }
        for p in projects
    ]


def _get_coordinator_tasks(cursor, coordinator_id, team_members):
    """Get all tasks assigned by coordinator to team members"""
    if not team_members:
        return []
    
    member_ids = [m['id'] for m in team_members]
    placeholders = ','.join('?' * len(member_ids))
    
    cursor.execute(f'''
        SELECT 
            t.id,
            t.title,
            t.status,
            t.priority,
            t.deadline,
            u.username as assigned_to,
            p.title as project_title,
            t.created_at,
            t.progress
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to_id = u.id
        LEFT JOIN projects p ON t.project_id = p.id
        WHERE t.assigned_to_id IN ({placeholders})
        AND t.created_by_id = ?
        ORDER BY t.created_at DESC
    ''', member_ids + [coordinator_id])
    
    tasks = cursor.fetchall()
    return [
        {
            "id": t['id'],
            "title": t['title'],
            "status": t['status'],
            "priority": t['priority'],
            "deadline": t['deadline'],
            "assigned_to": t['assigned_to'],
            "project_title": t['project_title'],
            "created_at": t['created_at'],
            "progress": t['progress']
        }
        for t in tasks
    ]
