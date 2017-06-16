# bot.py
import socket
import irc_cfg
import time
import re
import datetime
import os
import core_functions
import sqlite3
from random import randint

# initial connection to irc

s = socket.socket()
s.connect((irc_cfg.HOST, irc_cfg.PORT))
s.send("PASS {}\r\n".format(irc_cfg.PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(irc_cfg.NICK).encode("utf-8"))
s.send("JOIN {}\r\n".format(irc_cfg.CHAN).encode("utf-8"))
#s.send("PRIVMSG {} : coreuptedbot is online and giving points MrDestructoid\r\n".format(irc_cfg.CHAN))
time.sleep(1)
print(s.recv(1024).decode("utf-8")) #Print inital irc connection
#Stops bot from giving points to itself or a non-existent tmi user

#db setup
db_conn = sqlite3.connect('bot.db')
conn_cursor = db_conn.cursor()

#global variables
paused = False
announcecount = 0
last_chat_list = []

#time variables for timestamps

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d_%H%M%S')
announcetime = ts #static storage of timestamp
pointtime = ts #static storage of timestamp


#functions

def chat(sock, msg):
    #send as a message
    sock.send("PRIVMSG {} :{}\r\n".format(irc_cfg.CHAN, msg))

def ban(sock, user):
    #drops the banhammer
    chat(sock, ".ban {}".format(user))

def shorttimeout(sock, user, secs=120):
    #gives twitch timeout for secs
    chat(sock, ".timeout {}".format(user, secs))


def resetbonuspoints(sock, admin_name):
    #Activates after a designated user says !newstream
    #This empties the list of people who chatted
    if core_functions.user_exists(admin_name, 'admins'):
        chat(sock, "Chat bonus has been reset for all! Enjoy your chatting Kappa")
        conn_cursor.execute("DELETE FROM chatted_today")
        db_conn.commit()
    else:
        chat(sock, "You are not authorized to reset the chat")

def processchat(chatlist):
    #This makes every message in the format of
    #[['username1','message1'], ['username2','message2']]
    #icky regex ahead
    trimmedchat = []
    chatcounter = 0
    for rawresponse in chatlist:
        name = re.search(r"\w+", rawresponse).group(0) 
        message = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :").sub("", rawresponse)
        trimmedchat.append([name, message])
    return trimmedchat

def pausebot(sock, user):
    if core_functions.user_exists(admin_name, admins):
        global paused
        paused = True
        chat(sock, "Coreuptedbot is paused. Chat points paused. !coreuptedbot unpause to restart")

def unpausebot(sock, user):
    if core_functions.user_exists(admin_name, admins):
        global paused
        paused = False
        chat(sock, "Coreuptedbot is unpaused. Come and get your points MrDestructoid")

def gamble(sock, user, points):
    #Clears out eligible gamblers from table
    #Checks if user is eligible to gamble
    #If eligible, insert into table which makes them ineligible
    #Timestamp is automatically appended
    if points < irc_cfg.MINIMUM_GAMBLE:
        chat(sock, "Must gamble at least {} points.".format(irc_cfg.MINIMUM_GAMBLE))
    t2=(user,)
    conn_cursor.execute("DELETE FROM GAMBLERS where timestamp < DATETIME('now', '-%s second')" % irc_cfg.GAMBLE_RATE)
    db_conn.commit()
    if core_functions.user_exists(user, 'gamblers'):
        chat(sock, "You can only gamble once every {} seconds, {}".format(irc_cfg.GAMBLE_RATE, user))
        return
    if core_functions.cantakepoints(user, points) == False:
        chat(sock, "You don't have enough points to gamble that, {}".format(user))
        return
    core_functions.takepoints(user, points) #take their bet
    conn_cursor.execute("INSERT INTO GAMBLERS(username) values(?)", t2)
    db_conn.commit() #mark them as a gambler, timestamp is autmatically applied
    roll = randint(1,100)
    if roll < 60:
        chat(sock, "Rolled {}. {} lost {} points and now has {} points".format(roll,user,points,core_functions.getpoints(user)))
        return
    elif roll < 99:
        core_functions.givepoints(user, 2*points)
        chat(sock, "Rolled {}. {} won {} points and now has {} points".format(roll,user,2*points,core_functions.getpoints(user)))
    else: #99 or 100
        core_functions.givepoints(user, 3*points)
        chat(sock, "Rolled {}. {} won {} points and now has {} points".format(roll,user,3*points,core_functions.getpoints(user)))

def commandlist(username,message):
#todo: smaller functions
    if message == "PING :tmi.twitch.tv":
        #twitch pings us to check connection
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        print("Pong sent") #logging
    if re.match("!newstream", chatmessage[1]):
        resetbonuspoints(s, username)
    if re.match("!setbonus", message):
        #!coreuptedbot setpoints nerrage 2000
        try:
            if core_functions.user_exists(admin_name, admins):
                split_string = message.split()
                setpoint_name = split_string[1]
                setpoint_points = split_string[2]
                core_functions.setchatbonus(setpoint_name, setpoint_points)
                chat(s, "Chat bonus for {} set to {}".format(setpoint_name, setpoint_points))
            else:
                chat(s, "You are not authorized to set bonus points")
        except:
            chat(s, "!setbonus <user> <points>")
    if re.match("!pingbot", message):
        if paused:
            chat(s, "Coreuptedbot is PAUSED MrDestructoid")
        else:
            chat(s, "Coreuptedbot is ONLINE MrDestructoid")
    if re.match("!coreuptedbot pause", message):
        pausebot(s,username)
    if re.match("!coreuptedbot unpause", message):
        unpausebot(s,username)
    if re.match("!points", message):
        try:
            split_string = message.split()
            check_user = split_string[1]
            print check_user
        except:
            check_user = username
        if core_functions.user_exists(check_user,'chat_points') == 0:
            if check_user == username:
                core_functions.givepoints(username, 0)
            chat(s,"{} does not exist or hasn't been in this channel before".format(check_user))
            return
        points_owned = core_functions.getpoints(check_user)
        chat(s, "{} currently has {} points".format(check_user,points_owned))
    if re.match("!rank", message):
        try:
            split_string = message.split()
            check_user = split_string[1]
            print check_user
        except:
            check_user = username
        if core_functions.user_exists(check_user,'chat_points') == 0:
            if check_user == username:
                core_functions.givepoints(username, 0)
            chat(s,"{} does not exist or hasn't been in this channel before".format(check_user))
            return
        current_rank = core_functions.getrank(check_user)
        chat(s, "{} is currently rank {}".format(check_user,current_rank))
    if re.match("!gamble", message):
        try:
            split_string = message.split()
            gamble_points = int(split_string[1])
            gamble(s, username, gamble_points)
        except:
            chat(s, "!gamble <points to bet> Roll a 60 or above to double your points. Roll a 99 or 100 to triple them!")
    if re.match("!bonus", message):
        if core_functions.user_exists(username,'mods') or core_functions.user_exists(username,'admins'):
            try:
                split_string = message.split()
                bonus_user = split_string[1]
                bonus_points = int(split_string[2])
                core_functions.givepoints(bonus_user, bonus_points)
                chat(s, "{} points have been given to {} and they now have {}".format(bonus_points, bonus_user, core_functions.getpoints(bonus_user)))
            except:
                chat(s, "!bonus <username> <points>")
        else:
            chat(s, "Hey, you're not allowed to give a bonus! Stop cheating Kappa")
            shorttimeout(s, user)

def announcements(sock):
    #Make an announcement from announcements.txt
    global announcecount
    print("making announcement!")
    raw_announce_list = open("announcements.txt").readlines()
    announcelist = [x for x in raw_announce_list if not x.startswith('#')]
    chat(sock, announcelist[announcecount])
    announcecount += 1
    announcecount %= len(announcelist) #Start from 0 if at end of list

def tickpoints():
    #Give people in chat points for staying a full tick
    #Default is once per minute
    #Note: This logic means they must be there the tick before to get points
    global last_chat_list
    current_chat_list = core_functions.getchatlist()
    for j in [i for i in current_chat_list if i in last_chat_list]:
        core_functions.givepoints(j, irc_cfg.POINTS_PER_TICK)
    last_chat_list = current_chat_list

#main bot loop

while True:
    try:
        response = s.recv(1024).decode("utf-8")
        print(response) #logging
    except:
        continue
    response_list = response.splitlines()
    trimmed_responses = processchat(response_list)
    print(trimmed_responses) #logging
    #format [['username1', 'chat message1'], ['user2','chat2]...]
    for chatmessage in trimmed_responses:
      	username = chatmessage[0]
        message = chatmessage[1]
        commandlist(username, message)
    print("Timestamp: {}, announcetime {} ".format(float(time.time()), announcetime))
    if (announcetime <= float(time.time()) - irc_cfg.ANNOUNCEMENT_RATE and paused == False): #5 mins since last announcement
       announcements(s)
       announcetime = float(time.time()) 
    if (pointtime <= float(time.time()) - irc_cfg.TICK_RATE and paused == False): 
       tickpoints()
       pointtime = float(time.time()) 
    time.sleep(2)
