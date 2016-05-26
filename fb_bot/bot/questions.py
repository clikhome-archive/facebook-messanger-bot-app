# -*- coding: utf-8 -*-
from __future__ import absolute_import
import re

from fb_bot import shared_tasks


class ImmediateReply(Exception):
    pass


class BadAnswer(Exception):
    pass


class Question(object):
    question = None
    answer_matcher = re.compile(r'.+', re.IGNORECASE)
    answer_bad_message = 'Bad answer "%(answer)s"'

    def __init__(self, question, param_key, answer_match_pattern=None, skip_ask=False):
        self.question = question
        self.param_key = param_key
        self.param_value = None
        self.skip_ask = skip_ask
        self.answer = None
        if answer_match_pattern is not None:
            self.answer_matcher = re.compile(answer_match_pattern, re.IGNORECASE)

    def _validate_answer(self, answer):
        m = self.answer_matcher.match(answer)
        return bool(m)

    def set_answer(self, answer):
        if self.param_key == 'bedrooms' and answer.strip().lower() == 'studio':
            answer = '0'

        if self.param_key == 'rent__lte':
            answer = re.sub('\D+', '', answer)

        if not self._validate_answer(answer):
            raise BadAnswer(self.answer_bad_message % dict(answer=answer))

        if self.param_key == 'location_bbox':
            bbox = shared_tasks.geocode_location_to_bbox(answer)
            if bbox:
                self.param_value = bbox
                self.answer = answer
            else:
                raise BadAnswer("""Sorry, we can't find "%s" location.""" % answer)
        else:
            self.param_value = self.answer = answer

    def __repr__(self):
        return '<%s question="%s" key="%s">' % (self.__class__.__name__, self.question, self.param_key)


class EngineQuestion(Question):
    answer_matcher = re.compile(r'^yes|no|y|n$', re.IGNORECASE)
    answer_bad_message = 'Sorry, "%(answer)s" is a bad answer, please choose yes/y or no/n.'

    def set_answer(self, answer):
        answer = answer.strip().lower()
        if not self._validate_answer(answer):
            raise BadAnswer(self.answer_bad_message % dict(answer=answer))

        if answer == 'y':
            answer = 'yes'
        if answer == 'n':
            answer = 'no'

        return super(EngineQuestion, self).set_answer(answer)
