-- Migration: Add project_team_members table for coordinator team assignments
-- Purpose: Store team members assigned by Project Coordinators to specific projects
-- This table is separate from project_assignments to maintain granular control

-- Create the project_team_members table
CREATE TABLE IF NOT EXISTS project_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_by_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by_id) REFERENCES users(id),
    
    -- Ensure no duplicate assignments
    UNIQUE(project_id, user_id)
);

-- Create index for fast lookups by project
CREATE INDEX IF NOT EXISTS idx_project_team_members_project_id 
ON project_team_members(project_id);

-- Create index for fast lookups by user
CREATE INDEX IF NOT EXISTS idx_project_team_members_user_id 
ON project_team_members(user_id);

-- Create index for fast lookups by assigned_by
CREATE INDEX IF NOT EXISTS idx_project_team_members_assigned_by 
ON project_team_members(assigned_by_id);

-- View: Get project team members with details
CREATE VIEW IF NOT EXISTS project_team_members_detail AS
SELECT 
    ptm.id,
    ptm.project_id,
    ptm.user_id,
    ptm.assigned_by_id,
    ptm.assigned_at,
    u.username,
    u.email,
    ut.user_role,
    coord.username as assigned_by_name,
    p.title as project_title
FROM project_team_members ptm
JOIN users u ON ptm.user_id = u.id
LEFT JOIN usertypes ut ON u.user_type_id = ut.id
JOIN users coord ON ptm.assigned_by_id = coord.id
JOIN projects p ON ptm.project_id = p.id;

-- Comment: This table works alongside existing project_assignments table
-- - project_assignments: For general project team assignments
-- - project_team_members: For coordinator-specific team member assignments to their projects
