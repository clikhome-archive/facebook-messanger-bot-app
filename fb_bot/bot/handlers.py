# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re

from django.conf import settings

from fb_bot.bot.decorators import respond_to
from fb_bot.bot.questions import ImmediateReply
from fb_bot.bot.utils import get_results_attachment

log = logging.getLogger('clikhome_fbbot.%s' % __name__)

THE_GREETING = 'Hello, I am your real-estate advisor. Where do you want to move?'


def _set_answer(message, sr):
    text = message.text
    if sr.current_question:
        try:
            reply = sr.set_answer(text)
            if reply:
                message.reply(reply)
        except ImmediateReply, e:
            message.reply(e.message)
        else:
            ask_question(message, sr)
    else:
        message.reply('Bad command "{}"'.format(text))


def send_results(message, sr):
    more_url, listings = sr.get_search_result()
    if listings:
        attachment = get_results_attachment(listings, more_url)
        message.attachment_reply(attachment)
        log.debug('Return results for %s' % sr)
    else:
        log.debug('No results for %s' % sr)
        message.reply("Sorry, we can't find any listing with this criteria.")


def ask_question(message, sr, question_text=None):
    q = sr.next_question()
    if q is None:
        send_results(message, sr)
        sr.reset_questions()
    else:
        if question_text:
            message.reply(question_text)
        elif not q.skip_ask:
            message.reply(q.question)


@respond_to('^reset|again|restart$', re.IGNORECASE)
def restart(message, sr):
    sr.reset_questions()
    ask_question(message, sr, question_text=THE_GREETING)


# @respond_to('^I want to move to (.+)$', re.IGNORECASE)
# def define_location(message, sr, location):
#
#     if sr.current_question and sr.current_question.param_key == 'location_bbox':
#         _set_answer(message, sr)
#     else:
#         sr.reset_questions()
#         sr.next_question()
#         assert sr.current_question.param_key == 'location_bbox'
#         _set_answer(message, sr)

@respond_to('^Hi|Hello|ClikHome|help$', re.IGNORECASE)
def hi(message, sr):
    sr.reset_questions()
    message.reply(THE_GREETING)
    ask_question(message, sr)


def default_handler(message, sr):
    _set_answer(message, sr)
    # message.reply('Echo %r' % message.text)


@respond_to('^hey$', re.IGNORECASE)
def hey(message, sr):
    # eggplant
    message.reply(u'\U0001F346')


@respond_to('^secret500$', re.IGNORECASE)
def secret500(message, sr):
    message.reply('%s' % (1/0))

if settings.DEBUG:
    # @respond_to('^test$', re.IGNORECASE)
    # def test(message, sr):
    #     from properties.models import Listing
    #     attachment = get_results_attachment(Listing.objects.filter(is_listed=True)[0:5])
    #     message.attachment_reply(attachment)

    @respond_to('^show_results$', re.IGNORECASE)
    def show_results(message, sr):
        send_results(message, sr)

