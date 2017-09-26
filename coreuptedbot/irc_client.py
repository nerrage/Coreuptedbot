#irc_client.py
#This is the main class for connecting and interacting with twitch irc
#This also keeps us connected to IRC by responding to PINGs
#You must call get_messages() regularly to stay connected
import socket
import time
import re
from irc_cfg import *

#irc_client will get us connected to twitch and also be used to send messages
class irc_client:

    def __init__(self, nick, passw, chan):
        self.nick = nick
        self.passw = passw
        self.chan = chan

    def connect(self):
        self.sock = socket.socket()
        self.sock.connect(('irc.chat.twitch.tv', 6667))
        #the following order matters to twitch
        self.sock.send("PASS {}\r\n".format(self.passw).encode("utf-8"))
        self.sock.send("NICK {}\r\n".format(self.nick).encode("utf-8"))
        self.sock.send("JOIN {}\r\n".format(self.chan).encode("utf-8"))
        time.sleep(1)
        print(self.sock.recv(1024).decode("utf-8")) #Print inital irc connection

    def disconnect(self):
        self.sock.send("QUIT :")

    def chat(self,msg):
        self.sock.send("PRIVMSG {} :{}\r\n".format(self.chan, msg)) 

    def get_messages(self): #core part of this class
        #Parses the irc output into a list of lists [['user','message'],['user'...
        #but will also PONG any pings so that we stay connected
        #this must be called semi-regularly because of said PONGs
        message_list = []
        try: #weird characters will cause exceptions, lookin' at you emojis
            response = self.sock.recv(1024).decode("utf-8")
            print response #logging
        except:
            print "Error in processing above chat... continuing"
            return message_list #empty
        response_list = response.splitlines()
        for rawresponse in response_list: #clean it out with regex
            name = re.search(r"\w+", rawresponse).group(0) 
            message = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :").sub("", rawresponse)
            message_list.append([name, message])
        #message_list is now assembled but we want to filter out PINGs
        filtered_messages = []
        for message in message_list:
            username = message[0]
            chat = message[1]
            if chat == "PING :tmi.twitch.tv":
                self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
            else:
                filtered_messages.append([username,chat])
        return filtered_messages
