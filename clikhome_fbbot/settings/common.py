# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from configurations import Configuration, values

EnvVal = lambda environ_name: values.Value(
    environ_name=environ_name,
    environ_required=True,
    environ_prefix=None,
    late_binding=True
)


class DjangoCommon(Configuration):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()
    # SECRET_KEY = values.SecretValue(environ_name='DJANGO_SECRET_KEY')

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = ['*']

    # Application definition
    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'raven.contrib.django.raven_compat',
        'django_extensions',
        'djcelery',
        # 'kombu.transport.django',

        'fb_bot',
    )

    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
    )

    ROOT_URLCONF = 'clikhome_fbbot.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
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

    WSGI_APPLICATION = 'clikhome_fbbot.wsgi.application'


    # Database
    # https://docs.djangoproject.com/en/1.8/ref/settings/#databases
    DATABASES = values.DatabaseURLValue(environ_required=True)
    REDIS_URL = EnvVal('REDIS_URL')

    @property
    def CACHES(self):
        return {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': self.REDIS_URL,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                }
            }
        }

    # Internationalization
    # https://docs.djangoproject.com/en/1.8/topics/i18n/
    LANGUAGE_CODE = 'en-us'
    TIME_ZONE = 'UTC'
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.8/howto/static-files/
    STATIC_URL = '/static/'

    @property
    def RAVEN_CONFIG(self):
        if os.environ.get('SENTRY_DSN', None):
            return {
                'dsn': os.environ.get('SENTRY_DSN'),
                'tags': {'app': 'fb-bot-app'},
                # If you are using git, you can also automatically configure the
                # release based on the git info.
                # 'release': raven.fetch_git_sha(root()),
            }
        else:
            return {}

    @property
    def LOGGING(self):
        from .logging_conf import LOGGING
        return LOGGING

    # @classmethod
    # def pre_setup(cls):
    #     print 'pre_setup'
    #
    # @classmethod
    # def post_setup(cls):
    #     print 'post_setup'


class CeleryCommon(Configuration):
    BROKER_URL = EnvVal('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = EnvVal('CELERY_RESULT_BACKEND_URL')

    CELERY_TASK_RESULT_EXPIRES = 600
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_SEND_EVENTS = True
    CELERYD_CONCURRENCY = os.environ.get('CELERYD_CONCURRENCY', 10)
    CELERYD_LOG_FORMAT = """
        [%(asctime)s: %(levelname)s/%(processName)s/%(threadName)s] %(message)s
    """.strip()

    if os.environ.get('DYNO', False):
        # Don't print %(asctime)s on Heroku environ
        CELERYD_LOG_FORMAT = """
            [%(levelname)s/%(processName)s/%(threadName)s] %(message)s
        """.strip()


class AppsCommon(Configuration):
    # Facebook Messenger bot
    FBBOT_PAGE_ACCESS_TOKEN = EnvVal('FBBOT_PAGE_ACCESS_TOKEN')
    FBBOT_VERIFY_TOKEN = EnvVal('FBBOT_VERIFY_TOKEN')
    FBBOT_ADMINS_IDS = values.Value(
        environ_name='FBBOT_ADMINS_IDS',
        environ_required=False,
        environ_prefix=None,
        late_binding=True,
        default=['1595878670725308']
    )
    FBBOT_MSG_EXPIRE = 10
    GOOGLE_GEOCODER_API_KEY = EnvVal('GOOGLE_GEOCODER_API_KEY')
    CHAT_SESSION_TIMEOUT = os.getenv('CHAT_SESSION_TIMEOUT', 3600)


class Common(DjangoCommon, CeleryCommon, AppsCommon):
    pass
