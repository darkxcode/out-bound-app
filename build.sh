#!/bin/bash
# Exit on error
set -o errexit

# Install system dependencies
apt-get update
apt-get install -y \
    python3-dev \
    postgresql-client \
    postgresql-contrib \
    libpq-dev \
    gcc \
    python3-pip

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install wheel
pip install psycopg2-binary
pip install -r requirements.txt

# Create necessary directories
mkdir -p mailer/static
mkdir -p staticfiles

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate 