#!/bin/bash
set -e

echo "[entrypoint] Checking wiki data..."
ls -la /app/data/wiki/concepts/ 2>&1 || echo "[entrypoint] WIKI DIR NOT FOUND at /app/data/wiki/concepts/"
ls -la /app/backend/../data/wiki/concepts/ 2>&1 || echo "[entrypoint] WIKI DIR NOT FOUND at /app/backend/../data/wiki/concepts/"
echo "[entrypoint] Concept files found: $(ls /app/data/wiki/concepts/*.md 2>/dev/null | wc -l)"

echo "[entrypoint] Running migrate..."
python manage.py migrate --noinput
echo "[entrypoint] Migrate done. Starting daphne..."

exec daphne -b 0.0.0.0 -p 8080 config.asgi:application
