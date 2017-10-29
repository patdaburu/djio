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
        #print(sr._ogr_srs.GetLinearUnits())
        #print(sr._ogr_srs.GetLinearUnitsName())
        #print(sr._ogr_srs.GetUTMZone())
        ##print("3857 geographic ", sr._ogr_srs.IsGeographic())
        ##print("3857 projected ", sr._ogr_srs.IsProjected())


    def test_new_verifySrToInstance(self):
        sr1 = SpatialReference(srid=3857)
        sr2 = SpatialReference(srid=3857)
        self.assertTrue(sr1 == sr2)
        sr3 = SpatialReference(srid=4326)
        self.assertFalse(sr1 == sr3)
        #print("4326 geographic ", sr3._ogr_srs.IsGeographic())
        #print("4326 progjected ", sr3._ogr_srs.IsProjected())
        #print(sr3._ogr_srs.GetLinearUnitsName())