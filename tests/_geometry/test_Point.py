#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.geometry import Geometry, GeometryType, Point
from osgeo import ogr


class TestPointSuite(unittest.TestCase):

    def test_pointFromWkt_verify(self):
        point: Point = Geometry.from_wkt(wkt='POINT(-94.1 46.5)', spatial_reference=4326)
        self.assertEqual(GeometryType.POINT, point.geometry_type)
        self.assertEqual(-94.1, point.x)
        self.assertEqual(46.5, point.y)

    def test_pointFromOgr_verify(self):
        ogr_point = ogr.Geometry(ogr.wkbPoint)
        ogr_point.AddPoint(-94.1, 46.5)
        point: Point = Geometry.from_ogr(ogr_geom=ogr_point, spatial_reference=4326)
        self.assertEqual(GeometryType.POINT, point.geometry_type)
        self.assertEqual(-94.1, point.x)
        self.assertEqual(46.5, point.y)

    def test_flipCoordinates_verify(self):
        p = Point.from_coordinates(x=100.1, y=200.2, spatial_reference=3857)
        self.assertEqual(100.1, p.x)
        self.assertEqual(200.2, p.y)
        q = p.flip_coordinates()
        self.assertEqual(200.2, q.x)
        self.assertEqual(100.1, q.y)

    def test_pointToGml_verify(self):
        p = Point.from_coordinates(x=91.5, y=-46.1, spatial_reference=4326)
        self.assertEqual(
            """<gml:Point srsName="EPSG:4326"><gml:coordinates>91.5,-46.1</gml:coordinates></gml:Point>""",
            p.to_gml(version=2)
        )
        self.assertEqual(
            """<gml:Point srsName="urn:ogc:def:crs:EPSG::4326"><gml:pos>-46.1 91.5</gml:pos></gml:Point>""",
            p.to_gml(version=3)
        )

    def test_transform_verifyTargetSrid(self):
        p = Point.from_coordinates(x=91.5, y=-46.1, spatial_reference=4326)
        q = p.transform(spatial_reference=3857)
        self.assertEqual(3857, q.spatial_reference.srid)

    def test_transformToUtm_verifyTargetSrid(self):
        p = Point.from_lat_lon(latitude=41.885921, longitude=-82.968750)
        q = p.transform_to_utm()
        self.assertEqual(26917, q.spatial_reference.srid)

    def test_project_verify(self):
        p1: Point = Geometry.from_wkt(wkt='POINT(-94.1 46.5)', spatial_reference=4326)
        p2: Point = p1.project()
        self.assertEqual(26915, p2.spatial_reference.srid)

    def test_toPointTuple_verify(self):
        p = Point.from_coordinates(x=91.5, y=-46.1, z=1.0,
                                   spatial_reference=4326)
        p_tuple = p.to_point_tuple()
        self.assertEqual(91.5, p_tuple.x)
        self.assertEqual(-46.1, p_tuple.y)
        self.assertEqual(1.0, p_tuple.z)
        self.assertEqual(4326, p_tuple.srid)
        # Create another tuple to make sure that we get the cached instance.
        p_tuple_2 = p.to_point_tuple()
        self.assertTrue(p_tuple_2 == p_tuple)

    def test_pthash(self):  # TODO: Put this test elsewhere!
        p = Point.from_coordinates(x=91.5, y=-46.1, z=1.0,
                                   spatial_reference=4326)
        h = p.djiohash()
        print(h)