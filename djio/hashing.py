#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Need to know at a glance if two geometries are the same?
"""

from typing import Iterable, Tuple

# https://www.w3resource.com/python/python-bytes.php

def int_to_bytes(i: int, width: int):
    """
    Convert an integer to a fixed-width byte array.

    :param i: the integer
    :param width: the number of bytes in the array
    :return: the byte array
    """
    i_array = [0] * width
    mask = 255
    for idx in range(0, width):
        _idx = width - idx - 1
        _mask = mask << (_idx * 8)
        i_array[idx] = (i & _mask) >> (_idx * 8)
    return bytes(i_array)


def bytes_to_int(b: bytes):
    """
    Convert a byte array to an integer.

    :param b: the byte array
    :return: the integer
    """
    i = 0
    width = len(b)
    for idx in range(0, width):
        i_at_idx = b[idx] << (width - idx - 1) * 8
        i = i + i_at_idx
    return i



def djiohash_v1(geometry_type_code: int,
                srid: int,
                coordinates: Iterable[Tuple[float, float] or Tuple[float, float, float]]):
    # The first byte will hold the geometry type in the highest 4 bits of the first byte.
    # ☐☐☐☐0000
    b1_geometry_type = geometry_type_code << 4
    # The next bit tells us whether or not the geometry is a collection.
    # 0000☐000
    b1_is_collection = 0 << 3  # TODO: Revisit this when collections are implemented.
    # The next bit tells us whether or not this geometry has 3D coordinates (i.e. "M" values).
    # 00000☐00
    b1_has_m_values = 0 << 2  # TODO: Revisit this when we can determine this.
    # The last two bits in this byte are presently available.
    # 000000☐☐ <-- These are available.
    b1 = b1_geometry_type & b1_is_collection & b1_has_m_values

    # Bytes 2-4 describe the SRID.
    b2_4 = int_to_bytes(srid, width=3)






