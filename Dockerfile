# syntax=docker/dockerfile:1.7
#
# TRPM-LIMS production container image.
# Multi-stage build: a builder stage for Python deps, then a slim runtime stage.
#
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System build deps for psycopg2, cryptography, weasyprint, pillow, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=lims.settings \
    PORT=8000

# Runtime shared libraries (matches the builder's runtime-only dependencies).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        libjpeg62-turbo \
        zlib1g \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libffi8 \
        libssl3 \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r lims && useradd -r -g lims -d /app -s /sbin/nologin lims

COPY --from=builder /install /usr/local

WORKDIR /app
COPY --chown=lims:lims . /app

# Collect static at build time so the image is self-contained. SECRET_KEY is
# just a placeholder for the collectstatic step; real key comes from env at runtime.
RUN SECRET_KEY=build-time-placeholder DEBUG=False ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

RUN mkdir -p /app/logs /app/media && chown -R lims:lims /app/logs /app/media

USER lims
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:${PORT}/api/schema/ > /dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["gunicorn", "--config", "gunicorn.conf.py", "lims.wsgi:application"]
