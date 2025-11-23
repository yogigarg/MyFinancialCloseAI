# FinClose AI - Native Windows Setup (No Docker Required)

Complete guide to run FinClose AI on Windows using only Python and PostgreSQL.

---

## 📋 What You'll Need

### Already Installed
- ✅ **Python 3.11+** (you have this)
- ✅ **PostgreSQL** (you have this)

### Need to Install
- Nothing else! Everything runs natively on Windows.

---

## 🚀 Complete Setup Process

### Part 1: Database Setup (15 minutes)

**Follow the complete guide**: [POSTGRES_SETUP.md](POSTGRES_SETUP.md)

Quick summary:
1. Connect to PostgreSQL: `psql -U postgres`
2. Run database creation commands
3. Initialize schema with `init_database.sql`
4. Verify with test queries

**Result**: Database `finclose_ai` ready with all tables and schemas.

---

### Part 2: Application Setup (20 minutes)

## Step 1: Extract Project Files

Extract `finclose-ai.zip` to a folder, for example:
```
C:\Projects\finclose-ai\
```

## Step 2: Create Virtual Environment (Recommended)

```powershell
# Navigate to project folder
cd C:\Projects\finclose-ai

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activate again
.\venv\Scripts\Activate.ps1

# You should see (venv) in your prompt
```

## Step 3: Install Python Dependencies

### Install MCP Server Dependencies

```powershell
cd mcp-server
pip install -r requirements.txt
cd ..
```

### Install Agent Dependencies

```powershell
cd agents
pip install -r requirements.txt
cd ..
```

### Install Streamlit Dependencies

```powershell
cd streamlit-app
pip install -r requirements.txt
cd ..
```

### Install Shared Dependencies

```powershell
pip install psycopg2-binary python-dotenv
```

## Step 4: Configure Environment Variables

```powershell
# Copy the example file
copy .env.example .env

# Edit with Notepad
notepad .env
```

**Edit these values in .env:**

```bash
# ============================================================================
# PostgreSQL Configuration (IMPORTANT!)
# ============================================================================
DATABASE_URL=postgresql://finclose:your_password@localhost:5432/finclose_ai
# Replace 'your_password' with the password you set for finclose user

# ============================================================================
# NetSuite Configuration (REQUIRED)
# ============================================================================
NETSUITE_ACCOUNT_ID=your_account_id
NETSUITE_CONSUMER_KEY=your_consumer_key
NETSUITE_CONSUMER_SECRET=your_consumer_secret
NETSUITE_TOKEN_ID=your_token_id
NETSUITE_TOKEN_SECRET=your_token_secret
NETSUITE_REST_URL=https://your-account.suitetalk.api.netsuite.com

# ============================================================================
# Anthropic API (REQUIRED)
# ============================================================================
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# ============================================================================
# LangSmith (Optional - for monitoring)
# ============================================================================
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT=finclose-ai
LANGSMITH_TRACING=true

# ============================================================================
# Application Configuration
# ============================================================================
ENVIRONMENT=development
LOG_LEVEL=INFO
MATERIALITY_THRESHOLD=1000
DEFAULT_SUBSIDIARY=1

# No Redis needed for native setup - agents will run synchronously
# No Docker-specific settings needed
```

Save and close the file.

## Step 5: Create Required Directories

```powershell
# Create log and data directories
mkdir logs
mkdir data
mkdir data\uploads
mkdir data\exports
```

---

## 🎯 Running the Application

You'll need to run **3 separate processes** in different terminals.

### Terminal 1: MCP Server

```powershell
# Open PowerShell in project folder
cd C:\Projects\finclose-ai

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to MCP server
cd mcp-server

# Run the server
python netsuite_server.py

# Should see: "MCP Server running..."
# Keep this terminal open
```

### Terminal 2: Streamlit Web App

```powershell
# Open NEW PowerShell in project folder
cd C:\Projects\finclose-ai

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to streamlit app
cd streamlit-app

# Run Streamlit
streamlit run app.py

# Should see: "You can now view your Streamlit app in your browser."
# Should auto-open: http://localhost:8501
# Keep this terminal open
```

### Terminal 3: Test Agents (Optional)

```powershell
# Open NEW PowerShell in project folder
cd C:\Projects\finclose-ai

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Navigate to agents
cd agents

# Test ZIP Accrual Agent
python zip_accrual_agent.py

# Or test Payroll Recon Agent
python payroll_recon_agent.py

# You can close this after testing
```

---

## 🌐 Access the Application

1. **Open browser**: http://localhost:8501
2. **Login** with demo credentials:
   - Username: `justine` Password: `demo`
   - Username: `selena` Password: `demo`
   - Username: `will` Password: `demo`

3. **Try a workflow**:
   - Click "Workflows"
   - Select "ZIP Accrual"
   - Click "Start Workflow"
   - Watch it run!

---

## 📝 Quick Start Script (All-in-One)

Save this as `start-all.ps1` in your project root:

```powershell
# Start All Services Script
Write-Host "Starting FinClose AI Services..." -ForegroundColor Green

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start MCP Server in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd mcp-server; python netsuite_server.py"

# Wait 5 seconds
Start-Sleep -Seconds 5

# Start Streamlit
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd streamlit-app; streamlit run app.py"

Write-Host ""
Write-Host "Services started!" -ForegroundColor Green
Write-Host "- MCP Server running in separate window" -ForegroundColor Yellow
Write-Host "- Streamlit will open in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Access: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop: Close all PowerShell windows" -ForegroundColor Yellow
```

**Usage:**
```powershell
# From project root
.\start-all.ps1
```

---

## 🔧 Development Workflow

### Daily Usage

```powershell
# 1. Open project folder
cd C:\Projects\finclose-ai

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Start services (choose one method):

# Method A: Use start script
.\start-all.ps1

# Method B: Manual (in separate terminals)
# Terminal 1: cd mcp-server && python netsuite_server.py
# Terminal 2: cd streamlit-app && streamlit run app.py
```

### Testing Individual Components

```powershell
# Test database connection
python -c "import psycopg2; conn = psycopg2.connect('postgresql://finclose:password@localhost:5432/finclose_ai'); print('Connected!'); conn.close()"

# Test MCP Server
cd mcp-server
python netsuite_server.py
# Ctrl+C to stop

# Test agents
cd agents
python zip_accrual_agent.py
# Should run test workflow

# Test Streamlit
cd streamlit-app
streamlit run app.py
# Opens browser
```

### Making Code Changes

1. Edit files in VS Code, Notepad++, or any editor
2. Save changes
3. Restart the affected service:
   - For MCP changes: Restart Terminal 1 (Ctrl+C, then run again)
   - For agent changes: No restart needed (reloaded on each run)
   - For Streamlit changes: Usually auto-reloads, or restart Terminal 2

---

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
cd mcp-server
pip install -r requirements.txt

cd ..\agents
pip install -r requirements.txt

cd ..\streamlit-app
pip install -r requirements.txt
```

### Issue: Database connection failed

```powershell
# Test PostgreSQL connection
psql -U finclose -d finclose_ai

# If fails, check:
# 1. PostgreSQL service is running
sc query postgresql-x64-15

# 2. Password is correct in .env file
notepad .env

# 3. Database exists
psql -U postgres -c "\l" | findstr finclose_ai
```

### Issue: Port 8501 already in use

```powershell
# Find what's using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or run Streamlit on different port
streamlit run app.py --server.port 8502
```

### Issue: MCP Server won't start

```powershell
# Check if netsuite_server.py exists
dir mcp-server\netsuite_server.py

# Check Python path
where python

# Try running with full path
python C:\Projects\finclose-ai\mcp-server\netsuite_server.py

# Check for errors in code
python -m py_compile mcp-server\netsuite_server.py
```

### Issue: Virtual environment not activating

```powershell
# Allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activate again
.\venv\Scripts\Activate.ps1

# Alternative: Use full path
C:\Projects\finclose-ai\venv\Scripts\Activate.ps1

# Or run without virtual environment (not recommended)
python -m pip install -r mcp-server\requirements.txt
```

---

## 📊 Verifying Everything Works

### Checklist

```powershell
# 1. Database connection
psql -U finclose -d finclose_ai -c "SELECT COUNT(*) FROM workflow.executions;"
# Should return count (even if 0)

# 2. Python environment
python --version
# Should show 3.11 or higher

# 3. Dependencies installed
pip list | findstr langgraph
pip list | findstr streamlit
pip list | findstr anthropic
# Should see packages

# 4. MCP Server
# Terminal 1 should show "MCP Server running"

# 5. Streamlit
# Browser should open to http://localhost:8501

# 6. Login works
# Can login with justine/demo

# 7. Run workflow
# ZIP Accrual workflow completes without errors

# 8. Database updated
psql -U finclose -d finclose_ai -c "SELECT * FROM workflow.executions ORDER BY id DESC LIMIT 1;"
# Should show recent execution
```

---

## 🎓 Understanding the Setup

### What Runs Where

```
┌─────────────────────────────────────┐
│  Streamlit (Terminal 2)             │  → http://localhost:8501
│  - Web UI                           │  → User interface
│  - Calls agents directly            │  → No API server needed
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│  Agents (In-process)                │  → Runs in Streamlit
│  - ZIP Accrual Agent                │  → LangGraph workflows
│  - Payroll Reconciliation Agent     │  → Claude AI calls
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│  MCP Server (Terminal 1)            │  → Background process
│  - NetSuite integration             │  → Port 8000 (internal)
└─────────────────┬───────────────────┘
                  │
┌─────────────────┴───────────────────┐
│  PostgreSQL (Service)               │  → Port 5432
│  - Database: finclose_ai            │  → Always running
│  - User: finclose                   │  → Data storage
└─────────────────────────────────────┘
```

### File Structure

```
C:\Projects\finclose-ai\
│
├── venv\                    ← Virtual environment (created by you)
│   └── Scripts\
│       └── Activate.ps1
│
├── .env                     ← Your credentials (created by you)
│
├── logs\                    ← Log files (created by you)
│
├── data\                    ← Data files (created by you)
│   ├── uploads\
│   └── exports\
│
├── mcp-server\              ← NetSuite MCP Server
│   ├── netsuite_server.py   ← Run this in Terminal 1
│   └── requirements.txt
│
├── agents\                  ← AI Agents (called by Streamlit)
│   ├── zip_accrual_agent.py
│   ├── payroll_recon_agent.py
│   └── requirements.txt
│
├── streamlit-app\           ← Web UI
│   ├── app.py               ← Run this in Terminal 2
│   └── requirements.txt
│
└── shared\                  ← Shared utilities
    └── models.py
```

---

## 🔄 Start/Stop Services

### Start Services

```powershell
# Quick start (recommended)
.\start-all.ps1

# Or manual:
# Terminal 1: cd mcp-server && python netsuite_server.py
# Terminal 2: cd streamlit-app && streamlit run app.py
```

### Stop Services

```powershell
# Press Ctrl+C in each terminal

# Or close the PowerShell windows

# Or use Task Manager to end Python processes
```

### Restart Service

```powershell
# In the terminal running the service:
# 1. Press Ctrl+C
# 2. Press Up Arrow to recall last command
# 3. Press Enter to run again
```

---

## 📖 Next Steps After Setup

### 1. Configure Real Credentials

Edit `.env` file with your actual:
- NetSuite OAuth credentials
- Anthropic API key
- Database password

### 2. Test with Real Data

- Upload actual ZIP invoice files
- Import Workday payroll data
- Run production workflows

### 3. Customize for Your Needs

- Modify agents in `agents/` folder
- Customize UI in `streamlit-app/app.py`
- Add NetSuite tools in `mcp-server/netsuite_server.py`

### 4. Set Up Monitoring

- Configure LangSmith for agent tracing
- Set up database backups
- Create log rotation

---

## ✅ Success Checklist

- [ ] PostgreSQL database created and initialized
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (3 requirements.txt)
- [ ] .env file configured with credentials
- [ ] MCP Server starts without errors
- [ ] Streamlit opens in browser
- [ ] Can login with demo credentials
- [ ] ZIP Accrual workflow runs successfully
- [ ] Data appears in PostgreSQL database
- [ ] No errors in any terminal

**If all checked: You're ready to use FinClose AI!** 🎉

---

## 🆘 Getting Help

### Check Logs

```powershell
# Check terminal output for errors

# Check Streamlit logs
dir streamlit-app\.streamlit\

# Check Python error messages carefully
```

### Common Commands

```powershell
# Verify Python
python --version

# Verify PostgreSQL
psql -U finclose -d finclose_ai -c "SELECT version();"

# List installed packages
pip list

# Test imports
python -c "import langgraph, streamlit, anthropic; print('All imports OK')"
```

### Still Stuck?

1. Read error messages carefully
2. Check POSTGRES_SETUP.md for database issues
3. Verify .env file configuration
4. Make sure virtual environment is activated
5. Try reinstalling dependencies

---

**You're now running FinClose AI natively on Windows without Docker!** 🚀

**Access**: http://localhost:8501
**Login**: justine / demo

Happy automating! 🤖
