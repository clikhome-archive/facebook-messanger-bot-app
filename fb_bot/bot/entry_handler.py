# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import os
import logging
from threading import Lock

from django.conf import settings
from hotqueue import HotQueue
from redis.connection import ConnectionPool
from raven.contrib.django.raven_compat.models import client as raven_client
import aiml

from fb_bot.bot.chat_lock import ChatLock
from fb_bot.bot.chat_session import ChatSession
from fb_bot.bot.ctx import set_chat_context
from fb_bot.bot.manager import Manager
from fb_bot.bot.message import Message
from fb_bot.bot.signals import handler_before_call
from fb_bot.models import ChatLog
from fb_bot.tasks import handle_entry_queue

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class EntryHandler(object):
    redis_url = settings.REDIS_URL
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
        assert msg.is_message
        text = msg._message['text']

        now = datetime.datetime.utcnow()
        delta = (now - msg.timestamp)
        if delta.seconds >= settings.FBBOT_MSG_EXPIRE:
            log_message = 'Drop expired message, delta=%s' % delta.seconds
            ChatLog.objects.create(
                recipient=msg.sender.recipient_id,
                type='in',
                errors=log_message,
                text=text
            )
            log.warn(log_message)
            return

        ChatLog.objects.create(
            recipient=msg.sender.recipient_id,
            type='in',
            text=text
        )
        msg_obj = Message(msg, session)
        with msg_obj.session as session:
            respond = self.aiml_respond(text)
            if respond:
                session.reply(respond.strip().replace('  ', ' '))
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
        chat_lock = ChatLock(queue_name)
        if chat_lock.is_locked:
            return False
        sender_id = queue_name.split('-')[-1]

        with chat_lock as _:
            timeout = 3
            redis_kwargs = dict(connection_pool=ConnectionPool.from_url(self.redis_url))

            # TODO: use Kombu exclusive queue?
            # http://docs.celeryproject.org/projects/kombu/en/latest/reference/kombu.html#kombu.Queue.exclusive
            q = HotQueue(queue_name, **redis_kwargs)
            with ChatSession(sender_id) as session, set_chat_context(session):
                while True:
                    has_entry = False
                    for entry in q.consume(timeout=timeout):
                        has_entry = True
                        log.debug('!!!!Get from %d HotQueue %r - %r' % (handled_count, entry, entry._message['text']))
                        self._handle_message(entry, session)
                        handled_count += 1
                    if not has_entry:
                        break
        return handled_count

    def handle_entry_sync(self, entry, sender_id):
        with self.sync_lock as lock, ChatSession(sender_id) as session, set_chat_context(session):
            self._handle_message(entry, session)

    @classmethod
    def add_to_queue(cls, message_entries, async=True):
        if async:
            connection_pool = ConnectionPool.from_url(cls.redis_url)
            redis_kwargs = dict(connection_pool=connection_pool)
            queues = dict()

            for sender_id, messages in message_entries.items():
                queues.setdefault(sender_id, None)
                queue_name = 'fb-bot-chat-%s' % sender_id
                if not queues[sender_id]:
                    queues[sender_id] = HotQueue(queue_name, **redis_kwargs)
                queues[sender_id].put(*messages)
                handle_entry_queue.delay(queue_name)
        else:
            for sender_id, messages in message_entries.items():
                for msg in messages:
                    entry_handler.handle_entry_sync(msg, sender_id)

entry_handler = EntryHandler()
