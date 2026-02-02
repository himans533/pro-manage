-- =============================================
-- USER HIERARCHY MIGRATION
-- Description: Add parent_user_id column to enable hierarchical user structure
-- Date: 2026-02-02
-- =============================================

-- Add parent_user_id column to users table
-- This is NON-DESTRUCTIVE: does not modify existing data or tables
ALTER TABLE users ADD COLUMN parent_user_id INTEGER DEFAULT NULL;

-- Add foreign key constraint for parent_user_id
-- Self-referential foreign key: a user can have a parent user
ALTER TABLE users ADD CONSTRAINT fk_parent_user 
FOREIGN KEY (parent_user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Create index on parent_user_id for efficient hierarchical queries
CREATE INDEX IF NOT EXISTS idx_parent_user_id ON users(parent_user_id);

-- =============================================
-- HIERARCHY EXPLANATION:
-- =============================================
-- 
-- The parent_user_id column establishes a user hierarchy:
--
-- 1. SUPER ADMIN
--    - parent_user_id = NULL
--    - Top-level administrator
--    - Has no parent user
--
-- 2. PROJECT COORDINATOR
--    - parent_user_id = Super Admin's user ID
--    - Managed by a Super Admin
--    - Responsible for multiple projects/teams
--
-- 3. TEAM MEMBER
--    - parent_user_id = Project Coordinator's user ID
--    - Managed by a Project Coordinator
--    - Works on assigned tasks
--
-- =============================================
-- USAGE EXAMPLES:
-- =============================================
--
-- Get all Project Coordinators for a Super Admin:
--   SELECT * FROM users WHERE parent_user_id = ? AND user_type_id = 2
--
-- Get all Team Members under a Project Coordinator:
--   SELECT * FROM users WHERE parent_user_id = ? AND user_type_id = 3
--
-- Get the full hierarchy chain for a user (recursive):
--   WITH RECURSIVE user_hierarchy AS (
--     SELECT id, username, parent_user_id, 1 as level
--     FROM users WHERE id = ?
--     UNION ALL
--     SELECT u.id, u.username, u.parent_user_id, uh.level + 1
--     FROM users u
--     JOIN user_hierarchy uh ON u.id = uh.parent_user_id
--   )
--   SELECT * FROM user_hierarchy
--
-- Check if user is a direct report of another:
--   SELECT COUNT(*) > 0 FROM users WHERE id = ? AND parent_user_id = ?
--
-- =============================================
