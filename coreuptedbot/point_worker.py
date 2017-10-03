#point_worker.py
#This give people points over time for being in chat
#This uses no connection to IRC so we don't connect too many times
from irc_cfg import *
from user import *
import requests
import json

class point_worker:

    def __init__(self, name):
        self.name = name
        self.last_list = []
        self.tickpoints = POINTS_PER_TICK

    def getchatters(self):
        r = requests.get('http://tmi.twitch.tv/group/user/%s/chatters' % CHAN[1:])
        bad_hombres = json.loads(r.text)
        chat_list = bad_hombres["chatters"]["moderators"]
        chat_list.extend(bad_hombres["chatters"]["staff"])
        chat_list.extend(bad_hombres["chatters"]["admins"])
        chat_list.extend(bad_hombres["chatters"]["global_mods"])
        chat_list.extend(bad_hombres["chatters"]["viewers"])
        return chat_list


    def givepassivepoints(self):
        try: #Twitch API can fail and cause exceptions
            chat_list = self.getchatters()
            for j in [i for i in chat_list if i in self.last_list]:
            #This prevents abuse. You must be in chat a full tick to get points
                recipient_user = user(j)
                recipient_user.givepoints(self.tickpoints)
            self.tickpoints = POINTS_PER_TICK #reset points if were over base
            self.last_list = chat_list #update list of people eligable to receive next tick
        except: #twitch API has failed, try again and increase points
            self.tickpoints += POINTS_PER_TICK
        
