#point_worker.py
#This give people points over time for being in chat
#This uses no connection to IRC so we don't connect too many times
from irc_cfg import *
import requests
import json

def point_worker:

    def __init__(self, name)
        self.name = name

    def givepoints(self):
        r = requests.get('http://tmi.twitch.tv/group/user/%s/chatters' % CHAN[1:])
        bad_hombres = json.loads(r.text)
        chat_list = bad_hombres["chatters"]["moderators"]
        chat_list.extend(bad_hombres["chatters"]["staff"])
        chat_list.extend(bad_hombres["chatters"]["admins"])
        chat_list.extend(bad_hombres["chatters"]["global_mods"])
        chat_list.extend(bad_hombres["chatters"]["viewers"])
        for chatter in chat_list:
            recipient = user(chatter)
            recipient.givepoints(POINTS_PER_TICK)
