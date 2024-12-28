#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# python manage.py collectstatic --no-input
# build.sh
python manage.py collectstatic --noinput
python manage.py migrate 