import hashlib
import os
import base64

def pwd_hash(pwd_string,_salt=None):

    if not _salt:
        _salt = os.urandom(32)

    _hash = hashlib.pbkdf2_hmac('sha512',pwd_string.encode('utf-8'),_salt,100000)

    return _salt+_hash

def multi_sha512(pwd_string,n):

    p = pwd_string.encode('utf-8')

    for _ in range(n):

        p = hashlib.sha512(p+b'PYA').digest()

    return base64.b85encode(p)