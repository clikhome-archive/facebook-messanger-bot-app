# -*- coding: utf-8 -*-
from __future__ import absolute_import

from clikhome_fbbot.settings import Prod, EnvVal


class Stage(Prod):
    BROKER_URL = EnvVal('REDIS_URL')
    CELERY_RESULT_BACKEND = EnvVal('REDIS_URL')
    REDIS_URL = EnvVal('REDIS_URL')
