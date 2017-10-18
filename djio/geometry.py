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
from geoalchemy2.elements import WKBElement


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


class Geometry(object):
    """
    This is the common base class for all of the geometry types.
    """
    __metaclass__ = ABCMeta

    def __init__(self,
                 ogr_geometry: ogr.Geometry,
                 spatial_reference: SpatialReference or int=None):
        self._ogr_geometry: ogr.Geometry = ogr_geometry
        # Let's figure out what the spatial reference is.  (It might be an instance of SpatialReference, or it might
        # be the SRID.)
        self._spatial_reference: SpatialReference = (spatial_reference
                                                     if isinstance(spatial_reference, SpatialReference)
                                                     else SpatialReference(srid=spatial_reference))

    @staticmethod
    def from_ogr_geometry(ogr_geom: ogr.Geometry):
        pass

    @staticmethod
    def from_wkt(wkt: str):
        pass

    @staticmethod
    def from_wkb(wkb: object):
        pass

    @staticmethod
    def from_wkbelement(wkbelement: WKBElement):
        # 1. get the WKB.
        # 2. get the SRID.
        # 3. create the OGR geometry
        # 4. call from_ogr_geometry()
        pass


