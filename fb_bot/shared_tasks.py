# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import json
from clikhome_fbbot.celery import app

__doc__ = "Run tasks on the main website"

TASK_OPTIONS = dict(max_retries=0, queue='default')


def request_simple_listings_search(**kwargs):
    from django.conf import settings
    from fb_bot.tasks import return_simple_search_results

    task = app.send_task(
        'bridge.fbbot_tasks.fbbot_simple_listings_search',
        kwargs=kwargs, **TASK_OPTIONS)

    if getattr(settings, 'CELERY_ALWAYS_EAGER', False):
        with open(os.path.join(
            os.path.dirname(__file__),
            '..',
            'tests',
            'search_request_response.json'
        )) as fp:
            listings = json.load(fp)
        return_simple_search_results(user_id=kwargs['user_id'], listings=listings)

    return task



