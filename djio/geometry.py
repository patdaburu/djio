#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Working with geometries?  Need help?  Here it is!
"""

from abc import ABCMeta, abstractmethod
from enum import Enum
from osgeo import ogr
from geoalchemy2.types import WKBElement, WKTElement
from geoalchemy2.shape import to_shape as to_shapely
from geoalchemy2.shape import from_shape as from_shapely
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Point as ShapelyPoint, LineString, LinearRing, Polygon as ShapelyPolygon
from shapely.wkb import dumps as dumps_wkb
from shapely.wkb import loads as loads_wkb
from shapely.wkt import dumps as dumps_wkt
from shapely.wkt import loads as loads_wkt
from typing import Dict, Callable


class GeometryException(Exception):
    """
    Raised when something goes wrong with a geometry.
    """
    def __init__(self, message: str, inner: Exception=None):
        """

        :param message: the exception message
        :param inner: the exception that caused this exception
        """
        super().__init__(message)
        self._inner = inner

    @property
    def inner(self) -> Exception:
        """
        Get the inner exception that caused this exception.
        """
        return self._inner


class LateralSides(Enum):
    """
    This is a simple enumeration that identifies the lateral side of line (left or right).
    """
    LEFT = 'left'    #: the left side of the line
    RIGHT = 'right'  #: the right side of the line


class SpatialReference(object):
    """
    A spatial reference system (SRS) or coordinate reference system (CRS) is a coordinate-based local, regional or
    global system used to locate geographical entities. A spatial reference system defines a specific map projection,
    as well as transformations between different spatial reference systems.

    :seealso: https://en.wikipedia.org/wiki/Spatial_reference_system
    """
    _instances = {}  #: the instances of spatial reference that have been created

    def __init__(self, srid: int):
        """

        :param srid: the well-known spatial reference ID
        """
        # To coordinate __init__ with __new__, we're using a flag attribute that indicates to this instance that
        # even if __init__ is being called a second time, there's nothing more to do.
        if not hasattr(self, '_init'):
            self._init = True  # Mark this instance as "initialized".
            self._srid: int = srid  #: the spatial reference well-known ID
            # Keep a handy reference to OGR spatial reference.
            self._ogr_srs = self._get_ogr_sr(self._srid)

    def __new__(cls, srid: int):
        # If this spatial reference has already been created...
        if srid in SpatialReference._instances:
            # ...use the current instance.
            return SpatialReference._instances[srid]
        else:  # Otherwise, create a new instance.
            new_sr = super(SpatialReference, cls).__new__(cls)
            # Save it in the cache.
            SpatialReference._instances[srid] = new_sr
            # That's that.
            return new_sr

    @property
    def srid(self) -> int:
        """
        Get the spatial reference's well-known ID (srid).

        :return: the well-known spatial reference ID
        """
        return self._srid

    @staticmethod
    def _get_ogr_sr(srid: int) -> ogr.osr.SpatialReference:
        """
        Get an OGR spatial reference from its spatial reference ID (srid).

        :param srid: the spatial reference ID
        :return: the OGR spatial reference.
        """
        # Create the OGR spatial reference.
        ogr_sr = ogr.osr.SpatialReference()
        # Let's assume the SRID is defined by the EPSG.
        # (Note: If we need to support others, this is the place to do it.)
        ogr_sr.ImportFromEPSG(srid)
        # That's that.
        return ogr_sr


class GeometryType(Enum):
    """
    These are the supported geometric data types.
    """
    UNKNOWN: int = 0   #: The geometry type is unknown.
    POINT: int = 1     #: a point geometry
    POLYLINE: int = 2  #: a polyline geometry
    POLYGON: int = 3   #: a polygon geometry


_geometry_factory_functions = {}  #: a hash of GeometryTypes to functions that can create that type from a base geometry


class Geometry(object):
    """
    This is the common base class for all of the geometry types.
    """
    __metaclass__ = ABCMeta

    def __init__(self,
                 shapely: BaseGeometry,
                 spatial_reference: SpatialReference or int=None):
        # Keep that reference to the Shapely geometry.
        self._shapely: BaseGeometry = shapely
        # Let's figure out what the spatial reference is.  (It might be an instance of SpatialReference, or it might
        # be the SRID.)
        self._spatial_reference: SpatialReference = (spatial_reference
                                                     if isinstance(spatial_reference, SpatialReference)
                                                     else SpatialReference(srid=spatial_reference))

    @staticmethod
    def from_shapely(shapely: BaseGeometry,
                     srid: int):
        # Return the specific type based on the type of the base geometry.
        pass

    @staticmethod
    def from_ogr(ogr_geom: ogr.Geometry):
        pass

    @staticmethod
    def from_ewkt(ewkt: str):
        pass;

    @staticmethod
    def from_wkt(wkt: str, srid: int):
        shapely = loads_wkt(wkt)
        return Geometry.from_shapely(shapely)

    @staticmethod
    def from_wkb(wkb: str):
        # https://geoalchemy-2.readthedocs.io/en/0.2.6/_modules/geoalchemy2/shape.html#to_shape
        shapely = loads_wkb(wkb)
        return Geometry.from_shapely(shapely)

    @staticmethod
    def from_gml(gml: str):
        pass

    @staticmethod
    def from_geoalchemy2(spatial_element: WKBElement or WKTElement,
                         srid: int):
        shapely = to_shapely(spatial_element)
        return Geometry.from_shapely(shapely=shapely, srid=srid)


def _register_geometry_factory(geometry_type: GeometryType, factory_function: Callable[[BaseGeometry, int], Geometry]):
    """
    Register a geometry factory function.

    :param geometry_type: the enumerated geometry type
    :param factory_function: the factory function
    """
    _geometry_factory_functions[geometry_type] = factory_function


class Point(Geometry):
    def __init__(self,
                 shapely: ShapelyPoint,
                 spatial_reference: SpatialReference or int = None):
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    # TODO: Start adding Point-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POINT, Point)


class Polyline(Geometry):
    def __init__(self,
                 shapely: LineString or LinearRing,
                 spatial_reference: SpatialReference or int = None):
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    # TODO: Start adding Polyline-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYLINE, Polyline)


class Polygon(Geometry):
    def __init__(self,
                 shapely: ShapelyPolygon,
                 spatial_reference: SpatialReference or int = None):
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    # TODO: Start adding Polygon-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYLINE, Polygon)






