# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import sys
import traceback

from django.conf import settings
from hotqueue import HotQueue
from redis.connection import ConnectionPool

from fb_bot.bot.chat_lock import ChatLock
from fb_bot.bot.chat_session import ChatSession
from fb_bot.bot.manager import Manager
from fb_bot.bot.message import Message
from fb_bot.tasks import handle_entry_queue

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class EntryHandler(object):

    def __init__(self):
        from fb_bot.bot import handlers
        self.default_handler = handlers.default_handler

    def _handle_message(self, wh_msg, session):
        assert wh_msg.is_message
        text = wh_msg._message['text']
        msg_obj = Message(wh_msg, session)
        for cb, _ in self._get_receivers(msg_obj.text):
            cb = cb or self.default_handler
            with msg_obj.session as session:
                try:
                    sr = session.search_request
                    cb(msg_obj, sr)
                except:
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)
                    log.error("Error processing %s" % text)

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
            redis_kwargs = dict(connection_pool=ConnectionPool.from_url(settings.REDIS_URL))

            # TODO: use Kombu exclusive queue?
            # http://docs.celeryproject.org/projects/kombu/en/latest/reference/kombu.html#kombu.Queue.exclusive
            q = HotQueue(queue_name, **redis_kwargs)
            with ChatSession(sender_id) as session:
                while True:
                    has_entry = False
                    for entry in q.consume(timeout=timeout):
                        has_entry = True
                        log.debug('!!!!Get from %d HotQueue %r - %s' % (handled_count, entry, entry._message['text']))
                        self._handle_message(entry, session)
                        handled_count += 1
                    if not has_entry:
                        break
        return handled_count

    def handle_entry_sync(self, entry, sender_id):
        with ChatSession(sender_id) as session:
            self._handle_message(entry, session)

    @staticmethod
    def add_to_queue(message_entries, async=True):
        if async:
            connection_pool = ConnectionPool.from_url(settings.REDIS_URL)
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
