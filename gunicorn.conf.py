"""
Gunicorn configuration for TRPM-LIMS.

Tunables are read from environment variables so the same image can be
deployed in different environments without rebuilding.
"""
import multiprocessing
import os

# ----- Socket -----
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:8000')

# ----- Workers -----
# Default: (2 x CPU) + 1, capped at 8 to avoid OOM on small nodes.
_default_workers = min((multiprocessing.cpu_count() * 2) + 1, 8)
workers = int(os.environ.get('GUNICORN_WORKERS', _default_workers))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gthread')
threads = int(os.environ.get('GUNICORN_THREADS', '4'))
worker_connections = int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', '1000'))

# Recycle workers to avoid memory leaks.
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', '100'))

# ----- Timeouts -----
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '60'))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', '30'))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '5'))

# ----- Logging -----
# Log to stdout/stderr so Docker / systemd / k8s can collect them.
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# ----- Hygiene -----
preload_app = True  # Load the Django app once in the master before forking.
forwarded_allow_ips = '*'  # Trust X-Forwarded-* from the reverse proxy.
proc_name = 'trpm-lims'
