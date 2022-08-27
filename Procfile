web: gunicorn -c api/config/gunicorn.py api.config.wsgi:application

# SPECIAL
# Release phase is responsible for migrating the database
release: ./scripts/release.sh