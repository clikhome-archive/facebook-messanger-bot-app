# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import os
import logging
from threading import Lock

import redis
from django.conf import settings
from hotqueue import HotQueue
from raven.contrib.django.raven_compat.models import client as raven_client
import aiml

from fb_bot.bot.chat_lock import ChatLock
from fb_bot.bot.chat_session import ChatSession
from fb_bot.bot.globals import redis_connection_pool
from fb_bot.bot.ctx import set_chat_context, search_request
from fb_bot.bot.manager import Manager
from fb_bot.bot.message import Message
from fb_bot.bot.signals import handler_before_call
from fb_bot.models import ChatLog
from fb_bot.tasks import handle_entry_queue

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class EntryHandler(object):
    admin_ids = map(int, settings.FBBOT_ADMINS_IDS)

    def __init__(self):
        from fb_bot.bot import handlers
        self.default_handler = handlers.default_handler
        self.current_session = None
        self.sync_lock = Lock()
        self.aiml = aiml.Kernel()
        aiml_file = os.path.join(os.path.dirname(__file__), 'faq.xml')
        self.aiml.learn(aiml_file)

    def aiml_respond(self, input):
        return self.aiml.respond(input)

    def _handle_message(self, msg, session):
        """
        :type msg: WebhookMessaging
        """

        text_log = None

        if msg.is_message:
            text_log = text = msg._message['text']
        elif msg.is_postback:
            text = msg._postback['payload']
            text_log = 'POST_BACK: %r' % text
        else:
            raise Exception('Unexpected message %r' % msg)

        now = datetime.datetime.utcnow()
        delta = (now - msg.timestamp)
        if delta.seconds >= settings.FBBOT_MSG_EXPIRE:
            log_message = 'Drop expired message, delta={delta}, limit={limit}'.format(delta=delta.seconds,
                                                                                      limit=settings.FBBOT_MSG_EXPIRE)
            ChatLog.objects.create(
                recipient=msg.sender.recipient_id,
                type='in',
                errors=log_message,
                text=text_log
            )
            log.warn(log_message)
            return

        ChatLog.objects.create(
            recipient=msg.sender.recipient_id,
            type='in',
            text=text_log
        )
        msg_obj = Message(msg)
        respond = self.aiml_respond(text)
        if respond:
            session.reply(respond.strip().replace('  ', ' '))
            if search_request.current_question and search_request.current_question.wait_for_answer:
                search_request.current_question.activate()
            return

        for cb, _ in self._get_receivers(msg_obj.text):
            cb = cb or self.default_handler
            try:
                sr = session.search_request
                # if sr.is_waiting_for_results and not msg_obj.text.startswith(('@', '!')):
                #     log.warn('Drop message %r when is_waiting_for_results=True' % msg_obj)
                #     continue
                log.debug('Call %s:%s with text %r' % (cb.__name__, sr.current_question.__class__.__name__, text))
                handler_before_call.send(self, handler_cb=cb, message=msg_obj, text=text)
                cb(msg_obj)
            except Exception, e:
                raven_client.captureException()
                log.exception(dict(cb=cb, text=text, user_id=msg_obj.sender_id))

    def _get_receivers(self, text):
        has_matching = False
        for matcher in Manager.commands:
            if not matcher:
                continue
            m = matcher.search(text)
            if m:
                has_matching = True
                yield Manager.commands[matcher], text
                # TODO: handle groups yield commands[matcher], to_utf8(m.groups())
        if not has_matching:
            yield None, text

    def handle_entry_queue(self, queue_name):
        handled_count = 0
        chat_lock = ChatLock(redis.Redis(connection_pool=redis_connection_pool), queue_name)
        if chat_lock.is_locked:
            return False
        sender_id = queue_name.split('-')[-1]

        with chat_lock as _:
            # TODO: use Kombu exclusive queue?
            # http://docs.celeryproject.org/projects/kombu/en/latest/reference/kombu.html#kombu.Queue.exclusive
            q = HotQueue(queue_name, connection_pool=redis_connection_pool)
            with ChatSession(sender_id) as session, set_chat_context(session):
                for entry in q.consume(timeout=1):
                    log.debug('!!!!Get from %d HotQueue %r' % (handled_count, entry.__dict__))
                    self._handle_message(entry, session)
                    handled_count += 1
        return handled_count

    def handle_entry_sync(self, entry, sender_id):
        with self.sync_lock as lock, ChatSession(sender_id) as session, set_chat_context(session):
            self._handle_message(entry, session)

    @classmethod
    def add_to_queue(cls, entry, async=True):
        sender_id = entry.sender.recipient_id
        if async:
            queue = HotQueue('fb-bot-chat-%s' % sender_id, connection_pool=redis_connection_pool)
            queue.put(entry)
            handle_entry_queue.delay(queue.name)
        else:
            entry_handler.handle_entry_sync(entry, sender_id)

entry_handler = EntryHandler()
