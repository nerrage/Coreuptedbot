#pause_watcher.py
#This watches for !pausebot and !unpausebot in chat
#Then it will tell the bot to pause if it sees either
#Kind of greedy with an extra connection to irc but such is life
#This will eventually be removed (hopefully)
from irc_cfg import *
from irc_client import * 
from user import *
import time

class pause_watcher:

      def __init__(self, name):
          self.name = name
          self.chat_client = irc_client(name, NICK, PASS, CHAN)
          self.chat_client.connect()

      def watchforpause(pausestatus):
        #Pause status is the current T/F of the pause state
        #Will by default return the current status
        message_list = self.chat_client.get_messages()
        for message in message_list:
            username = message[0]
            chat = message[1]
            chatter = user(username)
            if chat == "!pausebot":
                if chatter.isadmin() or chatter.isowner():
                    chat_client.chat("Coreuptedbot is paused! That means {} and announcements are paused. !unpausebot to unpause".format(POINT_NAME))
                    return True
                else:
                    chat_client.chat("Only admins and the owner may use !pausebot") 
                    return pausestatus
            if chat == "!unpausebot":
                if chatter.isadmin() or chatter.isowner():
                    chat_client.chat("Coreuptedbot is unpaused! Come and get your {}".format(POINT_NAME))
                    return False
                else:
                    chat_client.chat("Only admins and the owner may use !pausebot") 
                    return pausestatus
        return pausestatus
