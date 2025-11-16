# Quick Start Guide - One-Command Deployment

This guide shows you how to deploy the Comboni School Management System to production with a single command.

## 🚀 Quick Deploy Options

### Option 1: Python Script (Cross-Platform)

**Windows, macOS, and Linux:**

```bash
python deploy.py
```

This script will:

- ✅ Check Python version
- ✅ Install all dependencies
- ✅ Create/update `.env` file with secure secret key
- ✅ Set up database and run migrations
- ✅ Create superuser (if needed)
- ✅ Collect static files
- ✅ Create media directories
- ✅ Verify the setup

### Option 2: Shell Script (Linux/macOS)

```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 3: Batch Script (Windows)

```cmd
deploy.bat
```

### Option 4: Docker (Recommended for Production)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📋 Prerequisites

### For Direct Deployment (Options 1-3):

- Python 3.8+
- pip
- PostgreSQL (optional, SQLite is default)
- Redis (optional, for WebSocket support)

### For Docker (Option 4):

- Docker
- Docker Compose

## 🎯 Step-by-Step Quick Start

### 1. Clone and Navigate

```bash
cd comboni_fullstack_webiste
```

### 2. Run Deployment Script

```bash
python deploy.py
```

### 3. Follow the Prompts

The script will:

- Ask for superuser credentials (if needed)
- Guide you through setup

### 4. Update Configuration

Edit `.env` file with your production settings:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Start Server

**Development:**

```bash
python manage.py runserver
```

**Production (WebSocket support):**

```bash
daphne -b 0.0.0.0 -p 8000 a_core.asgi:application
```

**Production (WSGI only):**

```bash
gunicorn a_core.wsgi:application --bind 0.0.0.0:8000
```

## 🐳 Docker Deployment (Easiest)

### 1. Create .env file

```bash
cp .env.example .env
# Edit .env with your settings
```

### 2. Start everything

```bash
docker-compose up -d
```

This automatically:

- ✅ Sets up PostgreSQL database
- ✅ Sets up Redis for WebSockets
- ✅ Builds and runs Django application
- ✅ Configures Nginx reverse proxy
- ✅ Handles all dependencies

### 3. Run migrations

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 4. Access the application

- Application: http://localhost:8000
- Admin: http://localhost:8000/admin/

## 🗄️ Database Setup (PostgreSQL)

### Automatic (with setup script):

```bash
python setup_db.py
```

This will:

- Check if PostgreSQL is installed
- Create database and user
- Update `.env` file automatically

### Manual:

```bash
# Linux/macOS
sudo -u postgres psql
CREATE DATABASE comboni_school_db;
CREATE USER comboni_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE comboni_school_db TO comboni_user;
\q
```

## 🔧 Common Commands

### Run Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Check Configuration

```bash
python manage.py check
```

### View Logs (Docker)

```bash
docker-compose logs -f web
```

### Restart Services (Docker)

```bash
docker-compose restart
```

## 🛠️ Troubleshooting

### Issue: Import errors

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution:**

1. Check if database server is running
2. Verify `.env` file has correct `DATABASE_URL`
3. For PostgreSQL, ensure user has proper permissions

### Issue: Static files not loading

**Solution:**

```bash
python manage.py collectstatic --noinput
```

### Issue: Permission denied

**Solution:** (Linux/macOS)

```bash
chmod +x deploy.sh
chmod +x deploy.py
```

### Issue: Docker containers not starting

**Solution:**

```bash
docker-compose down
docker-compose up -d --build
```

## 📝 Post-Deployment Checklist

- [ ] Update `.env` with production settings
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database (recommended)
- [ ] Configure email settings
- [ ] Set up SSL/HTTPS
- [ ] Configure Nginx (if not using Docker)
- [ ] Set up regular backups
- [ ] Configure monitoring
- [ ] Test all functionality

## 🎉 You're Done!

Your application should now be running. Access it at:

- **Development:** http://localhost:8000
- **Docker:** http://localhost (port 80) or http://localhost:8000

## 📚 Additional Resources

- See `DEPLOYMENT.md` for detailed production deployment
- See `README.md` for full documentation
- See `CHANGES.md` for recent changes

---

**Need Help?** Check the logs or review the detailed deployment guide in `DEPLOYMENT.md`.
