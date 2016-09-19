# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import requests

from django.conf import settings
from messengerbot import MessengerClient as BaseMessengerClient, messages, MessengerError

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class MessengerClient(BaseMessengerClient):

    def send_typing_on(self, recipient_id):
        # Turn typing indicators on
        return self._sender_action(recipient_id, 'typing_on')

    def send_typing_off(self, recipient_id):
        # Turn typing indicators off
        return self._sender_action(recipient_id, 'typing_off')

    def mark_seen(self, recipient_id):
        # Mark last message as read
        return self._sender_action(recipient_id, 'mark_seen')

    def _sender_action(self, recipient_id, action):
        # https://developers.facebook.com/docs/messenger-platform/send-api-reference/sender-actions
        data = {
            "recipient": {
                "id": recipient_id
            },
            "sender_action": action
        }
        response = requests.post(
            '%s/messages' % self.GRAPH_API_URL,
            params={'access_token': self.access_token},
            json=data
        )
        if response.status_code != 200:
            MessengerError(
                **response.json()['error']
            ).raise_exception()
        return response.json()

messenger = MessengerClient(access_token=settings.FBBOT_PAGE_ACCESS_TOKEN)


def send_attachment_reply(recipient, attachment):
    if not isinstance(recipient, messages.Recipient):
        recipient = messages.Recipient(recipient_id=recipient)
    message = messages.Message(attachment=attachment)
    request = messages.MessageRequest(recipient, message)
    return messenger.send(request)


def send_message(recipient, text):
    if not isinstance(recipient, messages.Recipient):
        recipient = messages.Recipient(recipient_id=recipient)
    message = messages.Message(text=text)
    request = messages.MessageRequest(recipient, message)
    return messenger.send(request)
