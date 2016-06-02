# -*- coding: utf-8 -*-
import os

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
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            # 'tags': {'custom-tag': 'x'},
        },
    },
    'loggers': {
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
        'clikhome_fbbot.fb_bot': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'redis': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'redis_lock': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django_redis': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'clikhome_fbbot': {
            'handlers': ['sentry'],
            'level': 'WARNING',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
    }
}
