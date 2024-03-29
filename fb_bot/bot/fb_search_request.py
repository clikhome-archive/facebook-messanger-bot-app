# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

from raven.contrib.django.raven_compat.models import client as raven_client
from fb_bot.bot.questions import get_questions_list, BaseQuestion
from fb_bot import shared_tasks

log = logging.getLogger('clikhome_fbbot.%s' % __name__)


class FbSearchRequest(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.questions_unanswered_list = list()
        self.questions_answered_list = list()
        self.current_question = None
        self.is_waiting_for_results = False
        self.reset()

    def reset(self):
        self.questions_unanswered_list = get_questions_list()
        self.questions_answered_list = list()
        self.current_question = None

    def next_question(self):
        if self.questions_unanswered_list:
            self.current_question = self.questions_unanswered_list.pop(0)
            self.questions_answered_list.append(self.current_question)
        else:
            self.current_question = None

        return self.current_question

    def go_to_question(self, question_class):
        question = None

        question_to_skip = list()
        for q in self.questions_unanswered_list:
            if isinstance(q, question_class):
                question = q
                break
            else:
                question_to_skip.append(q)

        if question:
            for q_remove in question_to_skip:
                self.questions_unanswered_list.remove(q_remove)
                self.questions_answered_list.append(q_remove)

        if question is not None:
            self.current_question = question
        else:
            log.warn('Cant change question')
            raven_client.captureMessage("Cant change question")

        return question

    @property
    def filter_params(self):
        result = dict()
        for q in self.questions_answered_list:
            if not isinstance(q, BaseQuestion):
                continue

            for key, value in q.filter_value.items():
                # self.log('[%s] set param %s="%r" from ' % (q.__class__.__name__, key, value))
                assert key not in result
                result[key] = value
        return result

    def request_search_results(self):
        filter_params = dict(self.filter_params)
        bbox = filter_params.pop('!location_bbox')
        location_fmt_address = str(bbox.formatted_address)

        verbose_params = filter_params.copy()
        verbose_params['user_id'] = str(self.user_id)
        verbose_params['bbox_as_list'] = str(bbox.as_list)
        verbose_params['search_location_fmt_address'] = location_fmt_address

        log.debug('%s: Query filter %r' % (self, verbose_params))

        shared_tasks.request_simple_listings_search(
            user_id=self.user_id,
            bbox_as_list=bbox.as_list,
            filters=filter_params,
            search_location_fmt_address=location_fmt_address,
            limit=1
        )
        self.is_waiting_for_results = True

    def log(self, msg):
        log.debug('%s: %s current_question: %r' % (self, msg, self.current_question))

    def __repr__(self):
        if self.current_question:
            current_question = self.current_question.__class__.__name__
        else:
            current_question = None
        return '<FbSearchRequest u=%s q=%s>' % (self.user_id, current_question)
