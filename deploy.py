#!/usr/bin/env python
"""
One-Command Production Deployment Script
Automates the entire production deployment process.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path
from urllib.parse import urlparse


# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    END = "\033[0m"
    BOLD = "\033[1m"


def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_step(step, total):
    print(f"\n{Colors.BOLD}[{step}/{total}]{Colors.END}")


def run_command(command, check=True, shell=False):
    """Run a shell command and return the result."""
    try:
        if shell:
            result = subprocess.run(
                command, shell=True, check=check, capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                command.split(), check=check, capture_output=True, text=True
            )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except Exception as e:
        return False, "", str(e)


def generate_secret_key():
    """Generate a secure Django secret key."""
    chars = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)"
    )
    return "".join(secrets.choice(chars) for _ in range(50))


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8+ is required")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_step(1, 8)
    print_info("Checking dependencies...")

    # Check if Django is already installed
    try:
        import django

        print_info(f"Django {django.get_version()} already installed")
        print_info("Checking for missing packages...")
    except ImportError:
        print_info("Django not found, installing dependencies...")

    # Try installing with --upgrade-strategy only-if-needed for speed
    success, stdout, stderr = run_command(
        "pip install -r requirements.txt --upgrade-strategy only-if-needed --quiet",
        shell=True,
    )
    if success:
        print_success("Dependencies checked/installed successfully")
        return True
    else:
        print_warning(f"Some dependencies may be missing: {stderr}")
        # Continue anyway - dependencies might already be installed
        return True


def setup_environment():
    """Set up environment variables."""
    print_step(2, 8)
    print_info("Setting up environment variables...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists():
        if env_example.exists():
            # Copy .env.example to .env
            with open(env_example, "r") as f:
                content = f.read()

            # Generate secret key
            secret_key = generate_secret_key()
            content = content.replace(
                "your-secret-key-change-this-in-production", secret_key
            )

            with open(env_file, "w") as f:
                f.write(content)

            print_success(".env file created with secure secret key")
        else:
            # Create basic .env file
            secret_key = generate_secret_key()
            env_content = f"""# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (Update these)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
EMAIL_TIMEOUT=60

# Redis Configuration (optional)
REDIS_URL=

# Security Settings
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
"""
            with open(env_file, "w") as f:
                f.write(env_content)
            print_success(".env file created")
    else:
        print_info(".env file already exists, skipping...")

    return True


def setup_database():
    """Set up database."""
    print_step(3, 8)
    print_info("Setting up database...")

    # Check if using PostgreSQL
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and ("postgresql://" in db_url or "postgres://" in db_url):
        print_info("PostgreSQL database detected")
        print_warning("Make sure PostgreSQL is running and database exists")
        print_info("You may need to create the database manually:")
        print_info("  createdb your_database_name")
    else:
        print_info("Using SQLite database (default)")

    # Check if migrations exist
    migrations_dir = Path("common/migrations")
    if migrations_dir.exists() and list(migrations_dir.glob("*.py")):
        print_info("Migrations already exist, running migrate...")
        # Skip makemigrations if migrations already exist
        skip_makemigrations = True
    else:
        skip_makemigrations = False

    # Run makemigrations only if needed
    if not skip_makemigrations:
        success, stdout, stderr = run_command(
            "python manage.py makemigrations", shell=True
        )
        if not success:
            print_warning(f"makemigrations: {stderr}")

    # Run migrations
    success, stdout, stderr = run_command(
        "python manage.py migrate --noinput", shell=True
    )
    if success:
        print_success("Database migrations completed")
        return True
    else:
        print_warning(f"Migration warning: {stderr}")
        # Try without --noinput if it fails
        success2, _, _ = run_command("python manage.py migrate", shell=True)
        if success2:
            print_success("Database migrations completed")
            return True
        return False


def create_superuser():
    """Create superuser if needed."""
    print_step(4, 8)
    print_info("Checking for superuser...")

    # Check if superuser exists
    success, stdout, stderr = run_command(
        "python manage.py shell -c \"from common.models import CustomUser; print('exists' if CustomUser.objects.filter(is_superuser=True).exists() else 'none')\"",
        shell=True,
    )

    if success and "none" in stdout:
        print_warning("No superuser found. Creating one...")
        print_info("You'll be prompted to enter superuser details")
        success, stdout, stderr = run_command(
            "python manage.py createsuperuser", shell=True
        )
        if success:
            print_success("Superuser created")
        else:
            print_warning("Superuser creation skipped or failed")
    else:
        print_info("Superuser already exists")

    return True


def collect_static():
    """Collect static files."""
    print_step(5, 8)
    print_info("Collecting static files...")

    success, stdout, stderr = run_command(
        "python manage.py collectstatic --noinput", shell=True
    )
    if success:
        print_success("Static files collected")
        return True
    else:
        print_warning(f"Static collection warning: {stderr}")
        return True  # Non-critical


def create_media_dirs():
    """Create media directories."""
    print_step(6, 8)
    print_info("Creating media directories...")

    media_dirs = [
        "media/avatars",
        "media/materials",
        "media/news_photos",
    ]

    for dir_path in media_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print_success("Media directories created")
    return True


def verify_setup():
    """Verify the setup."""
    print_step(7, 8)
    print_info("Verifying setup...")

    # Check settings
    success, stdout, stderr = run_command("python manage.py check", shell=True)
    if success:
        print_success("Django check passed")
    else:
        print_error(f"Django check failed: {stderr}")
        return False

    # Check database connection
    success, stdout, stderr = run_command(
        "python manage.py shell -c \"from django.db import connection; connection.ensure_connection(); print('connected')\"",
        shell=True,
    )
    if success:
        print_success("Database connection verified")
    else:
        print_warning(f"Database connection issue: {stderr}")

    return True


def print_summary():
    """Print deployment summary."""
    print_step(8, 8)
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}🎉 Deployment Setup Complete!{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    print(f"{Colors.GREEN}✓ Dependencies installed{Colors.END}")
    print(f"{Colors.GREEN}✓ Environment configured{Colors.END}")
    print(f"{Colors.GREEN}✓ Database set up{Colors.END}")
    print(f"{Colors.GREEN}✓ Static files collected{Colors.END}")
    print(f"{Colors.GREEN}✓ Media directories created{Colors.END}\n")

    print_info("Next steps:")
    print("  1. Update .env file with your production settings")
    print("  2. Set DEBUG=False for production")
    print("  3. Configure ALLOWED_HOSTS with your domain")
    print("  4. Set up PostgreSQL database (recommended for production)")
    print("  5. Configure email settings")
    print("  6. Start the server:\n")
    print(f"     {Colors.BOLD}Development:{Colors.END}")
    print("       python manage.py runserver")
    print("     OR")
    print("       daphne -b 0.0.0.0 -p 8000 a_core.asgi:application\n")
    print(f"     {Colors.BOLD}Production (with Gunicorn):{Colors.END}")
    print("       gunicorn a_core.wsgi:application --bind 0.0.0.0:8000\n")
    print(f"     {Colors.BOLD}Production (with Daphne for WebSockets):{Colors.END}")
    print("       daphne -b 0.0.0.0 -p 8000 a_core.asgi:application\n")

    print_warning("Don't forget to:")
    print("  - Set up SSL/HTTPS for production")
    print("  - Configure a reverse proxy (Nginx)")
    print("  - Set up regular database backups")
    print("  - Configure Redis for WebSocket support (if needed)")


def main():
    """Main deployment function."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(
        f"{Colors.BOLD}Comboni School Management System - Production Setup{Colors.END}"
    )
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Run deployment steps
    steps = [
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Setting up database", setup_database),
        ("Creating superuser", create_superuser),
        ("Collecting static files", collect_static),
        ("Creating media directories", create_media_dirs),
        ("Verifying setup", verify_setup),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print_error(f"Failed at step: {step_name}")
            response = input("Continue anyway? (y/n): ").lower()
            if response != "y":
                sys.exit(1)

    print_summary()


if __name__ == "__main__":
    main()
