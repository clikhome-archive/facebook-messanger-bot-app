# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import logging

from django.conf import settings
from hotqueue import HotQueue
from redis.connection import ConnectionPool
from raven.contrib.django.raven_compat.models import client as raven_client

from fb_bot.bot.chat_lock import ChatLock
from fb_bot.bot.chat_session import ChatSession
from fb_bot.bot.manager import Manager
from fb_bot.bot.message import Message
from fb_bot.tasks import handle_entry_queue

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class EntryHandler(object):
    redis_url = settings.REDIS_URL
    admin_ids = map(int, settings.FBBOT_ADMINS_IDS)

    def __init__(self):
        from fb_bot.bot import handlers
        self.default_handler = handlers.default_handler

    def _handle_message(self, msg, session):
        """
        :type msg: WebhookMessaging
        """
        assert msg.is_message

        now = datetime.datetime.utcnow()
        delta = (now - msg.timestamp)
        if delta.seconds >= settings.FBBOT_MSG_EXPIRE:
            log.warn('Drop expired message, delta=%s' % delta.seconds)
            return

        text = msg._message['text']
        msg_obj = Message(msg, session)
        for cb, _ in self._get_receivers(msg_obj.text):
            if cb:
                if msg_obj.text.startswith('@') and int(msg_obj.sender_id) not in self.admin_ids:
                    log.warn('Deny access to admin command %r for %r' % (msg_obj.text, msg_obj.sender_id))
                    msg_obj.reply('Access denied for %r' % cb.__name__)
                    continue
            else:
                cb = self.default_handler

            with msg_obj.session as session:
                try:
                    sr = session.search_request
                    if sr.is_waiting_for_results and not msg_obj.text.startswith(('@', '!')):
                        log.warn('Drop message %r when is_waiting_for_results=True' % msg_obj)
                        continue
                    cb(msg_obj, sr)
                except Exception, e:
                    raven_client.captureException()
                    log.exception(e, dict(cb=cb, text=text, user_id=msg_obj.sender_id))

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
            with ChatSession(sender_id) as session:
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
        with ChatSession(sender_id) as session:
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
