# 🎯 FinClose AI - Native Windows Setup (No Docker!)

## ✨ Perfect for You!

Since you **don't have Docker** installed, this guide shows you how to run FinClose AI directly on Windows using just:
- ✅ Python 3.11+ 
- ✅ PostgreSQL (which you already have!)

**No Docker, No Containers, No Complexity!** Just native Windows applications.

---

## 📦 What You Downloaded

This ZIP contains everything to run FinClose AI on Windows without Docker:

### 🪟 Native Windows Files (START HERE!)
1. **NATIVE_QUICK_START.txt** ← Quick reference (read this first!)
2. **NATIVE_WINDOWS_SETUP.md** ← Complete setup guide
3. **POSTGRES_SETUP.md** ← Database setup instructions
4. **start-all.ps1** ← One-click startup script
5. **stop-all.ps1** ← One-click stop script

### 💻 Source Code (2,687 lines)
- **mcp-server/** - NetSuite integration (721 lines)
- **agents/** - AI workflow agents (830 lines)  
- **streamlit-app/** - Web UI (420 lines)
- **shared/** - Common utilities (200 lines)

### 📚 Documentation (1,500+ lines)
- General: README.md, PROJECT_OVERVIEW.md, START_HERE.md
- Docker users: WINDOWS_SETUP.md, docker-compose.yml
- Production: docs/DEPLOYMENT.md

---

## 🚀 Quick Start (3 Steps - 30 Minutes)

### Step 1: Setup PostgreSQL Database (15 min)

**Follow**: [POSTGRES_SETUP.md](POSTGRES_SETUP.md)

Quick version:
```powershell
# 1. Connect to PostgreSQL
psql -U postgres

# 2. Create database and user
CREATE DATABASE finclose_ai;
CREATE USER finclose WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finclose_ai TO finclose;
\q

# 3. Initialize schema
# Download init_database.sql from POSTGRES_SETUP.md
psql -U finclose -d finclose_ai -f init_database.sql
```

✅ **Result**: Database ready with all tables and schemas

---

### Step 2: Configure Application (5 min)

```powershell
# Navigate to extracted folder
cd C:\Projects\finclose-ai

# Copy configuration template
copy .env.example .env

# Edit with your credentials
notepad .env
```

**Edit these in .env:**
```bash
# Database (REQUIRED)
DATABASE_URL=postgresql://finclose:your_password@localhost:5432/finclose_ai

# NetSuite (REQUIRED)
NETSUITE_ACCOUNT_ID=your_account_id
NETSUITE_CONSUMER_KEY=your_consumer_key
NETSUITE_CONSUMER_SECRET=your_consumer_secret
NETSUITE_TOKEN_ID=your_token_id
NETSUITE_TOKEN_SECRET=your_token_secret
NETSUITE_REST_URL=https://your-account.suitetalk.api.netsuite.com

# Anthropic API (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Save and close.

✅ **Result**: Application configured

---

### Step 3: Start Application (10 min)

```powershell
# Create virtual environment (first time only)
python -m venv venv

# Allow scripts (first time only)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Start everything!
.\start-all.ps1
```

**What happens:**
1. Virtual environment activates
2. Dependencies install (if needed)
3. MCP Server starts in new window
4. Streamlit starts in new window
5. Browser opens to http://localhost:8501

✅ **Result**: FinClose AI running!

**Login**: justine / demo

---

## 🎯 Daily Usage (After Setup)

```powershell
# Every time you want to use FinClose AI:

cd C:\Projects\finclose-ai
.\start-all.ps1

# Opens browser automatically to http://localhost:8501
# Login: justine / demo
```

**To stop:**
```powershell
.\stop-all.ps1
# Or close the PowerShell windows
```

---

## 📖 Complete Setup Guide

For detailed step-by-step instructions with troubleshooting:

👉 **[NATIVE_WINDOWS_SETUP.md](NATIVE_WINDOWS_SETUP.md)**

Covers:
- Virtual environment setup
- Dependency installation
- Manual service startup
- Testing components
- Common issues and fixes

---

## 🗄️ PostgreSQL Database Setup

For complete database setup instructions:

👉 **[POSTGRES_SETUP.md](POSTGRES_SETUP.md)**

Covers:
- Creating database and user
- Initializing schema (11 tables, 6 schemas)
- Granting permissions
- Verification queries
- Backup and restore
- Troubleshooting

**Database Schema Includes:**
- ✅ `workflow.executions` - Workflow tracking
- ✅ `approval.queue` - Approval requests
- ✅ `audit.log` - Audit trail
- ✅ `staging.*` - Input data tables
- ✅ `processing.*` - Calculated data
- ✅ `output.*` - Journal entries
- And 5 more tables!

---

## 🔧 What Runs Where

### Terminal 1: MCP Server
```
NetSuite MCP Server → Port 8000
- Handles NetSuite API calls
- Provides tools for agents
- OAuth authentication
```

### Terminal 2: Streamlit Web UI
```
Streamlit Application → http://localhost:8501
- Web interface
- Runs agents in-process
- No separate API server needed
```

### Background: PostgreSQL
```
PostgreSQL Database → Port 5432
- Always running as Windows service
- Stores all data
- No need to start/stop
```

---

## 📁 File Structure

```
C:\Projects\finclose-ai\
│
├── 🚀 START HERE (Native Windows)
│   ├── NATIVE_QUICK_START.txt    ← Quick reference
│   ├── NATIVE_WINDOWS_SETUP.md   ← Full guide
│   ├── POSTGRES_SETUP.md         ← Database setup
│   ├── start-all.ps1             ← Start script
│   └── stop-all.ps1              ← Stop script
│
├── ⚙️ Configuration
│   ├── .env.example              ← Template (copy to .env)
│   └── .env                      ← Your credentials (create this)
│
├── 🐍 Virtual Environment
│   └── venv/                     ← Created by you
│       └── Scripts/
│           └── Activate.ps1
│
├── 💻 Application Code
│   ├── mcp-server/               ← NetSuite integration
│   │   ├── netsuite_server.py
│   │   └── requirements.txt
│   │
│   ├── agents/                   ← AI agents
│   │   ├── zip_accrual_agent.py
│   │   ├── payroll_recon_agent.py
│   │   └── requirements.txt
│   │
│   ├── streamlit-app/            ← Web UI
│   │   ├── app.py
│   │   └── requirements.txt
│   │
│   └── shared/                   ← Utilities
│       └── models.py
│
├── 📁 Data Directories (create these)
│   ├── logs/                     ← Log files
│   └── data/                     ← Upload/export data
│       ├── uploads/
│       └── exports/
│
└── 📚 Documentation
    ├── README.md                 ← Project docs
    ├── PROJECT_OVERVIEW.md       ← What's included
    └── docs/DEPLOYMENT.md        ← Production guide
```

---

## ✅ Verification Checklist

After setup, verify everything works:

```powershell
# 1. Database connection
psql -U finclose -d finclose_ai -c "SELECT COUNT(*) FROM workflow.executions;"
# ✅ Should return a number

# 2. Virtual environment
.\venv\Scripts\Activate.ps1
python --version
# ✅ Should show Python 3.11+

# 3. Dependencies
pip list | findstr langgraph
pip list | findstr streamlit
# ✅ Should show packages

# 4. Start services
.\start-all.ps1
# ✅ Two windows open (MCP + Streamlit)

# 5. Access UI
# ✅ Browser opens to http://localhost:8501

# 6. Login
# ✅ Can login with justine/demo

# 7. Run workflow
# ✅ ZIP Accrual workflow completes

# 8. Check database
psql -U finclose -d finclose_ai -c "SELECT * FROM workflow.executions ORDER BY id DESC LIMIT 1;"
# ✅ Shows recent execution
```

---

## 🎓 How It Works

### Architecture (Native Windows)

```
┌─────────────────────────────────┐
│  Browser → http://localhost:8501│
└────────────┬────────────────────┘
             │
┌────────────┴────────────────────┐
│  Streamlit App (Terminal 2)     │
│  - Web UI                       │
│  - Calls agents directly        │
│  - No Docker, pure Python       │
└────────────┬────────────────────┘
             │
┌────────────┴────────────────────┐
│  AI Agents (In-Process)         │
│  - ZIP Accrual Agent            │
│  - Payroll Recon Agent          │
│  - Uses Claude 3.5 Sonnet       │
└────────────┬────────────────────┘
             │
┌────────────┴────────────────────┐
│  MCP Server (Terminal 1)        │
│  - NetSuite integration         │
│  - Provides tools to agents     │
└────────────┬────────────────────┘
             │
┌────────────┴────────────────────┐
│  PostgreSQL (Windows Service)   │
│  - Database: finclose_ai        │
│  - Always running               │
└─────────────────────────────────┘
```

**Key Points:**
- ✅ No containers, everything runs natively
- ✅ Two Python processes: MCP Server + Streamlit
- ✅ PostgreSQL runs as Windows service
- ✅ Agents run inside Streamlit (no separate process)
- ✅ MCP Server provides NetSuite tools
- ✅ All communication via Python imports (no HTTP for agents)

---

## 🐛 Common Issues & Fixes

### Can't activate virtual environment

```powershell
# Fix: Allow scripts
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
.\venv\Scripts\Activate.ps1
```

### Database connection failed

```powershell
# Check PostgreSQL is running
sc query postgresql-x64-15

# If not running, start it
net start postgresql-x64-15

# Test connection
psql -U finclose -d finclose_ai

# If password wrong, edit .env
notepad .env
```

### Port 8501 already in use

```powershell
# Find what's using it
netstat -ano | findstr :8501

# Kill the process
taskkill /PID <PID> /F
```

### Dependencies not installing

```powershell
# Make sure venv is activated (see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Try installing again
pip install -r mcp-server\requirements.txt
```

### ModuleNotFoundError

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Reinstall all dependencies
pip install -r mcp-server\requirements.txt
pip install -r agents\requirements.txt
pip install -r streamlit-app\requirements.txt
pip install psycopg2-binary python-dotenv
```

**Full troubleshooting**: See [NATIVE_WINDOWS_SETUP.md](NATIVE_WINDOWS_SETUP.md)

---

## 💡 Tips & Tricks

### Quick Commands

```powershell
# Start everything
.\start-all.ps1

# Stop everything
.\stop-all.ps1

# Connect to database
psql -U finclose -d finclose_ai

# View workflow executions
psql -U finclose -d finclose_ai -c "SELECT * FROM workflow.executions;"

# Check virtual environment packages
.\venv\Scripts\Activate.ps1
pip list
```

### Startup Script

Save this as `quick-start.bat` for double-click startup:

```batch
@echo off
cd C:\Projects\finclose-ai
powershell -ExecutionPolicy Bypass -File start-all.ps1
```

### Database Backup

```powershell
# Backup database
pg_dump -U finclose finclose_ai > backup_$(Get-Date -Format "yyyyMMdd").sql

# Restore if needed
psql -U finclose finclose_ai < backup_20251123.sql
```

---

## 📊 What You Can Do

Once running, you can:

1. **Run ZIP Accrual Workflow**
   - Automates 2-3 hours → 15 minutes
   - AI identifies service periods
   - Generates journal entries

2. **Run Payroll Reconciliation**
   - Automates 1-2 hours → 20 minutes
   - AI classifies variances
   - Routes to approval

3. **Review Approvals**
   - HITL interface
   - Approve/reject workflows
   - Full audit trail

4. **View Reports**
   - Workflow performance
   - Time savings analytics
   - Audit logs

---

## 🎉 You're Ready!

Everything is set up to run FinClose AI natively on Windows!

**Quick Start:**
```powershell
cd C:\Projects\finclose-ai
.\start-all.ps1
```

**Access**: http://localhost:8501  
**Login**: justine / demo

**Happy Automating!** 🤖

---

## 📞 Need Help?

1. **Read**: [NATIVE_WINDOWS_SETUP.md](NATIVE_WINDOWS_SETUP.md) - Full guide
2. **Database**: [POSTGRES_SETUP.md](POSTGRES_SETUP.md) - DB setup
3. **Quick Ref**: [NATIVE_QUICK_START.txt](NATIVE_QUICK_START.txt) - Commands
4. **Email**: support@jadeglobal.com

---

**Created**: November 22, 2025  
**Version**: 1.0  
**Platform**: Windows 10/11 (No Docker)  
**Team**: Jade Global AI & Automation
