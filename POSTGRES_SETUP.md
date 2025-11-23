# FinClose AI - Native Windows Setup (No Docker)

Run FinClose AI directly on Windows using local PostgreSQL and Python.

---

## 📋 Prerequisites

### What You Need Installed

1. **Python 3.11 or higher** ✅
   - Download: https://www.python.org/downloads/
   - During install: Check "Add Python to PATH"
   - Verify: `python --version`

2. **PostgreSQL** ✅ (You already have this!)
   - Verify: `psql --version`
   - Should be accessible from command line

3. **Git for Windows** (Optional but helpful)
   - Download: https://git-scm.com/download/win
   - Gives you Git Bash terminal

---

## 🗄️ PostgreSQL Database Setup

### Step 1: Connect to PostgreSQL

Open **Command Prompt** or **PowerShell** as Administrator:

```powershell
# Connect to PostgreSQL as superuser (usually 'postgres')
psql -U postgres
```

Enter your PostgreSQL password when prompted.

### Step 2: Create Database and User

```sql
-- Create the database
CREATE DATABASE finclose_ai;

-- Create a dedicated user
CREATE USER finclose WITH PASSWORD 'your_secure_password_here';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE finclose_ai TO finclose;

-- Connect to the new database
\c finclose_ai

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO finclose;

-- Exit psql
\q
```

### Step 3: Verify Database Creation

```powershell
# Connect as the new user
psql -U finclose -d finclose_ai

# Should connect successfully
# Type \q to exit
```

### Step 4: Initialize Database Schema

Save this SQL script as `init_database.sql`:

```sql
-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS processing;
CREATE SCHEMA IF NOT EXISTS approval;
CREATE SCHEMA IF NOT EXISTS output;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS audit;

-- Grant permissions on all schemas
GRANT ALL ON SCHEMA staging TO finclose;
GRANT ALL ON SCHEMA processing TO finclose;
GRANT ALL ON SCHEMA approval TO finclose;
GRANT ALL ON SCHEMA output TO finclose;
GRANT ALL ON SCHEMA workflow TO finclose;
GRANT ALL ON SCHEMA audit TO finclose;

-- Create workflow executions table
CREATE TABLE IF NOT EXISTS workflow.executions (
    id SERIAL PRIMARY KEY,
    workflow_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create approval queue table
CREATE TABLE IF NOT EXISTS approval.queue (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(50) UNIQUE NOT NULL,
    workflow_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    data JSONB NOT NULL,
    variances JSONB,
    journal_entries JSONB,
    approver VARCHAR(100),
    approved_at TIMESTAMP,
    comments TEXT
);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit.log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_name VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address VARCHAR(45)
);

-- Create staging tables for ZIP accruals
CREATE TABLE IF NOT EXISTS staging.zip_invoices (
    id SERIAL PRIMARY KEY,
    invoice_id VARCHAR(50),
    vendor_id INTEGER,
    vendor_name VARCHAR(200),
    amount DECIMAL(15,2),
    invoice_date DATE,
    description TEXT,
    account INTEGER,
    department INTEGER,
    class INTEGER,
    location INTEGER,
    status VARCHAR(50),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create staging tables for payroll
CREATE TABLE IF NOT EXISTS staging.workday_payroll (
    id SERIAL PRIMARY KEY,
    account VARCHAR(50),
    account_name VARCHAR(200),
    amount DECIMAL(15,2),
    pay_period DATE,
    department VARCHAR(100),
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create processing tables
CREATE TABLE IF NOT EXISTS processing.accrual_calculations (
    id SERIAL PRIMARY KEY,
    invoice_id VARCHAR(50),
    vendor VARCHAR(200),
    total_amount DECIMAL(15,2),
    service_start DATE,
    service_end DATE,
    total_days INTEGER,
    accrual_days INTEGER,
    accrual_amount DECIMAL(15,2),
    account INTEGER,
    department INTEGER,
    class INTEGER,
    location INTEGER,
    confidence VARCHAR(20),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create output tables
CREATE TABLE IF NOT EXISTS output.journal_entries (
    id SERIAL PRIMARY KEY,
    je_id VARCHAR(50),
    subsidiary INTEGER,
    trandate DATE,
    memo TEXT,
    total_debit DECIMAL(15,2),
    total_credit DECIMAL(15,2),
    status VARCHAR(50) DEFAULT 'pending',
    netsuite_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS output.journal_entry_lines (
    id SERIAL PRIMARY KEY,
    je_id INTEGER REFERENCES output.journal_entries(id),
    line_number INTEGER,
    account INTEGER,
    account_name VARCHAR(200),
    debit DECIMAL(15,2),
    credit DECIMAL(15,2),
    department INTEGER,
    class INTEGER,
    location INTEGER,
    entity INTEGER,
    memo TEXT
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow.executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_type ON workflow.executions(workflow_type);
CREATE INDEX IF NOT EXISTS idx_executions_created ON workflow.executions(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_approval_status ON approval.queue(status);
CREATE INDEX IF NOT EXISTS idx_approval_created ON approval.queue(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_approval_request_id ON approval.queue(request_id);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit.log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit.log(user_name);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit.log(action);

CREATE INDEX IF NOT EXISTS idx_je_status ON output.journal_entries(status);
CREATE INDEX IF NOT EXISTS idx_je_date ON output.journal_entries(trandate DESC);

-- Create views for common queries
CREATE OR REPLACE VIEW workflow.execution_summary AS
SELECT 
    workflow_type,
    status,
    COUNT(*) as count,
    MAX(started_at) as last_run,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds
FROM workflow.executions
WHERE completed_at IS NOT NULL
GROUP BY workflow_type, status;

CREATE OR REPLACE VIEW approval.pending_approvals AS
SELECT 
    request_id,
    workflow_type,
    created_at,
    status,
    data->>'total_accrual' as total_amount,
    COALESCE(jsonb_array_length(variances), 0) as variance_count
FROM approval.queue
WHERE status = 'pending'
ORDER BY created_at DESC;

-- Insert sample data for testing (optional)
INSERT INTO workflow.executions (workflow_type, status, metadata)
VALUES 
    ('zip_accrual', 'completed', '{"test": true}'),
    ('payroll_recon', 'completed', '{"test": true}')
ON CONFLICT DO NOTHING;

-- Grant permissions on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA staging TO finclose;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA processing TO finclose;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA approval TO finclose;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA output TO finclose;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA workflow TO finclose;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO finclose;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA staging TO finclose;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA processing TO finclose;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA approval TO finclose;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA output TO finclose;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA workflow TO finclose;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA audit TO finclose;

-- Create a function for logging
CREATE OR REPLACE FUNCTION audit.log_action(
    p_user_name VARCHAR,
    p_action VARCHAR,
    p_resource_type VARCHAR,
    p_resource_id VARCHAR,
    p_details JSONB DEFAULT NULL
)
RETURNS void AS $$
BEGIN
    INSERT INTO audit.log (user_name, action, resource_type, resource_id, details)
    VALUES (p_user_name, p_action, p_resource_type, p_resource_id, p_details);
END;
$$ LANGUAGE plpgsql;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE 'Schemas created: staging, processing, approval, output, workflow, audit';
    RAISE NOTICE 'Tables created: 11 tables';
    RAISE NOTICE 'Indexes created: 11 indexes';
    RAISE NOTICE 'Views created: 2 views';
END $$;
```

### Step 5: Run the Initialization Script

```powershell
# Save the script above as init_database.sql in your project folder

# Run it
psql -U finclose -d finclose_ai -f init_database.sql

# You should see: "Database initialized successfully!"
```

### Step 6: Verify Database Setup

```powershell
# Connect to database
psql -U finclose -d finclose_ai

# List schemas
\dn

# Expected output:
#   Name       |  Owner   
# -------------+----------
#  approval    | postgres
#  audit       | postgres
#  output      | postgres
#  processing  | postgres
#  public      | postgres
#  staging     | postgres
#  workflow    | postgres

# List tables in workflow schema
\dt workflow.*

# Expected: workflow.executions table

# List all tables
\dt *.*

# Exit
\q
```

---

## 📝 Database Connection String

After setup, your connection details are:

```bash
# For .env file
DATABASE_URL=postgresql://finclose:your_secure_password_here@localhost:5432/finclose_ai

# Components:
# - User: finclose
# - Password: your_secure_password_here (change this!)
# - Host: localhost
# - Port: 5432 (default PostgreSQL port)
# - Database: finclose_ai
```

---

## 🔧 Common PostgreSQL Commands

### Useful Commands for Management

```sql
-- List all databases
\l

-- List all users
\du

-- Connect to a database
\c finclose_ai

-- List schemas
\dn

-- List tables in a schema
\dt workflow.*

-- Describe a table
\d workflow.executions

-- Show table with data
SELECT * FROM workflow.executions;

-- Count records
SELECT COUNT(*) FROM workflow.executions;

-- Delete all data from a table (careful!)
TRUNCATE TABLE workflow.executions CASCADE;

-- Drop a table (careful!)
DROP TABLE IF EXISTS workflow.executions;

-- Backup database
\! pg_dump -U finclose finclose_ai > backup.sql

-- Restore database
\! psql -U finclose finclose_ai < backup.sql
```

### Monitoring Queries

```sql
-- See all workflows
SELECT workflow_type, status, started_at, completed_at 
FROM workflow.executions 
ORDER BY started_at DESC 
LIMIT 10;

-- See pending approvals
SELECT * FROM approval.pending_approvals;

-- See recent audit logs
SELECT timestamp, user_name, action, resource_type 
FROM audit.log 
ORDER BY timestamp DESC 
LIMIT 20;

-- Check database size
SELECT pg_size_pretty(pg_database_size('finclose_ai'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname IN ('staging', 'processing', 'approval', 'output', 'workflow', 'audit')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🛠️ Troubleshooting PostgreSQL

### Issue: Cannot connect to PostgreSQL

**Check if PostgreSQL is running:**
```powershell
# Check service status
sc query postgresql-x64-15  # Adjust version number

# Start service if stopped
net start postgresql-x64-15
```

**Check connection:**
```powershell
psql -U postgres -c "SELECT version();"
```

### Issue: Password authentication failed

**Reset password:**
```sql
-- Connect as postgres superuser
psql -U postgres

-- Reset password
ALTER USER finclose WITH PASSWORD 'new_password_here';
```

### Issue: Permission denied

**Grant permissions:**
```sql
-- Connect as postgres
psql -U postgres -d finclose_ai

-- Grant all permissions
GRANT ALL PRIVILEGES ON DATABASE finclose_ai TO finclose;
GRANT ALL ON SCHEMA public TO finclose;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA workflow TO finclose;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA workflow TO finclose;
```

### Issue: Table already exists

**Drop and recreate:**
```sql
-- Connect to database
psql -U finclose -d finclose_ai

-- Drop specific table
DROP TABLE IF EXISTS workflow.executions CASCADE;

-- Or drop all tables in a schema
DROP SCHEMA IF EXISTS workflow CASCADE;

-- Then re-run init_database.sql
```

### Issue: Find PostgreSQL data directory

```powershell
psql -U postgres -c "SHOW data_directory;"
```

---

## 📊 Database Backup & Restore

### Backup Database

```powershell
# Full database backup
pg_dump -U finclose -d finclose_ai -F c -f finclose_ai_backup.dump

# SQL format backup
pg_dump -U finclose -d finclose_ai > finclose_ai_backup.sql

# Backup specific schema
pg_dump -U finclose -d finclose_ai -n workflow > workflow_backup.sql

# Backup with date
pg_dump -U finclose -d finclose_ai > finclose_ai_backup_$(Get-Date -Format "yyyyMMdd").sql
```

### Restore Database

```powershell
# Restore from custom format
pg_restore -U finclose -d finclose_ai finclose_ai_backup.dump

# Restore from SQL file
psql -U finclose -d finclose_ai < finclose_ai_backup.sql

# Restore specific schema
psql -U finclose -d finclose_ai < workflow_backup.sql
```

### Automated Backup Script (Optional)

Save as `backup_database.ps1`:

```powershell
# PostgreSQL Database Backup Script
$backupDir = "C:\PostgreSQL\Backups"
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$backupDir\finclose_ai_$date.sql"

# Create backup directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Backup database
Write-Host "Backing up database to: $backupFile"
pg_dump -U finclose -d finclose_ai > $backupFile

# Keep only last 7 backups
Get-ChildItem $backupDir -Filter "finclose_ai_*.sql" | 
    Sort-Object CreationTime -Descending | 
    Select-Object -Skip 7 | 
    Remove-Item

Write-Host "Backup completed successfully!"
```

Run weekly: `.\backup_database.ps1`

---

## ✅ Verification Checklist

After completing setup:

- [ ] PostgreSQL service is running
- [ ] Can connect with: `psql -U finclose -d finclose_ai`
- [ ] Database `finclose_ai` exists
- [ ] User `finclose` exists with correct password
- [ ] 7 schemas created (staging, processing, approval, output, workflow, audit, public)
- [ ] 11+ tables created across schemas
- [ ] Can query: `SELECT * FROM workflow.executions;`
- [ ] Can insert test data without errors
- [ ] Indexes created successfully
- [ ] Views created successfully
- [ ] All permissions granted to `finclose` user

---

## 🔐 Security Best Practices

### 1. Change Default Password

```sql
-- Use a strong password
ALTER USER finclose WITH PASSWORD 'Strong!Pass123$';
```

### 2. Restrict Access (Optional)

Edit `pg_hba.conf` to restrict connections:
```
# Allow finclose user only from localhost
host    finclose_ai     finclose        127.0.0.1/32           md5
```

### 3. Regular Backups

Set up automated backups (see script above).

### 4. Monitor Connections

```sql
-- See active connections
SELECT * FROM pg_stat_activity WHERE datname = 'finclose_ai';
```

---

## 📖 Next Steps

Now that your PostgreSQL database is set up, proceed to:

1. **[NATIVE_WINDOWS_SETUP.md](NATIVE_WINDOWS_SETUP.md)** - Complete application setup without Docker
2. Configure your `.env` file with the database connection
3. Install Python dependencies
4. Run the application

---

## 🆘 Need Help?

### PostgreSQL Documentation
- Official Docs: https://www.postgresql.org/docs/
- Windows Install: https://www.postgresql.org/download/windows/

### Common Issues
- Port 5432 in use: Check for other PostgreSQL instances
- Permission errors: Re-run GRANT commands
- Connection refused: Check PostgreSQL service is running

---

**Your database is now ready for FinClose AI!** ✅

Next: Set up the application to connect to this database.
