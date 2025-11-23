# FinClose AI - Start All Services (Native Windows)
# Run this script to start MCP Server and Streamlit

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "  FinClose AI - Starting Services" -ForegroundColor Cyan
Write-Host "  (Native Windows - No Docker)" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠  .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and configure it" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "⚠  Could not activate virtual environment" -ForegroundColor Yellow
    Write-Host "Continuing without virtual environment..." -ForegroundColor Yellow
}

Write-Host ""

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Green
$packages = pip list 2>$null
if ($packages -notmatch "langgraph") {
    Write-Host "⚠  Dependencies not installed" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Green
    
    pip install -q -r mcp-server\requirements.txt
    pip install -q -r agents\requirements.txt
    pip install -q -r streamlit-app\requirements.txt
    pip install -q psycopg2-binary python-dotenv
    
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Starting Services" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Start MCP Server in new window
Write-Host "Starting NetSuite MCP Server..." -ForegroundColor Green
$mcpScript = @"
cd '$PWD'
& .\venv\Scripts\Activate.ps1
cd mcp-server
Write-Host '=================================================='  -ForegroundColor Cyan
Write-Host '  NetSuite MCP Server' -ForegroundColor Cyan
Write-Host '  Port: 8000' -ForegroundColor Cyan
Write-Host '=================================================='  -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting server...' -ForegroundColor Green
python netsuite_server.py
"@

$mcpProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $mcpScript -PassThru
Write-Host "✓ MCP Server started (PID: $($mcpProcess.Id))" -ForegroundColor Green

# Wait for MCP server to start
Write-Host "Waiting for MCP Server to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""

# Start Streamlit in new window
Write-Host "Starting Streamlit Web Application..." -ForegroundColor Green
$streamlitScript = @"
cd '$PWD'
& .\venv\Scripts\Activate.ps1
cd streamlit-app
Write-Host '=================================================='  -ForegroundColor Cyan
Write-Host '  Streamlit Web Application' -ForegroundColor Cyan
Write-Host '  URL: http://localhost:8501' -ForegroundColor Cyan
Write-Host '=================================================='  -ForegroundColor Cyan
Write-Host ''
Write-Host 'Starting Streamlit...' -ForegroundColor Green
Write-Host 'Your browser will open automatically...' -ForegroundColor Yellow
Write-Host ''
streamlit run app.py
"@

$streamlitProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $streamlitScript -PassThru
Write-Host "✓ Streamlit started (PID: $($streamlitProcess.Id))" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Services Started Successfully!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Yellow
Write-Host "  → http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login credentials:" -ForegroundColor Yellow
Write-Host "  Username: justine  |  Password: demo" -ForegroundColor White
Write-Host "  Username: selena   |  Password: demo" -ForegroundColor White
Write-Host "  Username: will     |  Password: demo" -ForegroundColor White
Write-Host ""
Write-Host "Services running in separate windows:" -ForegroundColor Yellow
Write-Host "  → MCP Server (PID: $($mcpProcess.Id))" -ForegroundColor Gray
Write-Host "  → Streamlit (PID: $($streamlitProcess.Id))" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "  1. Close the PowerShell windows" -ForegroundColor Gray
Write-Host "  2. Or run: .\stop-all.ps1" -ForegroundColor Gray
Write-Host "  3. Or press Ctrl+C in each window" -ForegroundColor Gray
Write-Host ""
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open browser
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "✓ Browser opened!" -ForegroundColor Green
Write-Host ""
Write-Host "This window can be closed. Services will continue running." -ForegroundColor Gray
Write-Host ""
