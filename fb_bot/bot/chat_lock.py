# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import redis_lock

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class ChatLock(object):

    def __init__(self, redis_client, lock_id, expire=4):
        self.redis_client = redis_client
        self.lock_key = 'chatlock-%s' % lock_id
        self.expire = expire
        self._lock = None

    @property
    def is_locked(self):
        if self.redis_client.get('lock:'+self.lock_key):
            return True
        else:
            return False

    @property
    def lock(self):
        if not self._lock:
            self._lock = redis_lock.Lock(self.redis_client, self.lock_key, expire=3, auto_renewal=True)
        return self._lock

    def __enter__(self):
        lock = self.lock.acquire(blocking=True)
        if lock:
            return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.lock._held:
            self.lock.release()
        else:
            log.warn('Try to release unlocked lock')
