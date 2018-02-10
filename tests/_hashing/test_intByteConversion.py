#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_intByteConversion
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a unit test module.
"""

import unittest
from djio.hashing import int_to_bytes, bytes_to_int


class TestGeometrySuite(unittest.TestCase):

    def test_convertNegativeIntToBytes(self):
        # Let's check every single integer -99,999 to 0.
        for i in range(-99999,0):
            #print("i={i}".format(i=i))
            b = int_to_bytes(i, width=3)
            #print("b={b}".format(b=b))
            i2 = bytes_to_int(b)
            #print("i2={i2}".format(i2=i2))
            #print('-' * 20)
            self.assertEqual(i, i2)
        # Now let's spot check big negative numbers.
        for i in range(9999999, 99999, 48):
            b = int_to_bytes(i, width=4)  # This will require more bytes.
            i2 = bytes_to_int(b)
            self.assertEqual(i, i2)


    def test_convertIntToBytes(self):
        # Let's check every single integer from 0 to just under 100,000.
        for i in range(0, 99999):
            #print("i={i}".format(i=i))
            b = int_to_bytes(i, width=3)
            #print("b={b}".format(b=b))
            i2 = bytes_to_int(b)
            #print("i2={i2}".format(i2=i2))
            #print('-' * 20)
            self.assertEqual(i, i2)
        # Now let's spot check big numbers.
        for i in range(99999, 9999999, 48):
            b = int_to_bytes(i, width=4)  # This will require more bytes.
            i2 = bytes_to_int(b)
            self.assertEqual(i, i2)

