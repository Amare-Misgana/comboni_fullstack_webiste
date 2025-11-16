# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Comboni School Management System to production.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Redis server (for WebSocket support)
- Domain name (optional but recommended)
- SSL certificate (recommended for production)
- Server with SSH access (e.g., Ubuntu, CentOS)

## Step 1: Server Setup

### Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Python and Dependencies

```bash
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx -y
```

## Step 2: Database Setup

### Create PostgreSQL Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE comboni_school_db;
CREATE USER comboni_user WITH PASSWORD 'your_secure_password';
ALTER ROLE comboni_user SET client_encoding TO 'utf8';
ALTER ROLE comboni_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE comboni_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE comboni_school_db TO comboni_user;
\q
```

## Step 3: Redis Setup

### Configure Redis

```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

## Step 4: Application Setup

### Clone Repository

```bash
cd /var/www
sudo git clone <your-repository-url> comboni_school
cd comboni_school
```

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Configuration

```bash
cp .env.example .env
nano .env
```

Update the `.env` file with production values:

```env
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DATABASE_URL=postgresql://comboni_user:your_secure_password@localhost/comboni_school_db

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

REDIS_URL=redis://localhost:6379/0

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Database Migration

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 5: Configure Application Server

### Using Daphne (Recommended for WebSocket support)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/comboni-school.service
```

Add the following:

```ini
[Unit]
Description=Comboni School Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/comboni_school
Environment="PATH=/var/www/comboni_school/venv/bin"
ExecStart=/var/www/comboni_school/venv/bin/daphne -b 0.0.0.0 -p 8000 a_core.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start comboni-school
sudo systemctl enable comboni-school
```

### Using Gunicorn (Alternative, WSGI only)

If you don't need WebSocket support, you can use Gunicorn:

```bash
sudo nano /etc/systemd/system/comboni-school.service
```

```ini
[Unit]
Description=Comboni School Management System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/comboni_school
Environment="PATH=/var/www/comboni_school/venv/bin"
ExecStart=/var/www/comboni_school/venv/bin/gunicorn --config gunicorn_config.py a_core.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

## Step 6: Configure Nginx

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/comboni-school
```

Add the following:

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS (uncomment after SSL setup)
    # return 301 https://$server_name$request_uri;

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Static files
    location /static/ {
        alias /var/www/comboni_school/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media-url/ {
        alias /var/www/comboni_school/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/comboni-school /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: SSL Certificate (Let's Encrypt)

Install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

Obtain SSL certificate:

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Step 8: Firewall Configuration

Configure UFW firewall:

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow SSH
sudo ufw enable
```

## Step 9: File Permissions

Set proper file permissions:

```bash
sudo chown -R www-data:www-data /var/www/comboni_school
sudo chmod -R 755 /var/www/comboni_school
sudo chmod -R 775 /var/www/comboni_school/media
```

## Step 10: Monitoring and Logging

### View Application Logs

```bash
sudo journalctl -u comboni-school -f
```

### View Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Step 11: Backup Strategy

### Database Backup

Create a backup script:

```bash
sudo nano /usr/local/bin/backup-comboni-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/comboni"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U comboni_user comboni_school_db > $BACKUP_DIR/db_backup_$DATE.sql
# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +30 -delete
```

Make it executable and schedule in crontab:

```bash
sudo chmod +x /usr/local/bin/backup-comboni-db.sh
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-comboni-db.sh
```

### Media Files Backup

```bash
sudo tar -czf /var/backups/comboni/media_backup_$(date +%Y%m%d).tar.gz /var/www/comboni_school/media/
```

## Troubleshooting

### Application won't start

- Check logs: `sudo journalctl -u comboni-school -n 50`
- Verify database connection
- Check Redis is running: `sudo systemctl status redis-server`
- Verify environment variables in `.env`

### Static files not loading

- Run: `python manage.py collectstatic --noinput`
- Check Nginx configuration
- Verify file permissions

### WebSocket connection fails

- Ensure Daphne is running (not Gunicorn)
- Check Redis connection
- Verify WebSocket configuration in Nginx

### Database connection errors

- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials in `.env`
- Test connection: `psql -U comboni_user -d comboni_school_db`

## Maintenance

### Update Application

```bash
cd /var/www/comboni_school
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart comboni-school
```

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Clear Cache (if using Redis for caching)

```bash
redis-cli FLUSHALL
```

## Security Checklist

- [ ] Change default secret key
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable HTTPS/SSL
- [ ] Use strong database passwords
- [ ] Set up firewall rules
- [ ] Configure regular backups
- [ ] Keep dependencies updated
- [ ] Set proper file permissions
- [ ] Use environment variables for sensitive data
- [ ] Enable security headers
- [ ] Configure rate limiting (optional)

## Performance Optimization

1. **Database Indexing**: Ensure proper indexes on frequently queried fields
2. **Caching**: Consider implementing Redis caching for frequently accessed data
3. **CDN**: Use a CDN for static files in high-traffic scenarios
4. **Database Connection Pooling**: Configure connection pooling for PostgreSQL
5. **Monitoring**: Set up monitoring tools (e.g., Sentry, New Relic)

## Support

For issues or questions:

- Check application logs
- Review Nginx error logs
- Verify all services are running
- Check firewall rules
- Review environment configuration
