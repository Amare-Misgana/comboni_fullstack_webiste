#!/usr/bin/env python
"""
Database Setup Script
Helps set up PostgreSQL database for production.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, shell=False):
    """Run a shell command."""
    try:
        result = subprocess.run(
            command if shell else command.split(),
            capture_output=True,
            text=True,
            shell=shell,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_postgresql():
    """Check if PostgreSQL is installed and running."""
    success, stdout, stderr = run_command("psql --version", shell=True)
    return success


def create_postgres_database():
    """Create PostgreSQL database interactively."""
    print("\n=== PostgreSQL Database Setup ===\n")

    if not check_postgresql():
        print("⚠ PostgreSQL not found. Please install PostgreSQL first.")
        print("   Ubuntu/Debian: sudo apt install postgresql postgresql-contrib")
        print("   macOS: brew install postgresql")
        print("   Windows: Download from https://www.postgresql.org/download/")
        return False

    print("PostgreSQL detected!\n")

    # Get database credentials
    db_name = (
        input("Database name [comboni_school_db]: ").strip() or "comboni_school_db"
    )
    db_user = input("Database user [comboni_user]: ").strip() or "comboni_user"
    db_password = input(f"Password for user '{db_user}': ").strip()

    if not db_password:
        print("❌ Password is required")
        return False

    # Create database and user
    commands = [
        f"sudo -u postgres psql -c \"CREATE USER {db_user} WITH PASSWORD '{db_password}';\"",
        f"sudo -u postgres psql -c \"ALTER ROLE {db_user} SET client_encoding TO 'utf8';\"",
        f"sudo -u postgres psql -c \"ALTER ROLE {db_user} SET default_transaction_isolation TO 'read committed';\"",
        f"sudo -u postgres psql -c \"ALTER ROLE {db_user} SET timezone TO 'UTC';\"",
        f'sudo -u postgres psql -c "CREATE DATABASE {db_name} OWNER {db_user};"',
        f'sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};"',
    ]

    print("\nCreating database and user...")
    for cmd in commands:
        success, stdout, stderr = run_command(cmd, shell=True)
        if not success and "already exists" not in stderr:
            print(f"⚠ Warning: {stderr}")

    # Update .env file
    db_url = f"postgresql://{db_user}:{db_password}@localhost/{db_name}"

    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()

        if "DATABASE_URL=" in content:
            lines = content.split("\n")
            new_lines = []
            for line in lines:
                if line.startswith("DATABASE_URL="):
                    new_lines.append(f"DATABASE_URL={db_url}")
                else:
                    new_lines.append(line)
            content = "\n".join(new_lines)
        else:
            content += f"\nDATABASE_URL={db_url}\n"

        with open(env_file, "w") as f:
            f.write(content)

        print(f"\n✓ Database URL added to .env file")
        print(f"✓ Database created: {db_name}")
        print(f"✓ User created: {db_user}")
        print("\nNext: Run migrations with 'python manage.py migrate'")
        return True
    else:
        print("⚠ .env file not found. Creating it...")
        with open(env_file, "w") as f:
            f.write(f"DATABASE_URL={db_url}\n")
        print("✓ .env file created with database URL")
        return True


def main():
    """Main function."""
    print("=" * 60)
    print("Database Setup Tool")
    print("=" * 60)

    choice = (
        input(
            "\nChoose database type:\n1. PostgreSQL (Production)\n2. SQLite (Development)\nChoice [1]: "
        ).strip()
        or "1"
    )

    if choice == "1":
        create_postgres_database()
    else:
        print("\nSQLite will be used by default (no setup needed)")
        print("Database file: db.sqlite3")


if __name__ == "__main__":
    main()
