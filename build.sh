#!/bin/bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Create database tables
python manage.py makemigrations campaigns spreadsheets
python manage.py migrate

# Create superuser if needed (will be skipped if user exists)
python manage.py createsuperuser --noinput || true

# Verify Redis connection
python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
r.ping()
" || echo "Warning: Redis connection failed" 