const express = require('express');
const path = require('path');
const session = require('express-session');
const app = express();

// Middleware
app.use(express.static(path.join(__dirname, 'AdminLoginPanel', 'static')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(session({
  secret: 'your-secret-key',
  resave: false,
  saveUninitialized: true
}));

// View engine
app.set('view engine', 'html');
app.set('views', path.join(__dirname, 'AdminLoginPanel', 'templates'));

// Mock user data
const users = {
  'superadmin@test.com': { id: 1, name: 'Super Admin', role: 'Super Admin', password: 'admin123' },
  'coordinator@test.com': { id: 2, name: 'John Coordinator', role: 'Project Coordinator', password: 'coord123' },
  'employee@test.com': { id: 3, name: 'Jane Employee', role: 'Team Member', password: 'emp123' }
};

// Mock projects data
const projects = [
  { id: 1, name: 'Project Alpha', status: 'Active', coordinator_id: 2, team_count: 3, task_count: 12 },
  { id: 2, name: 'Project Beta', status: 'Pending', coordinator_id: 2, team_count: 2, task_count: 8 }
];

// Mock tasks data
const tasks = [
  { id: 1, title: 'Task 1', project_id: 1, assigned_to: 3, status: 'In Progress', priority: 'High', deadline: '2026-03-15' },
  { id: 2, title: 'Task 2', project_id: 1, assigned_to: 3, status: 'Pending', priority: 'Medium', deadline: '2026-03-20' }
];

// Login route
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const user = users[email];
  
  if (user && user.password === password) {
    req.session.user = user;
    return res.redirect('/admin' + (user.role === 'Super Admin' ? '-dashboard' : user.role === 'Project Coordinator' ? '-dashboard' : '-dashboard'));
  }
  
  res.redirect('/');
});

// Logout
app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

// Login page
app.get('/', (req, res) => {
  if (req.session.user) {
    return res.redirect(req.session.user.role === 'Super Admin' ? '/admin-dashboard' : '/employee-dashboard');
  }
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Pro-Manage Login</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
        h1 { color: #333; margin-bottom: 30px; text-align: center; font-size: 28px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
        .demo-users { margin-top: 30px; padding-top: 30px; border-top: 1px solid #eee; }
        .demo-users p { color: #666; margin-bottom: 15px; font-size: 14px; }
        .user-button { display: block; margin-bottom: 10px; padding: 10px; background: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; text-align: center; cursor: pointer; transition: 0.2s; text-decoration: none; color: #333; }
        .user-button:hover { background: #eee; }
      </style>
    </head>
    <body>
      <div class="login-container">
        <h1>Pro-Manage</h1>
        <p style="text-align: center; color: #666; margin-bottom: 30px;">Project Management System</p>
        
        <form method="POST" action="/login">
          <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" required>
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" required>
          </div>
          <button type="submit">Login</button>
        </form>

        <div class="demo-users">
          <p><strong>Demo Credentials:</strong></p>
          <button class="user-button" onclick="autofill('superadmin@test.com', 'admin123')">
            Super Admin (See Everything)
          </button>
          <button class="user-button" onclick="autofill('coordinator@test.com', 'coord123')">
            Project Coordinator (See Own Projects)
          </button>
          <button class="user-button" onclick="autofill('employee@test.com', 'emp123')">
            Team Member (See Own Tasks)
          </button>
        </div>
      </div>

      <script>
        function autofill(email, password) {
          document.querySelector('input[name="email"]').value = email;
          document.querySelector('input[name="password"]').value = password;
          document.querySelector('form').submit();
        }
      </script>
    </body>
    </html>
  `);
});

// Admin Dashboard
app.get('/admin-dashboard', (req, res) => {
  if (!req.session.user) return res.redirect('/');
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Admin Dashboard - Pro-Manage</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 24px; }
        .navbar a { color: white; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .welcome { background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .welcome h2 { color: #333; margin-bottom: 10px; }
        .welcome p { color: #666; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #667eea; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }
        .stat-card .number { font-size: 36px; font-weight: bold; color: #333; }
        .projects { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .projects h3 { color: #333; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f5f5f5; padding: 12px; text-align: left; color: #333; font-weight: 600; }
        td { padding: 12px; border-bottom: 1px solid #eee; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .status-active { background: #d4edda; color: #155724; }
        .status-pending { background: #fff3cd; color: #856404; }
        .logout-btn { background: #dc3545; padding: 8px 16px; border-radius: 5px; border: none; color: white; cursor: pointer; }
      </style>
    </head>
    <body>
      <div class="navbar">
        <h1>Pro-Manage Admin Dashboard</h1>
        <div>
          <span>Welcome, ${req.session.user.name}</span>
          <a href="/logout" class="logout-btn">Logout</a>
        </div>
      </div>

      <div class="container">
        <div class="welcome">
          <h2>Welcome, ${req.session.user.name}!</h2>
          <p>You are logged in as <strong>${req.session.user.role}</strong>. You can see all projects, teams, and tasks in the system.</p>
        </div>

        <div class="stats">
          <div class="stat-card">
            <h3>Total Projects</h3>
            <div class="number">${projects.length}</div>
          </div>
          <div class="stat-card">
            <h3>Total Tasks</h3>
            <div class="number">${tasks.length}</div>
          </div>
          <div class="stat-card">
            <h3>Active Projects</h3>
            <div class="number">${projects.filter(p => p.status === 'Active').length}</div>
          </div>
          <div class="stat-card">
            <h3>In Progress Tasks</h3>
            <div class="number">${tasks.filter(t => t.status === 'In Progress').length}</div>
          </div>
        </div>

        <div class="projects">
          <h3>All Projects</h3>
          <table>
            <thead>
              <tr>
                <th>Project Name</th>
                <th>Status</th>
                <th>Team Members</th>
                <th>Tasks</th>
              </tr>
            </thead>
            <tbody>
              ${projects.map(p => `
                <tr>
                  <td>${p.name}</td>
                  <td><span class="status-badge status-${p.status.toLowerCase()}">${p.status}</span></td>
                  <td>${p.team_count}</td>
                  <td>${p.task_count}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
  `);
});

// Employee Dashboard
app.get('/employee-dashboard', (req, res) => {
  if (!req.session.user) return res.redirect('/');
  
  const userTasks = tasks.filter(t => req.session.user.role !== 'Super Admin' ? (req.session.user.role === 'Team Member' ? t.assigned_to === req.session.user.id : true) : true);
  
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Employee Dashboard - Pro-Manage</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 24px; }
        .navbar a { color: white; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .welcome { background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .welcome h2 { color: #333; margin-bottom: 10px; }
        .welcome p { color: #666; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #667eea; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }
        .stat-card .number { font-size: 36px; font-weight: bold; color: #333; }
        .tasks { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .tasks h3 { color: #333; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f5f5f5; padding: 12px; text-align: left; color: #333; font-weight: 600; }
        td { padding: 12px; border-bottom: 1px solid #eee; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .status-in-progress { background: #cfe2ff; color: #084298; }
        .status-pending { background: #fff3cd; color: #664d03; }
        .priority-high { color: #dc3545; font-weight: 600; }
        .priority-medium { color: #ffc107; font-weight: 600; }
        .logout-btn { background: #dc3545; padding: 8px 16px; border-radius: 5px; border: none; color: white; cursor: pointer; }
      </style>
    </head>
    <body>
      <div class="navbar">
        <h1>Pro-Manage Employee Dashboard</h1>
        <div>
          <span>Welcome, ${req.session.user.name}</span>
          <a href="/logout" class="logout-btn">Logout</a>
        </div>
      </div>

      <div class="container">
        <div class="welcome">
          <h2>Welcome, ${req.session.user.name}!</h2>
          <p>You are logged in as <strong>${req.session.user.role}</strong>. ${req.session.user.role === 'Team Member' ? 'You can see only your assigned tasks.' : 'You can see projects and tasks in your scope.'}</p>
        </div>

        <div class="stats">
          <div class="stat-card">
            <h3>My Tasks</h3>
            <div class="number">${userTasks.length}</div>
          </div>
          <div class="stat-card">
            <h3>In Progress</h3>
            <div class="number">${userTasks.filter(t => t.status === 'In Progress').length}</div>
          </div>
          <div class="stat-card">
            <h3>Pending</h3>
            <div class="number">${userTasks.filter(t => t.status === 'Pending').length}</div>
          </div>
        </div>

        <div class="tasks">
          <h3>${req.session.user.role === 'Team Member' ? 'My Assigned Tasks' : 'Tasks'}</h3>
          <table>
            <thead>
              <tr>
                <th>Task Title</th>
                <th>Project</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Deadline</th>
              </tr>
            </thead>
            <tbody>
              ${userTasks.map(t => `
                <tr>
                  <td>${t.title}</td>
                  <td>${projects.find(p => p.id === t.project_id)?.name || 'Unknown'}</td>
                  <td><span class="status-badge status-${t.status.toLowerCase().replace(' ', '-')}">${t.status}</span></td>
                  <td><span class="priority-${t.priority.toLowerCase()}">${t.priority}</span></td>
                  <td>${t.deadline}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </body>
    </html>
  `);
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`[v0] Pro-Manage server running on http://localhost:${PORT}`);
});
