"""
AUTHORIZATION MIDDLEWARE & ACCESS CONTROL SYSTEM
================================================

This module provides comprehensive role-based access control (RBAC) for the Project Management System.
It defines middleware and utility functions to enforce:

- Super Admin: Full access to everything
- Project Coordinator: Access to only their projects and their team members
- Team Member: Access to only their own tasks

No authentication is modified. Only authorization checks are added.
"""

from functools import wraps
from flask import g, session, jsonify, request
import sqlite3

# ============================================================================
# ROLE DEFINITIONS & CONSTANTS
# ============================================================================

ROLE_SUPER_ADMIN = "super admin"
ROLE_COORDINATOR = "project coordinator"
ROLE_TEAM_MEMBER = "team member"

# Role hierarchy (higher number = more permissions)
ROLE_HIERARCHY = {
    ROLE_TEAM_MEMBER: 1,
    ROLE_COORDINATOR: 2,
    ROLE_SUPER_ADMIN: 3
}

# ============================================================================
# UTILITY FUNCTIONS - GET CURRENT USER INFO
# ============================================================================

def get_current_user_id():
    """Get current user ID from session or Flask g object."""
    return getattr(g, 'current_user_id', None) or session.get('user_id')


def get_current_user_role(db_path):
    """
    Fetch current user's role from database.
    Returns: role string (lowercase)
    """
    user_id = get_current_user_id()
    if not user_id or user_id == 0:  # Super Admin has ID 0
        return ROLE_SUPER_ADMIN
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.cursor()
        row = cursor.execute('''
            SELECT ut.user_role FROM users u
            LEFT JOIN usertypes ut ON u.user_type_id = ut.id
            WHERE u.id = ?
        ''', (user_id,)).fetchone()
        
        conn.close()
        
        if row:
            return row['user_role'].lower() if row['user_role'] else ROLE_TEAM_MEMBER
        return ROLE_TEAM_MEMBER
    except Exception as e:
        print(f"Error fetching user role: {e}")
        return ROLE_TEAM_MEMBER


def is_super_admin(db_path):
    """Check if current user is Super Admin."""
    return get_current_user_role(db_path) == ROLE_SUPER_ADMIN


def is_coordinator(db_path):
    """Check if current user is a Project Coordinator."""
    role = get_current_user_role(db_path)
    return role == ROLE_COORDINATOR


def is_team_member(db_path):
    """Check if current user is a Team Member."""
    role = get_current_user_role(db_path)
    return role == ROLE_TEAM_MEMBER


# ============================================================================
# ACCESS CONTROL DECORATORS
# ============================================================================

def super_admin_only(db_path):
    """
    Decorator: Only Super Admin can access this endpoint.
    Usage: @super_admin_only(DB_PATH)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_super_admin(db_path):
                return jsonify({'error': 'Super Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def coordinator_or_admin(db_path):
    """
    Decorator: Only Coordinators and Super Admins can access this endpoint.
    Usage: @coordinator_or_admin(DB_PATH)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role = get_current_user_role(db_path)
            if role not in [ROLE_COORDINATOR, ROLE_SUPER_ADMIN]:
                return jsonify({'error': 'Coordinator access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# AUTHORIZATION HELPER FUNCTIONS
# ============================================================================

def user_can_view_project(user_id, project_id, db_path):
    """
    Check if user can view a project.
    - Super Admin: YES (always)
    - Coordinator: YES if project_coordinator_id = user_id
    - Team Member: YES if in project_team_members
    """
    if is_super_admin(db_path):
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if project_coordinator_id matches (for Coordinators)
        row = cursor.execute(
            'SELECT project_coordinator_id FROM projects WHERE id = ?',
            (project_id,)
        ).fetchone()
        
        if row and row['project_coordinator_id'] == user_id:
            conn.close()
            return True
        
        # Check if in project_team_members (for Team Members)
        row = cursor.execute(
            'SELECT 1 FROM project_team_members WHERE project_id = ? AND user_id = ?',
            (project_id, user_id)
        ).fetchone()
        
        conn.close()
        return row is not None
        
    except Exception as e:
        print(f"Error checking project access: {e}")
        return False


def user_can_view_task(user_id, task_id, db_path):
    """
    Check if user can view a task.
    - Super Admin: YES (always)
    - Coordinator: YES if task is in their project (project_coordinator_id)
    - Team Member: YES if assigned_to_id = user_id or created_by_id = user_id
    """
    if is_super_admin(db_path):
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get task details
        task = cursor.execute(
            'SELECT project_id, assigned_to_id, created_by_id FROM tasks WHERE id = ?',
            (task_id,)
        ).fetchone()
        
        if not task:
            conn.close()
            return False
        
        # Check if Team Member assigned to task
        if task['assigned_to_id'] == user_id or task['created_by_id'] == user_id:
            conn.close()
            return True
        
        # Check if Coordinator assigned to project
        project = cursor.execute(
            'SELECT project_coordinator_id FROM projects WHERE id = ?',
            (task['project_id'],)
        ).fetchone()
        
        if project and project['project_coordinator_id'] == user_id:
            conn.close()
            return True
        
        conn.close()
        return False
        
    except Exception as e:
        print(f"Error checking task access: {e}")
        return False


def user_can_view_team_member(user_id, target_user_id, db_path):
    """
    Check if user can view another user as team member.
    - Super Admin: YES (all)
    - Coordinator: YES if target_user has parent_user_id = user_id
    - Team Member: NO (cannot view other team members)
    """
    if is_super_admin(db_path):
        return True
    
    if is_team_member(db_path):
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if target user is under current coordinator
        row = cursor.execute(
            'SELECT parent_user_id FROM users WHERE id = ?',
            (target_user_id,)
        ).fetchone()
        
        conn.close()
        
        if row and row['parent_user_id'] == user_id:
            return True
        
        return False
        
    except Exception as e:
        print(f"Error checking team member access: {e}")
        return False


def get_filtered_projects(user_id, db_path):
    """
    Get projects filtered by user role.
    - Super Admin: All projects
    - Coordinator: Only projects where project_coordinator_id = user_id
    - Team Member: Only projects in project_team_members where user_id = user_id
    """
    role = get_current_user_role(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if role == ROLE_SUPER_ADMIN:
            # Super Admin: all projects
            projects = cursor.execute(
                'SELECT * FROM projects ORDER BY created_at DESC'
            ).fetchall()
        
        elif role == ROLE_COORDINATOR:
            # Coordinator: only their projects
            projects = cursor.execute('''
                SELECT * FROM projects 
                WHERE project_coordinator_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,)).fetchall()
        
        else:  # ROLE_TEAM_MEMBER
            # Team Member: projects they're assigned to
            projects = cursor.execute('''
                SELECT DISTINCT p.* FROM projects p
                JOIN project_team_members ptm ON p.id = ptm.project_id
                WHERE ptm.user_id = ?
                ORDER BY p.created_at DESC
            ''', (user_id,)).fetchall()
        
        conn.close()
        return [dict(p) for p in projects]
        
    except Exception as e:
        print(f"Error fetching filtered projects: {e}")
        return []


def get_filtered_tasks(user_id, db_path):
    """
    Get tasks filtered by user role.
    - Super Admin: All tasks
    - Coordinator: Tasks in their projects (project_coordinator_id)
    - Team Member: Only their assigned tasks
    """
    role = get_current_user_role(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if role == ROLE_SUPER_ADMIN:
            # Super Admin: all tasks
            tasks = cursor.execute(
                'SELECT * FROM tasks ORDER BY created_at DESC'
            ).fetchall()
        
        elif role == ROLE_COORDINATOR:
            # Coordinator: tasks in their projects
            tasks = cursor.execute('''
                SELECT t.* FROM tasks t
                JOIN projects p ON t.project_id = p.id
                WHERE p.project_coordinator_id = ?
                ORDER BY t.created_at DESC
            ''', (user_id,)).fetchall()
        
        else:  # ROLE_TEAM_MEMBER
            # Team Member: only assigned to them
            tasks = cursor.execute('''
                SELECT * FROM tasks 
                WHERE assigned_to_id = ?
                ORDER BY created_at DESC
            ''', (user_id,)).fetchall()
        
        conn.close()
        return [dict(t) for t in tasks]
        
    except Exception as e:
        print(f"Error fetching filtered tasks: {e}")
        return []


def get_filtered_team_members(user_id, db_path):
    """
    Get team members filtered by user role.
    - Super Admin: All users
    - Coordinator: Only users with parent_user_id = user_id
    - Team Member: No one (cannot view team members)
    """
    role = get_current_user_role(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if role == ROLE_SUPER_ADMIN:
            # Super Admin: all users
            users = cursor.execute(
                'SELECT * FROM users ORDER BY username'
            ).fetchall()
        
        elif role == ROLE_COORDINATOR:
            # Coordinator: only their team members
            users = cursor.execute('''
                SELECT * FROM users 
                WHERE parent_user_id = ?
                ORDER BY username
            ''', (user_id,)).fetchall()
        
        else:  # ROLE_TEAM_MEMBER
            # Team Member: cannot view others
            users = []
        
        conn.close()
        return [dict(u) for u in users]
        
    except Exception as e:
        print(f"Error fetching filtered team members: {e}")
        return []


# ============================================================================
# API CONDITION CHECK EXAMPLES
# ============================================================================

def check_project_access_api(project_id, db_path):
    """
    Middleware check for project endpoints.
    Call this at the start of any project endpoint.
    
    Usage in Flask route:
        @app.route('/api/projects/<int:project_id>')
        @login_required
        def get_project(project_id):
            if not check_project_access_api(project_id, DB_PATH):
                return jsonify({'error': 'Access denied'}), 403
            # ... rest of endpoint
    """
    user_id = get_current_user_id()
    return user_can_view_project(user_id, project_id, db_path)


def check_task_access_api(task_id, db_path):
    """
    Middleware check for task endpoints.
    Call this at the start of any task endpoint.
    """
    user_id = get_current_user_id()
    return user_can_view_task(user_id, task_id, db_path)


# ============================================================================
# EXAMPLE USAGE IN FLASK ROUTES
# ============================================================================

"""
Example 1: Super Admin Only Endpoint
====================================

@app.route('/api/hierarchy/full')
@login_required
@super_admin_only(DB_PATH)
def get_full_hierarchy():
    # Only Super Admin can reach here
    return jsonify({'data': 'hierarchy'})


Example 2: Coordinator or Admin Endpoint
=========================================

@app.route('/api/coordinator/team')
@login_required
@coordinator_or_admin(DB_PATH)
def get_coordinator_team():
    user_id = get_current_user_id()
    role = get_current_user_role(DB_PATH)
    
    if role == 'super admin':
        # Can see all teams
        team_members = get_filtered_team_members(user_id, DB_PATH)
    else:
        # Can only see their team
        team_members = get_filtered_team_members(user_id, DB_PATH)
    
    return jsonify({'team': team_members})


Example 3: Project Access with Filtering
=========================================

@app.route('/api/projects')
@login_required
def get_projects():
    user_id = get_current_user_id()
    
    # Automatically filters based on role
    projects = get_filtered_projects(user_id, DB_PATH)
    
    return jsonify({'projects': projects})


Example 4: Specific Project with Access Check
==============================================

@app.route('/api/projects/<int:project_id>')
@login_required
def get_project_detail(project_id):
    user_id = get_current_user_id()
    
    # Check access first
    if not user_can_view_project(user_id, project_id, DB_PATH):
        return jsonify({'error': 'Access denied to this project'}), 403
    
    # Fetch and return project
    conn = get_db_connection()
    project = conn.execute(
        'SELECT * FROM projects WHERE id = ?', 
        (project_id,)
    ).fetchone()
    conn.close()
    
    return jsonify(dict(project))


Example 5: Task Assignment with Role Check
==========================================

@app.route('/api/tasks/<int:task_id>/assign', methods=['POST'])
@login_required
def assign_task(task_id):
    user_id = get_current_user_id()
    role = get_current_user_role(DB_PATH)
    
    # Only Coordinators and Super Admin can assign tasks
    if role not in ['project coordinator', 'super admin']:
        return jsonify({'error': 'Only coordinators can assign tasks'}), 403
    
    # Get task and verify access
    if not user_can_view_task(user_id, task_id, DB_PATH):
        return jsonify({'error': 'Access denied to this task'}), 403
    
    # Proceed with assignment
    data = request.get_json()
    assigned_to = data.get('assigned_to_id')
    
    conn = get_db_connection()
    conn.execute(
        'UPDATE tasks SET assigned_to_id = ? WHERE id = ?',
        (assigned_to, task_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})
"""
