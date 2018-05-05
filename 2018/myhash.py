import hashlib

def checksum_md5(data):
    md5 = hashlib.md5(data)
    return md5.digest()
