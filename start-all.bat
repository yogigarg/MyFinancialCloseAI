@echo off
REM FinClose AI - Startup Script (Batch File Version)
REM Double-click this file to start the application

echo ================================================
echo   FinClose AI - Starting Services
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Done.
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing/checking dependencies...
pip install -q -r mcp-server\requirements.txt
pip install -q -r agents\requirements.txt
pip install -q -r streamlit-app\requirements.txt
pip install -q psycopg2-binary python-dotenv

echo.
echo ================================================
echo   Starting Services
echo ================================================
echo.

REM Start MCP Server in new window
echo Starting MCP Server...
start "FinClose AI - MCP Server" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && cd mcp-server && echo MCP Server running on port 8000 && python netsuite_server.py"

REM Wait 5 seconds
timeout /t 5 /nobreak > nul

REM Start Streamlit in new window
echo Starting Streamlit...
start "FinClose AI - Streamlit" cmd /k "cd /d %CD% && call venv\Scripts\activate.bat && cd streamlit-app && echo Streamlit running at http://localhost:8501 && streamlit run app.py"

REM Wait 3 seconds
timeout /t 3 /nobreak > nul

REM Open browser
echo.
echo Opening browser...
start http://localhost:8501

echo.
echo ================================================
echo   Services Started!
echo ================================================
echo.
echo Access: http://localhost:8501
echo Login: justine / demo
echo.
echo Two windows opened:
echo   1. MCP Server (port 8000)
echo   2. Streamlit (port 8501)
echo.
echo To stop: Close those windows or run stop-all.bat
echo.
echo You can close this window now.
echo.
pause
