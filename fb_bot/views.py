# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import json

import redis
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.views import generic
from messengerbot import webhooks

from fb_bot.bot.entry_handler import EntryHandler
from fb_bot.bot.globals import redis_connection_pool

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


def index(request):
    return HttpResponse('OK')


def secret500(request):
    1/0
    raise Exception('secret500')


class BotView(generic.View):
    handle_messages_async = not getattr(settings, 'CELERY_ALWAYS_EAGER', False)

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('hub.verify_token', None) and \
                self.request.GET['hub.verify_token'] == settings.FBBOT_VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.redis_conn = redis.Redis(connection_pool=redis_connection_pool)
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ Post function to handle Facebook messages"""
        log.debug('Payload %r' % request.body)
        payload = json.loads(request.body)

        wh = webhooks.Webhook(payload)
        message_entries = dict()
        redis_ttl = 86400

        for entry in wh.entries:
            for entry in entry.messaging:
                if entry.is_message and 'text' in entry._message:
                    mid = entry._message.get('mid', None)
                    if mid and self.redis_conn.get('mids-seen:%s' % mid):
                        log.debug('Ignore mid: %s' % entry._message['mid'])
                    else:
                        message_entries.setdefault(entry.sender.recipient_id, list())
                        message_entries[entry.sender.recipient_id].append(entry)
                        if mid:
                            self.redis_conn.set('mids-seen:%s' % mid, redis_ttl)

        if message_entries:
            EntryHandler.add_to_queue(message_entries, async=self.handle_messages_async)

        return HttpResponse()
