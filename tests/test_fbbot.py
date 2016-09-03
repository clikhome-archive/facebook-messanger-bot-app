# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import unittest
import json
import django

from clikhome_shared.utils.bbox import Bbox
from django.test.utils import override_settings
# from django.test import TransactionTestCase
from messengerbot import MessengerClient
from mock import patch, MagicMock, Mock
from facebook import GraphAPI

from tests.utils import BaseTestCase


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

    def test_parse_name(self):
        from fb_bot.bot.message import Message
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
        msg = Message(wh_msg=self.get_msg(), session=session_mock)
        results = []
        for data in fixtures:
            session_mock.data = dict(user_profile=data)
            results.append(msg.sender_first_name)
        self.assertEqual(results[0], results[1])

    def get_msg(self):
        from messengerbot.webhooks import WebhookEntry
        wh_entry_list = WebhookEntry(
            self.message_entry['entry'][0]['id'],
            self.message_entry['entry'][0]['time'],
            self.message_entry['entry'][0]['messaging'],
        )
        return wh_entry_list.messaging[0]

    @patch.object(MessengerClient, 'send')
    def test_greetings(self, mock_messenger_client_send):
        from fb_bot.bot.chat_session import ChatSession
        from fb_bot.bot.message import Message
        from fb_bot.bot import handlers

        with ChatSession('100009095718696') as session:
            msg = self.get_msg()
            message = Message(msg, session)
            fmt_greetings = handlers.THE_GREETING.format(sender_first_name=message.sender_first_name)
            def send_side_effect(message):
                assert message.message.text == fmt_greetings
            mock_messenger_client_send.side_effect = send_side_effect
            handlers.hi(message, session.search_request)
            mock_messenger_client_send.assert_called_once()

    def test_questions(self):
        from fb_bot.bot.fb_search_request import FbSearchRequest
        from fb_bot.bot import questions

        sr = FbSearchRequest(100009095718696)
        q = sr.next_question()
        self.assertIsInstance(q, questions.LocationQuestion)
        print q
        # self.mock_geolocator.return_value = None
        self.assertRegexpMatches(sr.set_answer('Iowa'), '^Ok, we are going to')

        q = sr.next_question()
        print q
        self.assertIsInstance(q, questions.BedroomsQuestion)
        sr.set_answer('1')

        q = sr.next_question()
        print q
        self.assertIsInstance(q, questions.PriceQuestion)
        sr.set_answer('9000')

        q = sr.next_question()
        print q
        lease_question = q
        self.assertIsInstance(q, questions.LeaseStartQuestion)
        sr.set_answer('today')
        sr.set_answer('yesterday')
        print lease_question.param_value

        # q = sr.next_question()
        # self.assertRegexpMatches(q.param_key, '^engine-question-\d+$')
        # sr.set_answer('no')
        #
        # q = sr.next_question()
        # self.assertRegexpMatches(q.param_key, '^engine-question-\d+$')
        # sr.set_answer('no')
        #
        # q = sr.next_question()
        # self.assertRegexpMatches(q.param_key, '^engine-question-\d+$')
        # sr.set_answer('no')


    # @unittest.skip
    # def test_search_request_with_session(self):
    #     from fb_bot.bot.chat_session import ChatSession
    #     user_id = 100009095718696
    #
    #     self.mock_graph_get.reset_mock()
    #
    #     session_obj = ChatSession(user_id)
    #
    #     with session_obj as session:
    #         self.mock_graph_get.assert_called_once_with(str(user_id))
    #         sr = session.search_request
    #         self._set_answers(sr)
    #         sr.reset()
    #         self._set_answers(sr)

    def test_geocoder(self):
        from fb_bot.bot.fb_search_request import FbSearchRequest
        sr = FbSearchRequest(100009095718696)
        sr.reset()
        q = sr.next_question()
        self.assertEqual(q.param_key, 'location_bbox')
        sr.set_answer('Iowa')
        # print sr.params['location_bbox']
        self.mock_geolocator.assert_called_once_with('Iowa')

    def _set_answers(self, sr, location='Iowa'):
        q = sr.next_question()
        self.assertEqual(q.param_key, 'location_bbox')
        self.assertRegexpMatches(sr.set_answer(location), '^Ok, we are going to')

        # print sr.params['location_bbox']

        q = sr.next_question()
        self.assertEqual(q.param_key, 'bedrooms')
        sr.set_answer('1')

        q = sr.next_question()
        self.assertEqual(q.param_key, 'rent__lte')
        sr.set_answer('9000')

        q = sr.next_question()
        self.assertRegexpMatches(q.param_key, '^engine-question-\d+$')
        sr.set_answer('no')

        q = sr.next_question()
        self.assertRegexpMatches(q.param_key, '^engine-question-\d+$')
        sr.set_answer('no')

        q = sr.next_question()
        self.assertRegexpMatches(q.param_key, '^engine-question-\d+$')
        sr.set_answer('no')

    # def test_search_request(self):
    #     from fb_bot.bot.fb_search_request import FbSearchRequest
    #
    #     sr = FbSearchRequest(1595878670725307)
    #     self._set_answers(sr, 'New York')
    #     qs = sr._get_listing_qs()
    #     print sr.params
    #     print 'Found %s results' % qs.count()

    # def test_geocode(self):
    #     locations = [
    #         'NY',
    #         'New York',
    #         'Boston',
    #         'Los Angeles',
    #         'nnnnnnnnnnnnnnnnn'
    #     ]
    #     from slack_bot.process.geocode import geocode_location_to_bbox
    #
    #     for q in locations:
    #         bbox = geocode_location_to_bbox(q)
    #         print q, bbox

    # def get_test_entries(self):
    #     import time
    #     recipient_id = 476499879206175
    #     sender_ids = [
    #         1595878670725308,
    #         1595878670725307,
    #         1595878670725306,
    #         1595878670725305,
    #         1595878670725304,
    #     ]
    #     # TODO:
    #     #  '{"object":"page","entry":[{"id":"476499879206175","time":1463910487964,"messaging":[{"sender":{"id":"1595878670725308"},"recipient":{"id":"476499879206175"},"timestamp":1463910214657,"message":{"mid":"mid.1463910214622:c27bc02ff9b9a98c22","seq":70,"text":"Hey"}}]}]}'
    #     # '{"object":"page","entry":[{"id":"476499879206175","time":1463910489705,"messaging":[{"sender":{"id":"1595878670725308"},"recipient":{"id":"476499879206175"},"timestamp":1463910455015,"message":{"mid":"mid.1463910455008:68160c45703c925412","seq":71,"sticker_id":369239263222822,"attachments":[{"type":"image","payload":{"url":"https:\\/\\/fbcdn-dragon-a.akamaihd.net\\/hphotos-ak-xfa1\\/t39.1997-6\\/851557_369239266556155_759568595_n.png"}}]}},{"sender":{"id":"1595878670725308"},"recipient":{"id":"476499879206175"},"timestamp":1463910479224,"message":{"mid":"mid.1463910479218:dcf4367d3dcbd4ac22","seq":72,"text":"gg"}}]}]}'
    #
    #     while True:
    #         for sender in sender_ids:
    #             e = {
    #                 "id": "476499879206175",
    #                 "time": int(time.time()),
    #                 # "time": 1463866630322,
    #                 "messaging": [
    #                     {
    #                         "sender": {"id": sender},
    #                         "recipient": {"id": recipient_id},
    #                         "timestamp": int(time.time()),
    #                         # "timestamp": 1463866597065,
    #                         "message": {"mid": "mid.1463866597025:cf64778ce6b2a7be18", "seq": 66, "text": "!!!!"}}
    #                     ]
    #             }
    #             yield e


    # def test_entry_queue(self):
    #     import redis
    #     from django.conf import settings
    #
    #     client = redis.StrictRedis.from_url(settings.REDIS_URL)
    #     # queue = CustomHotQueue("myqueue", redis_client=client)

    # def test_listing_to_attachment(self):
    #     from slack_bot.process.plugins import listing_to_attachment
    #     from properties.models import Listing
    #     import json
    #
    #     # for listing in Listing.objects.filter(score__gte=9, is_listed=True)[0:3]:
    #     for listing in Listing.objects.filter(id__in=[303909, 583007, 303913]).exclude(unit__photos=None)[0:3]:
    #         print json.dumps(listing_to_attachment(listing), indent=4)

    # def test_bot_process_spawn(self):
    #     from django.conf import settings
    #     from slack_bot.models import SlackIntegration
    #     slack_i = SlackIntegration.objects.first()
    #     kwargs = dict(bot_access_token=slack_i.bot_access_token)
    #     p = spawn_bot_process(**kwargs)
    #     print p
    #     print p.join()
