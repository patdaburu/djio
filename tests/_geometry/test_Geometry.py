#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""


import pytest
import unittest
from djio.geometry import Geometry, GeometryType, Point
import shapely.geometry.point


class TestGeometrySuite(unittest.TestCase):

    class TestGeometry(Geometry):
        """
        This is a test subclass that allows us to explicitly abstract members of Geometry directly.
        """
        def __init__(self):
            super().__init__(
                shapely_geometry=shapely.geometry.point.Point(1.0, -1.0),
                spatial_reference=4326
            )

        @property
        def geometry_type(self):
            return super().geometry_type

        @property
        def dimensions(self):
            return super().dimensions

        def get_point_tuples(self):
            return super().get_point_tuples()

        def iter_coords(self):
            return super().iter_coords()

        def flip_coordinates(self):
            return super().iter_coords()

    def test_init_geometryType_returnsGeometryImpl(self):
        test_geom = TestGeometrySuite.TestGeometry()
        self.assertEqual(test_geom.geometry_type, GeometryType.POINT)

    def test_init_dimensions_returnsGeometryImpl(self):
        test_geom = TestGeometrySuite.TestGeometry()
        self.assertEqual(0, test_geom.dimensions)  # once to create and cache the answer
        self.assertEqual(0, test_geom.dimensions)  # and again to hit the cache

    def test_init_dimensions_raisesNotImplementedError(self):
        test_geom = TestGeometrySuite.TestGeometry()
        with pytest.raises(NotImplementedError):
            test_geom.get_point_tuples()

    def test_init_iterCoords_raisesNotImplementedError(self):
        test_geom = TestGeometrySuite.TestGeometry()
        with pytest.raises(NotImplementedError):
            test_geom.iter_coords()

    def test_init_flipCoords_raisesNotImplementedError(self):
        test_geom = TestGeometrySuite.TestGeometry()
        with pytest.raises(NotImplementedError):
            test_geom.flip_coordinates()








