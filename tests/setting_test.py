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

    FBBOT_APP_ID = '1720907708191793'
    FBBOT_APP_SECRET = '4d778c37bfb304ffa0c2b5de1eab37a9'

    FBBOT_PAGE_ACCESS_TOKEN = 'EAAYdKAyjVDEBAI9M9BZCX94naZBCeVb7dmxCQGXPT6lSJUI52KOdmeu9Yzp4jZBG6o19RkcwVRPX9W2lW8nJ2g6gqtklBn80FfxwQrVVV966GpsdhFzwM3ZBCBdJknob9dmjr1qtmj2svMWiAAYn4TOZBOZAX61rMBcJIn72maHAZDZD'

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
