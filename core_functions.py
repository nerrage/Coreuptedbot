import requests
import irc_cfg
import json

owner = irc_cfg.CHAN[1:]

def getchatlist():
    #get everyone in chat, return as array
    #Special shoutout to bad_hombres on Twitch!
    r = requests.get('http://tmi.twitch.tv/group/user/%s/chatters' % owner)
    bad_hombres = json.loads(r.text)
    chat_list = bad_hombres["chatters"]["moderators"]
    chat_list.extend(bad_hombres["chatters"]["staff"])
    chat_list.extend(bad_hombres["chatters"]["admins"])
    chat_list.extend(bad_hombres["chatters"]["global_mods"])
    chat_list.extend(bad_hombres["chatters"]["viewers"])
    return chat_list
