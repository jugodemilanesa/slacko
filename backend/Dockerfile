FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Build-time defaults (Railway env vars las sobreescriben en runtime)
ENV DJANGO_SETTINGS_MODULE=config.settings.production
ENV SECRET_KEY=dummy-build-only-key

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8080

ENV PORT=8080

CMD ["./docker-entrypoint.sh"]
