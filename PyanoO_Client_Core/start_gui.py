import sys
import tkinter
from tkinter import *

from PyanoO_Client_Core.gui_utils import create_icon_png_file, get_astro, set_window_icon
from PyanoO_Client_Core.client_utils import connect

from PyanoO_Shared_Core import validators

from PIL import Image,ImageTk

import base64

class StartGui:

    def __init__(self,main_class):

        self.main_class = main_class

        self.root = Tk()
        self.root.configure(background='#101010')
        self.root.title('PyanoO Chat Client')
        self.root.option_add("*Font", "System")
        self.root.geometry('500x500')
        set_window_icon(self.root, 'StartGui')

        self.setup()

        self.alive = True

        self.mainloop()

    def mainloop(self):

        while self.alive:

            try:
                if self.root:
                    self.root.update()
                else:
                    break

            except TclError:
                if self.root:
                    sys.exit(0)

    def connect(self):

        ip = self.ip_input_entry.get()
        port = self.port_input_entry.get()
        key = self.key_input_entry.get()
        user = self.usern_input_entry.get()
        pwd = self.pwd_input_entry.get()

        error_msg = None

        if all((ip,port,key,user)):
            try:
                port = int(port)
            except ValueError:
                error_msg = 'Invalid port number!'
            else:
                uv = validators.username_valid(user)
                pv = validators.password_valid(pwd)
                if type(uv) == tuple:

                    if uv[1] == 'CHAR':

                        error_msg = "Usernames can only contain alphanumeric characters! ex. abcABC123"

                    elif uv[1] == 'SMALL':

                        error_msg = "Usernames can't be smaller than 3 characters"

                    elif uv[1] == 'BIG':

                        error_msg = "Usernames can't be bigger than 16 characters"

                elif type(pv) == tuple:

                    if pv[1] == 'SMALL':

                        error_msg = "Passwords can't be smaller than 5 characters"

                else:

                    c = connect(ip,port,key,user,pwd)

                    if type(c) == str:

                        error_msg = c

                    else:
                        self.root.destroy()
                        self.root = None
                        self.main_class(c[0],(ip,port),key,user,c[1])

        else:
            error_msg = 'Make sure all required values are filled in!'

        if error_msg:
            self.status_msg_label['text'] = error_msg
            self.status_msg_label.pack(side = TOP, fill=X)

    def setup(self):

        icon_img = ImageTk.PhotoImage(Image.open(create_icon_png_file('start')))
        self.icon_label = Label(self.root, image=icon_img, bg='#101010')
        self.icon_label.photo = icon_img

        self.title_label = Label(self.root, text="Pyano Chat Client", background='#303030', foreground='#66ff33', relief=SUNKEN)
        self.title_label.pack(side=TOP, fill=X)

        self.status_msg_label = Label(self.root, background='#202020', foreground='#ff0000', text='')
        self.status_msg_label.pack(side=TOP, fill=X)

        self.ip_input_frame = Frame(self.root, bg='#101010')
        self.ip_input_frame.pack(side=TOP, fill=X)

        self.port_input_frame = Frame(self.root, bg='#101010')
        self.port_input_frame.pack(side=TOP, fill=X)

        self.key_input_frame = Frame(self.root, bg='#101010')
        self.key_input_frame.pack(side=TOP, fill=X)

        self.usern_input_frame = Frame(self.root, bg='#101010')
        self.usern_input_frame.pack(side=TOP, fill=X)

        self.pwd_input_frame = Frame(self.root, bg='#101010')
        self.pwd_input_frame.pack(side=TOP, fill=X)

        self.ip_input_label = Label(self.ip_input_frame, text="Server IP", background='#303030', foreground='#66ff33')
        self.port_input_label = Label(self.port_input_frame, text="Server Port", background='#303030', foreground='#66ff33')
        self.key_input_label = Label(self.key_input_frame, text="Server Crypto Key", background='#303030', foreground='#66ff33')
        self.usern_input_label = Label(self.usern_input_frame, text="Username", background='#303030', foreground='#66ff33')
        self.pwd_input_label = Label(self.pwd_input_frame, text="Password (optional)", background='#303030', foreground='#66ff33')

        self.ip_input_label.pack(side=LEFT, expand=True, fill=X)
        self.port_input_label.pack(side=LEFT, expand=True, fill=X)
        self.key_input_label.pack(side=LEFT, expand=True, fill=X)
        self.usern_input_label.pack(side=LEFT, expand=True, fill=X)
        self.pwd_input_label.pack(side=LEFT, expand=True, fill=X)

        self.ip_input_entry = Entry(self.ip_input_frame, bg="#101010", fg="#66ff33")
        self.ip_input_entry.pack(side=RIGHT)

        self.port_input_entry = Entry(self.port_input_frame, bg="#101010", fg="#66ff33")
        self.port_input_entry.insert(0, '65511')
        self.port_input_entry.pack(side=RIGHT)

        self.key_input_entry = Entry(self.key_input_frame, bg="#101010", fg="#66ff33")
        self.key_input_entry.insert(0, 'default_PyanoO')
        self.key_input_entry.pack(side=RIGHT)

        self.usern_input_entry = Entry(self.usern_input_frame, bg="#101010", fg="#66ff33")
        self.usern_input_entry.pack(side=RIGHT)

        self.pwd_input_entry = Entry(self.pwd_input_frame, bg="#101010", fg="#66ff33", show=get_astro())
        self.pwd_input_entry.pack(side=RIGHT)

        self.send_btn = Button(self.root, text='Connect', command=self.connect, bg="#101010", fg="#66ff33")
        self.send_btn.pack(side=TOP, fill=X)

        self.info_label = Label(self.root, background='#101010', foreground='#202020', text=base64.b64decode(b'Q2F0dEZhd2tlcyAyMDE5').decode('utf-8'))
        self.info_label.pack(side=BOTTOM, fill=X)

        self.icon_label.pack(side=BOTTOM, expand=TRUE)
