#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_djioHashV1
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.geometry import Point


class TestGeometrySuite(unittest.TestCase):

    def test_hash_point(self):  # TODO: Put this test elsewhere!
        # TODO: This is a smoke test.
        p1 = Point.from_coordinates(x=91.5, y=-46.1, z=1.0,
                                    spatial_reference=4326)
        h1 = p1.djiohash()
        print(h1)
        p2 = Point.from_coordinates(x=91.5, y=-46.1, z=1.0,
                                    spatial_reference=4326)
        h2 = p2.djiohash()
        print(h2)
        p3 = Point.from_coordinates(x=91.6, y=-46.1, z=1.0,
                                    spatial_reference=4326)
        h3 = p3.djiohash()
        print(h3)
        p4 = Point.from_coordinates(x=-46.1, y=91.6, z=1.0,
                                    spatial_reference=4326)
        h4 = p4.djiohash()
        print(h4)
        p5 = Point.from_coordinates(x=91.5, y=-46.1,
                                    spatial_reference=4326)
        h5 = p5.djiohash()
        print(h5)
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)
        self.assertNotEqual(h1, h4)
        self.assertNotEqual(h1, h5)