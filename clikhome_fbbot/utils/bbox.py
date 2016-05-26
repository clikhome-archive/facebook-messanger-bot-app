# -*- coding: utf-8 -*-
from __future__ import absolute_import


class Bbox(object):

    def __init__(self, *args, **kwargs):
        assert args or kwargs and not (args and kwargs)
        if args:
            # bbox = (sw_lng, sw_lat, ne_lng, ne_lat)
            self.sw_lng = args[0]
            self.sw_lat = args[1]
            self.ne_lng = args[2]
            self.ne_lat = args[3]
        elif kwargs:
            self.sw_lng = kwargs.pop('sw_lng')
            self.sw_lat = kwargs.pop('sw_lat')
            self.ne_lng = kwargs.pop('ne_lng')
            self.ne_lat = kwargs.pop('ne_lat')
            self.formatted_address = kwargs.pop('formatted_address', None)

    @property
    def as_list(self):
        return self.sw_lng, self.sw_lat, self.ne_lng, self.ne_lat

    @property
    def as_dict(self):
        return {
            'ne_lat': self.ne_lat,
            'ne_lng': self.ne_lng,
            'sw_lat': self.sw_lat,
            'sw_lng': self.sw_lng,
        }

    def to_geom(self):
        from django.contrib.gis.geos import Polygon
        return Polygon.from_bbox(self.as_list)

    def __str__(self):
        if not self.formatted_address:
            return '%r' % self.as_dict
        else:
            return '"%s", %r' % (self.formatted_address, self.as_dict)
