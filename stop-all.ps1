# FinClose AI - Stop All Services
# Stops MCP Server and Streamlit processes

Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "  FinClose AI - Stopping Services" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Find and stop Python processes running our applications
Write-Host "Finding running services..." -ForegroundColor Yellow

# Get Python processes
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es)" -ForegroundColor Yellow
    
    foreach ($process in $pythonProcesses) {
        $commandLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($process.Id)").CommandLine
        
        if ($commandLine -match "netsuite_server|streamlit|app\.py") {
            Write-Host "Stopping process $($process.Id): $($process.ProcessName)" -ForegroundColor Green
            Stop-Process -Id $process.Id -Force
        }
    }
    
    Write-Host ""
    Write-Host "✓ Services stopped" -ForegroundColor Green
} else {
    Write-Host "No Python processes found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "All services stopped." -ForegroundColor Green
Write-Host ""
