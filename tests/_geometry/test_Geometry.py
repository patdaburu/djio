#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Provide a brief description of the module.
"""

import unittest
from djio.geometry import Geometry, GeometryType, Point
from osgeo import ogr

class TestGeometrySuite(unittest.TestCase):

    _wgs84: ogr.osr.SpatialReference = ogr.osr.SpatialReference()
    _wgs84.ImportFromEPSG(4326)

    def test_pointFromWkt_verify(self):
        point: Point = Geometry.from_wkt(wkt='POINT(-94.1 46.5)', srid=4326)
        self.assertEqual(GeometryType.POINT, point.geometry_type)
        self.assertEqual(-94.1, point.x)
        self.assertEqual(46.5, point.y)

    def test_pointFromOgr_verify(self):
        ogr_point = ogr.Geometry(ogr.wkbPoint)
        ogr_point.AddPoint(-94.1, 46.5)
        point: Point = Geometry.from_ogr(ogr_geom=ogr_point, srid=4326)
        self.assertEqual(GeometryType.POINT, point.geometry_type)
        self.assertEqual(-94.1, point.x)
        self.assertEqual(46.5, point.y)

    def test_flipCoordinates_verify(self):
        p = Point.from_coordinates(x=100.1, y=200.2, srid=3857)
        self.assertEqual(100.1, p.x)
        self.assertEqual(200.2, p.y)
        q = p.flip_coordinates()
        self.assertEqual(200.2, q.x)
        self.assertEqual(100.1, q.y)

    def test_pointToGml_verify(self):
        p = Point.from_coordinates(x=91.5, y=-46.1, srid=4326)
        self.assertEqual(
            """<gml:Point srsName="urn:ogc:def:crs:EPSG::4326"><gml:pos>-46.1 91.5</gml:pos></gml:Point>""",
            p.to_gml(version=3)
        )
        self.assertEqual(
            """<gml:Point srsName="EPSG:4326"><gml:coordinates>91.5,-46.1</gml:coordinates></gml:Point>""",
            p.to_gml(version=2)
        )



