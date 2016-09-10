# -*- coding: utf-8 -*-
from __future__ import absolute_import
import celery


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def handle_entry_queue(queue_name):
    from fb_bot.bot.entry_handler import entry_handler
    entry_handler.handle_entry_queue(queue_name)


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def return_simple_search_results(user_id, listings):
    # send_simple_results(user_id=user_id, listings=listings)
    from fb_bot.bot.ctx import set_chat_context
    from fb_bot.bot.chat_session import ChatSession
    from fb_bot.bot.message import attachment_reply, reply
    from fb_bot.bot.utils import get_results_attachment
    from fb_bot.bot.handlers import log

    with ChatSession(user_id) as session, set_chat_context(session):
        sr = session.search_request
        sr.is_waiting_for_results = False
        if listings:
            attachment = get_results_attachment(listings)
            attachment_reply(user_id, attachment)
            log.debug('Return results for %s' % sr)
            q = sr.next_question()
            reply(user_id, q.question)
        else:
            log.debug('No results for %s' % sr)
            # TODO: handle it
            reply(user_id, "Sorry, we can't find any listing with this criteria.")
