# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from configurations import values
from .common import Common, EnvVal


class Dev(Common):
    DEBUG = True
    DATABASES = values.DatabaseURLValue('sqlite://db.sqlite3')
    REDIS_URL = EnvVal('REDIS_URL')

    @classmethod
    def pre_setup(cls):
        DOTENV = os.path.join(Common.BASE_DIR, '.env')
        if os.path.exists(DOTENV):
            cls.DOTENV = DOTENV

        if cls.DOTENV_LOADED is None:
            cls.load_dotenv()
