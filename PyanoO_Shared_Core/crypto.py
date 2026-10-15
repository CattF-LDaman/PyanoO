import hashlib
from Crypto.Cipher import AES

def key_from_string(string,length=None):
    if length:
        if length <= 128:
            return hashlib.sha512(bytes(str(string)*length*21,'utf-8')).digest()[:length]
        else:
            raise Exception('Length should be less than or equal to 128!')
    else:
        return hashlib.sha512(bytes(str(string) * length * 21, 'utf-8')).digest()

def encrypt(b,keystring,ivstring='PyanoO'):
    key = key_from_string(str(keystring),16)
    IV = key_from_string(str(ivstring)+str(keystring),16)

    encryption_suite = AES.new(key, AES.MODE_CFB, IV)
    encrypted = encryption_suite.encrypt(b)

    return encrypted

def decrypt(b,keystring,ivstring='PyanoO'):
    key = key_from_string(str(keystring),16)
    IV = key_from_string(str(ivstring)+str(keystring),16)

    decryption_suite = AES.new(key, AES.MODE_CFB, IV)
    decrypted = decryption_suite.decrypt(b)

    return decrypted