import imaplib
import email
from email.header import decode_header
from database import Database
import time
import datetime


""" Class for accessing a mailbox
    with messages from the bank
"""
class Mail:

    def __init__(
        self,
        mail_pass:str = 'YOUR_MAIL_PASS', # Personal Security Code
        username:str = 'YOUR MAIL',       # Your mailbox name@mail.com
        imap_server:str = 'imap.YOUR.SERVER', #Server of mail. Exmpl: yandex.ru
        )->None:
        self.mail_pass = mail_pass
        self.username = username
        self.imap_server = imap_server
        self.msg = ''
        self.spis = []
        self.number_letter = ''

    """ Sign in to your mailbox
    """
    def logining(self)->None:
        self.imap = imaplib.IMAP4_SSL(self.imap_server)
        self.imap.login(self.username, self.mail_pass)
        self.imap.select('INBOX')
        (res, self.spis) = self.imap.uid('search', 'ALL')
        self.spis = self.spis[0].decode().split()

    """Determines which letter we will work with
    """
    def _new_letters(self, i:int): # i -Number of letter (in the end of program)
        self.number_letter = self.spis[len(self.spis) - i - 1]
        (res, self.msg) = self.imap.uid('fetch', self.number_letter,
                                        '(RFC822)')
        self.msg = email.message_from_bytes(self.msg[0][1])
        return self.msg # type = email.message.Message


""" A class that parses one letter and returns a tuple,
    which then goes to the database
"""
class Letter(Mail):

    def __init__(self, i:int)->None:# i -number of letter
        super().__init__()
        super().logining()
        self.msg = super()._new_letters(i) # type = email.message.Message
        self.letter_date = email.utils.parsedate_tz(self.msg['Date'])
        self.letter_day = datetime.date(*self.letter_date[:3])
        self.letter_time = datetime.time(*self.letter_date[3:5])
        self.letter_id = self.msg['Message-ID']
        self.letter_from = self.msg['Return-path']
        self.balance = 0
        self.cost = 0
        self.card = ''
        self.place = ''
        self.operation = ''
        self.date = ''
        self.timing = ''

    """Transorm a string of message into tuple of key_values like 'balance'
    """
    def searching(self)->tuple: #returns tuple - in future it will be one line in Table
        if self.msg.is_multipart() and self.letter_from=='<no-reply@sms-forwarder.com>':
            cnt=0
            try:
                for part in self.msg.walk():
                    if cnt==1:
                        part=str(part)
                        answer=part[part.find('D0=BD=D0=B8=D0=B5')\
                                    +19:part.find('You received')]
                        answer=answer.replace('=','')
                        answer=answer.replace('\n','')
                        answer=answer.split()
                        
                        self.cost = float(answer[3][:answer[3].find('D180')])
                        self.operation = bytes.fromhex(answer[2]).decode("utf-8")
                        if self.operation =='Оплата'\
                           or self.operation == 'Списание':
                            self.operation = 'Покупка'
                        self.card = answer[0]
                        
                        a = answer.index('D091D0B0D0BBD0B0D0BDD181:')+1
                        q = answer[a]
                        self.balance = float(q[:q.find('D1')])
                        self.place = ' '.join(answer[4:a-1])\
                                     if (self.operation =='Покупка'\
                                         or self.operation =='перевод') else 'None'

                        if self.place == 'Yandex Bank':
                            self.operation='Покупка'
                        if len(self.place) > 50:
                            self.place = 'Оплата или перевод'
                        break
                    cnt += 1
                return (self.number_letter, # int
                        self.card, # str
                        str(self.letter_time),# str
                        self.operation,# str
                        self.cost,# float,2
                        self.place,# str
                        self.balance,# float,2
                        str(self.letter_day))# str
            except:
                return (None, None, None, None, None, None, None)  
        else:
            return (None, None, None, None, None, None, None)

    """ Transorm a string of message into tuple of key_values like 'balance'
        The same function, but searching only for last two weeks messages
    """
    def searching_two_weeks(self)->None:
        try:
            while datetime.date.today() - datetime.timedelta(days=14) <= self.letter_day:
                if self.msg.is_multipart() and self.letter_from == '<no-reply@sms-forwarder.com>':
                    cnt=0
                    try:
                        for part in self.msg.walk():
                            if cnt == 1:
                                part = str(part)
                                answer = part[part.find('D0=BD=D0=B8=D0=B5')\
                                              + 19:part.find('You received')]
                                answer = answer.replace('=','')
                                answer = answer.replace('\n','')
                                answer = answer.split()
                                self.cost = float(answer[3][:answer[3].find('D180')])
                                self.operation = bytes.fromhex(answer[2]).decode("utf-8")
                                if self.operation == 'Оплата'\
                                   or self.operation =='Списание':
                                        self.operation = 'Покупка'
                                self.card = answer[0]
                                a = answer.index('D091D0B0D0BBD0B0D0BDD181:')+1
                                q = answer[a]
                                self.balance = float(q[:q.find('D1')])
                                self.place = ' '.join(answer[4:a-1])\
                                             if (self.operation =='Покупка'\
                                                 or self.operation =='перевод')\
                                                 else 'None'
                                if self.place == 'Yandex Bank':
                                    self.operation = 'Покупка'
                                break
                            cnt+=1
                        return (self.number_letter,# int
                                self.card, # str
                                str(self.letter_time), #str
                                self.operation, #str
                                self.cost, #float,2
                                self.place, # str
                                self.balance, # float,2
                                str(self.letter_day)) # str
                    except:
                        return (None, None, None, None, None, None, None)  
                else:
                    return (None, None, None, None, None, None, None)
        except:
            return (None, None, None, None, None, None, None)



if __name__ == "__main__":
    db = Database('YOUR PATH TO DATABASE')
    mail = Mail()
    mail.logining()
    db.delete_info()
    
    for i in range(0, len(mail.spis)):
        letter = Letter(i) # i - number of letter
        cortage = letter.searching()
        if type(cortage) == tuple and cortage[0] is not None:
            db.add_info(cortage)
            
    for i in range(0, len(mail.spis)):
        letter = Letter(i)
        cortage = letter.searching_two_weeks()
        if type(cortage) == tuple and cortage[0] is not None:
            db.add_14days(cortage)
        elif type(cortage) != tuple:
            break

