# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
if not os.environ.get('DJANGO_SETTINGS_MODULE', False):
    print 'WARN: DJANGO_SETTINGS_MODULE env is not set'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'local_settings')

from django.conf import settings  # noqa

app = Celery('clikhome_fbbot')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
assert app.conf.BROKER_URL
assert app.conf.CELERY_RESULT_BACKEND

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
