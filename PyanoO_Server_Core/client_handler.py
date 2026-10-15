# -*- coding: utf-8 -*-
import threading
import socket

from PyanoO_Server_Core.logger import *

from PyanoO_Shared_Core import crypto
from PyanoO_Shared_Core.validators import username_valid
from PyanoO_Shared_Core.constants import VERSION
from PyanoO_Shared_Core.datetime import give_default_datetime_string,datetime_from_default_string
from PyanoO_Shared_Core.hashing import *
from PyanoO_Shared_Core.message import from_sendable,Message

import json
import time
import os

class Client:

    def __init__(self,server,connection: socket.socket,client_id: str, client_addr: str):

        self.server = server

        self.log = self.server.log

        self.conn = connection

        self.id = client_id
        self.addr = client_addr

        self.handler_thread = threading.Thread(target=self.handle_main,name=self.id,daemon=True)

        self.receiving = True
        self.sending = True

        self.recv_in = []
        self.send_out = []

        self.alive = True
        self.terminated = False

        self.strikes = 0

        self.client_info = {"username":None}

        self.handler_thread.start()

    def handle_main(self):

        try:

            allowed = False

            self.conn.send(b"PYA_"+json.dumps({'version':VERSION,"accept":self.server.accept_connections,'name':self.server.config['SERVER_NAME']}).encode('utf-8'))

            greet = self.conn.recv(16)

            if crypto.decrypt(greet,self.server.crypto_key) != b"ACKNOWLEDGE":

                self.conn.send(b"DENIED")
                self.terminate("Client sent invalid greeting")

            else:

                self.conn.send(b"ACCEPT")

                creds = json.loads(crypto.decrypt(self.conn.recv(2048),self.server.crypto_key))

                u_file_path = "PyanoO_Server_Data/users/{}.user".format(creds['username'])

                def create_status_message(status,msg):

                    return crypto.encrypt(json.dumps({"status":status,"msg":msg}).encode('utf-8'),self.server.crypto_key)

                if not username_valid(creds['username']):

                    self.conn.send(create_status_message("DENIED","Invalid username"))
                    self.terminate("Username that client gave didn't pass validation")

                else:
                    if creds['username'] in self.server.connected_users:

                        self.conn.send((create_status_message("DENIED","User '{}' is already connected to the server".format(creds['username']))))
                        self.terminate("Duplicate user: '{}'".format(creds['username']))

                    else:

                        if os.path.exists(u_file_path):

                            with open(u_file_path,'r') as uf:
                                u = json.loads(uf.read())

                            if u['pwd_key']:

                                upc = pwd_hash(creds['password_hash'],base64.b85decode(u['pwd_salt']))[32:] == base64.b85decode(u['pwd_key']) # creds['password_hash'] is a SHA512 hash of plaintext password which gets hashed again with hashing.pwd_hash

                            else:

                                upc = True

                            if upc:

                                if u['banned']:
                                    self.conn.send(create_status_message("DENIED","You have been banned from this server. Reason: {}".format(u["ban_reason"])))
                                    self.terminate("Banned user tried to connect")

                                else:

                                    allowed = True
                                    self.conn.send(create_status_message("ACCEPTED", "Connect!"))


                            else:

                                self.conn.send(create_status_message('DENIED',"Incorrect password"))
                                self.terminate("Incorrect password")

                        else:

                            with open(u_file_path,'w') as uf:

                                u = {'username':creds['username'],'role':self.server.config['DEFAULT_ROLE'],'creation_time':give_default_datetime_string(),'pwd_key':None,'pwd_salt':None,'banned':False,'ban_reason':None}

                                uf.write(json.dumps(u))

                            self.log('New user with username " {} " created'.format(creds['username']))

                            self.conn.send(create_status_message("ACCEPTED","Connect!"))

                            allowed = True

                        if allowed:
                            self.client_info['username'] = creds['username']
            if allowed:

                with open(u_file_path,'r') as uf:
                    self.user = json.loads(uf.read())

                self.server.connected_users[self.client_info['username']] = self

                self.perm_levels = self.server.roles['permissions'][self.user['role']]

                self.log('Client with id " {} " connected with user " {} "'.format(self.id,self.client_info['username']))

                self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],self.server.config['WELCOME_MSG'].format(USER=self.client_info['username'],SERVER=self.server.config['SERVER_NAME'])))
                self.server.msg_box.append(self.server.compose_server_message("@ALL",self.server.config['JOIN_MSG'].format(USER=self.client_info['username'],ADDR=self.addr[0],PORT=self.addr[1])))

                def receiver():

                    while self.receiving:
                        try:

                            r = crypto.decrypt(self.conn.recv(4096),self.server.crypto_key)

                            self.recv_in.append(r)

                        except ConnectionError:
                            self.terminate()


                def sender():

                    while self.sending:
                        try:

                            for s in self.send_out:
                                self.send_out.remove(s)
                                self.conn.send(crypto.encrypt(s,self.server.crypto_key))
                                time.sleep(0.1)
                        except ConnectionError:
                            self.terminate()

                self.send_thread = threading.Thread(target=sender, name=self.id+'-send', daemon=True)
                self.recv_thread = threading.Thread(target=receiver, name=self.id+'-recv', daemon=True)

                self.send_thread.start()
                self.recv_thread.start()



                while self.alive:

                    if self.strikes >= self.server.config['MAX_STRIKES']:

                        self.terminate()

                    for msg in self.recv_in:
                        self.recv_in.remove(msg)
                        try:
                            m = from_sendable(msg)

                            if m.sender != self.client_info['username']:
                                self.strikes += 60

                            if len(m.content) > 800 and m.type in ['raw', 'msg']:
                                self.strikes += 3
                                continue

                            m.content = m.content.replace('\n','')

                            if m.type == 'cmd' and m.receiver == 'SERVER':

                                if not self.server.config['COMMANDS_ENABLED']:
                                    self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'], "Commands have been disabled."))
                                else:
                                    cmd = m.content.split(' ')
                                    cmf = cmd[0]

                                    allowed_cmds = self.server.roles['permissions'][self.user['role']]

                                    if cmf in self.server.command_levels:
                                        if self.server.command_levels[cmf] in allowed_cmds:

                                            if cmf == 'msg':
                                                self.server.msg_box.append(Message(self.client_info['username'],cmd[1]," ".join(cmd[2:]),'msg',m.datetime))

                                            if cmf == 'poke':

                                                self.server.msg_box.append(Message(self.client_info['username'],cmd[1],"*{} pokes you*".format(self.client_info['username']),'raw',m.datetime))
                                                if cmd[1] in self.server.connected_users:
                                                    self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"You poked {}".format(cmd[1])))

                                            if cmf in ['listusers','users']:
                                                self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"Online users: {}".format(", ".join(self.server.connected_users.keys))))

                                            if cmf == 'changepass':
                                                p = multi_sha512(cmd[1],100000).decode('utf-8')
                                                phs = pwd_hash(p)
                                                ph = phs[32:]
                                                ps = phs[:32]

                                                with open(u_file_path, 'w') as uf:
                                                    self.user['pwd_key'] = base64.b85encode(ph).decode('utf-8')
                                                    self.user['pwd_salt'] = base64.b85encode(ps).decode('utf-8')
                                                    uf.write(json.dumps(self.user))

                                                self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"Password changed."))

                                            if cmf in ['removepass','rempass','nopass']:

                                                with open(u_file_path, 'w') as uf:
                                                    self.user['pwd_key'] = None
                                                    self.user['pwd_salt'] = None
                                                    uf.write(json.dumps(self.user))

                                                self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"Password removed."))

                                            if cmf in ['listroles','roles']:

                                                self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"Online users with roles: {}".format(", ".join(["{} = {}".format(uz,self.server.connected_users[uz].user['role']) for uz in self.server.connected_users.keys()]))))

                                            if cmf == 'kick':

                                                self.server.msg_box.append(Message('SERVER',cmd[1],"You have been kicked"+str(': ' if cmd[2:] else '')+" ".join(cmd[2:]),'KICK',m.datetime))
                                                time.sleep(1)
                                                if cmd[1] in self.server.connected_users:
                                                    self.server.connected_users[cmd[1]].terminate("Kicked from the server by {}".format(self.client_info['username']))
                                                    self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'], "You kicked {}".format(cmd[1])))

                                            if cmf == 'ban':

                                                self.server.msg_box.append(Message('SERVER',cmd[1],"You have been banned"+str(': ' if cmd[2:] else '')+" ".join(cmd[2:]),'BAN',m.datetime))

                                                if cmd[1] in self.server.connected_users:
                                                    buchu = self.server.connected_users[cmd[1]].user
                                                    bu_file_path = "PyanoO_Server_Data/users/{}.user".format(cmd[1])
                                                    with open(bu_file_path, 'w') as uf:
                                                        buchu['banned'] = True
                                                        buchu['ban_reason'] = " ".join(cmd[2:])
                                                        uf.write(json.dumps(buchu))

                                                time.sleep(1)
                                                if cmd[1] in self.server.connected_users:
                                                    self.server.connected_users[cmd[1]].terminate("Banned from the server by {}".format(self.client_info['username']))
                                                    self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'], "You banned {}".format(cmd[1])))

                                        else:
                                            self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"You don't have access to level {} commands".format(self.server.command_levels[cmf])))
                                    else:
                                        self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"Unknown command: {}".format(cmf)))


                            else:

                                self.server.msg_box.append(m)

                        except:
                            raise
                            self.strikes += 1
                            self.server.msg_box.append(self.server.compose_server_message(self.client_info['username'],"An error occurred while parsing your message!"))

                if not self.terminated:
                    self.terminate()

        except Exception as e:
            raise
            self.terminate(e)

    def terminate(self,err=None):

        if self.alive:
            self.conn.close()
            self.alive = self.receiving = self.sending = False

            if self.client_info['username']:

                self.server.connected_users.pop(self.client_info['username'])

            if not err:
                self.log('Client with id " {} " terminated'.format(self.id))
            else:
                self.log('An error occurred while handling client with id " {} " causing the client to be terminated: {} '.format(self.id,repr(err)),ERROR)

            self.terminated = True

        else:

            self.log('Tried to terminate client with id " {} " but client was already terminated or client.alive was changed to False'.format(self.id),DEBUG)