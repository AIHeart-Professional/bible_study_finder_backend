@echo off
REM Debug launcher for Bible Study Finder Backend (Windows)
echo Starting Bible Study Finder API Debug Server...
echo.

REM Set debug environment variables
set DEBUG=true
set ENVIRONMENT=development
set PYTHONPATH=%~dp0

echo Debug Mode: ON
echo Environment: Development
echo Working Directory: %~dp0
echo.

REM Try to run the debug server
python debug_server.py --mode fastapi

REM If that fails, try simple mode
if errorlevel 1 (
    echo.
    echo FastAPI failed, trying simple test server...
    python debug_server.py --mode simple
)

pause
