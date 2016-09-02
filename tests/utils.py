# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import unittest

import django

os.environ['DJANGO_CONFIGURATION'] = 'Test'
os.environ['DJANGO_SETTINGS_MODULE'] = 'clikhome_fbbot.settings'
# os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
# from configurations import importer
# importer.installed = True
django.setup()


class BaseTestCase(unittest.TestCase):
    pass
    # def setUp(self):
    #     # from tests.setting_test import Test
    #     os.environ['DJANGO_CONFIGURATION'] = 'Test'
    #     os.environ['DJANGO_SETTINGS_MODULE'] = 'clikhome_fbbot.settings'
    #     # os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    #     # from configurations import importer
    #     # importer.installed = True
    #     django.setup()
