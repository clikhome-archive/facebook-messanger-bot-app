# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from django.conf import settings
from django.core.cache import caches
from facebook import GraphAPI
from fb_bot.bot.fb_search_request import FbSearchRequest

log = logging.getLogger('clikhome_fbbot.%s' % __name__)
CACHE_PREFIX = 'fb_bot-v2'


class ChatSession(object):
    graph_api_class = GraphAPI

    def __init__(self, user_id):
        self.user_id = user_id
        self.lock_key = CACHE_PREFIX + '-lock-chat-with-%s' % user_id
        self.cache_key = CACHE_PREFIX + '-chat-session-%s' % user_id
        self.cache = caches['default']
        self.cache_timeout = 3600
        self.graph = GraphAPI(settings.FBBOT_PAGE_ACCESS_TOKEN)
        self.data = dict()
        self._lock = None

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

    def __enter__(self):
        self.load()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()
