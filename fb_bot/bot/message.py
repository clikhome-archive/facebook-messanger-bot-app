# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging


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

    @property
    def text(self):
        return self.wh_msg._message['text']

    @property
    def sender_id(self):
        return self.wh_msg.sender.recipient_id

    def __unicode__(self):
        return '%r from %s' % (self.text, self.sender_id)

