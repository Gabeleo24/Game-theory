@echo off
REM ADS599 Capstone - Team Member Setup Script (Windows)
REM This script sets up the complete development environment for new team members

setlocal enabledelayedexpansion

echo ==========================================
echo 🚀 ADS599 Capstone Team Member Setup
echo ==========================================
echo.

REM Check prerequisites
echo [INFO] Checking prerequisites...

REM Check Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Git is installed
) else (
    echo [ERROR] Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker is installed
) else (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker Compose is installed
    set DOCKER_COMPOSE_CMD=docker-compose
) else (
    docker compose version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Docker Compose is installed
        set DOCKER_COMPOSE_CMD=docker compose
    ) else (
        echo [ERROR] Docker Compose is not installed. Please install Docker Desktop with Compose.
        pause
        exit /b 1
    )
)

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Python is installed
    set PYTHON_CMD=python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [SUCCESS] Python is installed
        set PYTHON_CMD=python3
    ) else (
        echo [WARNING] Python is not installed. Some features may not work.
        set PYTHON_CMD=
    )
)

echo.

REM Setup project directories
echo [INFO] Setting up project directories...

if not exist "data" mkdir data
if not exist "data\cache" mkdir data\cache
if not exist "data\analysis" mkdir data\analysis
if not exist "data\reports" mkdir data\reports
if not exist "data\models" mkdir data\models
if not exist "logs" mkdir logs
if not exist "logs\sql_logs" mkdir logs\sql_logs
if not exist "notebooks" mkdir notebooks
if not exist "tests" mkdir tests

echo [SUCCESS] Project directories created

REM Setup configuration
echo [INFO] Setting up configuration files...

if not exist "config\api_keys.yaml" (
    if exist "config\api_keys_template.yaml" (
        copy "config\api_keys_template.yaml" "config\api_keys.yaml" >nul
        echo [SUCCESS] API keys template copied to config\api_keys.yaml
        echo [WARNING] ⚠️  IMPORTANT: Edit config\api_keys.yaml with your actual API keys!
    ) else (
        echo [ERROR] API keys template not found!
    )
) else (
    echo [SUCCESS] API keys configuration already exists
)

REM Setup Python virtual environment (if Python is available)
if not "%PYTHON_CMD%"=="" (
    echo [INFO] Setting up Python virtual environment...
    
    if not exist "venv" (
        %PYTHON_CMD% -m venv venv
        echo [SUCCESS] Python virtual environment created
        
        REM Activate virtual environment and install dependencies
        if exist "venv\Scripts\activate.bat" (
            call venv\Scripts\activate.bat
            if exist "requirements.txt" (
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                echo [SUCCESS] Python dependencies installed
            )
            call venv\Scripts\deactivate.bat
        )
    ) else (
        echo [SUCCESS] Python virtual environment already exists
    )
)

REM Setup Docker environment
echo [INFO] Setting up Docker environment...

REM Pull required Docker images
echo [INFO] Pulling Docker images (this may take a few minutes)...
%DOCKER_COMPOSE_CMD% pull

REM Build custom images
echo [INFO] Building custom Docker images...
%DOCKER_COMPOSE_CMD% build

echo [SUCCESS] Docker environment setup complete

REM Create team member configuration
echo [INFO] Creating team member configuration...

REM Get current date/time in ISO format (Windows compatible)
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "MIN=%dt:~10,2%" & set "SS=%dt:~12,2%"
set "setup_date=%YY%-%MM%-%DD%T%HH%:%MIN%:%SS%Z"

echo # Team Member Configuration > config\team_member_config.yaml
echo team_member: >> config\team_member_config.yaml
echo   setup_date: "%setup_date%" >> config\team_member_config.yaml
echo   setup_version: "1.0" >> config\team_member_config.yaml
echo   environment: "development" >> config\team_member_config.yaml
echo. >> config\team_member_config.yaml
echo # Development preferences >> config\team_member_config.yaml
echo development: >> config\team_member_config.yaml
echo   auto_start_services: true >> config\team_member_config.yaml
echo   enable_debug_logging: true >> config\team_member_config.yaml
echo   jupyter_password: "soccer_intelligence" >> config\team_member_config.yaml

echo [SUCCESS] Team member configuration created

REM Setup development environment files
echo [INFO] Setting up development environment...

if not exist ".env" (
    echo # Development Environment Variables > .env
    echo ENVIRONMENT=development >> .env
    echo DEBUG=true >> .env
    echo. >> .env
    echo # Database Configuration >> .env
    echo POSTGRES_DB=soccer_intelligence >> .env
    echo POSTGRES_USER=soccerapp >> .env
    echo POSTGRES_PASSWORD=soccerpass123 >> .env
    echo. >> .env
    echo # Jupyter Configuration >> .env
    echo JUPYTER_PASSWORD=soccer_intelligence >> .env
    echo. >> .env
    echo # API Configuration (edit config/api_keys.yaml instead) >> .env
    echo # API keys should be configured in config/api_keys.yaml >> .env
    
    echo [SUCCESS] Development environment file created
)

REM Final setup verification
echo [INFO] Running setup verification...

REM Test Docker Compose configuration
%DOCKER_COMPOSE_CMD% config >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Docker Compose configuration is valid
) else (
    echo [ERROR] Docker Compose configuration has errors
    pause
    exit /b 1
)

REM Create setup completion marker
echo %setup_date% > .setup_complete

echo [SUCCESS] Setup verification complete

echo.
echo ==========================================
echo 🎉 Team Member Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. 📝 Edit config\api_keys.yaml with your API keys
echo 2. 🚀 Start the system: %DOCKER_COMPOSE_CMD% up -d
echo 3. ✅ Verify setup: scripts\setup\verify_setup.bat
echo 4. 📚 Read the documentation in docs\
echo.
echo Access points after starting:
echo 📊 Database: localhost:5432
echo 🔍 pgAdmin: http://localhost:8080
echo 📓 Jupyter: http://localhost:8888
echo 📈 Streamlit: http://localhost:8501
echo.
echo For help, see docs\setup\TEAM_MEMBER_ONBOARDING.md
echo or create an issue on GitHub.
echo.
echo [SUCCESS] Welcome to the ADS599 Capstone team! 🚀

pause
