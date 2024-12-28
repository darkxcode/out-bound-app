#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser (will be skipped if user exists)
python manage.py createsuperuser --noinput || true 