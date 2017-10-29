#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_SpatialReference
.. moduleauthor:: Pat Daburu <pat@daburu.net>
"""

import unittest
from djio.geometry import SpatialReference


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
