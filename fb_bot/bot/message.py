# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from django.conf import settings
from messengerbot import MessengerClient, messages

messenger = MessengerClient(access_token=settings.FBBOT_PAGE_ACCESS_TOKEN)

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


def attachment_reply(recipient, attachment):
    if not isinstance(recipient, messages.Recipient):
        recipient = messages.Recipient(recipient_id=recipient)
    message = messages.Message(attachment=attachment)
    request = messages.MessageRequest(recipient, message)
    messenger.send(request)


def reply(recipient, text):
    if not isinstance(recipient, messages.Recipient):
        recipient = messages.Recipient(recipient_id=recipient)
    message = messages.Message(text=text)
    request = messages.MessageRequest(recipient, message)
    return messenger.send(request)


class Message(object):

    def __init__(self, wh_msg, session):
        """
        {
          "id": "476499879206175",
          "time": 1463740457098,
          "messaging": [
            {
              "sender": {
                "id": "1595878670725308"
              },
              "recipient": {
                "id": "476499879206175"
              },
              "timestamp": 1463740457080,
              "message": {
                "mid": "mid.1463740457074:9a0c2e0040ca78f389",
                "seq": 17,
                "text": "hey"
              }
            }
          ]
        }
        """
        self.wh_msg = wh_msg
        self.session = session

    def reply(self, text):
        reply(self.wh_msg.recipient, text)

    @property
    def text(self):
        return self.wh_msg._message['text']

    @property
    def sender_id(self):
        return self.wh_msg.sender.recipient_id

    def __unicode__(self):
        return '%r from %s' % (self.text, self.sender_id)
    # @property
    # def session(self):
    #     if not self._session:
    #         self._session = ChatSession(self.sender_id)
    #     return self._session
