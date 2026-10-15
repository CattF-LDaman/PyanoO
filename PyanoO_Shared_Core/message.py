import json
import datetime
from PyanoO_Shared_Core.datetime import datetime_to_default_string,datetime_from_default_string

def from_sendable(sendable):

    s = json.loads(sendable.decode('utf-8'))

    return Message(s['from'],s['to'],s['content'],s['type'],datetime_from_default_string(s['time']),id=s['id'] if 'id' in s else None)

class Message:

    def __init__(self,sender,receiver,content,type,msg_datetime=None,id=None):

        self.id = id

        self.sender = sender
        self.receiver = receiver
        self.content = content.strip('\n').strip('\r')
        self.type = type
        if msg_datetime:
            self.datetime = msg_datetime
        else:
            self.datetime = datetime.datetime.now()
        self.datetime_string = datetime_to_default_string(msg_datetime)

    def as_sendable(self,add_id=False):

        m = {'from':self.sender,'to':self.receiver,'content':self.content,'type':self.type,'time':self.datetime_string}

        e = {}

        if add_id:

            e['id']=self.id

        return json.dumps({**m,**e}).encode('utf-8')

    def as_printable(self, user=None, show_id=False):

        t = self.type

        m = ""

        if t == 'raw':

            m = str(self.content)

        elif t == 'cmd':

            m = '(CMD) {} >> {}'.format(user,self.content)

        elif t == 'msg':
            if self.receiver == user:
                m = '(To you) | {} on {} | {}'.format(self.sender,self.datetime_string,str(self.content))
            elif self.receiver != "@ALL":
                if self.sender != user:
                    m = '(To {} from {}) | on {} | {} '.format(self.receiver,self.sender,self.datetime_string,str(self.content))
                else:
                    m = '(To {} from you) | on {} | {} '.format(self.receiver, self.datetime_string, str(self.content))
            else:
                m = '| {} on {} | {}'.format(self.sender,self.datetime_string,str(self.content))

        else:

            m = self.as_sendable().decode('utf-8')

        if show_id:

            m = "< ID {} > ".format(self.id)+m

        return m