"""
Django settings for the TRPM-LIMS project.

Configuration is loaded from environment variables (12-factor style) using
django-environ. See `.env.example` for the full list of supported variables.
For local development, copy `.env.example` to `.env` and adjust as needed.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    CORS_ALLOW_ALL_ORIGINS=(bool, False),
    SECURE_SSL_REDIRECT=(bool, True),
    SECURE_HSTS_SECONDS=(int, 60 * 60 * 24 * 365),  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS=(bool, True),
    SECURE_HSTS_PRELOAD=(bool, True),
    SESSION_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_SECURE=(bool, True),
    CSRF_TRUSTED_ORIGINS=(list, []),
    SENTRY_DSN=(str, ''),
    SENTRY_ENVIRONMENT=(str, 'production'),
    SENTRY_TRACES_SAMPLE_RATE=(float, 0.0),
    EMAIL_BACKEND=(str, 'django.core.mail.backends.smtp.EmailBackend'),
    EMAIL_HOST=(str, ''),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    EMAIL_USE_TLS=(bool, True),
    DEFAULT_FROM_EMAIL=(str, 'no-reply@trpm-lims.local'),
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/0'),
    CELERY_RESULT_BACKEND=(str, 'redis://localhost:6379/0'),
    NCBI_API_KEY=(str, ''),
    NCBI_EMAIL=(str, 'admin@trpm-lims.org'),
    FHIR_BASE_URL=(str, 'http://localhost:8000/fhir'),
    # Compliance feature flags.
    # ENABLE_PART11: when True, electronic signatures are required on
    # result approval / release workflows per 21 CFR Part 11. Clinical
    # deployments should set this; research deployments leave it off.
    ENABLE_PART11=(bool, False),
    ENABLE_HIPAA_MODE=(bool, False),
)

# Load .env if present (local dev convenience; never commit .env to VCS).
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(str(env_file))

# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------
# SECRET_KEY MUST be supplied via env in any non-trivial environment.
# A clearly-marked dev fallback is used only when DEBUG=True so a fresh
# checkout still works for local development.
DEBUG = env('DEBUG')

if DEBUG:
    SECRET_KEY = env(
        'SECRET_KEY',
        default='django-insecure-DEV-ONLY-DO-NOT-USE-IN-PRODUCTION',
    )
else:
    SECRET_KEY = env('SECRET_KEY')  # Raises ImproperlyConfigured if missing.

ALLOWED_HOSTS = env('ALLOWED_HOSTS')
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'drf_spectacular',
    'corsheaders',
    'django_otp',
    'django_otp.plugins.otp_totp',

    # Core LIMS apps
    'lab_management',
    'reagents',
    'molecular_diagnostics',
    'equipment',
    'storage',

    # Phase 1 apps
    'api',
    'users',
    'audit',
    'data_exchange',

    # Phase 2 apps
    'analytics',
    'transfers',
    'compliance',

    # Phase 3 apps
    'instruments',

    # Phase 4 apps - Feature gaps implementation
    'tenants',
    'single_cell',
    'bioinformatics',
    'ontology',
    'sensors',
    'dynamic_fields',
    'projects',
    'billing',

    # Phase 5 apps
    'microbiology',
    'qms',
    'messaging',
    'pathology',

    # Phase 6 apps
    'pharmacogenomics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must come immediately after SecurityMiddleware.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',
    'users.middleware.UserActivityMiddleware',
    'users.middleware.PasswordChangeMiddleware',
    'users.mfa.MFAEnforcementMiddleware',
    'tenants.middleware.TenantMiddleware',
]

ROOT_URLCONF = 'lims.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lims.wsgi.application'

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
# Defaults to SQLite for local dev. In production, set DATABASE_URL to a
# PostgreSQL DSN, e.g.:
#   DATABASE_URL=postgres://user:pass@host:5432/trpm_lims
DATABASES = {
    'default': env.db_url(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
    ),
}

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    # Prevent reuse of the last N passwords (21 CFR 11.300(b), HIPAA baseline).
    {'NAME': 'users.validators.PasswordHistoryValidator',
     'OPTIONS': {'history_length': 5}},
]

# Password aging: force a change every N days. Set to 0 to disable.
PASSWORD_MAX_AGE_DAYS = env.int('PASSWORD_MAX_AGE_DAYS', default=90)

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# ---------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise compressed + hashed static file storage for production.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# HTTPS / cookie / browser hardening
# ---------------------------------------------------------------------------
# Honor X-Forwarded-Proto from a TLS-terminating reverse proxy / load balancer.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

if not DEBUG:
    SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT')
    SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS')
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS')
    SECURE_HSTS_PRELOAD = env('SECURE_HSTS_PRELOAD')
    SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')
    CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')

CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS')

# ---------------------------------------------------------------------------
# Laboratory branding (used in generated reports)
# ---------------------------------------------------------------------------
LAB_NAME = env('LAB_NAME', default='Translational Research and Precision Medicine Lab')
LAB_ADDRESS = env('LAB_ADDRESS', default='')
LAB_PHONE = env('LAB_PHONE', default='')
LAB_ACCREDITATION = env('LAB_ACCREDITATION', default='')

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

from datetime import timedelta  # noqa: E402  (kept local to JWT block)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'TRPM-LIMS API',
    'DESCRIPTION': 'REST API for Translational Research and Precision Medicine LIMS',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# drf_spectacular emits W001/W002 warnings for missing type hints on
# SerializerMethodField and enum collisions across the 26 apps. These are
# cosmetic and don't affect runtime — silence so `manage.py check --deploy`
# stays clean. Revisit by adding @extend_schema_field type hints incrementally.
SILENCED_SYSTEM_CHECKS = [
    'drf_spectacular.W001',
    'drf_spectacular.W002',
]

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# In production, set CORS_ALLOWED_ORIGINS explicitly. CORS_ALLOW_ALL_ORIGINS
# is only honored when explicitly set in the environment.
CORS_ALLOW_ALL_ORIGINS = env('CORS_ALLOW_ALL_ORIGINS')
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

# ---------------------------------------------------------------------------
# Variant annotation / external integrations
# ---------------------------------------------------------------------------
NCBI_API_KEY = env('NCBI_API_KEY')
NCBI_EMAIL = env('NCBI_EMAIL')
ANNOTATION_CACHE_TTL_DAYS = 30
FHIR_BASE_URL = env('FHIR_BASE_URL')

# ---------------------------------------------------------------------------
# Compliance feature flags
# ---------------------------------------------------------------------------
# Gate regulated-lab features (e-signature enforcement, enhanced PHI masking,
# stricter session timeouts, etc.). Off by default for research use; flip to
# True via env for clinical deployments that must meet 21 CFR Part 11 / HIPAA.
ENABLE_PART11 = env('ENABLE_PART11')
ENABLE_HIPAA_MODE = env('ENABLE_HIPAA_MODE')

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'trpm-lims.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django.security': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# ---------------------------------------------------------------------------
# Sentry (optional — only initialized if SENTRY_DSN is set)
# ---------------------------------------------------------------------------
SENTRY_DSN = env('SENTRY_DSN')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=env('SENTRY_ENVIRONMENT'),
        traces_sample_rate=env('SENTRY_TRACES_SAMPLE_RATE'),
        send_default_pii=False,
    )
