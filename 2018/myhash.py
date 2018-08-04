import binascii
import struct
import random

def mychecksum(data):
    # random.seed(str(data))
    # return struct.pack(">I",random.getrandbits(32))
    return struct.pack(">I",binascii.crc32(data) & 0xffffffff)
