from .base import *  # noqa

DEBUG = True

HOST = "http://localhost:8000"

SECRET_KEY = "secret"

DATABASES = {
    # "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": base_dir_join("db.sqlite3"),}
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'theraq',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

STATIC_ROOT = base_dir_join("staticfiles")
STATIC_URL = "/static/"

MEDIA_ROOT = base_dir_join("mediafiles")
MEDIA_URL = "/media/"

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

AUTH_PASSWORD_VALIDATORS = []  # allow easy passwords only on local

# Celery
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email
INSTALLED_APPS += ("naomi", "drf_generators")
EMAIL_BACKEND = "naomi.mail.backends.naomi.NaomiBackend"
EMAIL_FILE_PATH = base_dir_join("tmp_email")

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "%(levelname)-8s [%(asctime)s] %(name)s: %(message)s"}, },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "standard", },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO"},
        "celery": {"handlers": ["console"], "level": "INFO"},
    },
}

JS_REVERSE_JS_MINIFY = False

CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "https://theraq.com",
    "http://127.0.0.1:8000"
]

CORS_ORIGIN_REGEX_WHITELIST = [
    r"^https://\w+\.theraq\.com",
]

LOGIN_REDIRECT_URL="http://localhost:8000"
