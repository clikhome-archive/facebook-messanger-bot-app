# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import sys
# from django.test import override_settings
# from freezegun import freeze_time

import pytest
from django.test import Client
from django.test import TestCase
from mock import patch

from fb_bot.bot.entry_handler import EntryHandler


@pytest.mark.django_db(transaction=False)
class HookViewTestCase(TestCase):

    def setUp(self):
        super(HookViewTestCase, self).setUp()
        kw = {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            'level': logging.DEBUG,
            'stream': sys.stdout,
        }
        logging.basicConfig(**kw)
        import redis
        from fb_bot.bot.globals import redis_connection_pool
        redis.Redis(connection_pool=redis_connection_pool).execute_command('flushdb')

    # @freeze_time("2016-09-18 16:12:00")
    # @override_settings(
    #     FBBOT_MSG_EXPIRE=10
    # )
    # def test_drop_expire(self):
    #     # TODO:
    #     pass

    @patch.object(EntryHandler, 'add_to_queue')
    def test_messages_dup(self, add_to_queue_mock):
        c = Client()
        raw_json = '''
            {
              "object": "page",
              "entry": [
                {
                  "id": "476499879206175",
                  "time": 1474211290283,
                  "messaging": [
                    {
                      "sender": {
                        "id": "1595878670725308"
                      },
                      "recipient": {
                        "id": "476499879206175"
                      },
                      "timestamp": 1474211290228,
                      "message": {
                        "mid": "mid.1474211290219:53c0d476bb7c114525",
                        "seq": 1151,
                        "text": "Hey"
                      }
                    }
                  ]
                }
              ]
            }
         '''

        response = c.post('/webhook/', raw_json, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        add_to_queue_mock.assert_called_once()

        raw_json = '''
            {
              "object": "page",
              "entry": [
                {
                  "id": "476499879206175",
                  "time": 1474211304797,
                  "messaging": [
                    {
                      "sender": {
                        "id": "1595878670725308"
                      },
                      "recipient": {
                        "id": "476499879206175"
                      },
                      "timestamp": 1474211290228,
                      "message": {
                        "mid": "mid.1474211290219:53c0d476bb7c114525",
                        "seq": 1151,
                        "text": "Hey"
                      }
                    }
                  ]
                }
              ]
            }
        '''
        add_to_queue_mock.reset_mock()
        response = c.post('/webhook/', raw_json, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(add_to_queue_mock.called, False)
