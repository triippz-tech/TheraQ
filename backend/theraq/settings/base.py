# https://docs.djangoproject.com/en/1.10/ref/settings/
import datetime
import os

from decouple import config  # noqa
from . import blacklist_usernames

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_dir_join(*args):
    return os.path.join(BASE_DIR, *args)


SITE_ID = 1

SECURE_HSTS_PRELOAD = True

DEBUG = True

ADMINS = (("Admin", "mgtripoli@triippztech.com"),)

AUTH_USER_MODEL = "accounts.User"

ALLOWED_HOSTS = []

DJANGO_APPS = [
    "baton",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "dj_rest_auth.registration",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.twitter",
    "allauth.socialaccount.providers.linkedin",
    "drf_yasg",
    "django_js_reverse",
    "webpack_loader",
    "import_export",
    "django_filters",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "subq",
    "questions",
]

BATON_APP = ["baton.autodiscover"]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + BATON_APP

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "theraq.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [base_dir_join("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.sentry_dsn",
                "core.context_processors.commit_sha",
            ],
        },
    },
]

WSGI_APPLICATION = "theraq.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator", },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_DIRS = (base_dir_join("../frontend"),)

# Webpack
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": False,  # on DEBUG should be False
        "STATS_FILE": base_dir_join("../webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "IGNORE": [".+\.hot-update.js", ".+\.map"],
    }
}

# Celery
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACKS_LATE = True
CELERY_TIMEZONE = TIME_ZONE

# Sentry
SENTRY_DSN = config("SENTRY_DSN", default="")
COMMIT_SHA = config("HEROKU_SLUG_COMMIT", default="")

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'error',
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
        # 'core.renderers.TheraQJsonRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': (
        # If you use MultiPartFormParser or FormParser, we also have a camel case version
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
        # Any other parsers
    ),
}

REST_USE_JWT = True
JWT_AUTH_COOKIE = "theraq-authentication"

# Simple JWT
# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=1),
#     'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
#     'BLACKLIST_AFTER_ROTATION': True,
#     'UPDATE_LAST_LOGIN': False,
# }

# https://django-allauth.readthedocs.io/en/latest/configuration.html
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'name',
            'name_format',
            'picture',
            'short_name'
        ],
        'EXCHANGE_TOKEN': True,
        'LOCALE_FUNC': 'path.to.callable',
        'VERIFIED_EMAIL': False,
        'VERSION': 'v7.0',
    },
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'linkedin': {
        'SCOPE': [
            'r_basicprofile',
            'r_emailaddress'
        ],
        'PROFILE_FIELDS': [
            'id',
            'first-name',
            'last-name',
            'email-address',
            'picture-url',
            'public-profile-url',
        ]
    }

}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_AUTHENTICATION_METHOD = "username"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_VERIFICATION = True  # Users must verify email to log in
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
UNIQUE_EMAIL = True
ACCOUNT_USERNAME_BLACKLIST = blacklist_usernames.usernames
SOCIALACCOUNT_EMAIL_REQUIRED = True
REST_SESSION_LOGIN = True

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'accounts.serializers.CustomRegisterSerializer',
}

BATON = {
    'SITE_HEADER': 'TheraQ Admin',
    'SITE_TITLE': 'TheraQ Admin',
    'INDEX_TITLE': 'Site administration',
    'SUPPORT_HREF': 'https://github.com/triippz-tech/theraq/issues',
    'COPYRIGHT': 'copyright © 2020 <a href="https://www.theraq.com">TheraQ</a>',  # noqa
    'POWERED_BY': '<a href="https://www.triippztech.com">TriippzTech</a>',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'MENU_ALWAYS_COLLAPSED': False,
    'MENU_TITLE': 'TheraQ Admin',
    'GRAVATAR_DEFAULT_IMG': 'retro',
    'MENU': (
        {'type': 'title', 'label': 'main', 'apps': ('auth',)},
        {
            'type': 'app',
            'name': 'auth',
            'label': 'Authentication',
            'icon': 'fa fa-lock',
            'models': (
                {
                    'name': 'group',
                    'label': 'Groups'
                },
            )
        },
        {
            'type': 'app',
            'name': 'accounts',
            'label': 'User Details',
            'icon': 'fa fa-users',
            'models': (
                {
                    'name': 'user',
                    'label': 'Users'
                },
                {
                    'name': 'usersetting',
                    'label': 'User Settings'
                },
                {
                    'name': 'userprofile',
                    'label': 'User Profiles'
                },
                {
                    'name': 'usercertification',
                    'label': 'User Certifications'
                },
                {
                    'name': 'useremployer',
                    'label': 'User Employers'
                },
                {
                    'name': 'userlicense',
                    'label': 'User Licenses'
                },
                {
                    'name': 'userschool',
                    'label': 'User Schools'
                },
            )
        },
        {
            'type': 'app',
            'name': 'subq',
            'label': 'Subs',
            'icon': 'fa fa-book',
            'models': (
                {
                    'name': 'subq',
                    'label': 'SubQ'
                },
                {
                    'name': 'subqfollower',
                    'label': 'SubQ Followers'
                },
            )
        },
        {
            'type': 'app',
            'name': 'questions',
            'label': 'Questions',
            'icon': 'fa fa-question',
            'models': (
                {
                    'name': 'question',
                    'label': 'Questions'
                },
                {
                    'name': 'questionwatchers',
                    'label': 'Question Watchers'
                },
                {
                    'name': 'questionviews',
                    'label': 'Question Views'
                },
                {
                    'name': 'qtag',
                    'label': 'Question Tags'
                },
                {
                    'name': 'questionqtag',
                    'label': 'Question QTags'
                },
                {
                    'name': 'reply',
                    'label': 'Question Reply'
                },
                {
                    'name': 'comment',
                    'label': 'Comments'
                },
                {
                    'name': 'commentvote',
                    'label': 'Comment Votes'
                },
                {
                    'name': 'questionvote',
                    'label': 'Question Votes'
                },
                {
                    'name': 'replyvote',
                    'label': 'Reply Votes'
                },
            )
        },
        {'type': 'title', 'label': 'Contents', 'apps': ('flatpages',)},
        {'type': 'model', 'label': 'Pages', 'name': 'flatpage', 'app': 'flatpages'},
    ),
}
