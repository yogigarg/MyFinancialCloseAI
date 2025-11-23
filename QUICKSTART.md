# FinClose AI - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Prerequisites Check

Make sure you have:
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] Git installed (`git --version`)

### Step 2: Get the Code

```bash
# If you haven't already, clone or extract the project
cd finclose-ai
```

### Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
# REQUIRED:
#   - NETSUITE_* credentials
#   - ANTHROPIC_API_KEY
#   - POSTGRES_PASSWORD (change from default)
nano .env  # or use your favorite editor
```

### Step 4: Run Setup

```bash
# Make setup script executable
chmod +x setup.sh

# Run the automated setup
./setup.sh
```

This will:
- ✅ Check prerequisites
- ✅ Create necessary directories
- ✅ Build Docker images
- ✅ Initialize database
- ✅ Set up schema and tables

### Step 5: Start Services

```bash
# Start all services in background
docker-compose up -d

# Check that all services are running
docker-compose ps

# You should see:
# - finclose-postgres (PostgreSQL)
# - finclose-redis (Redis)
# - finclose-mcp-server (NetSuite MCP)
# - finclose-streamlit (UI)
# - finclose-agents (Agent Workers)
```

### Step 6: Access the Application

Open your browser and go to:

**Streamlit UI**: http://localhost:8501

**Demo Login Credentials:**
- Username: `justine` Password: `demo`
- Username: `selena` Password: `demo`
- Username: `will` Password: `demo`

### Step 7: Test a Workflow

1. Login to Streamlit (http://localhost:8501)
2. Go to **Workflows** page
3. Select **ZIP Accrual** tab
4. Click "Start Workflow"
5. Watch the progress in real-time!

---

## 🔍 Verify Everything Works

### Check Service Health

```bash
# Check Streamlit
curl http://localhost:8501/_stcore/health

# Check MCP Server
curl http://localhost:8000/health

# Check database
docker-compose exec postgres psql -U finclose -d finclose_ai -c "SELECT 1"

# Check Redis
docker-compose exec redis redis-cli ping
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f streamlit-app
docker-compose logs -f mcp-server
docker-compose logs -f agent-workers
```

### Test NetSuite Connection

```bash
# From Python
docker-compose exec mcp-server python -c "
from netsuite_server import get_client
client = get_client()
print('NetSuite connection successful!')
"
```

---

## 🎮 Try the Demo Workflows

### 1. ZIP Accrual Workflow

**Purpose**: Automate invoice accrual processing

**Steps**:
1. Go to Workflows → ZIP Accrual
2. Select close date: November 30, 2025
3. Select subsidiary: Gusto US
4. Upload ZIP export CSV (or use demo data)
5. Click "Start Workflow"

**Expected Result**: 
- Invoices extracted
- Service periods identified by AI
- Accruals calculated
- Journal entries generated
- Approval request created

**Time**: ~30 seconds

### 2. Payroll Reconciliation

**Purpose**: Reconcile Workday payroll with NetSuite

**Steps**:
1. Go to Workflows → Payroll Reconciliation
2. Select pay period: November 15, 2025
3. Upload Workday export CSV
4. Click "Start Workflow"

**Expected Result**:
- Workday data extracted
- NetSuite JEs fetched
- Reconciliation performed
- Variances classified by AI
- Approval request if needed

**Time**: ~45 seconds

### 3. Review Approvals

**Purpose**: Approve or reject workflow results

**Steps**:
1. Go to Approvals page
2. See pending approval requests
3. Expand each request to see details
4. Click "Approve" or "Reject"

---

## 🛠️ Common Commands

### Start/Stop Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart streamlit-app

# Stop and remove all data
docker-compose down -v
```

### Database Operations

```bash
# Connect to database
docker-compose exec postgres psql -U finclose -d finclose_ai

# Backup database
docker-compose exec postgres pg_dump -U finclose finclose_ai > backup.sql

# Restore database
docker-compose exec -T postgres psql -U finclose -d finclose_ai < backup.sql
```

### Development Mode

```bash
# Run Streamlit in dev mode (auto-reload)
cd streamlit-app
streamlit run app.py --server.runOnSave true

# Run agent directly
cd agents
python zip_accrual_agent.py
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8501
lsof -i :8501

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Error

```bash
# Reset database
docker-compose down postgres
docker volume rm finclose-ai_postgres_data
docker-compose up -d postgres

# Wait 10 seconds, then run setup again
./setup.sh
```

### Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Rebuild image
docker-compose build --no-cache <service-name>

# Remove and recreate
docker-compose down
docker-compose up -d
```

### NetSuite Connection Failed

1. Verify credentials in `.env` file
2. Check NetSuite OAuth token is active
3. Verify account ID format (no hyphens)
4. Check REST API URL is correct

---

## 📚 Next Steps

### Customize for Your Needs

1. **Modify Agents**: Edit `agents/*.py` to match your workflows
2. **Update UI**: Customize `streamlit-app/app.py`
3. **Add NetSuite Tools**: Extend `mcp-server/netsuite_server.py`
4. **Configure Accounts**: Update account mappings

### Deploy to Production

See `docs/DEPLOYMENT.md` for complete production deployment guide:
- AWS infrastructure setup
- Kubernetes deployment
- Security configuration
- Monitoring setup

### Learn More

- **README.md**: Complete project documentation
- **IMPLEMENTATION_SUMMARY.md**: Technical overview
- **docs/DEPLOYMENT.md**: Production deployment
- **Code Comments**: Inline documentation

---

## 🆘 Getting Help

### Check Documentation

1. Read error messages carefully
2. Check logs: `docker-compose logs -f`
3. Review README.md
4. See DEPLOYMENT.md for infrastructure issues

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflict | Change ports in docker-compose.yml |
| Database error | Reset database (see Troubleshooting) |
| API key invalid | Check .env file |
| Import error | Rebuild containers |
| Permission denied | Run with sudo or fix permissions |

### Contact Support

- **Email**: support@jadeglobal.com
- **Documentation**: See README.md
- **Issues**: Create GitHub issue (if applicable)

---

## ✅ Success Checklist

Before considering setup complete:

- [ ] All Docker containers running (`docker-compose ps`)
- [ ] Streamlit accessible at http://localhost:8501
- [ ] Can login with demo credentials
- [ ] Database connection works
- [ ] MCP server health check passes
- [ ] Successfully ran test workflow
- [ ] Can view logs without errors
- [ ] NetSuite credentials validated

---

## 🎉 You're All Set!

Your FinClose AI system is now running. Start automating your month-end close!

**Remember**:
- 📝 Configure real credentials before production use
- 🔒 Never commit .env file to git
- 📊 Monitor LangSmith for agent performance
- 🚀 Follow DEPLOYMENT.md for production

**Happy Automating!** 🤖
