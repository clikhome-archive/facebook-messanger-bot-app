# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging


log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class Message(object):

    def __init__(self, wh_msg):
        self.wh_msg = wh_msg

    @property
    def text(self):
        if self.wh_msg.is_message:
            return self.wh_msg._message['text']
        elif self.wh_msg.is_postback:
            return self.wh_msg._postback['payload']

    @property
    def sender_id(self):
        return self.wh_msg.sender.recipient_id

    def __unicode__(self):
        return '%r from %s' % (self.text, self.sender_id)

