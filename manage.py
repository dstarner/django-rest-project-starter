#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from dotenv import load_dotenv

COVERAGE_COMMANDS = [
    'test',
    'checks',
]

# Load from .env if it exists
load_dotenv()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.config.settings')

    can_cover = any(map(lambda arg: arg in sys.argv, COVERAGE_COMMANDS))
    skip_coverage = sys.argv.pop(sys.argv.index('--skip-cov')) if can_cover and '--skip-cov' in sys.argv else False
    perform_coverage = can_cover and not skip_coverage
    if perform_coverage:
        import coverage
        cov = coverage.coverage(
            source=['api'],
            config_file='setup.cfg',
        )
        cov.erase()
        cov.start()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    if perform_coverage:
        cov.stop()
        cov.save()
        cov.report()
        cov.html_report(directory='coverage-report')


if __name__ == '__main__':
    main()
