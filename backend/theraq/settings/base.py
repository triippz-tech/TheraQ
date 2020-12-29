# https://docs.djangoproject.com/en/1.10/ref/settings/
import datetime
import os

from decouple import config  # noqa

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
    "accounts",
    "baton",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    # "rest_framework_simplejwt.token_blacklist",
    "social_django",
    "drf_yasg",
    "django_js_reverse",
    "webpack_loader",
    "import_export",
    "django_filters",
]

LOCAL_APPS = [
    "social_auth",
    "core",
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
    }
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
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

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        "rest_framework.authentication.SessionAuthentication",
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
}

SOCIAL_AUTH_POSTGRES_JSONFIELD = True

AUTHENTICATION_BACKENDS = (
    "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.google.GoogleOAuth2",
    "social_core.backends.facebook.FacebookOAuth2",
    "django.contrib.auth.backends.ModelBackend",
)

# this is needed to get a user's email from Facebook. See:
# https://stackoverflow.com/questions/32024327/facebook-doesnt-return-email-python-social-auth
# https://stackoverflow.com/a/32129851/6084948
# https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    "fields": "id,name,email",
}

# Social Auth Keys
SOCIAL_AUTH_TWITTER_KEY = config("SOCIAL_AUTH_TWITTER_KEY")
SOCIAL_AUTH_TWITTER_SECRET = config("SOCIAL_AUTH_TWITTER_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = config("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = config("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")
SOCIAL_AUTH_FACEBOOK_KEY = config("SOCIAL_AUTH_FACEBOOK_KEY")
SOCIAL_AUTH_FACEBOOK_SECRET = config("SOCIAL_AUTH_FACEBOOK_SECRET")

SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    # 'social_core.pipeline.user.get_username',
    "social_core.pipeline.social_auth.associate_by_email",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

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
