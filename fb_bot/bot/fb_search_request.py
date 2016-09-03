# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import os
import random

import aiml

from fb_bot.bot.questions import EngineQuestion, BadAnswer, ImmediateReply, get_questions_list, BaseQuestion
from fb_bot import shared_tasks

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class FbSearchRequest(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.questions_unanswered_list = list()
        self.questions_answered_list = list()
        self.current_question = None
        self.is_waiting_for_results = False
        # self.aiml = aiml.Kernel()
        # aiml_file = os.path.join(os.path.dirname(__file__), 'questions.xml')
        # self.aiml.learn(aiml_file)
        self.reset()

    def reset(self):
        self.questions_unanswered_list = get_questions_list()
        self.questions_answered_list = list()
        self.current_question = None

    @property
    def location_fmt_address(self):
        for q in self.questions_answered_list:
            if getattr(q, 'param_key', None) == 'location_bbox':
                return q.value.formatted_address

    def next_question(self):
        if self.questions_unanswered_list:
            self.current_question = self.questions_unanswered_list.pop(0)
            self.questions_answered_list.append(self.current_question)
        else:
            self.current_question = None
        return self.current_question

    def lookup_next_question(self):
        if self.questions_unanswered_list:
            return self.questions_unanswered_list[0]

    @property
    def params(self):
        result = dict()
        for q in self.questions_answered_list:
            if isinstance(q, EngineQuestion) or not isinstance(q, BaseQuestion):
                continue

            assert q.param_key not in result, q.param_key
            result[q.param_key] = q.value
            self.log('set param %s="%r"' % (q.param_key, result[q.param_key]))
        return result

    # @property
    # def engine_user_answers(self):
    #     user_answers = dict()
    #     for q in self.questions_answered_list:
    #         if isinstance(q, EngineQuestion) and q.value:
    #             user_answers[q.question] = q.value
    #     return user_answers

    def set_answer(self, answer):
        try:
            reply = self.current_question.set_answer(answer)
            if reply:
                return reply
        except BadAnswer, e:
            # if raise ImmediateReply we not ask next question
            raise ImmediateReply(e.message)

    def request_search_results(self):
        p = self.params
        bbox = p['location_bbox']

        # TODO: use other params
        filter_kwargs = dict(
            rent__lte=p['rent__lte'],
            unit__rental_complex__address__coords__contained=bbox.to_geom(),
            unit__bedrooms=p['bedrooms'],
            is_listed=True,
        )
        verbose_kwargs = filter_kwargs.copy()
        verbose_kwargs['unit__rental_complex__address__coords__contained'] = '%s' % verbose_kwargs['unit__rental_complex__address__coords__contained']
        self.log('Query filter %r' % verbose_kwargs)
        shared_tasks.request_listings_search(
            user_id=self.user_id,
            bbox_as_list=bbox.as_list,
            filter_kwargs=filter_kwargs,
            engine_user_answers=dict(),
            # engine_user_answers=self.engine_user_answers,
            search_location_fmt_address=self.location_fmt_address
        )
        self.is_waiting_for_results = True

    def log(self, msg):
        log.debug('%s: %s current_question: %r' % (self, msg, self.current_question))

    def __repr__(self):
        return '<FbSearchRequest u=%s>' % self.user_id
