#Dev version new features using sqlite and the like
#devbot.py 
# bot.py
import socket
import irc_cfg
import time
import re
import datetime
import os

# initial connection to irc

s = socket.socket()
s.connect((irc_cfg.HOST, irc_cfg.PORT))
s.send("PASS {}\r\n".format(irc_cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(irc_cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(irc_cfg.CHAN).encode("utf-8"))
s.send("PRIVMSG {} : coreuptedbot is online and giving points MrDestructoid\r\n".format(irc_cfg.CHAN))
time.sleep(1)
print(s.recv(1024).decode("utf-8"))
