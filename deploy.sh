#!/bin/bash
# One-Command Production Deployment Script (Linux/macOS)

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Comboni School Management System${NC}"
echo -e "${BLUE}Production Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found${NC}"

# Install dependencies
echo -e "\n${BLUE}[1/7] Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Setup environment
echo -e "\n${BLUE}[2/7] Setting up environment...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ .env file created from .env.example${NC}"
        echo -e "${YELLOW}⚠ Please update .env with your production settings${NC}"
    else
        echo -e "${YELLOW}⚠ .env.example not found, creating basic .env${NC}"
        cat > .env << EOF
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EOF
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Database setup
echo -e "\n${BLUE}[3/7] Setting up database...${NC}"
python3 manage.py makemigrations
python3 manage.py migrate
echo -e "${GREEN}✓ Database migrations completed${NC}"

# Create superuser if needed
echo -e "\n${BLUE}[4/7] Checking for superuser...${NC}"
if ! python3 manage.py shell -c "from common.models import CustomUser; exit(0 if CustomUser.objects.filter(is_superuser=True).exists() else 1)" 2>/dev/null; then
    echo -e "${YELLOW}No superuser found. Creating one...${NC}"
    python3 manage.py createsuperuser
else
    echo -e "${GREEN}✓ Superuser already exists${NC}"
fi

# Collect static files
echo -e "\n${BLUE}[5/7] Collecting static files...${NC}"
python3 manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

# Create media directories
echo -e "\n${BLUE}[6/7] Creating media directories...${NC}"
mkdir -p media/avatars media/materials media/news_photos
echo -e "${GREEN}✓ Media directories created${NC}"

# Verify setup
echo -e "\n${BLUE}[7/7] Verifying setup...${NC}"
python3 manage.py check
echo -e "${GREEN}✓ Django check passed${NC}"

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "Next steps:"
echo -e "  1. Update .env with production settings"
echo -e "  2. Set DEBUG=False"
echo -e "  3. Configure ALLOWED_HOSTS"
echo -e "  4. Start the server:\n"

echo -e "${BLUE}Development:${NC}"
echo -e "  python3 manage.py runserver\n"

echo -e "${BLUE}Production (Daphne for WebSockets):${NC}"
echo -e "  daphne -b 0.0.0.0 -p 8000 a_core.asgi:application\n"

echo -e "${BLUE}Production (Gunicorn):${NC}"
echo -e "  gunicorn a_core.wsgi:application --bind 0.0.0.0:8000\n"

