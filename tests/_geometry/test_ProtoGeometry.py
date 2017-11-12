#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.geometry import Geometry, ProtoGeometry, PointTuple, Polyline, Point, LatLonTuple


class TestProtoGeometrySuite(unittest.TestCase):

    def test_init_add_toPolyline(self):
        # Create the proto-geometry.  When it's time comes, it'll be projected to UTM zone 15.
        proto: ProtoGeometry = ProtoGeometry(spatial_reference=26915)
        # Add a lat/lon.
        proto.add(LatLonTuple(latitude=46.5, longitude=-94.1))
        # Add a Point in the adjacent UTM zone.
        proto.add(Point.from_coordinates(x=492326.81, y=5149608.22, spatial_reference=26916))
        # Add a web-mercator point as a PointTuple.
        proto.add(PointTuple(-10475164.0836, y=5700582.7324, z=0.0, srid=3857))
        # Tell the proto-geometry to give us a Polyline.
        p: Polyline = proto.to_polyline()
        # There you go.
        self.assertEqual(
            '<gml:LineString srsName="urn:ogc:def:crs:EPSG::26915"><gml:posList>415595.186865569 5150191.11554508 ' + \
            '952676.147829255 5166538.99156226 414060.603356157 5039084.94282137</gml:posList></gml:LineString>',
            p.to_gml()
        )

    def test_init_add_toPolygon(self):
        # Create the proto-geometry.  When it's time comes, it'll be projected to UTM zone 15.
        proto: ProtoGeometry = ProtoGeometry(spatial_reference=26915)
        # Add a lat/lon.
        proto.add(LatLonTuple(latitude=46.5, longitude=-94.1))
        # Add a Point in the adjacent UTM zone.
        proto.add(Point.from_coordinates(x=492326.81, y=5149608.22, spatial_reference=26916))
        # Add a web-mercator point as a PointTuple.
        proto.add(PointTuple(-10475164.0836, y=5700582.7324, z=0.0, srid=3857))
        # Tell the proto-geometry to give us a Polygon.
        p: Polyline = proto.to_polygon()
        # There you go.
        self.assertEqual(
            '<gml:Polygon srsName="urn:ogc:def:crs:EPSG::26915"><gml:exterior><gml:LinearRing><gml:posList>' + \
            '415595.186865569 5150191.11554508 952676.147829255 5166538.99156226 414060.603356157 5039084.94282137' +
            ' 415595.186865569 5150191.11554508</gml:posList></gml:LinearRing></gml:exterior></gml:Polygon>',
            p.to_gml()
        )