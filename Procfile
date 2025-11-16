# Procfile for Heroku or similar platforms
# For ASGI/WebSocket support, use Daphne
web: daphne -b 0.0.0.0 -p $PORT a_core.asgi:application

# Alternative: For WSGI-only (no WebSockets)
# web: gunicorn a_core.wsgi:application --bind 0.0.0.0:$PORT --workers 4

# For background tasks (if using Celery)
# worker: celery -A a_core worker -l info

