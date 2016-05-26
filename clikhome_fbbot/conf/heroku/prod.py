# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

os.environ['REDIS_URL'] = os.getenv('REDISCLOUD_URL', None)
os.environ['BROKER_URL'] = os.environ['REDIS_URL']
os.environ['CELERY_RESULT_BACKEND'] = os.environ['REDIS_URL']

from clikhome_fbbot.conf.base_settings import *

DEBUG = False

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = (
    '.herokuapp.com',
)
