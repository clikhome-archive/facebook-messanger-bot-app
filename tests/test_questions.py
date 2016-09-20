# -*- coding: utf-8 -*-
from __future__ import absolute_import
from unittest import skip
from mock import patch
from datetime import datetime

from tests.utils import BaseTestCase


@skip
class QuestionsTestCase(BaseTestCase):

    def setUp(self):
        super(QuestionsTestCase, self).setUp()
        from facebook import GraphAPI
        from fb_bot.bot.messenger_client import MessengerClient
        from fb_bot.bot.chat_session import ChatSession
        from fb_bot.bot.ctx import set_chat_context, session, search_request

        self.send_mock = patch.object(MessengerClient, 'send').start()
        self.mock_graph_get = patch.object(GraphAPI, 'get').start()
        self.session_reply = patch.object(ChatSession, 'reply').start()

        self.session = ChatSession('100009095718696').__enter__()
        self.ctx = set_chat_context(self.session)
        self.ctx.__enter__()

    def assertBadAnswer(self, question_object, answer):
        question_object.activate()
        self.session_reply.reset_mock()
        question_object.set_answer(answer)
        self.session_reply.assert_called_once()
        self.assertEqual(question_object.wait_for_answer, True)

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

        self.assertBadAnswer(LeaseStartQuestion(), 'none')

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
            assert q.additional_question.value == False

        q = PetsQuestion()
        try:
            q.set_answer('Dog')
        except ImmediateReply, e:
            self.assertRaises(BadAnswer, q.set_answer, 'maybe')

        q = PetsQuestion()
        q.set_answer('cat')
