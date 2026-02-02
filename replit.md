# Admin Login Panel

## Overview
An Admin Login Panel application for Employee and Admin Management. This Flask-based web application provides a secure dashboard for managing employees, projects, tasks, and daily reports.

## Project Structure
```
AdminLoginPanel/
├── app.py              # Main Flask application (routes, database, API)
├── models.py           # Database models
├── templates/          # HTML templates
│   ├── login.html
│   ├── admin-dashboard.html
│   ├── employee-dashboard.html
│   ├── super-admin-dashboard.html
│   └── ...
├── static/             # Static assets (CSS, JS, images)
├── uploads/            # User profile uploads
└── project_management.db  # SQLite database (auto-created)
```

## Tech Stack
- **Backend**: Python 3.12, Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Jinja2 templates)
- **Dependencies**: flask, flask-cors, werkzeug, pillow, gunicorn

## Running the Application
The application runs on port 5000 via the configured workflow:
```bash
cd AdminLoginPanel && python app.py
```

## Default Admin Credentials
- Email: anubha@gmail.com
- Password: Anubha@#46
- OTP: 654321

These can be configured via environment variables:
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`
- `ADMIN_OTP`

## Recent Changes
- 2026-02-02: Initial import and Replit environment setup
