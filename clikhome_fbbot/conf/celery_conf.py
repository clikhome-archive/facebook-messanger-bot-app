# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os


BROKER_URL = os.getenv('CELERY_BROKER_URL', None)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND_URL', None)
assert BROKER_URL
assert CELERY_RESULT_BACKEND

CELERY_TASK_RESULT_EXPIRES = 600
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_SEND_EVENTS = True

CELERYD_LOG_FORMAT = """
    [%(asctime)s: %(levelname)s/%(processName)s/%(threadName)s] %(message)s
""".strip()

if os.environ.get('DYNO', False):
    # Don't print %(asctime)s on Heroku environ
    CELERYD_LOG_FORMAT = """
        [%(levelname)s/%(processName)s/%(threadName)s] %(message)s
    """.strip()
