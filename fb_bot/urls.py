# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import include, url
from fb_bot import views

urlpatterns = [
    url(r'^$', 'fb_bot.views.index'),
    url(r'^secret500/?$', 'fb_bot.views.secret500'),
    url(r'^webhook/?$', views.WebHookView.as_view()),
]
