/**
 * TASK ASSIGNMENT FRONTEND CHANGES
 * ==================================
 * Filters "Assign Employee" dropdown to show only project team members
 * when a Project Coordinator creates a task.
 * 
 * Location: employee-dashboard.html JavaScript section (around line 3750)
 */

// =============================================================================
// REPLACEMENT FUNCTION
// =============================================================================
// Find this function around line 3751 in employee-dashboard.html:
// "const assigneeSelect = document.getElementById("taskAssignee");"
// 
// REPLACE the entire section (lines 3751-3755) with this:

async function populateTaskAssigneeDropdown(projectId) {
    /**
     * Load eligible assignees for the selected project.
     * 
     * If user is Project Coordinator:
     *  - Shows only employees from project_team_members table
     * 
     * If user is regular Employee:
     *  - Shows all employees (backward compatible)
     */
    
    const assigneeSelect = document.getElementById("taskAssignee");
    if (!assigneeSelect) return;
    
    try {
        // Set loading state
        assigneeSelect.innerHTML = '<option value="">Loading...</option>';
        
        // Fetch eligible assignees for this project
        const token = localStorage.getItem('employee_token');
        const response = await fetch(
            `${API_BASE}/projects/${projectId}/eligible-assignees`,
            {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        if (!response.ok) {
            console.error("[v0] Failed to fetch eligible assignees:", response.status);
            assigneeSelect.innerHTML = '<option value="">Error loading employees</option>';
            return;
        }
        
        const assignees = await response.json();
        
        // Populate dropdown with team members
        assigneeSelect.innerHTML = '<option value="">Unassigned</option>' +
            assignees.map(emp => 
                `<option value="${emp.id}">${emp.username}</option>`
            ).join('');
        
        console.log("[v0] Assignee dropdown populated with", assignees.length, "team members");
        
    } catch (error) {
        console.error("[v0] Error populating assignee dropdown:", error);
        assigneeSelect.innerHTML = '<option value="">Error loading employees</option>';
    }
}


// =============================================================================
// INTEGRATION POINT #1: Task Project Selection Change
// =============================================================================
// Find the function that updates the task form when "taskProject" changes
// Add this event listener in the same section (around line 3800):

// Add event listener to "Select Project" dropdown in task form:
document.addEventListener('DOMContentLoaded', function() {
    const taskProjectSelect = document.getElementById("taskProject");
    if (taskProjectSelect) {
        taskProjectSelect.addEventListener('change', function() {
            // When project changes, reload eligible assignees for that project
            if (this.value) {
                populateTaskAssigneeDropdown(parseInt(this.value));
            }
        });
    }
});


// =============================================================================
// INTEGRATION POINT #2: Update Modal Opening
// =============================================================================
// Find the function: openCreateTaskModal() around line 3798
// REPLACE it with this version:

function openCreateTaskModal() {
    const modal = document.getElementById("createTaskModal");
    if (modal) {
        modal.classList.add("active");
    }
    
    // Reset assignee dropdown when modal opens
    const assigneeSelect = document.getElementById("taskAssignee");
    if (assigneeSelect) {
        assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
    }
}


// =============================================================================
// INTEGRATION POINT #3: Update Initial Data Load
// =============================================================================
// Find the section around line 3740-3755 where projects and employees are loaded:
// 
// ORIGINAL CODE (lines 3751-3755):
// const assigneeSelect = document.getElementById("taskAssignee");
// if (assigneeSelect) {
//     assigneeSelect.innerHTML = '<option value="">Unassigned</option>' +
//         allEmployees.map((e) => `<option value="${e.id}">${e.username}</option>`).join("");
// }
//
// REPLACE WITH:

async function updateTaskFormDropdowns(projects) {
    /**
     * Update all task form dropdowns with project and assignee data
     */
    
    // Update project selects
    const selects = [
        document.getElementById("taskProject"),
        document.getElementById("milestoneProject"),
        document.getElementById("documentProject"),
        document.getElementById("reportProjectId"),
    ];
    
    selects.forEach((select) => {
        if (select) {
            select.innerHTML = '<option value="">Select a project</option>' +
                projects.map((p) => `<option value="${p.id}">${p.title}</option>`).join("");
        }
    });
    
    // Initialize assignee dropdown
    // IMPORTANT: This now shows as empty, will populate when project is selected
    const assigneeSelect = document.getElementById("taskAssignee");
    if (assigneeSelect) {
        assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
    }
}


// =============================================================================
// INTEGRATION POINT #4: Update createTask() Function
// =============================================================================
// Find the function: createTask(event) around line 3980
// 
// The task creation already uses projectId, so when submitted:
// - Frontend sends: project_id (coordinator's project)
// - Backend validates: assigned_to_id must be in project_team_members
//
// NO CHANGES NEEDED - Backend validation handles it


// =============================================================================
// BACKEND VALIDATION (add to app.py around line 3001)
// =============================================================================
// Add this validation in create_employee_task() after verifying assigned_to_id exists:
/*
        # NEW VALIDATION: If coordinator, verify assigned employee is in project team
        if assigned_to_id:
            cursor.execute('SELECT user_type FROM users WHERE id = ?', (user_id,))
            user_record = cursor.fetchone()
            
            if user_record and user_record['user_type'] == 'Project Coordinator':
                # Coordinator can only assign from project_team_members
                cursor.execute('''
                    SELECT 1 FROM project_team_members 
                    WHERE project_id = ? AND user_id = ?
                ''', (project_id, assigned_to_id))
                
                if not cursor.fetchone():
                    return jsonify({
                        "error": "This employee is not assigned to this project. "
                               "Please add them to the project team first."
                    }), 403
*/


// =============================================================================
// SUMMARY OF CHANGES
// =============================================================================
/*
1. Add new function: populateTaskAssigneeDropdown(projectId)
   - Fetches eligible assignees from backend endpoint
   - Shows only project team members for Coordinators
   
2. Update: Task project select change event
   - Calls populateTaskAssigneeDropdown() when project changes
   
3. Update: openCreateTaskModal()
   - Resets dropdown when modal opens
   
4. Update: updateTaskFormDropdowns()
   - Initializes empty assignee list (will populate on project selection)
   
5. Backend: Add validation in create_employee_task()
   - Ensures Coordinators can only assign team members
*/
