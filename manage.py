#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc

    # Create static directory if it doesn't exist
    try:
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mailer', 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
    except Exception as e:
        print(f"Warning: Could not create static directory: {e}")

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
