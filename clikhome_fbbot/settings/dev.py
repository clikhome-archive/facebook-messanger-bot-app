# -*- coding: utf-8 -*-
from __future__ import absolute_import
from configurations import values
from .common import Common, EnvVal


class Dev(Common):
    DEBUG = True
    DATABASES = values.DatabaseURLValue('sqlite://db.sqlite3')
    REDIS_URL = EnvVal('REDIS_URL')

