"""
User Hierarchy Backend - Flask Routes
This module provides API endpoints to fetch and display organization hierarchy.

Hierarchy Structure:
Super Admin (parent_user_id = NULL, user_type = 'Super Admin')
  ├── Project Coordinator (parent_user_id = Super Admin ID, user_type = 'Project Coordinator')
  │    ├── Team Members (parent_user_id = Coordinator ID, user_type = 'Team Member')
  │    │    ├── Projects (assigned to this user)
  │    │    │    ├── Milestones
  │    │    │    │    └── Tasks
"""

from flask import jsonify, session, g
from functools import wraps


# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================
def super_admin_required(f):
    """Decorator to ensure only Super Admin can access hierarchy view"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_admin = session.get('admin') or session.get('user_type') == 'admin'
        if not is_admin:
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# MAIN HIERARCHY ENDPOINT
# ============================================================================
@app.route('/api/hierarchy/full', methods=['GET'])
@super_admin_required
def get_full_hierarchy():
    """
    Fetches complete organizational hierarchy from Super Admin level down.
    
    Returns JSON structure:
    {
        "super_admins": [
            {
                "id": 1,
                "name": "Admin User",
                "coordinators": [
                    {
                        "id": 2,
                        "name": "Coordinator 1",
                        "team_members": [
                            {
                                "id": 3,
                                "name": "Team Member 1",
                                "projects": [
                                    {
                                        "id": 10,
                                        "title": "Project A",
                                        "milestones": [
                                            {
                                                "id": 20,
                                                "title": "Milestone 1",
                                                "tasks": [...]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all Super Admins (users with parent_user_id = NULL)
        cursor.execute('''
            SELECT DISTINCT u.id, u.username, u.email
            FROM users u
            WHERE u.parent_user_id IS NULL
            ORDER BY u.username
        ''')
        super_admins = cursor.fetchall()
        
        hierarchy = {"super_admins": []}
        
        for admin in super_admins:
            admin_dict = dict(admin)
            admin_dict['coordinators'] = _get_coordinators(cursor, admin['id'])
            hierarchy['super_admins'].append(admin_dict)
        
        conn.close()
        return jsonify(hierarchy), 200
        
    except Exception as e:
        print(f"Error fetching hierarchy: {str(e)}")
        return jsonify({"error": "Failed to fetch hierarchy"}), 500


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_coordinators(cursor, super_admin_id):
    """Get all Project Coordinators under a Super Admin"""
    cursor.execute('''
        SELECT DISTINCT u.id, u.username, u.email
        FROM users u
        WHERE u.parent_user_id = ?
        AND LOWER(u.user_type) LIKE '%coordinator%'
        ORDER BY u.username
    ''', (super_admin_id,))
    
    coordinators = cursor.fetchall()
    result = []
    
    for coordinator in coordinators:
        coord_dict = dict(coordinator)
        coord_dict['team_members'] = _get_team_members(cursor, coordinator['id'])
        result.append(coord_dict)
    
    return result


def _get_team_members(cursor, coordinator_id):
    """Get all Team Members under a Coordinator"""
    cursor.execute('''
        SELECT DISTINCT u.id, u.username, u.email
        FROM users u
        WHERE u.parent_user_id = ?
        AND LOWER(u.user_type) LIKE '%team%' OR LOWER(u.user_type) LIKE '%employee%'
        ORDER BY u.username
    ''', (coordinator_id,))
    
    team_members = cursor.fetchall()
    result = []
    
    for member in team_members:
        member_dict = dict(member)
        member_dict['projects'] = _get_projects_for_user(cursor, member['id'])
        result.append(member_dict)
    
    return result


def _get_projects_for_user(cursor, user_id):
    """Get all projects assigned to a user"""
    cursor.execute('''
        SELECT DISTINCT p.id, p.title, p.description, p.status
        FROM projects p
        JOIN project_team_members ptm ON p.id = ptm.project_id
        WHERE ptm.user_id = ?
        ORDER BY p.title
    ''', (user_id,))
    
    projects = cursor.fetchall()
    result = []
    
    for project in projects:
        project_dict = dict(project)
        project_dict['milestones'] = _get_milestones_for_project(cursor, project['id'])
        result.append(project_dict)
    
    return result


def _get_milestones_for_project(cursor, project_id):
    """Get all milestones in a project"""
    cursor.execute('''
        SELECT m.id, m.title, m.description, m.status
        FROM milestones m
        WHERE m.project_id = ?
        ORDER BY m.title
    ''', (project_id,))
    
    milestones = cursor.fetchall()
    result = []
    
    for milestone in milestones:
        milestone_dict = dict(milestone)
        milestone_dict['tasks'] = _get_tasks_for_milestone(cursor, milestone['id'])
        result.append(milestone_dict)
    
    return result


def _get_tasks_for_milestone(cursor, milestone_id):
    """Get all tasks in a milestone"""
    cursor.execute('''
        SELECT t.id, t.title, t.description, t.status, t.deadline
        FROM tasks t
        WHERE t.milestone_id = ?
        ORDER BY t.title
    ''', (milestone_id,))
    
    return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# SIMPLIFIED HIERARCHY ENDPOINT (for tree visualization)
# ============================================================================

@app.route('/api/hierarchy/tree', methods=['GET'])
@super_admin_required
def get_hierarchy_tree():
    """
    Simplified endpoint returning only names and IDs for tree visualization.
    Easier for frontend tree rendering.
    
    Returns:
    {
        "structure": [
            {
                "type": "super_admin",
                "id": 1,
                "name": "Admin Name",
                "children": [
                    {
                        "type": "coordinator",
                        "id": 2,
                        "name": "Coordinator Name",
                        "children": [...]
                    }
                ]
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT u.id, u.username, u.email
            FROM users u
            WHERE u.parent_user_id IS NULL
            ORDER BY u.username
        ''')
        super_admins = cursor.fetchall()
        
        structure = []
        for admin in super_admins:
            admin_node = {
                "type": "super_admin",
                "id": admin['id'],
                "name": f"{admin['username']} ({admin['email']})",
                "children": _build_coordinator_nodes(cursor, admin['id'])
            }
            structure.append(admin_node)
        
        conn.close()
        return jsonify({"structure": structure}), 200
        
    except Exception as e:
        print(f"Error fetching tree: {str(e)}")
        return jsonify({"error": "Failed to fetch hierarchy"}), 500


def _build_coordinator_nodes(cursor, super_admin_id):
    """Build coordinator tree nodes"""
    cursor.execute('''
        SELECT u.id, u.username, u.email
        FROM users u
        WHERE u.parent_user_id = ?
        AND (LOWER(u.user_type) LIKE '%coordinator%')
        ORDER BY u.username
    ''', (super_admin_id,))
    
    coordinators = cursor.fetchall()
    nodes = []
    
    for coord in coordinators:
        coord_node = {
            "type": "coordinator",
            "id": coord['id'],
            "name": f"{coord['username']} ({coord['email']})",
            "children": _build_team_member_nodes(cursor, coord['id'])
        }
        nodes.append(coord_node)
    
    return nodes


def _build_team_member_nodes(cursor, coordinator_id):
    """Build team member tree nodes"""
    cursor.execute('''
        SELECT u.id, u.username, u.email
        FROM users u
        WHERE u.parent_user_id = ?
        AND (LOWER(u.user_type) LIKE '%team%' OR LOWER(u.user_type) LIKE '%employee%')
        ORDER BY u.username
    ''', (coordinator_id,))
    
    team_members = cursor.fetchall()
    nodes = []
    
    for member in team_members:
        member_node = {
            "type": "team_member",
            "id": member['id'],
            "name": f"{member['username']} ({member['email']})",
            "children": _build_project_nodes(cursor, member['id'])
        }
        nodes.append(member_node)
    
    return nodes


def _build_project_nodes(cursor, user_id):
    """Build project tree nodes"""
    cursor.execute('''
        SELECT DISTINCT p.id, p.title, p.status
        FROM projects p
        JOIN project_team_members ptm ON p.id = ptm.project_id
        WHERE ptm.user_id = ?
        ORDER BY p.title
    ''', (user_id,))
    
    projects = cursor.fetchall()
    nodes = []
    
    for project in projects:
        project_node = {
            "type": "project",
            "id": project['id'],
            "name": f"{project['title']} ({project['status']})",
            "children": _build_milestone_nodes(cursor, project['id'])
        }
        nodes.append(project_node)
    
    return nodes


def _build_milestone_nodes(cursor, project_id):
    """Build milestone tree nodes"""
    cursor.execute('''
        SELECT m.id, m.title, m.status
        FROM milestones m
        WHERE m.project_id = ?
        ORDER BY m.title
    ''', (project_id,))
    
    milestones = cursor.fetchall()
    nodes = []
    
    for milestone in milestones:
        milestone_node = {
            "type": "milestone",
            "id": milestone['id'],
            "name": f"{milestone['title']} ({milestone['status']})",
            "children": _build_task_nodes(cursor, milestone['id'])
        }
        nodes.append(milestone_node)
    
    return nodes


def _build_task_nodes(cursor, milestone_id):
    """Build task tree nodes (leaf nodes)"""
    cursor.execute('''
        SELECT t.id, t.title, t.status
        FROM tasks t
        WHERE t.milestone_id = ?
        ORDER BY t.title
    ''', (milestone_id,))
    
    tasks = cursor.fetchall()
    nodes = []
    
    for task in tasks:
        task_node = {
            "type": "task",
            "id": task['id'],
            "name": f"{task['title']} ({task['status']})",
            "children": []
        }
        nodes.append(task_node)
    
    return nodes
