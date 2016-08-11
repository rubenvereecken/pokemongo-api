"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

import struct
import time
import xxhash
import ctypes
import inspect
import os
import logging

from binascii import unhexlify


class ConstReflect(dict):

    def __init__(self):
        super(dict, self).__init__(self)

        def determineRoutine(attribute):
            return not(inspect.isroutine(attribute))

        attributes = inspect.getmembers(type(self), determineRoutine)
        for attribute in attributes:
            if attribute[0].isupper():
                self[attribute[1]] = attribute[0]


def setupLogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        'Line %(lineno)d,%(filename)s- %(asctime)s- %(levelname)s- %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def f2i(float):
    return struct.unpack('<Q', struct.pack('<d', float))[0]


def f2h(float):
    return hex(struct.unpack('<Q', struct.pack('<d', float))[0])


def h2f(hex):
    return struct.unpack('<d', struct.pack('<Q', int(hex, 16)))[0]


def d2h(f):
    hex_str = f2h(f)[2:].replace('L', '')
    hex_str = ("0" * (len(hex_str) % 2)) + hex_str
    return unhexlify(hex_str)


def encodeLocation(loc):
    return (f2i(loc.latitude), f2i(loc.longitude), f2i(loc.altitude))


def getMs():
    return int(round(time.time() * 1000))


def hashLocation(authTicket, latitude, longitude, altitude):
    baseHash = xxhash.xxh32(
        authTicket.SerializeToString(),
        seed=0x1B845238
    ).intdigest()

    # Format location
    locationBytes = d2h(latitude) + d2h(longitude) + d2h(altitude)

    # Using serialized Auth Ticket
    hashA = xxhash.xxh32(locationBytes, seed=baseHash).intdigest()

    # Hash of location using static seed 0x1B845238
    hashB = xxhash.xxh32(locationBytes, seed=0x1B845238).intdigest()
    return hashA, hashB


def hashRequests(authTicket, payload):
    baseHash = xxhash.xxh64(
        authTicket.SerializeToString(),
        seed=0x1B845238
    ).intdigest()

    # Serialize and hash each request
    return [xxhash.xxh64(
        request.SerializeToString(),
        seed=baseHash
    ).intdigest() for request in payload]


# Assuming the encrypt.dll file floating around out there
def hashSignature(signature, libraryPath):
    serialized = signature.SerializeToString()
    size = len(serialized)

    library = ctypes.cdll.LoadLibrary(libraryPath)
    library.argtypes = [
        ctypes.c_char_p,  # const unsigned char *input
        ctypes.c_size_t,  # size_t input_size
        ctypes.c_char_p,  # const unsigned char *iv
        ctypes.c_size_t,  # size_t  *iv_size
        ctypes.POINTER(ctypes.c_ubyte),  # unsigned char * output
        ctypes.POINTER(ctypes.c_size_t)  # size_t* output_size
    ]
    library.restype = ctypes.c_int  # Retun int

    iv = os.urandom(32)
    outputSize = ctypes.c_size_t()

    # Hash sig
    library.encrypt(serialized, size, iv, 32, None, ctypes.byref(outputSize))
    output = (ctypes.c_ubyte * outputSize.value)()
    # Call lib
    library.encrypt(
        serialized,
        size,
        iv,
        32,
        ctypes.byref(output),
        ctypes.byref(outputSize)
    )

    return b''.join(map(chr, output))
