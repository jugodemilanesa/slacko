#!/bin/bash
set -e

echo "[entrypoint] Running migrate..."
python manage.py migrate --noinput
echo "[entrypoint] Migrate done. Starting daphne..."

exec daphne -b 0.0.0.0 -p 8080 config.asgi:application
