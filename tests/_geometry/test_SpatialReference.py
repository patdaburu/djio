#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_SpatialReference
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""

import pytest
import unittest
from djio.geometry import SpatialReference, SpatialReferenceException


class TestSpatialReferenceSuite(unittest.TestCase):

    def test_new_verifySrid(self):
        sr = SpatialReference(3857)
        self.assertEqual(3857, sr.srid)

    def test_new_verifyIsMetric(self):
        sr = SpatialReference(3857)
        self.assertTrue(sr.is_metric)

    def test_new_verifyIsNotMetric(self):
        sr = SpatialReference(4326)
        self.assertFalse(sr.is_metric)

    def test_new_verifySrToInstance(self):
        sr1 = SpatialReference(srid=3857)
        sr2 = SpatialReference(srid=3857)
        self.assertTrue(sr1 == sr2)
        sr3 = SpatialReference(srid=4326)
        self.assertFalse(sr1 == sr3)

    def test_new_isGeograhic(self):
        sr1 = SpatialReference(srid=3857)
        self.assertFalse(sr1.is_geographic)
        sr2 = SpatialReference(srid=4326)
        self.assertTrue(sr2.is_geographic)

    def test_new_isProjected(self):
        sr1 = SpatialReference(srid=3857)
        self.assertTrue(sr1.is_projected)
        sr2 = SpatialReference(srid=4326)
        self.assertFalse(sr2.is_projected)

    def test_new_isMetric(self):
        sr1 = SpatialReference(srid=3857)
        self.assertTrue(sr1.is_metric)
        sr2 = SpatialReference(srid=4326)
        self.assertFalse(sr2.is_metric)

    def test_initTwice_firstIsSameAsSecond(self):
        sr1 = SpatialReference(srid=3857)
        sr2 = SpatialReference(srid=3857)
        self.assertTrue(sr1.is_same_as(sr2))
        sr3 = SpatialReference(srid=4326)

    def test_initTwo_firstIsNotSameAsSecond(self):
        sr1 = SpatialReference(srid=3857)
        sr2 = SpatialReference(srid=4326)
        self.assertFalse(sr1.is_same_as(sr2))

    def test_getUtmForUnsupportedZone_raisesSpatialReferenceException(self):
        with pytest.raises(SpatialReferenceException):
            SpatialReference.get_utm_for_zone(45)  # a non-existent UTM zone

    def test_getUtmFromLongitude_continentalUS(self):
        lon_and_utm = {
            -69.609375: 19,
            -71.235352: 19,
            -73.432617: 18,
            -76.464844: 18,
            -79.365234: 17,
            -79.892578: 17,
            -88.769531: 16,
            -87.714844: 16,
            -93.955078: 15,
            -92.460938: 15,
            -97.998047: 14,
            -96.416016: 14,
            -102.392578: 13,
            -106.083984: 13,
            -108.017578: 12,
            -109.335938: 12,
            -116.279297: 11,
            -114.257813: 11,
            -122.080078: 10,
            -121.289063: 10
        }
        for lon in lon_and_utm.keys():
            utm_sr = SpatialReference.get_utm_from_longitude(lon)
            self.assertEqual(
                utm_sr.srid,
                int('269{utm}'.format(utm=lon_and_utm[lon])))





