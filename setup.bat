@echo off
REM EMA Trading Bot - Setup Script for Windows

echo ==========================================
echo EMA Trading Bot - Setup Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found

REM Create virtual environment
echo.
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [WARNING] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo.
echo Installing Python packages...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo [OK] Packages installed
) else (
    echo [ERROR] requirements.txt not found
    pause
    exit /b 1
)

REM Create config.ini from example
echo.
echo Setting up configuration...
if not exist "config.ini" (
    if exist "config.ini.example" (
        copy config.ini.example config.ini
        echo [OK] config.ini created from template
        echo [WARNING] Please edit config.ini and add your API credentials
    ) else (
        echo [ERROR] config.ini.example not found
    )
) else (
    echo [WARNING] config.ini already exists
)

REM Create directories
echo.
echo Creating directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "backtest_results" mkdir backtest_results
if not exist "charts" mkdir charts
echo [OK] Directories created

REM Initialize database
echo.
echo Initializing database...
python -c "from database_handler import TradingDatabase; TradingDatabase()" 2>nul
echo [OK] Database initialized

REM Summary
echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit config.ini and add your API credentials
echo 2. Run: python main.py --dashboard
echo 3. Start with paper trading: python main.py --paper
echo.
echo For help: python main.py --help
echo.
echo Happy Trading! 📈
echo.
pause
