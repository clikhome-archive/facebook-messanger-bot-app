# -*- coding: utf-8 -*-
from __future__ import absolute_import

from clikhome_shared.utils.geocode import Geolocator
from django.conf import settings

geolocator = Geolocator(api_key=settings.GOOGLE_GEOCODER_API_KEY)
