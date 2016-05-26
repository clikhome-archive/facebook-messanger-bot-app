# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from django.conf import settings
from messengerbot import MessengerClient, messages

messenger = MessengerClient(access_token=settings.FBBOT_PAGE_ACCESS_TOKEN)

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


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
        # recipient = messages.Recipient(recipient_id=self.sender_id)
        message = messages.Message(text=text)
        request = messages.MessageRequest(self.wh_msg.recipient, message)
        messenger.send(request)

    def attachment_reply(self, attachment):
        message = messages.Message(attachment=attachment)
        request = messages.MessageRequest(self.wh_msg.recipient, message)
        messenger.send(request)

    @property
    def text(self):
        return self.wh_msg._message['text']

    @property
    def sender_id(self):
        return self.wh_msg.sender.recipient_id

    # @property
    # def session(self):
    #     if not self._session:
    #         self._session = ChatSession(self.sender_id)
    #     return self._session
