# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
from unittest import skip

import os
import json

from clikhome_shared.utils.bbox import Bbox
from django.test.utils import override_settings
from messengerbot import MessengerClient
from mock import patch, MagicMock, Mock
from facebook import GraphAPI

from tests.utils import BaseTestCase

from fb_bot.bot.entry_handler import EntryHandler


class FbBotTest(BaseTestCase):

    def setUp(self):
        super(FbBotTest, self).setUp()

        with open(os.path.join(os.path.dirname(__file__), 'message_entry.json'), 'r') as fp:
            self.message_entry = json.load(fp)

        from clikhome_shared.utils.geocode import Geolocator

        self.mock_geolocator = patch.object(Geolocator, 'geocode_location_to_bbox').start()
        self.mock_geolocator.return_value = Bbox(**{
            'formatted_address': 'Iowa, USA',
            'ne_lng': -90.140061,
            'sw_lat': 40.375437,
            'sw_lng': -96.639535,
            'ne_lat': 43.5011961
        })

        self.mock_graph_get = patch.object(GraphAPI, 'get').start()
        self.mock_graph_get.return_value = {
            u'name': u'\u0410\u043b\u0435\u043a\u0441\u0435\u0439 \u041a\u043e\u0440\u043e\u0431\u043a\u043e\u0432',
            u'id': u'100009095718696'
        }

    @skip('Broken')
    def test_parse_name(self):
        fixtures = [
            {
                u'first_name': u'\u0410\u043b\u0435\u043a\u0441\u0435\u0439',
                u'gender': u'male',
                u'last_name': u'\u041a\u043e\u0440\u043e\u0431\u043a\u043e\u0432',
                u'locale': u'en_US',
                u'profile_pic': u'https://scontent.xx.fbcdn.net/v/t1.0-1/p200x200/12004789_1501056863540823_2883307817188408648_n.jpg?oh=6547a7dc9c75afb640197537f672d9ef&oe=5846D2D1',
                u'timezone': 3
            },
            {
                u'name': u'\u0410\u043b\u0435\u043a\u0441\u0435\u0439 \u041a\u043e\u0440\u043e\u0431\u043a\u043e\u0432',
                u'id': u'100009095718696'
            }
        ]
        session_mock = Mock()
        msg = self.get_message(session_mock)
        results = []
        for data in fixtures:
            session_mock.data = dict(user_profile=data)
            results.append(msg.sender_first_name)
        self.assertEqual(results[0], results[1])

    def get_wh_message(self, text=None):
        from messengerbot.webhooks import WebhookEntry
        now = int(datetime.datetime.utcnow().strftime('%s'))*1000

        def update_timestamp(msg):
            msg['timestamp'] = now
            return msg
        messaging = map(update_timestamp, list(self.message_entry['entry'][0]['messaging']))

        wh_entry_list = WebhookEntry(
            id=self.message_entry['entry'][0]['id'],
            time=now,
            messaging=messaging,
        )
        msg = wh_entry_list.messaging[0]
        if text:
            msg._message['text'] = text
        return msg

    def get_message(self, session, text=None):
        from fb_bot.bot.message import Message
        return Message(wh_msg=self.get_wh_message(text), session=session)

    @patch('fb_bot.shared_tasks.request_simple_listings_search')
    @patch.object(MessengerClient, 'send')
    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'unique-snowflake'
            }
        }
    )
    def test_all_handlers(self, mock_messenger_client_send, mock_request_listings_search_task):
        from fb_bot.bot.chat_session import ChatSession
        from fb_bot.bot.ctx import set_chat_context
        from fb_bot.bot import questions

        def send_logger(message):
            print 'Send: %r to %r' % (message.message.text, message.recipient.recipient_id)

        entry_handler = EntryHandler()

        with ChatSession('100009095718696') as session, set_chat_context(session):
            message = self.get_wh_message('Hi')

            def assert_greetings(message):
                assert message.message.text == questions.Greeting().greeting
                send_logger(message)

            mock_messenger_client_send.side_effect = assert_greetings

            entry_handler._handle_message(message, session)
            mock_messenger_client_send.assert_called_once()
            mock_messenger_client_send.side_effect = send_logger

            entry_handler._handle_message(self.get_wh_message('Fine'), session)
            entry_handler._handle_message(self.get_wh_message('Iowa'), session)
            entry_handler._handle_message(self.get_wh_message('studio'), session)
            entry_handler._handle_message(self.get_wh_message('9000'), session)
            entry_handler._handle_message(self.get_wh_message('today'), session)
            entry_handler._handle_message(self.get_wh_message('no'), session)
            mock_request_listings_search_task.assert_called_once()

    def test_session_local(self):
        from fb_bot.bot.chat_session import ChatSession

        with ChatSession('100009095718696') as s1:
            with ChatSession('100009095718696') as s2:
                self.assertEqual(s2._session_usage, 2)
                with ChatSession('200009095718696') as s3:
                    self.assertEqual(s1, s2)
                    self.assertNotEqual(s2, s3)
                    self.assertEqual(s3._session_usage, 1)
            self.assertEqual(s1._session_usage, 1)

        with ChatSession('100009095718696') as s1:
            self.assertEqual(s1._session_usage, 1)

