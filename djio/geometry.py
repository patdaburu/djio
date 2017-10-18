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

    #_ogr_srs_cache: Dict[int, ogr.osr.SpatialReference] = {}  #: a cache of OGR spatial references that we've created
    _instances = {}

    def __init__(self, srid: int):
        """

        :param srid: the well-known spatial reference ID
        """
        self._srid: int = srid  #: the spatial reference well-known ID
        # Keep a handy reference to OGR spatial reference.
        self._ogr_srs = self._get_ogr_srs(self._srid)

    def __new__(cls, srid: int):
        if srid in SpatialReference._instances:
            return SpatialReference._instances[srid]
        else:
            new_sr = super(SpatialReference, cls).__new__(cls)
            SpatialReference._instances[srid] = new_sr
            return new_sr

    @property
    def srid(self) -> int:
        """
        Get the spatial reference's well-known ID (srid).

        :return: the well-known spatial reference ID
        """
        return self._srid

    @staticmethod
    def _get_ogr_srs(srid: int) -> ogr.osr.SpatialReference:
        """
        Get an OGR spatial reference from its spatial reference ID (srid).

        :param srid: the spatial reference ID
        :return: the OGR spatial reference.
        """
        # Create the OGR spatial reference.
        ogr_srs = ogr.osr.SpatialReference()
        # Let's assume the SRID is defined by the EPSG.
        # (Note: If we need to support others, this is the place to do it.)
        ogr_srs.ImportFromEPSG(srid)
        # That's that.
        return ogr_srs


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


