-- ============================================================================
-- MIGRATION: Add Project Coordinator Assignment to Projects
-- ============================================================================
-- Safe, non-destructive migration to add project_coordinator_id column
-- Allows Super Admin to assign a Project Coordinator when creating a project
-- ============================================================================

-- Step 1: Add project_coordinator_id column (nullable, defaults to NULL)
-- This allows projects to be created without a coordinator initially
ALTER TABLE projects ADD COLUMN project_coordinator_id INTEGER DEFAULT NULL;

-- Step 2: Create foreign key constraint linking to users table
-- This ensures referential integrity - coordinator must be a valid user
ALTER TABLE projects ADD CONSTRAINT fk_project_coordinator 
  FOREIGN KEY (project_coordinator_id) REFERENCES users(id) ON DELETE SET NULL;

-- Step 3: Create index for faster lookups when querying projects by coordinator
-- This improves performance for queries like "get all projects assigned to coordinator X"
CREATE INDEX IF NOT EXISTS idx_project_coordinator_id ON projects(project_coordinator_id);

-- Step 4: Verify migration success (SELECT should return the new column)
-- Run this query to verify: PRAGMA table_info(projects);

-- ============================================================================
-- HOW TO USE:
-- ============================================================================
-- 1. When Super Admin creates a project:
--    - A dropdown appears with all users where user_type_id points to 'Project Coordinator'
-- 
-- 2. Upon selection:
--    INSERT INTO projects (..., project_coordinator_id) VALUES (..., :coordinator_id)
--
-- 3. To query a coordinator's projects:
--    SELECT * FROM projects WHERE project_coordinator_id = :coordinator_id
--
-- 4. To list projects WITHOUT a coordinator:
--    SELECT * FROM projects WHERE project_coordinator_id IS NULL
--
-- ============================================================================
