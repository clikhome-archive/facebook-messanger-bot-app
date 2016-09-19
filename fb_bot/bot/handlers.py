# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import re

from fb_bot.bot.decorators import respond_to
from fb_bot.bot.ctx import session, search_request as sr

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


@respond_to('^reset|again|restart|hey|hello|hi|mary$', re.IGNORECASE)
def restart(message):
    sr.reset()
    sr.next_question().activate()


def default_handler(message):
    session.send_mark_seen()
    session.send_typing_on()

    if sr.current_question is None:
        sr.next_question().activate()
    elif sr.current_question.wait_for_answer:
        sr.current_question.set_answer(message.text)

    if sr.current_question is None:
        session.send_typing_off()
        return
    elif not sr.current_question.wait_for_answer:
        sr.next_question().activate()
    session.send_typing_off()


@respond_to('^!hey$', re.IGNORECASE)
def hey(message):
    # eggplant
    session.reply('\U0001F346')


@respond_to('^!secret500$', re.IGNORECASE)
def secret500(message):
    session.reply('%s' % (1/0))

