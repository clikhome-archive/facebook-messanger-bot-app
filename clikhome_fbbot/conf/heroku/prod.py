# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from clikhome_fbbot.conf.base_settings import *

DEBUG = False

BROKER_URL = os.getenv('REDISCLOUD_URL', None)
CELERY_RESULT_BACKEND = os.getenv('REDISCLOUD_URL', None)

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = (
    '.herokuapp.com',
)
