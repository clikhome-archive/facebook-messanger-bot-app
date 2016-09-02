# -*- coding: utf-8 -*-
from __future__ import absolute_import

from datetime import datetime

from tests.utils import BaseTestCase


class QuestionsTestCase(BaseTestCase):

    def test_lease_question(self):
        from fb_bot.bot.questions import LeaseStartQuestion, BadAnswer

        def check_value(value):
            assert len(value) == 2
            for d in value:
                self.assertIsInstance(d, datetime)

        q = LeaseStartQuestion()
        q.set_answer('today')
        check_value(q.param_value)

        LeaseStartQuestion().set_answer('day before yesterday')
        LeaseStartQuestion().set_answer('yesterday')

        self.assertRaises(BadAnswer, LeaseStartQuestion().set_answer, 'none')
        self.assertRaises(BadAnswer, LeaseStartQuestion().set_answer, 'one')
        self.assertRaises(BadAnswer, LeaseStartQuestion().set_answer, '1')
        self.assertRaises(BadAnswer, LeaseStartQuestion().set_answer, 'why it does matter')

    def test_pets_question(self):
        from fb_bot.bot.questions import PetsQuestion, BadAnswer, ImmediateReply
        q = PetsQuestion()
        q.set_answer('No')

        self.assertRaises(ImmediateReply, PetsQuestion().set_answer, 'Dog')
        q = PetsQuestion()
        try:
            q.set_answer('Dog')
        except ImmediateReply, e:
            assert e.message
            q.set_answer('no')
            assert q.additional_question.value == 'no'

        q = PetsQuestion()
        try:
            q.set_answer('Dog')
        except ImmediateReply, e:
            self.assertRaises(BadAnswer, q.set_answer, 'maybe')

        q = PetsQuestion()
        q.set_answer('cat')
