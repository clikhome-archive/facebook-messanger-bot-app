# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import unittest

os.environ['DJANGO_CONFIGURATION'] = 'Test'
os.environ['DJANGO_SETTINGS_MODULE'] = 'clikhome_fbbot.settings'
import django
django.setup()


class BaseTestCase(unittest.TestCase):
    pass
