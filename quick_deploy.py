#!/usr/bin/env python
"""
Quick Deployment Script - Skips checks and installs only what's needed
Faster version for when dependencies are already installed
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

# Colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
END = "\033[0m"
BOLD = "\033[1m"

def print_success(msg): print(f"{GREEN}✓ {msg}{END}")
def print_info(msg): print(f"{BLUE}ℹ {msg}{END}")
def print_warning(msg): print(f"{YELLOW}⚠ {msg}{END}")

def run_cmd(cmd, shell=True):
    """Quick command runner"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=False)
        return result.returncode == 0
    except:
        return False

def main():
    print(f"\n{BOLD}🚀 Quick Deployment{END}\n")
    
    # Load env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    
    # 1. Environment
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print_success(".env file created")
        else:
            print_warning(".env file not found, but continuing...")
    else:
        print_info(".env file exists")
    
    # 2. Dependencies (quick check)
    print_info("Checking key dependencies...")
    try:
        import django
        print_success(f"Django {django.get_version()} installed")
    except:
        print_warning("Installing dependencies (this may take a moment)...")
        run_cmd("pip install -r requirements.txt --quiet")
    
    # 3. Database
    print_info("Setting up database...")
    run_cmd("python manage.py makemigrations --noinput")
    if run_cmd("python manage.py migrate --noinput"):
        print_success("Database ready")
    else:
        run_cmd("python manage.py migrate")
        print_success("Database ready")
    
    # 4. Superuser check
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')
        import django
        django.setup()
        from common.models import CustomUser
        if CustomUser.objects.filter(is_superuser=True).exists():
            print_info("Superuser exists")
        else:
            print_warning("No superuser - run: python manage.py createsuperuser")
    except:
        print_warning("Could not check superuser")
    
    # 5. Static files
    print_info("Collecting static files...")
    run_cmd("python manage.py collectstatic --noinput")
    print_success("Static files ready")
    
    # 6. Media dirs
    for dir_path in ["media/avatars", "media/materials", "media/news_photos"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print_success("Media directories ready")
    
    # 7. Verify
    if run_cmd("python manage.py check"):
        print_success("Django check passed")
    
    print(f"\n{BOLD}✅ Quick deployment complete!{END}\n")
    print("Start server with:")
    print("  python manage.py runserver")
    print("  OR")
    print("  daphne -b 0.0.0.0 -p 8000 a_core.asgi:application\n")

if __name__ == "__main__":
    main()

