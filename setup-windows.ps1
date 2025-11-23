# FinClose AI Setup Script for Windows
# Run this in PowerShell as Administrator

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  FinClose AI - Windows Setup Script" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "WARNING: Not running as Administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Green

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop for Windows." -ForegroundColor Red
    Write-Host "  Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "✓ Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Compose not found. Please install Docker Desktop (includes Compose)." -ForegroundColor Red
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11 or higher." -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker is running
Write-Host ""
Write-Host "Checking if Docker Desktop is running..." -ForegroundColor Green
try {
    docker ps | Out-Null
    Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not running. Please start Docker Desktop." -ForegroundColor Red
    Write-Host "  Look for Docker Desktop in your Start menu and run it." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Setting up environment" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Green
    Copy-Item .env.example .env
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠  IMPORTANT: Edit .env file with your actual credentials!" -ForegroundColor Yellow
    Write-Host "   Open .env in Notepad and add your API keys." -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Green
$directories = @("logs", "data\postgres", "data\redis", "data\uploads")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Build Docker images
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Building Docker images" -ForegroundColor Cyan
Write-Host "  (This may take 5-10 minutes on first run)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Docker images built successfully" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Failed to build Docker images" -ForegroundColor Red
    exit 1
}

# Start PostgreSQL and Redis first
Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Starting database services" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

docker-compose up -d postgres redis

Write-Host "Waiting for PostgreSQL to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Green

$sqlScript = @"
-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS processing;
CREATE SCHEMA IF NOT EXISTS approval;
CREATE SCHEMA IF NOT EXISTS output;
CREATE SCHEMA IF NOT EXISTS workflow;
CREATE SCHEMA IF NOT EXISTS audit;

-- Create core tables
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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_executions_status ON workflow.executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_type ON workflow.executions(workflow_type);
CREATE INDEX IF NOT EXISTS idx_approval_status ON approval.queue(status);
CREATE INDEX IF NOT EXISTS idx_approval_created ON approval.queue(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit.log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit.log(user_name);
"@

# Save SQL to temp file and execute
$sqlScript | Out-File -FilePath "temp_init.sql" -Encoding UTF8
docker-compose exec -T postgres psql -U finclose -d finclose_ai -f - < temp_init.sql 2>$null
Remove-Item "temp_init.sql" -ErrorAction SilentlyContinue

Write-Host "✓ Database initialized" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Edit .env file with your credentials:" -ForegroundColor White
Write-Host "   - Open .env in Notepad" -ForegroundColor Gray
Write-Host "   - Add your NetSuite OAuth credentials" -ForegroundColor Gray
Write-Host "   - Add your Anthropic API key" -ForegroundColor Gray
Write-Host "   - Change default passwords" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start all services:" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Check service status:" -ForegroundColor White
Write-Host "   docker-compose ps" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. View logs:" -ForegroundColor White
Write-Host "   docker-compose logs -f" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Access the application:" -ForegroundColor White
Write-Host "   - Streamlit UI: http://localhost:8501" -ForegroundColor Green
Write-Host "   - MCP Server: http://localhost:8000" -ForegroundColor Green
Write-Host "   - Agent API: http://localhost:8001" -ForegroundColor Green
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Yellow
Write-Host ""
