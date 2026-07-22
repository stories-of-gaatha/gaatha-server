#! /bin/bash

./manage.py wait_for_resources --db
# --access-logfile - routes access logs through Python logging so the
# health-probe filter (LOGGING in gaatha/settings.py) can drop /healthz/* hits.
gunicorn gaatha.wsgi:application --timeout=40 --bind 0.0.0.0:80 --access-logfile -
