import tkinter
from tkinter import *

from PyanoO_Shared_Core.message import *
from PyanoO_Client_Core.gui_utils import create_icon_png_file, get_astro, set_window_icon

from PIL import Image,ImageTk

import threading

class MainGui:

    def __init__(self,client,addr,user,server):

        self.client = client

        self.user = user
        self.addr = addr
        self.server = server

        self.title = "PyanoO with {USER} on {SERVER} at {ADDR}:{PORT}".format(USER=self.user,SERVER=self.server,ADDR=self.addr[0],PORT=self.addr[1])

        self.root = Tk()
        self.root.configure(background='#101010')
        self.root.title(self.title)
        self.root.option_add("*Font", "System")
        self.root.geometry('900x900')
        set_window_icon(self.root, 'StartGui')

        self.setup()

        self.alive = True

        self.client_dead = False

        #self.main_loop_thread = threading.Thread(target=self.mainloop,name="GuiThread",daemon=True)
        #self.main_loop_thread.start()

        self.mainloop()

    def mainloop(self):

        while self.alive:

            try:

                if self.client.alive == False and not self.client_dead:
                    self.messages['fg'] = '#999999'
                    self.title_label['fg'] = '#999999'
                    self.input_entry['fg'] = '#999999'
                    self.send_btn['fg'] = '#999999'
                    self.client_dead = True

                for m in self.client.new_msg:

                    self.client.new_msg.remove(m)

                    msg = m.as_printable(self.client.username, self.view_show_msg_id.get())

                    self.messages['state'] = NORMAL

                    self.messages.insert(END,msg+'\n')

                    self.messages['state'] = DISABLED

                self.root.update()

            except TclError:

                self.client.lost_connection()
                from client import start_client
                start_client()

    def parse_command(self,msg):

        c = msg.content

        cm = c.strip("/").split(" ")

        cmf = cm[0]

        cmds = {'leave':self.root.destroy}

        if cmf in cmds:
            cmds[cmf]()

        else:

            msg.receiver = 'SERVER'
            msg.type = 'cmd'
            msg.content = " ".join(cm)

            self.client.messages_out.append(msg)

    def send(self):

        msg_text = self.input_entry.get().strip()

        if len(msg_text) <= 800:
            if msg_text:
                m = Message(self.client.username,'@ALL',msg_text,'msg',datetime.datetime.now())
                if m.content.startswith('/'):
                    self.parse_command(m)
                else:
                    self.client.messages_out.append(m)

            self.input_entry.delete(0,END)
        else:
            self.client.client_msg("Messages above 800 characters are not allowed!","raw")

    def setup(self):

        icon_img = ImageTk.PhotoImage(Image.open(create_icon_png_file('start')))
        #self.icon_label = Label(self.root, image=icon_img, bg='#101010')
        #self.icon_label.photo = icon_img

        self.menubar = Menu(self.root)

        self.viewmenu = Menu(self.menubar, tearoff=0)

        self.viewmenu_admin = Menu(self.viewmenu, tearoff=0)

        self.view_show_msg_id = BooleanVar()
        self.view_show_msg_id.set(False)

        self.viewmenu_admin.add_checkbutton(label="Show MSG ID",onvalue=True,offvalue=False,variable=self.view_show_msg_id)
        self.viewmenu.add_cascade(label="Admin",menu=self.viewmenu_admin)

        self.menubar.add_cascade(label="View",menu=self.viewmenu)

        self.root.config(menu=self.menubar)

        self.title_label = Label(self.root, text=self.title, background='#303030', foreground='#66ff33', relief=SUNKEN)
        self.title_label.pack(side=TOP, fill=X)

        self.messages = Text(self.root, background='#303030', foreground='#66ff33', wrap=WORD, spacing3=20, state=DISABLED)
        self.messages.pack(side=TOP, fill=BOTH,expand=TRUE)

        self.message_list_scrollbar = Scrollbar(self.messages,command=self.messages.yview, bg="#202020")
        self.messages.configure(yscrollcommand=self.message_list_scrollbar.set)
        self.message_list_scrollbar.pack(side=RIGHT,fill=Y)

        self.input_entry = Entry(self.root,bg="#101010",fg="#66ff33")
        self.input_entry.pack(side=LEFT, fill=X, expand=True)

        self.send_btn = Button(self.root,text='Send',command=self.send,bg="#101010",fg="#66ff33")
        self.send_btn.pack(side=RIGHT,fill=X)

        def return_send():
            if self.root.focus_get() == self.input_entry:
                self.send()
            #else:
            #    self.send()

        self.root.bind('<Return>', lambda event: return_send())

        #self.info_label = Label(self.root, background='#101010', foreground='#202020', text=base64.b64decode(b'Q2F0dEZhd2tlcyAyMDE5').decode('utf-8'))
        #self.info_label.pack(side=LEFT, fill=X)

        #self.icon_label.pack(side=BOTTOM)

