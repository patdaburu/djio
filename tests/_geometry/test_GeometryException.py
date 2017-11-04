#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.geometry import GeometryException


class TestGeometryExceptionSuite(unittest.TestCase):

    def test_initWithoutInner_verify(self):
        ge = GeometryException(message='Test Message')
        self.assertEqual('Test Message', ge.message)
        self.assertIsNone(ge.inner)

    def test_initWithInner_verify(self):
        inner = Exception()
        ge = GeometryException(message='Test Message',
                               inner=inner)
        self.assertEqual('Test Message', ge.message)
        self.assertTrue(ge.inner == inner)
