# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Configure Poetry to not create virtual environment (we're in a container)
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV APP_MODE=prod

# Collect static files (will be run during build or at runtime)
# RUN poetry run python silicon/_microservices/admin/manage.py collectstatic --noinput

# Expose port (Fly.io will set PORT env var)
EXPOSE 8000

# Health check script
RUN echo '#!/bin/bash\npoetry run python silicon/_microservices/admin/manage.py check --database default || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Start server (migrations run via release_command in fly.toml)
CMD poetry run gunicorn silicon.core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 600 \
    --access-logfile - \
    --error-logfile - \
    --log-level info

