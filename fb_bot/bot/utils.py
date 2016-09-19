# -*- coding: utf-8 -*-
from __future__ import absolute_import
import requests


class CallToActions(object):
    payload = 'USER_DEFINED_PAYLOAD:GET_STARTED'

    @classmethod
    def setup(cls):
        from fb_bot.bot.messenger_client import messenger
        params = {
            'access_token': messenger.access_token
        }
        data = {
            "setting_type": "call_to_actions",
            "thread_state": "new_thread",
            "call_to_actions": [
                {
                    "payload": cls.payload
                }
            ]
        }
        response = requests.post(
            '%s/thread_settings' % messenger.GRAPH_API_URL,
            params=params,
            json=data
        )
        if response.status_code != 200:
            raise Exception(
                response.json()['error']
            )
        return response.json()

    @classmethod
    def remove(cls):
        from fb_bot.bot.messenger_client import messenger
        params = {
            'access_token': messenger.access_token
        }
        data = {
          "setting_type": "call_to_actions",
          "thread_state": "new_thread"
        }
        response = requests.delete(
            '%s/thread_settings' % messenger.GRAPH_API_URL,
            params=params,
            json=data
        )
        if response.status_code != 200:
            raise Exception(
                response.json()['error']
            )
        print response.content
