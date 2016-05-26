# -*- coding: utf-8 -*-
from __future__ import absolute_import
from clikhome_fbbot.celery import app
from clikhome_fbbot.utils.bbox import Bbox

__doc__ = "Run tasks on the main website"

TASK_OPTIONS = dict(max_retries=0, queue='default')


def get_engine_questions_list(**kwargs):
    return app.send_task(
        'bridge.fbbot_tasks.get_engine_questions_list',
        kwargs=kwargs, **TASK_OPTIONS).get()


def listings_search(**kwargs):
    return app.send_task(
        'bridge.fbbot_tasks.fbbot_listings_search',
        kwargs=kwargs, **TASK_OPTIONS).get()


def geocode_location_to_bbox(*args):
    result = app.send_task(
        'bridge.fbbot_tasks.geocode_location_to_bbox',
        args=args, **TASK_OPTIONS).get()

    if result:
        return Bbox(**result)
