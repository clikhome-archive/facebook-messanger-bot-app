# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings  # noqa

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clikhome_fbbot.settings')
# os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')


import configurations
configurations.setup()

app = Celery('clikhome_fbbot')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
assert app.conf.BROKER_URL
assert app.conf.CELERY_RESULT_BACKEND

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
