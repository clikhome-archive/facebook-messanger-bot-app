# -*- coding: utf-8 -*-
from __future__ import absolute_import
from clikhome_fbbot.celery import app

__doc__ = "Run tasks on the main website"

TASK_OPTIONS = dict(max_retries=0, queue='default')


def request_simple_listings_search(**kwargs):
    return app.send_task(
        'bridge.fbbot_tasks.fbbot_simple_listings_search',
        kwargs=kwargs, **TASK_OPTIONS)

