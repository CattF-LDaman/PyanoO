# -*- coding: utf-8 -*-
from PyanoO_Server_Core.logger import *
from PyanoO_Server_Core.constants import *
from PyanoO_Server_Core.client_handler import Client

from PyanoO_Shared_Core.datetime import give_default_datetime_string
from PyanoO_Shared_Core.message import Message
from PyanoO_Shared_Core.hashing import *
from PyanoO_Shared_Core.python_utils import *

import socket
import sys
import os
import datetime
import hashlib
import json
import threading
import traceback
import random
import ctypes

# ◢◤

class Main:

    def __init__(self):

        if not os.path.exists("PyanoO_Server_Data"):
            os.mkdir("PyanoO_Server_Data")
            os.mkdir("PyanoO_Server_Data/logs")
            os.mkdir("PyanoO_Server_Data/msg_logs")
            os.mkdir("PyanoO_Server_Data/users")

        self._log_path = "PyanoO_Server_Data/logs/log_{}_{}.log".format(hashlib.sha256(datetime.datetime.now().strftime("%d/%m/%Y @ %H:%M:%S").encode('utf-8')).hexdigest()[:6],datetime.datetime.now().strftime("%d-%m-%Y %H.%M.%S"))

        self.logger = Logger(self._log_path,print_debug=False)
        self.log = self.logger.log

        print("Log file at {}".format(self._log_path))

        self.log("New server session started on {}!".format(socket.gethostname()),WARNING)

        try:
            self.setup()

            self.accept_connections = True

            self._conn_loop_alive = True
            self._connections = []

            self.clients = {}
            self.connected_users = {}

            self.msg_box = []

            self.msg_history = []  # last 100 msg

            self.cur_msg_id = 0

            self.connection_loop_thread = threading.Thread(target=self.connection_loop,daemon=True)
            self.connection_loop_thread.start()
            self.log("Started connection loop")

            self.log("Server running")
            self.main()

        except Exception as e:
            self.log("An error occurred causing the server to stop working: {}".format(e),ERROR)
            type_, value_, traceback_ = sys.exc_info()
            tb = traceback.format_exception(type_, value_, traceback_)
            for ln in tb:
                self.log(ln,ERROR)

            logname = "PyanoO_Server_Data/logs/crash_{}.txt".format(random.randint(0,99999999))
            while os.path.exists(logname):
                logname = "PyanoO_Server_Data/logs/crash_{}.txt".format(random.randint(0, 99999999))

            with open(logname,"w") as cf:
                cf.write("\n".join(self.logger.logs_text))

            print('\n\nGo to {} for more information'.format(logname))
            if sys.platform == 'win32':
                ctypes.windll.user32.MessageBoxA(0, bytes('An error occurred causing the server to stop working.\nGo to {} for more information.'.format(os.path.abspath(logname)), 'utf-8'), b"PyanoO Server Error", 0x0 | 0x10)

    def setup(self):

        self.log("Setting up...")

        if not os.path.exists("PyanoO_Server_Data/config.json"):
            self.log("Aborting setup: missing config file",ERROR)

            self.log("Creating config file")
            with open("PyanoO_Server_Data/config.json","w") as cf:
                cf.write(json.dumps(DEFAULT_CONFIG))
            self.log("Config file created (PyanoO_Server_Data/config.json)")

            self.log("Closing server session...")
            sys.exit()

        else:
            with open("PyanoO_Server_Data/config.json","r") as cf:
                self.config = json.loads(cf.read())

                missing_keys = list_difference(DEFAULT_CONFIG,self.config)

                if missing_keys:
                    self.log("Config file is missing one or more keys: ' {} ', using default value for those keys".format(", ".join(missing_keys)),WARNING)

                self.config = merge_dict(self.config,DEFAULT_CONFIG)


        if not os.path.exists("PyanoO_Server_Data/roles.json"):

            self.log("Aborting setup: missing roles file",ERROR)

            self.log("Creating roles file")
            with open("PyanoO_Server_Data/roles.json","w") as cf:
                cf.write(json.dumps(DEFAULT_ROLES))
            self.log("Config file created (PyanoO_Server_Data/roles.json)")

            self.log("Closing server session...")
            sys.exit()
        else:
            with open("PyanoO_Server_Data/roles.json","r") as cf:

                self.roles = json.loads(cf.read())

                self.roles['permissions'][1337] = [i for i in range(1337)] #MASTER

        if not os.path.exists("PyanoO_Server_Data/commands.json"):

            self.log("Aborting setup: missing commands file",ERROR)

            self.log("Creating commands file")
            with open("PyanoO_Server_Data/commands.json","w") as cf:
                cf.write(json.dumps(DEFAULT_CMD_LEVELS))
            self.log("Config file created (PyanoO_Server_Data/commands.json)")

            self.log("Closing server session...")
            sys.exit()
        else:
            with open("PyanoO_Server_Data/commands.json","r") as cf:

                self.command_levels = json.loads(cf.read())

                self.command_levels = merge_dict(self.command_levels,DEFAULT_CMD_LEVELS)

        if not os.path.exists("PyanoO_Server_Data/users/master.user"):

            with open("PyanoO_Server_Data/users/master.user", 'w') as uf:

                pstr = hashlib.sha512((str(random.randint(0,999999999))+"pya"+str(self.config)+str(self)).encode('utf-8')).hexdigest()

                u = {'username': "master", 'role': 1337, 'creation_time': give_default_datetime_string(), 'pwd_key': None, 'pwd_salt': None, 'banned': False, 'ban_reason': None}

                print("!!! MASTER USER CREATED !!!")
                print("Log in as user ' master ' with password ' {} '".format(pstr))
                print("This password will only be shared once")
                print("To reset this user delete PyanoO_Server_Data/users/master.user and restart the server")

                p = multi_sha512(pstr, 100000).decode('utf-8')
                phs = pwd_hash(p)
                ph = phs[32:]
                ps = phs[:32]
                u['pwd_key'] = base64.b85encode(ph).decode('utf-8')
                u['pwd_salt'] = base64.b85encode(ps).decode('utf-8')

                uf.write(json.dumps(u))

        self.logger.print_debug = self.config['PRINT_DEBUG_LOGS']

        self.crypto_key = self.config['CRYPTO_KEY']

        self.log("Creating socket...",DEBUG)
        self.socket = socket.socket()
        self.log("Socket created",DEBUG)

        self.log('Binding socket...',DEBUG)
        self.socket.bind(('',self.config['HOST_PORT']))
        self.log('Socket bound to port {}'.format(self.config['HOST_PORT']),DEBUG)

        self.socket.listen(10)
        self.log("Started listening on socket",DEBUG)

        self.log('Done setting up!')
        self.log('Server accessible on port {}'.format(self.config['HOST_PORT']))

    def compose_server_message(self, receiver, content, type="msg"):

        return Message('SERVER',receiver,content,type,datetime.datetime.now())

    def main(self):

        while True:

            for msg in self.msg_box:

                self.msg_box.remove(msg)

                msg.id = self.cur_msg_id
                self.cur_msg_id += 1

                if msg.sender in self.connected_users and self.config['LOG_MESSAGES_TO_FILE']:
                    with open("PyanoO_Server_Data/msg_logs/{}.msgs".format(msg.sender),'a') as mf:

                        mf.write(msg.as_sendable(add_id=True).decode('utf-8')+'\n')

                if msg.receiver == "@ALL":

                    for client in self.connected_users.values():

                        msg_id_view = False

                        if self.config["MESSAGE_ID_VIEW_PERM_LEVEL"] in client.perm_levels:

                            msg_id_view = True

                        client.send_out.append(msg.as_sendable(msg_id_view))

                else:

                    if msg.receiver in self.connected_users:

                        self.connected_users[msg.receiver].send_out.append(msg.as_sendable())

                        if msg.sender in self.connected_users:

                            self.connected_users[msg.sender].send_out.append(msg.as_sendable())

                    elif msg.sender in self.connected_users:

                        self.connected_users[msg.sender].send_out.append(self.compose_server_message(msg.sender,'User " {} " not found'.format(msg.receiver)).as_sendable())


    def connection_loop(self):
        while self._conn_loop_alive:

            conn, addr = self.socket.accept()
            self._connections.append(conn)

            if addr[0] in []:
                self.log('Blocked connection tried to connect.',WARNING)
                conn.close()

            else:
                self.log('Connected with ' + addr[0] + ':' + str(addr[1])+'!')

                client_id = None
                while client_id in self.clients or not client_id:
                    client_id = hashlib.sha512((str(conn)+str(addr)).encode('utf-8')).hexdigest()[:8]+'-'+str(random.randint(0,9999999999))
                self.clients[client_id] = Client(self,conn,client_id,addr)

                self.log('New client with id " {} "'.format(client_id))
                #start_new_thread(self.client_thread, (Connection(conn,addr,ENCRYPTION_KEY),))



Main()