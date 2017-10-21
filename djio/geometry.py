#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Working with geometries?  Need help?  Here it is!
"""

from abc import ABCMeta, abstractmethod, abstractstaticmethod
from enum import Enum
from osgeo import ogr
from geoalchemy2.types import WKBElement, WKTElement
from geoalchemy2.shape import to_shape as to_shapely
from geoalchemy2.shape import from_shape as from_shapely
import re
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Point as ShapelyPoint, LineString, LinearRing, Polygon as ShapelyPolygon
from shapely.wkb import dumps as dumps_wkb
from shapely.wkb import loads as loads_wkb
from shapely.wkt import dumps as dumps_wkt
from shapely.wkt import loads as loads_wkt
from typing import Dict, Callable, Type


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

_shapely_geom_type_map: Dict[str, GeometryType] = {
    'point': GeometryType.POINT,
    'linestring': GeometryType.POLYLINE,
    'linearring': GeometryType.POLYLINE,
    'polygon' : GeometryType.POLYGON
}  #: maps Shapely geometry types to djio geometry types


_geometry_factory_functions: Dict[GeometryType, Callable[[BaseGeometry, int], 'Geometry']] = {

}  #: a hash of GeometryTypes to functions that can create that type from a base geometry


class Geometry(object):
    """
    This is the common base class for all of the geometry types.
    """
    __metaclass__ = ABCMeta

    # This is a regex that matches an EWKT string, capturing the spatial reference ID (SRID) in a group called 'srid'
    # and the rest of the well-known text (WKT) in a group called 'wkt'.
    _ewkt_re = re.compile(
        r"srid=(?P<srid>\d+)\s*;\s*(?P<wkt>.*)",
        flags=re.IGNORECASE)  #: a regex that matches extended WKT (EWKT)

    def __init__(self,
                 shapely: BaseGeometry,
                 spatial_reference: SpatialReference or int=None):
        """

        :param shapely: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        # Keep that reference to the Shapely geometry.
        self._shapely: BaseGeometry = shapely
        # Let's figure out what the spatial reference is.  (It might be an instance of SpatialReference, or it might
        # be the SRID.)
        self._spatial_reference: SpatialReference = (spatial_reference
                                                     if isinstance(spatial_reference, SpatialReference)
                                                     else SpatialReference(srid=spatial_reference))

    @property
    def geometry_type(self) -> GeometryType:
        try:
            return _shapely_geom_type_map[self._shapely.geom_type.lower()]
        except KeyError:
            return GeometryType.UNKNOWN

    @property
    def shapely(self) -> BaseGeometry:
        """
        Get the Shapely geometry underlying this geometry object.

        :return: the Shapely geometry
        """
        return self._shapely

    @staticmethod
    def from_shapely(shapely: BaseGeometry,
                     srid: int) -> 'Geometry':
        # Get Shapely's version of the geometry type.  (Note that the keys in the dictionary are all lower-cased.)
        geometry_type: GeometryType = _shapely_geom_type_map[shapely.geom_type.lower()]
        # With this information, we can use the registered function to create the djio geometry.
        return _geometry_factory_functions[geometry_type](shapely, srid)

    @staticmethod
    def from_ogr(ogr_geom: ogr.Geometry, srid: int=None) -> 'Geometry':
        # Grab the SRID from the arguments.
        _srid = srid
        # If the caller didn't provide one...
        if _srid is None:
            # ...dig it out of the geometry's spatial reference.
            ogr_srs: ogr.osr.SpatialReference = ogr_geom.GetSpatialReference()
            # Now, if the geometry didn't bring it's own spatial reference, we have a problem
            if ogr_srs is None:
                raise GeometryException('The geometry has no spatial reference, and no SRID was supplied.')
            _srid = int(ogr_srs.GetAttrValue('AUTHORITY', 1))
        return Geometry.from_wkb(wkb=ogr_geom.ExportToWkb(), srid=_srid)

    @staticmethod
    def from_ewkt(ewkt: str) -> 'Geometry':
        """
        Create a geometry from EWKT, a PostGIS-specifc format that includes the spatial reference system identifier an
        up to four (4) ordinate values (XYZM).  For example: SRID=4326;POINT(-44.3 60.1) to locate a longitude/latitude
        coordinate using the WGS 84 reference coordinate system.

        :param ewkt: the extended well-known text (EWKT)
        :return: the geometry
        """
        # Let's see if we can match the format so we can separate the SRID from the rest of the WKT.
        ewkt_match = Geometry._ewkt_re.search(ewkt)
        if not ewkt_match:
            raise GeometryException('The EWKT is not properly formatted.')  # TODO: Add more information?
        # We have a match!  Let's go get the pieces.
        srid = int(ewkt_match.group('srid'))  # Grab the SRID.
        wkt = ewkt_match.group('wkt')  # Get the WKT.
        # Now we have enough information to create a Shapely geometry plus the SRID, so...
        return Geometry.from_wkt(wkt=wkt, srid=srid)

    @staticmethod
    def from_wkt(wkt: str, srid: int) -> 'Geometry':
        shapely = loads_wkt(wkt)
        return Geometry.from_shapely(shapely=shapely, srid=srid)

    @staticmethod
    def from_wkb(wkb: str, srid: int) -> 'Geometry':
        # https://geoalchemy-2.readthedocs.io/en/0.2.6/_modules/geoalchemy2/shape.html#to_shape
        shapely = loads_wkb(wkb)
        return Geometry.from_shapely(shapely=shapely, srid=srid)

    @staticmethod
    def from_gml(gml: str) -> 'Geometry':
        raise NotImplementedError('Coming soon...')

    @staticmethod
    def from_geoalchemy2(spatial_element: WKBElement or WKTElement,
                         srid: int) -> 'Geometry':
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
    """
    In modern mathematics, a point refers usually to an element of some set called a space.  More specifically, in
    Euclidean geometry, a point is a primitive notion upon which the geometry is built, meaning that a point cannot be
    defined in terms of previously defined objects. That is, a point is defined only by some properties, called axioms,
    that it must satisfy. In particular, the geometric points do not have any length, area, volume or any other
    dimensional attribute. A common interpretation is that the concept of a point is meant to capture the notion of a
    unique location in Euclidean space.
    """
    def __init__(self,
                 shapely: ShapelyPoint,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POINT`
        """
        return GeometryType.POINT

    @property
    def x(self) -> float:
        """
        Get the X coordinate.

        :return: the X coordinate
        """
        # noinspection PyUnresolvedReferences
        return self._shapely.x

    @property
    def y(self) -> float:
        """
        Get the Y coordinate.

        :return: the Y coordinate
        """
        # noinspection PyUnresolvedReferences
        return self._shapely.y

    # TODO: Start adding Point-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POINT, Point)


class Polyline(Geometry):
    """
    In geometry, a polygonal chain is a connected series of line segments. More formally, a polygonal chain P is a curve
    specified by a sequence of points (A1 , A2, ... , An ) called its vertices. The curve itself consists of the line
    segments connecting the consecutive vertices. A polygonal chain may also be called a polygonal curve, polygonal
    path,  polyline,  piecewise linear curve, broken line or, in geographic information systems (that's us), a
    linestring or linear ring.
    """
    def __init__(self,
                 shapely: LineString or LinearRing,
                 spatial_reference: SpatialReference or int = None):
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POLYLINE`
        """
        return GeometryType.POLYLINE

    # TODO: Start adding Polyline-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYLINE, Polyline)


class Polygon(Geometry):
    """
    In elementary geometry, a polygon is a plane figure that is bounded by a finite chain of straight line segments
    closing in a loop to form a closed polygonal chain or circuit. These segments are called its edges or sides, and the
    points where two edges meet are the polygon's vertices (singular: vertex) or corners. The interior of the polygon is
    sometimes called its body.
    """
    def __init__(self,
                 shapely: ShapelyPolygon,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POLYGON`
        """
        return GeometryType.POLYGON

    # TODO: Start adding Polygon-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYGON, Polygon)






