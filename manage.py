#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailer.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc

    # Create static directory if it doesn't exist
    try:
        base_dir = Path(__file__).resolve().parent
        static_dir = base_dir / 'mailer' / 'static'
        static_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create static directory: {e}")

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
