# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class Manager(object):
    commands = dict()

    @classmethod
    def register_handler(cls, func, matchstr, flags):
        log.debug('registered respond_to "%s" to "%s"', func.__name__, matchstr)
        cls.commands[re.compile(matchstr, flags)] = func
