# -*- coding: utf-8 -*-
from __future__ import absolute_import
from configurations import values
from .common import Common, EnvVal


class Prod(Common):
    DEBUG = False

    BROKER_URL = EnvVal('CLOUDAMQP_URL')
    CELERY_RESULT_BACKEND = EnvVal('REDISCLOUD_URL')
    REDIS_URL = EnvVal('REDISCLOUD_URL')

    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True

    ALLOWED_HOSTS = (
        '.herokuapp.com',
    )
