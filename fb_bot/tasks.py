# -*- coding: utf-8 -*-
from __future__ import absolute_import

import celery


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def handle_entry_queue(queue_name):
    from fb_bot.bot.entry_handler import entry_handler
    entry_handler.handle_entry_queue(queue_name)
