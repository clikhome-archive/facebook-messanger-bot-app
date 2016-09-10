# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest

import logging
import sys

kw = {
    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
    'level': logging.DEBUG,
    'stream': sys.stdout,
}
logging.basicConfig(**kw)
import django

django.setup()


class BaseTestCase(unittest.TestCase):
    pass
