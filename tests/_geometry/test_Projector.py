#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Projector
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.geometry import Geometry, GeometryType, Point, Projector


class TestProjectorSuite(unittest.TestCase):

    projector = Projector()

    def test_project_verify(self):
        p1: Point = Geometry.from_wkt(wkt='POINT(-94.1 46.5)', spatial_reference=4326)
        p2: Point = self.projector.project(geometry=p1)
        self.assertEqual(26915, p2.spatial_reference.srid)