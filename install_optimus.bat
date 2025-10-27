@echo off
echo Installing OptimusPC...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install basic requirements
echo Installing basic requirements...
pip install -r requirements.txt

REM Try to install GPUtil (optional)
echo.
echo Attempting to install GPUtil for enhanced GPU monitoring...
pip install GPUtil 2>nul
if errorlevel 1 (
    echo Warning: GPUtil installation failed - GPU monitoring will use WMI only
    echo This is normal and OptimusPC will still work perfectly!
) else (
    echo GPUtil installed successfully - Enhanced GPU monitoring available!
)

echo.
echo Installation complete!
echo.
echo You can now run OptimusPC using: run_optimus.bat
echo.
pause

