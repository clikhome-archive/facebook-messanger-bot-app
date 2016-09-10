# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging
import re

from fb_bot.bot.decorators import respond_to
from fb_bot.bot.questions import ImmediateReply
from fb_bot.bot import questions

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


def _set_answer(message, sr):
    text = message.text
    q = sr.current_question
    if not q:
        message.reply('Bad command "{}"'.format(text))
    elif isinstance(q, questions.Greeting):
        message.reply(sr.next_question().question)
    else:
        try:
            reply = sr.set_answer(text)
            if reply:
                message.reply(reply)
        except ImmediateReply, e:
            message.reply(e.message)
        else:
            ask_question(message, sr)


def ask_question(message, sr, question_text=None):
    q = sr.next_question()
    if isinstance(q, questions.SendApartmentSuggestion):
        sr.request_search_results()
    elif isinstance(q, questions.Greeting):
        message.reply(unicode(q.greeting))
    else:
        if question_text:
            message.reply(question_text)
        elif not q.skip_ask:
            message.reply(q.question)


@respond_to('^reset|again|restart$', re.IGNORECASE)
def restart(message, sr):
    sr.reset()
    ask_question(message, sr)


# @respond_to('^Hi|Hey|Hello|ClikHome|help$', re.IGNORECASE)
# def hi(message, sr):
#     sr.reset()
#     ask_question(message, sr)


def default_handler(message, sr):
    if sr.current_question is None:
        ask_question(message, sr)
    else:
        _set_answer(message, sr)


@respond_to('^!hey$', re.IGNORECASE)
def hey(message, sr):
    # eggplant
    message.reply('\U0001F346')


@respond_to('^!secret500$', re.IGNORECASE)
def secret500(message, sr):
    message.reply('%s' % (1/0))

