# -*- coding: utf-8 -*-
from __future__ import absolute_import

import celery


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def handle_entry_queue(queue_name):
    from fb_bot.bot.entry_handler import entry_handler
    entry_handler.handle_entry_queue(queue_name)


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def return_search_results(user_id, more_url, listings):
    from fb_bot.bot.handlers import send_results
    send_results(user_id=user_id, more_url=more_url, listings=listings)


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def return_simple_search_results(user_id, listings):
    from fb_bot.bot.handlers import send_simple_results
    send_simple_results(user_id=user_id, listings=listings)
