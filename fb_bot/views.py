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


class WebHookView(generic.View):
    handle_messages_async = not getattr(settings, 'CELERY_ALWAYS_EAGER', False)
    redis_ttl = 86400

    def get(self, request, *args, **kwargs):
        if self.request.GET.get('hub.verify_token', None) and \
                self.request.GET['hub.verify_token'] == settings.FBBOT_VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        log.debug('Payload %r' % request.body)
        self.redis_conn = redis.Redis(connection_pool=redis_connection_pool)
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        payload = json.loads(request.body)
        wh = webhooks.Webhook(payload)

        for entries in wh.entries:
            for entry in entries.messaging:
                if entry.is_message and entry._message.get('is_echo', False):
                    log.debug('DROP ECHO: %r' % json.dumps(entry._message))
                elif entry.is_message and 'text' in entry._message:
                    self.message_hook(entry)
                elif entry.is_postback:
                    self.postback_hook(entry)
                else:
                    log.warn('Dropped unexpected entry %r' % entry)

        return HttpResponse()

    def postback_hook(self, entry):
        log.debug('POST_BACK: %r' % json.dumps(entry._postback))
        EntryHandler.add_to_queue(entry, async=self.handle_messages_async)

    def message_hook(self, entry):
        mid = entry._message.get('mid', None)
        if mid and self.redis_conn.get('mids-seen:%s' % mid):
            log.debug('Ignore by mid %r' % json.dumps(entry._message))
        else:
            EntryHandler.add_to_queue(entry, async=self.handle_messages_async)
            if mid:
                self.redis_conn.set('mids-seen:%s' % mid, self.redis_ttl)
