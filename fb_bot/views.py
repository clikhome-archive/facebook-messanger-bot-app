# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.views import generic
from messengerbot import webhooks

from fb_bot.bot.entry_handler import EntryHandler

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


# def webhook_messaging__repr__(self):
#     flags = list()
#     for prop_name in ['is_message', 'is_delivery', 'is_postback']:
#         if getattr(self, prop_name):
#             flags.append(prop_name)
#     return '<WebhookMessaging %s>' % ','.join(flags)
#
# webhooks.WebhookMessaging.__repr__ = webhook_messaging__repr__


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
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ Post function to handle Facebook messages"""
        log.debug('Payload %r' % request.body)
        payload = json.loads(request.body)

        wh = webhooks.Webhook(payload)
        message_entries = dict()

        for entry in wh.entries:
            for entry in entry.messaging:
                if entry.is_message and 'text' in entry._message:
                    message_entries.setdefault(entry.sender.recipient_id, list())
                    message_entries[entry.sender.recipient_id].append(entry)
        EntryHandler.add_to_queue(message_entries, async=self.handle_messages_async)
        return HttpResponse()
