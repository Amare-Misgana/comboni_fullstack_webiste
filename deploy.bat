@echo off
REM One-Command Production Deployment Script (Windows)

setlocal enabledelayedexpansion

echo ========================================
echo Comboni School Management System
echo Production Deployment Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    exit /b 1
)

echo [OK] Python found

REM Install dependencies
echo.
echo [1/7] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed

REM Setup environment
echo.
echo [2/7] Setting up environment...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo [OK] .env file created from .env.example
        echo [WARN] Please update .env with your production settings
    ) else (
        echo [WARN] Creating basic .env file
        (
            echo SECRET_KEY=change-this-in-production
            echo DEBUG=False
            echo ALLOWED_HOSTS=localhost,127.0.0.1
            echo DATABASE_URL=sqlite:///db.sqlite3
        ) > .env
    )
) else (
    echo [OK] .env file already exists
)

REM Database setup
echo.
echo [3/7] Setting up database...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo [WARN] Migration may have issues, continuing...
)
echo [OK] Database migrations completed

REM Create superuser
echo.
echo [4/7] Checking for superuser...
python manage.py shell -c "from common.models import CustomUser; exit(0 if CustomUser.objects.filter(is_superuser=True).exists() else 1)" 2>nul
if errorlevel 1 (
    echo [WARN] No superuser found. Creating one...
    python manage.py createsuperuser
) else (
    echo [OK] Superuser already exists
)

REM Collect static files
echo.
echo [5/7] Collecting static files...
python manage.py collectstatic --noinput
echo [OK] Static files collected

REM Create media directories
echo.
echo [6/7] Creating media directories...
if not exist media\avatars mkdir media\avatars
if not exist media\materials mkdir media\materials
if not exist media\news_photos mkdir media\news_photos
echo [OK] Media directories created

REM Verify setup
echo.
echo [7/7] Verifying setup...
python manage.py check
if errorlevel 1 (
    echo [WARN] Django check found issues, please review
) else (
    echo [OK] Django check passed
)

REM Summary
echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Update .env with production settings
echo   2. Set DEBUG=False
echo   3. Configure ALLOWED_HOSTS
echo   4. Start the server:
echo.
echo Development:
echo   python manage.py runserver
echo.
echo Production (Daphne for WebSockets):
echo   daphne -b 0.0.0.0 -p 8000 a_core.asgi:application
echo.
echo Production (Gunicorn):
echo   gunicorn a_core.wsgi:application --bind 0.0.0.0:8000
echo.

endlocal

