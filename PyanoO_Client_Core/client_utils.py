
import socket
import json
import base64

from PyanoO_Shared_Core.hashing import multi_sha512
from PyanoO_Shared_Core import crypto
from PyanoO_Shared_Core.constants import VERSION

def connect(ip,port,key,user,pwd):

    s = socket.socket()

    try:
        try:
            s.connect((ip,port))
        except socket.gaierror:
            raise PyanooConnectError("Unknown hostname")

        greet = s.recv(2048)

        if not greet.startswith(b"PYA_"):
            raise PyanooConnectError("Host isn't a PyanoO server")

        g = json.loads(greet[4:].decode('utf-8'))

        server_name = g['name']

        if g['version'] != VERSION:
            raise PyanooConnectError("Host and client are not running same PyanoO version")

        if g['accept'] == False:
            raise PyanooConnectError("Host isn't currently accepting new clients")

        s.send(crypto.encrypt(b"ACKNOWLEDGE",key))

        if s.recv(8) != b"ACCEPT":

            raise PyanooConnectError("Invalid crypto key!")

        s.send(crypto.encrypt(json.dumps({"username":user,"password_hash":multi_sha512(pwd,100000).decode('utf-8')}).encode('utf-8'),key))

        msg = json.loads(crypto.decrypt(s.recv(2048),key))

        if msg['status'] == 'DENIED':
            raise PyanooConnectError('Host denied connection: {}'.format(msg['msg']))
        else:
            return (s,server_name)

    except Exception as e:
        return "Couldn't connect to {}:{} > {}".format(ip,port,str(e))

class PyanooConnectError(Exception):
    pass