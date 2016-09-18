# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from django.conf import settings
from messengerbot import MessengerClient, messages

messenger = MessengerClient(access_token=settings.FBBOT_PAGE_ACCESS_TOKEN)

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


def send_attachment_reply(recipient, attachment):
    if not isinstance(recipient, messages.Recipient):
        recipient = messages.Recipient(recipient_id=recipient)
    message = messages.Message(attachment=attachment)
    request = messages.MessageRequest(recipient, message)
    messenger.send(request)


def send_message(recipient, text):
    if not isinstance(recipient, messages.Recipient):
        recipient = messages.Recipient(recipient_id=recipient)
    message = messages.Message(text=text)
    request = messages.MessageRequest(recipient, message)
    return messenger.send(request)
