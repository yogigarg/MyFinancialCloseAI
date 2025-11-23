# FinClose AI - Windows Installation Guide

Complete step-by-step guide to run FinClose AI on Windows.

---

## 📋 Prerequisites Installation

### Step 1: Install Docker Desktop for Windows

**Docker Desktop includes Docker Engine, Docker Compose, and everything you need.**

1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop
   - Click "Download for Windows"
   - Save the installer

2. **Install Docker Desktop**
   - Run `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - **Important**: Enable WSL 2 backend when prompted (recommended)
   - Restart your computer if prompted

3. **Start Docker Desktop**
   - Search for "Docker Desktop" in Start menu
   - Launch the application
   - Wait for Docker to start (icon in system tray will turn green)

4. **Verify Installation**
   ```powershell
   # Open PowerShell and run:
   docker --version
   docker-compose --version
   ```
   
   You should see version numbers like:
   ```
   Docker version 24.0.x
   Docker Compose version v2.x.x
   ```

### Step 2: Install Python 3.11+

1. **Download Python**
   - Go to: https://www.python.org/downloads/
   - Download Python 3.11 or higher (3.12 works too)

2. **Install Python**
   - Run the installer
   - ✅ **IMPORTANT**: Check "Add Python to PATH" at bottom
   - Click "Install Now"

3. **Verify Installation**
   ```powershell
   python --version
   ```
   
   Should show: `Python 3.11.x` or higher

### Step 3: Install Git for Windows (Optional but Recommended)

1. **Download Git**
   - Go to: https://git-scm.com/download/win
   - Download and run installer

2. **Install with defaults**
   - Accept all default settings
   - This gives you Git Bash (a Unix-like terminal)

---

## 📦 Download & Extract FinClose AI

### Option 1: Download ZIP from Claude

1. Download `finclose-ai.zip` from the link provided
2. Right-click the ZIP file → Extract All
3. Choose a location (e.g., `C:\Projects\finclose-ai`)
4. Open the extracted folder

### Option 2: Clone from Repository (if available)

```powershell
cd C:\Projects
git clone <repository-url>
cd finclose-ai
```

---

## ⚙️ Configuration

### Step 1: Configure Environment Variables

1. **Copy the example file**
   ```powershell
   # In PowerShell, navigate to project folder:
   cd C:\Projects\finclose-ai
   
   # Copy the template
   copy .env.example .env
   ```

2. **Edit .env file**
   ```powershell
   # Open in Notepad
   notepad .env
   
   # Or use VS Code if installed
   code .env
   ```

3. **Fill in your credentials**
   ```bash
   # NetSuite Configuration (REQUIRED)
   NETSUITE_ACCOUNT_ID=your_account_id
   NETSUITE_CONSUMER_KEY=your_consumer_key
   NETSUITE_CONSUMER_SECRET=your_consumer_secret
   NETSUITE_TOKEN_ID=your_token_id
   NETSUITE_TOKEN_SECRET=your_token_secret
   NETSUITE_REST_URL=https://your-account.suitetalk.api.netsuite.com
   
   # Anthropic API (REQUIRED)
   ANTHROPIC_API_KEY=sk-ant-api03-...
   
   # Database Password (CHANGE THIS!)
   POSTGRES_PASSWORD=your_secure_password_here
   
   # Optional: LangSmith for monitoring
   LANGSMITH_API_KEY=your_langsmith_key
   ```

4. **Save and close** the file

---

## 🚀 Run Setup Script

### Option 1: Automated Setup (PowerShell)

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to project**
   ```powershell
   cd C:\Projects\finclose-ai
   ```

3. **Allow script execution** (first time only)
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Run setup script**
   ```powershell
   .\setup-windows.ps1
   ```

5. **Wait for completion** (5-10 minutes first time)

### Option 2: Manual Setup (PowerShell)

If the script doesn't work, follow these steps:

1. **Open PowerShell**
   ```powershell
   cd C:\Projects\finclose-ai
   ```

2. **Create directories**
   ```powershell
   mkdir logs
   mkdir data\postgres
   mkdir data\redis
   mkdir data\uploads
   ```

3. **Build Docker images**
   ```powershell
   docker-compose build
   ```

4. **Start database services**
   ```powershell
   docker-compose up -d postgres redis
   ```

5. **Wait 30 seconds for PostgreSQL to start**
   ```powershell
   Start-Sleep -Seconds 30
   ```

6. **Initialize database**
   ```powershell
   # Create init script
   @"
   CREATE SCHEMA IF NOT EXISTS staging;
   CREATE SCHEMA IF NOT EXISTS processing;
   CREATE SCHEMA IF NOT EXISTS approval;
   CREATE SCHEMA IF NOT EXISTS output;
   CREATE SCHEMA IF NOT EXISTS workflow;
   CREATE SCHEMA IF NOT EXISTS audit;
   
   CREATE TABLE IF NOT EXISTS workflow.executions (
       id SERIAL PRIMARY KEY,
       workflow_type VARCHAR(50) NOT NULL,
       status VARCHAR(20) NOT NULL,
       started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       completed_at TIMESTAMP,
       error_message TEXT,
       metadata JSONB
   );
   
   CREATE TABLE IF NOT EXISTS approval.queue (
       id SERIAL PRIMARY KEY,
       request_id VARCHAR(50) UNIQUE NOT NULL,
       workflow_type VARCHAR(50) NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       status VARCHAR(20) NOT NULL,
       data JSONB NOT NULL,
       approver VARCHAR(100),
       approved_at TIMESTAMP,
       comments TEXT
   );
   
   CREATE TABLE IF NOT EXISTS audit.log (
       id SERIAL PRIMARY KEY,
       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       user_name VARCHAR(100),
       action VARCHAR(50) NOT NULL,
       resource_type VARCHAR(50),
       resource_id VARCHAR(100),
       details JSONB
   );
   
   CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow.executions(status);
   CREATE INDEX IF NOT EXISTS idx_approval_status ON approval.queue(status);
   CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit.log(timestamp);
   "@ | docker-compose exec -T postgres psql -U finclose -d finclose_ai
   ```

---

## 🎯 Start the Application

### Start All Services

```powershell
# Start all containers in background
docker-compose up -d

# Check that all services are running
docker-compose ps
```

You should see 5 services running:
- `finclose-postgres` (PostgreSQL database)
- `finclose-redis` (Redis cache)
- `finclose-mcp-server` (NetSuite integration)
- `finclose-streamlit` (Web UI)
- `finclose-agents` (Agent workers)

### Verify Services

```powershell
# Check logs
docker-compose logs -f

# Press Ctrl+C to stop viewing logs

# Check specific service
docker-compose logs streamlit-app

# Check service health
docker-compose ps
```

---

## 🌐 Access the Application

### Open in Browser

1. **Streamlit Web UI**
   - Open browser and go to: http://localhost:8501
   - Login with demo credentials:
     - Username: `justine` Password: `demo`
     - Username: `selena` Password: `demo`
     - Username: `will` Password: `demo`

2. **Test Other Endpoints**
   - MCP Server Health: http://localhost:8000/health
   - Agent API: http://localhost:8001

---

## 🧪 Test the System

### Run a Test Workflow

1. Login to Streamlit (http://localhost:8501)
2. Go to **Workflows** page
3. Click **ZIP Accrual** tab
4. Click "Start Workflow" button
5. Watch the progress in real-time!

### Expected Result
- Progress bar showing workflow steps
- Success message after ~30 seconds
- Approval request created
- Go to **Approvals** page to see the request

---

## 🔧 Common Commands

### Starting/Stopping Services

```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart streamlit-app

# Stop and remove all containers and data
docker-compose down -v
```

### Viewing Logs

```powershell
# All services (follow mode)
docker-compose logs -f

# Specific service
docker-compose logs -f streamlit-app
docker-compose logs -f mcp-server
docker-compose logs -f agent-workers

# Last 100 lines
docker-compose logs --tail=100

# Press Ctrl+C to exit log view
```

### Database Operations

```powershell
# Connect to PostgreSQL
docker-compose exec postgres psql -U finclose -d finclose_ai

# Inside PostgreSQL:
# \dt workflow.*          -- List tables in workflow schema
# \d workflow.executions  -- Describe table structure
# SELECT * FROM workflow.executions;  -- Query data
# \q                      -- Exit

# Backup database
docker-compose exec postgres pg_dump -U finclose finclose_ai > backup.sql

# Restore database
Get-Content backup.sql | docker-compose exec -T postgres psql -U finclose -d finclose_ai
```

### Rebuild After Code Changes

```powershell
# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Or rebuild specific service
docker-compose build streamlit-app
docker-compose up -d streamlit-app
```

---

## 🐛 Troubleshooting

### Issue: Docker Desktop Not Starting

**Solution:**
1. Check if Hyper-V is enabled (Windows Home needs WSL2)
2. Restart Docker Desktop
3. Check Windows Updates
4. Restart computer

### Issue: Port Already in Use

**Error:** `Bind for 0.0.0.0:8501 failed: port is already allocated`

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :8501

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change the port in docker-compose.yml
```

### Issue: PowerShell Script Won't Run

**Error:** `cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run setup again
.\setup-windows.ps1
```

### Issue: Database Connection Failed

**Solution:**
```powershell
# Reset database
docker-compose down -v
docker volume rm finclose-ai_postgres_data
docker-compose up -d postgres

# Wait 30 seconds
Start-Sleep -Seconds 30

# Run setup again
.\setup-windows.ps1
```

### Issue: Container Won't Start

**Solution:**
```powershell
# Check logs
docker-compose logs <service-name>

# Rebuild container
docker-compose build --no-cache <service-name>
docker-compose up -d <service-name>

# If all else fails, clean restart
docker-compose down -v
docker system prune -a  # WARNING: Removes all unused Docker data
.\setup-windows.ps1
docker-compose up -d
```

### Issue: Cannot Access http://localhost:8501

**Solution:**
1. Check if Docker is running: `docker-compose ps`
2. Check if container is healthy: `docker-compose logs streamlit-app`
3. Try: http://127.0.0.1:8501
4. Check Windows Firewall settings
5. Restart Docker Desktop

### Issue: Import Errors in Python

**Solution:**
```powershell
# Rebuild the containers
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Verify Everything is Working

Run this checklist:

```powershell
# 1. Check Docker is running
docker-compose ps

# Expected: All services with "Up" status

# 2. Check Streamlit
curl http://localhost:8501/_stcore/health

# Expected: HTTP 200 OK

# 3. Check MCP Server
curl http://localhost:8000/health

# Expected: JSON response

# 4. Check Database
docker-compose exec postgres psql -U finclose -d finclose_ai -c "SELECT 1"

# Expected: Returns 1

# 5. Check Redis
docker-compose exec redis redis-cli ping

# Expected: PONG
```

If all checks pass, you're ready to use FinClose AI! ✅

---

## 🎓 Next Steps

### Learn the System

1. **Read Documentation**
   - `START_HERE.md` - Overview
   - `QUICKSTART.md` - Quick guide
   - `README.md` - Full documentation
   - `PROJECT_OVERVIEW.md` - What's implemented

2. **Try Demo Workflows**
   - Login to http://localhost:8501
   - Run ZIP Accrual workflow
   - Run Payroll Reconciliation
   - Test approval interface

3. **Customize for Your Needs**
   - Modify agents in `agents/` folder
   - Update UI in `streamlit-app/` folder
   - Add NetSuite tools in `mcp-server/` folder

### Deploy to Production

When ready for production:
1. Read `docs/DEPLOYMENT.md`
2. Set up AWS infrastructure
3. Deploy to EKS cluster

---

## 💡 Windows-Specific Tips

### Using Different Terminals

**PowerShell** (Recommended for Windows)
```powershell
cd C:\Projects\finclose-ai
docker-compose up -d
```

**Command Prompt**
```cmd
cd C:\Projects\finclose-ai
docker-compose up -d
```

**Git Bash** (Unix-like on Windows)
```bash
cd /c/Projects/finclose-ai
./setup.sh  # Can use Linux script
```

### Editing Configuration Files

- **Notepad**: `notepad .env`
- **VS Code**: `code .env`
- **Notepad++**: `notepad++ .env`

### File Paths

Windows uses backslashes, but in PowerShell you can use forward slashes:
- `C:\Projects\finclose-ai` ✅
- `C:/Projects/finclose-ai` ✅

---

## 🆘 Getting Help

### Check Logs First

```powershell
docker-compose logs -f
```

### Common Log Locations

- Docker logs: `docker-compose logs`
- Application logs: `logs/` folder (if configured)
- Windows Event Viewer: For Docker Desktop issues

### Support Resources

- 📧 Email: support@jadeglobal.com
- 📖 Documentation: See all .md files
- 🐛 GitHub Issues: (if repository available)

---

## ✅ Success Checklist

Before considering setup complete:

- [ ] Docker Desktop installed and running
- [ ] Python 3.11+ installed
- [ ] Project files extracted
- [ ] `.env` file configured with credentials
- [ ] Setup script completed successfully
- [ ] All 5 containers running (`docker-compose ps`)
- [ ] Can access http://localhost:8501
- [ ] Can login with demo credentials
- [ ] Successfully ran test workflow
- [ ] No errors in logs

---

## 🎉 You're Ready!

If you've completed all steps, your FinClose AI system is now running on Windows!

**Access your application**: http://localhost:8501

**Demo credentials**:
- `justine` / `demo`
- `selena` / `demo`
- `will` / `demo`

Happy automating! 🤖

---

**Last Updated**: November 22, 2025  
**Version**: 1.0  
**Platform**: Windows 10/11
