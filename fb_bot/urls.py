# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import include, url
from fb_bot.views import BotView

urlpatterns = [
    url(r'^webhook/?$', BotView.as_view())
]
