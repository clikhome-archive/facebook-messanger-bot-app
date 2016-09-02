# -*- coding: utf-8 -*-
from configurations.utils import uppercase_attributes
from configurations.values import setup_value, Value

from clikhome_fbbot.settings import Common


class Test(Common):
    DEBUG = True
    SECRET_KEY = 'test'

    BROKER_BACKEND = 'memory'
    CELERY_RESULT_BACKEND = 'memory'
    BROKER_URL = 'memory://localhost/'
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

    REDIS_URL = 'redis://none:6379/1'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    }

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    GOOGLE_GEOCODER_API_KEY = None

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
        },
        'loggers': {
            'root': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }
    FBBOT_VERIFY_TOKEN = 'dev-verify-token'
    FBBOT_PAGE_ACCESS_TOKEN = 'none'

    @classmethod
    def setup(cls):
        for name, value in uppercase_attributes(cls).items():
            if isinstance(value, Value):
                try:
                    setup_value(cls, name, value)
                except ValueError, e:
                    print 'WARNING: ', e

    # @classmethod
    # def pre_setup(cls):
    #     DOTENV = os.path.join(Common.BASE_DIR, '.env')
    #     if os.path.exists(DOTENV):
    #         cls.DOTENV = DOTENV
    #
    #     if cls.DOTENV_LOADED is None:
    #         cls.load_dotenv()
