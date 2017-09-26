#chat_worker.py
#This creates a worker that will read through chat
#As it reads through it will pass it off to rewards, etc
from irc_cfg import *
from irc_client import *
from user import *
from command import *
from rewards import *
import time

class chat_worker:

    chat_client = irc_client(NICK, PASS, CHAN) 
    chat_client.connect()

    while True:
        time.sleep(2)
        message_list = chat_client.get_messages()
        for message in message_list:
            username = message[0]
            chat = message[1]
            chatter = user(username)
            if chatter.give_first_chat_bonus():
                chat_client.chat("Welcome to my chat, {}! You get {} bonus {} for your first message and you now have {}".format(username, FIRST_CHAT_BONUS_POINTS, POINT_NAME, chatter.getpoints()))
            firstword = chat.split()[0]
            if firstword[0] == "!": #start of something special
                chat_list = chat.split().pop(0)
                commander = command(firstword, username, chat_list)
                if commander.iscommand():
                    chat_client.chat(commander.execute_command()) 
