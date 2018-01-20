#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_Point
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.hashing import int_to_bytes, bytes_to_int


class TestGeometrySuite(unittest.TestCase):

    def test_convertIntToBytes(self):
        for i in range(0, 999999):
            #print("i={i}".format(i=i))
            b = int_to_bytes(i, width=4)
            #print("b={b}".format(b=b))
            i2 = bytes_to_int(b)
            #print("i2={i2}".format(i2=i2))
            #print('-' * 20)
            self.assertEqual(i, i2)
