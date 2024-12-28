#!/bin/bash
# Create necessary directories
mkdir -p static staticfiles media

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate 

chmod +x build.sh 