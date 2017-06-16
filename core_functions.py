import requests
import irc_cfg
import json
import sqlite3

db_conn = sqlite3.connect('bot.db')
conn_cursor = db_conn.cursor()

owner = irc_cfg.CHAN[1:]

def representsint(test_string):
    try: 
        int(test_string)
        return True
    except ValueError:
        return False

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

def user_exists(username, table):
    #Return 1 if user is on a table
    #Return 0 if user is not on table
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (irc_user,)
    conn_cursor.execute("SELECT COUNT(*) FROM "+table+" WHERE username = ?", t)
    result = conn_cursor.fetchone()
    return result[0]


def givepoints(username, gift_points):
    #Give points to a user, create record if not 
    #TODO add int validation
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (gift_points,irc_user)
    if user_exists(irc_user, 'chat_points'):
        conn_cursor.execute("UPDATE chat_points SET points = points + ? WHERE username = ?", t)
        db_conn.commit()
    else:
        conn_cursor.execute("INSERT INTO chat_points(points,username) values(?,?)", t)
        db_conn.commit()
    return

def getpoints(username):
    #Fetches a user's points from the chat_points table
    #If they don't exist give 0 to create record
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (username,)
    if user_exists(irc_user, 'chat_points'):
        conn_cursor.execute("SELECT points FROM chat_points WHERE username = ?", t)
        return conn_cursor.fetchone()[0]
    else:
        givepoints(irc_user, 0) #create user
        return getpoints(irc_user)

def cantakepoints(username, points):
    #If points passed can be taken return 1
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    if user_exists(irc_user, 'chat_points'):
        if getpoints(irc_user) > int(points):
            return True
        else:
            return False
    else:
        givepoints(irc_user, 0) #create user
        return 0

def takepoints(username, points):
    #purely take points, no checking
    #use cantakepoints to check
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (points,irc_user)
    conn_cursor.execute("UPDATE chat_points SET points = points - ? WHERE username = ?", t)
    db_conn.commit()

def setchatbonus(username,bonus_points):
    #sets the bonus in the custom bonus table
    #for first time chatting
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (bonus_points, username)
    if user_exists(irc_user, 'bonus_chat_points'):
        conn_cursor.execute("UPDATE bonus_chat_points SET points = ? WHERE username = ?", t)
        db_conn.commit()
    else:
        conn_cursor.execute("INSERT INTO bonus_chat_points(points, username) values (?, ?)", t)
        db_conn.commit()

def getchatbonus(username):
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (irc_user,)
    if user_exists(irc_user, 'bonus_chat_points'):
        conn_cursor.execute("SELECT points FROM chat_points WHERE username = ?", t)
        return conn_cursor.fetchone()[0]
    else:
        return irc_cfg.FIRST_CHAT_BONUS_POINTS #default

def hasfirstbonus(username):
    #Check if user has chatted once today
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    return user_exists(irc_user, 'chatted_today')

def givefirstbonus(username):
    #make damn sure hasfirstbonus is checked otherwise bad exceptions
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (irc_user,)
    bonus_points = getchatbonus(irc_user)
    givepoints(irc_user, bonus_points)
    conn_cursor.execute("INSERT INTO chatted_today VALUES ?", t)
    db_conn.commit()

def getrank(username):
    try:
        irc_user = username.lower() #Twitch IRC usernames are all lowercase
    except:
        print("{} could not be cast to lower".format(username))
        return 2
    t = (irc_user,)
    if user_exists(irc_user, 'chat_points'):
        conn_cursor.execute("SELECT (SELECT COUNT(*) FROM chat_points as t2 WHERE t2.points > t1.points) AS PointRank FROM chat_points AS t1 WHERE t1.username = ?", t)
        result = conn_cursor.fetchone()
        return int(result[0]) + 1
    else:
        givepoints(irc_user,0)
        getrank(irc_user)

def gettoppoints(amount):
    t = (amount,)
    conn_cursor.execute("SELECT t1.*, (SELECT count(*) FROM chat_points AS t2 WHERE t2.points > t1.points) AS PointRank FROM chat_points AS t1 ORDER BY points DESC LIMIT ?", t)
    return conn_cursor.fetchall() 
