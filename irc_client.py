import socket
import time
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

    def chat(self,msg):
        self.sock.send("PRIVMSG {} :{}\r\n".format(self.chan, msg)) 

core = irc_client(NICK, PASS, CHAN)
core.connect()
core.chat("Hello World!")
