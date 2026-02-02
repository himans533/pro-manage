-- Create project_team_members table to store team assignments
-- This table links projects to team members (employees) assigned by the Project Coordinator

CREATE TABLE IF NOT EXISTS project_team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(project_id, user_id)  -- Prevent duplicate team member assignments
);

-- Create index for efficient queries
CREATE INDEX IF NOT EXISTS idx_project_team_members_project_id 
ON project_team_members(project_id);

CREATE INDEX IF NOT EXISTS idx_project_team_members_user_id 
ON project_team_members(user_id);

-- Verify the table structure
-- SELECT * FROM project_team_members;
-- SELECT COUNT(*) as team_count FROM project_team_members WHERE project_id = ?;
