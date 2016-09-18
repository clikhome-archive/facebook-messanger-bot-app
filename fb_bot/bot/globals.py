# -*- coding: utf-8 -*-
from __future__ import absolute_import
from redis import ConnectionPool
from django.utils.functional import SimpleLazyObject

_redis_connection_pool = None


def get_redis_connection_pool():
    global _redis_connection_pool
    if _redis_connection_pool is None:
        from django.conf import settings
        _redis_connection_pool = ConnectionPool.from_url(settings.REDIS_URL)
    return _redis_connection_pool

redis_connection_pool = SimpleLazyObject(get_redis_connection_pool)
