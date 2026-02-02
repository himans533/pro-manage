# Pro-Manage Project Management System - Setup & Running Guide

## Project Overview
**Pro-Manage** is a professional project management system with role-based hierarchy and real-time project tracking built with Python Flask and SQLite.

### Technology Stack
- **Backend**: Python Flask 3.1.2+
- **Database**: SQLite3
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Security**: Flask-CORS, Werkzeug, password hashing with bcrypt

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Install Python Dependencies

```bash
# Navigate to AdminLoginPanel directory
cd AdminLoginPanel

# Install required packages
pip install -r requirements.txt
```

### Step 2: Initialize Database
The database will auto-initialize on first run, but you can pre-initialize it:

```bash
python check_db_script.py
```

This creates the SQLite database with all necessary tables:
- users (with hierarchy via parent_user_id)
- projects (with project_coordinator_id)
- project_team_members (team assignments)
- tasks (with status tracking)
- milestones (project phases)
- daily_reports (employee activities)
- activities (audit log)

---

## Running the Application

### Method 1: Using the Run Script (Recommended)

```bash
# From project root directory
python run.py
```

This will:
1. Initialize database if needed
2. Start Flask development server
3. Run on http://0.0.0.0:5000

### Method 2: Using npm scripts

```bash
# Development mode with auto-reload
npm run dev

# Or production mode
npm start
```

### Method 3: Direct Python Execution

```bash
cd AdminLoginPanel
python app.py
```

---

## Accessing the Application

Once running, open your browser and navigate to:

```
http://localhost:5000
```

### Default Login Credentials

| Role | Email | Password | OTP |
|------|-------|----------|-----|
| Super Admin | anubha@gmail.com | Anubha@#46 | 654321 |

**Note**: You can set custom credentials via environment variables:
```bash
export ADMIN_EMAIL="your@email.com"
export ADMIN_PASSWORD="YourPassword"
export ADMIN_OTP="123456"
```

---

## Project Structure

```
pro-manage/
├── AdminLoginPanel/
│   ├── app.py                      # Main Flask application
│   ├── models.py                   # Database models
│   ├── requirements.txt            # Python dependencies
│   ├── check_db_script.py          # Database initialization
│   ├── project_management.db       # SQLite database (auto-created)
│   ├── templates/
│   │   ├── admin-dashboard.html    # Admin dashboard
│   │   ├── employee-dashboard.html # Employee dashboard
│   │   ├── project-detail.html     # Project details
│   │   ├── admin-daily-reports.html # Daily reports
│   │   └── ...
│   ├── static/
│   │   ├── css/                    # Stylesheets
│   │   ├── js/                     # JavaScript files
│   │   └── images/                 # Images & assets
│   └── uploads/
│       └── profiles/               # User profile pictures
├── scripts/                        # Implementation reference files
├── run.py                          # Main entry point
├── package.json                    # Node/npm configuration
└── SETUP_AND_RUN_GUIDE.md         # This file
```

---

## Features Implemented

### 1. User Hierarchy System
- **Super Admin** → Sees everything, manages coordinators
- **Project Coordinator** → Sees their projects and team members
- **Team Member** → Sees only assigned tasks

### 2. Project Management
- Create/edit projects with coordinator assignment
- Add 2-3 team members per project
- Track project status (Active/Pending)
- Assign milestones and tasks

### 3. Task Management
- Create tasks under milestones
- Assign tasks to team members
- Track task status (Pending/In Progress/Completed)
- Monitor deadlines and overdue tasks

### 4. Dashboard Features
- Real-time statistics cards (5 metrics)
- Interactive organization hierarchy
- Coordinator details view with team breakdown
- Daily reports and activities

### 5. Authorization & Security
- Role-based access control (RBAC)
- Multi-layer authorization checks
- Secure password hashing
- OTP verification
- Session management

---

## Important Endpoints

### Authentication
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /verify-otp` - OTP verification

### Admin Endpoints
- `GET /admin` - Admin dashboard
- `GET /api/hierarchy/full` - Full organization hierarchy
- `GET /api/coordinator/<id>/details` - Coordinator details

### Employee Endpoints
- `GET /employee` - Employee dashboard
- `GET /api/employee/projects` - User's projects (filtered by role)
- `GET /api/employee/tasks` - User's tasks

### Project Management
- `POST /api/projects` - Create project
- `GET /api/projects/<id>` - Get project details
- `POST /api/projects/<id>/team-members` - Add team members

### Task Management
- `POST /api/tasks` - Create task
- `GET /api/tasks/<id>` - Get task details
- `PUT /api/tasks/<id>` - Update task status

### Dashboard Stats
- `GET /api/dashboard/stats` - Get 5 dashboard metrics

---

## Database Initialization

The database is automatically created with the following schema on first run:

```
users
├── id (PK)
├── username
├── email
├── password_hash
├── user_type (Super Admin, Project Coordinator, Team Member)
├── parent_user_id (FK - for hierarchy)
└── created_at

projects
├── id (PK)
├── project_name
├── description
├── status
├── created_by_id (FK)
├── project_coordinator_id (FK)
└── created_at

project_team_members
├── id (PK)
├── project_id (FK)
├── user_id (FK)
└── joined_at

tasks
├── id (PK)
├── task_name
├── description
├── status
├── priority
├── assigned_to_id (FK)
├── project_id (FK)
├── milestone_id (FK)
├── deadline
└── created_at

... and more tables for milestones, daily_reports, activities
```

---

## Troubleshooting

### Issue: "Missing script 'dev'"
**Solution**: This error occurs when npm can't find the dev script. Use:
```bash
python run.py
```
Or update package.json with correct scripts.

### Issue: Database locked
**Solution**: The database file might be corrupted or locked. Delete and reinitialize:
```bash
cd AdminLoginPanel
rm project_management.db
python check_db_script.py
```

### Issue: Port 5000 already in use
**Solution**: Use a different port:
```bash
PORT=8000 python run.py
```

### Issue: Module not found errors
**Solution**: Ensure all dependencies are installed:
```bash
pip install -r AdminLoginPanel/requirements.txt
```

### Issue: Templates not found
**Solution**: Ensure you're running from the correct directory:
```bash
cd pro-manage
python run.py
```

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| PORT | 5000 | Server port |
| ADMIN_EMAIL | anubha@gmail.com | Super admin email |
| ADMIN_PASSWORD | Anubha@#46 | Super admin password |
| ADMIN_OTP | 654321 | Super admin OTP |
| FLASK_ENV | production | Flask environment |

Set them in your system or in a `.env` file:

```bash
export PORT=5000
export ADMIN_EMAIL="your@email.com"
export ADMIN_PASSWORD="SecurePassword123"
export ADMIN_OTP="123456"
```

---

## Testing

Run the test suite:

```bash
cd AdminLoginPanel
python -m pytest
```

Or run specific tests:

```bash
python test_smoke.py
python test_daily_reports.py
python test_migration.py
```

---

## Performance Tips

1. **Database Optimization**
   - Indexes are created on frequently queried columns
   - Foreign key constraints are enabled
   - WAL mode is enabled for better concurrency

2. **Caching**
   - Dashboard stats are cached when possible
   - Consider implementing Redis for production

3. **Lazy Loading**
   - Large lists are paginated
   - Images are optimized before upload

---

## Security Considerations

1. **In Production**
   - Set `debug=False` in app.run()
   - Use strong SECRET_KEY (not hardcoded)
   - Set up HTTPS with SSL certificate
   - Use environment variables for sensitive data
   - Implement rate limiting
   - Use database backups

2. **Default Credentials**
   - Change admin password on first login
   - Remove default OTP
   - Use strong, unique passwords

---

## Next Steps

1. **First Login**: Use default admin credentials
2. **Create Users**: Add project coordinators and team members
3. **Create Projects**: Assign coordinators and team members
4. **Create Milestones**: Break down projects into phases
5. **Create Tasks**: Assign tasks to team members
6. **Monitor Dashboard**: Track progress and metrics

---

## Support & Documentation

For detailed information about features:
- See `/IMPLEMENTATION_GUIDE.md` for feature overview
- See `/INTEGRATION_CHECKLIST.md` for integration steps
- See `/CLEANUP_SUMMARY.md` for code organization
- Check the `/scripts` directory for implementation reference

---

## License
MIT License - Feel free to use this project as a template for your own systems.

**Happy Project Managing! 🚀**
