web: gunicorn mailer.wsgi:application
worker: celery -A mailer worker -l info
beat: celery -A mailer beat -l info 