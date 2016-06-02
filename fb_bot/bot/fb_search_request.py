# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import random

from clikhome_shared.engine.questions import get_questions_list
from fb_bot.bot.questions import Question, EngineQuestion, BadAnswer, ImmediateReply
from fb_bot import shared_tasks

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class FbSearchRequest(object):

    def __init__(self, user_verbose_id):
        self.user_verbose_id = user_verbose_id
        self.params = {}
        self.questions_unanswered_list = list()
        self.questions_answered_list = list()
        self.current_question = None
        self.is_searching = False
        self.location_fmt_address = None
        self.reset_questions()

    def reset_questions(self):
        self.questions_unanswered_list = [
            Question('Where do you want to move?', 'location_bbox', skip_ask=True),
            Question('How many bedrooms do you need?', 'bedrooms', '^\d+$'),
            Question('What is the maximum price per month you are willing to pay?', 'rent__lte', '^\d+$'),
            EngineQuestion,
            EngineQuestion,
            EngineQuestion,
        ]

        q_kwargs = dict(character=0, single=0)
        for x in xrange(0, 3):
            if bool(random.getrandbits(1)):
                q_kwargs['character'] += 1
            else:
                q_kwargs['single'] += 1

        engine_questions = get_questions_list(random=0, **q_kwargs)
        for i, q in enumerate(self.questions_unanswered_list):
            if q is EngineQuestion:
                self.questions_unanswered_list[i] = EngineQuestion(engine_questions.pop(), 'engine-question-%s' % i)

        self.current_question = None
        self.location_fmt_address = None
        self.params = {}

    def next_question(self):
        if self.questions_unanswered_list:
            self.current_question = self.questions_unanswered_list.pop(0)
            self.questions_answered_list.append(self.current_question)
        else:
            self.current_question = None
        return self.current_question

    def set_answer(self, answer):
        assert self.current_question

        try:
            self.current_question.set_answer(answer)
            if not isinstance(self.current_question, EngineQuestion):
                self._set_param(self.current_question.param_key, self.current_question.param_value)
                if self.current_question.param_key == 'location_bbox':
                    self.location_fmt_address = self.current_question.param_value.formatted_address
                    return 'Ok, we are going to "%s"' % self.location_fmt_address
        except BadAnswer, e:
            raise ImmediateReply(e.message)

    def get_search_result(self):
        try:
            self.is_searching = True
            bbox = self.params['location_bbox']
            assert self.engine_user_answers
            filter_kwargs = dict(
                rent__lte=self.params['rent__lte'],
                unit__rental_complex__address__coords__contained=bbox.to_geom(),
                unit__bedrooms=self.params['bedrooms'],
                is_listed=True,
            )
            verbose_kwargs = filter_kwargs.copy()
            verbose_kwargs['unit__rental_complex__address__coords__contained'] = '%s' % verbose_kwargs['unit__rental_complex__address__coords__contained']
            self.log('Query filter %r' % verbose_kwargs)
            more_url, listings = shared_tasks.listings_search(
                    bbox_as_list=bbox.as_list,
                    filter_kwargs=filter_kwargs,
                    engine_user_answers=self.engine_user_answers,
                    search_location_fmt_address=self.location_fmt_address
            )
            return more_url, listings
        finally:
            self.is_searching = False

    @property
    def engine_user_answers(self):
        user_answers = dict()
        for q in self.questions_answered_list:
            if isinstance(q, EngineQuestion) and q.answer:
                user_answers[q.question] = q.answer
        return user_answers

    def _set_param(self, key, value):
        self.log('set param %s="%r"' % (key, value))
        self.params[key] = value

    def log(self, msg):
        log.debug('%s: %s current_question: %r' % (self, msg, self.current_question))

    def __repr__(self):
        return '<FbSearchRequest u=%s>' % self.user_verbose_id
