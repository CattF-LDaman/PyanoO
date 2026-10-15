from PyanoO_Client_Core import start_gui
from PyanoO_Client_Core.main_gui import MainGui

from PyanoO_Shared_Core.message import *
from PyanoO_Shared_Core import crypto

import socket
import sys
import time
import threading

# ◢◤

class Main:

    def __init__(self,conn,addr,crypto_key,user,server_name):

        self.conn = conn

        self.crypto_key = crypto_key

        self.addr = addr

        self.username = user

        self.server = server_name

        self.new_msg = []
        self.messages = []

        self.alive = True

        self.sending = True
        self.receiving = True

        self.recv_in = []

        self.messages_out = []
        self.send_out = []

        threading.Thread(target=self.main,daemon=True).start()

        self.gui = MainGui(self,addr,user,server_name)

    def compose_client_msg(self,content,type='msg'):

        return Message("CLIENT",self.username,content,type,datetime.datetime.now())

    def client_msg(self,content,type='msg'):

        self.new_msg.append(self.compose_client_msg(content,type))

    def main(self):

        def receiver():

            while self.receiving:
                try:

                    r = crypto.decrypt(self.conn.recv(4096), self.crypto_key)

                    self.recv_in.append(r)

                except ConnectionError:
                    self.lost_connection()

        def sender():

            while self.sending:
                try:

                    for s in self.send_out:
                        self.send_out.remove(s)
                        self.conn.send(crypto.encrypt(s, self.crypto_key))
                        time.sleep(0.1)
                except ConnectionError:
                    self.lost_connection()

        self.send_thread = threading.Thread(target=sender, name='main-send', daemon=True)
        self.recv_thread = threading.Thread(target=receiver, name='main-recv', daemon=True)

        self.send_thread.start()
        self.recv_thread.start()

        while self.alive:

            for msg in self.messages_out:
                self.messages_out.remove(msg)
                self.send_out.append(msg.as_sendable())

            for msg in self.recv_in:
                self.recv_in.remove(msg)
                m = from_sendable(msg)
                self.messages.append(m)
                if m.type in ['KICK','BAN'] and m.sender == 'SERVER':
                    self.lost_connection(m.content)
                else:
                    self.new_msg.append(m)

    def lost_connection(self,reason="Connection lost"):

        if any([s is True for s in [self.sending,self.receiving,self.alive]]):
            self.client_msg("Lost connection to server: {}!".format(reason),'raw')

            self.conn.close()
            self.sending = self.receiving = self.alive = False


def start_client():
    start_gui.StartGui(Main)

start_client()
