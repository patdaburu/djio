#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Need to know at a glance if two geometries are the same?
"""

import math
from typing import Iterable, Tuple

# https://www.w3resource.com/python/python-bytes.php


def int_to_bytes(i: int,
                 width: int,
                 unsigned: bool=False,
                 as_iterable: bool=False) -> bytearray or Iterable[int]:
    """
    Convert an integer to a fixed-width byte array.

    :param i: the integer
    :param width: the number of bytes in the array
    :param as_iterable: when `True` the function returns a list of byte-sized `int`s instead of a `bytearray`.
    :return: the byte array
    """
    # We'll start by working with the absolute value and sort out negatives later.
    _i = i if (unsigned or i >=0) else int(math.fabs(i))
    # Create a list to hold the bite-sized integers as we create them.
    bsis = [0] * width
    # We'll use a mask that spans eight bits (1 byte) which we'll shift in order to get only the bits in a given
    # byte's position.
    mask = 255
    # Let's get started...
    for idx in range(0, width):
        # We want the larger parts of the number to be "on the left", that is to say, in the lower orders of the
        # bsis array.  So as we go through this loop, the position to which we shift the mask will gradually move
        # from "left" (the higher-order bits) to "right" (the lower-order bits).
        shift = width - idx - 1
        # Shift the mask.
        _mask = mask << (shift * 8)
        # The value that goes into the
        bsis[idx] = (_i & _mask) >> (shift * 8)
    # Unless the caller indicated we don't need to worry about the sign, we have a little more work to do...
    if not unsigned:
        # If the original integer (i) was negative we'll flip on the highest-order bit (of the highest-order byte, which
        # is to say the one at index 0), otherwise we'll flip it off.
        bsis[0] = bsis[0] & 127 if i >= 0 else bsis[0] | 128
    # Return what we got.
    return bsis if as_iterable else bytes(bsis)


def bytes_to_int(b: bytes):
    """
    Convert a byte array to an integer.

    :param b: the byte array
    :return: the integer
    """
    neg = False  # Have we determined the value to be negative?  We'll see.
    i=0  # This is the variable in which we'll store the value.
    # Now we need to do some tap dancing to handle negative integers...
    # We can't directly modify the original bytearray, so let's create a new variable to reference it.
    _bytes = b
    # If we discover that the highest-order bit in the higest-order byte (which should be at index 0) is flipped on...
    if _bytes[0] >= 128:
        # ...we need to create a new list of bite-sized integers.
        _bytes = list(b)
        # Now we flip the higest-order bit off so processing below can continue without worrying about negatives...
        _bytes[0] = _bytes[0] & 127
        # ...but we'll make note that the final result *is* negative.
        neg = True
    # Now we need to know how many bytes (or byte-sized ints) we're dealing with.
    width = len(_bytes)
    # Let's go through them all, starting with the highest-order byte.
    for idx in range(0, width):
        # Since the higest-order bytes are in the lower indexes, we'll bit shift each value *fewer* positions to the
        # left as we move from lower index values to higher index values.
        i_at_idx = _bytes[idx] << (width - idx - 1) * 8  # (Shift it 8 bits, or 1 byte.)
        # Now we can just add it!
        i = i + i_at_idx
    # Return the number we have (or its negative twin).
    return i if not neg else i * -1



def calc_bytes_required(i: int):
    """
    Calculate the number of bytes required to hold an integer.
    :param places:
    :return:
    """
    return int(math.floor((math.log(i)) + 1) / 8)


_calc_bytes_for_decimal_places_cache = {}  # This is a cache used by the _calc_bytes_for_decimal_places function.


def _calc_bytes_for_decimal_places(places: int):
    if places in _calc_bytes_for_decimal_places_cache:
        return _calc_bytes_for_decimal_places_cache[places]
    else:
        # Calculate the bytes required for the largest number that can be held in this many decimal places.
        return calc_bytes_required(int('9' * places))


def float_to_bytes(f: float,
                   width: int,
                   precision: int = 4,
                   as_iterable: bool=False) -> bytearray or Iterable[int]:
    # First, let's figure out how many bytes will be needed to hold the precision portion of the floating point number.
    precision_width = _calc_bytes_for_decimal_places(precision)
    # Sanity Check:  The precision width cannot be greater than the total width.
    if precision_width > width:
        raise ValueError('The precision would require more than the total number of bytes.')
    # Get the integer part of the number (the "whole" part, a.k.a. the "characteristic").
    int_part = int(f)
    # Now let's get the fractional part (sometimes a.k.a. the "mantissa").
    frac_part = int(math.modf(f)[0] * math.pow(10, precision))
    # Convert the whole number to a list of byte-sized ints (bsi).
    bsis = int_to_bytes(int_part,
                        # The width we want here is the full width minus the part reserved for precision.
                        width=(width - precision_width),
                        as_iterable=True)
    # Add the fractional byte-sized ints to the list.
    bsis.extend(int_to_bytes(frac_part, width=precision_width, as_iterable=True))
    # Depending on the arguments, we can now return either the byte-sized ints as we have them, or we can convert them
    # to a byte array.
    return bsis if as_iterable else bytearray(bsis)


def _coord_to_bytes(coord: Tuple[float, float] or Tuple[float, float, float],
                    width: int,
                    precision: int = 4,
                    as_iterable: bool = False) -> bytearray or Iterable[int]:
    # We'll need to know the length of the tuple a couple of times below, so...
    ord_count = len(coord)
    # The number of bytes we devote to each floating point number will be the total width of the byte array we'll
    # return, divided by the number of floats in the tuple.
    width_per_float = int(width / ord_count)
    # Sanity Check:
    if width_per_float < 1:
        raise ValueError('At least one byte must be available for each ordinal in the coordinate.')
    # Create an empty list to hold the byte-sized ints we generate.  We'll extend it as we go along.
    bsis = []
    for i in range(0, ord_count):
        bsis.extend(float_to_bytes(coord[i], width=width_per_float, precision=precision, as_iterable=True))
    # That's that.
    return bsis if as_iterable else bytearray(bsis)


def djiohash_v1(geometry_type_code: int,
                srid: int,
                coordinates: Iterable[Tuple[float, float] or Tuple[float, float, float]],
                precision: int = 4) -> bytearray:
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
    b1 = b1_geometry_type | b1_is_collection | b1_has_m_values

    # Bytes 2-4 contain the SRID.
    b2_4 = int_to_bytes(srid, width=3, as_iterable=True)

    # Bytes 5-7 contains the total number of vertices.  However, we won't know it until we complete the iteration.

    # Bytes 8-128 will contain the coordinate hashes.
    b8_128 = [0] * 24 #TODO: 120 is a magic constant!!!

    max_bits = 64
    mask = int(math.pow(2, max_bits)) - 1 # A 32-bit mask
    coords_bits = 0  # This is the value we're doing all this bit blasting against.

    coordinates_count = 0  # We'll keep the count as we iterate.
    offset = 0
    for coord in coordinates:
        for ord in coord:
            # Pull everything from the fractional part of the number into the whole part.
            ordi = int(ord * math.pow(10, precision))
            # Rotate the integer value by the offset:
            # Shift the number bitwise by the offset.  (Some of the bits will move beyond the high-order part of
            # the mask, as you'll see, we rotate them to the lower bits.)
            ordi_shift = ordi << offset
            # ordi_hi is the part of the number that rotates beyond the high order bits of the mask.
            ordi_hi = ordi >> max_bits - offset
            # Recombine the shifted part and the
            ordi_rot = ordi_shift + ordi_hi
            # Apply an XOR
            coords_bits ^= ordi_rot
            # Increment (or reset) the offset.
            offset = offset + 1 if offset < max_bits else 0
            # We're keeping track of the total number of coordinates.
            coordinates_count += 1

    #coords_bits = coords_bits & mask

    # Now we convert the bits to a series of byte-sized ints.
    coords_bsis = int_to_bytes(coords_bits, width=int(max_bits/8), unsigned=True, as_iterable=True)

    b5_7 = int_to_bytes(coordinates_count, width=3, as_iterable=True) # TODO: We could cut this down to 2 if we forbid vertex counts over 65536 or if we allow collisions here.

    all_bsis = [b1] + b2_4 + b5_7 + coords_bsis

    # Convert our accumulated list of byte-sized ints into a single byte array.
    bytes = bytearray(all_bsis)
    return bytearray(bytes)




# def djiohash_v1(geometry_type_code: int,
#                 srid: int,
#                 coordinates: Iterable[Tuple[float, float] or Tuple[float, float, float]],
#                 precision: int = 4) -> bytearray:
#     # The first byte will hold the geometry type in the highest 4 bits of the first byte.
#     # ☐☐☐☐0000
#     b1_geometry_type = geometry_type_code << 4
#     # The next bit tells us whether or not the geometry is a collection.
#     # 0000☐000
#     b1_is_collection = 0 << 3  # TODO: Revisit this when collections are implemented.
#     # The next bit tells us whether or not this geometry has 3D coordinates (i.e. "M" values).
#     # 00000☐00
#     b1_has_m_values = 0 << 2  # TODO: Revisit this when we can determine this.
#     # The last two bits in this byte are presently available.
#     # 000000☐☐ <-- These are available.
#     b1 = b1_geometry_type | b1_is_collection | b1_has_m_values
#
#     # Bytes 2-4 contain the SRID.
#     b2_4 = int_to_bytes(srid, width=3, as_iterable=True)
#
#     # Bytes 5-7 contains the total number of vertices.  However, we won't know it until we complete the iteration.
#
#     # Bytes 8-128 will contain the coordinate hashes.
#     b8_128 = [0] * 24 #TODO: 120 is a magic constant!!!
#
#     how_many_bytes_per_coord = 12  # TODO: Rename this!!! And move the constant!
#
#     coordinates_count = 0  # We'll keep the count as we iterate.
#     offset = 0
#     for coord in coordinates:
#         coord_bsis = _coord_to_bytes(coord, width=how_many_bytes_per_coord, precision=precision, as_iterable=True)
#         for coord_bsi in coord_bsis:
#             for i in range(0, how_many_bytes_per_coord):
#                 bsi = coord_bsis[i]
#                 if bsi != 0:
#                     b8_128[i+offset] ^= bsi
#         # Adjust the offset.
#         offset += how_many_bytes_per_coord
#         # Increment the coordinate count (we'll need it in a moment).
#         coordinates_count += 1
#
#     b5_7 = int_to_bytes(coordinates_count, width=3, as_iterable=True) # TODO: We could cut this down to 2 if we forbid vertex counts over 65536 or if we allow collisions here.
#
#     lst = [b1] + b2_4 + b5_7 + b8_128
#
#     bytes = bytearray(lst)
#     return bytearray(bytes)





