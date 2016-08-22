# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest

from clikhome_shared.utils.bbox import Bbox
from django.test.utils import override_settings
import os
# from django.test import TransactionTestCase
from messengerbot import MessengerClient
from mock import patch, MagicMock, Mock
from facebook import GraphAPI


class FbBotTest(unittest.TestCase):

    def setUp(self):
        # from tests.setting_test import Test
        os.environ['DJANGO_CONFIGURATION'] = 'Test'
        os.environ['DJANGO_SETTINGS_MODULE'] = 'clikhome_fbbot.settings'
        # os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
        # from configurations import importer
        # importer.installed = True

        import django
        django.setup()

        import json
        with open(os.path.join(os.path.dirname(__file__), 'message_entry.json'), 'r') as fp:
            self.message_entry = json.load(fp)

    @patch.object(MessengerClient, 'send')
    @patch.object(GraphAPI, 'get')
    def test_greetings(self, mock_graph_get, mock_messenger_client_send):
        mock_graph_get.return_value = {
            u'name': u'\u0410\u043b\u0435\u043a\u0441\u0435\u0439 \u041a\u043e\u0440\u043e\u0431\u043a\u043e\u0432',
            u'id': u'100009095718696'
        }

        from fb_bot.bot.chat_session import ChatSession
        from fb_bot.bot.message import Message
        from fb_bot.bot import handlers
        from messengerbot.webhooks import WebhookEntry

        with ChatSession('100009095718696') as session:
            wh_entry_list = WebhookEntry(
                self.message_entry['entry'][0]['id'],
                self.message_entry['entry'][0]['time'],
                self.message_entry['entry'][0]['messaging'],
            )
            msg = wh_entry_list.messaging[0]
            message = Message(msg, session)
            fmt_greetings = handlers.THE_GREETING.format(sender_first_name=message.sender_first_name)
            def send_side_effect(message):
                assert message.message.text == fmt_greetings
            mock_messenger_client_send.side_effect = send_side_effect
            handlers.hi(message, session.search_request)
        mock_messenger_client_send.assert_called_once()


    @patch('clikhome_fbbot.utils.geolocator.geocode_location_to_bbox')
    @patch.object(GraphAPI, 'get')
    def test_search_request(self, mock_graph_get, mock_geolocator):
        from fb_bot.bot.chat_session import ChatSession
        user_id = 100009095718696
        mock_graph_get.return_value = {
            u'name': u'\u0410\u043b\u0435\u043a\u0441\u0435\u0439 \u041a\u043e\u0440\u043e\u0431\u043a\u043e\u0432',
            u'id': u'100009095718696'
        }
        mock_geolocator.return_value = Bbox(**{
                'formatted_address': 'Iowa, USA',
                'ne_lng': -90.140061,
                'sw_lat': 40.375437,
                'sw_lng': -96.639535,
                'ne_lat': 43.5011961
        })
        session_obj = ChatSession(user_id)

        with session_obj as session:
            sr = session.search_request
            print sr
            self._set_answers(sr)
            sr.reset_questions()
            self._set_answers(sr)
        mock_graph_get.assert_called_once_with(str(user_id))
        mock_geolocator.assert_called()

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
