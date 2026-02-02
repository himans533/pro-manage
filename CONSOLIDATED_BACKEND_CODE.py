# CONSOLIDATED BACKEND CODE
# This file contains the unified, deduplicated versions of key endpoints
# These should REPLACE the duplicate versions in app.py

# ============================================================================
# 1. UNIFIED DAILY REPORT ENDPOINTS (Consolidate create_daily_report variants)
# ============================================================================

@app.route('/api/daily-reports', methods=['POST'])
@app.route('/api/daily-report', methods=['POST'])  # Backward compatibility
@app.route('/api/daily-report/submit', methods=['POST'])  # Backward compatibility  
@login_required
def create_daily_report_unified():
    """
    Unified daily report creation endpoint.
    Handles both employee format (task_id, project_id) and admin format (date, employee_id, task).
    Replaces: create_daily_report() + create_daily_report_api()
    """
    try:
        current_user_id = get_current_user_id()
        data = request.get_json() or {}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current user's role for permission checks
        cursor.execute('''
            SELECT ut.user_role FROM users u 
            JOIN usertypes ut ON u.user_type_id = ut.id 
            WHERE u.id = ?
        ''', (current_user_id,))
        current_role_row = cursor.fetchone()
        current_role = (current_role_row['user_role'] if current_role_row else 'employee').lower()
        
        # Determine target user (admin can submit for others)
        report_user_id = data.get('user_id') or data.get('employee_id') or current_user_id
        
        if report_user_id != current_user_id and current_role not in ['admin', 'super admin']:
            conn.close()
            return jsonify({'error': 'Only admins can submit reports for other users'}), 403
        
        # Extract fields (support both formats)
        task_id = data.get('task_id')
        project_id = data.get('project_id')
        report_date = data.get('report_date') or data.get('date') or datetime.now().strftime('%Y-%m-%d')
        work_description = data.get('work_description') or data.get('task') or data.get('result', '')
        time_spent_str = data.get('time_spent', 8)
        status = data.get('status', 'In Progress' if data.get('task') else 'Completed')
        blocker = data.get('blocker', '')
        result_of_effort = data.get('result_of_effort') or data.get('result') or work_description or ''
        remarks = data.get('remarks') or ''
        communication_email = data.get('communication_email') or data.get('email') or ''
        communication_phone = data.get('communication_phone') or data.get('phone') or ''
        
        # Validation
        if not work_description:
            conn.close()
            return jsonify({'error': 'Description is required'}), 400
            
        try:
            time_spent = float(time_spent_str)
            if not (0 <= time_spent <= 24):
                raise ValueError
        except (ValueError, TypeError):
            conn.close()
            return jsonify({'error': 'Hours spent must be between 0 and 24'}), 400
        
        # If task_id provided, verify it exists
        if task_id:
            cursor.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()
            if not task:
                conn.close()
                return jsonify({'error': 'Task not found'}), 404
            project_id = project_id or task['project_id']
        
        # Project_id is required for the database
        if not project_id and not task_id:
            conn.close()
            return jsonify({'error': 'Either project_id or task_id is required'}), 400
        
        # Check duplicate (if task_id provided)
        if task_id:
            cursor.execute(
                "SELECT id FROM daily_task_reports WHERE user_id = ? AND task_id = ? AND report_date = ?",
                (report_user_id, task_id, report_date)
            )
            if cursor.fetchone():
                conn.close()
                return jsonify({'error': 'A report for this task already exists for this date'}), 409
        
        communication_details = json.dumps({'email': communication_email, 'phone': communication_phone})
        
        cursor.execute('''
            INSERT INTO daily_task_reports 
            (user_id, task_id, project_id, report_date, work_description, result_of_effort, remarks, 
             communication_email, communication_phone, communication_details, time_spent, status, blocker, approval_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (report_user_id, task_id, project_id, report_date, work_description, result_of_effort, 
              remarks, communication_email, communication_phone, communication_details, time_spent, status, blocker))
        
        report_id = cursor.lastrowid
        conn.commit()
        
        log_activity(report_user_id, 'daily_report_created', 
                    f'Submitted daily report for task {task_id}' if task_id else f'Submitted daily report',
                    project_id, task_id=task_id)
        
        conn.close()
        return jsonify({'success': True, 'id': report_id}), 201
        
    except Exception as e:
        logger.exception('Unified create_daily_report failed')
        return jsonify({'error': str(e)}), 500


@app.route('/api/daily-reports', methods=['GET'])
@login_required
def list_daily_reports_unified():
    """
    Unified daily reports listing with role-based filtering.
    Replaces: list_daily_reports() + list_daily_reports_api()
    """
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user role
        cursor.execute('''
            SELECT ut.user_role FROM users u 
            JOIN usertypes ut ON u.user_type_id = ut.id 
            WHERE u.id = ?
        ''', (user_id,))
        role_row = cursor.fetchone()
        role = (role_row['user_role'] if role_row else 'employee').lower()
        
        # Parse filters
        start_date = request.args.get('start_date') or request.args.get('date_from')
        end_date = request.args.get('end_date') or request.args.get('date_to')
        employee_id = request.args.get('employee_id')
        project_id = request.args.get('project_id')
        task_id = request.args.get('task_id')
        status = request.args.get('status')
        approval_status = request.args.get('approval_status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        params = []
        where = []
        
        # Role-based filtering
        if role == 'employee':
            where.append('d.user_id = ?')
            params.append(user_id)
        elif role == 'project coordinator':
            # Coordinators see reports from their team members
            where.append('''d.user_id IN (
                SELECT id FROM users WHERE parent_user_id = ?
            )''')
            params.append(user_id)
        # Super admin sees all
        
        # Additional filters
        if start_date:
            where.append('d.report_date >= ?')
            params.append(start_date)
        if end_date:
            where.append('d.report_date <= ?')
            params.append(end_date)
        if employee_id:
            where.append('d.user_id = ?')
            params.append(employee_id)
        if project_id:
            where.append('d.project_id = ?')
            params.append(project_id)
        if task_id:
            where.append('d.task_id = ?')
            params.append(task_id)
        if status:
            where.append('d.status = ?')
            params.append(status)
        if approval_status:
            where.append('d.approval_status = ?')
            params.append(approval_status)
        
        where_clause = ' AND '.join(where) if where else '1=1'
        
        # Get total count
        count_query = f'''
            SELECT COUNT(*) as count FROM daily_task_reports d
            WHERE {where_clause}
        '''
        cursor.execute(count_query, params)
        total = cursor.fetchone()['count']
        
        # Get paginated results
        offset = (page - 1) * per_page
        query = f'''
            SELECT d.*, 
                   u.username as employee_name, 
                   p.name as project_name,
                   t.title as task_name
            FROM daily_task_reports d
            LEFT JOIN users u ON d.user_id = u.id
            LEFT JOIN projects p ON d.project_id = p.id
            LEFT JOIN tasks t ON d.task_id = t.id
            WHERE {where_clause}
            ORDER BY d.report_date DESC, d.created_at DESC
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, params + [per_page, offset])
        reports = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'total': total,
            'page': page,
            'per_page': per_page,
            'data': [dict(r) for r in reports]
        }), 200
        
    except Exception as e:
        logger.exception('list_daily_reports_unified failed')
        return jsonify({'error': str(e)}), 500


@app.route('/api/daily-reports/<int:report_id>', methods=['PUT'])
@login_required
def update_daily_report_unified(report_id):
    """
    Unified daily report update endpoint.
    Replaces duplicate update functions.
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get report and verify ownership
        cursor.execute('SELECT user_id FROM daily_task_reports WHERE id = ?', (report_id,))
        report = cursor.fetchone()
        if not report:
            conn.close()
            return jsonify({'error': 'Report not found'}), 404
        
        # Only owner or admin can update
        cursor.execute('''
            SELECT ut.user_role FROM users u 
            JOIN usertypes ut ON u.user_type_id = ut.id 
            WHERE u.id = ?
        ''', (user_id,))
        role_row = cursor.fetchone()
        role = (role_row['user_role'] if role_row else 'employee').lower() if role_row else 'employee'
        
        if report['user_id'] != user_id and role not in ['admin', 'super admin']:
            conn.close()
            return jsonify({'error': 'You can only update your own reports'}), 403
        
        # Update allowed fields
        update_fields = []
        update_params = []
        
        allowed_fields = ['work_description', 'result_of_effort', 'remarks', 'time_spent', 
                         'status', 'blocker', 'communication_email', 'communication_phone']
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f'{field} = ?')
                update_params.append(data[field])
        
        if not update_fields:
            conn.close()
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_params.append(report_id)
        
        cursor.execute(f'''
            UPDATE daily_task_reports 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', update_params)
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.exception('update_daily_report_unified failed')
        return jsonify({'error': str(e)}), 500


@app.route('/api/daily-reports/<int:report_id>/action', methods=['POST'])
@login_required
def action_daily_report_unified(report_id):
    """
    Unified daily report action endpoint (approve/reject).
    Replaces duplicate action functions.
    """
    try:
        user_id = get_current_user_id()
        data = request.get_json() or {}
        action = data.get('action', '').lower()  # 'approve' or 'reject'
        
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Action must be approve or reject'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user role
        cursor.execute('''
            SELECT ut.user_role FROM users u 
            JOIN usertypes ut ON u.user_type_id = ut.id 
            WHERE u.id = ?
        ''', (user_id,))
        role_row = cursor.fetchone()
        role = (role_row['user_role'] if role_row else 'employee').lower() if role_row else 'employee'
        
        # Only admin/super admin can approve/reject
        if role not in ['admin', 'super admin']:
            conn.close()
            return jsonify({'error': 'Only admins can approve/reject reports'}), 403
        
        new_status = 'approved' if action == 'approve' else 'rejected'
        comment = data.get('comment', '')
        
        cursor.execute('''
            UPDATE daily_task_reports 
            SET approval_status = ?, comment = ?, approved_by_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_status, comment, user_id, report_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'approval_status': new_status}), 200
        
    except Exception as e:
        logger.exception('action_daily_report_unified failed')
        return jsonify({'error': str(e)}), 500


@app.route('/api/daily-reports/<int:report_id>', methods=['DELETE'])
@login_required
def delete_daily_report_unified(report_id):
    """
    Unified daily report deletion endpoint.
    Replaces duplicate delete functions.
    """
    try:
        user_id = get_current_user_id()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get report and verify ownership
        cursor.execute('SELECT user_id FROM daily_task_reports WHERE id = ?', (report_id,))
        report = cursor.fetchone()
        if not report:
            conn.close()
            return jsonify({'error': 'Report not found'}), 404
        
        # Get user role
        cursor.execute('''
            SELECT ut.user_role FROM users u 
            JOIN usertypes ut ON u.user_type_id = ut.id 
            WHERE u.id = ?
        ''', (user_id,))
        role_row = cursor.fetchone()
        role = (role_row['user_role'] if role_row else 'employee').lower() if role_row else 'employee'
        
        # Only owner or admin can delete
        if report['user_id'] != user_id and role not in ['admin', 'super admin']:
            conn.close()
            return jsonify({'error': 'You can only delete your own reports'}), 403
        
        cursor.execute('DELETE FROM daily_task_reports WHERE id = ?', (report_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.exception('delete_daily_report_unified failed')
        return jsonify({'error': str(e)}), 500


# ============================================================================
# 2. UNIFIED DASHBOARD STATS ENDPOINT
# ============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats_unified():
    """
    Unified dashboard stats endpoint with role-based filtering.
    Replaces: get_admin_dashboard_stats() + get_employee_dashboard_stats()
    """
    try:
        user_id = get_current_user_id()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user role
        cursor.execute('''
            SELECT ut.user_role FROM users u 
            JOIN usertypes ut ON u.user_type_id = ut.id 
            WHERE u.id = ?
        ''', (user_id,))
        role_row = cursor.fetchone()
        role = (role_row['user_role'] if role_row else 'employee').lower() if role_row else 'employee'
        
        stats = {}
        
        if role == 'super admin':
            # Super admin sees everything
            cursor.execute('SELECT COUNT(*) as count FROM projects WHERE status = "Active"')
            stats['active_projects'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM projects WHERE status = "Pending"')
            stats['pending_projects'] = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE status IN ("In Progress", "Pending")
            ''')
            stats['active_tasks'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "Pending"')
            stats['pending_tasks'] = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE status != "Completed" AND deadline < CURRENT_DATE
            ''')
            stats['overdue_tasks'] = cursor.fetchone()['count']
            
        elif role == 'project coordinator':
            # Coordinator sees their team's data
            cursor.execute('''
                SELECT COUNT(DISTINCT id) as count FROM projects 
                WHERE project_coordinator_id = ?
            ''', (user_id,))
            stats['active_projects'] = cursor.fetchone()['count']
            stats['pending_projects'] = 0
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE assigned_to_id IN (
                    SELECT id FROM users WHERE parent_user_id = ?
                ) AND status IN ("In Progress", "Pending")
            ''', (user_id,))
            stats['active_tasks'] = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE assigned_to_id IN (
                    SELECT id FROM users WHERE parent_user_id = ?
                ) AND status = "Pending"
            ''', (user_id,))
            stats['pending_tasks'] = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE assigned_to_id IN (
                    SELECT id FROM users WHERE parent_user_id = ?
                ) AND status != "Completed" AND deadline < CURRENT_DATE
            ''', (user_id,))
            stats['overdue_tasks'] = cursor.fetchone()['count']
            
        else:  # Employee
            # Employee sees their own data
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE assigned_to_id = ? AND status IN ("In Progress", "Pending")
            ''', (user_id,))
            stats['active_tasks'] = cursor.fetchone()['count']
            
            cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE assigned_to_id = ? AND status = "Pending"', (user_id,))
            stats['pending_tasks'] = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT COUNT(*) as count FROM tasks 
                WHERE assigned_to_id = ? AND status != "Completed" AND deadline < CURRENT_DATE
            ''', (user_id,))
            stats['overdue_tasks'] = cursor.fetchone()['count']
            
            # Projects they're assigned to
            cursor.execute('''
                SELECT COUNT(DISTINCT project_id) as count FROM project_team_members 
                WHERE user_id = ?
            ''', (user_id,))
            stats['active_projects'] = cursor.fetchone()['count']
            stats['pending_projects'] = 0
        
        conn.close()
        return jsonify(stats), 200
        
    except Exception as e:
        logger.exception('get_dashboard_stats_unified failed')
        return jsonify({'error': str(e)}), 500


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================
"""
STEPS TO INTEGRATE INTO app.py:

1. REMOVE these duplicate functions:
   - create_daily_report() [line ~951]
   - create_daily_report_api() [line ~1534]
   - list_daily_reports() [line ~1068]
   - list_daily_reports_api() [line ~1602]
   - update_daily_report() first version [line ~1145]
   - update_daily_report() second version [line ~1689]
   - action_daily_report() [line ~1205]
   - action_daily_report_api() [line ~1794]
   - delete_daily_report() [line ~1242]
   - delete_daily_report_api() [line ~1855]
   - get_admin_dashboard_stats() [line ~1457]
   - get_employee_dashboard_stats() [line ~3455]

2. REPLACE with the unified functions above

3. ADD ROUTE ALIASES for backward compatibility

4. TEST all endpoints:
   - POST /api/daily-reports
   - GET /api/daily-reports
   - PUT /api/daily-reports/{id}
   - POST /api/daily-reports/{id}/action
   - DELETE /api/daily-reports/{id}
   - GET /api/dashboard/stats

5. UPDATE HTML AJAX calls to use new endpoint paths if needed
"""
