# -*- coding: utf-8 -*-
from __future__ import absolute_import
import celery


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def handle_entry_queue(queue_name):
    from fb_bot.bot.entry_handler import entry_handler
    entry_handler.handle_entry_queue(queue_name)


@celery.task(ignore_result=True, max_retries=0, queue='fb-bot', expires=30)
def return_simple_search_results(user_id, listings):
    from fb_bot.bot.ctx import set_chat_context
    from fb_bot.bot.chat_session import ChatSession
    from fb_bot.bot import templates
    from fb_bot.bot.handlers import log

    with ChatSession(user_id) as session, set_chat_context(session):
        sr = session.search_request
        sr.is_waiting_for_results = False
        if listings:
            attachment = templates.get_results_attachment(listings)
            session.attachment_reply(attachment)
            log.debug('Return results for %s' % sr)
            sr.next_question().activate()
        else:
            log.debug('No results for %s' % sr)
            session.reply("Sorry, we can't find any listing with this criteria.")
            sr.next_question().activate(is_bad_request=True)
