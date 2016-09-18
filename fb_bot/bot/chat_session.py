# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import threading

from django.conf import settings
from django.core.cache import caches
from facebook import GraphAPI
from fb_bot.bot import messenger_client
from fb_bot.bot.fb_search_request import FbSearchRequest

log = logging.getLogger('clikhome_fbbot.%s' % __name__)
CACHE_PREFIX = 'fb_bot-v2'


class ChatSession(object):
    graph_api_class = GraphAPI
    local = threading.local()

    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.lock_key = CACHE_PREFIX + '-lock-chat-with-%s' % user_id
        self.cache_key = CACHE_PREFIX + '-chat-session-%s' % user_id
        self.cache = caches['default']
        self.cache_timeout = settings.CHAT_SESSION_TIMEOUT
        self.graph = GraphAPI(settings.FBBOT_PAGE_ACCESS_TOKEN)
        self.data = dict()
        self._session_usage = 0

        if not hasattr(self.local, 'sessions'):
            self.local.sessions = dict()

    def save(self):
        self.cache.set(self.cache_key, self.data, self.cache_timeout)
        self.cache.close()

    def load(self):
        self.data = self.cache.get(self.cache_key, dict())
        if not self.data:
            log.info('Start new chat session for u=%s' % self.user_id)

        if not self.data.get('user_profile', None):
            self.data['user_profile'] = self.graph.get(str(self.user_id))

    @property
    def search_request(self):
        """
        :rtype: ``FbSearchRequest``
        """
        if not self.data.get('search_request', None):
            log.info('Create new search_request for u=%s' % self.user_id)
            self.data['search_request'] = FbSearchRequest(self.user_id)
        return self.data['search_request']

    @property
    def user_first_name(self):
        if 'first_name' in self.data['user_profile']:
            return self.data['user_profile']['first_name']
        else:
            return self.data['user_profile']['name'].split(' ', 1)[0]

    def reply(self, text):
        return messenger_client.send_message(self.user_id, text)

    def attachment_reply(self, attachment):
        return messenger_client.send_attachment_reply(self.user_id, attachment)

    def __enter__(self):
        # Check session in local thread first
        local_session = self.local.sessions.get(self.user_id, None)

        if local_session:
            local_session._session_usage += 1
            return local_session
        else:
            self.load()
            self.local.sessions[self.user_id] = self
            self._session_usage += 1
            return self

    def __exit__(self, exc_type, exc_value, traceback):
        session = self.local.sessions.get(self.user_id, self)
        session._session_usage -= 1

        if session._session_usage <= 0:
            session.local.sessions.pop(self.user_id, None)
            session.save()
