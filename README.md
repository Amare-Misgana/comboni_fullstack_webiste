# Comboni School Management System

A comprehensive full-stack Django web application for managing school operations, including student management, teacher administration, class organization, materials sharing, real-time messaging, quizzes, and news updates.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Production Deployment](#production-deployment)
- [User Roles](#user-roles)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality

- **Multi-Role Authentication**: Separate dashboards for Admins, Teachers, Students, and Visitors
- **Real-Time Chat**: WebSocket-based messaging system with online status tracking
- **Student Management**: Complete CRUD operations for student records with bulk import/export via Excel
- **Teacher Management**: Teacher profiles, assignment to classes and subjects
- **Class Management**: Class creation, classroom assignment, homeroom teacher assignment
- **Subject Management**: Subject creation and assignment to classes and teachers
- **Material Sharing**: Upload, download, edit, and delete educational materials
- **Activity & Grading**: Activity creation with category-based weighting system
- **Quiz System**: Interactive quizzes with multiple choice, true/false, and fill-in-the-blank types
- **News Management**: News creation with email notifications to all users
- **Conduct Tracking**: Student conduct grade management

### Advanced Features

- **Excel Integration**: Bulk student/teacher import and template downloads
- **Email Notifications**: Automated email alerts for news updates
- **Activity Weight Management**: Configurable category weights for grading calculations
- **Online Status**: Real-time user online/offline status
- **Role-Based Access Control**: Secure access restrictions based on user roles
- **File Management**: Secure file uploads with organized media storage

## 🛠 Technology Stack

### Backend

- **Django 5.2.4**: Web framework
- **Django Channels**: WebSocket support for real-time features
- **Daphne**: ASGI server for WebSocket support
- **SQLite/PostgreSQL**: Database (SQLite for development, PostgreSQL recommended for production)

### Frontend

- **HTML5/CSS3**: Frontend structure and styling
- **JavaScript**: Interactive features and WebSocket client
- **Bootstrap/Tailwind**: CSS frameworks (if used)

### Additional Libraries

- **Pillow**: Image processing
- **Pandas**: Excel file handling
- **NumPy**: Data processing

## 📁 Project Structure

```
comboni_fullstack_webiste/
├── a_core/                    # Main project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Root URL configuration
│   ├── asgi.py               # ASGI configuration for WebSockets
│   └── wsgi.py               # WSGI configuration
│
├── common/                    # Shared models and utilities
│   ├── models.py             # CustomUser, ClassRoom, Activity, Material, etc.
│   └── utils.py              # Utility functions
│
├── a_school_admin/           # Admin application
│   ├── models.py             # AdminAction, News models
│   ├── views.py              # Admin views (dashboard, materials, news)
│   ├── views_f/              # Modular views
│   │   ├── view_class.py     # Class management views
│   │   ├── view_student.py   # Student management views
│   │   └── view_teacher.py   # Teacher management views
│   └── urls.py               # Admin URL patterns
│
├── a_teacher/                # Teacher application
│   ├── models.py             # TeacherAction, QuickQuiz, QuizChoice
│   ├── views.py              # Teacher dashboard, class views
│   └── quiz_views.py         # Quiz creation and management
│
├── a_student/                # Student application
│   ├── models.py             # StudentQuizResult
│   ├── views.py              # Student dashboard
│   └── quiz_views.py         # Student quiz interface
│
├── a_visitor/                # Public visitor application
│   ├── views.py              # Home, contact, about, news, login
│   └── templates/            # Public-facing templates
│
├── a_message/                # Messaging application
│   ├── models.py             # Message, OnlineStatus
│   ├── consumers.py          # WebSocket consumers
│   └── routing.py            # WebSocket URL routing
│
├── templates/                # Shared templates
│   ├── base.html
│   └── fragments/            # Reusable template fragments
│
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User-uploaded files
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── .env.example             # Environment variables template
```

## 🚀 Quick Start (One-Command Deployment)

**Fastest way to get started - just one command:**

```bash
python deploy.py
```

Or use Docker (Recommended for Production):

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

📖 See [QUICK_START.md](QUICK_START.md) for all deployment options.

---

## 🛠️ Manual Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd comboni_fullstack_webiste
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your configuration values
# See Configuration section below
```

### Step 5: Database Setup

```bash
# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser
```

### Step 6: Collect Static Files

```bash
python manage.py collectstatic
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development - SQLite)
# For production, use PostgreSQL
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_TIMEOUT=60

# Redis (for production WebSocket channels)
REDIS_URL=redis://localhost:6379/0

# Media & Static Files
MEDIA_ROOT=/path/to/media
STATIC_ROOT=/path/to/static
```

### Security Settings

For production, ensure:

- `DEBUG=False`
- Strong `SECRET_KEY` (use Django's `get_random_secret_key()`)
- Configure `ALLOWED_HOSTS` with your domain
- Use PostgreSQL database
- Enable HTTPS
- Configure proper CORS settings if needed

## 🏃 Running the Application

### Development Server

```bash
# Run Django development server
python manage.py runserver

# Run with Daphne for WebSocket support (recommended)
daphne -b 0.0.0.0 -p 8000 a_core.asgi:application
```

The application will be available at `http://localhost:8000`

### Access Points

- **Home/Visitor**: `http://localhost:8000/`
- **Admin Dashboard**: `http://localhost:8000/admin-dashboard/`
- **Teacher Dashboard**: `http://localhost:8000/teacher-dashboard/`
- **Student Dashboard**: `http://localhost:8000/student-dashboard/`
- **Django Admin**: `http://localhost:8000/admin/`

## 🚢 Production Deployment

### 1. Database Migration

For production, use PostgreSQL:

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update DATABASES in settings.py to use PostgreSQL
# Run migrations
python manage.py migrate
```

### 2. Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput
```

### 3. Channel Layers (Redis)

For WebSocket functionality in production, use Redis:

```bash
# Install Redis
# Update CHANNEL_LAYERS in settings.py
# Install channels-redis
pip install channels-redis
```

### 4. Server Configuration

- Use Gunicorn or uWSGI for WSGI
- Use Daphne for ASGI/WebSocket support
- Configure Nginx as reverse proxy
- Set up SSL/TLS certificates

### 5. Example Production Commands

```bash
# Using Gunicorn for HTTP
gunicorn a_core.wsgi:application --bind 0.0.0.0:8000

# Using Daphne for WebSocket support
daphne -b 0.0.0.0 -p 8000 a_core.asgi:application

# Or use supervisor/systemd for process management
```

## 👥 User Roles

### Admin

- Full system access
- Student/Teacher management
- Class and subject management
- News creation and management
- Material sharing
- Activity weight configuration
- View all admin actions log

### Teacher

- View assigned classes and students
- Create and manage activities
- Assign marks to students
- Share materials with classes
- Create quizzes (True/False, Multiple Choice, Fill-in-the-blank)
- Edit student conduct
- Real-time messaging with students and admins

### Student

- View personal dashboard
- Access shared materials
- View grades and activities
- Take quizzes
- Real-time messaging with classmates and teachers
- View news updates

### Visitor

- View public pages (home, about, contact)
- Browse news
- Access login pages

## 📡 API Endpoints

### Admin Endpoints

- `/admin-dashboard/` - Admin dashboard
- `/admin-dashboard/students-mang/` - Student management
- `/admin-dashboard/teachers-mang/` - Teacher management
- `/admin-dashboard/class-mang/` - Class management
- `/admin-dashboard/materials/` - Material management
- `/admin-dashboard/news/` - News management
- `/admin-dashboard/chat/` - Admin chat interface

### Teacher Endpoints

- `/teacher-dashboard/` - Teacher dashboard
- `/teacher-dashboard/classes/` - Assigned classes
- `/teacher-dashboard/set-quiz/` - Create quiz
- `/teacher-dashboard/chat/` - Teacher chat interface

### Student Endpoints

- `/student-dashboard/` - Student dashboard
- `/student-dashboard/quizzes/` - Available quizzes
- `/student-dashboard/material/` - Access materials
- `/student-dashboard/chat/` - Student chat interface

### Visitor Endpoints

- `/` - Home page
- `/about/` - About page
- `/contact/` - Contact page
- `/news/` - News listing
- `/login-choice/` - Login page selection
- `/login/<role>/` - Role-specific login

### WebSocket Endpoints

- `/ws/chat/<roomname>/` - Chat room WebSocket
- `/ws/online/` - Online status WebSocket

## 🔒 Security Features

- Role-based access control
- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection
- Secure password hashing
- Session security
- File upload validation
- Email verification ready

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep views focused and modular

### Testing

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test a_school_admin
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket connection fails**

   - Ensure Daphne is running
   - Check Redis connection (production)
   - Verify ASGI configuration

2. **Static files not loading**

   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATIC_URL` settings
   - Verify web server static file configuration

3. **Email not sending**

   - Verify email credentials in `.env`
   - Check SMTP server settings
   - For Gmail, use App Password

4. **Database connection errors**
   - Verify database credentials
   - Ensure database server is running
   - Check database permissions

## 📄 License

[Specify your license here]

## 👨‍💻 Author

[Your name/team name]

## 🙏 Acknowledgments

- Django community
- Django Channels team
- All contributors and testers

## 📞 Support

For issues, questions, or contributions, please:

- Open an issue on GitHub
- Contact the development team
- Check the documentation

---

**Note**: This application is designed for educational institutions and should be properly secured before deployment in a production environment.
