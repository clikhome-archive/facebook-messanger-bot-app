# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from fb_bot.bot.manager import Manager

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


def respond_to(matchstr, flags=0):
    def wrapper(func):
        Manager.register_handler(func, matchstr, flags)
        return func
    return wrapper
