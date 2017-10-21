#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Provide a brief description of the module.
"""

import unittest
from djio.geometry import Geometry, GeometryType, Point

class TestGeometrySuite(unittest.TestCase):

    def test_pointFromWkt_verify(self):
        point: Point = Geometry.from_wkt(wkt='POINT(-94.1 46.5)', srid=4326)
        self.assertEqual(GeometryType.POINT, point.geometry_type)
        self.assertEqual(-94.1, point.x)
        self.assertEqual(46.5, point.y)

